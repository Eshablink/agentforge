from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.rate_limit import RateLimitExceeded, RateLimitUnavailable, auth_request_limiter
from app.core.settings import get_settings
from app.core.telemetry import record
from app.db.session import SessionLocal
from app.models.user import AuthSession, User
from app.schemas.platform import LoginRequest, RegisterRequest

_bearer = HTTPBearer(auto_error=False)
_ITERATIONS = 600_000


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return (
        "pbkdf2_sha256$"
        + str(_ITERATIONS)
        + "$"
        + base64.urlsafe_b64encode(salt).decode()
        + "$"
        + base64.urlsafe_b64encode(digest).decode()
    )


def _verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_b64, digest_b64 = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _limit_auth(email: str) -> None:
    key = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
    try:
        auth_request_limiter.check(key)
    except RateLimitExceeded as exc:
        record("auth_throttled", category="rate_limit")
        raise HTTPException(status_code=429, detail="Too many authentication attempts") from exc
    except RateLimitUnavailable as exc:
        record("auth_throttled", category="limiter_unavailable")
        raise HTTPException(status_code=503, detail="Authentication temporarily unavailable") from exc


def register_user(db: Session, payload: RegisterRequest) -> User:
    email = str(payload.email).strip().lower()
    _limit_auth(email)
    user = User(email=email, password_hash=_hash_password(payload.password), is_active=True)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account already exists") from exc
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> tuple[User, str, datetime]:
    email = str(payload.email).strip().lower()
    _limit_auth(email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = secrets.token_urlsafe(36)
    expires = datetime.now(timezone.utc) + timedelta(seconds=get_settings().session_ttl_seconds)
    db.add(AuthSession(user_id=user.id, token_hash=_token_hash(token), expires_at=expires))
    db.commit()
    return user, token, expires


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    db = SessionLocal()
    try:
        row = db.scalar(select(AuthSession).where(AuthSession.token_hash == _token_hash(credentials.credentials)))
        if row is None or row.revoked_at is not None or row.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Authentication required")
        user = db.get(User, row.user_id)
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="Authentication required")
        db.expunge(user)
        return user
    finally:
        db.close()


def logout_user(db: Session, user: User) -> None:
    rows = db.scalars(select(AuthSession).where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))).all()
    now = datetime.now(timezone.utc)
    for row in rows:
        row.revoked_at = now
    db.commit()


def cleanup_sessions(db: Session, *, batch_size: int = 500) -> int:
    """Explicit bounded maintenance; no active sessions are deleted."""
    if not 1 <= batch_size <= 1000:
        raise ValueError("batch_size must be between 1 and 1000")
    now = datetime.now(timezone.utc)
    ids = db.scalars(select(AuthSession.id).where(AuthSession.expires_at < now).order_by(AuthSession.expires_at).limit(batch_size)).all()
    if ids:
        db.execute(delete(AuthSession).where(AuthSession.id.in_(ids)))
        db.commit()
    return len(ids)

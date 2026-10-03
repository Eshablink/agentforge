from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.dependencies import get_db
from app.models.user import AuthSession, User
from app.schemas.platform import LoginRequest, RegisterRequest

_passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer(auto_error=False)


def _token_hash(token: str) -> str:
    import hashlib
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def register_user(db: Session, payload: RegisterRequest) -> User:
    email = str(payload.email).strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Account already exists")
    user = User(email=email, password_hash=_passwords.hash(payload.password), is_active=True)
    db.add(user)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account already exists") from exc
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> tuple[User, str, datetime]:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    try:
        valid = bool(user and _passwords.verify(payload.password, user.password_hash) and user.is_active)
    except (ValueError, TypeError):
        valid = False
    if not valid or user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = __import__("secrets").token_urlsafe(36)
    expires = datetime.now(timezone.utc) + timedelta(seconds=get_settings().session_ttl_seconds)
    db.add(AuthSession(user_id=user.id, token_hash=_token_hash(token), expires_at=expires))
    db.commit()
    return user, token, expires


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == _token_hash(credentials.credentials)))
    if row is None or row.revoked_at is not None or row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def logout_user(db: Session, user: User) -> None:
    rows = db.scalars(select(AuthSession).where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))).all()
    now = datetime.now(timezone.utc)
    for row in rows:
        row.revoked_at = now
    db.commit()

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Response, status
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


class AuthenticationError(Exception):
    pass


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def register_user(db: Session, payload: RegisterRequest) -> User:
    email = str(payload.email).strip().lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="Account already exists")
    user = User(email=email, password_hash=_passwords.hash(payload.password), is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> tuple[User, str, datetime]:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if not user or not _passwords.verify(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = secrets.token_urlsafe(36)
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
    token_hash = _token_hash(credentials.credentials)
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
    if not row or row.revoked_at or row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.get(User, row.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def logout_user(db: Session, credentials: HTTPAuthorizationCredentials | None) -> None:
    if credentials is None:
        return
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == _token_hash(credentials.credentials)))
    if row and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)
        db.commit()

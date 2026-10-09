"""Password hashing and per-user JWT bearer authentication."""

import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from . import models
from .database import get_db


JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_SECONDS = 30 * 60
password_hasher = PasswordHash.recommended()
_DUMMY_PASSWORD_HASH = password_hasher.hash(
    "dummy-password-used-only-to-reduce-login-timing-differences"
)
bearer_scheme = HTTPBearer(auto_error=False)


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET debe tener al menos 32 bytes aleatorios")
    return secret


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if password_hash is None:
        password_hasher.verify(password, _DUMMY_PASSWORD_HASH)
        return False
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=ACCESS_TOKEN_SECONDS
    )
    claims = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(claims, _jwt_secret(), algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.Usuario:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        claims = jwt.decode(
            credentials.credentials,
            _jwt_secret(),
            algorithms=[JWT_ALGORITHM],
        )
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.isdecimal():
            raise unauthorized
        user_id = int(subject)
    except (JWTError, RuntimeError, ValueError) as exc:
        raise unauthorized from exc

    user = db.get(models.Usuario, user_id)
    if user is None:
        raise unauthorized
    return user
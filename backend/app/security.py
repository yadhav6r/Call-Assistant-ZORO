from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
import hmac
from secrets import token_urlsafe
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings, refresh_lifetime
from app.dependencies import get_db
from app.models import AuthSession, User

password_hash = PasswordHash.recommended()
_DUMMY_PASSWORD_HASH = password_hash.hash("zoro-nonexistent-account-dummy-password")
bearer = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user: User
    session: AuthSession


def new_refresh_token() -> str:
    return token_urlsafe(48)


def digest_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def login_bucket_hash(kind: str, value: str, settings: Settings) -> str:
    key = settings.jwt_secret_key.get_secret_value().encode("utf-8")
    message = f"login-limit:{kind}:{value.strip().lower()}".encode("utf-8")
    return hmac.new(key, message, sha256).hexdigest()


def issue_access_token(user_id: UUID, session_id: UUID, settings: Settings) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(user_id),
            "sid": str(session_id),
            "typ": "access",
            "iss": "zoro-api",
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_access_ttl_minutes),
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )


async def create_auth_session(
    db: AsyncSession, user: User, settings: Settings
) -> tuple[AuthSession, str]:

    raw_refresh_token = new_refresh_token()
    session = AuthSession(
        user_id=user.id,
        refresh_token_hash=digest_refresh_token(raw_refresh_token),
        expires_at=datetime.now(UTC) + refresh_lifetime(settings),
    )
    db.add(session)
    await db.flush()
    return session, raw_refresh_token


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=["HS256"],
            issuer="zoro-api",
            options={"require": ["sub", "sid", "typ", "exp", "iat", "iss"]},
        )
        if claims.get("typ") != "access":
            raise unauthorized
        user_id = UUID(claims["sub"])
        session_id = UUID(claims["sid"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise unauthorized from None

    auth_session = await db.get(AuthSession, session_id)
    now = datetime.now(UTC)
    if (
        auth_session is None
        or auth_session.user_id != user_id
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= now
    ):
        raise unauthorized
    user = await db.get(User, user_id)
    if user is None or (
        settings.app_env.lower() == "production"
        and (settings.owner_email is None or user.email != str(settings.owner_email).lower())
    ):
        raise unauthorized
    return AuthContext(user=user, session=auth_session)





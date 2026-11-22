from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings, refresh_lifetime
from app.dependencies import get_db
from app.models import AuthSession, User
from app.security import (
    AuthContext,
    _DUMMY_PASSWORD_HASH,
    create_auth_session,
    digest_refresh_token,
    get_auth_context,
    issue_access_token,
    login_bucket_hash,
    new_refresh_token,
    password_hash,
)
from app.services.auth_limits import (
    EMAIL_FAILURE_LIMIT,
    IP_FAILURE_LIMIT,
    active_lock_until,
    clear_failures,
    prune_old_failures,
    record_failure,
    retry_after_seconds,
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: Credentials,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    if settings.app_env.lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account creation is disabled. The private owner account is provisioned separately.",
        )
    user = User(
        email=str(body.email).lower(),
        password_hash=password_hash.hash(body.password),
        display_name=str(body.email).split("@", 1)[0],
    )
    db.add(user)
    try:
        await db.flush()
        auth_session, refresh_token = await create_auth_session(db, user, settings)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="An account with that email already exists") from None
    return TokenResponse(
        access_token=issue_access_token(user.id, auth_session.id, settings),
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_ttl_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: Credentials,
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    email = str(body.email).lower()
    is_owner_email = (
        settings.app_env.lower() != "production"
        or settings.owner_email is not None
        and email == str(settings.owner_email).lower()
    )
    bucket_hashes: list[str] = []
    now = datetime.now(UTC)
    if settings.app_env.lower() == "production":
        await prune_old_failures(db, now)
        client_ip = request.client.host if request.client else "unknown"
        email_bucket = login_bucket_hash("email", email, settings)
        ip_bucket = login_bucket_hash("ip", client_ip, settings)
        bucket_hashes = [email_bucket, ip_bucket]
        locked_until = await active_lock_until(db, bucket_hashes, now)
        if locked_until is not None:
            retry_after = retry_after_seconds(locked_until, now)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many sign-in attempts. Try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    user = None
    if is_owner_email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
    valid_password = password_hash.verify(
        body.password,
        user.password_hash if user is not None and user.password_hash else _DUMMY_PASSWORD_HASH,
    )
    if user is None or not valid_password:
        if settings.app_env.lower() == "production":
            await record_failure(db, bucket_hashes[0], EMAIL_FAILURE_LIMIT, now)
            await record_failure(db, bucket_hashes[1], IP_FAILURE_LIMIT, now)
            await db.commit()
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    if settings.app_env.lower() == "production":
        await clear_failures(db, bucket_hashes)
    auth_session, refresh_token = await create_auth_session(db, user, settings)
    await db.commit()
    return TokenResponse(
        access_token=issue_access_token(user.id, auth_session.id, settings),
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_ttl_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    token_hash = digest_refresh_token(body.refresh_token)
    result = await db.execute(
        select(AuthSession).where(AuthSession.refresh_token_hash == token_hash).with_for_update()
    )
    auth_session = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if (
        auth_session is None
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= now
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = await db.get(User, auth_session.user_id)
    if user is None or (
        settings.app_env.lower() == "production"
        and (settings.owner_email is None or user.email != str(settings.owner_email).lower())
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    next_refresh_token = new_refresh_token()
    auth_session.refresh_token_hash = digest_refresh_token(next_refresh_token)
    auth_session.expires_at = now + refresh_lifetime(settings)
    await db.commit()
    return TokenResponse(
        access_token=issue_access_token(user.id, auth_session.id, settings),
        refresh_token=next_refresh_token,
        expires_in=settings.jwt_access_ttl_minutes * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> None:
    context.session.revoked_at = datetime.now(UTC)
    await db.commit()




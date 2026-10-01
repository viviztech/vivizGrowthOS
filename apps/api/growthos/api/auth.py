from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from growthos.api.dependencies import CurrentUser, SessionDep
from growthos.core.security import DUMMY_PASSWORD_HASH, create_access_token, verify_password
from growthos.models import Tenant, User
from growthos.schemas import LoginRequest, TokenResponse, UserResponse
from growthos.services.entitlements import permission_codes

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: SessionDep) -> TokenResponse:
    user = await session.scalar(
        select(User)
        .join(Tenant)
        .where(
            Tenant.slug == body.tenant_slug,
            Tenant.status == "active",
            User.email == body.email.lower(),
            User.is_active.is_(True),
        )
    )
    valid_password = verify_password(
        body.password, user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    )
    if user is None or not valid_password:
        raise HTTPException(status_code=401, detail="Invalid tenant, email, or password")
    return TokenResponse(
        access_token=create_access_token(user_id=user.id, tenant_id=user.tenant_id)
    )


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        full_name=user.full_name,
        permissions=sorted(permission_codes(user.roles)),
    )

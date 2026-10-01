from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from growthos.core.database import get_session
from growthos.core.security import decode_access_token
from growthos.models import Role, Tenant, User
from growthos.services.entitlements import FeatureEntitlementService, permission_codes

bearer = HTTPBearer(auto_error=False)
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = str(payload["sub"])
        tenant_id = str(payload["tenant_id"])
    except (jwt.InvalidTokenError, KeyError, TypeError) as exc:
        raise unauthorized from exc

    user = await session.scalar(
        select(User)
        .where(User.id == user_id, User.tenant_id == tenant_id, User.is_active.is_(True))
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    if user is None:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_tenant(session: SessionDep, user: CurrentUser) -> Tenant:
    tenant = await session.scalar(
        select(Tenant).where(Tenant.id == user.tenant_id, Tenant.status == "active")
    )
    if tenant is None:
        raise HTTPException(status_code=403, detail="Tenant is not active")
    return tenant


CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]


def require_permission(permission: str) -> Callable[..., User]:
    async def dependency(user: CurrentUser) -> User:
        if permission not in permission_codes(user.roles):
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
        return user

    return dependency


def require_module(module_code: str, permission: str) -> Callable[..., None]:
    async def dependency(
        session: SessionDep,
        tenant: CurrentTenant,
        user: Annotated[User, Depends(require_permission(permission))],
    ) -> None:
        del user
        await FeatureEntitlementService(session, tenant).require_module(module_code)

    return dependency

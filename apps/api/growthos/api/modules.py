from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from growthos.api.dependencies import CurrentTenant, CurrentUser, SessionDep, require_permission
from growthos.models import ModuleCatalog, TenantModule, User
from growthos.schemas import (
    EnableModuleRequest,
    ModuleActivationResponse,
    ModuleConfiguration,
    ModuleResponse,
    NavigationItem,
)
from growthos.services.entitlements import FeatureEntitlementService, permission_codes

router = APIRouter(tags=["modules"])


@router.get("/modules", response_model=list[ModuleResponse])
async def list_modules(
    session: SessionDep, tenant: CurrentTenant, user: CurrentUser
) -> list[ModuleResponse]:
    del user
    service = FeatureEntitlementService(session, tenant)
    modules = await service.get_available_modules()
    enabled = {item.module_id: item for item in await service.get_enabled_modules()}
    return [
        ModuleResponse(
            code=module.code,
            name=module.name,
            category=module.category,
            description=module.description,
            business_value=module.business_value,
            is_core=module.is_core,
            is_billable=module.is_billable,
            version=module.version,
            enabled=module.id in enabled,
            configured=enabled[module.id].configured if module.id in enabled else False,
            dependencies=[item.depends_on.code for item in module.dependencies],
        )
        for module in modules
    ]


@router.get("/modules/enabled", response_model=list[ModuleResponse])
async def enabled_modules(
    session: SessionDep, tenant: CurrentTenant, user: CurrentUser
) -> list[ModuleResponse]:
    del user
    records = await FeatureEntitlementService(session, tenant).get_enabled_modules()
    return [
        ModuleResponse(
            code=item.module.code,
            name=item.module.name,
            category=item.module.category,
            description=item.module.description,
            business_value=item.module.business_value,
            is_core=item.module.is_core,
            is_billable=item.module.is_billable,
            version=item.module.version,
            enabled=True,
            configured=item.configured,
        )
        for item in records
    ]


@router.post("/modules/{module_code}/enable", response_model=ModuleActivationResponse)
async def enable_module(
    module_code: str,
    body: EnableModuleRequest,
    session: SessionDep,
    tenant: CurrentTenant,
    user: Annotated[User, Depends(require_permission("modules.manage"))],
) -> ModuleActivationResponse:
    del user
    enabled, dependencies = await FeatureEntitlementService(session, tenant).enable_module(
        module_code, source=body.source, activate_dependencies=body.activate_dependencies
    )
    return ModuleActivationResponse(enabled=enabled, dependencies_activated=dependencies)


@router.post("/modules/{module_code}/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_module(
    module_code: str,
    session: SessionDep,
    tenant: CurrentTenant,
    user: Annotated[User, Depends(require_permission("modules.manage"))],
) -> Response:
    del user
    await FeatureEntitlementService(session, tenant).disable_module(module_code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _tenant_module(session: SessionDep, tenant_id: str, module_code: str) -> TenantModule:
    record = await session.scalar(
        select(TenantModule)
        .join(ModuleCatalog)
        .where(TenantModule.tenant_id == tenant_id, ModuleCatalog.code == module_code)
    )
    if record is None or record.status != "enabled":
        raise HTTPException(status_code=403, detail="Module is not enabled for this tenant")
    return record


@router.get("/modules/{module_code}/configuration", response_model=ModuleConfiguration)
async def get_configuration(
    module_code: str,
    session: SessionDep,
    tenant: CurrentTenant,
    user: Annotated[User, Depends(require_permission("modules.manage"))],
) -> ModuleConfiguration:
    del user
    record = await _tenant_module(session, tenant.id, module_code)
    return ModuleConfiguration(values=record.configuration_json)


@router.put("/modules/{module_code}/configuration", response_model=ModuleConfiguration)
async def update_configuration(
    module_code: str,
    body: ModuleConfiguration,
    session: SessionDep,
    tenant: CurrentTenant,
    user: Annotated[User, Depends(require_permission("modules.manage"))],
) -> ModuleConfiguration:
    del user
    record = await _tenant_module(session, tenant.id, module_code)
    record.configuration_json = body.values
    record.configured = True
    await session.commit()
    return body


@router.get("/navigation", response_model=list[NavigationItem])
async def navigation(
    session: SessionDep, tenant: CurrentTenant, user: CurrentUser
) -> list[NavigationItem]:
    granted = permission_codes(user.roles)
    enabled = await FeatureEntitlementService(session, tenant).get_enabled_modules()
    items: list[NavigationItem] = []
    for record in sorted(enabled, key=lambda item: (not item.module.is_core, item.module.name)):
        for raw in record.module.navigation:
            if raw.get("permission") in granted:
                items.append(NavigationItem(**raw, module_code=record.module.code))
    return items

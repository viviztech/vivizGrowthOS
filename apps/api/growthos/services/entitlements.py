from collections.abc import Iterable
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from growthos.models import ModuleCatalog, ModuleDependency, Tenant, TenantModule


class FeatureEntitlementService:
    """Single authority for module, dependency, tenant, and plan access."""

    def __init__(self, session: AsyncSession, tenant: Tenant) -> None:
        self.session = session
        self.tenant = tenant

    def check_plan_access(self, module: ModuleCatalog) -> bool:
        plan_rank = {"base": 0, "growth": 1, "pro": 2, "enterprise": 3}
        tenant_rank = plan_rank.get(self.tenant.plan_code, -1)
        required_rank = plan_rank.get(module.minimum_plan, 99)
        return module.is_core or tenant_rank >= required_rank

    async def get_available_modules(self) -> list[ModuleCatalog]:
        result = await self.session.scalars(
            select(ModuleCatalog)
            .where(ModuleCatalog.status == "active")
            .options(
                selectinload(ModuleCatalog.dependencies).selectinload(ModuleDependency.depends_on)
            )
            .order_by(ModuleCatalog.category, ModuleCatalog.name)
        )
        return list(result.unique())

    async def get_enabled_modules(self) -> list[TenantModule]:
        result = await self.session.scalars(
            select(TenantModule)
            .where(TenantModule.tenant_id == self.tenant.id, TenantModule.status == "enabled")
            .options(selectinload(TenantModule.module))
        )
        return list(result.unique())

    async def is_module_enabled(self, module_code: str) -> bool:
        if self.tenant.status != "active":
            return False
        record = await self.session.scalar(
            select(TenantModule)
            .join(ModuleCatalog)
            .where(
                TenantModule.tenant_id == self.tenant.id,
                TenantModule.status == "enabled",
                ModuleCatalog.code == module_code,
            )
        )
        return record is not None

    async def require_module(self, module_code: str) -> None:
        if not await self.is_module_enabled(module_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Module '{module_code}' is not enabled for this tenant",
            )

    async def resolve_dependencies(self, module_code: str) -> list[ModuleCatalog]:
        catalog = {item.code: item for item in await self.get_available_modules()}
        if module_code not in catalog:
            raise HTTPException(status_code=404, detail="Unknown or unavailable module")
        if not self.check_plan_access(catalog[module_code]):
            raise HTTPException(status_code=403, detail="Current plan does not allow this module")

        resolved: list[ModuleCatalog] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(code: str) -> None:
            if code in visiting:
                raise HTTPException(status_code=409, detail="Cyclic module dependency detected")
            if code in visited:
                return
            visiting.add(code)
            module = catalog[code]
            for relation in module.dependencies:
                if relation.dependency_type == "required":
                    visit(relation.depends_on.code)
            visiting.remove(code)
            visited.add(code)
            resolved.append(module)

        visit(module_code)
        return resolved

    async def enable_module(
        self, module_code: str, *, source: str, activate_dependencies: bool
    ) -> tuple[list[str], list[str]]:
        required = await self.resolve_dependencies(module_code)
        dependencies = [module for module in required if module.code != module_code]
        disabled_dependencies = [
            module for module in dependencies if not await self.is_module_enabled(module.code)
        ]
        if disabled_dependencies and not activate_dependencies:
            codes = ", ".join(module.code for module in disabled_dependencies)
            raise HTTPException(status_code=409, detail=f"Required modules are disabled: {codes}")

        activated: list[str] = []
        dependency_codes: list[str] = []
        for module in required:
            tenant_module = await self.session.scalar(
                select(TenantModule).where(
                    TenantModule.tenant_id == self.tenant.id,
                    TenantModule.module_id == module.id,
                )
            )
            if tenant_module is None:
                tenant_module = TenantModule(
                    tenant_id=self.tenant.id,
                    module_id=module.id,
                    source=source,
                    module_version=module.version,
                )
                self.session.add(tenant_module)
            if tenant_module.status != "enabled":
                tenant_module.status = "enabled"
                tenant_module.enabled_at = datetime.now(UTC)
                tenant_module.disabled_at = None
                activated.append(module.code)
                if module.code != module_code:
                    dependency_codes.append(module.code)
        await self.session.commit()
        return activated, dependency_codes

    async def disable_module(self, module_code: str) -> None:
        module = await self.session.scalar(
            select(ModuleCatalog).where(ModuleCatalog.code == module_code)
        )
        if module is None:
            raise HTTPException(status_code=404, detail="Unknown module")
        if module.is_core:
            raise HTTPException(status_code=409, detail="Core modules cannot be disabled")

        enabled = await self.get_enabled_modules()
        enabled_ids = {item.module_id for item in enabled}
        blockers = await self.session.scalars(
            select(ModuleCatalog.code)
            .join(ModuleDependency, ModuleDependency.module_id == ModuleCatalog.id)
            .where(
                ModuleDependency.depends_on_module_id == module.id,
                ModuleDependency.module_id.in_(enabled_ids),
            )
        )
        blocker_codes = list(blockers)
        if blocker_codes:
            raise HTTPException(
                status_code=409,
                detail=f"Disable dependent modules first: {', '.join(blocker_codes)}",
            )

        record = await self.session.scalar(
            select(TenantModule).where(
                TenantModule.tenant_id == self.tenant.id,
                TenantModule.module_id == module.id,
            )
        )
        if record:
            record.status = "disabled"
            record.disabled_at = datetime.now(UTC)
            await self.session.commit()


def permission_codes(roles: Iterable[object]) -> set[str]:
    return {permission.code for role in roles for permission in getattr(role, "permissions", [])}

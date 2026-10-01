import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from growthos.catalog import MODULE_DEFINITIONS
from growthos.core.database import SessionFactory
from growthos.core.security import hash_password
from growthos.models import (
    ModuleCatalog,
    ModuleDependency,
    Permission,
    Role,
    Tenant,
    TenantModule,
    User,
)


async def seed_catalog(session: AsyncSession) -> dict[str, ModuleCatalog]:
    modules: dict[str, ModuleCatalog] = {}
    module_dependencies: dict[str, list[str]] = {}
    for definition in MODULE_DEFINITIONS:
        dependencies = definition.get("dependencies", [])
        values = {key: value for key, value in definition.items() if key != "dependencies"}
        module = await session.scalar(
            select(ModuleCatalog).where(ModuleCatalog.code == values["code"])
        )
        if module is None:
            module = ModuleCatalog(**values)
            session.add(module)
        else:
            for key, value in values.items():
                setattr(module, key, value)
        modules[module.code] = module
        module_dependencies[module.code] = dependencies
    await session.flush()
    for module in modules.values():
        for dependency_code in module_dependencies[module.code]:
            dependency = modules[dependency_code]
            exists = await session.scalar(
                select(ModuleDependency).where(
                    ModuleDependency.module_id == module.id,
                    ModuleDependency.depends_on_module_id == dependency.id,
                )
            )
            if exists is None:
                session.add(
                    ModuleDependency(module_id=module.id, depends_on_module_id=dependency.id)
                )
    await session.commit()
    return modules


async def seed_demo() -> None:
    async with SessionFactory() as session:
        modules = await seed_catalog(session)
        tenant = await session.scalar(select(Tenant).where(Tenant.slug == "viviz-demo"))
        if tenant is None:
            tenant = Tenant(name="VIVIZ Technologies", slug="viviz-demo")
            session.add(tenant)
            await session.flush()

        permission_codes = sorted(
            {code for module in modules.values() for code in module.permissions}
        )
        permissions: list[Permission] = []
        for code in permission_codes:
            permission = await session.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=code.replace(".", " ").title())
                session.add(permission)
            permissions.append(permission)

        role = await session.scalar(
            select(Role).where(Role.tenant_id == tenant.id, Role.code == "tenant_admin")
        )
        if role is None:
            role = Role(tenant_id=tenant.id, code="tenant_admin", name="Tenant administrator")
            session.add(role)
        role.permissions = permissions

        user = await session.scalar(
            select(User).where(User.tenant_id == tenant.id, User.email == "admin@vivizgrowthos.com")
        )
        if user is None:
            user = User(
                tenant_id=tenant.id,
                email="admin@vivizgrowthos.com",
                full_name="VIVIZ Admin",
                password_hash=hash_password("ChangeMe123!"),
            )
            session.add(user)
        user.roles = [role]

        core = modules["core"]
        enabled = await session.scalar(
            select(TenantModule).where(
                TenantModule.tenant_id == tenant.id, TenantModule.module_id == core.id
            )
        )
        if enabled is None:
            session.add(
                TenantModule(
                    tenant_id=tenant.id,
                    module_id=core.id,
                    status="enabled",
                    source="plan",
                    configured=True,
                )
            )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo())

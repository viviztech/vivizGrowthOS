import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from growthos.models import ModuleCatalog, ModuleDependency, Tenant, TenantModule
from growthos.services.entitlements import FeatureEntitlementService


async def module(session: AsyncSession, code: str, *, core: bool = False) -> ModuleCatalog:
    value = ModuleCatalog(
        code=code,
        name=code.replace("_", " ").title(),
        category="test",
        is_core=core,
        permissions=[f"{code}.view"],
        navigation=[],
    )
    session.add(value)
    await session.flush()
    return value


@pytest.mark.asyncio
async def test_enabling_module_activates_required_dependencies(session: AsyncSession) -> None:
    tenant = Tenant(name="Tenant A", slug="tenant-a")
    session.add(tenant)
    notifications = await module(session, "internal_notifications")
    workflow = await module(session, "workflow_engine")
    session.add(ModuleDependency(module_id=workflow.id, depends_on_module_id=notifications.id))
    await session.commit()

    activated, dependencies = await FeatureEntitlementService(session, tenant).enable_module(
        "workflow_engine", source="manual", activate_dependencies=True
    )

    assert activated == ["internal_notifications", "workflow_engine"]
    assert dependencies == ["internal_notifications"]


@pytest.mark.asyncio
async def test_missing_dependency_consent_rejects_activation(session: AsyncSession) -> None:
    tenant = Tenant(name="Tenant A", slug="tenant-a")
    session.add(tenant)
    dependency = await module(session, "appointments")
    visits = await module(session, "site_visits")
    session.add(ModuleDependency(module_id=visits.id, depends_on_module_id=dependency.id))
    await session.commit()

    with pytest.raises(HTTPException) as exc:
        await FeatureEntitlementService(session, tenant).enable_module(
            "site_visits", source="manual", activate_dependencies=False
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_enabled_modules_are_tenant_scoped(session: AsyncSession) -> None:
    tenant_a = Tenant(name="Tenant A", slug="tenant-a")
    tenant_b = Tenant(name="Tenant B", slug="tenant-b")
    session.add_all([tenant_a, tenant_b])
    leads = await module(session, "leads")
    session.add(TenantModule(tenant_id=tenant_a.id, module_id=leads.id, status="enabled"))
    await session.commit()

    assert await FeatureEntitlementService(session, tenant_a).is_module_enabled("leads")
    assert not await FeatureEntitlementService(session, tenant_b).is_module_enabled("leads")


@pytest.mark.asyncio
async def test_deactivation_rejects_enabled_dependents(session: AsyncSession) -> None:
    tenant = Tenant(name="Tenant A", slug="tenant-a")
    session.add(tenant)
    dependency = await module(session, "appointments")
    visits = await module(session, "site_visits")
    session.add(ModuleDependency(module_id=visits.id, depends_on_module_id=dependency.id))
    session.add_all(
        [
            TenantModule(tenant_id=tenant.id, module_id=dependency.id, status="enabled"),
            TenantModule(tenant_id=tenant.id, module_id=visits.id, status="enabled"),
        ]
    )
    await session.commit()

    with pytest.raises(HTTPException) as exc:
        await FeatureEntitlementService(session, tenant).disable_module("appointments")
    assert exc.value.status_code == 409
    assert "site_visits" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_disabled_module_is_forbidden(session: AsyncSession) -> None:
    tenant = Tenant(name="Tenant A", slug="tenant-a")
    session.add(tenant)
    await module(session, "leads")
    await session.commit()

    with pytest.raises(HTTPException) as exc:
        await FeatureEntitlementService(session, tenant).require_module("leads")
    assert exc.value.status_code == 403

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from growthos.api.dependencies import get_session
from growthos.core.database import Base
from growthos.core.security import hash_password
from growthos.main import app
from growthos.models import ModuleCatalog, Permission, Role, Tenant, TenantModule, User


@pytest.mark.asyncio
async def test_api_root_is_discoverable() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as client:
        response = await client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_login_and_adaptive_navigation_are_connected() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        tenant = Tenant(name="Demo", slug="demo")
        session.add(tenant)
        await session.flush()
        permission = Permission(code="dashboard.view", description="View dashboard")
        role = Role(tenant_id=tenant.id, code="tenant_admin", name="Tenant admin")
        role.permissions = [permission]
        user = User(
            tenant_id=tenant.id,
            email="admin@acme.com",
            full_name="Admin",
            password_hash=hash_password("Password123!"),
        )
        user.roles = [role]
        core = ModuleCatalog(
            code="core",
            name="Core",
            category="platform",
            is_core=True,
            permissions=["dashboard.view"],
            navigation=[
                {
                    "label": "Dashboard",
                    "href": "/dashboard",
                    "icon": "LayoutDashboard",
                    "permission": "dashboard.view",
                },
                {
                    "label": "Settings",
                    "href": "/settings",
                    "icon": "Settings",
                    "permission": "settings.view",
                },
            ],
        )
        session.add_all([user, core])
        await session.flush()
        session.add(TenantModule(tenant_id=tenant.id, module_id=core.id, status="enabled"))
        await session.commit()

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            login = await client.post(
                "/api/v1/auth/login",
                json={
                    "tenant_slug": "demo",
                    "email": "admin@acme.com",
                    "password": "Password123!",
                },
            )
            assert login.status_code == 200, login.text
            token = login.json()["access_token"]
            navigation = await client.get(
                "/api/v1/navigation", headers={"Authorization": f"Bearer {token}"}
            )
            assert navigation.status_code == 200
            assert [item["label"] for item in navigation.json()] == ["Dashboard"]
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()

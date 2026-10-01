from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from growthos.core.database import Base


def new_id() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(UTC)


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    plan_code: Mapped[str] = mapped_column(String(40), default="base")

    users: Mapped[list[User]] = relationship(back_populates="tenant")
    modules: Mapped[list[TenantModule]] = relationship(back_populates="tenant")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(254), index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant: Mapped[Tenant] = relationship(back_populates="users")
    roles: Mapped[list[Role]] = relationship(secondary=user_roles, lazy="selectin")


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_role_tenant_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(100))
    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions, lazy="selectin"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")


class ModuleCatalog(TimestampMixin, Base):
    __tablename__ = "module_catalog"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(60), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    business_value: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="active")
    is_core: Mapped[bool] = mapped_column(Boolean, default=False)
    is_billable: Mapped[bool] = mapped_column(Boolean, default=False)
    minimum_plan: Mapped[str] = mapped_column(String(40), default="base")
    version: Mapped[str] = mapped_column(String(24), default="1.0.0")
    configuration_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    navigation: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list)

    dependencies: Mapped[list[ModuleDependency]] = relationship(
        foreign_keys="ModuleDependency.module_id", back_populates="module", lazy="selectin"
    )


class ModuleDependency(Base):
    __tablename__ = "module_dependencies"
    __table_args__ = (
        UniqueConstraint("module_id", "depends_on_module_id", name="uq_module_dependency"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    module_id: Mapped[str] = mapped_column(
        ForeignKey("module_catalog.id", ondelete="CASCADE"), index=True
    )
    depends_on_module_id: Mapped[str] = mapped_column(
        ForeignKey("module_catalog.id", ondelete="RESTRICT"), index=True
    )
    dependency_type: Mapped[str] = mapped_column(String(16), default="required")

    module: Mapped[ModuleCatalog] = relationship(
        foreign_keys=[module_id], back_populates="dependencies"
    )
    depends_on: Mapped[ModuleCatalog] = relationship(foreign_keys=[depends_on_module_id])


class TenantModule(TimestampMixin, Base):
    __tablename__ = "tenant_modules"
    __table_args__ = (UniqueConstraint("tenant_id", "module_id", name="uq_tenant_module"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    module_id: Mapped[str] = mapped_column(
        ForeignKey("module_catalog.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    source: Mapped[str] = mapped_column(String(32), default="manual")
    configured: Mapped[bool] = mapped_column(Boolean, default=False)
    configuration_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    module_version: Mapped[str] = mapped_column(String(24), default="1.0.0")
    configuration_version: Mapped[str] = mapped_column(String(24), default="1.0.0")
    enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    tenant: Mapped[Tenant] = relationship(back_populates="modules")
    module: Mapped[ModuleCatalog] = relationship(lazy="selectin")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(80))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class BusinessProfile(TimestampMixin, Base):
    __tablename__ = "business_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, index=True
    )
    industry_code: Mapped[str] = mapped_column(String(80), index=True)
    business_model: Mapped[str] = mapped_column(String(16))
    customer_type: Mapped[str] = mapped_column(String(16))
    offering_type: Mapped[str] = mapped_column(String(16))
    employee_range: Mapped[str] = mapped_column(String(24), default="1-10")
    location_count: Mapped[int] = mapped_column(default=1)
    market_scope: Mapped[str] = mapped_column(String(40), default="local")
    average_sales_cycle_days: Mapped[int] = mapped_column(default=0)
    sales_team_size: Mapped[int] = mapped_column(default=1)
    requires_leads: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_online_sales: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_appointments: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_quotations: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_field_visits: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_customer_support: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_repeat_business: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_dealer_network: Mapped[bool] = mapped_column(Boolean, default=False)
    primary_channels_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    current_tools_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    goals_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    pain_points_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    digital_maturity_score: Mapped[int] = mapped_column(default=0)
    automation_maturity_score: Mapped[int] = mapped_column(default=0)


class ModuleRecommendation(Base):
    __tablename__ = "module_recommendations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "module_id", name="uq_tenant_module_recommendation"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    module_id: Mapped[str] = mapped_column(
        ForeignKey("module_catalog.id", ondelete="CASCADE"), index=True
    )
    recommendation_level: Mapped[str] = mapped_column(String(24))
    score: Mapped[int]
    rule_score: Mapped[int] = mapped_column(default=0)
    industry_score: Mapped[int] = mapped_column(default=0)
    ai_score: Mapped[int] = mapped_column(default=0)
    reason: Mapped[str] = mapped_column(Text)
    business_value: Mapped[str] = mapped_column(Text)
    dependency_notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="proposed", index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    module: Mapped[ModuleCatalog] = relationship(lazy="selectin")

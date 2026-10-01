"""Platform foundation and adaptive module framework.

Revision ID: 20261001_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261001_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("plan_code", sa.String(40), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])
    op.create_index("ix_tenants_status", "tenants", ["status"])

    op.create_table(
        "permissions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=False),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "roles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "code", name="uq_role_tenant_code"),
    )
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])

    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.String(36),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            sa.String(36),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            sa.String(36),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "module_catalog",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("business_value", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("is_core", sa.Boolean(), nullable=False),
        sa.Column("is_billable", sa.Boolean(), nullable=False),
        sa.Column("minimum_plan", sa.String(40), nullable=False),
        sa.Column("version", sa.String(24), nullable=False),
        sa.Column("configuration_schema", sa.JSON(), nullable=False),
        sa.Column("navigation", sa.JSON(), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_module_catalog_code", "module_catalog", ["code"])
    op.create_index("ix_module_catalog_category", "module_catalog", ["category"])

    op.create_table(
        "module_dependencies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "module_id",
            sa.String(36),
            sa.ForeignKey("module_catalog.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "depends_on_module_id",
            sa.String(36),
            sa.ForeignKey("module_catalog.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("dependency_type", sa.String(16), nullable=False),
        sa.UniqueConstraint("module_id", "depends_on_module_id", name="uq_module_dependency"),
    )
    op.create_index("ix_module_dependencies_module_id", "module_dependencies", ["module_id"])
    op.create_index(
        "ix_module_dependencies_depends_on_module_id",
        "module_dependencies",
        ["depends_on_module_id"],
    )

    op.create_table(
        "tenant_modules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "module_id",
            sa.String(36),
            sa.ForeignKey("module_catalog.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("configured", sa.Boolean(), nullable=False),
        sa.Column("configuration_json", sa.JSON(), nullable=False),
        sa.Column("module_version", sa.String(24), nullable=False),
        sa.Column("configuration_version", sa.String(24), nullable=False),
        sa.Column("enabled_at", sa.DateTime(timezone=True)),
        sa.Column("disabled_at", sa.DateTime(timezone=True)),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "module_id", name="uq_tenant_module"),
    )
    op.create_index("ix_tenant_modules_tenant_id", "tenant_modules", ["tenant_id"])
    op.create_index("ix_tenant_modules_module_id", "tenant_modules", ["module_id"])
    op.create_index("ix_tenant_modules_status", "tenant_modules", ["status"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("actor_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(80)),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    for table in (
        "audit_logs",
        "tenant_modules",
        "module_dependencies",
        "module_catalog",
        "role_permissions",
        "user_roles",
        "roles",
        "users",
        "permissions",
        "tenants",
    ):
        op.drop_table(table)

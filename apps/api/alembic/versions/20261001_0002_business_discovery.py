"""Business discovery and module recommendations.

Revision ID: 20261001_0002
Revises: 20261001_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261001_0002"
down_revision: str | None = "20261001_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "business_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("industry_code", sa.String(80), nullable=False),
        sa.Column("business_model", sa.String(16), nullable=False),
        sa.Column("customer_type", sa.String(16), nullable=False),
        sa.Column("offering_type", sa.String(16), nullable=False),
        sa.Column("employee_range", sa.String(24), nullable=False),
        sa.Column("location_count", sa.Integer(), nullable=False),
        sa.Column("market_scope", sa.String(40), nullable=False),
        sa.Column("average_sales_cycle_days", sa.Integer(), nullable=False),
        sa.Column("sales_team_size", sa.Integer(), nullable=False),
        sa.Column("requires_leads", sa.Boolean(), nullable=False),
        sa.Column("requires_online_sales", sa.Boolean(), nullable=False),
        sa.Column("requires_appointments", sa.Boolean(), nullable=False),
        sa.Column("requires_quotations", sa.Boolean(), nullable=False),
        sa.Column("requires_field_visits", sa.Boolean(), nullable=False),
        sa.Column("requires_customer_support", sa.Boolean(), nullable=False),
        sa.Column("requires_repeat_business", sa.Boolean(), nullable=False),
        sa.Column("requires_dealer_network", sa.Boolean(), nullable=False),
        sa.Column("primary_channels_json", sa.JSON(), nullable=False),
        sa.Column("current_tools_json", sa.JSON(), nullable=False),
        sa.Column("goals_json", sa.JSON(), nullable=False),
        sa.Column("pain_points_json", sa.JSON(), nullable=False),
        sa.Column("digital_maturity_score", sa.Integer(), nullable=False),
        sa.Column("automation_maturity_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_business_profiles_tenant_id", "business_profiles", ["tenant_id"])
    op.create_index("ix_business_profiles_industry_code", "business_profiles", ["industry_code"])

    op.create_table(
        "module_recommendations",
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
        sa.Column("recommendation_level", sa.String(24), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("rule_score", sa.Integer(), nullable=False),
        sa.Column("industry_score", sa.Integer(), nullable=False),
        sa.Column("ai_score", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("business_value", sa.Text(), nullable=False),
        sa.Column("dependency_notes", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("rejected_at", sa.DateTime(timezone=True)),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "module_id", name="uq_tenant_module_recommendation"),
    )
    op.create_index("ix_module_recommendations_tenant_id", "module_recommendations", ["tenant_id"])
    op.create_index("ix_module_recommendations_module_id", "module_recommendations", ["module_id"])
    op.create_index("ix_module_recommendations_status", "module_recommendations", ["status"])


def downgrade() -> None:
    op.drop_table("module_recommendations")
    op.drop_table("business_profiles")

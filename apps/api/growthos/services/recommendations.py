from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from growthos.models import BusinessProfile, ModuleCatalog, ModuleRecommendation, Tenant


@dataclass(frozen=True)
class Candidate:
    module_code: str
    level: str
    score: int
    reason: str


def maturity_scores(current_tools: dict[str, object]) -> tuple[int, int]:
    digital_keys = ("website", "analytics", "crm", "ecommerce", "booking", "customer_database")
    automation_keys = ("lead_automation", "whatsapp_automation", "email_automation", "workflow")
    digital = round(
        sum(bool(current_tools.get(key)) for key in digital_keys) / len(digital_keys) * 100
    )
    automation = round(
        sum(bool(current_tools.get(key)) for key in automation_keys) / len(automation_keys) * 100
    )
    return digital, automation


def recommendation_candidates(profile: BusinessProfile) -> list[Candidate]:
    candidates: dict[str, Candidate] = {}

    def add(code: str, level: str, score: int, reason: str) -> None:
        existing = candidates.get(code)
        if existing is None or score > existing.score:
            candidates[code] = Candidate(code, level, score, reason)

    if profile.requires_leads:
        add("leads", "essential", 95, "Your business generates enquiries that need follow-up.")
        add(
            "contacts",
            "recommended",
            78,
            "A customer directory supports consistent lead follow-up.",
        )
    if profile.sales_team_size > 1 and profile.requires_leads:
        add(
            "workflow_engine",
            "recommended",
            82,
            "Multiple salespeople benefit from consistent assignment and follow-up.",
        )
    if profile.requires_appointments:
        add("appointments", "essential", 92, "Customers need to book time with your business.")
    if "whatsapp" in profile.primary_channels_json:
        add("whatsapp", "recommended", 88, "WhatsApp is one of your primary customer channels.")
    if "manual_followup" in profile.pain_points_json:
        add("workflow_engine", "essential", 90, "Manual follow-up is a stated business pain point.")
    if profile.industry_code.startswith("real_estate"):
        add(
            "property_listing",
            "recommended",
            84,
            "Property inventory is relevant to this industry profile.",
        )
        if profile.requires_field_visits:
            add(
                "site_visit_booking",
                "essential",
                94,
                "Field visits require structured site-visit scheduling.",
            )
    if profile.requires_online_sales:
        add("product_catalog", "essential", 96, "The business sells products directly online.")
        add("cart", "essential", 93, "Online purchases require a customer cart.")
        add("orders", "essential", 91, "Online sales require order capture and tracking.")
    if {"understand_marketing_roi", "increase_conversion"} & set(profile.goals_json):
        add(
            "analytics", "recommended", 85, "Your growth goals require measurable performance data."
        )
    return sorted(candidates.values(), key=lambda item: item.score, reverse=True)


class RecommendationService:
    def __init__(self, session: AsyncSession, tenant: Tenant) -> None:
        self.session = session
        self.tenant = tenant

    async def generate(self, profile: BusinessProfile) -> list[ModuleRecommendation]:
        catalog = {
            module.code: module
            for module in await self.session.scalars(
                select(ModuleCatalog).where(ModuleCatalog.status == "active")
            )
        }
        generated: list[ModuleRecommendation] = []
        for candidate in recommendation_candidates(profile):
            module = catalog.get(candidate.module_code)
            if module is None:
                continue
            record = await self.session.scalar(
                select(ModuleRecommendation).where(
                    ModuleRecommendation.tenant_id == self.tenant.id,
                    ModuleRecommendation.module_id == module.id,
                )
            )
            if record is None:
                record = ModuleRecommendation(tenant_id=self.tenant.id, module_id=module.id)
                self.session.add(record)
            record.recommendation_level = candidate.level
            record.score = candidate.score
            record.rule_score = candidate.score
            record.industry_score = 20 if profile.industry_code in module.category else 0
            record.ai_score = 0
            record.reason = candidate.reason
            record.business_value = module.business_value
            record.status = "proposed"
            record.generated_at = datetime.now(UTC)
            generated.append(record)
        await self.session.commit()
        for record in generated:
            await self.session.refresh(record, ["module"])
        return generated

    async def set_status(self, recommendation_id: str, new_status: str) -> ModuleRecommendation:
        record = await self.session.scalar(
            select(ModuleRecommendation).where(
                ModuleRecommendation.id == recommendation_id,
                ModuleRecommendation.tenant_id == self.tenant.id,
            )
        )
        if record is None:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        record.status = new_status
        now = datetime.now(UTC)
        if new_status == "accepted":
            record.accepted_at = now
        elif new_status == "rejected":
            record.rejected_at = now
        await self.session.commit()
        await self.session.refresh(record, ["module"])
        return record

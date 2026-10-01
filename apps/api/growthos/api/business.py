from typing import Literal

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from growthos.api.dependencies import CurrentTenant, CurrentUser, SessionDep
from growthos.models import BusinessProfile, ModuleRecommendation
from growthos.schemas import (
    BusinessAssessment,
    BusinessProfileResponse,
    RecommendationResponse,
)
from growthos.services.recommendations import RecommendationService, maturity_scores

router = APIRouter(tags=["business discovery"])


def profile_response(profile: BusinessProfile) -> BusinessProfileResponse:
    return BusinessProfileResponse(
        id=profile.id,
        tenant_id=profile.tenant_id,
        industry_code=profile.industry_code,
        business_model=profile.business_model,  # type: ignore[arg-type]
        customer_type=profile.customer_type,  # type: ignore[arg-type]
        offering_type=profile.offering_type,  # type: ignore[arg-type]
        employee_range=profile.employee_range,
        location_count=profile.location_count,
        market_scope=profile.market_scope,
        average_sales_cycle_days=profile.average_sales_cycle_days,
        sales_team_size=profile.sales_team_size,
        requires_leads=profile.requires_leads,
        requires_online_sales=profile.requires_online_sales,
        requires_appointments=profile.requires_appointments,
        requires_quotations=profile.requires_quotations,
        requires_field_visits=profile.requires_field_visits,
        requires_customer_support=profile.requires_customer_support,
        requires_repeat_business=profile.requires_repeat_business,
        requires_dealer_network=profile.requires_dealer_network,
        primary_channels=profile.primary_channels_json,
        current_tools=profile.current_tools_json,
        goals=profile.goals_json,
        pain_points=profile.pain_points_json,
        digital_maturity_score=profile.digital_maturity_score,
        automation_maturity_score=profile.automation_maturity_score,
    )


def recommendation_response(record: ModuleRecommendation) -> RecommendationResponse:
    return RecommendationResponse(
        id=record.id,
        module_code=record.module.code,
        module_name=record.module.name,
        level=record.recommendation_level,
        score=record.score,
        reason=record.reason,
        business_value=record.business_value,
        dependency_notes=record.dependency_notes,
        status=record.status,
    )


@router.post("/business-assessment", response_model=BusinessProfileResponse)
async def save_assessment(
    body: BusinessAssessment,
    session: SessionDep,
    tenant: CurrentTenant,
    user: CurrentUser,
) -> BusinessProfileResponse:
    del user
    profile = await session.scalar(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    if profile is None:
        profile = BusinessProfile(tenant_id=tenant.id)
        session.add(profile)
    values = body.model_dump(exclude={"primary_channels", "current_tools", "goals", "pain_points"})
    for key, value in values.items():
        setattr(profile, key, value)
    profile.primary_channels_json = body.primary_channels
    profile.current_tools_json = body.current_tools
    profile.goals_json = body.goals
    profile.pain_points_json = body.pain_points
    profile.digital_maturity_score, profile.automation_maturity_score = maturity_scores(
        body.current_tools
    )
    await session.commit()
    await session.refresh(profile)
    return profile_response(profile)


@router.get("/business-profile", response_model=BusinessProfileResponse)
async def get_profile(
    session: SessionDep, tenant: CurrentTenant, user: CurrentUser
) -> BusinessProfileResponse:
    del user
    profile = await session.scalar(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Business assessment has not been completed")
    return profile_response(profile)


@router.put("/business-profile", response_model=BusinessProfileResponse)
async def update_profile(
    body: BusinessAssessment,
    session: SessionDep,
    tenant: CurrentTenant,
    user: CurrentUser,
) -> BusinessProfileResponse:
    return await save_assessment(body, session, tenant, user)


@router.post("/recommendations/generate", response_model=list[RecommendationResponse])
async def generate_recommendations(
    session: SessionDep, tenant: CurrentTenant, user: CurrentUser
) -> list[RecommendationResponse]:
    del user
    profile = await session.scalar(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    if profile is None:
        raise HTTPException(status_code=409, detail="Complete business assessment first")
    records = await RecommendationService(session, tenant).generate(profile)
    return [recommendation_response(record) for record in records]


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def list_recommendations(
    session: SessionDep, tenant: CurrentTenant, user: CurrentUser
) -> list[RecommendationResponse]:
    del user
    records = await session.scalars(
        select(ModuleRecommendation)
        .where(ModuleRecommendation.tenant_id == tenant.id)
        .options(selectinload(ModuleRecommendation.module))
        .order_by(ModuleRecommendation.score.desc())
    )
    return [recommendation_response(record) for record in records]


@router.post("/recommendations/{recommendation_id}/{action}", response_model=RecommendationResponse)
async def review_recommendation(
    recommendation_id: str,
    action: Literal["accept", "reject", "defer"],
    session: SessionDep,
    tenant: CurrentTenant,
    user: CurrentUser,
) -> RecommendationResponse:
    del user
    status = {"accept": "accepted", "reject": "rejected", "defer": "deferred"}[action]
    record = await RecommendationService(session, tenant).set_status(recommendation_id, status)
    return recommendation_response(record)

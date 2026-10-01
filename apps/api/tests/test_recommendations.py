from growthos.models import BusinessProfile
from growthos.services.recommendations import maturity_scores, recommendation_candidates


def profile(**overrides: object) -> BusinessProfile:
    values: dict[str, object] = {
        "tenant_id": "tenant-1",
        "industry_code": "professional_services_it",
        "business_model": "B2B",
        "customer_type": "business",
        "offering_type": "services",
        "sales_team_size": 1,
        "requires_leads": False,
        "requires_online_sales": False,
        "requires_appointments": False,
        "requires_field_visits": False,
        "primary_channels_json": [],
        "current_tools_json": {},
        "goals_json": [],
        "pain_points_json": [],
    }
    values.update(overrides)
    return BusinessProfile(**values)


def test_real_estate_profile_receives_relevant_modules() -> None:
    recommendations = recommendation_candidates(
        profile(
            industry_code="real_estate_developer",
            requires_leads=True,
            requires_field_visits=True,
        )
    )
    codes = {item.module_code for item in recommendations}
    assert {"leads", "property_listing", "site_visit_booking"} <= codes


def test_ecommerce_profile_receives_commerce_stack() -> None:
    recommendations = recommendation_candidates(profile(requires_online_sales=True))
    codes = {item.module_code for item in recommendations}
    assert {"product_catalog", "cart", "orders"} <= codes


def test_appointments_are_not_essential_without_booking_need() -> None:
    recommendations = recommendation_candidates(profile(requires_appointments=False))
    assert not any(
        item.module_code == "appointments" and item.level == "essential" for item in recommendations
    )


def test_maturity_scores_are_bounded_and_evidence_based() -> None:
    digital, automation = maturity_scores({"website": True, "crm": True, "lead_automation": True})
    assert digital == 33
    assert automation == 25

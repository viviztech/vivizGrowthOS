from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    tenant_slug: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    full_name: str
    permissions: list[str]


class ModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    category: str
    description: str
    business_value: str
    is_core: bool
    is_billable: bool
    version: str
    enabled: bool = False
    configured: bool = False
    dependencies: list[str] = Field(default_factory=list)


class ModuleConfiguration(BaseModel):
    values: dict[str, Any]


class EnableModuleRequest(BaseModel):
    source: Literal["manual", "industry_pack", "ai_recommendation"] = "manual"
    activate_dependencies: bool = True


class ModuleActivationResponse(BaseModel):
    enabled: list[str]
    dependencies_activated: list[str]


class NavigationItem(BaseModel):
    label: str
    href: str
    icon: str
    permission: str | None = None
    module_code: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "api"


class BusinessAssessment(BaseModel):
    industry_code: str = Field(min_length=2, max_length=80)
    business_model: Literal["B2B", "B2C", "both"]
    customer_type: Literal["business", "consumer", "both"]
    offering_type: Literal["products", "services", "both"]
    employee_range: str = "1-10"
    location_count: int = Field(default=1, ge=1, le=10000)
    market_scope: str = "local"
    average_sales_cycle_days: int = Field(default=0, ge=0, le=3650)
    sales_team_size: int = Field(default=1, ge=0, le=10000)
    requires_leads: bool = False
    requires_online_sales: bool = False
    requires_appointments: bool = False
    requires_quotations: bool = False
    requires_field_visits: bool = False
    requires_customer_support: bool = False
    requires_repeat_business: bool = False
    requires_dealer_network: bool = False
    primary_channels: list[str] = Field(default_factory=list, max_length=30)
    current_tools: dict[str, bool | str] = Field(default_factory=dict)
    goals: list[str] = Field(default_factory=list, max_length=30)
    pain_points: list[str] = Field(default_factory=list, max_length=30)


class BusinessProfileResponse(BusinessAssessment):
    id: str
    tenant_id: str
    digital_maturity_score: int
    automation_maturity_score: int


class RecommendationResponse(BaseModel):
    id: str
    module_code: str
    module_name: str
    level: str
    score: int
    reason: str
    business_value: str
    dependency_notes: str
    status: str

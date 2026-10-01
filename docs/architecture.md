# Architecture

GrowthOS is a multi-tenant monorepo. The FastAPI service is authoritative for identity, tenant isolation, permissions, plans, module dependencies, and entitlements. The Next.js admin client consumes API-generated navigation and never treats hidden UI as authorization.

## Request authorization

`Bearer token -> active user -> token tenant -> active tenant -> permission -> plan -> module entitlement`

The client cannot select a tenant ID in protected requests. Optional feature routes use the central `FeatureEntitlementService` through FastAPI dependencies.

## Adaptive composition

The module catalog stores permissions and navigation metadata. A tenant module records activation, source, version, and configuration. Navigation is the intersection of enabled tenant modules and user permissions. Required module dependencies are resolved recursively and cycles are rejected.

## Business intelligence

Business assessment data is tenant-scoped. Deterministic rules create recommendations from needs, industry, goals, channels, and pain points. Recommendation review does not activate a module; explicit module enablement remains a separate, entitlement-checked action. The future AI provider will add validated scores and explanations only for known catalog codes.


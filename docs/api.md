# API

Base path: `/api/v1`

## Identity

- `POST /auth/login`
- `GET /auth/me`

## Adaptive modules

- `GET /modules`
- `GET /modules/enabled`
- `POST /modules/{code}/enable`
- `POST /modules/{code}/disable`
- `GET|PUT /modules/{code}/configuration`
- `GET /navigation`

## Business discovery and recommendations

- `POST /business-assessment`
- `GET|PUT /business-profile`
- `POST /recommendations/generate`
- `GET /recommendations`
- `POST /recommendations/{id}/accept`
- `POST /recommendations/{id}/reject`
- `POST /recommendations/{id}/defer`

All endpoints except login and `/health` require a bearer token. Tenant context comes from that token, not a request body or query parameter.


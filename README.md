# VIVIZ GrowthOS

VIVIZ GrowthOS is an adaptive, multi-tenant business growth platform. Each tenant receives a module set based on its profile, plan, and explicit approval. Optional features are enforced by the API and are never exposed only through frontend hiding.

## Architecture

- `apps/admin`: Next.js 16 admin application with adaptive navigation
- `apps/api`: FastAPI, Pydantic v2, async SQLAlchemy and Alembic
- `packages/types`: shared TypeScript contracts
- `docs`: architecture, audit, and implementation tracking
- PostgreSQL/pgvector: persistent tenant data
- Redis: task and cache foundation

## Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+ (pgvector recommended)
- Redis 7+
- Docker Desktop is optional and runs all supporting services

## Setup

1. Copy `.env.example` to `.env` and replace `SECRET_KEY`.
2. API: `cd apps/api`, create a virtual environment, then run `pip install -e .[dev]`.
3. Apply migrations: `alembic upgrade head`.
4. Start API: `uvicorn growthos.main:app --reload`.
5. From the repository root run `npm.cmd install` and `npm.cmd run dev`.

API docs are available at `http://localhost:8000/docs`; the admin application uses `http://localhost:3000`.

For local demo data, run `python -m growthos.seed` from `apps/api`. The seeded workspace is
`viviz-demo` with user `admin@vivizgrowthos.com` and temporary password `ChangeMe123!`.
Change that password before any shared or deployed environment.

## Verification

- API tests: `cd apps/api && pytest`
- API lint: `cd apps/api && ruff check .`
- Admin tests: `npm.cmd test`
- Type check: `npm.cmd run typecheck`
- Production build: `npm.cmd run build`

See `docs/PROJECT_AUDIT.md`, `docs/architecture.md`, `docs/api.md`, `docs/modules.md`,
`PROJECT_STATUS.md`, and `docs/IMPLEMENTATION_STATUS.md` for current scope and limitations.

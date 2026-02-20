Lead Qualification MVP – Agent Guide
===================================

This document is for automated coding agents working in this repo. It summarizes how to build, run, and extend the system safely and consistently.

**Repo Layout**
- Root: `/Users/chetansirohi/Desktop/Revops`
- Backend (FastAPI + LangGraph): `backend`
- Frontend (Next.js App Router + TS): `frontend` (TBD - needs to be restored/recreated)
- Architecture/docs/examples: `examples`

**NOTE:** The frontend folder was lost during repo restructuring. If you have a backup of the frontend files (from Time Machine or other backup), restore them to `./frontend`. Otherwise, recreate using:
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*"
```

**Environment & Services**
- Python: 3.9–3.12 (do **not** assume 3.14 support).
- Node: 18+.
- DB: SQLite file at `backend/data/lead_qualification.db`.
- AI: OpenAI via `OPENAI_API_KEY` (must be set in the environment for backend).

## Commands

**Backend – Setup & Run**
- From `backend`:
  - Create venv: `python3 -m venv venv`
  - Activate venv (macOS/Linux): `source venv/bin/activate`
  - Install deps: `pip install -r requirements.txt`
  - Init/seed DB: `python3 -c "from models.database import init_db, seed_data; init_db(); seed_data()"`
  - Run dev server: `uvicorn main:app --reload --port 8000`
- Health check: `curl http://localhost:8000/health`

**Backend – Tests / Checks**
- There is **no automated test suite** yet (no `pytest`/CI config).
- Use `test_commands.sh` as the canonical manual test script.
  - Example single-endpoint test (health):
    - `curl http://localhost:8000/health | python3 -m json.tool`
  - Example single workflow test (lead 1):
    - `curl -X POST http://localhost:8000/api/leads/1/qualify | python3 -m json.tool`
- If you introduce `pytest`, prefer this pattern (do **not** assume it exists today):
  - All tests in `backend/tests/`.
  - Run all tests: `pytest`.
  - Run a single test file: `pytest backend/tests/test_workflow.py`.
  - Run a single test function: `pytest backend/tests/test_workflow.py::test_human_review_flow`.

**Frontend – Setup & Run**
- From `frontend`:
  - Install deps: `npm install`
  - Dev server: `npm run dev` (http://localhost:3000)
  - Production build: `npm run build`
  - Start production server: `npm run start`
  - Lint (ESLint + Next core web vitals + TS): `npm run lint`
- There is **no frontend test runner** configured (no Jest/Vitest). If you add one, wire it to `npm test` and document it here.

**End-to-End Manual Flow (for agents)**
- Ensure backend and frontend are both running.
- Visit `http://localhost:3000`:
  - Qualify a lead on `/leads`.
  - For medium-score leads (5–7), review/decide on `/pending-reviews`.
  - Confirm stats and workflow metrics on `/` (dashboard).

## Code Style – General

**Imports & Module Boundaries**
- Python (backend):
  - Order: stdlib → third-party → local (`models.*`, `agents.*`).
  - Avoid circular imports; keep DB access in `models/database.py` and schemas in `models/schemas.py`.
- TypeScript/TSX (frontend):
  - Use path alias `@/*` defined in `tsconfig.json` (e.g. `@/lib/api`, `@/components/Sidebar`).
  - Prefer a single import line per module group; keep React/Next imports at the top.

**Formatting**
- Backend:
  - 4-space indentation, no tabs.
  - Double quotes or single quotes are both present; be consistent within a file.
  - Keep existing docstring style (`"""..."""` at top of module and above endpoints where needed).
- Frontend:
  - Use semicolons and single quotes for strings, matching existing TS/TSX files.
  - Keep JSX on multiple lines for complex structures; prefer readable mapping over clever one-liners.
  - Let ESLint (`eslint.config.mjs`) and Next conventions drive spacing and unused imports.

**Types & Nullability**
- Python:
  - Use `typing` (`Optional`, `List`, etc.) and Pydantic models from `models/schemas.py` for external shapes.
  - Keep enums as `Enum` subclasses with UPPER_CASE names and lowercase string values (see `LeadStatus`).
  - For DB helpers, return typed models (`Lead`, `SalesRep`, `WorkflowState`) instead of raw tuples.
- TypeScript:
  - `strict` mode is enabled; always type function parameters and return values for exported functions.
  - Use explicit union types for status fields (e.g. `'new' | 'analyzing' | ...` in `lib/api.ts`).
  - Prefer interfaces for data models (`Lead`, `DashboardStats`, `WorkflowMetrics`).

**Naming Conventions**
- Python:
  - Functions, variables: `snake_case` (`get_all_leads`, `thread_id`).
  - Classes and Pydantic models: `PascalCase` (`Lead`, `DashboardStats`).
  - Constants: `UPPER_SNAKE_CASE` (e.g. `DB_PATH`).
- TypeScript/React:
  - Components: `PascalCase` (`DashboardPage`, `Sidebar`).
  - Hooks/state: `camelCase` (`useState`, `loadLeads`, `pendingCount`).
  - Props interfaces: `PascalCase` with `Props` suffix when appropriate (`ResetDatabaseButtonProps`).

## Backend Guidelines (FastAPI + LangGraph)

**Routing & Schemas**
- Define HTTP endpoints in `backend/main.py` only; keep pure business logic in `models` and `agents` modules.
- Always use Pydantic models from `models/schemas.py` for request/response bodies and `response_model` declarations.
- When adding status values, update **both** `LeadStatus` and any SQL queries that filter on `status`.

**Database Access**
- Use helpers from `models/database.py` for all DB operations.
- Do not open ad-hoc SQLite connections in random modules.
- When adding new columns/tables, update `init_db()` to create them and, if needed, `seed_data()`.

**Error Handling**
- Use `HTTPException` for client-visible failures with appropriate status codes:
  - 400 for invalid input (e.g. bad `decision`, missing `thread_id`).
  - 404 for missing resources (e.g. unknown `lead_id`).
  - 500 for unexpected internal errors (e.g. workflow failures).
- Preserve idempotency where the architecture expects it:
  - `resume_workflow` with `Command(resume=...)` must be safe to retry; avoid side effects that double-apply.
- When catching broad `Exception`, reset any transient state (e.g. lead status) before raising `HTTPException`.

**Thread & Workflow Semantics (Critical)**
- `thread_id` is the primary key for workflow instances:
  - Format: `lead_{lead_id}_{timestamp}` in `qualify_lead_endpoint`.
  - When creating new flows, **never drop or invent** a `thread_id`; always reuse or propagate the one from upstream.
- When modifying HITL endpoints:
  - `POST /api/leads/{id}/qualify` must return `thread_id` whenever a workflow is started.
  - `POST /api/leads/{id}/human-decision` must require `thread_id` and pass it to `resume_workflow`.
  - `GET /api/leads/{id}/workflow-status` should read from `workflow_states` via `get_workflow_status`.

## Frontend Guidelines (Next.js App Router)

**Routing & Components**
- App router is used (`frontend/app/*`). Pages are server or client components as declared by `'use client';`.
- Keep layout concerns in `app/layout.tsx` and domain UI in route-specific `page.tsx` files.
- Use `Sidebar` as the global navigation; do not duplicate nav logic elsewhere.

**Data Fetching Layer**
- All network traffic to the backend should go through `frontend/lib/api.ts`:
  - Add new typed functions here for each new backend endpoint.
  - Reuse exported interfaces (`Lead`, `PendingReview`, `WorkflowMetrics`, etc.).
- Do **not** call `fetch('http://localhost:8000/...')` directly from components; wrap it in `lib/api.ts` to centralize error handling and types.

**State & Error Handling**
- Store async-loading state explicitly (`loading`, `processing`, `qualifying`) using `useState`.
- Catch errors around awaits and log with `console.error('context message', error)`; surface user-friendly messages in the UI.
- For critical flows (HITL):
  - Ensure you always pass the `thread_id` returned by `qualifyLead` into `submitHumanDecision`.
  - Validate required values in client components and show a clear error (see `PendingReviewsPage.handleDecision`).

**Styling & Layout**
- Use Tailwind CSS utility classes as primary styling mechanism.
- Respect existing theming from `app/globals.css` and shadcn/tailwind imports.
- Prefer simple, composable Tailwind classes over adding new global CSS (unless you need theme-level changes).

## Testing & Validation Practices

**Manual API Testing**
- Use `test_commands.sh` as the source of truth for manual QA:
  - Health, CRUD, qualification, HITL, dashboard stats, workflow metrics, and DB reset endpoints are all covered.
- For one-off checks, copy commands from that script rather than inventing new ad-hoc flows.

**When Adding Automated Tests**
- Backend:
  - Use `pytest` with FastAPI `TestClient` or HTTPX async client.
  - Focus on: workflow edge cases, HITL resume logic, DB consistency, and error handling.
- Frontend:
  - Add a test runner (e.g. Vitest + Testing Library) and integrate with `npm test`.
  - Test UI state transitions for `/leads` and `/pending-reviews` pages.

## Agent-Specific Notes

- Keep backend and frontend URLs in sync:
  - Backend CORS: `allow_origins=["http://localhost:3000"]` in `main.py`.
  - Frontend base URL: `API_BASE_URL` in `frontend/lib/api.ts`.
- When changing API shapes, update **all** of:
  - FastAPI endpoint response schemas.
  - Pydantic models in `models/schemas.py`.
  - TS interfaces and callers in `frontend/lib/api.ts` and relevant pages/components.
- Do not modify files under `node_modules/` (including third-party `AGENTS.md`).

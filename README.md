# RecallOS

**A persistent AI memory platform — built on [Cognee](https://www.cognee.ai/). Its first app: interview prep that remembers you.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
&nbsp;Python 3.12 · FastAPI · React 18 · TypeScript · Cognee · PostgreSQL · Supabase

RecallOS builds a living **competency graph** per learner. It doesn't store transcripts — it
stores what each answer *revealed*, accumulates that across unlimited sessions, and uses an
authored **prerequisite graph** to diagnose the single upstream concept (the **root cause**)
behind several recurring weaknesses. Then it tells you what to fix first.

> The moment that makes it click: *"Caching, database round-trips, and distributed transactions
> aren't three separate weaknesses — they all build on **Consistency Models**, which you've never
> been asked about."* That conclusion lives in no single session; the graph assembles it.

Chat history has no relationships; vector search returns the three failures as independently
"similar" and can never say they **converge**. It's a graph problem — which is why Cognee is the
core engine, not a swappable store.

---

## Features

- **Competency graph memory** — every scored answer becomes evidence in a per-user knowledge
  graph; memory compounds across sessions.
- **Deterministic root-cause diagnosis** — a pure traversal over an authored prerequisite
  ontology, so the diagnosis is trustworthy on every run (never an LLM guess).
- **LLM answer scoring** — free-text answers are graded 0–5 by an interviewer-style model with a
  rationale and demonstrated/missed concepts.
- **The four memory verbs** — Remember, Recall, Improve (memify), Forget — mapped onto Cognee's
  native API.
- **Authentication & multi-tenancy** — provider-agnostic OIDC/JWKS verification (Supabase as the
  initial provider); per-user data isolation across the ledger and Cognee datasets.
- **Production hardening** — IP rate limiting, a sandboxed demo account, and an admin reset
  command.

## Architecture

Clean / hexagonal: a domain-agnostic **platform core** with **interview prep** as the first app.
The core is pure (no framework, DB, or Cognee imports) and that purity is enforced in CI by
`import-linter`.

```
            ┌──────────────────────────── api (FastAPI) ────────────────────────────┐
 HTTP  ───▶ │  /api/v1: provision · answers · diagnosis · graph · improve · forget   │
            │  auth (verify OIDC bearer) · rate limiting · error mapping             │
            └───────────────┬───────────────────────────────────────────────────────┘
                            │ depends on ports only
            ┌───────────────▼──────────── core (pure) ──────────────┐
            │  domain:      Concept · PrereqGraph · Ontology ·       │
            │               Mastery · RootCause · AnswerAssessment   │
            │  application: use-cases (Provision/Remember/Score/     │
            │               Diagnose/Improve/Forget/Reset) + ports   │
            └───────────────┬───────────────────────────────────────┘
                            │ ports implemented by
            ┌───────────────▼──────────── adapters ─────────────────┐
            │  CogneeMemoryEngine (the only `import cognee`)         │
            │  PostgresEvidenceLedger · PostgresUserRepository       │
            │  JwtPrincipalVerifier (OIDC) · GeminiAnswerScorer      │
            │  FileOntologyRepository  (+ in-memory test doubles)    │
            └───────────────────────────────────────────────────────┘
```

- **Cognee** (in-process: SQLite + Kuzu + LanceDB) is the memory/retrieval/reasoning engine.
- **PostgreSQL** is the durable evidence ledger and the source of truth for mastery; it never
  stores concept relationships — those belong to the authored ontology and the Cognee graph.
- **Supabase** handles authentication only; the server trusts standard JWTs verified against the
  issuer's JWKS, so the provider is swappable by configuration.
- The **root-cause decision is deterministic** — Cognee powers the memory, retrieval, narration,
  and improve around it.

## Tech stack

| Layer | Technologies |
|---|---|
| **Server** | Python 3.12, FastAPI, SQLAlchemy + Alembic, Cognee, PostgreSQL, slowapi, PyJWT, Pydantic |
| **Memory / AI** | Cognee (Kuzu + LanceDB), Google Gemini (`gemini-2.5-flash` + `gemini-embedding-001`) |
| **Client** | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, React Hook Form + Zod, Framer Motion, React Flow, Supabase JS |
| **Auth** | Supabase (OIDC/JWKS) — provider-agnostic on the server |
| **Testing** | pytest, import-linter, Vitest + Testing Library, Playwright |

## Screenshots

> _Placeholders — add captures before publishing._

| Landing | Session (root cause) | Memory |
|---|---|---|
| ![Landing](screenshots/landing.png) | ![Session](screenshots/session.png) | ![Memory](screenshots/memory.png) |

## Local setup

**Prerequisites:** Python 3.12, Node 22, a PostgreSQL database (local via Docker or managed), a
Google AI Studio key, and a Supabase project for auth.

```bash
# 0. (optional) a local Postgres
docker compose up -d postgres

# 1. Server
cd server
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # fill in the values below
alembic upgrade head          # create tables

# 2. Client (new terminal)
cd client
npm install
cp .env.example .env.local    # fill in the values below
```

> On first boot Cognee downloads a Kuzu graph extension, so the server needs outbound network the
> first time (or pre-install it in your image).

## Environment variables

**`server/.env`**

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` / `LLM_API_KEY` / `EMBEDDING_API_KEY` | Google AI Studio key(s) for the LLM + embeddings |
| `LLM_MODEL` / `EMBEDDING_MODEL` / `EMBEDDING_DIMENSIONS` | Cognee model config (defaults to Gemini) |
| `DATABASE_URL` | PostgreSQL URL (`postgresql+psycopg2://…`) |
| `COGNEE_SYSTEM_DIR` / `COGNEE_DATA_DIR` | Local Cognee store locations |
| `OIDC_ISSUER` / `OIDC_AUDIENCE` / `OIDC_JWKS_URL` | OIDC verification (Supabase: `https://<ref>.supabase.co/auth/v1`, `authenticated`, `…/.well-known/jwks.json`) |
| `CORS_ORIGINS` | Allowed client origins |
| `DEMO_EMAIL` | The sandboxed demo account (used by the reset script) |

**`client/.env.local`**

| Variable | Description |
|---|---|
| `VITE_API_URL` | Server base URL (e.g. `http://localhost:8000`) |
| `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` | Supabase project URL + publishable key |
| `VITE_DEMO_EMAIL` / `VITE_DEMO_PASSWORD` | Credentials for the "Try the demo" button |

## Running

```bash
# Server  →  http://localhost:8000   (OpenAPI at /docs)
cd server && .venv/bin/uvicorn recallos.api.app:app --port 8000 --reload

# Client  →  http://localhost:5173
cd client && npm run dev
```

Then: **Get started** (or **Try the demo**) → answer questions (score low on Caching / DB Round
Trips / Distributed Transactions) → watch the graph recolor and **Consistency Models surface as
the root cause** → **Memory** → Improve / Forget → reload to confirm your memory persisted.

Reset the demo account's data in place (preserves the account):

```bash
cd server && .venv/bin/python -m recallos.scripts.reset_demo
```

## Testing

```bash
# Server — fast, offline suite + architecture boundary
cd server
.venv/bin/python -m pytest -q
.venv/bin/lint-imports
# Server — live integration (real Cognee + Gemini + Postgres); run with the sandbox/network on
.venv/bin/python -m pytest tests/api/test_api_integration.py -m integration -o addopts=""

# Client — unit/component, then a real-browser E2E (servers must be running)
cd client
npm run test
npx tsc --noEmit && npm run build
npx playwright test
```

## Project structure

```
.
├── server/                     # Python / FastAPI backend
│   ├── recallos/
│   │   ├── core/               # pure domain + application (use-cases, ports)
│   │   ├── adapters/           # cognee · persistence · auth · scoring · ontology
│   │   ├── api/                # FastAPI app, routers, deps, schemas, errors
│   │   ├── apps/interview_prep # the Backend-SDE ontology (data, not code)
│   │   ├── scripts/            # admin scripts (e.g. reset_demo)
│   │   └── config.py
│   ├── migrations/             # Alembic
│   └── tests/                  # domain · application · adapters · api · contracts
├── client/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── lib/auth/           # AuthService abstraction (the only Supabase seam)
│   │   ├── lib/api/            # typed client, hooks, schemas
│   │   ├── features/           # graph · session · memory
│   │   ├── screens/            # landing · auth · session · memory
│   │   └── components/
│   └── e2e/                    # Playwright specs
├── docker-compose.yml          # local PostgreSQL
└── LICENSE
```

## Roadmap

- [x] Pure platform core + authored ontology (interview-prep v1)
- [x] Cognee memory engine + Postgres ledger + `/api/v1`
- [x] React client (interactive competency graph)
- [x] Authentication, multi-tenancy & rate limiting (Supabase OIDC)
- [x] LLM answer scoring
- [ ] Async cognify (background ingestion)
- [ ] Server-side session history
- [ ] Deployment, observability & CI/CD
- [ ] Additional learning domains beyond Backend-SDE

## Contributing

Contributions are welcome.

- Keep `recallos.core` pure — no framework/DB/Cognee imports. `import-linter` enforces this; run
  `lint-imports` before opening a PR.
- Prefer native Cognee capabilities over custom implementations.
- Formatting/linting: server uses `black` + `isort`; client uses `prettier` + `eslint`.
- Add a test with every behavior change; keep the fast suites green
  (`pytest -q`, `npm run test`).

## License

[MIT](./LICENSE) © 2026 Saurabh Mahapatra

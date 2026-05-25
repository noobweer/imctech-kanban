# Gemini CLI Context: imctech-kanban

## Agent Behavior

Always follow the **karpathy-guidelines** skill when writing, reviewing, or refactoring any code in this project:

- Think before coding. Surface assumptions and tradeoffs. Ask when uncertain.
- Simplicity first. Minimum code that solves the problem. Nothing speculative.
- Surgical changes. Touch only what the request requires. Match existing style.
- Goal-driven execution. Define verifiable success criteria before starting.

## Project Overview

A full-stack Kanban board application featuring a Django-based backend and a Vue 3 frontend. The project is containerized using Docker and uses modern package managers (`uv` for Python, `bun` for Node.js).

- **Architecture:** Monorepo with `backend/` and `frontend/` directories.
- **Backend:** Django 6.0.4, Django Ninja (API), Django Ninja JWT (Authentication), SQLite database.
- **Frontend:** Vue 3 (Composition API), Vite 8, Pinia (State Management), TypeScript, Tailwind CSS 4.
- **Communication:** Frontend uses `ofetch` to interact with the Django Ninja API (`/api/`).

## Building and Running

### Docker (Recommended)

```bash
# Start all services
docker-compose up

# Rebuild and start
docker-compose up --build
```

### Manual Setup

#### Backend

```bash
cd backend
# Install dependencies
uv sync
# Apply migrations
uv run python manage.py migrate
# Start dev server
uv run python manage.py runserver
```

- API Docs: `http://localhost:8000/api/docs` (Swagger)

#### Frontend

```bash
cd frontend
# Install dependencies
bun install
# Start dev server
bun run dev
```

- Dev Server: `http://localhost:5173`

## Development Conventions

### Backend

- **Framework:** Django with [Django Ninja](https://django-ninja.rest-framework.com/) for type-safe APIs.
- **Authentication:** JWT-based. Logic resides in the `users` app (`users/api.py`, `users/models.py`).
- **Migrations:** Always run `uv run python manage.py makemigrations` and `migrate` after model changes.
- **Timezone:** `Asia/Vladivostok`.
- **Verify:** Run `uv run manage.py check` inside the Docker container (`docker compose exec backend bash`).

#### Backend Architecture: Layered Structure

The `pb` app follows a strict three-layer architecture. Never mix layers.

```
backend/pb/
    models.py          # Data layer — Django ORM models only. No business logic.
    schemas.py         # Serialization layer — Django Ninja Schema (in/out DTOs).
    permissions.py     # Permission helpers — pure functions, no HTTP.
    admin.py           # Django admin registrations.
    migrations/        # Auto-generated migrations.

    services/          # Business logic layer
        project_service.py
        board_service.py
        column_service.py
        invite_service.py
        member_service.py
        task_service.py

    routers/           # HTTP layer (thin)
        __init__.py    # Combines all routers into one exported `router`
        projects.py
        boards.py
        columns.py
        invites.py
        members.py
        tasks.py

    api.py             # Stub: `from .routers import router` — do not add logic here.
```

#### Layer Rules

**Services (`pb/services/`)**
- Pure Python functions. No `request` object. No HTTP responses.
- Receive typed primitive arguments (user, model instances, validated payload).
- Raise standard Python exceptions for error cases:
  - `ValueError` — invalid input (translated to HTTP 400)
  - `PermissionError` — authorization failure (translated to HTTP 403)
  - `LookupError` / `Model.DoesNotExist` — not found (translated to HTTP 404)
- Return model instances or raise — never return HTTP status codes.

**Routers (`pb/routers/`)**
- Thin HTTP handlers only. Each endpoint should follow this exact pattern:
  1. Fetch object (`get_object_or_404`)
  2. Check permission (`permissions.py`)
  3. Call service function
  4. Return schema or HTTP error
- No business logic, no DB queries beyond `get_object_or_404`.
- Max ~15 lines per endpoint.

**Models (`pb/models.py`)**
- Django ORM models and enums only.
- `clean()` for field-level validation, `save()` calls `full_clean()`.
- No service logic, no API code.

#### Adding a New Endpoint

1. Add business logic to the relevant `services/*.py` file.
2. Add a thin handler in the relevant `routers/*.py` file.
3. If a new schema is needed, add it to `schemas.py`.
4. If a new permission check is needed, add it to `permissions.py`.
5. Run `uv run manage.py check` to verify.


### Frontend

- **Framework:** Vue 3 with Composition API and `<script setup>`.
- **State:** [Pinia](https://pinia.vuejs.org/) stores in `frontend/src/stores/`.
- **API:** Centralized in `frontend/src/api/`. Uses `ofetch` with automated token refresh.
- **Styling:** Tailwind CSS 4.
- **Linting/Formatting:**
  - `bun run lint` (uses `oxlint` and `eslint`)
  - `bun run format` (uses `prettier`)
  - `bun run type-check` (uses `vue-tsc`)

### General

- **Environment Variables:** Managed via `.env` file in the root. Use `.env.example` as a template.
- **Language:** Code and comments are primarily in English, but Russian documentation/comments may exist (e.g., in `README.md`).

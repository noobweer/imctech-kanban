# Gemini CLI Context: imctech-kanban

## Agent Behavior

Always follow the **karpathy-guidelines** skill when writing, reviewing, or refactoring any code in this project:

- Think before coding. Surface assumptions and tradeoffs. Ask when uncertain.
- Simplicity first. Minimum code that solves the problem. Nothing speculative.
- Surgical changes. Touch only what the request requires. Match existing style.
- Goal-driven execution. Define verifiable success criteria before starting.

## Project Overview

A full-stack Kanban board application featuring a Django-based backend and a Vue 3 frontend. The project is containerized using Docker and uses modern package managers (`uv` for Python, `bun` for Node.js).

- **Architecture:** Monorepo with `backend/` and `frontend/` directories. Dockerized.
- **Backend:** Django 6.0.4, Django Ninja (API), Django Channels (WebSockets via InMemoryChannelLayer), Django Ninja JWT (Authentication), PostgreSQL database.
- **Frontend:** Vue 3 (Composition API), Vite 8, Pinia (State Management), TypeScript, Tailwind CSS 4.
- **Communication:** Frontend uses `ofetch` to interact with the Django Ninja API (`/api/`) and native `WebSocket` for real-time board updates (`/ws/boards/...`).

## Building and Running

### Docker

```bash
# Start all services
docker-compose up

# Rebuild and start
docker-compose up --build
```

### Running Commands (Agent Instructions)

**Crucial:** Since the project is strictly dockerized, you MUST run all development and verification commands inside the running containers using `docker-compose exec` if you need to interact with the environment, or run them locally ONLY IF you are absolutely certain the local environment matches and it's safe (e.g. static type checks).

#### Backend (Python/Django)
To run django management commands, tests, or linters:
```bash
docker-compose exec backend uv run python manage.py <command>
# Example:
docker-compose exec backend uv run python manage.py makemigrations
docker-compose exec backend uv run python manage.py migrate
docker-compose exec backend uv run python manage.py check
```

#### Frontend (Node/Bun)
To run formatters, linters, or type-checks:
```bash
docker-compose exec frontend bun run <script>
# Example:
docker-compose exec frontend bun run type-check
docker-compose exec frontend bun run lint
docker-compose exec frontend bun run format
```

## Development Conventions

### Backend

- **Framework:** Django with [Django Ninja](https://django-ninja.rest-framework.com/) for type-safe APIs.
- **Authentication:** JWT-based. Logic resides in the `users` app (`users/api.py`, `users/models.py`).
- **Migrations:** Always run migrations inside the container: `docker-compose exec backend uv run python manage.py makemigrations` and `docker-compose exec backend uv run python manage.py migrate` after model changes.
- **Timezone:** `Asia/Vladivostok`.
- **Verify:** Run verification inside the Docker container: `docker-compose exec backend uv run python manage.py check`.

#### Backend Architecture: Layered Structure

The `pb` app follows a strict three-layer architecture. Never mix layers.

```
backend/pb/
    models.py          # Data layer — Django ORM models only. No business logic.
    permissions.py     # Permission helpers — pure functions, no HTTP.
    admin.py           # Django admin registrations.
    migrations/        # Auto-generated migrations.

    schemas/           # Serialization layer — Django Ninja Schemas (in/out DTOs).
        __init__.py
        boards.py
        columns.py
        comments.py
        invites.py
        members.py
        mentor_requests.py
        projects.py
        tasks.py

    services/          # Business logic layer
        activity_service.py
        archive_service.py
        board_service.py
        column_service.py
        comment_service.py
        invite_service.py
        member_service.py
        mentor_request_service.py
        overview_service.py
        project_service.py
        task_lifecycle.py
        task_service.py
        ws_service.py

    routers/           # HTTP layer (thin)
        __init__.py    # Combines all routers into one exported `router`
        boards.py
        columns.py
        comments.py
        invites.py
        members.py
        mentor_requests.py
        overview.py
        projects.py
        tasks.py

    websockets/        # WebSocket layer (Django Channels consumers)
        consumers.py
        routing.py

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
- **Linting/Formatting (Run via docker-compose exec frontend):**
  - `docker-compose exec frontend bun run lint`
  - `docker-compose exec frontend bun run format`
  - `docker-compose exec frontend bun run type-check`

### General

- **Environment Variables:** Managed via `.env` file in the root. Use `.env.example` as a template.
- **Language:** Code and comments are primarily in English, but Russian documentation/comments may exist (e.g., in `README.md`).

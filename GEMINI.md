# Gemini CLI Context: imctech-kanban

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

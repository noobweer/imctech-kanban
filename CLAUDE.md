# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A kanban board application with a Django backend and Vue 3 frontend, containerized with Docker.

## Architecture

**Backend (Django 6.0.4)**
- Located in `backend/` directory
- Uses Django Ninja for API endpoints
- Configuration in `backend/config/` (settings, urls, wsgi, asgi)
- SQLite database (db.sqlite3)
- Python 3.12+ with uv package manager
- CORS headers configured via django-cors-headers
- Environment variables loaded from root `.env` file via python-dotenv

**Frontend (Vue 3 + TypeScript)**
- Located in `frontend/` directory
- Vue 3 with Composition API
- Vite 8 for build tooling
- Pinia for state management
- Vue Router 5 for routing
- Bun as package manager
- Path alias: `@` maps to `frontend/src/`
- Linting: oxlint + ESLint with Prettier formatting

**Docker Setup**
- Backend runs on port 8000
- Frontend runs on port 5173
- Volumes mounted for hot-reload during development
- Backend uses uv, frontend uses bun

## Development Commands

**Full Stack (Docker)**
```bash
# Start both services
docker-compose up

# Rebuild containers
docker-compose up --build

# Stop services
docker-compose down
```

**Backend (Django)**
```bash
cd backend

# Install dependencies
uv sync

# Run development server
uv run python manage.py runserver

# Run migrations
uv run python manage.py migrate

# Create migrations
uv run python manage.py makemigrations

# Create superuser
uv run python manage.py createsuperuser

# Django shell
uv run python manage.py shell
```

**Frontend (Vue)**
```bash
cd frontend

# Install dependencies
bun install

# Run development server
bun run dev

# Build for production
bun run build

# Type checking
bun run type-check

# Lint and fix
bun run lint

# Format code
bun run format

# Preview production build
bun run preview
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to True for development
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

The backend loads environment variables from the root `.env` file (one level up from backend/).

## Key Files

- `backend/config/settings.py`: Django settings, loads from .env
- `backend/config/urls.py`: URL routing
- `frontend/src/main.ts`: Vue app entry point
- `frontend/src/router/index.ts`: Vue Router configuration (currently empty routes)
- `frontend/vite.config.ts`: Vite configuration with @ alias
- `docker-compose.yml`: Container orchestration

## Timezone

Backend is configured for `Asia/Vladivostok` timezone.

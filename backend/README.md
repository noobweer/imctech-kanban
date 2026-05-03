# Kanban Backend

Django backend with JWT authentication and User management API.

## Stack

- Python 3.12+
- Django 6.0.4
- Django Ninja 1.6.2
- Django Ninja JWT 5.4.4
- SQLite

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Apply migrations:
```bash
uv run python manage.py migrate
```

3. Create superuser (optional):
```bash
uv run python manage.py createsuperuser
```

4. Run development server:
```bash
uv run python manage.py runserver
```

Server runs at http://localhost:8000

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/api/docs
- OpenAPI schema: http://localhost:8000/api/openapi.json

See [docs/api-overview.md](docs/api-overview.md) for detailed endpoint documentation.

## Quick Test

1. Register user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "12345678",
    "name": "Test Student",
    "role": "student"
  }'
```

2. Login (get tokens):
```bash
curl -X POST http://localhost:8000/api/token/pair \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "12345678"
  }'
```

3. Use access token:
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```
backend/
├── config/          # Django settings and URLs
├── users/           # User management app
│   ├── models.py    # UserProfile model
│   ├── schemas.py   # Ninja schemas
│   ├── api.py       # API endpoints
│   └── admin.py     # Django admin
├── manage.py
└── pyproject.toml
```

## Environment Variables

Create `.env` file in project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
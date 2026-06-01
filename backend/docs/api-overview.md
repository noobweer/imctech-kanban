# API Overview

Base URL: `http://localhost:8000/api`

## Authentication

All endpoints except `/auth/register` and `/token/*` require JWT authentication.

Include token in Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Routers Documentation

- [Auth](auth.md)
- [Users](users.md)
- [Projects](projects.md)
- [Boards](boards.md)
- [Columns](columns.md)
- [Invites](invites.md)
- [Members](members.md)
- [Tasks](tasks.md)
- [Comments](comments.md)

## User Roles

- `student` - Default role
- `mentor` - Mentor role

Roles are enforced at the endpoint level:
*   **student**: Can interact with tasks, but cannot create projects or boards.
*   **mentor**: Can manage boards and columns (invited mentors act as co-managers), but cannot create, modify, move, or archive tasks.

## Security Notes

- Passwords hashed using Django's password hashing
- Password never returned in API responses
- JWT tokens expire after 60 minutes (access) / 1 day (refresh)
- CORS configured for `http://localhost:5173`

## Testing Flow

1. Register user → get user data
2. Login → get access + refresh tokens
3. Use access token for protected endpoints
4. Refresh token when access expires
5. Test CRUD operations with proper permissio

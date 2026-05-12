# API Overview

Base URL: `http://localhost:8000/api`

## Authentication

All endpoints except `/auth/register` and `/token/*` require JWT authentication.

Include token in Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### Auth Endpoints

#### POST /auth/register
Register new user.

**Request:**
```json
{
  "username": "test_student",
  "password": "12345678",
  "name": "Test Student",
  "role": "student"
}
```

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Test Student",
  "role": "student",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T10:00:00Z"
}
```

**Errors:**
- `400` - Username already exists

---

#### POST /token/pair
Login and get JWT tokens.

**Request:**
```json
{
  "username": "test_student",
  "password": "12345678"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errors:**
- `401` - Invalid credentials

---

#### POST /token/refresh
Refresh access token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### GET /auth/me
Get current authenticated user.

**Auth:** Required

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Test Student",
  "role": "student",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T10:00:00Z"
}
```

---

### User CRUD Endpoints

#### GET /users
List all users.

**Auth:** Required

**Response:** `200 OK`
```json
[
  {
    "username": "test_student",
    "name": "Test Student",
    "role": "student",
    "created_at": "2026-05-03T10:00:00Z",
    "updated_at": "2026-05-03T10:00:00Z"
  },
  {
    "username": "mentor1",
    "name": "John Mentor",
    "role": "mentor",
    "created_at": "2026-05-03T09:00:00Z",
    "updated_at": "2026-05-03T09:00:00Z"
  }
]
```

---

#### GET /users/{username}
Get user by username.

**Auth:** Required

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Test Student",
  "role": "student",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T10:00:00Z"
}
```

**Errors:**
- `404` - User not found

---

#### PATCH /users/{username}
Update user.

**Auth:** Required  
**Permissions:** User can update self, or staff can update anyone

**Request:**
```json
{
  "name": "Updated Name",
  "role": "mentor",
  "password": "newpassword123"
}
```

All fields optional.

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Updated Name",
  "role": "mentor",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T11:00:00Z"
}
```

**Errors:**
- `403` - Permission denied
- `404` - User not found

---

#### DELETE /users/{username}
Delete user.

**Auth:** Required  
**Permissions:** User can delete self, or staff can delete anyone

**Response:** `200 OK`
```json
{
  "success": true
}
```

**Errors:**
- `403` - Permission denied
- `404` - User not found

---

### Project CRUD Endpoints

#### GET /projects
List all projects accessible to the user.
*   **Auth:** Required
*   **Access:** User sees projects where they own or are a member of at least one board. Staff sees all.

#### POST /projects
Create a new project.
*   **Auth:** Required

#### GET /projects/{project_id}
Get project details.
*   **Auth:** Required

#### PATCH /projects/{project_id}
Update project name.
*   **Auth:** Required

#### DELETE /projects/{project_id}
Delete project (fails if boards exist).
*   **Auth:** Required

---

### Board CRUD Endpoints

#### GET /boards
List all boards accessible to the user.
*   **Auth:** Required
*   **Query Params:** `status` (active/archived)

#### POST /boards
Create a new board.
*   **Auth:** Required

#### GET /boards/{board_id}
Get board details.
*   **Auth:** Required

#### PATCH /boards/{board_id}
Update board (name/status).
*   **Auth:** Required

#### DELETE /boards/{board_id}
Archive board.
*   **Auth:** Required

---

## User Roles

- `student` - Default role
- `mentor` - Mentor role

Roles stored but not enforced in current implementation.

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
5. Test CRUD operations with proper permissions

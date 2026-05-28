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

### Column CRUD Endpoints

#### GET /boards/{board_id}/columns
List columns of a board.
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Query Params:** `status` (active/archived)

#### GET /columns/{column_id}
Get column details.
*   **Auth:** Required
*   **Access:** Owner, member, or staff of the associated board.

#### POST /boards/{board_id}/columns
Create a new column.
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### PATCH /columns/{column_id}
Update column (name/status).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### POST /columns/{column_id}/move
Change column position.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Request:** `{"position": 1}`

#### POST /columns/{column_id}/archive
Archive column.
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### DELETE /columns/{column_id}
Soft delete column (sets status to archived).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### POST /boards/{board_id}/columns/defaults
Create default columns (To Do, In Progress, Done).
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Condition:** Board must have no existing columns.

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
5. Test CRUD operations with proper permissio
---

### Invite Endpoints

#### GET /boards/{board_id}/invites
List all invites for a board.
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### GET /boards/{board_id}/invites/current
Get current active invite for a board.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Condition:** Returns `404` if no active invite exists.

#### POST /boards/{board_id}/invites
Create a new invite. Deactivates all existing active invites for this board.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Body:** `expires_in_days` (int, default 7), `max_uses` (int or null for Unlimited).

#### GET /invites/{invite_id}
Get invite details.
*   **Auth:** Required
*   **Access:** Owner/staff get full info. Any authenticated user gets public info (is_active, is_expired, board_name).

#### PATCH /invites/{invite_id}
Update invite settings (expires_in_days, expire_at, max_uses, is_active).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### DELETE /invites/{invite_id}
Soft-deactivate invite (sets `is_active = false`, does not delete).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### POST /invites/{invite_id}/join
Join a board via invite link. Adds user to `Board.members`, increments `used_count`.
*   **Auth:** Required
*   **Access:** Any authenticated user.
*   **Condition:** Invite must be active, not expired, not exhausted. Already owner/member returns `200` with no side effects.

---

### Members Endpoints

#### GET /boards/{board_id}/members
List all members including owner.
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Notes:** Owner is always first with `is_owner: true`. No password returned.

#### DELETE /boards/{board_id}/members/{username}
Remove a member from a board.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Condition:** Cannot remove the board owner.

#### POST /boards/{board_id}/leave
Leave a board as the current user.
*   **Auth:** Required
*   **Access:** Any member.
*   **Condition:** Owner cannot leave.

---

### Task Endpoints

#### GET /boards/{board_id}/tasks
List all tasks for a board.
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Filters:** `status`, `column_id`, `column_kind`, `priority`, `assignee`, `tag`, `search`.

#### GET /boards/{board_id}/backlog/tasks
List tasks in the Backlog column.
*   **Auth:** Required
*   **Filters:** Same as above.

#### GET /columns/{column_id}/tasks
List tasks in a specific column.
*   **Auth:** Required

#### GET /tasks/{task_id}
Get task details.
*   **Auth:** Required

#### POST /boards/{board_id}/tasks
Create a new task. If `column_id` is omitted, creates the task in the Backlog (auto-creating the Backlog column if necessary).
*   **Auth:** Required
*   **Access:** Owner, member, or staff.

#### POST /columns/{column_id}/tasks
Create a new task in a specific column.
*   **Auth:** Required

#### PATCH /tasks/{task_id}
Update task details (title, content, priority, deadline, status, column_id, tags, checklist, assignees).
*   **Auth:** Required

#### POST /tasks/{task_id}/archive
Archive a task (soft delete).
*   **Auth:** Required

#### POST /tasks/{task_id}/restore
Restore an archived task.
*   **Auth:** Required

#### DELETE /tasks/{task_id}
Soft delete a task (archives it).
*   **Auth:** Required

#### POST /tasks/{task_id}/move
Change task position within the same column or move to a different column.
*   **Auth:** Required
*   **Request:** `{"target_column_id": "uuid", "position": 1}`
*   **Response:** Returns the moved `task`, a list of `affected_column_ids`, and `reordered_tasks` containing a dictionary of task IDs mapped to their newly assigned integer positions `{"uuid": 1, "uuid": 2}`.

#### POST /tasks/{task_id}/assign
Assign a user to the task.
*   **Auth:** Required
*   **Request:** `{"username": "mentor1"}`

#### POST /tasks/{task_id}/unassign
Unassign a user from the task.
*   **Auth:** Required
*   **Request:** `{"username": "mentor1"}`

#### POST /tasks/{task_id}/checklist/items
Add an item to the task checklist.
*   **Auth:** Required
*   **Request:** `{"title": "Item name"}`

#### PATCH /tasks/{task_id}/checklist/items/{item_id}
Update a checklist item's title or completion status.
*   **Auth:** Required
*   **Request:** `{"title": "New title", "is_done": true}` (fields are optional)

#### POST /tasks/{task_id}/checklist/items/{item_id}/toggle
Toggle the completion status of a checklist item.
*   **Auth:** Required

#### POST /tasks/{task_id}/checklist/items/{item_id}/delete
Delete a checklist item.
*   **Auth:** Required

#### POST /tasks/{task_id}/checklist/reorder
Reorder the checklist items.
*   **Auth:** Required
*   **Request:** `{"ordered_item_ids": ["uuid-1", "uuid-2"]}`

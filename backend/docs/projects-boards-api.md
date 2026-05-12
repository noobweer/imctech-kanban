# Projects and Boards API

Detailed documentation for Project and Board management.

## Project Endpoints

### GET /projects
List all projects accessible to the user.
*   **Access:** Staff/superuser sees all. Standard user sees projects where they are an owner or member of at least one board.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Project Name",
    "created_at": "2026-05-12T10:00:00Z",
    "updated_at": "2026-05-12T10:00:00Z"
  }
]
```

---

### POST /projects
Create a new project.

**Request:**
```json
{
  "name": "New Project"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "New Project",
  "created_at": "2026-05-12T10:00:00Z",
  "updated_at": "2026-05-12T10:00:00Z"
}
```

---

### GET /projects/{project_id}
Get project details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Project Name",
  "created_at": "2026-05-12T10:00:00Z",
  "updated_at": "2026-05-12T10:00:00Z"
}
```

---

### PATCH /projects/{project_id}
Update project name.
*   **Access:** Staff/superuser or user who is an owner of at least one board in the project.

**Request:**
```json
{
  "name": "Updated Project Name"
}
```

**Response:** `200 OK`

---

### DELETE /projects/{project_id}
Delete project.
*   **Access:** Staff/superuser or user who is an owner of at least one board in the project.
*   **Constraint:** Cannot delete project if it has associated boards.

**Response:** `200 OK`
```json
{
  "success": true
}
```

---

## Board Endpoints

### GET /boards
List all boards accessible to the user.
*   **Query Params:** `status` (optional: `active`, `archived`)
*   **Access:** Staff/superuser sees all. Standard user sees boards where they are an owner or member.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Board Name",
    "project_id": "uuid",
    "project_name": "Project Name",
    "owner_username": "test_user",
    "members": ["user1", "user2"],
    "status": "active",
    "tasks_total": 0,
    "tasks_done": 0,
    "progress_percent": 0,
    "created_at": "2026-05-12T10:00:00Z",
    "updated_at": "2026-05-12T10:00:00Z"
  }
]
```

---

### POST /boards
Create a new board.
*   **Note:** If `project_id` is not provided, a project with name `"{board_name} Project"` is automatically created.

**Request:**
```json
{
  "name": "New Board",
  "project_id": "uuid (optional)",
  "status": "active",
  "tasks_total": 0,
  "tasks_done": 0,
  "progress_percent": 0
}
```

**Response:** `201 Created`

---

### GET /boards/{board_id}
Get board details.

**Response:** `200 OK`

---

### PATCH /boards/{board_id}
Update board.
*   **Access:** Staff/superuser or board owner.
*   **Editable fields:** `name`, `status`.

**Request:**
```json
{
  "name": "Updated Board Name",
  "status": "archived"
}
```

**Response:** `200 OK`

---

### DELETE /boards/{board_id}
Safe deletion (archives the board).
*   **Access:** Staff/superuser or board owner.
*   **Action:** Sets `status` to `archived`.

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Board archived successfully"
}
```

# Board CRUD Endpoints

#### GET /boards
List all boards accessible to the user.
*   **Auth:** Required
*   **Query Params:** `status` (active/archived)

#### POST /boards
Create a new board.
*   **Auth:** Required
*   **Access:** Mentor or staff (Students restricted).

#### GET /boards/{board_id}
Get board details.
*   **Auth:** Required

#### PATCH /boards/{board_id}
Update board (name/status).
*   **Auth:** Required

#### DELETE /boards/{board_id}
Archive board.
*   **Auth:** Required

#### GET /boards/{board_id}/archive/tasks
List archived tasks (tasks in the technical Archive column).
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Filters:** `priority`, `assignee`, `tag`, `search`.

#### GET /boards/{board_id}/archive/columns
List archived columns.
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Query Params:** `kind` (board/backlog)

# Column CRUD Endpoints

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

#### POST /columns/{column_id}/restore
Restore an archived column.
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### DELETE /columns/{column_id}
Soft delete column (sets status to archived).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### POST /columns/{column_id}/clear
Move all tasks from this column to the Archive column.
*   **Auth:** Required
*   **Access:** Board owner, member, or staff.

#### POST /boards/{board_id}/columns/defaults
Create default columns (To Do, In Progress, Done).
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Condition:** Board must have no existing columns.

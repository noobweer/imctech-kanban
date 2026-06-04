# Task Endpoints

**Note:** Users with the `mentor` role are restricted from all task mutation endpoints (create, update, move, delete, archive, assign, checklist). They only have read access to tasks.

#### GET /boards/{board_id}/tasks
List all tasks for a board.
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Filters:** `status`, `column_id`, `column_kind`, `priority`, `assignee`, `tag`, `search`, `sort_by`, `deadline_filter`.

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

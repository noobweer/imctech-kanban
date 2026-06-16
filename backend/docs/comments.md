# Comments Endpoints

#### GET /tasks/{task_id}/comments
List all comments for a task.
*   **Auth:** Required
*   **Access:** Owner, member, or staff of the associated board.

#### POST /tasks/{task_id}/comments
Create a new comment on a task.
*   **Auth:** Required
*   **Access:** Mentor/staff for the first comment. Assignee/mentor/staff for subsequent comments.
*   **Body:** `content` (str, required), `links` (List[str], optional).

#### PATCH /comments/{comment_id}
Update a comment's content or links.
*   **Auth:** Required
*   **Access:** Comment author or staff.

#### DELETE /comments/{comment_id}
Soft delete a comment.
*   **Auth:** Required
*   **Access:** Comment author or staff.

#### POST /tasks/{task_id}/comments/read
Mark all comments for a task as read for the current user.
*   **Auth:** Required
*   **Access:** Owner, member, or staff of the associated board.

#### GET /tasks/{task_id}/comments/state
Get the comment read state (`none`, `read`, `unread`) for a specific task.
*   **Auth:** Required
*   **Access:** Owner, member, or staff of the associated board.

#### GET /boards/{board_id}/comments/states
Get comment read states for tasks in a board.
*   **Auth:** Required
*   **Access:** Owner, member, or staff of the board.
*   **Query Params:** `task_ids` (Optional list of UUIDs).

#### GET /boards/{board_id}/comments/feed
Get task feed based on comments activity for the board.
*   **Auth:** Required
*   **Access:** Owner, member, or staff of the board.
*   **Query Params:** `filter` (str: `new` or `activity`. Defaults to `new`).

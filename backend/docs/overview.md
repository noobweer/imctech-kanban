# Overview Endpoints

**Note:** These endpoints provide aggregated data for the board's overview panel.
Users with the `mentor` role have full access to these read-only statistics.

#### GET /boards/{board_id}/overview/progress
Returns the overall progress of tasks distributed across the active board columns (Bar Chart data).
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Response Schema (`ProgressOut`):**
    ```json
    {
      "total_tasks": 10,
      "columns": [
        {"id": "uuid", "name": "To Do", "task_count": 3, "percent": 30},
        {"id": "uuid", "name": "In Progress", "task_count": 2, "percent": 20},
        {"id": "uuid", "name": "Done", "task_count": 5, "percent": 50}
      ]
    }
    ```

#### GET /boards/{board_id}/overview/activity
Returns activity and completion statistics broken down by board members.
*   **Auth:** Required
*   **Query Parameters:**
    *   `period` (optional, default="weekly"): Determines the scope of the data. Can be `"weekly"` (since the beginning of the current week) or `"all_time"`.
*   **Response Schema (`ActivityOut`):**
    ```json
    {
      "period": "weekly",
      "week_start": "2026-05-25",
      "week_end": "2026-05-31",
      "members": [
        {
          "username": "user1",
          "name": "Иван Иванов",
          "columns": [
            {"column_id": "uuid", "column_name": "To Do", "task_count": 2, "percent": 40},
            {"column_id": "uuid", "column_name": "Done", "task_count": 1, "percent": 20}
          ]
        }
      ]
    }
    ```

#### GET /boards/{board_id}/overview/deadlines
Returns all tasks with deadlines split into two groups: overdue and due within 4 days.
*   **Auth:** Required
*   **Response Schema (`DeadlinesOut`):**
    ```json
    {
      "overdue": [
        {
          "id": "uuid",
          "title": "Fix login bug",
          "deadline": "2026-05-28T10:00:00Z",
          "column": "In Progress",
          "assignees": ["username1"],
          "priority": 2,
          "added_to_board_at": "2026-05-20T09:00:00Z"
        }
      ],
      "due_soon": [ ... ]
    }
    ```

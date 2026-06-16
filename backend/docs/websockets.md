# WebSockets and PostgreSQL Documentation

## WebSocket Endpoint
WebSocket connection for board updates is available at:
`ws://<host>:<port>/ws/boards/{board_id}/`

## Authentication
Connect to the WebSocket by passing your JWT access token via the `token` query parameter:
`ws://<host>:<port>/ws/boards/{board_id}/?token=<access_token>`

If the token is invalid, expired, or the user does not have access to the board, the connection will be immediately closed.

## Event Format
All WebSocket events share the following JSON structure:
```json
{
  "type": "event.type",
  "board_id": "uuid",
  "payload": {},
  "actor_id": "uuid-or-null",
  "created_at": "iso-datetime"
}
```

## Emitted Events

### Tasks
- `task.created`: Created a new task. Payload: `TaskOut` object.
- `task.updated`: Updated task fields. Payload: `TaskOut` object.
- `task.moved`: Task moved to another column or position. Payload: `{"task": {"id", "column_id", "position"}, "affected_column_ids": [...], "reordered_tasks": [...]}`.
- `task.archived`: Task moved to archive. Payload: `TaskOut` object.
- `task.restored`: Task restored from archive. Payload: `TaskOut` object.
- `task.assignees_updated`: Task assignees changed. Payload: `TaskOut` object.
- `task.checklist_updated`: Checklist modified (added, toggled, reordered, etc.). Payload: `TaskOut` object.

### Columns
- `column.created`: Created a new column. Payload: `ColumnOut` object.
- `column.updated`: Updated column name/status. Payload: `ColumnOut` object.
- `column.moved`: Column reordered. Payload: `ColumnOut` object.
- `column.archived`: Column archived. Payload: `ColumnOut` object.
- `column.restored`: Column restored. Payload: `ColumnOut` object.
- `column.cleared`: Column cleared of all tasks. Payload: `{"column_id": "uuid"}`.

### Comments
- `comment.created`: Comment added to a task. Payload: `TaskCommentOut` object.
- `comment.updated`: Comment text/links updated. Payload: `TaskCommentOut` object.
- `comment.deleted`: Comment deleted. Payload: `{"comment_id": "uuid", "task_id": "uuid"}`.
- `comments.read_state_updated`: Comment read state modified. Payload: `TaskCommentStateOut` object.

## PostgreSQL Migration

The project uses PostgreSQL via Docker Compose.

### Environment Variables
Set these variables in your `.env` file (defaults are provided in `docker-compose.yml`):
- `POSTGRES_DB` (default: kanban)
- `POSTGRES_USER` (default: kanban_user)
- `POSTGRES_PASSWORD` (default: kanban_pass)
- `POSTGRES_HOST` (default: db in docker-compose, localhost otherwise)
- `POSTGRES_PORT` (default: 5432)

### Running Locally
To launch the complete infrastructure:
```bash
docker-compose up --build
```
This will automatically launch the PostgreSQL container, Daphne ASGI server, and Frontend Vite server.

### Migrations
To apply migrations on the newly created PostgreSQL database:
```bash
docker-compose exec backend uv run python manage.py makemigrations
docker-compose exec backend uv run python manage.py migrate
```

### Manual Testing
You can test WebSockets using standard browser DevTools (Network -> WS) or using a script like `wscat`:
```bash
wscat -c "ws://localhost:8000/ws/boards/<board_id>/?token=<token>"
```
Make changes via the REST API endpoints and observe the incoming events on the WebSocket connection.

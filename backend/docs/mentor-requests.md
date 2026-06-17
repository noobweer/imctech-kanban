# Mentor Requests API

Запросы к наставнику — это механизм "поднятия руки" для студента (помощь/проверка) в рамках конкретной задачи.

## Концепт

- Запрос не заменяет комментарии. Он использует `TaskComment` как основу для ведения диалога.
- По одной задаче может быть только **один активный запрос** (`open` или `in_progress`).
- У запроса нет конкретного адресата. Все менторы, у которых есть доступ к доске, могут его увидеть и ответить на него.
- Ответ наставника (`respond`) автоматически создаёт комментарий в задаче и переводит запрос в `in_progress`.
- Только автор запроса (или admin) может перевести его в `resolved`.

## Статусы (`status`)

- `open`: запрос создан, ментор ещё не ответил.
- `in_progress`: ментор написал первый комментарий-ответ на запрос.
- `resolved`: автор запроса пометил, что проблема решена.
- `cancelled`: автор или ментор отменили запрос.

## Типы (`request_type`)

- `help`: Нужна помощь.
- `review`: Нужна проверка.

## Endpoints

### 1. Создать запрос

`POST /api/tasks/{task_id}/mentor-requests`
Создаёт запрос.

**Payload:**
```json
{
  "request_type": "help",
  "message": "Не могу понять, почему падает тест."
}
```

### 2. Получить активный запрос задачи

`GET /api/tasks/{task_id}/mentor-request`
Возвращает активный запрос (status `open` или `in_progress`) по задаче. 
Если запроса нет — возвращает `204 No Content`.

### 3. Получить список запросов доски

`GET /api/boards/{board_id}/mentor-requests`
Возвращает запросы доски с пагинацией.

**Query параметры:**
- `status` (open, in_progress, resolved, cancelled)
- `request_type` (help, review)
- `mine` (true/false) - если true, возвращает только созданные текущим пользователем.

### 4. Действия с запросом

- `GET /api/mentor-requests/{request_id}` — получить детали.
- `POST /api/mentor-requests/{request_id}/respond` — ментор отвечает на запрос. 
  **Payload:** `{"content": "Текст комментария"}`
- `POST /api/mentor-requests/{request_id}/resolve` — автор помечает запрос решённым.
- `POST /api/mentor-requests/{request_id}/cancel` — отмена запроса.
  **Payload (опционально для автора, обязательно для ментора):** `{"close_reason": "Неактуально"}`

## Activity Log и WebSockets

События ActivityLog:
- `mentor_request_created`
- `mentor_request_started`
- `mentor_request_resolved`
- `mentor_request_cancelled`

События WebSocket:
Рассылаются через `board_event`:
- `mentor_request.created`
- `mentor_request.started`
- `mentor_request.resolved`
- `mentor_request.cancelled`

Ты работаешь в существующей backend и frontend кодовой базе Kanban-модуля IMCTech.

Нужно реализовать вкладку Comments внутри доски — единый раздел для отслеживания обновлений по комментариям.

---

# 1. Текущий контекст проекта

Проект уже существует. Не переписывай его с нуля.

Backend stack:
- Python, Django, Django Ninja, Ninja JWT, SQLite, uv, Docker / Docker Compose.

Frontend stack:
- Vue 3 (Composition API), TypeScript, Vite, Pinia, Vue Router, Bun.

Текущая backend-структура:
- `pb/api.py` — compatibility stub;
- общий router собирается в `pb/routers/__init__.py`;
- HTTP endpoints лежат в `pb/routers/`;
- бизнес-логика лежит в `pb/services/`;
- основные модели лежат в `pb/models.py`;
- схемы API лежат в `pb/schemas.py`;
- Django admin лежит в `pb/admin.py`;
- права доступа лежат в `pb/permissions.py`;
- роли пользователя лежат в `users.models.UserProfile.role`.

В текущем репозитории уже есть:
- `Project`, `Board`, `Column`, `Invite`, `Task`;
- `TaskComment` — модель комментария к задаче;
- `TaskCommentReadState` — модель состояния прочтения комментариев (поле `last_read_at`);
- `UserProfile.role = student | mentor`;
- endpoints для комментариев: `GET/POST /tasks/{task_id}/comments`, `PATCH/DELETE /comments/{comment_id}`, `POST /tasks/{task_id}/comments/read`, `GET /tasks/{task_id}/comments/state`, `GET /boards/{board_id}/comments/states`;
- `comments_state` в ответах: `none | read | unread`.

---

# 2. Границы задачи

Реализовать:
- новый backend endpoint для вкладки Comments;
- вкладку Comments во фронтенде.

Не трогать существующие модели и endpoints комментариев — они уже работают.

---

# 3. Доступ

Вкладка Comments видна всем участникам доски — и mentor, и student.


---

# 4. UI вкладки Comments

Comments — отдельная вкладка в навигации доски рядом с Board, Backlog, Archive, Overview.

Не модальное окно. Открывается как отдельный экран внутри доски.

## 4.1. Структура экрана

Два фильтра в верхней части:
- **New comments** (по умолчанию активен)
- **Activity**

Справа от каждого фильтра — число в скобках или badge, показывающее количество карточек которые отвечают этому фильтру.

Пример: `New comments (3)   Activity (7)`

Под фильтрами — список карточек задач отвечающих активному фильтру. Список скроллится вниз если карточек много.

## 4.2. Фильтр New comments

Показывает задачи где у текущего пользователя есть непрочитанные комментарии.

Это задачи с if get_task_comment_state(user, t)["comments_state"] == "unread" для текущего пользователя.

Сортировка: по времени последнего комментария (`last_comment_at`), от новых к старым.

## 4.3. Фильтр Activity

Показывает задачи в которых текущий пользователь участвовал в обсуждении:
- написал хотя бы один не удалённый комментарий к задаче;
- или является assignee задачи у которой есть хотя бы один не удалённый комментарий.

Сортировка: по времени последнего комментария (`last_comment_at`), от новых к старым.

## 4.4. Карточки задач

Карточки отображаются в том же стиле что и на доске.

При нажатии на карточку — открывается задача с активной вкладкой комментариев.

---

# 5. Backend endpoint

## 5.1. Новый endpoint

```
GET /api/boards/{board_id}/comments/feed
```

Query параметры:
- `filter`: `new` (default) | `activity`

Auth: JWT required.

Access: любой участник доски (`has_board_access(user, board)`).

## 5.2. Response

```json
{
  "filter": "new",
  "total": 3,
  "tasks": [
    {
      "id": "uuid",
      "title": "Fix login bug",
      "column": "In Progress",
      "priority": 2,
      "deadline": "2026-06-01T10:00:00Z",
      "added_to_board_at": "2026-05-20T09:00:00Z",
      "assignees": ["username1"],
      "comments_count": 4,
      "last_comment_at": "2026-05-31T12:00:00Z",
      "comments_state": "unread"
    }
  ]
}
```

`total` — количество задач в ответе (используется фронтендом для badge у фильтра).

`comments_state` — берётся из существующей логики расчёта (`none | read | unread`).

## 5.3. Логика для фильтра `new`

Сначала берём все задачи доски у которых есть хотя бы один не удалённый комментарий. Потом для каждой задачи вызываем calculate_comment_state(task, user) и оставляем только те где результат unread. То есть задачи где появились комментарии которые пользователь ещё не читал. При этом для обычного пользователя выводятся только его задачи, а для ментора все задачи. Разумеется из тех, что попали в результат.


## 5.4. Логика для фильтра `activity`

Два отдельных запроса — задачи где пользователь сам писал комментарий, и задачи где он assignee и есть комментарии. Потом объединяем их и убираем дубликаты. Это нужно чтобы задача не попала дважды.

## 5.5. Сортировка

Для обоих фильтров сортировать по `last_comment_at` — времени последнего не удалённого комментария задачи.


## 5.6. Реализация

Вынести бизнес-логику в `pb/services/comment_service.py` — добавить функцию:

```python
def get_comments_feed(board, user, filter_type: str) -> dict:
    ...
```

Роутер должен быть тонким: получить board, проверить доступ, вызвать сервис, вернуть ответ.

Добавить endpoint в существующий роутер `pb/routers/comments.py`.

---

# 6. Изменения в БД

Новых моделей не требуется.

Все необходимые данные уже есть:
- `TaskComment` — комментарии с `is_deleted`, `owner`, `created_at`;
- `TaskCommentReadState` — `last_read_at` для расчёта `unread`;
- `Task.assignees` — для фильтра Activity;
- существующая функция `calculate_comment_state(task, user)` — для определения `unread`.

---

# 7. Схемы

Добавить в `pb/schemas.py`:

```python
class CommentFeedTaskOut(Schema):
    id: uuid.UUID
    title: str
    column: str
    priority: int
    deadline: Optional[datetime]
    added_to_board_at: Optional[datetime]
    assignees: List[str]
    comments_count: int
    last_comment_at: Optional[datetime]
    comments_state: str  # none | read | unread

class CommentFeedOut(Schema):
    filter: str
    total: int
    tasks: List[CommentFeedTaskOut]
```

---

# 8. Edge cases

- Задача заархивирована — не показывается ни в одном фильтре.
- Все комментарии задачи удалены (soft-delete) — задача не показывается.
- Пользователь является assignee но комментариев нет — не попадает в Activity.
- Пользователь написал комментарий и является assignee — попадает в Activity один раз.
- Собственные комментарии пользователя не делают задачу unread для него — это уже реализовано в `calculate_comment_state`.
- Задача в фильтре New comments одновременно может быть и в Activity — это нормально, фильтры независимы.

---

# 9. Проверка через Swagger

Подготовить тестовые данные:
- mentor и student на одной доске;
- задача с assignee = student;
- mentor пишет комментарий к задаче.

Проверить:
1. `GET /api/boards/{board_id}/comments/feed?filter=new` под student — должна вернуться задача с `comments_state = unread`.
2. После `POST /api/tasks/{task_id}/comments/read` под student — задача пропадает из фильтра `new`.
3. `GET /api/boards/{board_id}/comments/feed?filter=activity` под student — задача есть (student является assignee и есть комментарии).
4. `GET /api/boards/{board_id}/comments/feed?filter=activity` под mentor — задача есть (mentor написал комментарий).
5. `total` в ответе совпадает с количеством карточек в `tasks`.

---

# 10. Отчёт после реализации

В конце дай отчёт:
1. Какие файлы изменены.
2. Какие схемы добавлены.
3. Какой endpoint добавлен.
4. Как работает логика фильтра `new`.
5. Как работает логика фильтра `activity`.
6. Как считается `total` для badge.
7. Как проверить через Swagger.

Ты работаешь в существующей backend и frontend кодовой базе Kanban-модуля IMCTech.

Нужно реализовать Sprint 3 Task 2: систему логирования действий (ActivityLog), панель Overview и обновления карточек задач.

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
- `Project`, `Board`, `Column`, `Invite`, `Task`, `TaskComment`, `TaskCommentReadState`;
- `UserProfile.role = student | mentor`;
- `Task.assignees`, `Task.checklist`;
- `ColumnKind.BOARD`, `ColumnKind.BACKLOG`;
- task lifecycle endpoints включая `POST /tasks/{task_id}/move`;
- mentor permission helpers в `pb/permissions.py`;
- mentor не может создавать/изменять/перемещать/архивировать задачи — только читать.

В текущем репозитории ещё нет:
- модели `ActivityLog`;
- поля `Task.added_to_board_at`;
- панели Overview на фронтенде.

---

# 2. Часть 1 — ActivityLog

## 2.1. Зачем

ActivityLog нужен для отображения истории действий участников в панели Overview. Каждое действие участника доски — одна запись в таблице. Записи привязаны к конкретной доске, поэтому история одной доски не пересекается с историей другой.

## 2.2. Модель

Добавить в `pb/models.py`:

```python
class ActivityLog(models.Model):
    ACTION_TYPES = [
        ("task_created",      "Task Created"),
        ("task_moved",        "Task Moved"),
        ("task_archived",     "Task Archived"),
        ("task_restored",     "Task Restored"),
        ("task_assigned",     "Task Assigned"),
        ("task_deadline_set", "Task Deadline Set"),
        ("column_created",    "Column Created"),
        ("column_moved",      "Column Moved"),
        ("column_archived",   "Column Archived"),
        ("column_cleared",    "Column Cleared"),
        ("member_joined",     "Member Joined"),
        ("member_left",       "Member Left"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["board", "created_at"]),
            models.Index(fields=["board", "action_type"]),
        ]

    def __str__(self):
        return f"{self.action_type} by {self.actor} in {self.board.name}"
```

## 2.3. Автоматизация логирования (Архитектура)

Для чистоты кода используется **JWT Context Middleware**. Это позволяет сервисам автоматически получать автора действия, не требуя изменений в роутерах или сигнатурах функций.

### 2.3.1. Глобальный контекст (pb/middleware.py)
Создать Middleware, который извлекает пользователя из JWT-токена и сохраняет его в `contextvars`. Это делает пользователя доступным в любом слое приложения (Service, Model, Signal).

```python
import contextvars
from ninja_jwt.authentication import JWTAuth

_current_user = contextvars.ContextVar("current_user", default=None)

def get_current_user():
    return _current_user.get()

class JWTContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth = JWTAuth()

    def __call__(self, request):
        header = request.headers.get("Authorization")
        if header and header.startswith("Bearer "):
            token = header.split(" ")[1]
            try:
                # Используем стандартный механизм аутентификации Ninja JWT
                user = self.auth.authenticate(request, token)
                if user:
                    _current_user.set(user)
            except:
                pass
        
        response = self.get_response(request)
        _current_user.set(None) # Очистка контекста
        return response
```
*Добавить `pb.middleware.JWTContextMiddleware` в `settings.py` в начало списка `MIDDLEWARE`.*

### 2.3.2. Хелпер логирования (pb/services/activity_service.py)
Централизованная функция для создания записей.

```python
from pb.models import ActivityLog
from pb.middleware import get_current_user

def create_log(board, action_type, metadata=None):
    user = get_current_user()
    return ActivityLog.objects.create(
        board=board,
        actor=user,
        action_type=action_type,
        metadata=metadata or {}
    )
```

## 2.4. Использование в сервисах

В функциях сервисов достаточно вызвать `create_log`. Передавать `user` в аргументы функции не нужно.

### task_service.py
```python
def move_task(task, new_column, position):
    old_column_name = task.column.name
    # ... логика перемещения ...
    
    create_log(
        board=task.column.board,
        action_type="task_moved",
        metadata={
            "task_id": str(task.id),
            "task_title": task.title,
            "from_column": old_column_name,
            "to_column": new_column.name
        }
    )
```

## 2.5. Что ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ (Важно!)

1.  **Роутеры (`pb/routers/*.py`)**: Не нужно менять `auth=JWTAuth()` или импорты.
2.  **Сигнатуры сервисов**: Функции не загромождаются лишним параметром `user`.
3.  **Бизнес-логика**: Логирование остается прозрачным и не мешает основной работе сервисов.

## 2.6. Admin

Добавить в `pb/admin.py`:

```python
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "board", "actor", "action_type", "created_at")
    list_filter = ("action_type", "created_at", "board")
    search_fields = ("actor__username", "board__name")
    readonly_fields = ("id", "created_at")
    raw_id_fields = ("board", "actor")
```

## 2.7. Миграции

```bash
uv run python manage.py makemigrations pb
uv run python manage.py migrate
```

---

# 3. Часть 2 — Поле added_to_board_at

## 3.1. Назначение

Фиксирует момент когда задача попала в колонку типа `kind = board` (не Backlog). Это ключевое поле для фильтрации "Новых" задач и расчета дедлайнов в Overview.

- Если задача создана сразу в колонке доски — `added_to_board_at = now()`.
- Если задача перенесена из Backlog в колонку доски — `added_to_board_at` проставляется в момент первого переноса.
- **При восстановлении из архива** на доску — поле `added_to_board_at` **обновляется** на текущее время.

## 3.2. Изменение модели Task

Добавить в `pb/models.py` в класс `Task`:

```python
# Индекс обязателен для производительности Overview
added_to_board_at = models.DateTimeField(null=True, blank=True, db_index=True)
```

## 3.3. Логика проставления (task_service.py)

Чтобы не дублировать код, воспользуйся правилом **DRY**. Создай в `task_service.py` вспомогательную функцию и вызывай её в нужных местах.

```python
def _set_board_timestamp(task, column, force_update=False):
    """
    Устанавливает дату попадания на доску.
    force_update=True используется для восстановления из архива.
    """
    if column.kind == ColumnKind.BOARD:
        if force_update or task.added_to_board_at is None:
            task.added_to_board_at = timezone.now()
```

**Где вызывать:**

1.  **`create_task`**: В самом конце, перед `return task`.
    `_set_board_timestamp(task, column)`
2.  **`move_task`**: После того как определена `new_column`.
    `_set_board_timestamp(task, new_column)`
3.  **`restore_task`** (в `archive_service.py`): После смены статуса на active.
    `_set_board_timestamp(task, target_column, force_update=True)`

## 3.4. Data migration для существующих задач
... (без изменений) ...

Создать data migration: для всех существующих задач в колонках `kind = board` проставить `added_to_board_at = created_at`. Для задач в Backlog оставить `null`.

---

# 4. Часть 3 — Backend endpoints для Overview

Все эндпоинты требуют JWT. Доступны только пользователям с `role = mentor` или `is_staff = True`.

**Важно:** Вся логика расчетов должна находиться в `pb/services/overview_service.py`. Роутеры должны быть максимально тонкими (Thin Routers).

Добавить новый файл `pb/services/overview_service.py` и новый роутер `pb/routers/overview.py`.

Подключить в `pb/routers/__init__.py`:
```python
from .overview import router as overview_router
router.add_router("", overview_router, tags=["Overview"])
```

## 4.1. Bar Chart

```
GET /api/boards/{board_id}/overview/progress
```

**Логика (overview_service.py):**
- Получить **все** активные колонки доски типа `kind="board"`, отсортированные по `position`.
- Для каждой колонки посчитать количество активных задач (`status="active"`).
- **Не фильтровать** пустые колонки (они нужны для стабильной легенды на фронтенде).
- Если задач в колонке 0, вернуть `task_count: 0` и `percent: 0`.

Response:
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

## 4.2. Activity

```
GET /api/boards/{board_id}/overview/activity?period=weekly
```

**Оптимизация производительности:**
- **Запрещено** делать запросы к БД внутри цикла по участникам (N+1).
- Сначала вытянуть все `ActivityLog` для данной доски за указанный период одним запросом.
- Для расчета `weekly` использовать `timezone.now()` (период считается по `Asia/Vladivostok`).

**Логика расчета Done (overview_service.py):**
- Найти финальное попадание в Done за период.
- Если задача зашла в Done, а потом вышла из него (moved back) — она **не считается** выполненной.
- Проверку "выхода из Done" делать в памяти Python после загрузки логов.

Response:
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

## 4.3. Deadlines

```
GET /api/boards/{board_id}/overview/deadlines
```

**Логика (overview_service.py):**
- Использовать `timezone.now()` для определения `overdue` и `due_soon` (+4 дня).
- Обязательно использовать `select_related("column")` и `prefetch_related("assignees")` для минимизации запросов.

Response:
```json
{
  "overdue": [
    {
      "id": "uuid", "title": "Fix login bug",
      "deadline": "2026-05-28T10:00:00Z",
      "column": "In Progress",
      "assignees": ["username1"],
      "priority": 2,
      "added_to_board_at": "2026-05-20T09:00:00Z"
    }
  ],
  "due_soon": [...]
}
```

---

# 5. Часть 4 — Frontend: вкладка Overview

## 5.1. Доступ

Вкладка Overview показывается только пользователям с `role = mentor`.

Student вкладку не видит совсем.

## 5.2. Структура экрана

Overview — отдельная вкладка в навигации доски рядом с Board, Backlog, Archive. Не всплывающее окно.

Содержит:
1. Bar Chart вверху.
2. Две кнопки: **Activity** и **Deadlines**.
3. Если активна Activity — справа от кнопок показывается фильтр **Weekly / All Time**.
4. Если активна Deadlines — фильтр скрывается.
5. Содержимое под кнопками зависит от активного режима.

## 5.3. Bar Chart

Горизонтальная полоса разбитая на цветные сегменты. Цвета из фиксированного набора по порядку.

Под полосой легенда: `■ 15% Todo  ■ 25% In progress  ■ 35% Need Review  ■ 25% Done`.

Колонки без задач не отображаются.

## 5.4. Режим Activity — таблица

Строки — участники доски (все, включая тех без задач).

Столбцы — активные колонки доски + стрелка.

Ячейка: `N (X%)` где N — количество задач, X — процент от задач пользователя.

Для Done — счётчик по логике финального попадания за период.

Таблица скроллится горизонтально если колонок много, вертикально если участников много.

Последний столбец — кнопка-стрелка → открывает модальное окно задач пользователя.

## 5.5. Модальное окно задач пользователя

Открывается поверх Overview. Не заменяет содержимое панели.

Содержит:
- Кнопка закрыть (←).
- Селектор пользователя — можно переключить на любого участника доски.
- Три фильтра-кнопки:
  - **[Название колонки]** — выпадающий список колонок, независимый фильтр.
  - **Date** — сортировка по `added_to_board_at` от новых к старым.
  - **Deadline** — только задачи с дедлайном в ближайшие 3 дня или просроченные.
  - Date и Deadline взаимозаменяемые: активен только один из них.
- Сетка карточек: 3 в ряд, скролл только вниз. Карточки уменьшены чтобы вмещаться.
- По умолчанию активен Date

На каждой карточке кнопка **Comment** в правом верхнем углу. При нажатии — открывается задача с активной вкладкой комментариев.

## 5.6. Режим Deadlines

Карточки задач всей доски с дедлайном.

Две группы:
1. **Просроченные** — дедлайн прошёл. Всегда отображаются, без ограничения по дальности.
2. **Скоро истекает** — дедлайн в ближайшие 4 дня.

Задачи дальше 4 дней не показываются (кроме просроченных).

Сортировка внутри каждой группы: по близости к дедлайну (самые близкие первые).

Сетка карточек: 3 в ряд, скролл вниз. Нет дополнительных фильтров.

На карточках тоже есть кнопка Comment.

---

# 6. Часть 5 — Обновление карточек задач

## 6.1. Что изменить

На всех карточках задач во всём приложении (доска, Backlog, модальное окно, Deadlines).

Было:
```
Due Jun 2
```

Стало:
```
Add on board Jun 1/Due Jun 2
```

Если `added_to_board_at` равно `null` — строку `Add on board` не показывать.

Если дедлайн не задан — строку `Due` не показывать.

## 6.2. Формат дат

Все даты во всём приложении отображать в формате: `Jun 1`, `Jul 28`, `Dec 31`.

Не использовать числовой формат (`01.06.2026`, `2026-06-01`).

Это касается всех существующих карточек.

---

# 7. Edge cases

- Участник без задач — показывается в таблице Activity с нулями.
- Задача перемещена в Done несколько раз — считается только последнее финальное попадание (нет более поздней записи `task_moved` с `from_column = "Done"`).
- Задача из Done заархивирована — всё равно считается как выполненная.
- `added_to_board_at` для существующих задач — data migration: задачи в `kind = board` получают `created_at`, задачи в Backlog получают `null`.
- Если колонка есть, но на ней нет задач - просто не показывать на Bar Chart, но показывать снизу 0% и её цвет
- Дедлайн ровно через 4 дня — входит в `due_soon`.
- Дедлайн сегодня — просроченная если время уже прошло, `due_soon` если ещё нет.
- mentor перемещает задачи? Нет — mentor не может изменять задачи согласно текущим правам. Логи `task_moved` пишутся только от student/staff.
- Все задачи заархивированы — bar chart пустой, Done показывает ранее выполненные за период если они были.

---

# 8. Отчёт после реализации

В конце дай отчёт:
1. Какие файлы изменены.
2. Какие модели добавлены или изменены.
3. Какие миграции созданы.
4. Какие endpoints добавлены.
5. В каких функциях добавлено логирование.
6. Как изменились сигнатуры функций.
7. Как считается Done для Weekly и All Time.
8. Как работает `added_to_board_at`.
9. Как проверить через Swagger.

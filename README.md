# Kanban Board

Приложение для управления задачами в стиле Kanban с Django бэкендом и Vue 3 фронтендом.

## Технологии

**Backend:**
- Django 6.0.4
- Django Ninja (API)
- Python 3.12+
- uv (менеджер пакетов)
- SQLite

**Frontend:**
- Vue 3 (Composition API)
- TypeScript
- Vite 8
- Pinia (управление состоянием)
- Vue Router 5
- Bun (менеджер пакетов)

## Требования

- Docker и Docker Compose (рекомендуется)

**Или для локальной разработки:**
- Python 3.12+
- Node.js 20.19+ или 22.12+
- Bun
- uv

## Установка и запуск

### Вариант 1: Docker (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd imctech-kanban
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Отредактируйте `.env` при необходимости:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

4. Запустите контейнеры:
```bash
docker-compose up
```

5. Приложение будет доступно:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

### Вариант 2: Локальная разработка

#### Backend

1. Перейдите в директорию backend:
```bash
cd backend
```

2. Установите зависимости:
```bash
uv sync
```

3. Создайте файл `.env` в корне проекта (см. выше)

4. Примените миграции:
```bash
uv run python manage.py migrate
```

5. Создайте суперпользователя (опционально):
```bash
uv run python manage.py createsuperuser
```

6. Запустите сервер:
```bash
uv run python manage.py runserver
```

Backend будет доступен на http://localhost:8000

#### Frontend

1. Откройте новый терминал и перейдите в директорию frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
bun install
```

3. Запустите dev-сервер:
```bash
bun run dev
```

Frontend будет доступен на http://localhost:5173

## Полезные команды

### Docker

```bash
# Пересобрать контейнеры
docker-compose up --build

# Остановить контейнеры
docker-compose down

# Просмотр логов
docker-compose logs -f

# Выполнить команду в контейнере backend
docker-compose exec backend uv run python manage.py <command>
```

### Backend

```bash
cd backend

# Создать миграции
uv run python manage.py makemigrations

# Применить миграции
uv run python manage.py migrate

# Django shell
uv run python manage.py shell

# Запустить тесты
uv run python manage.py test
```

### Frontend

```bash
cd frontend

# Проверка типов
bun run type-check

# Линтинг и автофикс
bun run lint

# Форматирование кода
bun run format

# Сборка для продакшена
bun run build

# Предпросмотр production сборки
bun run preview
```

## Структура проекта

```
imctech-kanban/
├── backend/              # Django приложение
│   ├── config/          # Настройки Django
│   ├── manage.py
│   └── pyproject.toml
├── frontend/            # Vue 3 приложение
│   ├── src/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   └── main.ts
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Разработка

- Backend использует hot-reload при изменении файлов
- Frontend использует Vite HMR для мгновенного обновления
- Изменения в коде автоматически применяются в Docker контейнерах благодаря volume mounting

## Часовой пояс

Backend настроен на часовой пояс `Asia/Vladivostok`.

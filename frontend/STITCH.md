# Stitch → Vue3 Migration Guide

Гайд по переносу экранов из Stitch MCP в Vue3 приложение с правильной архитектурой.

## Оглавление

1. [Архитектура проекта](#архитектура-проекта)
2. [Процесс переноса экрана](#процесс-переноса-экрана)
3. [Правила переноса](#правила-переноса)
4. [Примеры](#примеры)
5. [Чеклист](#чеклист)

---

## Архитектура проекта

### Структура папок

```
frontend/src/
├── components/
│   ├── ui/              # Базовые UI компоненты (Button, Card, Badge, Icon)
│   ├── layout/          # Layout компоненты (Sidebar, Header, Container)
│   └── features/        # Feature-specific компоненты (BoardCard, ProjectList)
├── views/               # Страницы (роуты)
├── stores/              # Pinia stores (модульные по фичам)
│   ├── boards.ts
│   ├── projects.ts
│   └── auth.ts
├── composables/         # Vue composables
├── types/               # TypeScript типы
│   ├── board.ts
│   ├── project.ts
│   └── user.ts
└── assets/              # Статика
```

### Принципы организации

**Компоненты:**
- `ui/` — атомарные, переиспользуемые везде (Button, Badge, Avatar)
- `layout/` — структурные компоненты (Sidebar, Header, Container)
- `features/` — специфичные для фичи (BoardCard, ProjectCard)

**Stores:**
- Один store на фичу (boards, projects, auth)
- Composition API style (`setup()` функция)
- Типизированный state

**Views:**
- Одна view = одна страница = один роут
- Композиция из компонентов
- Минимум логики (логика в composables/stores)

---

## Процесс переноса экрана

### Шаг 1: Получить экран из Stitch

```typescript
// Используй Stitch MCP tool
mcp__stitch__get_screen({
  name: "projects/{projectId}/screens/{screenId}",
  projectId: "5379286775200031920",
  screenId: "5e041c42a07742e7996e12d15a1820c5"
})
```

Получишь:
- `htmlCode.downloadUrl` — ссылка на HTML
- `screenshot.downloadUrl` — скриншот экрана
- `title` — название экрана

### Шаг 2: Анализ структуры

Открой HTML и определи:

1. **Атомарные компоненты** (используются многократно):
   - Кнопки
   - Бейджи
   - Аватары
   - Иконки
   - Input поля

2. **Составные компоненты** (специфичные для фичи):
   - Карточки (BoardCard, ProjectCard)
   - Списки (BoardList, ProjectList)
   - Формы (CreateBoardForm)

3. **Layout компоненты**:
   - Sidebar
   - Header
   - Container/Wrapper

4. **Данные**:
   - Какие данные отображаются?
   - Какая структура данных?
   - Откуда данные (API, store)?

### Шаг 3: Создать типы

Создай TypeScript интерфейсы в `types/`.

**Пример:** `types/board.ts`

```typescript
export interface Board {
  id: string
  title: string
  category: string
  createdAt: string
  progress: number
  collaborators: User[]
}

export interface User {
  id: string
  name: string
  avatar: string
}
```

### Шаг 4: Создать UI компоненты

Создай базовые переиспользуемые компоненты в `components/ui/`.

**Порядок создания:**
1. Icon.vue (обертка для Material Symbols)
2. Button.vue
3. Badge.vue
4. Avatar.vue
5. Card.vue

См. [Примеры](#примеры) ниже.

### Шаг 5: Создать feature компоненты

Создай специфичные компоненты в `components/features/`.

**Пример:** `components/features/BoardCard.vue`

```vue
<script setup lang="ts">
import type { Board } from '@/types/board'
import Icon from '@/components/ui/Icon.vue'
import Badge from '@/components/ui/Badge.vue'
import Avatar from '@/components/ui/Avatar.vue'

interface Props {
  board: Board
}

defineProps<Props>()

const emit = defineEmits<{
  click: [id: string]
  menu: [id: string]
}>()
</script>

<template>
  <div class="bg-surface-container-lowest rounded-xl p-6 hover:shadow-lg transition-shadow">
    <div class="flex items-start justify-between mb-4">
      <h3 class="text-feature-title text-on-surface">{{ board.title }}</h3>
      <button @click="emit('menu', board.id)" class="text-on-surface-variant">
        <Icon name="more_vert" />
      </button>
    </div>
    
    <Badge variant="neutral" class="mb-4">{{ board.category }}</Badge>
    
    <div class="flex items-center gap-2 text-caption text-on-surface-variant mb-4">
      <Icon name="calendar_today" size="sm" />
      <span>{{ board.createdAt }}</span>
    </div>
    
    <div class="flex items-center gap-2 mb-4">
      <Avatar
        v-for="user in board.collaborators.slice(0, 3)"
        :key="user.id"
        :src="user.avatar"
        :alt="user.name"
        size="sm"
      />
      <span v-if="board.collaborators.length > 3" class="text-caption text-on-surface-variant">
        +{{ board.collaborators.length - 3 }}
      </span>
    </div>
    
    <div class="space-y-2">
      <div class="flex items-center justify-between text-caption">
        <span class="text-on-surface-variant">Progress</span>
        <span class="text-on-surface font-medium">{{ board.progress }}%</span>
      </div>
      <div class="h-2 bg-surface-container rounded-full overflow-hidden">
        <div 
          class="h-full bg-primary transition-all"
          :style="{ width: `${board.progress}%` }"
        />
      </div>
    </div>
  </div>
</template>
```

### Шаг 6: Создать view

Создай страницу в `views/`.

**Пример:** `views/BoardsView.vue`

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useBoardsStore } from '@/stores/boards'
import BoardCard from '@/components/features/BoardCard.vue'
import Button from '@/components/ui/Button.vue'

const boardsStore = useBoardsStore()
const boards = computed(() => boardsStore.activeBoards)

const handleCreateBoard = () => {
  // Логика создания доски
}

const handleBoardClick = (id: string) => {
  // Навигация на доску
}
</script>

<template>
  <div class="container mx-auto px-6 py-8">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-section-heading text-on-surface">Your Boards</h1>
      <Button @click="handleCreateBoard">Create Board</Button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <BoardCard
        v-for="board in boards"
        :key="board.id"
        :board="board"
        @click="handleBoardClick"
      />
    </div>
  </div>
</template>
```

### Шаг 7: Добавить роут

Добавь роут в `router/index.ts`.

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import BoardsView from '@/views/BoardsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/boards',
      name: 'boards',
      component: BoardsView,
    },
  ],
})

export default router
```

### Шаг 8: Создать store

Создай Pinia store в `stores/`.

**Пример:** `stores/boards.ts`

```typescript
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Board } from '@/types/board'

export const useBoardsStore = defineStore('boards', () => {
  // State
  const boards = ref<Board[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeBoards = computed(() => 
    boards.value.filter(b => !b.archived)
  )

  const archivedBoards = computed(() => 
    boards.value.filter(b => b.archived)
  )

  // Actions
  async function fetchBoards() {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/boards')
      boards.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch boards'
    } finally {
      loading.value = false
    }
  }

  async function createBoard(data: Omit<Board, 'id'>) {
    // Логика создания
  }

  async function updateBoard(id: string, data: Partial<Board>) {
    // Логика обновления
  }

  async function deleteBoard(id: string) {
    // Логика удаления
  }

  return {
    // State
    boards,
    loading,
    error,
    // Getters
    activeBoards,
    archivedBoards,
    // Actions
    fetchBoards,
    createBoard,
    updateBoard,
    deleteBoard,
  }
})
```

### Шаг 9: Добавить composables (опционально)

Если есть переиспользуемая логика, создай composable в `composables/`.

**Пример:** `composables/useBoards.ts`

```typescript
import { ref, onMounted } from 'vue'
import { useBoardsStore } from '@/stores/boards'

export function useBoards() {
  const store = useBoardsStore()
  const isInitialized = ref(false)

  onMounted(async () => {
    if (!isInitialized.value) {
      await store.fetchBoards()
      isInitialized.value = true
    }
  })

  return {
    boards: store.activeBoards,
    loading: store.loading,
    error: store.error,
    createBoard: store.createBoard,
    updateBoard: store.updateBoard,
    deleteBoard: store.deleteBoard,
  }
}
```

---

## Правила переноса

### 1. Компонентизация

**Атомарные компоненты** (`components/ui/`):
- Button
- Badge
- Avatar
- Icon
- Input
- Card (базовый контейнер)

**Layout компоненты** (`components/layout/`):
- Sidebar
- Header
- Container
- PageWrapper

**Feature компоненты** (`components/features/`):
- BoardCard
- ProjectCard
- BoardList
- CreateBoardForm

**Правило:** Если компонент используется в 2+ местах → `ui/`. Если специфичен для фичи → `features/`.

### 2. Tailwind классы

**Используй design tokens из DESIGN.md:**

```vue
<!-- ❌ Плохо: хардкод цветов -->
<div class="bg-[#7132f5] text-[#ffffff]">

<!-- ✅ Хорошо: design tokens -->
<div class="bg-primary text-on-primary">
```

**Доступные токены:**

**Цвета:**
- `primary`, `secondary`, `tertiary`
- `surface`, `surface-dim`, `surface-bright`
- `surface-container`, `surface-container-low`, `surface-container-high`
- `on-primary`, `on-secondary`, `on-surface`
- `outline`, `outline-variant`

**Типографика:**
- `text-display-hero` (48px, 700)
- `text-section-heading` (36px, 700)
- `text-sub-heading` (28px, 700)
- `text-feature-title` (22px, 600)
- `text-body` (16px, 400)
- `text-caption` (14px, 400)
- `text-small` (12px, 400)

**Spacing:**
- `space-xs` (4px)
- `space-sm` (8px)
- `space-md` (12px)
- `space-base` (16px)
- `space-lg` (24px)
- `space-xl` (32px)

**Border Radius:**
- `rounded-sm` (3px)
- `rounded` (6px)
- `rounded-md` (8px)
- `rounded-lg` (12px)
- `rounded-xl` (16px)

### 3. TypeScript

**Всегда типизируй:**

```vue
<script setup lang="ts">
import type { Board } from '@/types/board'

// Props
interface Props {
  board: Board
  variant?: 'default' | 'compact'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
})

// Emits
const emit = defineEmits<{
  click: [id: string]
  delete: [id: string]
}>()

// Refs
const isOpen = ref<boolean>(false)
const selectedId = ref<string | null>(null)
</script>
```

### 4. Composition API

**Используй `<script setup>`:**

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Reactive state
const count = ref(0)
const doubled = computed(() => count.value * 2)

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})

// Methods
function increment() {
  count.value++
}
</script>
```

### 5. Иконки

**Используй Material Symbols через `@material-symbols/svg-400`:**

```vue
<!-- components/ui/Icon.vue -->
<script setup lang="ts">
interface Props {
  name: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
}
</script>

<template>
  <span :class="['inline-flex items-center justify-center', sizeClasses[size]]">
    <component :is="() => import(`@material-symbols/svg-400/outlined/${name}.svg`)" />
  </span>
</template>
```

**Использование:**

```vue
<script setup lang="ts">
import Icon from '@/components/ui/Icon.vue'
</script>

<template>
  <Icon name="calendar_today" size="sm" />
  <Icon name="more_vert" />
</template>
```

### 6. State Management

**Модульные stores по фичам:**

```
stores/
├── boards.ts      # Доски
├── projects.ts    # Проекты
├── auth.ts        # Аутентификация
└── ui.ts          # UI state (модалки, сайдбар)
```

**Структура store:**

```typescript
export const useFeatureStore = defineStore('feature', () => {
  // State
  const items = ref<Item[]>([])
  const loading = ref(false)
  
  // Getters
  const activeItems = computed(() => items.value.filter(i => i.active))
  
  // Actions
  async function fetchItems() { /* ... */ }
  
  return { items, loading, activeItems, fetchItems }
})
```

---

## Примеры

### Пример 1: Button компонент

**`components/ui/Button.vue`**

```vue
<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'outlined' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
})

const variantClasses = {
  primary: 'bg-primary text-on-primary hover:bg-primary/90',
  secondary: 'bg-secondary text-on-secondary hover:bg-secondary/90',
  outlined: 'bg-transparent border border-outline text-primary hover:bg-primary/10',
  ghost: 'bg-transparent text-primary hover:bg-primary/10',
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-small',
  md: 'px-4 py-2 text-body',
  lg: 'px-6 py-3 text-feature-title',
}
</script>

<template>
  <button
    :class="[
      'rounded-lg font-medium transition-colors',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      variantClasses[variant],
      sizeClasses[size],
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>
```

**Использование:**

```vue
<Button variant="primary">Create Board</Button>
<Button variant="outlined" size="sm">Cancel</Button>
<Button variant="ghost" disabled>Disabled</Button>
```

### Пример 2: Badge компонент

**`components/ui/Badge.vue`**

```vue
<script setup lang="ts">
interface Props {
  variant?: 'success' | 'neutral' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
})

const variantClasses = {
  success: 'bg-success-subtle text-success-green-text',
  neutral: 'bg-neutral-subtle text-neutral-gray',
  warning: 'bg-warning-subtle text-warning-text',
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center px-2 py-1 rounded-md text-small font-medium',
      variantClasses[variant],
    ]"
  >
    <slot />
  </span>
</template>
```

### Пример 3: BoardCard компонент

См. [Шаг 5](#шаг-5-создать-feature-компоненты) выше.

### Пример 4: BoardsView с роутом

См. [Шаг 6](#шаг-6-создать-view) и [Шаг 7](#шаг-7-добавить-роут) выше.

### Пример 5: Boards Store

См. [Шаг 8](#шаг-8-создать-store) выше.

---

## Чеклист

Используй этот чеклист для каждого экрана:

### Подготовка
- [ ] Получен HTML из Stitch (`mcp__stitch__get_screen`)
- [ ] Проанализирована структура экрана
- [ ] Определены компоненты (атомарные, составные, layout)
- [ ] Определены данные и их структура

### Типы
- [ ] Созданы TypeScript интерфейсы в `types/`
- [ ] Типы экспортированы и переиспользуемы

### UI компоненты
- [ ] Созданы базовые UI компоненты в `components/ui/`
- [ ] Компоненты типизированы (Props, Emits)
- [ ] Компоненты используют design tokens
- [ ] Компоненты переиспользуемы

### Feature компоненты
- [ ] Созданы feature компоненты в `components/features/`
- [ ] Компоненты типизированы
- [ ] Компоненты композируют UI компоненты

### View
- [ ] Создан view в `views/`
- [ ] View композирует компоненты
- [ ] Минимум логики в view (логика в store/composables)

### Роутинг
- [ ] Добавлен роут в `router/index.ts`
- [ ] Роут типизирован (name, params)

### State Management
- [ ] Создан store в `stores/` (если нужен)
- [ ] Store типизирован
- [ ] Store следует модульной структуре

### Composables
- [ ] Созданы composables в `composables/` (если нужны)
- [ ] Composables переиспользуемы

### Проверка
- [ ] Проверена типизация (нет `any`, все типизировано)
- [ ] Проверена адаптивность (mobile, tablet, desktop)
- [ ] Проверены design tokens (нет хардкода цветов/размеров)
- [ ] Проверена доступность (aria-labels, keyboard navigation)
- [ ] Код отформатирован (`bun run format`)
- [ ] Нет ошибок линтера (`bun run lint`)

---

## Полезные команды

```bash
# Установить зависимости
cd frontend
bun install

# Добавить Material Symbols (выполни вручную)
bun add @material-symbols/svg-400

# Запустить dev сервер
bun run dev

# Проверить типы
bun run type-check

# Линтинг и форматирование
bun run lint
bun run format

# Билд
bun run build
```

> **Note:** Зависимость `@material-symbols/svg-400` нужно установить вручную командой `bun add @material-symbols/svg-400` в папке `frontend/`.

---

## Troubleshooting

### Проблема: Иконки не отображаются

**Решение:** Проверь импорт и название иконки:

```vue
<!-- Правильно -->
<Icon name="calendar_today" />

<!-- Неправильно -->
<Icon name="calendar-today" />  <!-- дефис вместо подчеркивания -->
<Icon name="CalendarToday" />   <!-- camelCase вместо snake_case -->
```

### Проблема: Design tokens не работают

**Решение:** Убедись, что Tailwind конфигурация загружена. Проверь `tailwind.config.js`.

### Проблема: TypeScript ошибки в store

**Решение:** Убедись, что типы импортированы:

```typescript
import type { Board } from '@/types/board'  // ✅ type import
import { Board } from '@/types/board'       // ❌ value import
```

---

## Дополнительные ресурсы

- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [TypeScript with Vue](https://vuejs.org/guide/typescript/overview.html)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Material Symbols](https://fonts.google.com/icons)

---

**Последнее обновление:** 2026-05-01

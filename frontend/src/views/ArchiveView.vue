<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search, ArchiveRestore, Layout, CheckSquare } from 'lucide-vue-next'
import type { Board } from '@/types/board'
import type { Task } from '@/types/task'
import type { Column } from '@/types/column'
import TaskCard from '@/components/features/TaskCard.vue'
import Button from '@/components/ui/Button.vue'
import RestoreTaskModal from '@/components/features/RestoreTaskModal.vue'
import ArchiveColumnTasksModal from '@/components/features/ArchiveColumnTasksModal.vue'
import { boardsApi } from '@/api/boards'
import { columnsApi } from '@/api/columns'
import { useTasksStore } from '@/stores/tasks'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const activeTab = ref<'columns' | 'tasks'>('columns')
const searchQuery = ref('')
const loading = ref(false)

const archivedTasks = ref<Task[]>([])
const archivedColumns = ref<Column[]>([])

const toast = useToast()
const tasksStore = useTasksStore()

const isModalOpen = ref(false)
const taskToRestore = ref<Task | null>(null)

const isColumnModalOpen = ref(false)
const columnToView = ref<Column | null>(null)

async function loadArchiveData() {
  if (!props.board) return
  loading.value = true
  try {
    const [tasksRes, columnsRes] = await Promise.all([
      boardsApi.getArchiveTasks(props.board.id),
      boardsApi.getArchiveColumns(props.board.id),
    ])

    // Check if response is wrapped in pagination { items: [], count: ... }
    archivedTasks.value = Array.isArray(tasksRes) ? tasksRes : (tasksRes as any).items || []
    archivedColumns.value = Array.isArray(columnsRes) ? columnsRes : (columnsRes as any).items || []
  } catch (error: any) {
    toast.error(error.message || 'Failed to load archive data')
  } finally {
    loading.value = false
  }
}

watch(
  () => props.board,
  (newBoard) => {
    if (newBoard) {
      loadArchiveData()
    }
  },
  { immediate: true },
)

const filteredTasks = computed(() => {
  if (!searchQuery.value) return archivedTasks.value
  const q = searchQuery.value.toLowerCase()
  return archivedTasks.value.filter(
    (t) => t.title.toLowerCase().includes(q) || t.content?.toLowerCase().includes(q),
  )
})

const filteredColumns = computed(() => {
  if (!searchQuery.value) return archivedColumns.value
  const q = searchQuery.value.toLowerCase()
  return archivedColumns.value.filter((c) => c.name.toLowerCase().includes(q))
})

async function handleRestoreColumn(columnId: string) {
  try {
    await columnsApi.restoreColumn(columnId)
    archivedColumns.value = archivedColumns.value.filter((c) => c.id !== columnId)
    toast.success('Column restored')
  } catch (error: any) {
    toast.error(error.message || 'Failed to restore column')
  }
}

function handleOpenRestoreTask(task: Task) {
  taskToRestore.value = task
  isModalOpen.value = true
}

function handleOpenColumnTasks(column: Column) {
  columnToView.value = column
  isColumnModalOpen.value = true
}

async function handleRestoreTask(taskId: string, targetColumnId: string) {
  try {
    await tasksStore.restoreTask(taskId, targetColumnId)
    archivedTasks.value = archivedTasks.value.filter((t) => t.id !== taskId)
    isModalOpen.value = false
    toast.success('Task restored')
  } catch (error) {
    // Error handled in store
  }
}
</script>

<template>
  <main class="h-full overflow-y-auto p-4 md:p-6 bg-background custom-scrollbar">
    <div class="max-w-7xl mx-auto flex flex-col min-h-full relative">
      <div
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 shrink-0"
      >
        <div class="flex items-center gap-4">
          <h2
            class="font-section-heading text-[36px] font-bold text-on-surface whitespace-nowrap leading-tight tracking-tight"
          >
            Archive
          </h2>
          <span
            class="px-3 py-1 bg-surface-container-high rounded-full text-xs font-bold text-neutral-gray mt-1"
          >
            {{
              activeTab === 'columns'
                ? filteredColumns.length + ' Columns'
                : filteredTasks.length + ' Tasks'
            }}
          </span>
        </div>

        <div class="flex items-center gap-3 w-full md:w-auto">
          <!-- Integrated Search Bar -->
          <div class="relative w-full md:w-64">
            <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-gray" />
            <input
              v-model="searchQuery"
              class="w-full pl-10 pr-4 py-2 bg-white border border-border-gray rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all text-sm"
              :placeholder="activeTab === 'columns' ? 'Search columns...' : 'Search tasks...'"
              type="text"
            />
          </div>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="inline-flex p-1 bg-surface-container-high rounded-xl mb-8 shrink-0 w-fit">
        <button
          @click="activeTab = 'columns'"
          :class="[
            'flex items-center gap-2 px-5 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
            activeTab === 'columns'
              ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
              : 'text-neutral-gray hover:text-primary-container cursor-pointer',
          ]"
        >
          <Layout :size="16" />
          Columns
        </button>
        <button
          @click="activeTab = 'tasks'"
          :class="[
            'flex items-center gap-2 px-5 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
            activeTab === 'tasks'
              ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
              : 'text-neutral-gray hover:text-primary-container cursor-pointer',
          ]"
        >
          <CheckSquare :size="16" />
          Tasks
        </button>
      </div>

      <!-- Content Area -->
      <div class="relative flex-1">
        <Transition name="t-page" mode="out-in">
          <!-- Columns Tab -->
          <div v-if="activeTab === 'columns'" key="columns">
            <div
              v-if="loadingBoard || loading"
              class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6"
            >
              <div
                v-for="i in 4"
                :key="i"
                class="h-32 border border-border-gray rounded-xl animate-pulse bg-surface-container-low/50"
              ></div>
            </div>

            <TransitionGroup
              v-else-if="filteredColumns.length > 0"
              name="t-task"
              tag="div"
              class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6"
            >
              <div
                v-for="col in filteredColumns"
                :key="col.id"
                class="bg-white p-4 md:p-5 rounded-xl border border-border-gray shadow-sm hover:shadow-lg hover:border-primary-container/50 transition-all duration-200 flex flex-col gap-3 cursor-pointer group"
                @click="handleOpenColumnTasks(col)"
              >
                <div class="flex justify-between items-start gap-2">
                  <h3
                    class="font-sub-heading text-[16px] font-bold text-on-surface leading-tight transition-all truncate pr-2"
                    :title="col.name"
                  >
                    {{ col.name }}
                  </h3>

                  <button
                    class="text-[var(--color-primary-container)] bg-[var(--color-primary-container)]/10 hover:bg-[var(--color-primary-container)]/20 transition-all shrink-0 p-2 rounded-xl active:scale-95 shadow-sm"
                    title="Restore Column"
                    @click.stop="handleRestoreColumn(col.id)"
                  >
                    <ArchiveRestore :size="18" />
                  </button>
                </div>

                <p class="text-xs text-text-secondary line-clamp-2 min-h-[18px]">Archived Column</p>

                <div class="flex items-end justify-between mt-auto pt-3">
                  <div class="flex gap-2 flex-wrap items-center">
                    <span
                      class="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-surface-container text-neutral-gray w-fit"
                    >
                      <Layout :size="12" />
                      {{ col.sum_tasks }} task{{ col.sum_tasks !== 1 ? 's' : '' }}
                    </span>
                  </div>
                </div>
              </div>
            </TransitionGroup>

            <div v-else class="h-64 flex flex-col items-center justify-center text-center">
              <div
                class="w-16 h-16 bg-surface-container rounded-full flex items-center justify-center mb-4"
              >
                <Layout :size="32" class="text-neutral-gray opacity-50" />
              </div>
              <p class="text-text-secondary text-lg">No archived columns found.</p>
            </div>
          </div>

          <!-- Tasks Tab -->
          <div v-else-if="activeTab === 'tasks'" key="tasks">
            <div
              v-if="loadingBoard || loading"
              class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6"
            >
              <div
                v-for="i in 4"
                :key="i"
                class="h-48 border border-border-gray rounded-xl animate-pulse bg-surface-container-low/50"
              ></div>
            </div>

            <TransitionGroup
              v-else-if="filteredTasks.length > 0"
              name="t-task"
              tag="div"
              class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 pb-6 items-stretch"
            >
              <div v-for="task in filteredTasks" :key="task.id" class="h-full">
                <TaskCard
                  :task="task"
                  :is-archive-mode="true"
                  class="h-full opacity-70 hover:opacity-100 transition-opacity duration-300 cursor-default"
                  @click="handleOpenRestoreTask(task)"
                  @restore="handleOpenRestoreTask"
                />
              </div>
            </TransitionGroup>

            <div v-else class="h-64 flex flex-col items-center justify-center text-center">
              <div
                class="w-16 h-16 bg-surface-container rounded-full flex items-center justify-center mb-4"
              >
                <CheckSquare :size="32" class="text-neutral-gray opacity-50" />
              </div>
              <p class="text-text-secondary text-lg">No archived tasks found.</p>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <RestoreTaskModal
      :is-open="isModalOpen"
      :task="taskToRestore"
      @close="isModalOpen = false"
      @restore="handleRestoreTask"
    />

    <ArchiveColumnTasksModal
      v-if="board"
      :is-open="isColumnModalOpen"
      :column="columnToView"
      :board-id="board.id"
      @close="isColumnModalOpen = false"
    />
  </main>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* Reuse t-task transitions from BacklogTasksView */
.t-task-move,
.t-task-enter-active,
.t-task-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.t-task-enter-from,
.t-task-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.t-task-leave-active {
  position: absolute;
}
</style>

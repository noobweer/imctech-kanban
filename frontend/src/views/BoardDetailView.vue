<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { Plus, Layout } from 'lucide-vue-next'
import { useColumnsStore } from '@/stores/columns'
import { useTasksStore } from '@/stores/tasks'
import type { Board } from '@/types/board'
import type { Task, TaskIn, TaskUpdateIn } from '@/types/task'
import Button from '@/components/ui/Button.vue'
import ColumnCard from '@/components/features/ColumnCard.vue'
import TaskModal from '@/components/features/TaskModal.vue'
import ColumnModal from '@/components/features/ColumnModal.vue'

const props = defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const columnsStore = useColumnsStore()
const tasksStore = useTasksStore()
const loadingColumns = ref(columnsStore.columns.length === 0)

const isModalOpen = ref(false)
const isColumnModalOpen = ref(false)
const editingTask = ref<Task | null>(null)
const defaultColumnForNewTask = ref<string | undefined>(undefined)

async function loadColumns() {
  if (!props.board) return
  
  // If we already have columns, load silently in the background
  const isSilent = columnsStore.columns.length > 0
  
  if (!isSilent) loadingColumns.value = true
  try {
    await columnsStore.fetchColumns(props.board.id, isSilent)
    // Start polling after successful initial fetch
    columnsStore.startPolling(props.board.id)
  } finally {
    loadingColumns.value = false
  }
}

async function loadTasks() {
  if (!props.board) return
  await tasksStore.fetchTasks(props.board.id, true)
  tasksStore.startPolling(props.board.id)
}

function getTasksForColumn(columnId: string) {
  return tasksStore.getTasksByColumnId(columnId)
}

async function handleCreateDefaultColumns() {
  if (!props.board) return
  await columnsStore.createDefaultColumns(props.board.id)
}

function handleCreateColumn() {
  isColumnModalOpen.value = true
}

async function handleSaveColumn(name: string) {
  if (!props.board) return
  await columnsStore.createColumn(props.board.id, { name })
  isColumnModalOpen.value = false
}

async function handleRenameColumn(id: string, name: string) {
  await columnsStore.updateColumn(id, { name })
}

async function handleArchiveColumn(id: string) {
  if (confirm('Are you sure you want to archive this column?')) {
    await columnsStore.archiveColumn(id)
  }
}

async function handleMoveColumn(id: string, direction: 'left' | 'right') {
  const currentColumns = columnsStore.activeColumns
  const index = currentColumns.findIndex(c => c.id === id)
  if (index === -1) return

  const targetColumn = direction === 'left' ? currentColumns[index - 1] : currentColumns[index + 1]
  if (!targetColumn) return

  await columnsStore.moveColumn(id, targetColumn.position)
}

function handleAddTask(columnId: string) {
  editingTask.value = null
  defaultColumnForNewTask.value = columnId
  isModalOpen.value = true
}

function handleEditTask(task: Task) {
  editingTask.value = task
  defaultColumnForNewTask.value = undefined
  isModalOpen.value = true
}

async function handleSaveTask(data: TaskIn | TaskUpdateIn) {
  if (!props.board) return
  try {
    if (editingTask.value) {
      await tasksStore.updateTask(editingTask.value.id, data as TaskUpdateIn)
    } else {
      await tasksStore.createTask(props.board.id, data as TaskIn)
    }
    isModalOpen.value = false
  } catch (error) {
    // Error handled in store
  }
}

async function handleMoveTask(taskId: string, targetColumnId: string, position: number) {
  if (!props.board) return
  await tasksStore.moveTask(taskId, targetColumnId, position)
}

const isDraggingTask = ref(false)

watch(() => props.board, (newBoard) => {
  if (newBoard) {
    loadColumns()
    loadTasks()
  }
}, { immediate: true })

onMounted(() => {
  loadColumns()
  if (props.board) loadTasks()
})

onUnmounted(() => {
  columnsStore.stopPolling()
  tasksStore.stopPolling()
})
</script>

<template>
  <!-- Column Canvas -->
  <main v-dragscroll="!isDraggingTask" class="h-full overflow-x-scroll p-4 md:p-6 bg-background custom-scrollbar-x cursor-grab active:cursor-grabbing">
    <div v-if="loadingBoard || loadingColumns" class="flex gap-4 md:gap-6 min-h-full max-w-max">
      <div v-for="i in 4" :key="i" class="w-80 h-[500px] border border-border-gray rounded-xl animate-pulse"></div>
    </div>
    
    <div v-else-if="columnsStore.activeColumns.length > 0" class="flex items-start gap-6 pb-4 min-h-full w-max">
      <TransitionGroup name="t-column">
        <ColumnCard 
          v-for="(column, index) in columnsStore.activeColumns" 
          :key="column.id"
          :column="column"
          :tasks="getTasksForColumn(column.id)"
          :is-first="index === 0"
          :is-last="index === columnsStore.activeColumns.length - 1"
          @move-left="handleMoveColumn($event, 'left')"
          @move-right="handleMoveColumn($event, 'right')"
          @rename="handleRenameColumn"
          @archive="handleArchiveColumn"
          @add-task="handleAddTask"
          @edit-task="handleEditTask"
          @move-task="handleMoveTask"
          @drag-start="isDraggingTask = true"
          @drag-end="isDraggingTask = false"
        />
        
        <!-- Add Column Placeholder -->
        <button 
          key="add-column-button"
          class="w-80 h-16 flex items-center justify-center gap-2 border-2 border-dashed border-border-gray/30 rounded-xl text-text-secondary hover:border-primary-container/30 hover:text-primary-container transition-all shrink-0 cursor-pointer bg-surface-container-low/20"
          @click="handleCreateColumn"
        >
          <Plus :size="20" />
          Add Another Column
        </button>
      </TransitionGroup>
    </div>

    <div v-else class="h-full flex flex-col items-center justify-center text-center">
      <div class="bg-surface-white p-12 rounded-2xl shadow-xl border border-border-gray max-w-lg">
        <div class="w-20 h-20 bg-surface-container-low rounded-full flex items-center justify-center mx-auto mb-6">
          <Layout :size="40" class="text-primary-container opacity-40" />
        </div>
        <h2 class="text-2xl font-bold text-text-primary mb-3">No columns yet</h2>
        <p class="text-text-secondary mb-8 leading-relaxed">Your board is empty. Start by loading default columns or design your custom workflow from scratch.</p>
        <div class="flex items-center justify-center gap-4">
          <Button variant="primary" @click="handleCreateDefaultColumns">Load Defaults</Button>
          <Button variant="outlined" @click="handleCreateColumn">Create Custom</Button>
        </div>
      </div>
    </div>
    
    <TaskModal 
      :isOpen="isModalOpen" 
      :task="editingTask" 
      :boardId="board?.id"
      :defaultColumnId="defaultColumnForNewTask"
      @close="isModalOpen = false" 
      @save="handleSaveTask" 
    />

    <ColumnModal
      :isOpen="isColumnModalOpen"
      @close="isColumnModalOpen = false"
      @save="handleSaveColumn"
    />
  </main>
</template>

<style scoped>
.custom-scrollbar-x::-webkit-scrollbar {
  height: 8px;
}
.custom-scrollbar-x::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar-x::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 10px;
}
.custom-scrollbar-x::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* TransitionGroup classes for columns */
.t-column-move,
.t-column-enter-active,
.t-column-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.t-column-enter-from,
.t-column-leave-to {
  opacity: 0;
}

.t-column-leave-active {
  position: absolute;
}
</style>

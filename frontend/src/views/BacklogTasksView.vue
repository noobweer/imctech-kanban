<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Plus, Search } from 'lucide-vue-next'
import type { Board } from '@/types/board'
import type { Task, TaskIn, TaskUpdateIn } from '@/types/task'
import Button from '@/components/ui/Button.vue'
import { useToast } from '@/composables/useToast'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'
import TaskCard from '@/components/features/TaskCard.vue'
import TaskModal from '@/components/features/TaskModal.vue'
import TaskViewModal from '@/components/features/TaskViewModal.vue'
import { useTasksStore } from '@/stores/tasks'
import { useColumnsStore } from '@/stores/columns'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const tasksStore = useTasksStore()
const columnsStore = useColumnsStore()
const authStore = useAuthStore()
const isMentor = computed(() => authStore.user?.role === 'mentor')
const searchQuery = ref('')

const isModalOpen = ref(false)
const isViewModalOpen = ref(false)
const showArchiveTaskConfirm = ref(false)
const taskToArchive = ref<Task | null>(null)
const editingTask = ref<Task | null>(null)
const viewingTask = ref<Task | null>(null)

// Initialize and poll tasks
watch(() => props.board, (newBoard) => {
  if (newBoard) {
    tasksStore.fetchTasks(newBoard.id)
    tasksStore.startPolling(newBoard.id)
  }
}, { immediate: true })

onUnmounted(() => {
  tasksStore.stopPolling()
})

const localBacklogTasks = ref<Task[]>([...tasksStore.backlogTasks])

watch(() => tasksStore.backlogTasks, (newTasks) => {
  if (newTasks) {
    localBacklogTasks.value = [...newTasks]
  }
}, { deep: true, immediate: true })

const filteredTasks = computed(() => {
  let list = localBacklogTasks.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(t => t.title.toLowerCase().includes(q) || t.content?.toLowerCase().includes(q))
  }
  return list
})

function handleAddTask() {
  editingTask.value = null
  isModalOpen.value = true
}

function handleViewTask(task: Task) {
  viewingTask.value = task
  isViewModalOpen.value = true
}

function handleEditTask(task: Task) {
  editingTask.value = task
  isViewModalOpen.value = false
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
    // Error handled in store via toast
  }
}

async function handleArchiveTask(task: Task) {
  taskToArchive.value = task
  showArchiveTaskConfirm.value = true
}

async function confirmArchiveTask() {
  if (taskToArchive.value) {
    await tasksStore.archiveTask(taskToArchive.value.id)
    showArchiveTaskConfirm.value = false
    taskToArchive.value = null
  }
}

async function handlePushToBoard(task: Task) {
  if (!props.board) return
  // Fetch columns if not loaded to find the first active board column
  if (columnsStore.columns.length === 0) {
    await columnsStore.fetchColumns(props.board.id, true)
  }
  const firstActiveColumn = columnsStore.activeColumns[0]
  if (!firstActiveColumn) {
    alert('Please create a column on the board first.')
    return
  }
  
  // Find where it should go in that column (bottom of the column)
  const targetTasks = tasksStore.getTasksByColumnId(firstActiveColumn.id)
  const position = targetTasks.length
  
  await tasksStore.moveTask(task.id, firstActiveColumn.id, position)
}
</script>

<template>
  <!-- Main Content -->
  <main v-dragscroll="true" class="h-full overflow-y-auto p-4 md:p-6 bg-background custom-scrollbar cursor-grab active:cursor-grabbing">
    <div class="max-w-7xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-4 flex-1">
          <h2 class="font-section-heading text-[36px] font-bold text-on-surface whitespace-nowrap leading-tight tracking-tight">
            Backlog Tasks
          </h2>
          <span class="px-3 py-1 bg-surface-container-high rounded-full text-xs font-bold text-neutral-gray">
            {{ filteredTasks.length }} Tasks
          </span>
          
          <!-- Integrated Search Bar -->
          <div class="relative w-full max-w-md hidden md:block">
            <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-gray" />
            <input
              v-model="searchQuery"
              class="w-full pl-10 pr-4 py-2 bg-white border border-border-gray rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all text-sm"
              placeholder="Search tasks..."
              type="text"
            />
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <!-- Search for mobile -->
          <button class="p-2 border border-border-gray rounded-xl hover:bg-white transition-colors md:hidden text-neutral-gray">
            <Search :size="20" />
          </button>
          <Button v-if="!isMentor" variant="primary" size="sm" class="gap-2 whitespace-nowrap" @click="handleAddTask">
            <Plus :size="20" /> 
            Add Task
          </Button>
        </div>      
      </div>

      <!-- 4-column Grid -->
      <div v-if="loadingBoard || tasksStore.loading && tasksStore.tasks.length === 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div v-for="i in 8" :key="i" class="h-48 border border-border-gray rounded-xl animate-pulse bg-surface-container-low/50"></div>
      </div>

      <TransitionGroup 
        v-else 
        name="t-task"
        tag="div" 
        class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 pb-6 relative"
      >
        <TaskCard 
          v-for="task in filteredTasks" 
          :key="task.id" 
          :task="task"
          :allow-push-to-board="true"
          @click="handleViewTask"
          @edit="handleEditTask"
          @archive="handleArchiveTask"
          @push-to-board="handlePushToBoard"
        />
      </TransitionGroup>
      
      <div v-if="!tasksStore.loading && filteredTasks.length === 0" class="mt-12 text-center text-text-secondary">
        <p>No tasks found in backlog. {{ searchQuery ? 'Try adjusting your search.' : 'Create one to get started!' }}</p>
      </div>
    </div>
    
    <TaskModal 
      :isOpen="isModalOpen" 
      :task="editingTask"
      :boardId="board?.id" 
      @close="isModalOpen = false" 
      @save="handleSaveTask" 
    />

    <TaskViewModal
      :isOpen="isViewModalOpen"
      :task="viewingTask"
      :boardId="board?.id"
      @close="isViewModalOpen = false"
      @edit="handleEditTask"
    />

    <ConfirmModal
      :is-open="showArchiveTaskConfirm"
      title="Archive Task"
      description="Are you sure you want to archive this task? It will be moved to the Archive tab."
      confirm-text="Archive Task"
      is-destructive
      @close="showArchiveTaskConfirm = false"
      @confirm="confirmArchiveTask"
    />
  </main>
</template>

<style scoped>
.font-sub-heading {
  font-family: 'Space Grotesk', sans-serif;
}

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

/* TransitionGroup classes for tasks */
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

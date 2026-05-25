<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Plus, Search } from 'lucide-vue-next'
import type { Board } from '@/types/board'
import type { Task, TaskIn, TaskUpdateIn } from '@/types/task'
import Button from '@/components/ui/Button.vue'
import TaskCard from '@/components/features/TaskCard.vue'
import TaskModal from '@/components/features/TaskModal.vue'
import { useTasksStore } from '@/stores/tasks'

const props = defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const tasksStore = useTasksStore()
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingTask = ref<Task | null>(null)

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

const filteredTasks = computed(() => {
  let list = tasksStore.backlogTasks
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

function handleEditTask(task: Task) {
  editingTask.value = task
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
</script>

<template>
  <!-- Main Content -->
  <main v-dragscroll class="h-full overflow-y-auto p-4 md:p-6 bg-background custom-scrollbar cursor-grab active:cursor-grabbing">
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
          <Button variant="primary" size="sm" class="gap-2 whitespace-nowrap" @click="handleAddTask">
            <Plus :size="20" /> 
            Add Task
          </Button>
        </div>      
      </div>

      <!-- 4-column Grid -->
      <div v-if="loadingBoard || tasksStore.loading && tasksStore.tasks.length === 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div v-for="i in 8" :key="i" class="h-48 border border-border-gray rounded-xl animate-pulse bg-surface-container-low/50"></div>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 pb-6">
        <TaskCard 
          v-for="task in filteredTasks" 
          :key="task.id" 
          :task="task"
          @click="handleEditTask"
          @edit="handleEditTask"
        />
      </div>
      
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
</style>

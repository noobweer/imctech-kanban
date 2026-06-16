<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { X, Loader2 } from 'lucide-vue-next'
import { apiClient } from '@/api/client'
import type { Board } from '@/types/board'
import type { Task } from '@/types/task'
import type { ActivityMemberOut } from '@/api/overview'
import TaskCard from '@/components/features/TaskCard.vue'
import TaskViewModal from '@/components/features/TaskViewModal.vue'
import Select from '@/components/ui/Select.vue'
import Modal from '@/components/ui/Modal.vue'

const props = defineProps<{
  isOpen: boolean
  board: Board
  initialUsername: string
  members: ActivityMemberOut[]
}>()

const emit = defineEmits<{
  close: []
}>()

const selectedUsername = ref(props.initialUsername)
const selectedFilter = ref<'date' | 'deadline'>('date')
const selectedColumnId = ref<string>('')

watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      selectedUsername.value = props.initialUsername
      fetchTasks()
    }
  },
)

const tasks = ref<Task[]>([])
const loading = ref(false)

const activeColumns = props.members && props.members.length > 0 ? (props.members[0]?.columns || []) : []

async function fetchTasks() {
  loading.value = true
  try {
    const query: Record<string, string> = {
      assignee: selectedUsername.value,
    }
    if (selectedFilter.value === 'date') {
      query.sort_by = '-added_to_board_at'
    } else if (selectedFilter.value === 'deadline') {
      query.deadline_filter = 'due_soon_or_overdue'
    }
    if (selectedColumnId.value) {
      query.column_id = selectedColumnId.value
    }

    // In our backend, list_tasks handles these filters now.
    // It returns paginated { items: [], count: n }
    const response = await apiClient<any>(`/boards/${props.board.id}/tasks`, { query })
    tasks.value = response.items || []
  } catch (e) {
    console.error('Failed to fetch user tasks', e)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTasks()
})

watch([selectedUsername, selectedFilter, selectedColumnId], () => {
  if (props.isOpen) {
    fetchTasks()
  }
})

const isTaskViewOpen = ref(false)
const viewingTask = ref<Task | null>(null)

function handleViewTask(task: Task) {
  viewingTask.value = task
  isTaskViewOpen.value = true
}
</script>

<template>
  <Modal
    :model-value="isOpen && !isTaskViewOpen"
    max-width="1024px"
    @update:model-value="emit('close')"
  >
    <!-- Header -->
    <template #header>
      <div class="flex items-center gap-4 flex-1 pr-4">
        <h2 class="text-xl font-bold font-product text-on-surface whitespace-nowrap">
          Member Tasks
        </h2>

        <!-- User Selector -->
        <div class="w-64">
          <Select
            v-model="selectedUsername"
            :options="
              members.map((m) => ({ label: `${m.name} (@${m.username})`, value: m.username }))
            "
          />
        </div>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <!-- Filters Row -->
      <div
        class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shrink-0 pb-6 border-b border-border-gray"
      >
        <!-- Column Filter -->
        <div class="flex items-center gap-3">
          <span class="text-sm font-semibold text-neutral-gray">Column:</span>
          <div class="w-48">
            <Select
              v-model="selectedColumnId"
              :options="[
                { label: 'All Columns', value: '' },
                ...activeColumns.map((col) => ({ label: col.column_name, value: col.column_id })),
              ]"
            />
          </div>
        </div>

        <!-- Mutually Exclusive Filter (Date / Deadline) -->
        <div class="inline-flex p-1 bg-surface-container-high rounded-xl shrink-0">
          <button
            :class="[
              'px-5 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
              selectedFilter === 'date'
                ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
                : 'text-neutral-gray hover:text-primary-container cursor-pointer',
            ]"
            @click="selectedFilter = 'date'"
          >
            Date
          </button>
          <button
            :class="[
              'px-5 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
              selectedFilter === 'deadline'
                ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
                : 'text-neutral-gray hover:text-primary-container cursor-pointer',
            ]"
            @click="selectedFilter = 'deadline'"
          >
            Deadline
          </button>
        </div>
      </div>

      <!-- Content Body -->
      <div class="min-h-[300px]">
        <div v-if="loading" class="flex justify-center items-center h-full min-h-[300px]">
          <Loader2 class="animate-spin text-primary-container" :size="32" />
        </div>

        <div
          v-else-if="tasks.length > 0"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
        >
          <TaskCard
            v-for="task in tasks"
            :key="task.id"
            :task="task"
            :allow-push-to-board="false"
            @click="handleViewTask(task)"
          />
        </div>

        <div
          v-else
          class="flex flex-col justify-center items-center h-full min-h-[300px] text-text-secondary"
        >
          <p>No tasks found for this user with the current filters.</p>
        </div>
      </div>
    </div>
  </Modal>

  <TaskViewModal
    :isOpen="isTaskViewOpen"
    :task="viewingTask"
    :boardId="board.id"
    @close="isTaskViewOpen = false"
  />
</template>

<style scoped>
.font-product {
  font-family: 'Kraken-Product', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c3c4ce;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9497a9;
}
</style>

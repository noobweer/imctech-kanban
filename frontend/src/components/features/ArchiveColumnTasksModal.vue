<script setup lang="ts">
import { ref, watch } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import TaskViewModal from '@/components/features/TaskViewModal.vue'
import { tasksApi } from '@/api/tasks'
import type { Task } from '@/types/task'
import type { Column } from '@/types/column'
import { CheckSquare, CalendarDays, Layout } from 'lucide-vue-next'
import { format } from 'date-fns'

const props = defineProps<{
  isOpen: boolean
  column: Column | null
  boardId: string
}>()

const emit = defineEmits<{
  close: []
}>()

const loading = ref(false)
const tasks = ref<Task[]>([])
const error = ref('')

async function fetchTasks() {
  if (!props.column || !props.boardId) return

  loading.value = true
  error.value = ''
  try {
    const res = await tasksApi.getBoardTasks(props.boardId, { column_id: props.column.id })
    // @ts-ignore - handling paginated response
    tasks.value = Array.isArray(res) ? res : res.items || []
  } catch (err: any) {
    error.value = err.message || 'Failed to load tasks'
  } finally {
    loading.value = false
  }
}

watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal && props.column) {
      fetchTasks()
    } else {
      tasks.value = []
    }
  },
)

function formatTaskDate(task: Task) {
  if (!task.deadline) return ''
  return format(new Date(task.deadline), 'MMM d, yyyy')
}

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
    max-width="500px"
    @update:model-value="emit('close')"
  >
    <div class="flex flex-col h-[500px] max-h-[70vh]">
      <!-- Header -->
      <div class="shrink-0 mb-4 px-2 pt-2">
        <h3
          class="text-xl font-bold text-on-surface mb-1 flex items-center gap-2 truncate"
          :title="column?.name"
        >
          <Layout :size="20" class="text-neutral-gray" />
          {{ column?.name }}
        </h3>
        <p class="text-sm text-text-secondary">Archived Tasks: {{ column?.sum_tasks || 0 }}</p>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto custom-scrollbar px-2 pb-2">
        <div v-if="loading" class="flex flex-col gap-3">
          <div
            v-for="i in 3"
            :key="i"
            class="h-16 animate-pulse bg-surface-container-low rounded-xl"
          ></div>
        </div>

        <div
          v-else-if="error"
          class="h-full flex items-center justify-center p-6 text-center text-error bg-[var(--color-error)]/5 rounded-xl border border-error/20"
        >
          {{ error }}
        </div>

        <div
          v-else-if="tasks.length === 0"
          class="h-full flex flex-col items-center justify-center text-center p-6 text-text-secondary bg-surface-container-lowest rounded-xl border border-border-gray"
        >
          <CheckSquare :size="32" class="mb-3 opacity-50" />
          <p>No tasks found in this column.</p>
        </div>

        <div v-else class="flex flex-col gap-3">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="bg-white p-4 md:p-5 rounded-xl border border-border-gray shadow-sm hover:shadow-lg hover:border-primary-container/50 transition-all duration-200 group flex flex-col gap-2 cursor-pointer"
            @click="handleViewTask(task)"
          >
            <h4
              class="font-semibold text-on-surface text-sm leading-tight group-hover:text-primary-container transition-colors line-clamp-2"
            >
              {{ task.title }}
            </h4>
            <div class="flex items-center justify-between mt-1">
              <span
                class="flex items-center gap-1 text-[11px] font-medium text-neutral-gray bg-surface-container-low px-2 py-0.5 rounded-full"
              >
                <CheckSquare :size="12" />
                {{ task.checklist_done_count }}/{{ task.checklist_total_count }}
              </span>

              <span
                v-if="task.deadline"
                class="flex items-center gap-1 text-[11px] font-medium text-text-secondary"
              >
                <CalendarDays :size="12" />
                {{ formatTaskDate(task) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end pt-2">
        <Button variant="primary" @click="emit('close')">Close</Button>
      </div>
    </template>
  </Modal>

  <TaskViewModal
    :isOpen="isTaskViewOpen"
    :task="viewingTask"
    :boardId="boardId"
    @close="isTaskViewOpen = false"
  />
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
</style>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useOverviewStore } from '@/stores/overview'
import type { Board } from '@/types/board'
import type { Task } from '@/types/task'
import TaskCard from '@/components/features/TaskCard.vue'
import TaskViewModal from '@/components/features/TaskViewModal.vue'

const props = defineProps<{
  board: Board
}>()

const overviewStore = useOverviewStore()
const data = computed(() => overviewStore.deadlinesData)
const loading = computed(() => overviewStore.isLoadingDeadlines)

const isTaskViewOpen = ref(false)
const viewingTask = ref<Task | null>(null)

function handleTaskClick(task: any) {
  viewingTask.value = task as Task
  isTaskViewOpen.value = true
}
</script>

<template>
  <div class="flex flex-col gap-10">
    
    <div v-if="loading && !data" class="flex flex-col gap-4">
      <div class="h-6 w-32 bg-[rgba(148,151,169,0.12)] rounded animate-pulse mb-2"></div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="h-32 bg-[rgba(148,151,169,0.12)] rounded-xl animate-pulse"></div>
      </div>
    </div>

    <template v-else-if="data">
      <!-- Overdue Section -->
      <section v-if="data.overdue.length > 0">
        <h3 class="text-lg font-bold text-near-black mb-4 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[var(--color-error)]"></span>
          Overdue
          <span class="text-sm font-normal text-cool-gray ml-2">{{ data.overdue.length }} tasks</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- We cast DeadlineTaskOut to Task conceptually or just map needed fields.
               TaskCard expects a full Task, so we might need to cast.
               Our DeadlineTaskOut provides id, title, deadline, column, assignees, priority, added_to_board_at. -->
          <TaskCard 
            v-for="(task, index) in data.overdue" 
            :key="task.id"
            :task="(task as unknown as Task)"
            :allow-push-to-board="false"
            class="animate-fade-up"
            :style="{ animationDelay: `${index * 50}ms` }"
            @click="handleTaskClick"
          />
        </div>
      </section>

      <!-- Due Soon Section -->
      <section v-if="data.due_soon.length > 0">
        <h3 class="text-lg font-bold text-near-black mb-4 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[#f59e0b]"></span>
          Due Soon
          <span class="text-sm font-normal text-cool-gray ml-2">{{ data.due_soon.length }} tasks</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <TaskCard 
            v-for="(task, index) in data.due_soon" 
            :key="task.id"
            :task="(task as unknown as Task)"
            :allow-push-to-board="false"
            class="animate-fade-up"
            :style="{ animationDelay: `${index * 50}ms` }"
            @click="handleTaskClick"
          />
        </div>
      </section>
      
      <div v-if="data.overdue.length === 0 && data.due_soon.length === 0" class="flex flex-col items-center justify-center py-20 text-cool-gray">
        <p>No tasks with upcoming deadlines.</p>
      </div>
    </template>

    <TaskViewModal
      :isOpen="isTaskViewOpen"
      :task="viewingTask"
      :boardId="board.id"
      @close="isTaskViewOpen = false"
    />
  </div>
</template>

<style scoped>
.text-near-black {
  color: #101114;
}
.text-cool-gray {
  color: #686b82;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-up {
  opacity: 0;
  animation: fadeUp 0.4s ease-out forwards;
}
</style>

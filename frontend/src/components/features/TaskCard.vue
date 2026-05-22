<script setup lang="ts">
import { computed } from 'vue'
import { MoreVertical, CalendarDays, Check } from 'lucide-vue-next'
import type { Task } from '@/types/task'

const props = defineProps<{
  task: Task
}>()

const emit = defineEmits<{
  click: [task: Task]
  edit: [task: Task]
}>()

const isDone = computed(() => props.task.status === 'archived' || props.task.column_name?.toLowerCase() === 'done')

const progressText = computed(() => `${props.task.checklist_done_count}/${props.task.checklist_total_count}`)

const progressClass = computed(() => {
  if (props.task.checklist_done_count === props.task.checklist_total_count && props.task.checklist_total_count > 0) {
    return 'bg-success-subtle text-success-green-text'
  }
  if (props.task.checklist_done_count > 0) {
    return 'bg-surface-container text-neutral-gray'
  }
  return 'bg-surface-container text-neutral-gray opacity-70'
})

const firstTag = computed(() => props.task.tags?.[0] || 'Task')

const tagClass = computed(() => {
  if (isDone.value) return 'bg-surface-container-low text-neutral-gray'
  if (firstTag.value.toLowerCase() === 'bug') return 'bg-error-container text-error'
  return 'bg-surface-container-high text-on-surface'
})

const formattedDeadline = computed(() => {
  if (!props.task.deadline) return 'No deadline'
  const date = new Date(props.task.deadline)
  return `Due to ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`
})

const isDeadlineClose = computed(() => {
  if (!props.task.deadline || isDone.value) return false
  const deadlineTime = new Date(props.task.deadline).getTime()
  const now = new Date().getTime()
  const hoursLeft = (deadlineTime - now) / (1000 * 60 * 60)
  // Highlight if past due or within 48 hours
  return hoursLeft <= 48
})

const assigneeName = computed(() => props.task.assignees?.[0] || 'Unassigned')
const assigneeInitial = computed(() => assigneeName.value.charAt(0).toUpperCase())

</script>

<template>
  <div 
    class="bg-white p-5 rounded-xl border border-border-gray shadow-[0px_4px_12px_rgba(0,0,0,0.03)] hover:shadow-md hover:border-primary-container/50 transition-all flex flex-col gap-3 cursor-pointer group"
    :class="{ 'opacity-75 grayscale-[0.2]': isDone }"
    @click="emit('click', task)"
  >
    <div class="flex justify-between items-start">
      <h3 class="font-sub-heading text-[18px] font-bold text-on-surface" :class="{ 'line-through text-text-secondary': isDone }">
        {{ task.title }}
      </h3>
      <button class="text-neutral-gray hover:text-on-surface transition-colors" @click.stop="emit('edit', task)">
        <MoreVertical :size="20" />
      </button>
    </div>
    
    <p class="text-sm text-text-secondary line-clamp-1 min-h-[20px]">
      {{ task.content }}
    </p>
    
    <div class="flex items-center gap-2 text-neutral-gray/80 mb-1" :class="{ 'text-error font-semibold': isDeadlineClose }">
      <CalendarDays :size="16" />
      <span class="text-xs font-medium">{{ formattedDeadline }}</span>
    </div>
    
    <div class="flex items-center justify-between mt-auto pt-2">
      <div class="flex gap-2">
        <span 
          v-if="task.checklist_total_count > 0"
          class="px-3 py-1 rounded-full text-[11px] font-bold"
          :class="progressClass"
        >
          {{ progressText }}
        </span>
        <span 
          class="px-3 py-1 rounded-full text-[11px] font-bold capitalize"
          :class="tagClass"
        >
          {{ firstTag }}
        </span>
      </div>
      
      <div class="flex items-center gap-2">
        <span class="text-xs font-medium text-neutral-gray">{{ assigneeName }}</span>
        <div class="w-6 h-6 rounded-full bg-primary-container/20 text-primary-container border border-surface-white flex items-center justify-center text-[10px] font-bold">
          {{ assigneeInitial }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-sub-heading {
  font-family: 'Space Grotesk', sans-serif;
}
</style>

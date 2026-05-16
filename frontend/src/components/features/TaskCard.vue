<script setup lang="ts">
import { computed } from 'vue'
import { MoreVertical, Calendar, Check } from 'lucide-vue-next'
import type { Task } from '@/types/task'

const props = defineProps<{
  task: Task
}>()

const isDone = computed(() => props.task.status === 'done')

const progressText = computed(() => `${props.task.subtasksCompleted}/${props.task.subtasksTotal}`)

const progressClass = computed(() => {
  if (props.task.status === 'inprogress') return 'border-primary-container/20 text-primary-container'
  if (props.task.status === 'review' || props.task.status === 'done') return 'bg-success-subtle text-success-green-text border-success-green-text/10'
  return 'border-border-gray'
})

const tagClass = computed(() => {
  if (isDone.value) return 'bg-surface-container-low text-neutral-gray border-border-gray'
  if (props.task.type === 'Bug') return 'bg-error/5 text-error border-error/10'
  return 'bg-surface-container-low text-text-secondary border-border-gray'
})
</script>

<template>
  <article 
    class="bg-surface-white p-4 rounded-xl shadow-[0_4px_24px_rgba(0,0,0,0.03)] border border-border-gray mb-4 hover:border-primary-container transition-all cursor-pointer group"
    :class="{ 'opacity-75 grayscale-[0.2] hover:grayscale-0': isDone }"
  >
    <div class="flex justify-between items-start mb-2">
      <h3 class="font-bold text-text-primary" :class="{ 'line-through': isDone }">
        {{ task.title }}
      </h3>
      <button class="text-neutral-gray group-hover:text-text-secondary transition-colors">
        <MoreVertical :size="16" />
      </button>
    </div>

    <p class="text-sm text-text-secondary mb-4 line-clamp-2">
      {{ task.description }}
    </p>

    <div class="flex items-center gap-2 text-xs text-text-secondary mb-4">
      <component :is="isDone ? Check : Calendar" :size="14" />
      <span>{{ isDone ? `Completed on ${task.completedDate}` : `Due to ${task.dueDate}` }}</span>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <span 
        class="px-2 py-1 text-[10px] font-bold rounded-xl border"
        :class="progressClass"
      >
        {{ progressText }}
      </span>
      
      <span 
        class="px-2 py-1 text-[10px] font-bold rounded-xl border"
        :class="tagClass"
      >
        {{ task.type }}
      </span>

      <div class="flex items-center gap-1 ml-auto">
        <span class="text-[10px] text-text-secondary font-medium">{{ task.assignee.name }}</span>
        <img 
          :alt="task.assignee.name" 
          class="w-6 h-6 rounded-full border border-surface-white object-cover" 
          :src="task.assignee.avatar"
        />
      </div>
    </div>
  </article>
</template>

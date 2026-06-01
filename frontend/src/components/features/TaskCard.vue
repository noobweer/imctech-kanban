<script setup lang="ts">
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import { useAuthStore } from '@/stores/auth'
import { useBoardsStore } from '@/stores/boards'
import { useCommentsStore } from '@/stores/comments'
import type { Task } from '@/types/task'
import { CalendarDays, CheckSquare, MessageSquare, MoreVertical } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps<{
  task: Task
  allowPushToBoard?: boolean
}>()

const boardsStore = useBoardsStore()
const authStore = useAuthStore()
const commentsStore = useCommentsStore()
const isMentor = computed(() => authStore.user?.role === 'mentor')

const commentState = computed(() => commentsStore.boardStates[props.task.id])
const totalComments = computed(() => commentState.value?.comments_count || 0)
const unreadCount = computed(() =>
  commentState.value?.comments_state === 'unread' ? commentState.value.comments_count : 0,
)

const emit = defineEmits<{
  click: [task: Task]
  edit: [task: Task]
  archive: [task: Task]
  'push-to-board': [task: Task]
}>()

const isDone = computed(
  () => props.task.column_kind === 'archive' || props.task.column_name?.toLowerCase() === 'done',
)

const progressText = computed(
  () => `${props.task.checklist_done_count}/${props.task.checklist_total_count}`,
)

const progressClass = computed(() => {
  if (
    props.task.checklist_done_count === props.task.checklist_total_count &&
    props.task.checklist_total_count > 0
  ) {
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
  return `Due ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
})

const isDeadlineClose = computed(() => {
  if (!props.task.deadline || isDone.value) return false
  const deadlineTime = new Date(props.task.deadline).getTime()
  const now = new Date().getTime()
  const hoursLeft = (deadlineTime - now) / (1000 * 60 * 60)
  return hoursLeft <= 48
})

function getAssigneeName(username: string) {
  return boardsStore.members.find((m) => m.username === username)?.name || username
}
</script>

<template>
  <div
    class="bg-white p-4 md:p-5 rounded-xl border border-border-gray shadow-sm hover:shadow-lg hover:border-primary-container/50 transition-all duration-200 flex flex-col gap-3 cursor-pointer group"
    :class="{ 'opacity-75 grayscale-[0.2]': isDone }"
    @click="emit('click', task)"
  >
    <div class="flex justify-between items-start gap-2">
      <h3
        class="font-sub-heading text-[16px] font-bold text-on-surface leading-tight transition-all"
        :class="{ 'line-through text-text-secondary': isDone }"
      >
        {{ task.title }}
      </h3>
      <Dropdown position="bottom-right" @click.stop>
        <template #trigger>
          <button
            class="text-neutral-gray hover:text-on-surface transition-colors shrink-0 p-1 rounded hover:bg-black/5"
          >
            <MoreVertical :size="18" />
          </button>
        </template>
        <div class="py-1">
          <DropdownItem icon="pencil" @click="emit('edit', task)">
            {{ isMentor ? 'View Task' : 'Edit Task' }}
          </DropdownItem>
          <DropdownItem
            v-if="!isMentor"
            icon="archive"
            variant="danger"
            @click="emit('archive', task)"
          >
            Archive Task
          </DropdownItem>
          <div
            v-if="allowPushToBoard && !isMentor"
            class="my-1 border-t border-border-gray/50"
          ></div>
          <DropdownItem v-if="allowPushToBoard && !isMentor" @click="emit('push-to-board', task)">
            Move to Board
          </DropdownItem>
        </div>
      </Dropdown>
    </div>

    <p v-if="task.content" class="text-xs text-text-secondary line-clamp-2 min-h-[18px]">
      {{ task.content }}
    </p>

    <div
      v-if="task.deadline"
      class="flex items-center gap-1.5 text-neutral-gray/80"
      :class="{ 'text-error font-semibold': isDeadlineClose }"
    >
      <CalendarDays :size="14" />
      <span class="text-xs font-medium">{{ formattedDeadline }}</span>
    </div>

    <div class="flex items-end justify-between mt-auto pt-3">
      <div class="flex gap-2 flex-wrap items-center">
        <span
          v-if="task.checklist_total_count > 0"
          class="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
          :class="progressClass"
        >
          <CheckSquare :size="12" />
          {{ progressText }}
        </span>
        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold capitalize" :class="tagClass">
          {{ firstTag }}
        </span>

        <span
          v-if="totalComments > 0"
          class="relative flex items-center gap-1 ml-1 transition-colors duration-200"
          :class="unreadCount > 0 ? 'text-primary-container' : 'text-neutral-gray'"
        >
          <MessageSquare :size="14" />
          <span class="text-[11px] font-bold">{{ totalComments }}</span>

          <span
            v-if="unreadCount > 0"
            class="absolute -top-[2px] -right-2 w-[6px] h-[6px] bg-[var(--color-error)] rounded-full shadow-[0_0_0_2px_white] animate-pulse"
          ></span>
        </span>
      </div>

      <div v-if="task.assignees?.length" class="flex items-center -space-x-1">
        <img
          v-for="username in task.assignees"
          :key="username"
          :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(getAssigneeName(username))}&background=7132f5&color=fff&size=64`"
          class="t-avatar w-7 h-7 rounded-full border-2 border-white shadow-sm hover:z-10 hover:-translate-y-1 hover:scale-110"
          :title="getAssigneeName(username)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-sub-heading {
  font-family: 'Space Grotesk', sans-serif;
}
</style>

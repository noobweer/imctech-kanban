<script setup lang="ts">
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import { useAuthStore } from '@/stores/auth'
import { useBoardsStore } from '@/stores/boards'
import { useCommentsStore } from '@/stores/comments'
import type { Task } from '@/types/task'
import {
  CalendarDays,
  CheckSquare,
  MessageSquare,
  MoreVertical,
  ArchiveRestore,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { format } from 'date-fns'

const props = defineProps<{
  task: Task
  allowPushToBoard?: boolean
  isArchiveMode?: boolean
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
  restore: [task: Task]
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

const tags = computed(() => props.task.tags || [])
const firstTag = computed(() => tags.value[0])
const remainingTagsCount = computed(() => Math.max(0, tags.value.length - 1))

const tagClass = computed(() => {
  if (isDone.value) return 'bg-surface-container-low text-neutral-gray'
  if (firstTag.value && firstTag.value.toLowerCase() === 'bug')
    return 'bg-[var(--color-error)]/10 text-[var(--color-error)]'
  return 'bg-surface-container-high text-on-surface'
})

const formattedDateString = computed(() => {
  const parts = []
  // We check if added_to_board_at is defined and not null
  if ((props.task as any).added_to_board_at) {
    const addedDate = new Date((props.task as any).added_to_board_at)
    parts.push(`Add on board ${format(addedDate, 'MMM d')}`)
  }
  if (props.task.deadline) {
    const deadlineDate = new Date(props.task.deadline)
    parts.push(`Due ${format(deadlineDate, 'MMM d')}`)
  }
  return parts.join(' / ')
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

      <button
        v-if="isArchiveMode && !isMentor"
        class="text-[var(--color-primary-container)] bg-[var(--color-primary-container)]/10 hover:bg-[var(--color-primary-container)]/20 transition-all shrink-0 p-2 rounded-xl active:scale-95 shadow-sm"
        title="Restore Task"
        @click.stop="emit('restore', task)"
      >
        <ArchiveRestore :size="18" />
      </button>

      <Dropdown v-else-if="!isArchiveMode" position="bottom-right" @click.stop>
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
      v-if="formattedDateString"
      class="flex items-center gap-1.5 text-neutral-gray/80"
      :class="{ 'text-error font-semibold': isDeadlineClose }"
    >
      <CalendarDays :size="14" />
      <span class="text-xs font-medium">{{ formattedDateString }}</span>
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
        <template v-if="tags.length > 0">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" :class="tagClass">
            {{ firstTag }}
          </span>
          <span
            v-if="remainingTagsCount > 0"
            class="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-surface-container-high text-text-secondary"
          >
            +{{ remainingTagsCount }}
          </span>
        </template>

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

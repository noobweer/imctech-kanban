<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import { useAuthStore } from '@/stores/auth'
import { useBoardsStore } from '@/stores/boards'
import { useCommentsStore } from '@/stores/comments'
import type { Task } from '@/types/task'
import DOMPurify from 'dompurify'
import {
  AlignLeft,
  CalendarDays,
  Edit2,
  Flag,
  ListChecks,
  MessageSquare,
  Users,
} from 'lucide-vue-next'
import { marked } from 'marked'
import { computed, ref, watch } from 'vue'
import CommentsList from './CommentsList.vue'

const props = defineProps<{
  isOpen: boolean
  task?: Task | null
  boardId?: string
}>()

const emit = defineEmits<{
  close: []
  edit: [task: Task]
}>()

const boardsStore = useBoardsStore()
const authStore = useAuthStore()
const commentsStore = useCommentsStore()

const isMentor = computed(() => authStore.user?.role === 'mentor')
const canEdit = computed(() => !isMentor.value)

const activeTab = ref<'details' | 'checklist' | 'comments'>('details')

watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      if (props.boardId) {
        boardsStore.fetchMembers(props.boardId)
      }
      if (props.task) {
        commentsStore.fetchTaskComments(props.task.id)
      }
      activeTab.value = 'details'
    }
  },
)

const commentState = computed(() => {
  if (!props.task) return null
  return commentsStore.boardStates[props.task.id]
})

const unreadCount = computed(() => {
  if (commentState.value?.comments_state === 'unread') {
    return commentState.value.comments_count
  }
  return 0
})

const totalComments = computed(() => commentState.value?.comments_count || 0)

async function handleMarkAsRead() {
  if (!props.task) return
  await commentsStore.markAsRead(props.task.id)
}

const parsedContent = computed(() => {
  if (!props.task?.content) return ''
  // marked.parse returns string or Promise<string>, with sync options it's string.
  const rawHtml = marked.parse(props.task.content, { breaks: true }) as string
  return DOMPurify.sanitize(rawHtml)
})

const priorityLabel = computed(() => {
  if (props.task?.priority === 2) return { text: 'High', class: 'bg-white text-error shadow-sm' }
  if (props.task?.priority === 1)
    return { text: 'Medium', class: 'bg-white text-primary-container shadow-sm' }
  return { text: 'Low', class: 'bg-white text-text-secondary shadow-sm' }
})

const deadlineFormatted = computed(() => {
  if (!props.task?.deadline) return 'No deadline'
  return new Date(props.task.deadline).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
})

function getAssigneeName(username: string) {
  return boardsStore.members.find((m) => m.username === username)?.name || username
}
</script>

<template>
  <Modal :model-value="isOpen" max-width="1000px" @update:model-value="emit('close')">
    <div class="flex flex-col md:flex-row gap-6 md:gap-8 h-[80vh] min-h-[450px] max-h-[750px]">
      <!-- Left Main Content -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Title & Edit -->
        <div class="flex items-start justify-between gap-4 mb-6">
          <h1 class="font-section-heading text-2xl md:text-3xl font-bold text-on-surface">
            {{ task?.title }}
          </h1>
          <Button
            v-if="canEdit && task"
            variant="ghost"
            size="sm"
            @click="emit('edit', task)"
            class="text-text-secondary hover:text-primary-container shrink-0 mt-1"
          >
            <Edit2 :size="16" class="mr-1.5" /> Edit
          </Button>
        </div>

        <!-- Tabs -->
        <div class="flex items-end justify-between border-b border-border-gray mb-6 shrink-0 gap-4">
          <div class="flex gap-6">
            <button
              type="button"
              @click="activeTab = 'details'"
              :class="[
                'pb-3 font-semibold text-sm transition-all border-b-2 flex items-center gap-2 cursor-pointer',
                activeTab === 'details'
                  ? 'border-primary-container text-primary-container'
                  : 'border-transparent text-text-secondary hover:text-primary-container',
              ]"
            >
              <AlignLeft :size="16" />
              Details
            </button>

            <button
              type="button"
              @click="activeTab = 'checklist'"
              :class="[
                'pb-3 font-semibold text-sm transition-all border-b-2 flex items-center gap-2 cursor-pointer',
                activeTab === 'checklist'
                  ? 'border-primary-container text-primary-container'
                  : 'border-transparent text-text-secondary hover:text-primary-container',
              ]"
            >
              <ListChecks :size="16" />
              Checklist
              <span
                v-if="task?.checklist?.length"
                class="ml-1 px-2 py-0.5 rounded-full bg-surface-container-high text-[10px] text-text-primary"
              >
                {{ task.checklist.length }}
              </span>
            </button>

            <button
              type="button"
              @click="activeTab = 'comments'"
              :class="[
                'pb-3 font-semibold text-sm transition-all border-b-2 flex items-center gap-2 cursor-pointer relative',
                activeTab === 'comments'
                  ? 'border-primary-container text-primary-container'
                  : 'border-transparent text-text-secondary hover:text-primary-container',
              ]"
            >
              <MessageSquare :size="16" />
              Comments

              <template v-if="activeTab === 'comments' && unreadCount > 0">
                <div
                  @click.stop="handleMarkAsRead"
                  class="ml-1 bg-[var(--color-error)] text-white hover:opacity-90 px-2 py-0.5 rounded shadow-sm text-[10px] font-bold transition-all flex items-center gap-1 cursor-pointer"
                >
                  <svg
                    width="8"
                    height="8"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  Read All
                </div>
              </template>
              <template v-else>
                <span
                  v-if="totalComments > 0"
                  class="ml-1 px-2 py-0.5 rounded-full text-[10px]"
                  :class="
                    unreadCount > 0
                      ? 'bg-[var(--color-error)] text-white'
                      : 'bg-surface-container-high text-text-primary'
                  "
                >
                  {{ totalComments }}
                </span>
                <span
                  v-if="unreadCount > 0 && activeTab !== 'comments'"
                  class="absolute top-0 -right-2 w-[6px] h-[6px] rounded-full bg-[var(--color-error)] animate-pulse shadow-sm"
                ></span>
              </template>
            </button>
          </div>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <div
            v-show="activeTab === 'details'"
            class="flex-1 flex flex-col animate-in fade-in duration-300"
          >
            <div
              v-if="task?.content"
              class="text-[15px] text-on-surface/90 leading-[1.6] max-w-prose markdown-body"
              v-html="parsedContent"
            ></div>
            <div v-else class="text-neutral-gray italic text-[15px]">No description provided.</div>
          </div>

          <div
            v-show="activeTab === 'checklist'"
            class="flex-1 flex flex-col animate-in fade-in duration-300"
          >
            <div v-if="task?.checklist && task.checklist.length > 0" class="flex flex-col gap-3">
              <div
                v-for="item in task.checklist"
                :key="item.id"
                class="flex items-start gap-3 group"
              >
                <div class="relative w-5 h-5 flex items-center justify-center shrink-0 mt-0.5">
                  <input
                    :checked="item.is_done"
                    disabled
                    class="w-[18px] h-[18px] rounded border-border-gray text-primary disabled:opacity-60 transition-opacity"
                    type="checkbox"
                  />
                </div>
                <span
                  class="text-[15px] leading-snug pt-0.5 transition-colors"
                  :class="item.is_done ? 'text-neutral-gray/70 line-through' : 'text-on-surface/90'"
                >
                  {{ item.title }}
                </span>
              </div>
            </div>
            <div v-else class="text-neutral-gray italic text-[15px]">No checklist items.</div>
          </div>

          <div
            v-show="activeTab === 'comments'"
            class="flex-1 flex flex-col h-full animate-in fade-in duration-300 relative border border-border-gray/50 rounded-xl overflow-hidden bg-surface-container-lowest/50"
          >
            <CommentsList v-if="task" :task-id="task.id" :can-create="true" />
          </div>
        </div>
      </div>

      <!-- Right Sidebar (Matches TaskModal) -->
      <div
        class="w-full md:w-[280px] shrink-0 bg-surface-container-lowest rounded-2xl p-5 flex flex-col gap-6 border border-border-gray"
      >
        <!-- Priority -->
        <div>
          <label
            class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2"
          >
            <Flag :size="14" /> Priority
          </label>
          <div class="flex bg-surface-container-low rounded-xl p-1 gap-1">
            <div
              class="flex-1 py-1.5 rounded-lg text-xs font-semibold text-center"
              :class="task?.priority === 0 ? priorityLabel.class : 'text-text-secondary opacity-50'"
            >
              Low
            </div>
            <div
              class="flex-1 py-1.5 rounded-lg text-xs font-semibold text-center"
              :class="task?.priority === 1 ? priorityLabel.class : 'text-text-secondary opacity-50'"
            >
              Medium
            </div>
            <div
              class="flex-1 py-1.5 rounded-lg text-xs font-semibold text-center"
              :class="task?.priority === 2 ? priorityLabel.class : 'text-text-secondary opacity-50'"
            >
              High
            </div>
          </div>
        </div>

        <!-- Deadline -->
        <div>
          <label
            class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2"
          >
            <CalendarDays :size="14" /> Deadline
          </label>
          <div
            class="w-full bg-white border border-border-gray rounded-xl px-3 py-2.5 text-sm text-on-surface font-medium flex items-center h-[42px]"
          >
            {{ deadlineFormatted }}
          </div>
        </div>

        <!-- Assignees -->
        <div>
          <label
            class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2"
          >
            <Users :size="14" /> Assignees
          </label>
          <div class="flex flex-wrap gap-2 items-center">
            <template v-if="task?.assignees?.length">
              <img
                v-for="username in task.assignees"
                :key="username"
                :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(getAssigneeName(username))}&background=7132f5&color=fff`"
                class="w-8 h-8 rounded-full border-2 border-white shadow-sm"
                :title="getAssigneeName(username)"
              />
            </template>
            <span v-else class="text-text-secondary italic text-sm">Unassigned</span>
          </div>
        </div>
      </div>
    </div>
  </Modal>
</template>

<style scoped>
.font-section-heading {
  font-family: 'Space Grotesk', sans-serif;
}

/* Markdown Styling */
.markdown-body :deep(h1) {
  font-size: 1.5em;
  font-weight: 700;
  margin-top: 1em;
  margin-bottom: 0.5em;
}
.markdown-body :deep(h2) {
  font-size: 1.25em;
  font-weight: 700;
  margin-top: 1em;
  margin-bottom: 0.5em;
}
.markdown-body :deep(h3) {
  font-size: 1.1em;
  font-weight: 700;
  margin-top: 1em;
  margin-bottom: 0.5em;
}
.markdown-body :deep(p) {
  margin-bottom: 1em;
}
.markdown-body :deep(ul) {
  list-style-type: disc;
  padding-left: 1.5em;
  margin-bottom: 1em;
}
.markdown-body :deep(ol) {
  list-style-type: decimal;
  padding-left: 1.5em;
  margin-bottom: 1em;
}
.markdown-body :deep(li) {
  margin-bottom: 0.25em;
}
.markdown-body :deep(a) {
  color: var(--color-primary-container);
  text-decoration: underline;
}
.markdown-body :deep(blockquote) {
  border-left: 4px solid var(--color-border-gray);
  padding-left: 1em;
  color: var(--color-text-secondary);
  margin-bottom: 1em;
}
.markdown-body :deep(code) {
  background-color: var(--color-surface-container-high);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}
.markdown-body :deep(pre) {
  background-color: var(--color-surface-container-highest);
  padding: 1em;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 1em;
}
.markdown-body :deep(pre code) {
  background-color: transparent;
  padding: 0;
}
</style>

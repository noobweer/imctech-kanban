<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { MessageSquare, Activity } from 'lucide-vue-next'
import type { Board } from '@/types/board'
import type { Task } from '@/types/task'
import type { CommentFeedTaskOut } from '@/types/commentFeed'
import TaskCard from '@/components/features/TaskCard.vue'
import TaskViewModal from '@/components/features/TaskViewModal.vue'
import { boardsApi } from '@/api/boards'
import { useCommentsStore } from '@/stores/comments'
import { useToast } from '@/composables/useToast'
import { useRoute } from 'vue-router'

const props = defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const activeTab = ref<'new' | 'activity'>('new')
const loading = ref(false)

const newTasks = ref<CommentFeedTaskOut[]>([])
const activityTasks = ref<CommentFeedTaskOut[]>([])
const newCount = ref(0)
const activityCount = ref(0)

const toast = useToast()
const commentsStore = useCommentsStore()

const isViewModalOpen = ref(false)
const viewingTask = ref<Task | null>(null)

async function loadFeedData() {
  if (!props.board) return
  loading.value = true
  try {
    const [newRes, activityRes] = await Promise.all([
      boardsApi.getCommentsFeed(props.board.id, 'new'),
      boardsApi.getCommentsFeed(props.board.id, 'activity'),
    ])

    newTasks.value = newRes.tasks || []
    activityTasks.value = activityRes.tasks || []
    newCount.value = newRes.total || 0
    activityCount.value = activityRes.total || 0

    // Populate commentsStore with states to ensure TaskCard shows the badge correctly
    const allTasks = [...newTasks.value, ...activityTasks.value]
    allTasks.forEach((t) => {
      commentsStore.boardStates[t.id] = {
        task_id: t.id,
        comments_state: t.comments_state,
        comments_count: t.comments_count,
        has_comments: t.comments_count > 0,
        has_unread_comments: t.comments_state === 'unread',
      }
    })
  } catch (error: any) {
    toast.error(error.message || 'Failed to load comments feed')
  } finally {
    loading.value = false
  }
}

watch(
  () => props.board,
  (newBoard) => {
    if (newBoard) {
      loadFeedData()
    }
  },
  { immediate: true },
)

const currentTasks = computed(() => {
  return activeTab.value === 'new' ? newTasks.value : activityTasks.value
})

function handleViewTask(feedTask: CommentFeedTaskOut) {
  // Cast to Task since TaskCard/TaskViewModal expects it
  // Missing fields like 'content' are fine since they are optional/handled gracefully
  const partialTask = {
    ...feedTask,
    checklist_total_count: 0,
    checklist_done_count: 0,
  } as unknown as Task

  viewingTask.value = partialTask
  isViewModalOpen.value = true
}

</script>

<template>
  <main class="h-full overflow-y-auto p-4 md:p-6 bg-background custom-scrollbar">
    <div class="max-w-7xl mx-auto flex flex-col min-h-full relative">
      <div
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 shrink-0"
      >
        <div class="flex items-center gap-4">
          <h2
            class="font-section-heading text-[36px] font-bold text-on-surface whitespace-nowrap leading-tight tracking-tight"
          >
            Comments
          </h2>
          <span
            class="px-3 py-1 bg-surface-container-high rounded-full text-xs font-bold text-neutral-gray mt-1"
          >
            {{ currentTasks.length }} Tasks
          </span>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="inline-flex p-1 bg-surface-container-high rounded-xl mb-8 shrink-0 w-fit">
        <button
          @click="activeTab = 'new'"
          :class="[
            'flex items-center gap-2 px-5 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
            activeTab === 'new'
              ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
              : 'text-neutral-gray hover:text-primary-container cursor-pointer',
          ]"
        >
          <MessageSquare :size="16" />
          New
          <span
            v-if="newCount > 0"
            class="ml-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold"
            :class="activeTab === 'new' ? 'bg-primary-container/10 text-primary-container' : 'bg-black/5 text-neutral-gray'"
          >
            {{ newCount }}
          </span>
        </button>
        <button
          @click="activeTab = 'activity'"
          :class="[
            'flex items-center gap-2 px-5 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
            activeTab === 'activity'
              ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
              : 'text-neutral-gray hover:text-primary-container cursor-pointer',
          ]"
        >
          <Activity :size="16" />
          Active
          <span
            v-if="activityCount > 0"
            class="ml-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold"
            :class="activeTab === 'activity' ? 'bg-primary-container/10 text-primary-container' : 'bg-black/5 text-neutral-gray'"
          >
            {{ activityCount }}
          </span>
        </button>
      </div>

      <!-- Content Area -->
      <div class="relative flex-1">
        <Transition name="t-page" mode="out-in">
          <div :key="activeTab">
            <!-- Loading Skeletons -->
            <div
              v-if="loadingBoard || loading"
              class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6"
            >
              <div
                v-for="i in 4"
                :key="i"
                class="h-48 border border-border-gray rounded-xl animate-pulse bg-surface-container-low/50"
              ></div>
            </div>

            <!-- Task Grid with Staggered Reveal -->
            <TransitionGroup
              v-else-if="currentTasks.length > 0"
              name="t-task"
              tag="div"
              class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 pb-6 items-stretch"
            >
              <div
                v-for="task in currentTasks"
                :key="task.id"
                class="h-full"
              >
                <TaskCard
                  :task="(task as unknown as Task)"
                  class="h-full hover:border-primary-container transition-all duration-300"
                  @click="handleViewTask(task)"
                  @edit="handleViewTask(task)"
                />
              </div>
            </TransitionGroup>

            <!-- Empty State -->
            <div v-else class="h-64 flex flex-col items-center justify-center text-center">
              <div
                class="w-16 h-16 bg-surface-container rounded-full flex items-center justify-center mb-4"
              >
                <MessageSquare :size="32" class="text-neutral-gray opacity-50" />
              </div>
              <p class="text-text-secondary text-lg">
                {{ activeTab === 'new' ? 'No new comments to read.' : 'No recent comment activity.' }}
              </p>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Task View Modal -->
    <TaskViewModal
      v-if="board"
      :isOpen="isViewModalOpen"
      :task="viewingTask"
      :boardId="board.id"
      @close="isViewModalOpen = false"
    />
  </main>
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

/* Reuse t-task transitions from ArchiveView */
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

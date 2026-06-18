<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, PieChart, MessageSquare } from 'lucide-vue-next'
import { boardsApi } from '@/api/boards'
import type { Board } from '@/types/board'
import UserProfileDropdown from '@/components/features/UserProfileDropdown.vue'
import BoardMembersModal from '@/components/features/BoardMembersModal.vue'
import BoardSettingsModal from '@/components/features/BoardSettingsModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useBoardWebSocket } from '@/composables/useBoardWebSocket'

const authStore = useAuthStore()
const ws = useBoardWebSocket()
const isMentor = computed(() => authStore.user?.role === 'mentor')

const route = useRoute()
const router = useRouter()

const boardId = ref(route.params.id as string)
const board = ref<Board | null>(null)
const loading = ref(true)
const showMembersModal = ref(false)
const showSettingsModal = ref(false)

async function loadBoardData() {
  loading.value = true
  try {
    board.value = await boardsApi.getBoard(boardId.value)
  } catch (error) {
    console.error('Failed to load board details:', error)
    router.push('/boards')
  } finally {
    loading.value = false
  }
}

import { onUnmounted } from 'vue'
import { useCommentsStore } from '@/stores/comments'
import { useMentorRequestsStore } from '@/stores/mentorRequests'

const commentsStore = useCommentsStore()
const mentorRequestsStore = useMentorRequestsStore()

onUnmounted(() => {
  ws.disconnect()
})

const unreadCommentsCount = computed(() => {
  return Object.values(commentsStore.boardStates).filter((s) => s.has_unread_comments).length
})

const mentorRequestsCount = computed(() => {
  if (!isMentor.value) return 0
  return mentorRequestsStore.boardRequests.filter((r) => r.status === 'open').length
})

const totalNotifications = computed(() => unreadCommentsCount.value + mentorRequestsCount.value)

async function loadInitialData(id: string) {
  try {
    await Promise.all([
      mentorRequestsStore.fetchBoardRequests(id),
      commentsStore.fetchBoardStates(id),
    ])
  } catch (e) {
    console.error('Failed to load board specific states:', e)
  }
}

onMounted(() => {
  loadBoardData()
  if (boardId.value) {
    loadInitialData(boardId.value)
  }
})

watch(
  () => route.params.id,
  (newId) => {
    if (newId && newId !== boardId.value) {
      boardId.value = newId as string
      loadBoardData()
      loadInitialData(boardId.value)
    }
  },
)

watch(
  () => board.value,
  (newBoard) => {
    if (newBoard) {
      ws.connect(newBoard.id)
    } else {
      ws.disconnect()
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="h-screen flex flex-col bg-white overflow-hidden">
    <!-- Main Header -->
    <header class="bg-white border-b border-border-gray sticky top-0 z-50">
      <div class="flex justify-between items-center w-full px-4 md:px-6 py-3 max-w-full">
        <!-- Left Section: Back + Title -->
        <div class="flex items-center gap-4 flex-1">
          <button
            aria-label="Go back"
            class="p-2 hover:bg-surface-container-low rounded-full transition-colors cursor-pointer text-neutral-gray hover:text-primary-container"
            @click="router.push('/boards')"
          >
            <ChevronLeft :size="20" />
          </button>
          <div v-if="board" class="min-w-0">
            <h1 class="text-xl font-bold leading-tight text-text-primary truncate">
              {{ board.name }}
            </h1>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-[10px] font-bold px-1.5 py-0.5 bg-surface-container-high rounded text-text-secondary leading-none uppercase shrink-0" :title="board.project_name">{{ board.project_name }}</span>
              <span v-if="board.description" class="text-xs text-text-secondary truncate max-w-[150px] md:max-w-sm" :title="board.description">{{ board.description }}</span>
            </div>
          </div>
          <div v-else-if="loading" class="animate-pulse flex flex-col gap-2">
            <div class="h-6 w-48 bg-surface-container-high rounded"></div>
            <div class="h-3 w-32 bg-surface-container rounded"></div>
          </div>
        </div>

        <!-- Right Section: Actions + Profile -->
        <div class="flex items-center justify-end gap-2 md:gap-3 flex-1">
          <button
            v-if="authStore.user?.role !== 'student'"
            class="hidden md:block px-4 py-1.5 border border-border-gray rounded-xl font-semibold hover:bg-surface-container-low transition-all text-neutral-gray hover:text-primary-container text-sm cursor-pointer"
            @click="showSettingsModal = true"
          >
            Settings
          </button>
          <button
            class="px-3 md:px-4 py-1.5 border border-border-gray rounded-xl font-semibold hover:bg-surface-container-low transition-all text-neutral-gray hover:text-primary-container text-sm cursor-pointer"
            @click="showMembersModal = true"
          >
            Members
          </button>
          <div class="ml-2">
            <UserProfileDropdown />
          </div>
        </div>
      </div>
    </header>

    <!-- Secondary Navigation -->
    <nav
      class="px-4 md:px-6 border-b border-border-gray flex items-center justify-between shrink-0 overflow-x-auto custom-scrollbar-x gap-4"
    >
      <div class="flex gap-4 md:gap-8 min-w-max">
        <router-link
          :to="`/boards/${boardId}`"
          class="py-4 font-medium text-sm transition-colors border-b-2"
          :class="[
            route.name === 'board-detail'
              ? 'border-primary-container text-primary-container'
              : 'border-transparent text-text-secondary hover:text-primary-container',
          ]"
        >
          Board
        </router-link>
        <router-link
          :to="`/boards/${boardId}/backlog`"
          class="py-4 font-medium text-sm transition-colors border-b-2"
          :class="[
            route.name === 'board-backlog'
              ? 'border-primary-container text-primary-container'
              : 'border-transparent text-text-secondary hover:text-primary-container',
          ]"
        >
          Backlog
        </router-link>
        <router-link
          :to="`/boards/${boardId}/archive`"
          class="py-4 font-medium text-sm transition-colors border-b-2"
          :class="[
            route.name === 'board-archive'
              ? 'border-primary-container text-primary-container'
              : 'border-transparent text-text-secondary hover:text-primary-container',
          ]"
        >
          Archive
        </router-link>
      </div>
      <div class="flex gap-4 md:gap-8 min-w-max">
        <router-link
          v-if="isMentor"
          :to="`/boards/${boardId}/overview`"
          class="py-4 font-medium text-sm transition-colors border-b-2"
          :class="[
            route.name === 'board-overview'
              ? 'border-primary-container text-primary-container'
              : 'border-transparent text-text-secondary hover:text-primary-container',
          ]"
        >
          <span class="flex items-center gap-2"><PieChart :size="16" /> Overview</span>
        </router-link>
        <router-link
          :to="`/boards/${boardId}/comments`"
          class="py-4 font-medium text-sm transition-colors border-b-2"
          :class="[
            route.name === 'board-comments'
              ? 'border-primary-container text-primary-container'
              : 'border-transparent text-text-secondary hover:text-primary-container',
          ]"
        >
          <span class="flex items-center gap-2">
            <MessageSquare :size="16" />
            Comments
            <span
              v-if="totalNotifications > 0"
              class="bg-[var(--color-error)] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full leading-none min-w-[18px] text-center"
            >
              {{ totalNotifications > 99 ? '99+' : totalNotifications }}
            </span>
          </span>
        </router-link>
      </div>
    </nav>

    <!-- Content Area -->
    <div class="flex-1 overflow-hidden">
      <router-view v-if="board || loading" :board="board" :loading-board="loading" />
    </div>

    <!-- Modals -->
    <BoardMembersModal v-if="board" v-model="showMembersModal" :board="board" />
    <BoardSettingsModal v-if="board" v-model="showSettingsModal" :board="board" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, PieChart, MessageSquare } from 'lucide-vue-next'
import { boardsApi } from '@/api/boards'
import type { Board } from '@/types/board'
import UserProfileDropdown from '@/components/features/UserProfileDropdown.vue'

const route = useRoute()
const router = useRouter()

const boardId = ref(route.params.id as string)
const board = ref<Board | null>(null)
const loading = ref(true)

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

// Watch for ID changes in case we navigate between boards
watch(() => route.params.id, (newId) => {
  if (newId && newId !== boardId.value) {
    boardId.value = newId as string
    loadBoardData()
  }
})

onMounted(loadBoardData)
</script>

<template>
  <div class="h-full flex flex-col bg-white overflow-hidden">
    <!-- Main Header -->
    <header class="bg-white border-b border-border-gray sticky top-0 z-50">
      <div class="flex justify-between items-center w-full px-6 py-3 max-w-full">
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
            <h1 class="text-xl font-bold leading-tight text-text-primary truncate">{{ board.name }}</h1>
            <p class="text-xs text-text-secondary truncate">{{ board.project_name }}</p>
          </div>
          <div v-else-if="loading" class="animate-pulse flex flex-col gap-2">
            <div class="h-6 w-48 bg-surface-container-high rounded"></div>
            <div class="h-3 w-32 bg-surface-container rounded"></div>
          </div>
        </div>

        <!-- Right Section: Actions + Profile -->
        <div class="flex items-center justify-end gap-3 flex-1">
          <button class="px-4 py-1.5 border border-border-gray rounded-xl font-semibold hover:bg-surface-container-low transition-all text-neutral-gray hover:text-primary-container text-sm cursor-pointer">
            Settings
          </button>
          <button class="px-4 py-1.5 border border-border-gray rounded-xl font-semibold hover:bg-surface-container-low transition-all text-neutral-gray hover:text-primary-container text-sm cursor-pointer">
            Members
          </button>
          <div class="ml-2">
            <UserProfileDropdown />
          </div>
        </div>
      </div>
    </header>

    <!-- Secondary Navigation -->
    <nav class="px-6 border-b border-border-gray flex items-center justify-between shrink-0">
      <div class="flex gap-8">
        <router-link 
          :to="`/boards/${boardId}`"
          class="py-4 font-medium text-sm transition-colors border-b-2"
          :class="[
            route.name === 'board-detail' 
              ? 'border-primary-container text-primary-container' 
              : 'border-transparent text-text-secondary hover:text-primary-container'
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
              : 'border-transparent text-text-secondary hover:text-primary-container'
          ]"
        >
          Backlog
        </router-link>
        <a class="py-4 font-medium text-text-secondary hover:text-primary-container text-sm transition-colors border-b-2 border-transparent" href="#">Archive</a>
      </div>
      <div class="flex gap-8">
        <a class="py-4 font-medium text-text-secondary hover:text-primary-container text-sm transition-colors" href="#">
          <span class="flex items-center gap-2"><PieChart :size="16" /> Overview</span>
        </a>
        <a class="py-4 font-medium text-text-secondary hover:text-primary-container text-sm transition-colors" href="#">
          <span class="flex items-center gap-2"><MessageSquare :size="16" /> Comments</span>
        </a>
      </div>
    </nav>

    <!-- Content Area -->
    <div class="flex-1 overflow-hidden">
      <router-view v-if="board || loading" :board="board" :loading-board="loading" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, LayoutDashboard, CheckSquare, Menu, Settings } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useBoardsStore } from '@/stores/boards'
import BoardCard from '@/components/features/BoardCard.vue'
import UserProfileDropdown from '@/components/features/UserProfileDropdown.vue'

const router = useRouter()
const authStore = useAuthStore()
const boardsStore = useBoardsStore()

const isMentor = computed(() => authStore.user?.role === 'mentor')
const hasBoards = computed(() => boardsStore.filteredBoards.length > 0)

function handleCreateBoard() {
  router.push('/boards/create')
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="bg-white border-b border-border-gray sticky top-0 z-50">
      <!-- Mobile Layout -->
      <div class="md:hidden flex flex-col px-4 pt-4 pb-4 gap-4">
        <!-- Row 1: Menu + Title + Create -->
        <div class="flex justify-between items-center gap-4">
          <div class="relative w-full">
            <Search
              :size="20"
              class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-gray"
            />
            <input
              v-model="boardsStore.searchQuery"
              class="w-full pl-10 pr-4 py-3 bg-white border border-border-gray rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-container focus:border-transparent transition-all"
              placeholder="Search boards..."
              type="text"
            />
          </div>

          <button
            v-if="isMentor"
            class="bg-primary-container text-white px-4 py-3 rounded-xl text-sm font-semibold hover:opacity-90 active:scale-95 transition-all flex items-center gap-1"
            @click="handleCreateBoard"
          >
            <Plus :size="18" />
            Create
          </button>
          <div v-else class="w-[88px]"></div>
        </div>

        <!-- Row 3: Toggle -->
        <div class="bg-surface-container-low p-1 rounded-xl flex w-full">
          <button
            :class="[
              'flex-1 py-2 text-sm font-semibold rounded-lg transition-all',
              boardsStore.activeTab === 'active'
                ? 'bg-white text-primary-container shadow-sm'
                : 'text-neutral-gray',
            ]"
            @click="boardsStore.activeTab = 'active'"
          >
            Active
          </button>
          <button
            :class="[
              'flex-1 py-2 text-sm font-semibold rounded-lg transition-all',
              boardsStore.activeTab === 'archived'
                ? 'bg-white text-primary-container shadow-sm'
                : 'text-neutral-gray',
            ]"
            @click="boardsStore.activeTab = 'archived'"
          >
            Archived
          </button>
        </div>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden md:flex justify-between items-center w-full px-6 py-3 max-w-full">
        <!-- Left: Toggle + Create Button -->
        <div class="flex items-center gap-4 flex-1">
          <div class="inline-flex p-1 bg-surface-container-high rounded-xl">
            <button
              :class="[
                'px-4 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
                boardsStore.activeTab === 'active'
                  ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
                  : 'text-neutral-gray hover:text-primary-container cursor-pointer',
              ]"
              @click="boardsStore.activeTab = 'active'"
            >
              Active
            </button>
            <button
              :class="[
                'px-4 py-1.5 text-sm font-semibold rounded-lg transition-colors',
                boardsStore.activeTab === 'archived'
                  ? 'bg-white text-primary-container shadow-sm'
                  : 'text-neutral-gray hover:text-primary-container cursor-pointer',
              ]"
              @click="boardsStore.activeTab = 'archived'"
            >
              Archived
            </button>
          </div>
          <button
            v-if="isMentor"
            class="bg-primary-container cursor-pointer text-white px-5 py-2 rounded-xl text-sm font-semibold shadow-sm hover:opacity-90 active:scale-[0.98] transition-all flex items-center gap-2"
            @click="handleCreateBoard"
          >
            <Plus :size="18" />
            Create Board
          </button>
        </div>

        <!-- Center: Search Bar -->
        <div class="flex-[1.5] max-w-xl hidden md:block">
          <div class="relative group">
            <Search
              :size="20"
              class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-gray group-focus-within:text-primary-container transition-colors"
            />
            <input
              v-model="boardsStore.searchQuery"
              class="w-full bg-surface-container-low border border-border-gray rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
              placeholder="Search boards..."
              type="text"
            />
          </div>
        </div>

        <!-- Right: Nav + Avatar -->
        <div class="flex items-center justify-end gap-6 flex-1">
          <UserProfileDropdown />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="px-6 py-10 pb-24 md:pb-10 max-w-7xl mx-auto">
      <!-- Board Grid -->
      <div v-if="hasBoards">
        <div class="mb-10">
          <h1 class="font-['Space_Grotesk'] text-[36px] font-bold leading-[1.22] tracking-[-0.5px] text-text-primary mb-2">
            Your Boards
          </h1>
          <p class="font-['Inter'] text-[16px] leading-[1.38] text-neutral-gray max-w-2xl">
            Access and manage your active project boards and team collaborations.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <BoardCard
            v-for="board in boardsStore.filteredBoards"
            :key="board.id"
            :board="board"
            :show-menu="isMentor"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="min-h-[calc(100vh-10rem)] flex flex-col items-center justify-center">
        <div class="max-w-md w-full text-center space-y-8">
          <!-- Decorative Illustration -->
          <div class="relative w-64 h-64 mx-auto mb-10">
            <div
              class="absolute inset-0 bg-gradient-to-tr from-purple-subtle to-transparent rounded-full blur-3xl opacity-60"
            ></div>
            <div class="relative z-10 w-full h-full flex items-center justify-center">
              <div class="relative">
                <!-- Background Card -->
                <div
                  class="w-32 h-40 bg-white border border-border-gray rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.03)] flex items-center justify-center transform rotate-[-6deg] absolute -left-8 top-0"
                >
                  <LayoutDashboard :size="48" class="text-primary-container opacity-20" />
                </div>
                <!-- Main Card -->
                <div
                  class="w-32 h-40 bg-white border border-border-gray rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] flex items-center justify-center transform rotate-[4deg] relative z-20"
                >
                  <LayoutDashboard :size="64" class="text-primary-container" />
                </div>
                <!-- Floating Element -->
                <div
                  class="absolute -right-12 top-10 w-16 h-16 bg-white border border-border-gray rounded-xl shadow-[0_4px_24px_rgba(0,0,0,0.03)] flex items-center justify-center z-30 transform -rotate-12"
                >
                  <CheckSquare :size="24" class="text-success-green" />
                </div>
              </div>
            </div>
          </div>

          <!-- Content -->
          <div class="space-y-3">
            <h1 class="font-['Space_Grotesk'] text-[36px] font-bold leading-[1.22] tracking-[-0.5px] text-text-primary">
              No boards found
            </h1>
            <p class="font-['Inter'] text-[16px] leading-[1.38] text-neutral-gray max-w-sm mx-auto">
              Organize your projects. Start by creating
              your very first workspace.
            </p>
          </div>

          <!-- CTA -->
          <div v-if="isMentor" class="pt-4">
            <button
              class="bg-primary-container hover:opacity-90 text-white px-8 py-4 rounded-xl flex items-center gap-3 font-['Inter'] text-lg font-semibold mx-auto transition-all shadow-lg shadow-purple-500/20 active:scale-95"
              @click="handleCreateBoard"
            >
              <Plus :size="24" />
              Create your first board
            </button>
          </div>
        </div>

        <!-- Decorative Blobs (desktop only) -->
        <div class="hidden md:block fixed bottom-0 left-0 right-0 pointer-events-none overflow-hidden h-32">
          <div
            class="absolute bottom-[-100px] left-[-50px] w-[500px] h-[500px] bg-purple-subtle rounded-full blur-[100px] opacity-30"
          ></div>
          <div
            class="absolute bottom-[-100px] right-[-50px] w-[300px] h-[300px] bg-purple-subtle rounded-full blur-[80px] opacity-20"
          ></div>
        </div>
      </div>
    </main>

    <!-- Bottom Navigation (Mobile) -->
    <nav
      class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-border-gray px-6 pb-6 pt-3 flex justify-around items-center shadow-[0_-1px_4px_rgba(16,24,40,0.04)] z-50"
    >
      <button class="flex flex-col items-center gap-1">
        <LayoutDashboard :size="24" class="text-primary-container" />
        <span class="text-xs font-semibold text-primary-container">Boards</span>
      </button>
      <button class="flex flex-col items-center gap-1">
        <Settings :size="24" class="text-neutral-gray" />
        <span class="text-xs font-medium text-neutral-gray">Settings</span>
      </button>
    </nav>
  </div>
</template>

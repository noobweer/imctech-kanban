<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, MoreVertical } from 'lucide-vue-next'
import type { Board } from '@/types/board'

const props = defineProps<{
  board: Board
  showMenu: boolean
}>()

const visibleMembers = computed(() => props.board.members.slice(0, 2))
const remainingCount = computed(() => Math.max(0, props.board.members.length - 2))

const formattedDate = computed(() => {
  const date = new Date(props.board.dueDate)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
})
</script>

<template>
  <div
    class="bg-white rounded-xl cursor-pointer p-[16px] shadow-[0_4px_24px_rgba(0,0,0,0.03)] border border-border-gray flex flex-col hover:shadow-indigo-500/15 transition-shadow relative"
  >
    <button
      v-if="showMenu"
      class="absolute top-4 right-4 text-neutral-gray hover:text-text-primary transition-colors"
    >
      <MoreVertical :size="20" />
    </button>

    <div class="mb-4">
      <h3 class="text-xl font-semibold text-text-primary">{{ board.title }}</h3>
      <p class="text-sm text-text-secondary">{{ board.category }}</p>
    </div>

    <div class="flex items-center gap-2 text-sm text-neutral-gray mb-4">
      <Calendar :size="16" />
      <span>Due {{ formattedDate }}</span>
    </div>

    <div class="mt-auto">
      <div class="flex justify-between items-center mb-4">
        <div class="flex -space-x-2">
          <img
            v-for="member in visibleMembers"
            :key="member.username"
            :src="member.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(member.name)}&background=7132f5&color=fff`"
            :alt="member.name"
            class="w-8 h-8 rounded-full border-2 border-white object-cover"
          />
          <div
            v-if="remainingCount > 0"
            class="w-8 h-8 rounded-full bg-surface-container-high border-2 border-white flex items-center justify-center text-[10px] text-text-primary font-bold"
          >
            +{{ remainingCount }}
          </div>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between text-xs font-semibold">
          <span class="text-neutral-gray">Progress</span>
          <span class="text-primary-container">{{ board.progress }}%</span>
        </div>
        <div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
          <div
            class="bg-primary-container h-full rounded-full transition-all"
            :style="{ width: `${board.progress}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

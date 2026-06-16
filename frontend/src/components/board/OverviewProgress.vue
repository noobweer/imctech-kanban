<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useOverviewStore } from '@/stores/overview'
import type { Board } from '@/types/board'

const props = defineProps<{
  board: Board
}>()

const overviewStore = useOverviewStore()
const data = computed(() => overviewStore.progressData)
const loading = computed(() => overviewStore.isLoadingProgress)

const animateIn = ref(false)

onMounted(() => {
  setTimeout(() => {
    animateIn.value = true
  }, 100)
})

// predefined kraken-friendly palette for segments
const COLORS = [
  '#7132f5', // Kraken Purple
  '#149e61', // Success Green
  '#f59e0b', // Amber
  '#3b82f6', // Blue
  '#ec4899', // Pink
  '#6366f1', // Indigo
  '#10b981', // Emerald
]

const segments = computed(() => {
  if (!data.value || data.value.total_tasks === 0) return []
  return data.value.columns.map((col, idx) => ({
    ...col,
    color: COLORS[idx % COLORS.length],
  }))
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div
      v-if="loading && !data"
      class="h-[16px] bg-[rgba(148,151,169,0.12)] rounded-[12px] w-full animate-pulse"
    ></div>

    <template v-else-if="segments.length > 0">
      <!-- Progress Bar -->
      <div
        class="relative h-[16px] bg-[rgba(148,151,169,0.12)] rounded-[12px] w-full flex overflow-hidden group"
      >
        <div
          v-for="segment in segments"
          :key="segment.id"
          class="h-full transition-all duration-1000 ease-out flex items-center justify-center group/segment hover:brightness-110 relative"
          :style="{
            width: animateIn ? `${segment.percent}%` : '0%',
            backgroundColor: segment.color,
          }"
          :title="`${segment.name}: ${segment.task_count} (${segment.percent}%)`"
        ></div>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap gap-x-6 gap-y-3">
        <div v-for="segment in segments" :key="segment.id" class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-[3px]" :style="{ backgroundColor: segment.color }"></div>
          <span class="text-sm font-medium text-near-black">{{ segment.percent }}%</span>
          <span class="text-sm text-cool-gray">{{ segment.name }}</span>
        </div>
      </div>
    </template>

    <div v-else class="text-cool-gray text-sm py-4">No tasks on the board yet.</div>
  </div>
</template>

<style scoped>
.text-near-black {
  color: #101114;
}
.text-cool-gray {
  color: #686b82;
}
</style>

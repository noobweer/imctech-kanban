<script setup lang="ts">
import { useOverviewStore } from '@/stores/overview'
import type { Board } from '@/types/board'
import { computed, watch } from 'vue'
import OverviewActivity from './OverviewActivity.vue'
import OverviewDeadlines from './OverviewDeadlines.vue'
import OverviewProgress from './OverviewProgress.vue'
import Select from '@/components/ui/Select.vue'

const props = defineProps<{
  board: Board | null
  loadingBoard?: boolean
}>()

const overviewStore = useOverviewStore()

const activeMode = computed({
  get: () => overviewStore.activeMode,
  set: (val) => {
    overviewStore.activeMode = val
  },
})

const activityPeriod = computed({
  get: () => overviewStore.activityPeriod,
  set: (val) => {
    overviewStore.activityPeriod = val
  },
})

async function fetchData() {
  if (!props.board) return
  await overviewStore.fetchProgress(props.board.id)

  if (activeMode.value === 'activity') {
    await overviewStore.fetchActivity(props.board.id)
  } else {
    await overviewStore.fetchDeadlines(props.board.id)
  }
}

watch(
  () => props.board,
  (newBoard) => {
    if (newBoard) {
      fetchData()
    }
  },
  { immediate: true },
)

watch([activeMode, activityPeriod], () => {
  if (!props.board) return
  if (activeMode.value === 'activity') {
    overviewStore.fetchActivity(props.board.id)
  } else {
    overviewStore.fetchDeadlines(props.board.id)
  }
})
</script>

<template>
  <div class="h-full flex flex-col bg-background overflow-y-auto">
    <div class="max-w-[1200px] w-full mx-auto p-4 md:p-8 flex flex-col gap-8">
      <!-- Top Section: Progress Bar Chart -->
      <section
        class="bg-white rounded-[16px] p-6 shadow-[0_4px_24px_rgba(0,0,0,0.03)] min-h-[108px]"
      >
        <div v-if="loadingBoard" class="text-sm font-medium text-cool-gray flex items-center gap-2">
          Loading progress data...
        </div>
        <OverviewProgress v-else-if="board" :board="board" />
      </section>

      <!-- Middle Section: Controls -->
      <section class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <!-- Segmented Control for Mode -->
        <div class="inline-flex p-1 bg-surface-container-high rounded-xl shrink-0 w-full md:w-auto">
          <button
            :class="[
              'flex-1 md:flex-none px-6 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
              activeMode === 'activity'
                ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
                : 'text-neutral-gray hover:text-primary-container cursor-pointer',
            ]"
            @click="activeMode = 'activity'"
          >
            Activity
          </button>
          <button
            :class="[
              'flex-1 md:flex-none px-6 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150',
              activeMode === 'deadlines'
                ? 'bg-white text-primary-container shadow-sm active:scale-[0.98]'
                : 'text-neutral-gray hover:text-primary-container cursor-pointer',
            ]"
            @click="activeMode = 'deadlines'"
          >
            Deadlines
          </button>
        </div>

        <!-- Activity Filter Select -->
        <Transition name="fade-slide">
          <div v-if="activeMode === 'activity'" class="w-full md:w-48 shrink-0">
            <Select
              v-model="activityPeriod"
              :options="[
                { label: 'Weekly Activity', value: 'weekly' },
                { label: 'All Time Activity', value: 'all_time' },
              ]"
            />
          </div>
        </Transition>
      </section>

      <!-- Bottom Section: Dynamic Content -->
      <section class="flex-1 relative">
        <Transition name="fade-mode" mode="out-in">
          <div v-if="loadingBoard" class="h-64 flex items-center justify-center">
            <span class="text-sm font-medium text-cool-gray"
              >Loading activity and deadlines...</span
            >
          </div>
          <OverviewActivity v-else-if="activeMode === 'activity' && board" :board="board" />
          <OverviewDeadlines v-else-if="activeMode === 'deadlines' && board" :board="board" />
        </Transition>
      </section>
    </div>
  </div>
</template>

<style scoped>
.font-product {
  font-family: 'Kraken-Product', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.text-near-black {
  color: #101114;
}
.text-cool-gray {
  color: #686b82;
}
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

.fade-mode-enter-active,
.fade-mode-leave-active {
  transition: all 0.3s ease;
}
.fade-mode-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-mode-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

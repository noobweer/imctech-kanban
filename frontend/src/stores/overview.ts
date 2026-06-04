import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getBoardProgress,
  getBoardActivity,
  getBoardDeadlines,
  type ProgressOut,
  type ActivityOut,
  type DeadlinesOut,
} from '@/api/overview'

export const useOverviewStore = defineStore('overview', () => {
  const activeMode = ref<'activity' | 'deadlines'>('activity')
  const activityPeriod = ref<'weekly' | 'all_time'>('weekly')

  const progressData = ref<ProgressOut | null>(null)
  const activityData = ref<ActivityOut | null>(null)
  const deadlinesData = ref<DeadlinesOut | null>(null)

  const isLoadingProgress = ref(false)
  const isLoadingActivity = ref(false)
  const isLoadingDeadlines = ref(false)

  async function fetchProgress(boardId: string) {
    try {
      isLoadingProgress.value = true
      progressData.value = await getBoardProgress(boardId)
    } catch (e) {
      console.error('Failed to fetch progress:', e)
    } finally {
      isLoadingProgress.value = false
    }
  }

  async function fetchActivity(boardId: string) {
    try {
      isLoadingActivity.value = true
      activityData.value = await getBoardActivity(boardId, activityPeriod.value)
    } catch (e) {
      console.error('Failed to fetch activity:', e)
    } finally {
      isLoadingActivity.value = false
    }
  }

  async function fetchDeadlines(boardId: string) {
    try {
      isLoadingDeadlines.value = true
      deadlinesData.value = await getBoardDeadlines(boardId)
    } catch (e) {
      console.error('Failed to fetch deadlines:', e)
    } finally {
      isLoadingDeadlines.value = false
    }
  }

  return {
    activeMode,
    activityPeriod,
    progressData,
    activityData,
    deadlinesData,
    isLoadingProgress,
    isLoadingActivity,
    isLoadingDeadlines,
    fetchProgress,
    fetchActivity,
    fetchDeadlines,
  }
})

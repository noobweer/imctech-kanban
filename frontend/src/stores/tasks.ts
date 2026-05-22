import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { tasksApi } from '@/api/tasks'
import type { Task, TaskIn, TaskUpdateIn } from '@/types/task'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const toast = useToast()

  const backlogTasks = computed(() => tasks.value.filter(t => t.column_kind === 'backlog' && t.status === 'active'))
  
  const getTasksByColumnId = computed(() => {
    return (columnId: string) => tasks.value.filter(t => t.column_id === columnId && t.status === 'active')
  })

  // Poll interval
  let intervalId: number | null = null

  async function fetchTasks(boardId: string, isSilent = false) {
    if (!isSilent) loading.value = true
    error.value = null
    try {
      // Get all tasks (backlog and board)
      const data: any = await tasksApi.getBoardTasks(boardId)
      
      // Handle django-ninja pagination format if present
      const items = data && !Array.isArray(data) && 'items' in data ? data.items : data
      
      tasks.value = Array.isArray(items) ? items : []
    } catch (e: any) {
      if (!isSilent) {
        error.value = e.message || 'Failed to load tasks'
        toast.error(error.value)
      }
    } finally {
      if (!isSilent) loading.value = false
    }
  }

  function startPolling(boardId: string) {
    if (intervalId) return
    intervalId = window.setInterval(() => {
      fetchTasks(boardId, true)
    }, 5000)
  }

  function stopPolling() {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  async function createTask(boardId: string, data: TaskIn) {
    loading.value = true
    try {
      const newTask = await tasksApi.createTask(boardId, data)
      tasks.value.push(newTask)
      toast.success('Task created successfully')
      return newTask
    } catch (e: any) {
      toast.error(e.message || 'Failed to create task')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateTask(taskId: string, data: TaskUpdateIn) {
    try {
      const updated = await tasksApi.updateTask(taskId, data)
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updated
      }
      return updated
    } catch (e: any) {
      toast.error(e.message || 'Failed to update task')
      throw e
    }
  }

  async function archiveTask(taskId: string) {
    try {
      const updated = await tasksApi.archiveTask(taskId)
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updated
      }
      toast.info('Task archived')
    } catch (e: any) {
      toast.error(e.message || 'Failed to archive task')
      throw e
    }
  }

  async function deleteTask(taskId: string) {
    try {
      await tasksApi.deleteTask(taskId)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
      toast.info('Task deleted')
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete task')
      throw e
    }
  }

  return {
    tasks,
    loading,
    error,
    backlogTasks,
    getTasksByColumnId,
    fetchTasks,
    startPolling,
    stopPolling,
    createTask,
    updateTask,
    archiveTask,
    deleteTask
  }
})

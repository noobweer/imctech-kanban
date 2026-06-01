import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { tasksApi } from '@/api/tasks'
import { useCommentsStore } from '@/stores/comments'
import type { Task, TaskIn, TaskUpdateIn } from '@/types/task'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const toast = useToast()
  const commentsStore = useCommentsStore()

  const backlogTasks = computed(() => {
    const filtered = tasks.value.filter(t => t.column_kind === 'backlog')
    return filtered.sort((a, b) => a.position - b.position)
  })
  
  const getTasksByColumnId = computed(() => {
    return (columnId: string) => {
      const filtered = tasks.value.filter(t => t.column_id === columnId)
      return filtered.sort((a, b) => a.position - b.position)
    }
  })

  const isDragging = ref(false)

  // Poll interval
  let intervalId: number | null = null

  async function fetchTasks(boardId: string, isSilent = false) {
    if (isDragging.value) return // Prevent overwriting state mid-drag
    
    if (!isSilent) loading.value = true
    error.value = null
    try {
      // Get all tasks (backlog and board)
      const data: any = await tasksApi.getBoardTasks(boardId)
      
      // Handle django-ninja pagination format if present
      const items = data && !Array.isArray(data) && 'items' in data ? data.items : data
      
      tasks.value = Array.isArray(items) ? items : []
      
      // Fetch comment states for the board
      await commentsStore.fetchBoardStates(boardId)
    } catch (e: any) {
      if (!isSilent) {
        error.value = e.message || 'Failed to load tasks'
        toast.error(error.value as string)
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
    } catch (e: any) {
      toast.error(e.message || 'Failed to archive task')
      throw e
    }
  }

  async function restoreTask(taskId: string, targetColumnId: string, position?: number) {
    try {
      const updated = await tasksApi.restoreTask(taskId, targetColumnId, position)
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updated
      } else {
        tasks.value.push(updated)
      }
    } catch (e: any) {
      toast.error(e.message || 'Failed to restore task')
      throw e
    }
  }

  async function deleteTask(taskId: string) {
    try {
      await tasksApi.deleteTask(taskId)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete task')
      throw e
    }
  }

  function updateTaskInStore(updatedTask: Partial<Task> & { id: string }) {
    const index = tasks.value.findIndex(t => t.id === updatedTask.id)
    if (index !== -1) {
      tasks.value[index] = { ...tasks.value[index], ...updatedTask } as Task
    }
  }

  async function moveTask(taskId: string, targetColumnId: string, position: number) {
    // Optimistic Update
    const taskIndex = tasks.value.findIndex(t => t.id === taskId)
    let previousTaskState: Task | null = null
    
    if (taskIndex !== -1) {
      previousTaskState = { ...tasks.value[taskIndex] } as Task
      
      // Calculate a fake position float for optimistic sorting
      const targetTasks = tasks.value
        .filter(t => t.column_id === targetColumnId && t.id !== taskId)
        .sort((a, b) => a.position - b.position)
        
      let optimisticPosition = 65536.0
      if (targetTasks.length > 0) {
        if (position === 0) {
          optimisticPosition = targetTasks[0]!.position / 2.0
        } else if (position >= targetTasks.length) {
          optimisticPosition = targetTasks[targetTasks.length - 1]!.position + 65536.0
        } else {
          optimisticPosition = (targetTasks[position - 1]!.position + targetTasks[position]!.position) / 2.0
        }
      }

      tasks.value[taskIndex] = { 
        ...tasks.value[taskIndex], 
        column_id: targetColumnId, 
        position: optimisticPosition 
      } as Task
    }

    try {
      // Backend expects 1-indexed positions, but vuedraggable and store use 0-indexed.
      const parsedPosition = parseInt(position as any, 10)
      const result = await tasksApi.moveTask(taskId, targetColumnId, parsedPosition + 1)
      updateTaskInStore(result.task)
      
      // Update all reordered sibling tasks' positions
      if (result.reordered_tasks) {
        for (const [id, newPos] of Object.entries(result.reordered_tasks)) {
          const storeTask = tasks.value.find(t => t.id === id)
          if (storeTask) {
            storeTask.position = newPos
          }
        }
      }
      
      // Silent sync to guarantee absolute truth from backend
      const taskBoardId = tasks.value.find(t => t.id === taskId)?.board_id
      if (taskBoardId) {
        fetchTasks(taskBoardId, true)
      }
      
      return result
    } catch (e: any) {
      // Revert optimistic update on failure
      if (previousTaskState && taskIndex !== -1) {
        tasks.value[taskIndex] = previousTaskState
      }
      toast.error(e.message || 'Failed to move task')
      throw e
    }
  }

  async function addChecklistItem(taskId: string, title: string) {
    try {
      const updated = await tasksApi.addChecklistItem(taskId, title)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to add item')
      throw e
    }
  }

  async function updateChecklistItem(taskId: string, itemId: string, data: { title?: string; is_done?: boolean }) {
    try {
      const updated = await tasksApi.updateChecklistItem(taskId, itemId, data)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to update item')
      throw e
    }
  }

  async function toggleChecklistItem(taskId: string, itemId: string) {
    try {
      const updated = await tasksApi.toggleChecklistItem(taskId, itemId)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to toggle item')
      throw e
    }
  }

  async function deleteChecklistItem(taskId: string, itemId: string) {
    try {
      const updated = await tasksApi.deleteChecklistItem(taskId, itemId)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete item')
      throw e
    }
  }

  async function reorderChecklist(taskId: string, orderedItemIds: string[]) {
    try {
      const updated = await tasksApi.reorderChecklist(taskId, orderedItemIds)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to reorder items')
      throw e
    }
  }

  async function assignTask(taskId: string, username: string) {
    try {
      const updated = await tasksApi.assignTask(taskId, username)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to assign user')
      throw e
    }
  }

  async function unassignTask(taskId: string, username: string) {
    try {
      const updated = await tasksApi.unassignTask(taskId, username)
      updateTaskInStore(updated)
    } catch (e: any) {
      toast.error(e.message || 'Failed to unassign user')
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
    restoreTask,
    deleteTask,
    moveTask,
    addChecklistItem,
    updateChecklistItem,
    toggleChecklistItem,
    deleteChecklistItem,
    reorderChecklist,
    assignTask,
    unassignTask,
    isDragging
  }
})

import { apiClient } from './client'
import type { Task, TaskIn, TaskUpdateIn } from '@/types/task'

export const tasksApi = {
  getBoardTasks(boardId: string, params?: Record<string, any>) {
    return apiClient<Task[]>(`/boards/${boardId}/tasks`, { params })
  },

  getBacklogTasks(boardId: string, params?: Record<string, any>) {
    return apiClient<Task[]>(`/boards/${boardId}/backlog/tasks`, { params })
  },

  getColumnTasks(columnId: string, params?: Record<string, any>) {
    return apiClient<Task[]>(`/columns/${columnId}/tasks`, { params })
  },

  getTask(taskId: string) {
    return apiClient<Task>(`/tasks/${taskId}`)
  },

  createTask(boardId: string, data: TaskIn) {
    return apiClient<Task>(`/boards/${boardId}/tasks`, {
      method: 'POST',
      body: data
    })
  },

  createColumnTask(columnId: string, data: TaskIn) {
    return apiClient<Task>(`/columns/${columnId}/tasks`, {
      method: 'POST',
      body: data
    })
  },

  updateTask(taskId: string, data: TaskUpdateIn) {
    return apiClient<Task>(`/tasks/${taskId}`, {
      method: 'PATCH',
      body: data
    })
  },

  archiveTask(taskId: string) {
    return apiClient<Task>(`/tasks/${taskId}/archive`, {
      method: 'POST'
    })
  },

  restoreTask(taskId: string) {
    return apiClient<Task>(`/tasks/${taskId}/restore`, {
      method: 'POST'
    })
  },

  deleteTask(taskId: string) {
    return apiClient<{ success: boolean; message: string }>(`/tasks/${taskId}`, {
      method: 'DELETE'
    })
  }
}

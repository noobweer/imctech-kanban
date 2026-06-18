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
      body: data,
    })
  },

  createColumnTask(columnId: string, data: TaskIn) {
    return apiClient<Task>(`/columns/${columnId}/tasks`, {
      method: 'POST',
      body: data,
    })
  },

  updateTask(taskId: string, data: TaskUpdateIn) {
    return apiClient<Task>(`/tasks/${taskId}`, {
      method: 'PATCH',
      body: data,
    })
  },

  archiveTask(taskId: string) {
    return apiClient<Task>(`/tasks/${taskId}/archive`, {
      method: 'POST',
    })
  },

  restoreTask(taskId: string, targetColumnId: string, position?: number) {
    return apiClient<Task>(`/tasks/${taskId}/restore`, {
      method: 'POST',
      body: { target_column_id: targetColumnId, position },
    })
  },

  deleteTask(taskId: string) {
    return apiClient<{ success: boolean; message: string }>(`/tasks/${taskId}`, {
      method: 'DELETE',
    })
  },

  // Task move
  moveTask(taskId: string, targetColumnId: string, position: number) {
    return apiClient<{
      task: Task
      affected_column_ids: string[]
      reordered_tasks: Record<string, number>
    }>(`/tasks/${taskId}/move`, {
      method: 'POST',
      body: { target_column_id: targetColumnId, position },
    })
  },

  // Checklist
  addChecklistItem(taskId: string, title: string) {
    return apiClient<Task>(`/tasks/${taskId}/checklist/items`, {
      method: 'POST',
      body: { title },
    })
  },

  updateChecklistItem(taskId: string, itemId: string, data: { title?: string; is_done?: boolean }) {
    return apiClient<Task>(`/tasks/${taskId}/checklist/items/${itemId}`, {
      method: 'PATCH',
      body: data,
    })
  },

  toggleChecklistItem(taskId: string, itemId: string) {
    return apiClient<Task>(`/tasks/${taskId}/checklist/items/${itemId}/toggle`, {
      method: 'POST',
    })
  },

  deleteChecklistItem(taskId: string, itemId: string) {
    return apiClient<Task>(`/tasks/${taskId}/checklist/items/${itemId}/delete`, {
      method: 'POST',
    })
  },

  reorderChecklist(taskId: string, orderedItemIds: string[]) {
    return apiClient<Task>(`/tasks/${taskId}/checklist/reorder`, {
      method: 'POST',
      body: { ordered_item_ids: orderedItemIds },
    })
  },

  // Assignment
  assignTask(taskId: string, username: string) {
    return apiClient<Task>(`/tasks/${taskId}/assign`, {
      method: 'POST',
      body: { username },
    })
  },

  unassignTask(taskId: string, username: string) {
    return apiClient<Task>(`/tasks/${taskId}/unassign`, {
      method: 'POST',
      body: { username },
    })
  },

  // Mentor Requests
  createMentorRequest(taskId: string, data: import('@/types/mentorRequest').MentorRequestCreate) {
    return apiClient<import('@/types/mentorRequest').MentorRequest>(
      `/tasks/${taskId}/mentor-requests`,
      {
        method: 'POST',
        body: data,
      },
    )
  },

  getActiveMentorRequest(taskId: string) {
    return apiClient<import('@/types/mentorRequest').MentorRequest | null>(
      `/tasks/${taskId}/mentor-request`,
    )
  },
}

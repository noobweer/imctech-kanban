import { apiClient } from './client'
import type {
  TaskComment,
  TaskCommentCreateIn,
  TaskCommentUpdateIn,
  TaskCommentStateOut,
} from '@/types/comment'

export const commentsApi = {
  getTaskComments(taskId: string) {
    return apiClient<TaskComment[]>(`/tasks/${taskId}/comments`)
  },

  createComment(taskId: string, data: TaskCommentCreateIn) {
    return apiClient<TaskComment>(`/tasks/${taskId}/comments`, {
      method: 'POST',
      body: data,
    })
  },

  updateComment(commentId: string, data: TaskCommentUpdateIn) {
    return apiClient<TaskComment>(`/comments/${commentId}`, {
      method: 'PATCH',
      body: data,
    })
  },

  deleteComment(commentId: string) {
    return apiClient<{ success: boolean; message: string }>(`/comments/${commentId}`, {
      method: 'DELETE',
    })
  },

  markAsRead(taskId: string) {
    return apiClient<{ success: boolean }>(`/tasks/${taskId}/comments/read`, {
      method: 'POST',
    })
  },

  getTaskCommentState(taskId: string) {
    return apiClient<TaskCommentStateOut>(`/tasks/${taskId}/comments/state`)
  },

  getBoardCommentsStates(boardId: string, taskIds?: string[]) {
    const params = taskIds && taskIds.length > 0 ? { task_ids: taskIds.join(',') } : {}
    return apiClient<TaskCommentStateOut[]>(`/boards/${boardId}/comments/states`, { params })
  },
}

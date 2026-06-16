import { defineStore } from 'pinia'
import { ref } from 'vue'
import { commentsApi } from '@/api/comments'
import type {
  TaskComment,
  TaskCommentStateOut,
  TaskCommentCreateIn,
  TaskCommentUpdateIn,
} from '@/types/comment'
import { useToast } from '@/composables/useToast'

export const useCommentsStore = defineStore('comments', () => {
  const boardStates = ref<Record<string, TaskCommentStateOut>>({})
  const activeTaskComments = ref<TaskComment[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const toast = useToast()

  async function fetchBoardStates(boardId: string) {
    try {
      const states = await commentsApi.getBoardCommentsStates(boardId)
      const stateMap: Record<string, TaskCommentStateOut> = {}
      for (const s of states) {
        stateMap[s.task_id] = s
      }
      boardStates.value = stateMap
    } catch (e: any) {
      console.error('Failed to fetch board comment states:', e)
    }
  }

  async function fetchTaskComments(taskId: string) {
    loading.value = true
    error.value = null
    try {
      const comments = await commentsApi.getTaskComments(taskId)
      activeTaskComments.value = comments
    } catch (e: any) {
      error.value = e.message || 'Failed to load comments'
      toast.error(error.value as string)
    } finally {
      loading.value = false
    }
  }

  async function createComment(taskId: string, data: TaskCommentCreateIn) {
    try {
      const comment = await commentsApi.createComment(taskId, data)
      const exists = activeTaskComments.value.some((c) => c.id === comment.id)
      if (!exists) {
        activeTaskComments.value.push(comment)
      } else {
        const idx = activeTaskComments.value.findIndex((c) => c.id === comment.id)
        if (idx !== -1) activeTaskComments.value[idx] = comment
      }

      // Update state optimistically
      if (!boardStates.value[taskId]) {
        boardStates.value[taskId] = {
          task_id: taskId,
          comments_state: 'read',
          comments_count: 1,
          has_comments: true,
          has_unread_comments: false,
        }
      } else {
        boardStates.value[taskId].comments_count += 1
      }
      return comment
    } catch (e: any) {
      toast.error(e.message || 'Failed to post comment')
      throw e
    }
  }

  async function updateComment(commentId: string, data: TaskCommentUpdateIn) {
    try {
      const updated = await commentsApi.updateComment(commentId, data)
      const idx = activeTaskComments.value.findIndex((c) => c.id === commentId)
      if (idx !== -1) {
        activeTaskComments.value[idx] = updated
      }
      return updated
    } catch (e: any) {
      toast.error(e.message || 'Failed to update comment')
      throw e
    }
  }

  async function deleteComment(commentId: string) {
    try {
      await commentsApi.deleteComment(commentId)
      const deletedComment = activeTaskComments.value.find((c) => c.id === commentId)
      const taskId = deletedComment?.task_id

      activeTaskComments.value = activeTaskComments.value.filter((c) => c.id !== commentId)
      if (taskId && boardStates.value[taskId]) {
        boardStates.value[taskId].comments_count = Math.max(
          0,
          boardStates.value[taskId].comments_count - 1,
        )
      }
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete comment')
      throw e
    }
  }

  async function markAsRead(taskId: string) {
    try {
      await commentsApi.markAsRead(taskId)
      if (boardStates.value[taskId]) {
        boardStates.value[taskId].comments_state = 'read'
        boardStates.value[taskId].has_unread_comments = false
      }
    } catch (e: any) {
      toast.error(e.message || 'Failed to mark comments as read')
    }
  }

  function handleSocketEvent(type: string, payload: any) {
    if (type === 'comment.created') {
      const exists = activeTaskComments.value.some((c) => c.id === payload.id)
      if (
        !exists &&
        activeTaskComments.value.length > 0 &&
        activeTaskComments.value[0]?.task_id === payload.task_id
      ) {
        activeTaskComments.value.push(payload)
      }

      const taskId = payload.task_id
      if (!boardStates.value[taskId]) {
        boardStates.value[taskId] = {
          task_id: taskId,
          comments_state: 'unread',
          comments_count: 1,
          has_comments: true,
          has_unread_comments: true,
        }
      } else {
        boardStates.value[taskId].comments_count += 1
        boardStates.value[taskId].comments_state = 'unread'
        boardStates.value[taskId].has_unread_comments = true
      }
    } else if (type === 'comment.updated') {
      const idx = activeTaskComments.value.findIndex((c) => c.id === payload.id)
      if (idx !== -1) {
        activeTaskComments.value[idx] = { ...activeTaskComments.value[idx], ...payload }
      }
    } else if (type === 'comment.deleted') {
      activeTaskComments.value = activeTaskComments.value.filter((c) => c.id !== payload.comment_id)
      const taskId = payload.task_id
      if (boardStates.value[taskId]) {
        boardStates.value[taskId].comments_count = Math.max(
          0,
          boardStates.value[taskId].comments_count - 1,
        )
      }
    } else if (type === 'comments.read_state_updated') {
      boardStates.value[payload.task_id] = payload
    }
  }

  return {
    boardStates,
    activeTaskComments,
    loading,
    error,
    fetchBoardStates,
    fetchTaskComments,
    createComment,
    updateComment,
    deleteComment,
    markAsRead,
    handleSocketEvent,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { mentorRequestsApi } from '@/api/mentorRequests'
import { tasksApi } from '@/api/tasks'
import { boardsApi } from '@/api/boards'
import type { MentorRequest, MentorRequestType } from '@/types/mentorRequest'
import { useToast } from '@/composables/useToast'

export const useMentorRequestsStore = defineStore('mentorRequests', () => {
  const toast = useToast()

  // state
  const activeRequests = ref<Record<string, MentorRequest | null>>({}) // key: taskId
  const boardRequests = ref<MentorRequest[]>([])
  const boardRequestsTotal = ref(0)
  const loading = ref(false)

  // actions
  async function fetchActiveRequest(taskId: string) {
    loading.value = true
    try {
      const request = await tasksApi.getActiveMentorRequest(taskId)
      // will be null (204 No Content) if none exists
      activeRequests.value[taskId] = request
    } catch (err) {
      console.error(err)
      toast.error('Failed to fetch active mentor request')
    } finally {
      loading.value = false
    }
  }

  async function fetchBoardRequests(
    boardId: string,
    params?: Record<string, string | number | boolean>,
  ) {
    loading.value = true
    try {
      const res = await boardsApi.getMentorRequests(boardId, params)
      boardRequests.value = res.items
      boardRequestsTotal.value = res.count
    } catch (err: unknown) {
      console.error(err)
      toast.error('Failed to fetch board mentor requests')
    } finally {
      loading.value = false
    }
  }

  async function createRequest(taskId: string, requestType: MentorRequestType, message: string) {
    loading.value = true
    try {
      const newReq = await tasksApi.createMentorRequest(taskId, {
        request_type: requestType,
        message,
      })
      activeRequests.value[taskId] = newReq
      return newReq
    } catch (err: unknown) {
      console.error(err)
      toast.error((err as Error).message || 'Failed to create request')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function respondRequest(requestId: string, content: string) {
    loading.value = true
    try {
      const res = await mentorRequestsApi.respond(requestId, { content })
      // Update in activeRequests if it matches
      const taskId = res.mentor_request.task_id
      if (activeRequests.value[taskId]?.id === requestId) {
        activeRequests.value[taskId] = res.mentor_request
      }

      // Inject the newly created comment into commentsStore
      const { useCommentsStore } = await import('@/stores/comments')
      const commentsStore = useCommentsStore()

      const exists = commentsStore.activeTaskComments.some((c) => c.id === res.comment.id)
      if (
        !exists &&
        (commentsStore.activeTaskComments.length === 0 ||
          commentsStore.activeTaskComments[0]?.task_id === taskId)
      ) {
        commentsStore.activeTaskComments.push(res.comment)
      }

      if (!commentsStore.boardStates[taskId]) {
        commentsStore.boardStates[taskId] = {
          task_id: taskId,
          comments_state: 'read',
          comments_count: 1,
          has_comments: true,
          has_unread_comments: false,
        }
      } else {
        if (!exists) {
          commentsStore.boardStates[taskId].comments_count += 1
        }
        commentsStore.boardStates[taskId].comments_state = 'read'
        commentsStore.boardStates[taskId].has_unread_comments = false
      }

      return res
    } catch (err: unknown) {
      console.error(err)
      toast.error((err as Error).message || 'Failed to respond to request')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function resolveRequest(requestId: string, taskId: string) {
    loading.value = true
    try {
      const res = await mentorRequestsApi.resolve(requestId)
      if (activeRequests.value[taskId]?.id === requestId) {
        activeRequests.value[taskId] = null // It's no longer active
      }
      return res
    } catch (err: unknown) {
      console.error(err)
      toast.error((err as Error).message || 'Failed to resolve request')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function cancelRequest(requestId: string, taskId: string, reason?: string) {
    loading.value = true
    try {
      const res = await mentorRequestsApi.cancel(requestId, { close_reason: reason })
      if (activeRequests.value[taskId]?.id === requestId) {
        activeRequests.value[taskId] = null // It's no longer active
      }
      return res
    } catch (err: unknown) {
      console.error(err)
      toast.error((err as Error).message || 'Failed to cancel request')
      throw err
    } finally {
      loading.value = false
    }
  }

  // WebSocket event handlers (Optimistic updates / reactive sync)
  function handleRequestCreated(req: MentorRequest) {
    activeRequests.value[req.task_id] = req

    // Add to boardRequests if not exists
    if (!boardRequests.value.some((r) => r.id === req.id)) {
      boardRequests.value.unshift(req)
      boardRequestsTotal.value++
    }
  }

  function handleRequestStarted(req: MentorRequest) {
    if (activeRequests.value[req.task_id]?.id === req.id) {
      activeRequests.value[req.task_id] = req
    }

    // Update in boardRequests
    const idx = boardRequests.value.findIndex((r) => r.id === req.id)
    if (idx !== -1) {
      boardRequests.value[idx] = req
    }
  }

  function handleRequestClosed(req: MentorRequest) {
    // resolved or cancelled
    if (activeRequests.value[req.task_id]?.id === req.id) {
      activeRequests.value[req.task_id] = null
    }

    // Remove from boardRequests since we only show open/in_progress
    boardRequests.value = boardRequests.value.filter((r) => r.id !== req.id)
    boardRequestsTotal.value = Math.max(0, boardRequestsTotal.value - 1)
  }

  return {
    activeRequests,
    boardRequests,
    boardRequestsTotal,
    loading,
    fetchActiveRequest,
    fetchBoardRequests,
    createRequest,
    respondRequest,
    resolveRequest,
    cancelRequest,
    handleRequestCreated,
    handleRequestStarted,
    handleRequestClosed,
  }
})

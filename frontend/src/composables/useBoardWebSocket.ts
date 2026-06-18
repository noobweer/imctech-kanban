import { ref } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { useColumnsStore } from '@/stores/columns'
import { useCommentsStore } from '@/stores/comments'
import { useMentorRequestsStore } from '@/stores/mentorRequests'
import { useAuthStore } from '@/stores/auth'

export function useBoardWebSocket() {
  const ws = ref<WebSocket | null>(null)
  let reconnectTimer: number | null = null
  let currentBoardId: string | null = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_DELAY = 10000

  const tasksStore = useTasksStore()
  const columnsStore = useColumnsStore()
  const commentsStore = useCommentsStore()
  const mentorRequestsStore = useMentorRequestsStore()
  const authStore = useAuthStore()

  function connect(boardId: string) {
    if (currentBoardId === boardId && ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    disconnect() // clear previous connection
    currentBoardId = boardId
    reconnectAttempts = 0
    _connect()
  }

  function _connect() {
    if (!currentBoardId) return

    const token = localStorage.getItem('access_token')
    if (!token) {
      console.warn('No access token found for WebSocket connection')
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.DEV ? `${window.location.hostname}:8000` : window.location.host
    const url = `${protocol}//${host}/ws/boards/${currentBoardId}/?token=${token}`

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      // If we reconnected, fetch a fresh copy of the board to sync any missed events
      if (reconnectAttempts > 0 && currentBoardId) {
        columnsStore.fetchColumns(currentBoardId, true)
        tasksStore.fetchTasks(currentBoardId, true)
      }
      reconnectAttempts = 0
    }

    ws.value.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data)
        const { type, payload, actor_id } = data

        // Echo Cancellation: Ignore events triggered by the current user
        if (actor_id && authStore.user && String(actor_id) === String(authStore.user.id)) {
          return
        }

        // Route events to appropriate stores
        if (type.startsWith('task.')) {
          tasksStore.handleSocketEvent(type, payload)
        } else if (type.startsWith('column.')) {
          columnsStore.handleSocketEvent(type, payload)
        } else if (type.startsWith('comment.') || type.startsWith('comments.')) {
          commentsStore.handleSocketEvent(type, payload)
        } else if (type.startsWith('mentor_request.')) {
          if (type === 'mentor_request.created') {
            mentorRequestsStore.handleRequestCreated(payload)
          } else if (type === 'mentor_request.started') {
            mentorRequestsStore.handleRequestStarted(payload)
          } else if (type === 'mentor_request.resolved' || type === 'mentor_request.cancelled') {
            mentorRequestsStore.handleRequestClosed(payload)
          }
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message', err)
      }
    }

    ws.value.onclose = (event) => {
      ws.value = null
      // Do not reconnect if it was a normal closure (e.g. we disconnected)
      if (event.code === 1000 || event.code === 1001) return

      // Also, if we don't have a board ID anymore, stop
      if (!currentBoardId) return

      scheduleReconnect()
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket Error:', error)
      // onclose will fire after onerror usually
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)

    // Exponential backoff
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), MAX_RECONNECT_DELAY)
    reconnectAttempts++

    reconnectTimer = window.setTimeout(() => {
      _connect()
    }, delay)
  }

  function disconnect() {
    currentBoardId = null
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close(1000, 'Client disconnected')
      ws.value = null
    }
  }

  return {
    connect,
    disconnect,
  }
}

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Board, BoardMember, Invite } from '@/types/board'
import { boardsApi, type CreateBoardData, type UpdateBoardData } from '@/api/boards'
import { membersApi } from '@/api/members'
import { invitesApi, type CreateInviteData } from '@/api/invites'

export const useBoardsStore = defineStore('boards', () => {
  const boards = ref<Board[]>([])
  const loading = ref(false)
  const activeTab = ref<'active' | 'archived'>('active')
  const searchQuery = ref('')

  // Members state
  const members = ref<BoardMember[]>([])
  const membersLoading = ref(false)

  // Invite state
  const currentInvite = ref<Invite | null>(null)
  const inviteLoading = ref(false)

  const filteredBoards = computed(() => {
    if (!Array.isArray(boards.value)) return []
    return boards.value.filter((board) => {
      const matchesTab = board.status === activeTab.value
      const matchesSearch =
        searchQuery.value === '' ||
        board.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        board.project_name.toLowerCase().includes(searchQuery.value.toLowerCase())
      return matchesTab && matchesSearch
    })
  })

  async function fetchBoards() {
    loading.value = true
    try {
      const response = await boardsApi.getBoards()
      // Backend @paginate returns { items: [], count: n }
      if (response && typeof response === 'object' && 'items' in response) {
        boards.value = (response as any).items
      } else if (Array.isArray(response)) {
        boards.value = response
      } else {
        boards.value = []
      }
    } catch (error) {
      console.error('Failed to fetch boards:', error)
      boards.value = []
    } finally {
      loading.value = false
    }
  }

  async function createBoard(data: CreateBoardData) {
    loading.value = true
    try {
      const newBoard = await boardsApi.createBoard(data)
      boards.value.unshift(newBoard)
      return newBoard
    } catch (error) {
      console.error('Failed to create board:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateBoard(id: string, updates: UpdateBoardData) {
    try {
      const updatedBoard = await boardsApi.updateBoard(id, updates)
      const index = boards.value.findIndex((b) => b.id === id)
      if (index !== -1) {
        boards.value[index] = updatedBoard
      }
    } catch (error) {
      console.error('Failed to update board:', error)
      throw error
    }
  }

  async function archiveBoard(id: string) {
    // Backend DELETE archives the board
    try {
      await boardsApi.deleteBoard(id)
      const board = boards.value.find((b) => b.id === id)
      if (board) {
        board.status = 'archived'
      }
    } catch (error) {
      console.error('Failed to archive board:', error)
      throw error
    }
  }

  async function restoreBoard(id: string) {
    await updateBoard(id, { status: 'active' })
  }

  async function deleteBoard(id: string) {
    // If backend only supports archiving via DELETE, we might need a separate endpoint for hard delete
    // For now, let's treat it as archive per API docs
    await archiveBoard(id)
  }

  // --- Members ---

  async function fetchMembers(boardId: string) {
    membersLoading.value = true
    try {
      members.value = await membersApi.getMembers(boardId)
    } catch (error) {
      console.error('Failed to fetch members:', error)
      members.value = []
    } finally {
      membersLoading.value = false
    }
  }

  async function removeMember(boardId: string, username: string) {
    await membersApi.removeMember(boardId, username)
    members.value = members.value.filter((m) => m.username !== username)
  }

  async function leaveBoard(boardId: string) {
    await membersApi.leaveBoard(boardId)
  }

  // --- Invite ---

  async function fetchCurrentInvite(boardId: string) {
    inviteLoading.value = true
    try {
      currentInvite.value = await invitesApi.getCurrentInvite(boardId)
    } catch (error: any) {
      // 404 means no active invite yet — that's OK
      if (error?.response?.status !== 404) {
        console.error('Failed to fetch current invite:', error)
      }
      currentInvite.value = null
    } finally {
      inviteLoading.value = false
    }
  }

  async function generateInvite(boardId: string, data: CreateInviteData) {
    inviteLoading.value = true
    try {
      currentInvite.value = await invitesApi.createInvite(boardId, data)
    } catch (error) {
      console.error('Failed to generate invite:', error)
      throw error
    } finally {
      inviteLoading.value = false
    }
  }

  return {
    boards,
    loading,
    activeTab,
    searchQuery,
    filteredBoards,
    fetchBoards,
    createBoard,
    updateBoard,
    archiveBoard,
    restoreBoard,
    deleteBoard,
    // Members
    members,
    membersLoading,
    fetchMembers,
    removeMember,
    leaveBoard,
    // Invite
    currentInvite,
    inviteLoading,
    fetchCurrentInvite,
    generateInvite,
  }
})

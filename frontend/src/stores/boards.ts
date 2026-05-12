import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Board } from '@/types/board'
import { boardsApi, type CreateBoardData, type UpdateBoardData } from '@/api/boards'

export const useBoardsStore = defineStore('boards', () => {
  const boards = ref<Board[]>([])
  const loading = ref(false)
  const activeTab = ref<'active' | 'archived'>('active')
  const searchQuery = ref('')

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
  }
})

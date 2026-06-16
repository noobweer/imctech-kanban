import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Column, CreateColumnData, UpdateColumnData } from '@/types/column'
import { columnsApi } from '@/api/columns'

export const useColumnsStore = defineStore('columns', () => {
  const columns = ref<Column[]>([])
  const loading = ref(false)
  const currentBoardId = ref<string | null>(null)

  const activeColumns = computed(() => {
    return [...columns.value]
      .filter((c) => c.status === 'active')
      .sort((a, b) => a.position - b.position)
  })

  async function fetchColumns(boardId: string, silent = false) {
    // Stale-While-Revalidate logic:
    // If we're on the same board and have data, don't show loading state
    const isSameBoard = currentBoardId.value === boardId
    const hasData = columns.value.length > 0

    if (!silent && (!isSameBoard || !hasData)) {
      loading.value = true
    }

    // Clear data only if navigating to a DIFFERENT board
    if (!isSameBoard) {
      columns.value = []
      currentBoardId.value = boardId
    }

    try {
      const response = await columnsApi.getBoardColumns(boardId)
      let newColumns: Column[] = []

      if (response && typeof response === 'object' && 'items' in response) {
        newColumns = response.items
      } else if (Array.isArray(response)) {
        newColumns = response
      }

      // Only update if we haven't switched boards in the meantime
      if (currentBoardId.value === boardId) {
        columns.value = newColumns
      }
    } catch (error) {
      console.error('Failed to fetch columns:', error)
      // On error, only clear if we didn't have stale data
      if (!isSameBoard) columns.value = []
    } finally {
      loading.value = false
    }
  }

  async function createColumn(boardId: string, data: CreateColumnData) {
    try {
      const newColumn = await columnsApi.createColumn(boardId, data)
      const exists = columns.value.some((c) => c.id === newColumn.id)
      if (!exists) {
        columns.value.push(newColumn)
      } else {
        const index = columns.value.findIndex((c) => c.id === newColumn.id)
        if (index !== -1) columns.value[index] = newColumn
      }
      return newColumn
    } catch (error) {
      console.error('Failed to create column:', error)
      throw error
    }
  }

  async function createDefaultColumns(boardId: string) {
    loading.value = true
    try {
      const newColumns = await columnsApi.createDefaultColumns(boardId)
      columns.value = newColumns
      return newColumns
    } catch (error) {
      console.error('Failed to create default columns:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateColumn(id: string, updates: UpdateColumnData) {
    try {
      const updatedColumn = await columnsApi.updateColumn(id, updates)
      const index = columns.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        columns.value[index] = updatedColumn
      }
      return updatedColumn
    } catch (error) {
      console.error('Failed to update column:', error)
      throw error
    }
  }

  async function moveColumn(id: string, position: number) {
    try {
      // Optimistic update would be nice, but backend recalculates everything.
      // Re-fetching or manual recalculation is safer.
      await columnsApi.moveColumn(id, { position })
      // For simplicity, we re-fetch all columns of the board after move
      // to ensure positions are in sync with backend logic.
      const boardId = columns.value[0]?.board_id
      if (boardId) {
        await fetchColumns(boardId)
      }
    } catch (error) {
      console.error('Failed to move column:', error)
      throw error
    }
  }

  async function archiveColumn(id: string) {
    try {
      await columnsApi.archiveColumn(id)
      const column = columns.value.find((c) => c.id === id)
      if (column) {
        column.status = 'archived'
      }
    } catch (error) {
      console.error('Failed to archive column:', error)
      throw error
    }
  }

  async function restoreColumn(id: string) {
    try {
      await columnsApi.restoreColumn(id)
      const column = columns.value.find((c) => c.id === id)
      if (column) {
        column.status = 'active'
      } else if (currentBoardId.value) {
        // Just refetch to be safe since position was recalculated by backend
        await fetchColumns(currentBoardId.value, true)
      }
    } catch (error) {
      console.error('Failed to restore column:', error)
      throw error
    }
  }

  async function clearColumn(id: string) {
    try {
      await columnsApi.clearColumn(id)
      // Re-fetch columns to update sum_tasks
      if (currentBoardId.value) {
        await fetchColumns(currentBoardId.value, true)
      }
    } catch (error) {
      console.error('Failed to clear column:', error)
      throw error
    }
  }

  function handleSocketEvent(type: string, payload: any) {
    if (type === 'column.created') {
      const exists = columns.value.some((c) => c.id === payload.id)
      if (!exists) columns.value.push(payload)
    } else if (
      type === 'column.updated' ||
      type === 'column.moved' ||
      type === 'column.archived' ||
      type === 'column.restored'
    ) {
      const index = columns.value.findIndex((c) => c.id === payload.id)
      if (index !== -1) {
        columns.value[index] = { ...columns.value[index], ...payload }
      }
    } else if (type === 'column.cleared') {
      if (currentBoardId.value) {
        fetchColumns(currentBoardId.value, true)
      }
    }
  }

  return {
    columns,
    loading,
    activeColumns,
    fetchColumns,
    createColumn,
    createDefaultColumns,
    updateColumn,
    moveColumn,
    archiveColumn,
    restoreColumn,
    clearColumn,
    handleSocketEvent,
  }
})

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Column, CreateColumnData, UpdateColumnData } from '@/types/column'
import { columnsApi } from '@/api/columns'

export const useColumnsStore = defineStore('columns', () => {
  const columns = ref<Column[]>([])
  const loading = ref(false)

  const activeColumns = computed(() => {
    return [...columns.value]
      .filter((c) => c.status === 'active')
      .sort((a, b) => a.position - b.position)
  })

  async function fetchColumns(boardId: string) {
    loading.value = true
    try {
      const response = await columnsApi.getBoardColumns(boardId)
      if (response && typeof response === 'object' && 'items' in response) {
        columns.value = response.items
      } else if (Array.isArray(response)) {
        columns.value = response
      } else {
        columns.value = []
      }
    } catch (error) {
      console.error('Failed to fetch columns:', error)
      columns.value = []
    } finally {
      loading.value = false
    }
  }

  async function createColumn(boardId: string, data: CreateColumnData) {
    try {
      const newColumn = await columnsApi.createColumn(boardId, data)
      columns.value.push(newColumn)
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
      if (columns.value.length > 0) {
        await fetchColumns(columns.value[0].board_id)
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
  }
})

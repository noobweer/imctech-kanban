import { apiClient } from './client'
import type { Column, CreateColumnData, UpdateColumnData, MoveColumnData } from '@/types/column'

export const columnsApi = {
  async getBoardColumns(boardId: string, status?: 'active' | 'archived'): Promise<Column[] | { items: Column[]; count: number }> {
    return apiClient(`/boards/${boardId}/columns`, {
      query: status ? { status } : {},
    })
  },

  async createColumn(boardId: string, data: CreateColumnData): Promise<Column> {
    return apiClient(`/boards/${boardId}/columns`, {
      method: 'POST',
      body: data,
    })
  },

  async createDefaultColumns(boardId: string): Promise<Column[]> {
    return apiClient(`/boards/${boardId}/columns/defaults`, {
      method: 'POST',
    })
  },

  async getColumn(id: string): Promise<Column> {
    return apiClient(`/columns/${id}`)
  },

  async updateColumn(id: string, data: UpdateColumnData): Promise<Column> {
    return apiClient(`/columns/${id}`, {
      method: 'PATCH',
      body: data,
    })
  },

  async moveColumn(id: string, data: MoveColumnData): Promise<Column> {
    return apiClient(`/columns/${id}/move`, {
      method: 'POST',
      body: data,
    })
  },

  async archiveColumn(id: string): Promise<Column> {
    return apiClient(`/columns/${id}/archive`, {
      method: 'POST',
    })
  },

  async deleteColumn(id: string): Promise<{ success: boolean; message: string }> {
    return apiClient(`/columns/${id}`, {
      method: 'DELETE',
    })
  },
}

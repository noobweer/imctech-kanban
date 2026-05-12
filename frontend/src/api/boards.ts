import { apiClient } from './client'
import type { Board } from '@/types/board'

export interface CreateBoardData {
  name: string
  description?: string
  project_id?: string
  status?: 'active' | 'archived'
}

export interface UpdateBoardData {
  name?: string
  description?: string
  status?: 'active' | 'archived'
}

export const boardsApi = {
  async getBoards(status?: 'active' | 'archived'): Promise<Board[] | { items: Board[]; count: number }> {
    return apiClient('/boards', {
      query: status ? { status } : {},
    })
  },

  async createBoard(data: CreateBoardData): Promise<Board> {
    return apiClient('/boards', {
      method: 'POST',
      body: data,
    })
  },

  async getBoard(id: string): Promise<Board> {
    return apiClient(`/boards/${id}`)
  },

  async updateBoard(id: string, data: UpdateBoardData): Promise<Board> {
    return apiClient(`/boards/${id}`, {
      method: 'PATCH',
      body: data,
    })
  },

  async deleteBoard(id: string): Promise<{ success: boolean; message: string }> {
    return apiClient(`/boards/${id}`, {
      method: 'DELETE',
    })
  },
}

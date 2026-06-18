import { apiClient } from './client'
import type { Board } from '@/types/board'
import type { CreateColumnData } from '@/types/column'
import type { CommentFeedOut } from '@/types/commentFeed'

export interface CreateBoardData {
  name: string
  description?: string
  project_id?: string
  status?: 'active' | 'archived'
  columns?: CreateColumnData[]
}

export interface UpdateBoardData {
  name?: string
  description?: string
  status?: 'active' | 'archived'
}

export const boardsApi = {
  async getBoards(
    status?: 'active' | 'archived',
  ): Promise<Board[] | { items: Board[]; count: number }> {
    return apiClient('/boards', {
      query: status ? { status } : {},
    })
  },

  async getArchiveTasks(boardId: string, params?: Record<string, any>) {
    return apiClient(`/boards/${boardId}/archive/tasks`, { params })
  },

  async getArchiveColumns(boardId: string, params?: Record<string, any>) {
    return apiClient(`/boards/${boardId}/archive/columns`, { params })
  },

  async getCommentsFeed(boardId: string, filter: 'new' | 'activity'): Promise<CommentFeedOut> {
    return apiClient(`/boards/${boardId}/comments/feed`, {
      query: { filter },
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

  async getMentorRequests(
    boardId: string,
    params?: {
      status?: string
      request_type?: string
      mine?: boolean
      limit?: number
      offset?: number
    },
  ): Promise<{ items: import('@/types/mentorRequest').MentorRequest[]; count: number }> {
    return apiClient(`/boards/${boardId}/mentor-requests`, {
      query: params,
    })
  },
}

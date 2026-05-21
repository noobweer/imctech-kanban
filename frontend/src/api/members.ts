import { apiClient } from './client'
import type { BoardMember } from '@/types/board'

export const membersApi = {
  async getMembers(boardId: string): Promise<BoardMember[]> {
    return apiClient(`/boards/${boardId}/members`)
  },

  async removeMember(
    boardId: string,
    username: string,
  ): Promise<{ success: boolean; message: string }> {
    return apiClient(`/boards/${boardId}/members/${username}`, {
      method: 'DELETE',
    })
  },

  async leaveBoard(boardId: string): Promise<{ success: boolean; message: string }> {
    return apiClient(`/boards/${boardId}/leave`, {
      method: 'POST',
    })
  },
}

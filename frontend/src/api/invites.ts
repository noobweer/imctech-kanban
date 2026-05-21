import { apiClient } from './client'
import type { Invite } from '@/types/board'

export interface CreateInviteData {
  expires_in_days?: number
  max_uses: number | null
}

export interface InvitePublicInfo {
  id: string
  board_name: string
  is_active: boolean
  is_expired: boolean
  is_exhausted: boolean
  invite_path: string
}

export const invitesApi = {
  async getInvites(boardId: string): Promise<Invite[]> {
    return apiClient(`/boards/${boardId}/invites`)
  },

  async getCurrentInvite(boardId: string): Promise<Invite> {
    return apiClient(`/boards/${boardId}/invites/current`)
  },

  async createInvite(boardId: string, data: CreateInviteData): Promise<Invite> {
    return apiClient(`/boards/${boardId}/invites`, {
      method: 'POST',
      body: data,
    })
  },

  async getInvite(inviteId: string): Promise<Invite | InvitePublicInfo> {
    return apiClient(`/invites/${inviteId}`)
  },

  async deleteInvite(inviteId: string): Promise<{ success: boolean; message: string }> {
    return apiClient(`/invites/${inviteId}`, {
      method: 'DELETE',
    })
  },

  async joinByInvite(inviteId: string): Promise<{ success: boolean; message: string }> {
    return apiClient(`/invites/${inviteId}/join`, {
      method: 'POST',
    })
  },
}

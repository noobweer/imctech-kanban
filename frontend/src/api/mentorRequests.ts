import { apiClient } from './client'
import type {
  MentorRequest,
  MentorRequestRespond,
  MentorRequestCancel,
} from '@/types/mentorRequest'
import type { TaskComment } from '@/types/comment'

export const mentorRequestsApi = {
  get: async (id: string): Promise<MentorRequest> => {
    return apiClient(`/mentor-requests/${id}`)
  },

  respond: async (
    id: string,
    payload: MentorRequestRespond,
  ): Promise<{ mentor_request: MentorRequest; comment: TaskComment }> => {
    return apiClient(`/mentor-requests/${id}/respond`, {
      method: 'POST',
      body: payload,
    })
  },

  resolve: async (id: string): Promise<MentorRequest> => {
    return apiClient(`/mentor-requests/${id}/resolve`, {
      method: 'POST',
    })
  },

  cancel: async (id: string, payload: MentorRequestCancel): Promise<MentorRequest> => {
    return apiClient(`/mentor-requests/${id}/cancel`, {
      method: 'POST',
      body: payload,
    })
  },
}

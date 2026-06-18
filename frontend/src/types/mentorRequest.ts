export type MentorRequestType = 'help' | 'review'
export type MentorRequestStatus = 'open' | 'in_progress' | 'resolved' | 'cancelled'

export interface MentorRequest {
  id: string
  task_id: string
  task_title: string
  board_id: string
  created_by_id: number
  created_by_username: string
  request_type: MentorRequestType
  status: MentorRequestStatus
  message: string

  started_by_id: number | null
  started_by_username: string | null
  started_comment_id: string | null
  started_at: string | null

  closed_by_id: number | null
  closed_by_username: string | null
  closed_at: string | null
  close_reason: string | null

  created_at: string
  updated_at: string
}

export interface MentorRequestCreate {
  request_type: MentorRequestType
  message: string
}

export interface MentorRequestRespond {
  content: string
}

export interface MentorRequestCancel {
  close_reason?: string
}

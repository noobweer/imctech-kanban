export interface TaskComment {
  id: string
  task_id: string
  content: string
  links: string[]
  owner_username: string
  owner_name: string
  owner_role: string
  is_edited: boolean
  created_at: string
  updated_at: string
}

export interface TaskCommentCreateIn {
  content: string
  links?: string[]
}

export interface TaskCommentUpdateIn {
  content?: string
  links?: string[]
}

export type CommentState = 'none' | 'read' | 'unread'

export interface TaskCommentStateOut {
  task_id: string
  comments_state: CommentState
  comments_count: number
  has_comments: boolean
  has_unread_comments: boolean
  last_comment_at?: string
}

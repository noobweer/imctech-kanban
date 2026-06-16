export interface CommentFeedTaskOut {
  id: string
  title: string
  column: string
  priority: number
  deadline: string | null
  added_to_board_at: string | null
  assignees: string[]
  comments_count: number
  last_comment_at: string | null
  comments_state: 'none' | 'read' | 'unread'
}

export interface CommentFeedOut {
  filter: 'new' | 'activity'
  total: number
  tasks: CommentFeedTaskOut[]
}

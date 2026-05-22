export interface ChecklistItem {
  title: string
  is_done: boolean
}

export interface Task {
  id: string
  board_id: string
  board_name: string
  column_id: string
  column_name: string
  column_kind: string
  title: string
  content: string
  priority: number
  deadline: string | null
  status: 'active' | 'archived'
  assignees: string[]
  owner_username: string
  position: number
  tags: string[]
  checklist: ChecklistItem[]
  checklist_done_count: number
  checklist_total_count: number
  created_at: string
  updated_at: string
}

export interface TaskIn {
  title: string
  content?: string
  column_id?: string
  priority?: number
  deadline?: string | null
  tags?: string[]
  checklist?: ChecklistItem[]
  assignees?: string[]
}

export interface TaskUpdateIn {
  title?: string
  content?: string
  column_id?: string
  priority?: number
  deadline?: string | null
  status?: 'active' | 'archived'
  tags?: string[]
  checklist?: ChecklistItem[]
  assignees?: string[]
}

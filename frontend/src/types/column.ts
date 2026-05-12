export interface Column {
  id: string
  board_id: string
  board_name: string
  name: string
  position: number
  status: 'active' | 'archived'
  sum_tasks: number
  created_at: string
  updated_at: string
}

export interface CreateColumnData {
  name: string
  position?: number
}

export interface UpdateColumnData {
  name?: string
  status?: 'active' | 'archived'
}

export interface MoveColumnData {
  position: number
}

export interface Board {
  id: string
  name: string
  description?: string
  project_id: string
  project_name: string
  owner_username: string
  members: string[]
  status: 'active' | 'archived'
  tasks_total: number
  tasks_done: number
  progress_percent: number
  created_at: string
  updated_at: string
}

export interface BoardMember {
  username: string
  name: string
  role: string
  is_owner: boolean
}

export interface Invite {
  id: string
  board_id: string
  board_name: string
  invite_code: string
  invite_path: string
  max_uses: number | null
  used_count: number
  expire_at: string
  is_active: boolean
  created_by_username: string | null
  created_at: string
  updated_at: string
}

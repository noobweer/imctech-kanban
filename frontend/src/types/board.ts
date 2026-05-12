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
  avatar?: string
  role?: 'Mentor' | 'Student'
}

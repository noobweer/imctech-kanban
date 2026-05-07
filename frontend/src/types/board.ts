export interface Board {
  id: string
  title: string
  category: string
  dueDate: string
  progress: number
  members: BoardMember[]
  createdBy: string
  archived?: boolean
}

export interface BoardMember {
  username: string
  name: string
  avatar?: string
  role?: 'Mentor' | 'Student'
}

export interface Task {
  id: string
  title: string
  description: string
  dueDate?: string
  completedDate?: string
  subtasksTotal: number
  subtasksCompleted: number
  type: 'Bug' | 'Feature' | 'Task'
  assignee: {
    name: string
    avatar: string
  }
  status: 'todo' | 'inprogress' | 'review' | 'done'
}

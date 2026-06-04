import { apiClient } from './client'

export interface ProgressColumnOut {
  id: string
  name: string
  task_count: number
  percent: number
}

export interface ProgressOut {
  total_tasks: number
  columns: ProgressColumnOut[]
}

export interface ActivityColumnOut {
  column_id: string
  column_name: string
  task_count: number
  percent: number
}

export interface ActivityMemberOut {
  username: string
  name: string
  columns: ActivityColumnOut[]
}

export interface ActivityOut {
  period: string
  week_start: string
  week_end: string
  members: ActivityMemberOut[]
}

export interface DeadlineTaskOut {
  id: string
  title: string
  deadline: string
  column: string
  assignees: string[]
  priority: number
  added_to_board_at: string | null
}

export interface DeadlinesOut {
  overdue: DeadlineTaskOut[]
  due_soon: DeadlineTaskOut[]
}

export async function getBoardProgress(boardId: string): Promise<ProgressOut> {
  return await apiClient<ProgressOut>(`/boards/${boardId}/overview/progress`)
}

export async function getBoardActivity(
  boardId: string,
  period: 'weekly' | 'all_time' = 'weekly',
): Promise<ActivityOut> {
  return await apiClient<ActivityOut>(`/boards/${boardId}/overview/activity`, {
    query: { period },
  })
}

export async function getBoardDeadlines(boardId: string): Promise<DeadlinesOut> {
  return await apiClient<DeadlinesOut>(`/boards/${boardId}/overview/deadlines`)
}

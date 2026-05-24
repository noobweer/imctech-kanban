import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info'

export interface ToastItem {
  id: number
  type: ToastType
  message: string
}

let nextId = 0
const toasts = ref<ToastItem[]>([])

function add(type: ToastType, message: string, duration = 3500) {
  const id = ++nextId
  toasts.value.push({ id, type, message })
  setTimeout(() => remove(id), duration)
}

function remove(id: number) {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

export function useToast() {
  return {
    success: (message: string, duration?: number) => add('success', message, duration),
    error: (message: string, duration?: number) => add('error', message, duration),
    info: (message: string, duration?: number) => add('info', message, duration),
    remove,
    toasts,
  }
}

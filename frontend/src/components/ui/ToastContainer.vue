<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { useToast, type ToastType } from '@/composables/useToast'

const { toasts, remove } = useToast()

function colorClasses(type: ToastType) {
  if (type === 'success') return 'border-l-[3px] border-l-[var(--color-success-green)] bg-[var(--color-success-subtle)] text-[var(--color-success-green-text)]'
  if (type === 'error')   return 'border-l-[3px] border-l-[var(--color-error)] bg-[rgba(186,26,26,0.1)] text-[var(--color-error)]'
  return                         'border-l-[3px] border-l-[var(--color-primary-container)] bg-[rgba(113,50,245,0.1)] text-[var(--color-primary-container)]'
}

function label(type: ToastType) {
  if (type === 'success') return 'Success'
  if (type === 'error')   return 'Error'
  return 'Info'
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 w-[320px] max-w-[calc(100vw-48px)]"
      aria-live="polite"
      aria-atomic="false"
    >
      <TransitionGroup
        tag="div"
        class="flex flex-col gap-3"
        enter-active-class="t-panel-slide-enter"
        leave-active-class="t-panel-slide-leave"
        enter-from-class="t-panel-slide-from"
        enter-to-class="t-panel-slide-to"
        leave-from-class="t-panel-slide-to"
        leave-to-class="t-panel-slide-from"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="flex items-start gap-3 rounded-xl px-4 py-3 shadow-dropdown cursor-default select-none"
          :class="colorClasses(toast.type)"
        >
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-semibold leading-none mb-1">{{ label(toast.type) }}</p>
            <p class="text-[13px] font-medium leading-snug break-words">{{ toast.message }}</p>
          </div>
          <button
            class="shrink-0 mt-0.5 opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
            :aria-label="`Dismiss ${label(toast.type)} notification`"
            @click="remove(toast.id)"
          >
            <X :size="16" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import { useColumnsStore } from '@/stores/columns'
import type { Task } from '@/types/task'

const props = defineProps<{
  isOpen: boolean
  task: Task | null
}>()

const emit = defineEmits<{
  close: []
  restore: [taskId: string, targetColumnId: string]
}>()

const columnsStore = useColumnsStore()
const selectedColumnId = ref('')
const isShaking = ref(false)

const availableColumns = computed(() => {
  return columnsStore.columns.filter(c => 
    c.status === 'active' && (c.kind === 'board' || c.kind === 'backlog')
  )
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // Default to backlog if available, otherwise first board column
    const backlog = availableColumns.value.find(c => c.kind === 'backlog')
    selectedColumnId.value = backlog?.id || availableColumns.value[0]?.id || ''
  }
})

function handleRestore() {
  if (!selectedColumnId.value || !props.task) {
    isShaking.value = true
    setTimeout(() => { isShaking.value = false }, 500)
    return
  }
  emit('restore', props.task.id, selectedColumnId.value)
}
</script>

<template>
  <Modal
    :model-value="isOpen"
    max-width="400px"
    @update:model-value="emit('close')"
  >
    <div class="flex flex-col gap-6 p-2">
      <div>
        <h3 class="text-xl font-bold text-on-surface mb-2">Restore Task</h3>
        <p class="text-sm text-text-secondary">Choose where you want to restore <span class="font-bold text-text-primary">"{{ task?.title }}"</span>.</p>
      </div>

      <div>
        <label for="target-column" class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-2 block">
          Target Column
        </label>
        <select
          id="target-column"
          v-model="selectedColumnId"
          class="w-full px-4 py-2 bg-surface-container-low border border-border-gray rounded-xl focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all text-sm appearance-none"
          :class="{ 'is-shaking border-error': isShaking }"
        >
          <option value="" disabled>Select a column</option>
          <option v-for="col in availableColumns" :key="col.id" :value="col.id">
            {{ col.name }} {{ col.kind === 'backlog' ? '(Backlog)' : '' }}
          </option>
        </select>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3 px-2">
        <Button variant="ghost" size="md" @click="emit('close')">
          Cancel
        </Button>
        <Button variant="primary" size="md" @click="handleRestore">
          Confirm Restore
        </Button>
      </div>
    </template>
  </Modal>
</template>

<style scoped>
.is-shaking {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23686b82' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}
</style>

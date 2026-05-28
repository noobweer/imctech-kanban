<script setup lang="ts">
import { ref, watch } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
  save: [name: string]
}>()

const columnName = ref('')
const isShaking = ref(false)

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    columnName.value = ''
  }
})

function handleSave() {
  if (!columnName.value.trim()) {
    isShaking.value = true
    setTimeout(() => { isShaking.value = false }, 500)
    return
  }
  emit('save', columnName.value.trim())
}
</script>

<template>
  <Modal
    :model-value="isOpen"
    max-width="400px"
    @update:model-value="emit('close')"
  >
    <form @submit.prevent="handleSave" id="column-form" class="flex flex-col gap-6 p-2">
      <div>
        <h3 class="text-xl font-bold text-on-surface mb-2">Add Column</h3>
        <p class="text-sm text-text-secondary">Create a new column to organize your tasks.</p>
      </div>

      <div>
        <label for="column-name" class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-2 block">
          Column Name
        </label>
        <Input
          id="column-name"
          v-model="columnName"
          placeholder="e.g. In Review"
          :class="{ 'is-shaking border-error': isShaking }"
          autofocus
        />
      </div>
    </form>

    <template #footer>
      <div class="flex items-center justify-end gap-3 px-2">
        <Button variant="ghost" size="md" @click="emit('close')">
          Cancel
        </Button>
        <Button variant="primary" size="md" type="submit" form="column-form">
          Create Column
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
</style>

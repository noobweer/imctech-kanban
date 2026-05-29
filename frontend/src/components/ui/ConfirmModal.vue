<script setup lang="ts">
import { AlertTriangle, Info } from 'lucide-vue-next'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'

interface Props {
  isOpen: boolean
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  isDestructive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  isDestructive: false,
})

const emit = defineEmits<{
  close: []
  confirm: []
}>()
</script>

<template>
  <Modal
    :model-value="isOpen"
    max-width="440px"
    @update:model-value="emit('close')"
  >
    <div class="flex gap-4 p-2 sm:p-4">
      <!-- Icon -->
      <div 
        class="shrink-0 w-12 h-12 rounded-full flex items-center justify-center"
        :class="isDestructive ? 'bg-error-container text-error' : 'bg-surface-container-high text-primary-container'"
      >
        <AlertTriangle v-if="isDestructive" :size="24" />
        <Info v-else :size="24" />
      </div>

      <!-- Text -->
      <div class="flex-1 pt-1">
        <h3 class="text-xl font-bold text-on-surface mb-2 leading-tight">
          {{ title }}
        </h3>
        <p class="text-sm text-text-secondary leading-relaxed">
          {{ description }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col sm:flex-row sm:items-center justify-end gap-3 px-2 sm:px-4">
        <Button 
          variant="ghost" 
          size="sm" 
          class="w-full sm:w-auto" 
          @click="emit('close')"
        >
          {{ cancelText }}
        </Button>
        <Button 
          variant="primary" 
          size="sm" 
          class="w-full sm:w-auto"
          :class="{ 'btn-destructive': isDestructive }"
          @click="emit('confirm')"
        >
          {{ confirmText }}
        </Button>
      </div>
    </template>
  </Modal>
</template>

<style scoped>
.btn-destructive {
  background-color: var(--color-error) !important;
}
.btn-destructive:hover {
  background-color: rgba(186, 26, 26, 0.9) !important;
}
</style>

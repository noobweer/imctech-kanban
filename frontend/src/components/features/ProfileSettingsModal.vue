<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Modal from '@/components/ui/Modal.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const authStore = useAuthStore()
const displayName = ref('')
const error = ref('')

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen && authStore.user) {
      displayName.value = authStore.user.name
      error.value = ''
    }
  }
)

function close() {
  emit('update:modelValue', false)
}

function handleSave() {
  error.value = ''

  if (!displayName.value.trim()) {
    error.value = 'Display name is required'
    return
  }

  if (displayName.value.trim().length < 2) {
    error.value = 'Display name must be at least 2 characters'
    return
  }

  authStore.updateProfile(displayName.value.trim())
  close()
}
</script>

<template>
  <Modal :model-value="modelValue" title="Profile Settings" max-width="450px" @update:model-value="emit('update:modelValue', $event)">
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-text-primary mb-2">
          Display Name
        </label>
        <Input
          v-model="displayName"
          placeholder="Enter your display name"
          :error="error"
          @keyup.enter="handleSave"
        />
        <p v-if="error" class="mt-1 text-xs text-error">
          {{ error }}
        </p>
      </div>

      <div class="text-xs text-neutral-gray">
        <p><strong>Username:</strong> @{{ authStore.user?.username }}</p>
        <p><strong>Role:</strong> {{ authStore.user?.role === 'mentor' ? 'Mentor' : 'Student' }}</p>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button variant="ghost" size="sm" @click="close">
          Cancel
        </Button>
        <Button variant="primary" size="sm" @click="handleSave">
          Save Changes
        </Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Board } from '@/types/board'
import { useBoardsStore } from '@/stores/boards'
import Modal from '@/components/ui/Modal.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

interface Props {
  modelValue: boolean
  board: Board
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const boardsStore = useBoardsStore()
const boardTitle = ref('')
const error = ref('')
const showDeleteConfirm = ref(false)

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      boardTitle.value = props.board.title
      error.value = ''
      showDeleteConfirm.value = false
    }
  }
)

function close() {
  emit('update:modelValue', false)
}

function handleSave() {
  error.value = ''

  if (!boardTitle.value.trim()) {
    error.value = 'Board name is required'
    return
  }

  if (boardTitle.value.trim().length < 2) {
    error.value = 'Board name must be at least 2 characters'
    return
  }

  boardsStore.updateBoard(props.board.id, { title: boardTitle.value.trim() })
  close()
}

function handleArchive() {
  if (props.board.archived) {
    boardsStore.restoreBoard(props.board.id)
  } else {
    boardsStore.archiveBoard(props.board.id)
  }
  close()
}

function handleDelete() {
  if (!showDeleteConfirm.value) {
    showDeleteConfirm.value = true
    return
  }

  boardsStore.deleteBoard(props.board.id)
  close()
}
</script>

<template>
  <Modal :model-value="modelValue" title="Board Settings" max-width="500px" @update:model-value="emit('update:modelValue', $event)">
    <div class="space-y-6">
      <!-- Board Name -->
      <div>
        <label class="block text-sm font-medium text-text-primary mb-2">
          Board Name
        </label>
        <Input
          v-model="boardTitle"
          placeholder="Enter board name"
          :error="error"
          @keyup.enter="handleSave"
        />
        <p v-if="error" class="mt-1 text-xs text-error">
          {{ error }}
        </p>
      </div>

      <!-- Actions -->
      <div class="space-y-3 pt-4 border-t border-border-gray">
        <div>
          <Button
            variant="secondary"
            size="md"
            class="w-full flex items-center justify-center gap-2"
            @click="handleArchive"
          >
            <span class="text-sm">{{ board.archived ? 'Restore Board' : 'Archive Board' }}</span>
          </Button>
          <p class="mt-1 text-xs text-neutral-gray">
            {{ board.archived ? 'Move this board back to active boards.' : 'Move this board to archived. You can restore it later.' }}
          </p>
        </div>

        <div>
          <Button
            variant="outlined"
            size="md"
            class="w-full flex items-center justify-center gap-2 !text-error !border-error hover:!bg-red-50"
            @click="handleDelete"
          >
            <span class="text-sm">
              {{ showDeleteConfirm ? 'Click again to confirm deletion' : 'Delete Board' }}
            </span>
          </Button>
          <p class="mt-1 text-xs text-error">
            {{ showDeleteConfirm ? 'This action cannot be undone!' : 'Permanently delete this board and all its data.' }}
          </p>
        </div>
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

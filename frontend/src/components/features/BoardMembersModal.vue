<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Board, BoardMember } from '@/types/board'
import { useBoardsStore } from '@/stores/boards'
import Modal from '@/components/ui/Modal.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import { Search, X } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  board: Board
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const boardsStore = useBoardsStore()
const searchQuery = ref('')
const inviteUsername = ref('')
const inviteError = ref('')

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      searchQuery.value = ''
      inviteUsername.value = ''
      inviteError.value = ''
    }
  }
)

const filteredMembers = computed(() => {
  if (!searchQuery.value.trim()) {
    return props.board.members
  }

  const query = searchQuery.value.toLowerCase()
  return props.board.members.filter(
    (member) =>
      member.name.toLowerCase().includes(query) ||
      member.username.toLowerCase().includes(query)
  )
})

function close() {
  emit('update:modelValue', false)
}

function handleRemoveMember(username: string) {
  boardsStore.removeBoardMember(props.board.id, username)
}

function handleInvite() {
  inviteError.value = ''

  if (!inviteUsername.value.trim()) {
    inviteError.value = 'Username is required'
    return
  }

  const username = inviteUsername.value.trim().replace('@', '')

  // Check if already a member
  if (props.board.members.find((m) => m.username === username)) {
    inviteError.value = 'User is already a member'
    return
  }

  // Mock: Create a new member
  const newMember: BoardMember = {
    username,
    name: username.charAt(0).toUpperCase() + username.slice(1),
    avatar: undefined,
  }

  boardsStore.addBoardMember(props.board.id, newMember)
  inviteUsername.value = ''
}
</script>

<template>
  <Modal :model-value="modelValue" title="Board Members" max-width="550px" @update:model-value="emit('update:modelValue', $event)">
    <div class="space-y-6">
      <!-- Search -->
      <div class="relative">
        <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-gray" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search members..."
          class="w-full pl-10 pr-4 py-2.5 bg-surface-container-low border border-border-gray rounded-xl text-sm focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all"
        />
      </div>

      <!-- Members List -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold text-text-primary">
            Members ({{ filteredMembers.length }})
          </h3>
        </div>

        <div class="space-y-2 max-h-[300px] overflow-y-auto">
          <div
            v-for="member in filteredMembers"
            :key="member.username"
            class="flex items-center gap-3 p-3 rounded-lg border border-border-gray hover:bg-surface-container-low transition-colors"
          >
            <div class="h-10 w-10 rounded-full overflow-hidden border border-border-gray flex-shrink-0">
              <img
                :src="member.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(member.name)}&background=7132f5&color=fff`"
                :alt="member.name"
                class="w-full h-full object-cover"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-text-primary truncate">
                {{ member.name }}
              </p>
              <p class="text-xs text-neutral-gray truncate">
                @{{ member.username }}
              </p>
            </div>
            <button
              class="text-neutral-gray hover:text-error transition-colors p-1.5 rounded-lg hover:bg-red-50"
              @click="handleRemoveMember(member.username)"
            >
              <X :size="18" />
            </button>
          </div>

          <div v-if="filteredMembers.length === 0" class="text-center py-8 text-neutral-gray text-sm">
            No members found
          </div>
        </div>
      </div>

      <!-- Invite Section -->
      <div class="pt-4 border-t border-border-gray">
        <h3 class="text-sm font-semibold text-text-primary mb-3">
          Invite Members
        </h3>
        <div class="flex gap-2">
          <div class="flex-1">
            <Input
              v-model="inviteUsername"
              placeholder="Enter username"
              :error="inviteError"
              @keyup.enter="handleInvite"
            />
            <p v-if="inviteError" class="mt-1 text-xs text-error">
              {{ inviteError }}
            </p>
          </div>
          <Button variant="primary" size="md" @click="handleInvite">
            Invite
          </Button>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end">
        <Button variant="primary" @click="close">
          Close
        </Button>
      </div>
    </template>
  </Modal>
</template>

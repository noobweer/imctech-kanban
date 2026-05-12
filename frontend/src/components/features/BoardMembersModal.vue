<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Board } from '@/types/board'
import Modal from '@/components/ui/Modal.vue'
import Icon from '@/components/ui/Icon.vue'
import { useBoardsStore } from '@/stores/boards'

interface Props {
  modelValue: boolean
  board: Board
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const boardsStore = useBoardsStore()

// Invite link state
const inviteLink = ref(`https://kanban.app/join/${props.board.id}-${Math.random().toString(36).substr(2, 6)}`)
const linkExpiration = ref('7 days')
const linkMaxUses = ref('Unlimited')

function close() {
  emit('update:modelValue', false)
}

function handleCopyLink() {
  navigator.clipboard.writeText(inviteLink.value)
  // TODO: Show toast notification
}

function handleGenerateLink() {
  inviteLink.value = `https://kanban.app/join/${props.board.id}-${Math.random().toString(36).substr(2, 6)}`
  // TODO: API call to generate new link
}

function handleRemoveMember(username: string) {
  // boardsStore.removeBoardMember(props.board.id, username)
  console.log('Remove member:', username)
}

function handleLeaveTeam() {
  // TODO: Implement leave team logic
  console.log('Leave team:', props.board.id)
  close()
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Board Members"
    max-width="550px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <!-- Scrollable Content -->
    <div class="overflow-y-auto max-h-[600px] -mx-6 -my-6">
      <!-- Section 1: Invite New Members -->
      <section class="px-6 py-6">
        <div class="flex items-center gap-2 mb-4">
          <Icon name="user_plus" size="sm" class="text-primary-container" />
          <h3 class="font-semibold text-[22px] text-text-primary">Invite New Members</h3>
        </div>
        <p class="text-sm text-text-secondary mb-3">
          Share this link with your team to grant them access to the board.
        </p>

        <!-- Invite link + Copy button -->
        <div class="flex gap-2 mb-6">
          <input
            readonly
            :value="inviteLink"
            class="flex-1 px-4 py-3 bg-surface-container-low border border-outline/24 rounded-xl text-sm text-text-primary focus:outline-none focus:border-primary-container transition-all"
          />
          <button
            class="px-4 py-3 bg-white font-semibold border border-secondary-container text-secondary-container rounded-xl hover:bg-surface-container transition-all flex items-center gap-2 shadow-[0_4px_24px_rgba(0,0,0,0.03)] active:scale-95"
            @click="handleCopyLink"
          >
            <Icon name="copy" size="sm" />
            Copy
          </button>
        </div>

        <!-- Expiration + Max Uses dropdowns -->
        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="text-xs">Expiration</label>
            <div class="relative">
              <select
                v-model="linkExpiration"
                class="w-full appearance-none px-4 py-3 bg-white border border-outline/24 rounded-xl text-sm text-text-primary focus:outline-none focus:border-primary-container transition-all"
              >
                <option>7 days</option>
                <option>24 hours</option>
                <option>30 days</option>
                <option>Never</option>
              </select>
              <Icon name="chevron_down" size="sm" class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-outline" />
            </div>
          </div>
          <div class="flex flex-col gap-2">
            <label class="text-xs">Max Uses</label>
            <div class="relative">
              <select
                v-model="linkMaxUses"
                class="w-full appearance-none px-4 py-3 bg-white border border-outline/24 rounded-xl text-sm text-text-primary focus:outline-none focus:border-primary-container transition-all"
              >
                <option>Unlimited</option>
                <option>5 uses</option>
                <option>10 uses</option>
                <option>50 uses</option>
              </select>
              <Icon name="chevron_down" size="sm" class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-outline" />
            </div>
          </div>
        </div>

        <!-- Generate button -->
        <button
          class="w-full mt-6 py-3 bg-primary-container text-white font-semibold text-base rounded-xl hover:bg-purple-deep transition-all shadow-[0_4px_24px_rgba(88,0,216,0.12)] active:scale-[0.98]"
          @click="handleGenerateLink"
        >
          Generate New Link
        </button>
      </section>

      <!-- Divider -->
      <div class="h-px bg-border-gray mx-6"></div>

      <!-- Section 2: Current Team Members -->
      <section class="px-6 py-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Icon name="users" size="sm" class="text-primary-container" />
            <h3 class="font-semibold text-[22px] text-text-primary">Current Team Members</h3>
          </div>
          <span class="text-xs text-text-secondary bg-surface-container px-2 py-1 rounded-lg">
            {{ board.members.length }} Members
          </span>
        </div>

        <div class="space-y-0">
          <div
            v-for="username in board.members"
            :key="username"
            class="flex items-center justify-between p-3 bg-white border border-transparent hover:border-border-gray hover:shadow-[0_4px_24px_rgba(0,0,0,0.03)] rounded-xl transition-all group"
          >
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full border-2 border-primary-container/20 overflow-hidden flex-shrink-0">
                <img
                  :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(username)}&background=7132f5&color=fff`"
                  :alt="username"
                  class="w-full h-full object-cover"
                />
              </div>
              <div>
                <p class="text-sm font-medium text-text-primary leading-tight">
                  {{ username }}
                </p>
                <span
                  v-if="username === board.owner_username"
                  class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-[2px] rounded-full mt-1 text-success-green-text bg-success-subtle"
                >
                  Owner
                </span>
              </div>
            </div>
            <button
              v-if="username !== board.owner_username"
              class="text-outline hover:text-error p-2 rounded-lg hover:bg-error/10 transition-all opacity-0 group-hover:opacity-100"
              @click="handleRemoveMember(username)"
            >
              <Icon name="user_minus" size="sm" />
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <template #footer>
      <div class="flex justify-center px-2">
        <button
          class="text-error hover:bg-error/5 px-6 py-3 rounded-xl transition-all flex items-center gap-2 active:scale-95 font-medium"
          @click="handleLeaveTeam"
        >
          <Icon name="logout" size="sm" />
          Leave Team
        </button>
      </div>
    </template>
  </Modal>
</template>

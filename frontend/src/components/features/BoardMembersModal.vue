<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import type { Board } from '@/types/board'
import Modal from '@/components/ui/Modal.vue'
import Icon from '@/components/ui/Icon.vue'
import { useBoardsStore } from '@/stores/boards'
import { useAuthStore } from '@/stores/auth'

interface Props {
  modelValue: boolean
  board: Board
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()
const boardsStore = useBoardsStore()
const authStore = useAuthStore()
const toast = useToast()

// Is current user the owner of this board?
const isOwner = computed(() => authStore.user?.username === props.board.owner_username)

// Invite settings selects
const linkExpiration = ref('7 days')
const linkMaxUses = ref('Unlimited')

// Map UI select values → API params
const expirationMap: Record<string, number> = {
  '7 days': 7,
  '24 hours': 1,
  '30 days': 30,
  'Never': 3650,
}
const maxUsesMap: Record<string, number | null> = {
  'Unlimited': null,
  '5 uses': 5,
  '10 uses': 10,
  '50 uses': 50,
}

// Full invite URL for display
const inviteUrl = computed(() => {
  if (!boardsStore.currentInvite) return ''
  // Use frontend route /join/{id} instead of backend invite_path
  return `${window.location.origin}/join/${boardsStore.currentInvite.id}`
})

// Load data when modal opens
watch(
  () => props.modelValue,
  async (open) => {
    if (!open) return
    await Promise.all([
      boardsStore.fetchMembers(props.board.id),
      isOwner.value ? boardsStore.fetchCurrentInvite(props.board.id) : Promise.resolve(),
    ])
  },
)

function close() {
  emit('update:modelValue', false)
}

function handleCopyLink() {
  if (!inviteUrl.value) return
  navigator.clipboard.writeText(inviteUrl.value)
  toast.success('Invite link copied to clipboard!')
}

async function handleGenerateLink() {
  await boardsStore.generateInvite(props.board.id, {
    expires_in_days: expirationMap[linkExpiration.value] ?? 7,
    max_uses: maxUsesMap[linkMaxUses.value] ?? null,
  })
}

async function handleRemoveMember(username: string) {
  try {
    await boardsStore.removeMember(props.board.id, username)
  } catch (error) {
    console.error('Failed to remove member:', error)
  }
}

async function handleLeaveTeam() {
  try {
    await boardsStore.leaveBoard(props.board.id)
    close()
    router.push('/boards')
  } catch (error) {
    console.error('Failed to leave board:', error)
  }
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
      <!-- Section 1: Invite New Members (owner only) -->
      <section v-if="isOwner" class="px-6 py-6">
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
            :value="inviteUrl || 'No active invite link'"
            class="flex-1 px-4 py-3 bg-surface-container-low border border-outline/24 rounded-xl text-sm text-text-primary focus:outline-none focus:border-primary-container transition-all"
          />
          <button
            :disabled="!inviteUrl"
            class="px-4 py-3 bg-white font-semibold border border-secondary-container text-secondary-container rounded-xl hover:bg-surface-container transition-all flex items-center gap-2 shadow-[0_4px_24px_rgba(0,0,0,0.03)] active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
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
          :disabled="boardsStore.inviteLoading"
          class="w-full mt-6 py-3 bg-primary-container text-white font-semibold text-base rounded-xl hover:bg-purple-deep transition-all shadow-[0_4px_24px_rgba(88,0,216,0.12)] active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
          @click="handleGenerateLink"
        >
          {{ boardsStore.inviteLoading ? 'Generating…' : 'Generate New Link' }}
        </button>
      </section>

      <!-- Divider -->
      <div v-if="isOwner" class="h-px bg-border-gray mx-6"></div>

      <!-- Section 2: Current Team Members -->
      <section class="px-6 py-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Icon name="users" size="sm" class="text-primary-container" />
            <h3 class="font-semibold text-[22px] text-text-primary">Current Team Members</h3>
          </div>
          <span class="text-xs text-text-secondary bg-surface-container px-2 py-1 rounded-lg">
            {{ boardsStore.members.length }} Members
          </span>
        </div>

        <!-- Loading skeleton -->
        <div v-if="boardsStore.membersLoading" class="space-y-3">
          <div
            v-for="i in 3"
            :key="i"
            class="flex items-center gap-4 p-3 animate-pulse"
          >
            <div class="w-10 h-10 rounded-full bg-surface-container-high flex-shrink-0"></div>
            <div class="flex flex-col gap-2 flex-1">
              <div class="h-3 w-32 bg-surface-container-high rounded"></div>
              <div class="h-2 w-20 bg-surface-container rounded"></div>
            </div>
          </div>
        </div>

        <div v-else class="space-y-0">
          <div
            v-for="member in boardsStore.members"
            :key="member.username"
            class="flex items-center justify-between p-3 bg-white border border-transparent hover:border-border-gray hover:shadow-[0_4px_24px_rgba(0,0,0,0.03)] rounded-xl transition-all group"
          >
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full border-2 border-primary-container/20 overflow-hidden flex-shrink-0">
                <img
                  :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(member.name)}&background=7132f5&color=fff`"
                  :alt="member.name"
                  class="w-full h-full object-cover"
                />
              </div>
              <div>
                <p class="text-sm font-medium text-text-primary leading-tight">
                  {{ member.name }}
                </p>
                <div class="flex items-center gap-2 mt-1">
                  <span
                    v-if="member.is_owner"
                    class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-[2px] rounded-full text-success-green-text bg-success-subtle"
                  >
                    Owner
                  </span>
                  <span
                    v-if="member.role"
                    class="inline-flex items-center text-xs px-2 py-[2px] rounded-full text-text-secondary bg-surface-container capitalize"
                  >
                    {{ member.role }}
                  </span>
                </div>
              </div>
            </div>
            <button
              v-if="isOwner && !member.is_owner"
              class="text-outline hover:text-error p-2 rounded-lg hover:bg-error/10 transition-all opacity-0 group-hover:opacity-100"
              @click="handleRemoveMember(member.username)"
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
          v-if="!isOwner"
          class="text-error hover:bg-error/5 px-6 py-3 rounded-xl transition-all flex items-center gap-2 active:scale-95 font-medium"
          @click="handleLeaveTeam"
        >
          <Icon name="logout" size="sm" />
          Leave Team
        </button>
        <span v-else class="text-xs text-text-secondary py-3">
          You are the owner of this board
        </span>
      </div>
    </template>
  </Modal>
</template>

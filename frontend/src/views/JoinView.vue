<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { invitesApi } from '@/api/invites'
import type { InvitePublicInfo } from '@/api/invites'
import Button from '@/components/ui/Button.vue'
import { ClipboardList, XCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const inviteId = route.params.inviteId as string

const invite = ref<InvitePublicInfo | null>(null)
const loading = ref(true)
const joining = ref(false)
const error = ref<string | null>(null)
const isErrorShaking = ref(false)
const success = ref(false)
const joinedBoardId = ref<string | undefined>(undefined)

const enterPage = ref(false)

onMounted(async () => {
  // Trigger page enter animation
  nextTick(() => {
    enterPage.value = true
  })

  try {
    const data = await invitesApi.getInvite(inviteId)
    invite.value = data as InvitePublicInfo
  } catch (e: any) {
    if (e?.response?.status === 404) {
      error.value = 'This invite link is invalid or does not exist.'
    } else {
      error.value = 'Failed to load invite. Please try again.'
    }
  } finally {
    loading.value = false
  }
})

async function handleJoin() {
  if (isErrorShaking.value) return
  joining.value = true
  error.value = null
  
  try {
    const res = await invitesApi.joinByInvite(inviteId)
    joinedBoardId.value = res.board_id
    success.value = true
    
    // Redirect to the specific board after a snappier 1s delay
    setTimeout(() => {
      if (joinedBoardId.value) {
        router.push(`/boards/${joinedBoardId.value}`)
      } else {
        router.push('/boards')
      }
    }, 1000)
    
  } catch (e: any) {
    const detail = e?.data?.detail || e?.message || 'Failed to join board.'
    error.value = detail
    
    isErrorShaking.value = true
    setTimeout(() => {
      isErrorShaking.value = false
    }, 500)
    
  } finally {
    joining.value = false
  }
}

function getStatusMessage(): string | null {
  if (!invite.value) return null
  if (!invite.value.is_active) return 'This invite link has been deactivated.'
  if (invite.value.is_expired) return 'This invite link has expired.'
  if (invite.value.is_exhausted) return 'This invite link has reached its maximum number of uses.'
  return null
}
</script>

<template>
  <main class="min-h-screen flex items-center justify-center bg-[var(--color-background)] px-4">
    <div 
      class="w-full max-w-md transition-all duration-[600ms] ease-[cubic-bezier(0.22,1,0.36,1)]"
      :class="enterPage ? 'opacity-100 translate-y-0 blur-0' : 'opacity-0 translate-y-6 blur-sm'"
    >

      <!-- Loading Skeleton -->
      <div v-if="loading" class="bg-white rounded-2xl border border-border-gray shadow-modal p-6 sm:p-8 text-center space-y-6">
        <div class="w-16 h-16 rounded-2xl bg-surface-container-high animate-pulse mx-auto"></div>
        <div class="space-y-3">
          <div class="h-4 w-40 bg-surface-container rounded mx-auto animate-pulse"></div>
          <div class="h-8 w-64 bg-surface-container-high rounded mx-auto animate-pulse"></div>
        </div>
        <div class="h-[52px] w-full bg-surface-container-high rounded-xl animate-pulse mt-2"></div>
      </div>

      <!-- Error (invite not found) -->
      <div v-else-if="error && !invite" class="bg-white rounded-2xl border border-border-gray shadow-modal p-6 sm:p-8 text-center space-y-6">
        <div class="w-16 h-16 rounded-2xl bg-[var(--color-error)]/10 text-[var(--color-error)] flex items-center justify-center mx-auto">
          <XCircle :size="32" stroke-width="1.5" />
        </div>
        <div class="space-y-2">
          <h1 class="text-2xl font-bold text-text-primary tracking-tight">Invalid Invite</h1>
          <p class="text-text-secondary">{{ error }}</p>
        </div>
        <Button variant="primary" size="lg" class="w-full mt-2" @click="router.push('/boards')">
          Go to Boards
        </Button>
      </div>

      <!-- Invite card -->
      <div 
        v-else-if="invite" 
        class="bg-white rounded-2xl border border-border-gray shadow-modal p-6 sm:p-8 space-y-6 t-input"
        :class="{ 'is-shaking border-[var(--color-error)]': isErrorShaking }"
      >
        <!-- Board info -->
        <div class="text-center space-y-4">
          <div class="w-16 h-16 rounded-2xl bg-[var(--color-primary-container)]/10 text-[var(--color-primary-container)] flex items-center justify-center mx-auto">
            <ClipboardList :size="32" stroke-width="1.5" />
          </div>
          <div class="space-y-1">
            <p class="text-sm font-medium text-text-secondary">You've been invited to join</p>
            <h1 class="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
              {{ invite.board_name }}
            </h1>
          </div>
        </div>

        <!-- Status warning (expired / exhausted / inactive) -->
        <div
          v-if="getStatusMessage()"
          class="px-4 py-3 bg-[var(--color-error)]/5 border border-[var(--color-error)]/20 rounded-xl text-sm font-medium text-[var(--color-error)] text-center"
        >
          {{ getStatusMessage() }}
        </div>

        <!-- API error -->
        <div v-if="error && !isErrorShaking" class="px-4 py-3 bg-[var(--color-error)]/5 border border-[var(--color-error)]/20 rounded-xl text-sm font-medium text-[var(--color-error)] text-center">
          {{ error }}
        </div>

        <div class="space-y-3 pt-2">
          <!-- Join button -->
          <Button
            variant="primary"
            size="lg"
            class="w-full text-[16px]"
            :disabled="joining || success || !!getStatusMessage()"
            @click="handleJoin"
          >
            {{ success ? 'Joined!' : (joining ? 'Joining…' : 'Join Board') }}
          </Button>

          <!-- Already joined? -->
          <Button
            variant="ghost"
            class="w-full text-text-secondary h-11"
            @click="router.push('/boards')"
          >
            Back to my boards
          </Button>
        </div>
      </div>
    </div>
  </main>
</template>

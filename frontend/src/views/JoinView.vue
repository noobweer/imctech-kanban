<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { invitesApi } from '@/api/invites'
import type { InvitePublicInfo } from '@/api/invites'

const route = useRoute()
const router = useRouter()

const inviteId = route.params.inviteId as string

const invite = ref<InvitePublicInfo | null>(null)
const loading = ref(true)
const joining = ref(false)
const error = ref<string | null>(null)
const success = ref(false)

onMounted(async () => {
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
  joining.value = true
  error.value = null
  try {
    await invitesApi.joinByInvite(inviteId)
    success.value = true
    // Redirect to boards after short delay
    setTimeout(() => router.push('/boards'), 1500)
  } catch (e: any) {
    const detail = e?.data?.detail || e?.message || 'Failed to join board.'
    error.value = detail
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
  <main class="min-h-screen flex items-center justify-center bg-surface-white px-4">
    <div class="w-full max-w-md">

      <!-- Loading -->
      <div v-if="loading" class="text-center space-y-4 animate-pulse">
        <div class="h-8 w-48 bg-surface-container-high rounded mx-auto"></div>
        <div class="h-4 w-64 bg-surface-container rounded mx-auto"></div>
        <div class="h-12 w-full bg-surface-container-high rounded-xl"></div>
      </div>

      <!-- Error (invite not found) -->
      <div v-else-if="error && !invite" class="text-center space-y-4">
        <div class="w-16 h-16 rounded-full bg-error/10 flex items-center justify-center mx-auto">
          <span class="text-2xl">✕</span>
        </div>
        <h1 class="text-xl md:text-2xl font-bold text-text-primary font-['Space_Grotesk']">
          Invalid Invite
        </h1>
        <p class="text-text-secondary text-sm">{{ error }}</p>
        <button
          class="w-full py-3 bg-primary-container text-white font-semibold rounded-xl hover:bg-purple-deep transition-all"
          @click="router.push('/boards')"
        >
          Go to Boards
        </button>
      </div>

      <!-- Invite card -->
      <div v-else-if="invite" class="bg-white rounded-2xl border border-border-gray shadow-modal p-4 md:p-8 space-y-4 md:space-y-6">

        <!-- Board info -->
        <div class="text-center space-y-2">
          <div class="w-16 h-16 rounded-2xl bg-primary-container/10 flex items-center justify-center mx-auto mb-4">
            <span class="text-3xl">📋</span>
          </div>
          <p class="text-sm text-text-secondary">You've been invited to join</p>
          <h1 class="text-xl md:text-2xl font-bold text-text-primary font-['Space_Grotesk']">
            {{ invite.board_name }}
          </h1>
        </div>

        <!-- Status warning (expired / exhausted / inactive) -->
        <div
          v-if="getStatusMessage()"
          class="px-4 py-3 bg-error/5 border border-error/20 rounded-xl text-sm text-error text-center"
        >
          {{ getStatusMessage() }}
        </div>

        <!-- Success state -->
        <div
          v-else-if="success"
          class="px-4 py-3 bg-success-subtle border border-success-green-text/20 rounded-xl text-sm text-success-green-text text-center"
        >
          🎉 You've joined the board! Redirecting…
        </div>

        <!-- Join button -->
        <button
          v-if="!getStatusMessage() && !success"
          :disabled="joining"
          class="w-full py-3 bg-primary-container text-white font-semibold text-base rounded-xl hover:bg-purple-deep transition-all shadow-dropdown active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
          @click="handleJoin"
        >
          {{ joining ? 'Joining…' : 'Join Board' }}
        </button>

        <!-- API error -->
        <p v-if="error && invite" class="text-sm text-error text-center">
          {{ error }}
        </p>

        <!-- Already joined? -->
        <button
          class="w-full text-sm text-text-secondary hover:text-primary-container transition-colors"
          @click="router.push('/boards')"
        >
          Back to my boards
        </button>
      </div>
    </div>
  </main>
</template>

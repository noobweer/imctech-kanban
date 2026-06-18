<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useMentorRequestsStore } from '@/stores/mentorRequests'
import type { MentorRequestType } from '@/types/mentorRequest'
import { ArrowRight, Check, CornerDownRight, LifeBuoy, Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

const props = defineProps<{
  taskId: string
}>()

const authStore = useAuthStore()
const mentorRequestsStore = useMentorRequestsStore()
const toast = useToast()

const isMentor = computed(() => authStore.user?.role === 'mentor')

const activeRequest = computed(() => mentorRequestsStore.activeRequests[props.taskId])

const isFormOpen = ref(false)
const requestType = ref<MentorRequestType>('help')
const message = ref('')

function openRequestForm(type: MentorRequestType) {
  requestType.value = type
  isFormOpen.value = true
}

const isRespondOpen = ref(false)
const respondMessage = ref('')

onMounted(async () => {
  await mentorRequestsStore.fetchActiveRequest(props.taskId)
})

async function submitRequest() {
  if (!message.value.trim()) return
  try {
    await mentorRequestsStore.createRequest(props.taskId, requestType.value, message.value)
    isFormOpen.value = false
    message.value = ''
    toast.success('Request sent successfully')
  } catch {
    // Error handled by store
  }
}

async function handleCancel(reason?: string) {
  if (!activeRequest.value) return
  if (isMentor.value && !reason) {
    reason = prompt('Please provide a reason for cancelling this request:') || 'Cancelled by mentor'
  }
  try {
    await mentorRequestsStore.cancelRequest(activeRequest.value.id, props.taskId, reason)
    toast.success('Request cancelled')
  } catch {
    // Error handled by store
  }
}

async function handleResolve() {
  if (!activeRequest.value) return
  try {
    await mentorRequestsStore.resolveRequest(activeRequest.value.id, props.taskId)
    toast.success('Request resolved')
  } catch {
    // Error handled by store
  }
}

async function handleRespond() {
  if (!activeRequest.value || !respondMessage.value.trim()) return
  try {
    await mentorRequestsStore.respondRequest(activeRequest.value.id, respondMessage.value)
    isRespondOpen.value = false
    respondMessage.value = ''
    toast.success('Response sent')
  } catch {
    // Error handled by store
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="mb-4 flex flex-col gap-2">
    <!-- Active Request Block -->
    <Transition name="fade-slide">
      <div
        v-if="activeRequest"
        class="relative rounded-xl border border-[var(--color-primary-container)] bg-[rgba(133,91,251,0.06)] overflow-hidden"
      >
        <!-- Status Indicator Strip -->
        <div class="absolute left-0 top-0 bottom-0 w-1 bg-primary-container"></div>

        <div class="p-4 pl-5">
          <div class="flex justify-between items-start gap-4 mb-2">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span
                  class="px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wide uppercase"
                  :class="
                    activeRequest.request_type === 'help'
                      ? 'bg-[#ff9800]/10 text-[#e65100]'
                      : 'bg-[#2196f3]/10 text-[#0d47a1]'
                  "
                >
                  {{ activeRequest.request_type === 'help' ? 'Help Needed' : 'Review Requested' }}
                </span>
                <span class="text-xs text-neutral-gray flex items-center gap-1">
                  <span
                    class="w-1.5 h-1.5 rounded-full"
                    :class="
                      activeRequest.status === 'open'
                        ? 'bg-[var(--color-error)] animate-pulse'
                        : 'bg-primary-container'
                    "
                  ></span>
                  {{ activeRequest.status === 'open' ? 'Waiting for mentor' : 'In Progress' }}
                </span>
              </div>
              <p class="text-sm text-on-surface font-medium leading-snug">
                <span class="font-bold text-primary-container"
                  >{{ activeRequest.created_by_username }}:</span
                >
                {{ activeRequest.message }}
              </p>
              <div class="text-[10px] text-neutral-gray mt-1">
                Requested at {{ formatDate(activeRequest.created_at) }}
              </div>
            </div>

            <!-- Actions for Student -->
            <div v-if="!isMentor" class="flex flex-col gap-2 shrink-0">
              <Button
                size="sm"
                variant="ghost"
                class="text-[var(--color-error)] hover:bg-[var(--color-error)] hover:text-white"
                @click="handleCancel()"
              >
                <X :size="14" class="mr-1" /> Cancel
              </Button>
              <Button
                v-if="activeRequest.status === 'in_progress'"
                size="sm"
                variant="outlined"
                class="border-primary-container text-primary-container"
                @click="handleResolve()"
              >
                <Check :size="14" class="mr-1" /> Mark Resolved
              </Button>
            </div>

            <!-- Actions for Mentor -->
            <div v-else class="flex flex-col gap-2 shrink-0">
              <Button
                v-if="!isRespondOpen && activeRequest.status === 'open'"
                size="sm"
                variant="primary"
                @click="isRespondOpen = true"
              >
                <CornerDownRight :size="14" class="mr-1" /> Respond
              </Button>
              <Button
                size="sm"
                variant="ghost"
                class="text-neutral-gray hover:text-[var(--color-error)]"
                @click="handleCancel()"
              >
                <X :size="14" class="mr-1" /> Reject
              </Button>
            </div>
          </div>

          <!-- Mentor Respond Form -->
          <Transition name="expand">
            <div v-if="isMentor && isRespondOpen" class="mt-3 overflow-hidden">
              <div class="flex gap-2">
                <textarea
                  v-model="respondMessage"
                  placeholder="Type your response... this will start the request and add a comment."
                  class="flex-1 text-sm bg-white border border-border-gray rounded-lg p-2 resize-none outline-none focus:border-primary-container custom-scrollbar"
                  rows="2"
                  @keydown.enter.exact.prevent="handleRespond"
                ></textarea>
                <div class="flex flex-col justify-end">
                  <Button
                    size="sm"
                    variant="primary"
                    :disabled="!respondMessage.trim() || mentorRequestsStore.loading"
                    @click="handleRespond"
                  >
                    Send
                  </Button>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>

    <!-- Create Request Buttons (Only Student, Only if NO active request) -->
    <Transition name="fade">
      <div v-if="!isMentor && !activeRequest" class="flex flex-col items-center">
        <div v-if="!isFormOpen" class="flex gap-3 w-full justify-center">
          <Button
            size="sm"
            variant="ghost"
            class="text-xs font-semibold text-neutral-gray hover:text-primary-container hover:bg-[rgba(133,91,251,0.06)]"
            @click="openRequestForm('help')"
          >
            <LifeBuoy :size="14" class="mr-1" /> Ask for Help
          </Button>
          <Button
            size="sm"
            variant="ghost"
            class="text-xs font-semibold text-neutral-gray hover:text-primary-container hover:bg-[rgba(133,91,251,0.06)]"
            @click="openRequestForm('review')"
          >
            <Search :size="14" class="mr-1" /> Request Review
          </Button>
        </div>

        <!-- Create Request Form -->
        <Transition name="expand">
          <div
            v-if="isFormOpen"
            class="w-full bg-white border border-border-gray rounded-xl p-3 overflow-hidden"
          >
            <div class="flex items-center gap-2 mb-2 text-primary-container text-sm font-bold">
              <component :is="requestType === 'help' ? LifeBuoy : Search" :size="16" />
              {{ requestType === 'help' ? 'Asking for Help' : 'Requesting Review' }}
            </div>
            <textarea
              v-model="message"
              placeholder="What do you need assistance with?"
              class="w-full text-sm bg-surface-container-lowest border border-border-gray rounded-lg p-2 mb-2 resize-none outline-none focus:border-primary-container custom-scrollbar"
              rows="2"
              @keydown.enter.exact.prevent="submitRequest"
            ></textarea>
            <div class="flex justify-end gap-2">
              <Button
                size="sm"
                variant="ghost"
                class="text-neutral-gray"
                @click="isFormOpen = false"
                >Cancel</Button
              >
              <Button
                size="sm"
                variant="primary"
                :disabled="!message.trim() || mentorRequestsStore.loading"
                @click="submitRequest"
              >
                Send Request <ArrowRight :size="14" class="ml-1" />
              </Button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 200px;
  opacity: 1;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 10px;
}
</style>

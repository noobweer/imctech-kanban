<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import ProfileSettingsModal from './ProfileSettingsModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const showSettingsModal = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/auth')
}

function openSettings() {
  showSettingsModal.value = true
}
</script>

<template>
  <div>
    <Dropdown position="bottom-right">
      <template #trigger>
        <button class="h-8 w-8o rounded-full overflow-hidden border border-border-gray transition-all cursor-pointer">
          <img
            v-if="authStore.user"
            :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(authStore.user.name)}&background=7132f5&color=fff`"
            :alt="authStore.user.name"
            class="w-full h-full object-cover"
          />
        </button>
      </template>

      <!-- User Info Section -->
      <div class="px-4 py-3 border-b border-border-gray">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full overflow-hidden border border-border-gray flex-shrink-0">
            <img
              v-if="authStore.user"
              :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(authStore.user.name)}&background=7132f5&color=fff`"
              :alt="authStore.user.name"
              class="w-full h-full object-cover"
            />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-text-primary truncate">
              {{ authStore.user?.name }}
            </p>
            <p class="text-xs text-neutral-gray truncate">
              @{{ authStore.user?.username }}
            </p>
          </div>
        </div>
        <div class="mt-2">
          <span
            :class="[
              'inline-flex items-center px-2 py-1 rounded-md text-xs font-medium',
              authStore.user?.role === 'mentor'
                ? 'bg-surface-container-high text-neutral-gray'
                : 'bg-surface-container-high text-neutral-gray',
            ]"
          >
            {{ authStore.user?.role === 'mentor' ? 'Mentor' : 'Student' }}
          </span>
        </div>
      </div>

      <!-- Menu Items -->
      <div>
        <DropdownItem icon="settings" @click="openSettings">
          Profile Settings
        </DropdownItem>
        <DropdownItem icon="logout" variant="danger" @click="handleLogout">
          Logout
        </DropdownItem>
      </div>
    </Dropdown>

    <ProfileSettingsModal v-model="showSettingsModal" />
  </div>
</template>

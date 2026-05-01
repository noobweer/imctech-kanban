<script setup lang="ts">
import { ref } from 'vue'
import type { LoginCredentials } from '@/types/auth'
import Icon from '@/components/ui/Icon.vue'

interface Props {
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<{
  submit: [credentials: LoginCredentials]
}>()

const email = ref('')
const password = ref('')
const errors = ref<{ email?: string; password?: string }>({})

const validate = (): boolean => {
  errors.value = {}

  if (!email.value) {
    errors.value.email = 'Login is required'
  }

  if (!password.value) {
    errors.value.password = 'Password is required'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (validate()) {
    emit('submit', {
      email: email.value,
      password: password.value,
    })
  }
}
</script>

<template>
  <form class="space-y-base" @submit.prevent="handleSubmit">
    <div class="space-y-sm">
      <label class="block text-[14px] font-medium text-text-primary" for="login">
        Login
      </label>
      <div class="relative">
        <input
          id="login"
          v-model="email"
          type="email"
          placeholder="Username"
          :disabled="loading"
          class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50 bg-surface-container-lowest text-[16px] font-medium transition-colors focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center text-outline">
          <Icon name="alternate_email" size="sm" />
        </div>
      </div>
      <p v-if="errors.email" class="text-[14px] text-error">{{ errors.email }}</p>
    </div>

    <div class="space-y-sm">
      <label class="block text-[14px] font-medium text-text-primary" for="password">
        Password
      </label>
      <div class="relative">
        <input
          id="password"
          v-model="password"
          type="password"
          placeholder="••••••••••••"
          :disabled="loading"
          class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50 bg-surface-container-lowest text-[16px] font-medium transition-colors focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center text-outline">
          <Icon name="lock_open" size="sm" />
        </div>
      </div>
      <p v-if="errors.password" class="text-[14px] text-error">{{ errors.password }}</p>
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="w-full bg-primary-container cursor-pointer text-white py-md px-lg rounded-xl text-[16px] font-semibold shadow-[0_4px_24px_rgba(113,50,245,0.2)] hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
    >
      {{ loading ? 'Logging in...' : 'Log In' }}
    </button>
  </form>
</template>

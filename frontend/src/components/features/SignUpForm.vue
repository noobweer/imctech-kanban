<script setup lang="ts">
import { ref } from 'vue'
import type { SignUpData } from '@/types/auth'
import Icon from '@/components/ui/Icon.vue'

interface Props {
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<{
  submit: [data: SignUpData]
}>()

const email = ref('')
const password = ref('')
const displayName = ref('')
const userType = ref<'student' | 'mentor'>('student')
const errors = ref<{ email?: string; password?: string; displayName?: string }>({})

const validate = (): boolean => {
  errors.value = {}

  if (!email.value) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.value.email = 'Invalid email format'
  }

  if (!password.value) {
    errors.value.password = 'Password is required'
  } else if (password.value.length < 6) {
    errors.value.password = 'Password must be at least 6 characters'
  }

  if (!displayName.value) {
    errors.value.displayName = 'Display name is required'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (validate()) {
    emit('submit', {
      email: email.value,
      password: password.value,
      displayName: displayName.value,
      userType: userType.value,
    })
  }
}
</script>

<template>
  <form class="space-y-base" @submit.prevent="handleSubmit">
    <div class="space-y-sm">
      <label class="block text-[14px] font-medium text-text-primary" for="email">
        Login
      </label>
      <div class="relative">
        <input
          id="email"
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

    <div class="space-y-sm">
      <label class="block text-[14px] font-medium text-text-primary" for="display-name">
        Display Name
      </label>
      <div class="relative">
        <input
          id="display-name"
          v-model="displayName"
          type="text"
          placeholder="Alex Rivera"
          :disabled="loading"
          class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50 bg-surface-container-lowest text-[16px] font-medium transition-colors focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center text-outline">
          <Icon name="person" size="sm" />
        </div>
      </div>
      <p v-if="errors.displayName" class="text-[14px] text-error">{{ errors.displayName }}</p>
    </div>

    <div class="space-y-sm">
      <label class="block text-[14px] font-medium text-text-primary">
        I am a
      </label>
      <div class="bg-surface-container-low p-xs rounded-xl flex">
        <button
          type="button"
          :class="[
            'flex-1 py-md flex items-center justify-center gap-2 text-[16px] font-semibold rounded-lg transition-all duration-200',
            userType === 'student'
              ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)] text-text-primary'
              : 'text-neutral-gray hover:text-text-primary'
          ]"
          @click="userType = 'student'"
        >
          <Icon name="school" size="sm" />
          <span>Student</span>
        </button>
        <button
          type="button"
          :class="[
            'flex-1 py-md flex items-center justify-center gap-2 text-[16px] font-semibold rounded-lg transition-all duration-200',
            userType === 'mentor'
              ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)] text-text-primary'
              : 'text-neutral-gray hover:text-text-primary'
          ]"
          @click="userType = 'mentor'"
        >
          <Icon name="star" size="sm" />
          <span>Mentor</span>
        </button>
      </div>
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="w-full bg-primary-container text-white py-md px-lg rounded-xl text-[16px] font-semibold shadow-[0_4px_24px_rgba(113,50,245,0.2)] hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
    >
      {{ loading ? 'Signing up...' : 'Complete Sign Up' }}
    </button>
  </form>
</template>

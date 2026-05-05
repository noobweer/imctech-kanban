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

const username = ref('')
const password = ref('')
const name = ref('')
const role = ref<'student' | 'mentor'>('student')
const errors = ref<{ username?: string; password?: string; name?: string }>({})

const validate = (): boolean => {
  errors.value = {}

  if (!username.value) {
    errors.value.username = 'Username is required'
  }

  if (!password.value) {
    errors.value.password = 'Password is required'
  } else if (password.value.length < 6) {
    errors.value.password = 'Password must be at least 6 characters'
  }

  if (!name.value) {
    errors.value.name = 'Name is required'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (validate()) {
    emit('submit', {
      username: username.value,
      password: password.value,
      name: name.value,
      role: role.value,
    })
  }
}
</script>

<template>
  <form class="space-y-base" @submit.prevent="handleSubmit">
    <div class="space-y-sm">
      <label class="block text-[14px] font-medium text-text-primary" for="username">
        Username
      </label>
      <div class="relative">
        <input
          id="username"
          v-model="username"
          type="text"
          placeholder="Username"
          :disabled="loading"
          class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50 bg-surface-container-lowest text-[16px] font-medium transition-colors focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center text-outline">
          <Icon name="alternate_email" size="sm" />
        </div>
      </div>
      <p v-if="errors.username" class="text-[14px] text-error">{{ errors.username }}</p>
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
      <label class="block text-[14px] font-medium text-text-primary" for="name">
        Name
      </label>
      <div class="relative">
        <input
          id="name"
          v-model="name"
          type="text"
          placeholder="Alex Rivera"
          :disabled="loading"
          class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50 bg-surface-container-lowest text-[16px] font-medium transition-colors focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center text-outline">
          <Icon name="person" size="sm" />
        </div>
      </div>
      <p v-if="errors.name" class="text-[14px] text-error">{{ errors.name }}</p>
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
            role === 'student'
              ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)] text-text-primary'
              : 'text-neutral-gray hover:text-text-primary cursor-pointer'
          ]"
          @click="role = 'student'"
        >
          <Icon name="school" size="sm" />
          <span>Student</span>
        </button>
        <button
          type="button"
          :class="[
            'flex-1 py-md flex items-center justify-center gap-2 text-[16px] font-semibold rounded-lg transition-all duration-200',
            role === 'mentor'
              ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)] text-text-primary'
              : 'text-neutral-gray hover:text-text-primary cursor-pointer'
          ]"
          @click="role = 'mentor'"
        >
          <Icon name="star" size="sm" />
          <span>Mentor</span>
        </button>
      </div>
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="w-full bg-primary-container cursor-pointer text-white py-md px-lg rounded-xl text-[16px] font-semibold shadow-[0_4px_24px_rgba(113,50,245,0.2)] hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
    >
      {{ loading ? 'Signing up...' : 'Sign Up' }}
    </button>
  </form>
</template>

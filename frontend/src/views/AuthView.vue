<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials, SignUpData } from '@/types/auth'
import LoginForm from '@/components/features/LoginForm.vue'
import SignUpForm from '@/components/features/SignUpForm.vue'

const authStore = useAuthStore()
const activeTab = ref<'login' | 'signup'>('signup')

const handleLogin = async (credentials: LoginCredentials) => {
  try {
    await authStore.login(credentials)
  } catch (error) {
    console.error('Login error:', error)
  }
}

const handleSignUp = async (data: SignUpData) => {
  try {
    await authStore.signUp(data)
  } catch (error) {
    console.error('Sign up error:', error)
  }
}
</script>

<template>
  <main class="min-h-screen flex flex-col md:flex-row overflow-hidden bg-surface-white">
    <!-- Left: Dark background with gradient -->
    <section class="hidden md:flex w-1/2 bg-slate-950 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-[#7132f5]/20 to-transparent" />
    </section>

    <!-- Right: Auth form -->
    <section class="flex-1 bg-surface-white flex flex-col justify-center items-center p-gutter lg:p-xl relative">

      <div class="w-full max-w-md space-y-lg">
        <!-- Header -->
        <div class="text-center md:text-left">
          <h1 class="text-[28px] md:text-[48px] font-bold text-text-primary tracking-tighter mb-sm">
            Welcome to Kanban
          </h1>
          <p class="text-[16px] text-text-secondary">
            Simple and minimalistic kanban for beginners
          </p>
        </div>

        <!-- Toggle: Sign Up / Log In -->
        <div class="bg-surface-container-low p-xs rounded-xl flex">
          <button
            :class="[
              'flex-1 py-md text-center text-[16px] font-semibold rounded-lg transition-all duration-200',
              activeTab === 'signup'
                ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)] text-text-primary'
                : 'text-neutral-gray hover:text-text-primary'
            ]"
            @click="activeTab = 'signup'"
          >
            Sign Up
          </button>
          <button
            :class="[
              'flex-1 py-md text-center text-[16px] font-semibold rounded-lg transition-all duration-200',
              activeTab === 'login'
                ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)] text-text-primary'
                : 'text-neutral-gray hover:text-text-primary'
            ]"
            @click="activeTab = 'login'"
          >
            Log In
          </button>
        </div>

        <!-- Forms -->
        <SignUpForm
          v-if="activeTab === 'signup'"
          :loading="authStore.loading"
          @submit="handleSignUp"
        />
        <LoginForm
          v-else
          :loading="authStore.loading"
          @submit="handleLogin"
        />

        <p v-if="authStore.error" class="text-[14px] text-error text-center">
          {{ authStore.error }}
        </p>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'

type TabType = 'login' | 'signup'

const activeTab = ref<TabType>('login')

const setTab = (tab: TabType) => {
  activeTab.value = tab
}
</script>

<template>
  <div class="w-full">
    <div class="flex gap-8 mb-10">
      <button
        :class="[
          'text-[18px] font-semibold transition-colors pb-2 border-b-2',
          activeTab === 'login'
            ? 'text-primary border-primary'
            : 'text-text-secondary border-transparent hover:text-on-surface',
        ]"
        @click="setTab('login')"
      >
        Login
      </button>
      <button
        :class="[
          'text-[18px] font-semibold transition-colors pb-2 border-b-2',
          activeTab === 'signup'
            ? 'text-primary border-primary'
            : 'text-text-secondary border-transparent hover:text-on-surface',
        ]"
        @click="setTab('signup')"
      >
        Sign Up
      </button>
    </div>

    <div>
      <slot v-if="activeTab === 'login'" name="login" />
      <slot v-else name="signup" />
    </div>
  </div>
</template>

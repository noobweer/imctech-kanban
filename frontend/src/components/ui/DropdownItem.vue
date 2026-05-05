<script setup lang="ts">
import Icon from './Icon.vue'

interface Props {
  variant?: 'default' | 'danger'
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})
</script>

<template>
  <button
    :class="[
      'w-full flex items-center gap-3 px-4 py-3 text-left text-sm font-medium transition-all duration-150',
      variant === 'danger'
        ? 'text-error hover:bg-red-50'
        : 'text-text-primary hover:bg-gray-100',
    ]"
  >
    <Icon v-if="icon" :name="icon" size="sm" />
    <slot />
  </button>
</template>

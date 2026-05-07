<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'outlined' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  type: 'button',
})

const variantClasses = {
  primary: 'bg-primary-container text-white shadow-sm',
  secondary: 'bg-secondary text-on-secondary',
  outlined: 'bg-transparent border-[1px] border-primary text-primary',
  ghost: 'bg-transparent text-primary',
}

const variantHoverClasses = {
  primary: 'hover:bg-primary/90',
  secondary: 'hover:bg-secondary/90',
  outlined: 'hover:bg-primary/5',
  ghost: 'hover:bg-primary/10',
}

const sizeClasses = {
  sm: 'px-4 py-2 text-[14px]',
  md: 'px-5 py-3 text-[16px]',
  lg: 'px-6 py-3.5 text-[16px]',
}
</script>

<template>
  <button
    :type="type"
    :class="[
      'rounded-xl font-semibold transition-all cursor-pointer',
      variantClasses[variant],
      sizeClasses[size],
      !disabled && variantHoverClasses[variant],
      disabled && 'opacity-50 cursor-not-allowed',
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

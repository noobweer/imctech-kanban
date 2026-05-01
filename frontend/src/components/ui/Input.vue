<script setup lang="ts">
interface Props {
  type?: 'text' | 'email' | 'password' | 'number'
  placeholder?: string
  modelValue?: string
  error?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  modelValue: '',
  error: '',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="w-full">
    <div class="relative">
      <div v-if="$slots.icon" class="absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary">
        <slot name="icon" />
      </div>
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="[
          'w-full px-4 py-3.5 rounded-lg border transition-colors text-[16px]',
          'text-on-surface placeholder:text-text-secondary',
          'focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20',
          error ? 'border-error' : 'border-border-gray',
          disabled && 'opacity-50 cursor-not-allowed',
          $slots.icon && 'pl-12',
        ]"
        @input="handleInput"
      />
    </div>
    <p v-if="error" class="mt-2 text-[14px] text-error">
      {{ error }}
    </p>
  </div>
</template>

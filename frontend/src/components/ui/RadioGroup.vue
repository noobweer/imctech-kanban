<script setup lang="ts">
export interface RadioOption {
  value: string
  label: string
  icon?: string
}

interface Props {
  options: RadioOption[]
  modelValue?: string
  name: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleChange = (value: string) => {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="space-y-3">
    <label
      v-for="option in options"
      :key="option.value"
      :class="[
        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors',
        modelValue === option.value
          ? 'border-primary bg-primary/5'
          : 'border-border-gray hover:border-outline',
      ]"
    >
      <input
        :type="'radio'"
        :name="name"
        :value="option.value"
        :checked="modelValue === option.value"
        class="w-5 h-5 text-primary focus:ring-primary"
        @change="handleChange(option.value)"
      />
      <slot name="option" :option="option">
        <div class="flex items-center gap-2">
          <slot name="icon" :option="option" />
          <span class="text-body text-on-surface">{{ option.label }}</span>
        </div>
      </slot>
    </label>
  </div>
</template>

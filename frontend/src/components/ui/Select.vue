<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string | number
  options: { label: string; value: string | number }[]
  placeholder?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const isOpen = ref(false)
const selectRef = ref<HTMLElement | null>(null)

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === props.modelValue)
})

function toggleOpen() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

function selectOption(value: string | number) {
  emit('update:modelValue', value)
  isOpen.value = false
}

// Close when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="relative w-full min-w-[140px]" ref="selectRef">
    <button
      type="button"
      class="flex items-center justify-between w-full px-4 py-2 bg-white border rounded-[12px] text-sm font-semibold transition-all duration-200 outline-none"
      :class="[
        isOpen
          ? 'border-[var(--color-primary-container)] ring-2 ring-[var(--color-primary-container)]/20 shadow-sm'
          : 'border-border-gray hover:border-[var(--color-primary-container)]/50',
        disabled
          ? 'opacity-50 cursor-not-allowed bg-surface-container-lowest'
          : 'cursor-pointer shadow-[0_4px_24px_rgba(0,0,0,0.03)] hover:shadow-[0_4px_24px_rgba(0,0,0,0.06)]',
      ]"
      @click="toggleOpen"
      :disabled="disabled"
    >
      <span :class="selectedOption ? 'text-[#101114]' : 'text-neutral-gray'">
        {{ selectedOption ? selectedOption.label : placeholder || 'Select option' }}
      </span>
      <ChevronDown
        :size="16"
        class="text-neutral-gray transition-transform duration-300"
        :class="{ 'rotate-180 text-[var(--color-primary-container)]': isOpen }"
      />
    </button>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-y-95 opacity-0 -translate-y-2"
      enter-to-class="transform scale-y-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-y-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-y-95 opacity-0 -translate-y-2"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 w-full mt-2 bg-white border border-border-gray rounded-[12px] shadow-[0_4px_24px_rgba(0,0,0,0.08)] py-1.5 origin-top overflow-hidden"
      >
        <button
          v-for="option in options"
          :key="option.value"
          type="button"
          class="flex items-center justify-between w-full px-4 py-2.5 text-sm transition-colors duration-150 group"
          :class="[
            modelValue === option.value
              ? 'bg-[var(--color-primary-container)]/5 text-[var(--color-primary-container)] font-bold'
              : 'text-[#101114] hover:bg-surface-container-low font-medium',
          ]"
          @click="selectOption(option.value)"
        >
          {{ option.label }}
          <div
            class="transition-transform duration-200"
            :class="
              modelValue === option.value
                ? 'scale-100 opacity-100'
                : 'scale-0 opacity-0 absolute right-4'
            "
          >
            <Check :size="16" class="text-[var(--color-primary-container)]" />
          </div>
        </button>
      </div>
    </Transition>
  </div>
</template>

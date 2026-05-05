<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Props {
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right'
  offset?: number
}

const props = withDefaults(defineProps<Props>(), {
  position: 'bottom-right',
  offset: 8,
})

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

function toggle() {
  isOpen.value = !isOpen.value
}

function close() {
  isOpen.value = false
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

defineExpose({ close })
</script>

<template>
  <div ref="dropdownRef" class="relative inline-block">
    <div @click="toggle">
      <slot name="trigger" />
    </div>

    <Transition
      enter-active-class="transition-all duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition-all duration-100 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="isOpen"
        :class="[
          'absolute z-50 min-w-[200px] bg-white border border-border-gray rounded-xl shadow-[0_4px_24px_rgba(0,0,0,0.03)] py-2',
          {
            'right-0 top-full': position === 'bottom-right',
            'left-0 top-full': position === 'bottom-left',
            'right-0 bottom-full': position === 'top-right',
            'left-0 bottom-full': position === 'top-left',
          },
        ]"
        :style="{ marginTop: position.startsWith('bottom') ? `${offset}px` : undefined, marginBottom: position.startsWith('top') ? `${offset}px` : undefined }"
        @click="close"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>

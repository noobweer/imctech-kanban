<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  title?: string
  maxWidth?: string
  closeOnBackdrop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxWidth: '500px',
  closeOnBackdrop: true,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function close() {
  emit('update:modelValue', false)
}

function handleBackdropClick() {
  if (props.closeOnBackdrop) {
    close()
  }
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.modelValue) {
    close()
  }
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  },
)

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition
      appear
      enter-active-class="transition-opacity duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40"
        @click.self="handleBackdropClick"
      >
        <Transition appear name="t-modal">
          <div
            v-if="modelValue"
            class="bg-white rounded-xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] w-full max-h-[90vh] flex flex-col"
            :style="{ maxWidth }"
          >
            <!-- Header -->
            <div
              v-if="title || $slots.header"
              class="flex items-center justify-between p-4 md:p-6 border-b border-border-gray shrink-0"
            >
              <slot name="header">
                <h2 class="text-xl font-semibold text-text-primary">{{ title }}</h2>
              </slot>
              <button
                class="text-neutral-gray hover:text-text-primary transition-colors p-1 rounded-lg bg-white hover:bg-gray-100 cursor-pointer"
                @click="close"
              >
                <X :size="20" />
              </button>
            </div>

            <!-- Body -->
            <div class="p-4 md:p-6 overflow-y-auto custom-scrollbar flex-1 min-h-0">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="p-4 md:p-6 border-t border-border-gray shrink-0">
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

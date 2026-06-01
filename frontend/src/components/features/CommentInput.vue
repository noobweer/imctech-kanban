<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { SendHorizontal } from 'lucide-vue-next'

const emit = defineEmits<{
  submit: [text: string]
}>()

defineProps<{
  disabled?: boolean
}>()

const text = ref('')
const isShaking = ref(false)
const inputWrapRef = ref<HTMLElement | null>(null)

function handleSubmit() {
  if (isShaking.value) return
  
  const content = text.value.trim()
  if (!content) {
    isShaking.value = true
    
    // Auto-revert shake class to allow replay
    setTimeout(() => {
      isShaking.value = false
    }, 140) // var(--shake-dur-a)*2 + var(--shake-dur-b)*2 = 280, wait half or just enough to feel it
    return
  }
  
  emit('submit', content)
  text.value = ''
}
</script>

<template>
  <div class="p-3 bg-surface-container-lowest border-t border-border-gray sticky bottom-0 z-10 w-full">
    <div 
      ref="inputWrapRef"
      class="relative bg-white rounded-xl border border-border-gray t-input transition-all duration-200 focus-within:border-[#5800d8] focus-within:ring-2 focus-within:ring-[#5800d8]/20 outline-none"
      :class="{ 'is-shaking border-error focus-within:border-error focus-within:ring-error/20': isShaking }"
    >
      <textarea
        v-model="text"
        rows="1"
        placeholder="Write a comment..."
        :disabled="disabled"
        class="w-full bg-transparent outline-none focus:outline-none p-3 pr-12 text-on-surface text-[15px] resize-y min-h-[48px] max-h-[150px] custom-scrollbar disabled:opacity-50 disabled:cursor-not-allowed"
        @keydown.enter.exact.prevent="handleSubmit"
      ></textarea>
      
      <button
        @click="handleSubmit"
        :disabled="disabled || !text.trim()"
        class="absolute right-2 bottom-2 w-8 h-8 rounded-lg flex items-center justify-center text-primary-container hover:bg-primary-container/10 transition-all active:scale-95 disabled:opacity-30 disabled:hover:bg-transparent disabled:cursor-not-allowed disabled:active:scale-100"
      >
        <SendHorizontal :size="18" />
      </button>
    </div>
  </div>
</template>

<style scoped>
textarea {
  font-family: inherit;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 10px;
}
</style>

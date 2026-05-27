<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'
import { Type, List } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const content = ref(props.modelValue)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const activeFormats = ref<string[]>(['normal'])

watch(() => props.modelValue, (newVal) => {
  if (content.value !== newVal) {
    content.value = newVal
  }
})

watch(content, (newVal) => {
  emit('update:modelValue', newVal)
  updateActiveFormat()
})

type MarkdownAction = 'h1' | 'h2' | 'h3' | 'bold' | 'list' | 'normal'

const textActions: { action: MarkdownAction, label: string }[] = [
  { action: 'h1', label: 'H1' },
  { action: 'h2', label: 'H2' },
  { action: 'h3', label: 'H3' },
]

function updateActiveFormat() {
  if (!textareaRef.value) return
  const text = content.value
  const start = textareaRef.value.selectionStart
  
  let lineStart = start
  while (lineStart > 0 && text[lineStart - 1] !== '\n') lineStart--
  let lineEnd = start
  while (lineEnd < text.length && text[lineEnd] !== '\n') lineEnd++
  
  const currentLine = text.slice(lineStart, lineEnd)
  const formats: string[] = []
  
  if (currentLine.startsWith('# ')) formats.push('h1')
  else if (currentLine.startsWith('## ')) formats.push('h2')
  else if (currentLine.startsWith('### ')) formats.push('h3')
  else if (currentLine.startsWith('- ')) formats.push('list')
  else formats.push('normal')
  
  activeFormats.value = formats
}

function applyMarkdown(action: MarkdownAction) {
  if (!textareaRef.value) return
  
  const textarea = textareaRef.value
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = content.value

  // For Bold (wrap selected text)
  if (action === 'bold') {
    const selected = text.slice(start, end)
    const before = text.slice(0, start)
    const after = text.slice(end)
    
    content.value = `${before}**${selected}**${after}`
    
    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(start + 2, start + 2 + selected.length)
      updateActiveFormat()
    })
    return
  }

  // For Line-based formatting (H1, H2, H3, list, normal)
  let lineStart = start
  while (lineStart > 0 && text[lineStart - 1] !== '\n') lineStart--
  
  let lineEnd = end
  while (lineEnd < text.length && text[lineEnd] !== '\n') lineEnd++

  const currentLine = text.slice(lineStart, lineEnd)
  const beforeLine = text.slice(0, lineStart)
  const afterLine = text.slice(lineEnd)

  const cleanLine = currentLine.replace(/^(### |## |# |- )/, '')
  let prefix = ''
  if (action === 'h1') prefix = '# '
  if (action === 'h2') prefix = '## '
  if (action === 'h3') prefix = '### '
  if (action === 'list') prefix = '- '

  const newLine = prefix + cleanLine
  content.value = beforeLine + newLine + afterLine

  const cursorOffset = newLine.length - currentLine.length
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + cursorOffset, end + cursorOffset)
    updateActiveFormat()
  })
}

onMounted(() => {
  // Initialize formatting state if there's pre-filled content
  if (content.value) {
    nextTick(updateActiveFormat)
  }
})
</script>

<template>
  <div class="border border-border-gray rounded-xl overflow-hidden flex flex-col flex-grow bg-white transition-all">
    <div class="flex items-center gap-2 px-3 py-2 border-b border-border-gray bg-surface-container-lowest overflow-x-auto">
      <div class="flex items-center gap-1 border-r border-border-gray pr-2 mr-1">
        <button 
          :class="[
            'font-semibold rounded-lg transition-colors flex items-center justify-center shrink-0 px-2.5 py-1 text-[13px] cursor-pointer active:scale-95',
            activeFormats.includes('normal') ? 'bg-purple-subtle text-primary-container' : 'text-on-surface-variant hover:bg-surface-container hover:text-text-primary'
          ]"
          type="button" 
          @click.prevent="applyMarkdown('normal')" 
          title="Normal text"
        >
          <Type :size="16" />
        </button>
        <button 
          v-for="btn in textActions" 
          :key="btn.action"
          :class="[
            'font-semibold rounded-lg transition-colors flex items-center justify-center shrink-0 px-2.5 py-1 text-[13px] cursor-pointer active:scale-95',
            activeFormats.includes(btn.action) ? 'bg-purple-subtle text-primary-container' : 'text-on-surface-variant hover:bg-surface-container hover:text-text-primary'
          ]"
          type="button" 
          @click.prevent="applyMarkdown(btn.action)"
        >
          {{ btn.label }}
        </button>
      </div>
      <div class="flex items-center gap-1">
        <button 
          class="font-semibold text-on-surface-variant hover:bg-surface-container hover:text-text-primary rounded-lg transition-colors flex items-center justify-center shrink-0 w-8 h-8 font-bold cursor-pointer active:scale-95" 
          type="button" 
          @click.prevent="applyMarkdown('bold')"
        >B</button>
        <button 
          :class="[
            'font-semibold rounded-lg transition-colors flex items-center justify-center shrink-0 w-8 h-8 cursor-pointer active:scale-95',
            activeFormats.includes('list') ? 'bg-purple-subtle text-primary-container' : 'text-on-surface-variant hover:bg-surface-container hover:text-text-primary'
          ]"
          type="button" 
          @click.prevent="applyMarkdown('list')"
        >
          <List :size="20" />
        </button>
      </div>
    </div>
    <textarea
      ref="textareaRef"
      v-model="content"
      class="w-full p-4 text-on-surface placeholder:text-text-secondary focus:outline-none flex-grow min-h-[220px] text-base resize-none custom-scrollbar"
      :placeholder="placeholder || 'Describe the details...'"
      @keyup="updateActiveFormat"
      @click="updateActiveFormat"
      @focus="updateActiveFormat"
    ></textarea>
  </div>
</template>

<style scoped>
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

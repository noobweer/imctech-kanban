<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, GripVertical, ChevronUp, ChevronDown } from 'lucide-vue-next'
import type { ChecklistItem } from '@/types/task'

const props = defineProps<{
  modelValue: ChecklistItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ChecklistItem[]]
}>()

const items = ref<ChecklistItem[]>(JSON.parse(JSON.stringify(props.modelValue)))
const draggedIndex = ref<number | null>(null)
const dropTargetIndex = ref<number | null>(null)

let isLocalUpdate = false

watch(() => props.modelValue, (newVal) => {
  if (isLocalUpdate) return
  items.value = JSON.parse(JSON.stringify(newVal))
}, { deep: true })

watch(items, (newVal) => {
  isLocalUpdate = true
  emit('update:modelValue', newVal)
  // use setTimeout or promise to reset after emit is processed
  Promise.resolve().then(() => {
    isLocalUpdate = false
  })
}, { deep: true })

function addItem() {
  items.value.push({ title: '', is_done: false })
}

function removeItem(index: number) {
  items.value.splice(index, 1)
}

function moveItemUp(index: number) {
  if (index > 0) {
    const temp = items.value[index]
    items.value[index] = items.value[index - 1]
    items.value[index - 1] = temp
  }
}

function moveItemDown(index: number) {
  if (index < items.value.length - 1) {
    const temp = items.value[index]
    items.value[index] = items.value[index + 1]
    items.value[index + 1] = temp
  }
}

function handleDragStart(index: number) {
  draggedIndex.value = index
}

function handleDragOver(event: DragEvent, index: number) {
  event.preventDefault()
  dropTargetIndex.value = index
}

function handleDrop(event: DragEvent, targetIndex: number) {
  event.preventDefault()
  if (draggedIndex.value === null || draggedIndex.value === targetIndex) return

  const [removed] = items.value.splice(draggedIndex.value, 1)
  items.value.splice(targetIndex, 0, removed)
  
  draggedIndex.value = null
  dropTargetIndex.value = null
}

function handleDragEnd() {
  draggedIndex.value = null
  dropTargetIndex.value = null
}
</script>

<template>
  <div class="border border-border-gray rounded-xl p-6 flex flex-col flex-grow bg-white">
    <div class="flex-grow space-y-3 mb-4 max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
      <div v-if="items.length === 0" class="text-sm text-text-secondary italic">No items added. Click below to add one.</div>
      
      <div 
        v-for="(item, index) in items" 
        :key="index" 
        draggable="true"
        :class="[
          'flex items-center gap-2 md:gap-3 group bg-white border rounded-lg p-2 transition-all',
          draggedIndex === index ? 'opacity-40 border-border-gray' : 'border-transparent hover:border-border-gray hover:shadow-card',
          dropTargetIndex === index && draggedIndex !== index ? 'border-primary-container border-t-2 shadow-lg' : ''
        ]"
        @dragstart="handleDragStart(index)"
        @dragover="handleDragOver($event, index)"
        @drop="handleDrop($event, index)"
        @dragend="handleDragEnd"
      >
        <div class="hidden md:block cursor-grab active:cursor-grabbing text-neutral-gray opacity-40 hover:opacity-100 transition-opacity">
          <GripVertical :size="16" />
        </div>
        
        <input
          v-model="item.is_done"
          class="w-5 h-5 rounded border-border-gray text-primary focus:ring-primary-container transition-all cursor-pointer shrink-0"
          type="checkbox"
        />
        <input 
          v-model="item.title"
          class="text-sm font-medium text-on-surface focus:outline-none bg-transparent flex-1 min-w-0 placeholder:text-neutral-gray/50"
          placeholder="What needs to be done?"
        />
        
        <div class="flex items-center gap-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity shrink-0">
          <button 
            type="button" 
            class="md:hidden text-text-secondary hover:text-primary-container p-1 bg-surface-container-low hover:bg-purple-subtle rounded-md cursor-pointer disabled:opacity-30"
            @click="moveItemUp(index)"
            :disabled="index === 0"
            title="Move up"
          >
            <ChevronUp :size="16" />
          </button>
          <button 
            type="button" 
            class="md:hidden text-text-secondary hover:text-primary-container p-1 bg-surface-container-low hover:bg-purple-subtle rounded-md cursor-pointer disabled:opacity-30"
            @click="moveItemDown(index)"
            :disabled="index === items.length - 1"
            title="Move down"
          >
            <ChevronDown :size="16" />
          </button>
          <button 
            type="button" 
            class="text-text-secondary hover:text-error p-1 bg-surface-container-low hover:bg-error/10 rounded-md cursor-pointer"
            @click="removeItem(index)"
            title="Remove item"
          >
            ×
          </button>
        </div>
      </div>
    </div>
    
    <div class="pt-4 mt-auto border-t border-border-gray border-dashed shrink-0">
      <button
        class="flex items-center gap-2 text-primary font-button text-sm hover:opacity-80 transition-opacity px-2 py-1 rounded-lg hover:bg-surface-container-low cursor-pointer"
        type="button"
        @click="addItem"
      >
        <Plus :size="18" />
        Add Item
      </button>
    </div>
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

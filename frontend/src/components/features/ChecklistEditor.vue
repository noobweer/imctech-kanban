<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus } from 'lucide-vue-next'
import type { ChecklistItem } from '@/types/task'

const props = defineProps<{
  modelValue: ChecklistItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ChecklistItem[]]
}>()

const items = ref<ChecklistItem[]>(JSON.parse(JSON.stringify(props.modelValue)))

watch(() => props.modelValue, (newVal) => {
  // Simple check to avoid circular updates, though deep watcher covers it mostly
  items.value = JSON.parse(JSON.stringify(newVal))
}, { deep: true })

watch(items, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

function addItem() {
  items.value.push({ title: 'New Item', is_done: false })
}

function removeItem(index: number) {
  items.value.splice(index, 1)
}
</script>

<template>
  <div class="border border-border-gray rounded-xl p-6 flex flex-col flex-grow bg-white">
    <div class="flex-grow space-y-4 mb-4 max-h-[220px] overflow-y-auto custom-scrollbar pr-2">
      <div v-if="items.length === 0" class="text-sm text-text-secondary italic">No items added</div>
      
      <div v-for="(item, index) in items" :key="index" class="flex items-center gap-3 group">
        <input
          v-model="item.is_done"
          class="w-5 h-5 rounded border-border-gray text-primary focus:ring-primary-container transition-all cursor-pointer shrink-0"
          type="checkbox"
        />
        <input 
          v-model="item.title"
          class="text-base text-on-surface group-hover:text-primary transition-colors focus:outline-none border-b border-transparent focus:border-primary-container bg-transparent flex-1 min-w-0"
          placeholder="Item title"
        />
        <button 
          type="button" 
          class="text-text-secondary hover:text-error opacity-0 group-hover:opacity-100 transition-opacity text-xl leading-none px-2 shrink-0"
          @click="removeItem(index)"
          title="Remove item"
        >
          ×
        </button>
      </div>
    </div>
    <div class="pt-6 mt-auto border-t border-border-gray border-dashed shrink-0">
      <button
        class="flex items-center gap-2 text-primary font-button text-sm hover:opacity-80 transition-opacity"
        type="button"
        @click="addItem"
      >
        <Plus :size="20" />
        Add item
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

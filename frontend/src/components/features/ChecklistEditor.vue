<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Plus, GripVertical, Check } from 'lucide-vue-next'
import draggable from 'vuedraggable'
import type { ChecklistItem, Task } from '@/types/task'
import { useTasksStore } from '@/stores/tasks'

const props = defineProps<{
  modelValue: ChecklistItem[]
  task?: Task | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ChecklistItem[]]
}>()

const tasksStore = useTasksStore()
const items = ref<ChecklistItem[]>(JSON.parse(JSON.stringify(props.modelValue)))
let isLocalUpdate = false

watch(() => props.modelValue, (newVal) => {
  if (isLocalUpdate) return
  items.value = JSON.parse(JSON.stringify(newVal))
}, { deep: true })

watch(items, (newVal) => {
  isLocalUpdate = true
  emit('update:modelValue', newVal)
  Promise.resolve().then(() => {
    isLocalUpdate = false
  })
}, { deep: true })


async function addItem() {
  if (props.task) {
    await tasksStore.addChecklistItem(props.task.id, 'New Item')
    // Store updates task, parent will pass down new items via modelValue watcher
  } else {
    items.value.push({ title: 'New Item', is_done: false })
  }
}

async function removeItem(index: number, item: ChecklistItem) {
  if (props.task && item.id) {
    await tasksStore.deleteChecklistItem(props.task.id, item.id)
  } else {
    items.value.splice(index, 1)
  }
}

async function handleToggle(index: number, item: ChecklistItem) {
  if (props.task && item.id) {
    await tasksStore.toggleChecklistItem(props.task.id, item.id)
  }
}

async function handleTitleChange(item: ChecklistItem) {
  if (props.task && item.id) {
    await tasksStore.updateChecklistItem(props.task.id, item.id, { title: item.title })
  }
}

async function handleDragEnd() {
  if (props.task) {
    const orderedIds = items.value.map(i => i.id).filter(Boolean) as string[]
    await tasksStore.reorderChecklist(props.task.id, orderedIds)
  }
}
</script>

<template>
  <div class="border border-border-gray rounded-xl p-6 flex flex-col flex-grow bg-white">
    <div class="flex-grow space-y-3 mb-4 max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
      <div v-if="items.length === 0" class="text-sm text-text-secondary italic">No items added. Click below to add one.</div>
      
      <draggable 
        v-model="items" 
        group="checklist" 
        handle=".drag-handle"
        item-key="id"
        ghost-class="opacity-40"
        @end="handleDragEnd"
        class="space-y-3"
      >
        <template #item="{ element: item, index }">
          <div class="flex items-center gap-2 md:gap-3 group bg-white border border-transparent hover:border-border-gray hover:shadow-card rounded-lg p-2 transition-all">
            <div class="drag-handle cursor-grab active:cursor-grabbing text-neutral-gray opacity-40 hover:opacity-100 transition-opacity">
              <GripVertical :size="16" />
            </div>
            
            <div class="relative w-5 h-5 flex items-center justify-center shrink-0">
              <input
                v-model="item.is_done"
                class="w-5 h-5 rounded border-border-gray text-primary focus:ring-primary-container transition-all cursor-pointer peer"
                type="checkbox"
                @change="handleToggle(index, item)"
              />
            </div>

            <input 
              v-model="item.title"
              class="text-sm font-medium focus:outline-none bg-transparent flex-1 min-w-0 placeholder:text-neutral-gray/50 transition-colors"
              :class="item.is_done ? 'text-text-secondary line-through' : 'text-on-surface'"
              placeholder="What needs to be done?"
              @blur="handleTitleChange(item)"
              @keyup.enter="handleTitleChange(item)"
            />
            
            <button 
              type="button" 
              class="text-text-secondary hover:text-error p-1 bg-surface-container-low hover:bg-error/10 rounded-md cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity"
              @click="removeItem(index, item)"
              title="Remove item"
            >
              ×
            </button>
          </div>
        </template>
      </draggable>
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

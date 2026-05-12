<script setup lang="ts">
import { ref } from 'vue'
import type { Column } from '@/types/column'
import Button from '@/components/ui/Button.vue'
import Icon from '@/components/ui/Icon.vue'
import Input from '@/components/ui/Input.vue'

const props = defineProps<{
  column: Column
  isFirst: boolean
  isLast: boolean
}>()

const emit = defineEmits<{
  (e: 'move-left', id: string): void
  (e: 'move-right', id: string): void
  (e: 'rename', id: string, name: string): void
  (e: 'archive', id: string): void
}>()

const isEditing = ref(false)
const editedName = ref(props.column.name)

function startEditing() {
  editedName.ref = props.column.name
  isEditing.value = true
}

function handleRename() {
  if (editedName.value.trim() && editedName.value !== props.column.name) {
    emit('rename', props.column.id, editedName.value.trim())
  }
  isEditing.value = false
}
</script>

<template>
  <div class="flex flex-col bg-gray-50 rounded-lg w-72 min-h-[400px] border border-gray-200">
    <div class="p-3 flex items-center justify-between group">
      <div v-if="!isEditing" class="flex items-center gap-2 flex-1 min-w-0">
        <h3 class="font-semibold text-gray-900 truncate" @click="startEditing">{{ column.name }}</h3>
        <span class="text-xs text-gray-400 bg-gray-200 px-1.5 py-0.5 rounded-full">{{ column.sum_tasks }}</span>
      </div>
      <div v-else class="flex-1 min-w-0">
        <Input 
          v-model="editedName" 
          size="sm" 
          auto-focus 
          @blur="handleRename" 
          @keyup.enter="handleRename"
          @keyup.esc="isEditing = false"
        />
      </div>

      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          v-if="!isFirst" 
          class="p-1 hover:bg-gray-200 rounded transition-colors text-gray-500"
          title="Move left"
          @click="emit('move-left', column.id)"
        >
          <Icon name="chevron-left" size="14" />
        </button>
        <button 
          v-if="!isLast" 
          class="p-1 hover:bg-gray-200 rounded transition-colors text-gray-500"
          title="Move right"
          @click="emit('move-right', column.id)"
        >
          <Icon name="chevron-right" size="14" />
        </button>
        <button 
          class="p-1 hover:bg-red-100 hover:text-red-600 rounded transition-colors text-gray-500"
          title="Archive column"
          @click="emit('archive', column.id)"
        >
          <Icon name="archive" size="14" />
        </button>
      </div>
    </div>

    <div class="flex-1 p-3 flex flex-col gap-3">
      <!-- Tasks will be rendered here in future tasks -->
      <div class="border-2 border-dashed border-gray-200 rounded-lg p-4 flex flex-col items-center justify-center text-gray-400 text-sm italic">
        No tasks yet
      </div>
    </div>

    <div class="p-2 border-t border-gray-100">
      <Button variant="ghost" size="sm" block class="justify-start gap-2 text-gray-500 font-normal">
        <Icon name="plus" size="14" />
        Add Task
      </Button>
    </div>
  </div>
</template>

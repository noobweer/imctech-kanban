<script setup lang="ts">
import { ref } from 'vue'
import { Plus, MoreVertical, ChevronLeft, ChevronRight, Archive } from 'lucide-vue-next'
import type { Column } from '@/types/column'
import type { Task } from '@/types/task'
import Input from '@/components/ui/Input.vue'
import TaskCard from '@/components/features/TaskCard.vue'
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'

const props = defineProps<{
  column: Column
  tasks?: Task[]
  isFirst: boolean
  isLast: boolean
}>()

const emit = defineEmits<{
  (e: 'move-left', id: string): void
  (e: 'move-right', id: string): void
  (e: 'rename', id: string, name: string): void
  (e: 'archive', id: string): void
  (e: 'add-task', columnId: string): void
}>()

const isEditing = ref(false)
const editedName = ref(props.column.name)

function startEditing() {
  editedName.value = props.column.name
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
  <section class="flex flex-col w-80 min-h-[500px] shrink-0">
    <!-- Column Header -->
    <div class="mb-4 px-1 flex items-center justify-between group/header">
      <div v-if="!isEditing" class="flex items-center gap-2 flex-1 min-w-0">
        <h2 class="font-bold text-gray-700 truncate cursor-pointer" @click="startEditing">
          {{ column.name }}
        </h2>
        <span class="bg-surface-container-high text-xs font-bold px-2 py-0.5 rounded-full text-text-secondary">
          {{ tasks?.length || 0 }}
        </span>
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

      <div class="flex items-center gap-1">
        <!-- Quick Add Task -->
        <button 
          class="p-1 hover:bg-surface-container-high rounded transition-colors text-neutral-gray hover:text-primary-container"
          title="Add task"
          @click="emit('add-task', column.id)"
        >
          <Plus :size="20" />
        </button>

        <!-- Column Actions Menu -->
        <Dropdown position="bottom-right">
          <template #trigger>
            <button class="p-1 hover:bg-surface-container-high rounded transition-colors text-neutral-gray hover:text-primary-container">
              <MoreVertical :size="20" />
            </button>
          </template>
          
          <div class="py-1">
            <DropdownItem v-if="!isFirst" icon="chevron-left" @click="emit('move-left', column.id)">
              Move Left
            </DropdownItem>
            <DropdownItem v-if="!isLast" icon="chevron-right" @click="emit('move-right', column.id)">
              Move Right
            </DropdownItem>
            <div v-if="!isFirst || !isLast" class="my-1 border-t border-border-gray/50"></div>
            <DropdownItem icon="archive" variant="danger" @click="emit('archive', column.id)">
              Archive Column
            </DropdownItem>
          </div>
        </Dropdown>
      </div>
    </div>

    <!-- Task List -->
    <div class="flex-1 flex flex-col gap-3 overflow-y-auto max-h-[calc(100vh-300px)] custom-scrollbar">
      <template v-if="tasks && tasks.length > 0">
        <TaskCard 
          v-for="task in tasks" 
          :key="task.id" 
          :task="task" 
        />
      </template>
      <div 
        v-else 
        class="border-2 border-dashed border-border-gray/50 rounded-xl p-8 flex flex-col items-center justify-center text-text-secondary text-sm italic text-center"
      >
        <Plus :size="24" class="mb-2 opacity-20" />
        No tasks yet
      </div>
    </div>
  </section>
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
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}
</style>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Plus, MoreHorizontal, Pencil, Trash2, MoreVertical } from 'lucide-vue-next'
import draggable from 'vuedraggable'
import type { Column } from '@/types/column'
import type { Task } from '@/types/task'
import Input from '@/components/ui/Input.vue'
import TaskCard from '@/components/features/TaskCard.vue'
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import { useTasksStore } from '@/stores/tasks'

const tasksStore = useTasksStore()

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
  (e: 'clear-tasks', id: string): void
  (e: 'add-task', columnId: string): void
  (e: 'edit-task', task: Task): void
  (e: 'archive-task', task: Task): void
  (e: 'move-task', taskId: string, targetColumnId: string, position: number): void
  (e: 'drag-start'): void
  (e: 'drag-end'): void
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

const localTasks = ref<Task[]>([...(props.tasks || [])])

watch(() => props.tasks, (newTasks) => {
  // Only sync if they are different to prevent layout thrashing
  // vuedraggable handles local array sorting instantly
  if (newTasks) {
    localTasks.value = [...newTasks]
  }
}, { deep: true, immediate: true })

function onTasksChange(evt: any) {
  if (evt.added) {
    const task = evt.added.element
    const position = evt.added.newIndex
    emit('move-task', task.id, props.column.id, position)
  } else if (evt.moved) {
    const task = evt.moved.element
    const position = evt.moved.newIndex
    emit('move-task', task.id, props.column.id, position)
  }
}

function onDragStart() {
  emit('drag-start')
  tasksStore.isDragging = true
}

function onDragEnd() {
  emit('drag-end')
  tasksStore.isDragging = false
}
</script>

<template>
  <section data-no-dragscroll class="flex flex-col w-[280px] md:w-80 min-h-[500px] shrink-0 bg-surface-container-lowest/40 rounded-xl p-2 border border-transparent hover:border-border-gray/50 transition-colors">
    <!-- Column Header -->
    <div class="mb-3 px-2 flex items-center justify-between group/header h-10">
      <div v-if="!isEditing" class="flex items-center gap-2 flex-1 min-w-0">
        <h2 class="font-bold text-on-surface truncate cursor-pointer hover:text-primary transition-colors" @click="startEditing">
          {{ column.name }}
        </h2>
        <span class="bg-surface-container text-xs font-bold px-2 py-0.5 rounded-full text-neutral-gray">
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

      <div class="flex items-center gap-1 opacity-0 group-hover/header:opacity-100 focus-within:opacity-100 transition-opacity">
        <!-- Quick Add Task -->
        <button 
          class="p-1 hover:bg-surface-container rounded transition-colors text-text-secondary hover:text-primary"
          title="Add task"
          @click="emit('add-task', column.id)"
        >
          <Plus :size="18" />
        </button>

        <!-- Column Actions Menu -->
        <Dropdown position="bottom-right">
          <template #trigger>
            <button class="p-1 hover:bg-surface-container rounded transition-colors text-text-secondary hover:text-primary">
              <MoreVertical :size="18" />
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
            <DropdownItem icon="trash" @click="emit('clear-tasks', column.id)">
              Clear Tasks to Archive
            </DropdownItem>
            <DropdownItem icon="archive" variant="danger" @click="emit('archive', column.id)">
              Archive Column
            </DropdownItem>
          </div>
        </Dropdown>
      </div>
    </div>

    <!-- Task List (Draggable) -->
    <draggable
      v-model="localTasks"
      group="tasks"
      item-key="id"
      :animation="200"
      ghost-class="opacity-40"
      drag-class="cursor-grabbing"
      @start="emit('drag-start')"
      @end="emit('drag-end')"
      @change="onTasksChange"
      class="flex-1 flex flex-col gap-3 overflow-y-scroll max-h-[calc(100vh-300px)] custom-scrollbar pb-10 min-h-[100px]"
    >
      <template #item="{ element: task }">
        <TaskCard 
          :task="task"
          @click="emit('edit-task', task)"
          @edit="emit('edit-task', task)"
          @archive="emit('archive-task', task)"
        />
      </template>
      
      <template #footer v-if="!tasks?.length">
        <div class="border-2 border-dashed border-border-gray/50 rounded-xl p-8 flex flex-col items-center justify-center text-text-secondary text-sm italic text-center h-full m-2">
          Drop tasks here
        </div>
      </template>
    </draggable>
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

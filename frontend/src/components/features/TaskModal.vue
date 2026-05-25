<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Plus, ListChecks, Flag, CalendarDays, Users, Check } from 'lucide-vue-next'
import type { TaskIn, TaskUpdateIn, Task, ChecklistItem } from '@/types/task'
import { useBoardsStore } from '@/stores/boards'
import Modal from '@/components/ui/Modal.vue'
import MarkdownEditor from '@/components/features/MarkdownEditor.vue'
import ChecklistEditor from '@/components/features/ChecklistEditor.vue'

const props = defineProps<{
  isOpen: boolean
  task?: Task | null
  boardId?: string
  defaultColumnId?: string
}>()

const boardsStore = useBoardsStore()

const emit = defineEmits<{
  close: []
  save: [data: TaskIn | TaskUpdateIn]
}>()

// Form state
const title = ref('')
const content = ref('')
const priority = ref<number>(1) // 0=Low, 1=Medium, 2=High
const deadline = ref<string>('')
const checklist = ref<ChecklistItem[]>([])
const assignees = ref<string[]>([])
const isAssigneesDropdownOpen = ref(false)
const assigneesDropdownRef = ref<HTMLElement | null>(null)

function closeAssigneesDropdown(e: MouseEvent) {
  if (assigneesDropdownRef.value && !assigneesDropdownRef.value.contains(e.target as Node)) {
    isAssigneesDropdownOpen.value = false
  }
}

function toggleAssignee(username: string) {
  const index = assignees.value.indexOf(username)
  if (index === -1) {
    assignees.value.push(username)
  } else {
    assignees.value.splice(index, 1)
  }
}

// Initialize form when opening
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    if (props.boardId) boardsStore.fetchMembers(props.boardId)

    if (props.task) {
      title.value = props.task.title
      content.value = props.task.content || ''
      priority.value = props.task.priority
      deadline.value = props.task.deadline ? (props.task.deadline.split('T')[0] || '') : ''
      checklist.value = JSON.parse(JSON.stringify(props.task.checklist || []))
      assignees.value = [...(props.task.assignees || [])]
    } else {
      title.value = ''
      content.value = ''
      priority.value = 1
      deadline.value = ''
      checklist.value = []
      assignees.value = []
    }
  } else {
    isAssigneesDropdownOpen.value = false
  }
})

onMounted(() => {
  document.addEventListener('click', closeAssigneesDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeAssigneesDropdown)
})

function handleSave() {
  if (!title.value.trim()) {
    alert('Title is required')
    return
  }

  const data: TaskIn = {
    title: title.value.trim(),
    content: content.value.trim(),
    priority: priority.value,
    deadline: deadline.value ? new Date(deadline.value).toISOString() : null,
    checklist: checklist.value.filter(i => i.title.trim()),
    assignees: assignees.value,
    tags: ['Task']
  }

  if (!props.task && props.defaultColumnId) {
    data.column_id = props.defaultColumnId
  }

  emit('save', data)
}
</script>

<template>
  <Modal
    :model-value="isOpen"
    max-width="1000px"
    @update:model-value="emit('close')"
  >
    <div>
      <header class="mb-10 text-center">
        <h1 class="font-section-heading text-sub-heading text-on-surface mb-2 font-bold">
          {{ task ? 'Edit Task' : 'Create Task' }}
        </h1>
        <p class="font-caption text-text-secondary">
          Define the parameters and objectives for this action item.
        </p>
      </header>

      <form class="space-y-6 md:space-y-10" @submit.prevent="handleSave" id="task-form">
        <!-- Task Title Input -->
        <div class="space-y-3">
          <label class="font-button text-sm text-on-surface-variant block font-bold" for="task-title">
            Task Title
          </label>
          <input
            id="task-title"
            v-model="title"
            class="w-full bg-white border border-border-gray rounded-xl px-4 py-4 text-on-surface placeholder:text-text-secondary focus:ring-2 focus:ring-primary-container focus:border-transparent transition-all outline-none"
            placeholder="e.g. Work on Kanban board"
            type="text"
            required
          />
        </div>

        <!-- Two-Column Middle Section: Description and Checklist -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
          <!-- Rich Text Description (Left) -->
          <div class="space-y-3 flex flex-col">
            <label class="font-button text-sm text-on-surface-variant block font-bold">
              Description
            </label>
            <MarkdownEditor v-model="content" placeholder="Describe the task details..." />
          </div>

          <!-- Checklist (Right) -->
          <div class="space-y-3 flex flex-col">
            <label class="font-button text-sm text-on-surface-variant flex items-center gap-2 font-bold">
              <ListChecks :size="18" />
              Checklist
            </label>
            <ChecklistEditor v-model="checklist" />
          </div>
        </div>

        <!-- Priority and Deadline Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
          <!-- Priority Level -->
          <div class="space-y-3">
            <label class="font-button text-sm text-on-surface-variant flex items-center gap-2 font-bold">
              <Flag :size="18" />
              Priority Level
            </label>
            <div class="flex items-center gap-3">
              <button
                class="flex-1 py-3 px-4 rounded-xl border font-button text-sm transition-colors"
                :class="priority === 0 ? 'bg-primary-container/10 border-primary-container text-primary-container' : 'bg-white border-border-gray text-on-surface-variant hover:border-primary-container hover:text-primary'"
                type="button"
                @click="priority = 0"
              >
                Low
              </button>
              <button
                class="flex-1 py-3 px-4 rounded-xl border font-button text-sm transition-colors"
                :class="priority === 1 ? 'bg-primary-container/10 border-primary-container text-primary-container' : 'bg-white border-border-gray text-on-surface-variant hover:border-primary-container hover:text-primary'"
                type="button"
                @click="priority = 1"
              >
                Medium
              </button>
              <button
                class="flex-1 py-3 px-4 rounded-xl border font-button text-sm transition-colors"
                :class="priority === 2 ? 'bg-error/10 border-error text-error' : 'bg-white border-border-gray text-on-surface-variant hover:border-error hover:text-error'"
                type="button"
                @click="priority = 2"
              >
                High
              </button>
            </div>
          </div>

          <!-- Deadline Picker -->
          <div class="space-y-3">
            <label class="font-button text-sm text-on-surface-variant flex items-center gap-2 font-bold" for="due-date">
              <CalendarDays :size="18" />
              Deadline
            </label>
            <div class="relative">
              <input
                id="due-date"
                v-model="deadline"
                class="w-full bg-white border border-border-gray rounded-xl px-4 py-3 text-on-surface focus:ring-2 focus:ring-primary-container focus:border-transparent transition-all outline-none"
                type="date"
              />
            </div>
          </div>
        </div>

        <!-- Assignees Section -->
        <div class="space-y-3 pb-8">
          <label class="font-button text-sm text-on-surface-variant flex items-center gap-2 font-bold">
            <Users :size="18" />
            Assignees
          </label>
          <div class="flex items-center gap-2 flex-wrap">
            <div
              v-for="username in assignees"
              :key="username"
              class="w-10 h-10 rounded-full bg-primary-container text-white flex items-center justify-center font-bold text-sm shadow-sm"
              :title="boardsStore.members.find(m => m.username === username)?.name || username"
            >
              {{ (boardsStore.members.find(m => m.username === username)?.name || username).charAt(0).toUpperCase() }}
            </div>
            
            <div class="relative" ref="assigneesDropdownRef">
              <button
                type="button"
                class="w-10 h-10 rounded-full border-2 border-dashed border-border-gray flex items-center justify-center text-text-secondary hover:border-primary-container hover:text-primary-container transition-colors"
                @click.stop="isAssigneesDropdownOpen = !isAssigneesDropdownOpen"
              >
                <Plus :size="20" />
              </button>
              
              <Transition name="t-dropdown">
                <div v-if="isAssigneesDropdownOpen" class="absolute bottom-full mb-2 left-0 origin-bottom-left w-64 bg-white border border-border-gray rounded-xl shadow-dropdown z-50 py-2 max-h-60 overflow-y-auto custom-scrollbar">
                  <div v-if="boardsStore.membersLoading" class="px-4 py-3 text-sm text-text-secondary">Loading members...</div>
                  <div v-else-if="boardsStore.members.length === 0" class="px-4 py-3 text-sm text-text-secondary">No members found on this board</div>
                  <button
                    v-else
                    v-for="member in boardsStore.members"
                    :key="member.username"
                    type="button"
                    class="w-full text-left px-4 py-2 hover:bg-surface-container-lowest flex items-center justify-between transition-colors"
                    @click="toggleAssignee(member.username)"
                  >
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center text-xs font-bold">
                        {{ member.name.charAt(0).toUpperCase() }}
                      </div>
                      <span class="text-sm font-medium text-on-surface">{{ member.name }}</span>
                    </div>
                    <Check v-if="assignees.includes(member.username)" :size="18" class="text-primary-container" />
                  </button>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Action Footer via slot -->
    <template #footer>
      <div class="flex items-center justify-end gap-4">
        <button
          class="min-w-[140px] py-[13px] px-8 rounded-xl border border-secondary text-secondary font-button hover:bg-purple-subtle transition-all"
          type="button"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          class="min-w-[140px] py-[13px] px-8 rounded-xl bg-primary-container text-white font-button shadow-card active:scale-[0.98] transition-all hover:bg-purple-deep"
          type="submit"
          form="task-form"
        >
          {{ task ? 'Save Changes' : 'Create Task' }}
        </button>
      </div>
    </template>
  </Modal>
</template>

<style scoped>
.font-section-heading {
  font-family: 'Space Grotesk', sans-serif;
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

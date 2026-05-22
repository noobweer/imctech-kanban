<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Plus, List, ListChecks, Flag, CalendarDays, Type, Users, Check } from 'lucide-vue-next'
import type { TaskIn, TaskUpdateIn, Task, ChecklistItem } from '@/types/task'
import { useBoardsStore } from '@/stores/boards'

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
    document.body.style.overflow = 'hidden'
    if (props.boardId) boardsStore.fetchMembers(props.boardId)

    if (props.task) {
      title.value = props.task.title
      content.value = props.task.content || ''
      priority.value = props.task.priority
      deadline.value = props.task.deadline ? (props.task.deadline.split('T')[0] || '') : ''
      // Deep copy checklist so we don't mutate prop directly before save
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
    document.body.style.overflow = ''
    isAssigneesDropdownOpen.value = false
  }
})

// Keyboard and Backdrop closing
function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
  document.addEventListener('click', closeAssigneesDropdown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('click', closeAssigneesDropdown)
  document.body.style.overflow = ''
})

function addChecklistItem() {
  checklist.value.push({ title: 'New Item', is_done: false })
}

function removeChecklistItem(index: number) {
  checklist.value.splice(index, 1)
}

const textareaRef = ref<HTMLTextAreaElement | null>(null)

function applyMarkdown(action: 'h1' | 'h2' | 'h3' | 'bold' | 'list' | 'normal') {
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
    
    // Move cursor after the inserted markdown
    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(start + 2, start + 2 + selected.length)
    }, 0)
    return
  }

  // For Line-based formatting (H1, H2, H3, list, normal)
  // Find start of current line
  let lineStart = start
  while (lineStart > 0 && text[lineStart - 1] !== '\n') {
    lineStart--
  }
  
  // Find end of current line
  let lineEnd = end
  while (lineEnd < text.length && text[lineEnd] !== '\n') {
    lineEnd++
  }

  const currentLine = text.slice(lineStart, lineEnd)
  const beforeLine = text.slice(0, lineStart)
  const afterLine = text.slice(lineEnd)

  // Remove existing markdown prefixes from the line
  const cleanLine = currentLine.replace(/^(### |## |# |- )/, '')

  let newLine = cleanLine
  let prefix = ''

  if (action === 'h1') prefix = '# '
  if (action === 'h2') prefix = '## '
  if (action === 'h3') prefix = '### '
  if (action === 'list') prefix = '- '
  // if action === 'normal', prefix stays ''

  newLine = prefix + cleanLine

  content.value = beforeLine + newLine + afterLine

  // Adjust cursor
  const cursorOffset = newLine.length - currentLine.length
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + cursorOffset, end + cursorOffset)
  }, 0)
}

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
    tags: ['Task'] // Default tag since UI doesn't have a tag picker yet
  }

  if (!props.task && props.defaultColumnId) {
    data.column_id = props.defaultColumnId
  }

  emit('save', data)
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="isOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 bg-black/40"
        @click.self="emit('close')"
      >
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <!-- Main Form Container -->
        <div v-if="isOpen" class="w-full max-w-[1000px] bg-white rounded-xl shadow-[0px_4px_24px_rgba(0,0,0,0.03)] flex flex-col overflow-hidden border border-border-gray max-h-full overflow-y-auto">
      <div class="p-8 md:p-12">
        <header class="mb-10 text-center">
          <h1 class="font-section-heading text-sub-heading text-on-surface mb-2 font-bold">
            {{ task ? 'Edit Task' : 'Create Task' }}
          </h1>
          <p class="font-caption text-text-secondary">
            Define the parameters and objectives for this action item.
          </p>
        </header>

        <form class="space-y-10" @submit.prevent="handleSave">
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
              <div class="border border-border-gray rounded-xl overflow-hidden flex flex-col flex-grow">
                <div class="flex items-center gap-2 px-3 py-2 border-b border-border-gray bg-surface-container-lowest">
                  <div class="flex items-center gap-1 border-r border-border-gray pr-2 mr-1">
                    <button class="px-2.5 py-1 text-[13px] font-semibold text-on-surface-variant hover:bg-purple-subtle hover:text-primary rounded-lg transition-colors flex items-center justify-center" type="button" @click.prevent="applyMarkdown('normal')" title="Normal text">
                      <Type :size="16" />
                    </button>
                    <button class="px-2.5 py-1 text-[13px] font-semibold text-on-surface-variant hover:bg-purple-subtle hover:text-primary rounded-lg transition-colors" type="button" @click.prevent="applyMarkdown('h1')">H1</button>
                    <button class="px-2.5 py-1 text-[13px] font-semibold text-on-surface-variant hover:bg-purple-subtle hover:text-primary rounded-lg transition-colors" type="button" @click.prevent="applyMarkdown('h2')">H2</button>
                    <button class="px-2.5 py-1 text-[13px] font-semibold text-on-surface-variant hover:bg-purple-subtle hover:text-primary rounded-lg transition-colors" type="button" @click.prevent="applyMarkdown('h3')">H3</button>
                  </div>
                  <div class="flex items-center gap-1">
                    <button class="w-8 h-8 flex items-center justify-center font-bold text-on-surface-variant hover:bg-purple-subtle hover:text-primary rounded-lg transition-colors" type="button" @click.prevent="applyMarkdown('bold')">B</button>
                    <button class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:bg-purple-subtle hover:text-primary rounded-lg transition-colors" type="button" @click.prevent="applyMarkdown('list')">
                      <List :size="20" />
                    </button>
                  </div>
                </div>
                <textarea
                  ref="textareaRef"
                  v-model="content"
                  class="w-full p-4 text-on-surface placeholder:text-text-secondary focus:outline-none flex-grow min-h-[220px] text-base resize-none"
                  placeholder="Describe the task details..."
                ></textarea>
              </div>
            </div>

            <!-- Checklist (Right) -->
            <div class="space-y-3 flex flex-col">
              <label class="font-button text-sm text-on-surface-variant flex items-center gap-2 font-bold">
                <ListChecks :size="18" />
                Checklist
              </label>
              <div class="border border-border-gray rounded-xl p-6 flex flex-col flex-grow bg-white">
                <div class="flex-grow space-y-4 mb-4 max-h-[220px] overflow-y-auto custom-scrollbar">
                  <div v-if="checklist.length === 0" class="text-sm text-text-secondary italic">No items added</div>
                  
                  <div v-for="(item, index) in checklist" :key="index" class="flex items-center gap-3 group">
                    <input
                      v-model="item.is_done"
                      class="w-5 h-5 rounded border-border-gray text-primary focus:ring-primary-container transition-all cursor-pointer"
                      type="checkbox"
                    />
                    <input 
                      v-model="item.title"
                      class="text-base text-on-surface group-hover:text-primary transition-colors focus:outline-none border-b border-transparent focus:border-primary-container bg-transparent flex-1"
                      placeholder="Item title"
                    />
                    <button 
                      type="button" 
                      class="text-text-secondary hover:text-error opacity-0 group-hover:opacity-100 transition-opacity"
                      @click="removeChecklistItem(index)"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <div class="pt-6 mt-auto border-t border-border-gray border-dashed">
                  <button
                    class="flex items-center gap-2 text-primary font-button text-sm hover:opacity-80 transition-opacity"
                    type="button"
                    @click="addChecklistItem"
                  >
                    <Plus :size="20" />
                    Add item
                  </button>
                </div>
              </div>
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
          <div class="space-y-3">
            <label class="font-button text-sm text-on-surface-variant flex items-center gap-2 font-bold">
              <Users :size="18" />
              Assignees
            </label>
            <div class="flex items-center gap-2 flex-wrap">
              <!-- Selected assignees avatars -->
              <div
                v-for="username in assignees"
                :key="username"
                class="w-10 h-10 rounded-full bg-primary-container text-white flex items-center justify-center font-bold text-sm shadow-sm"
                :title="boardsStore.members.find(m => m.username === username)?.name || username"
              >
                {{ (boardsStore.members.find(m => m.username === username)?.name || username).charAt(0).toUpperCase() }}
              </div>
              
              <!-- Add assignee button & dropdown -->
              <div class="relative" ref="assigneesDropdownRef">
                <button
                  type="button"
                  class="w-10 h-10 rounded-full border-2 border-dashed border-border-gray flex items-center justify-center text-text-secondary hover:border-primary-container hover:text-primary-container transition-colors"
                  @click.stop="isAssigneesDropdownOpen = !isAssigneesDropdownOpen"
                >
                  <Plus :size="20" />
                </button>
                
                <Transition
                  enter-active-class="transition-all duration-150 ease-out"
                  enter-from-class="opacity-0 scale-95 -translate-y-1"
                  enter-to-class="opacity-100 scale-100 translate-y-0"
                  leave-active-class="transition-all duration-100 ease-in"
                  leave-from-class="opacity-100 scale-100 translate-y-0"
                  leave-to-class="opacity-0 scale-95 -translate-y-1"
                >
                  <div v-if="isAssigneesDropdownOpen" class="absolute top-full mt-2 left-0 w-64 bg-white border border-border-gray rounded-xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] z-50 py-2 max-h-60 overflow-y-auto custom-scrollbar">
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

          <!-- Action Footer -->
          <div class="flex items-center justify-end gap-4 pt-6 border-t border-border-gray">
            <button
              class="min-w-[140px] py-[13px] px-8 rounded-xl border border-secondary text-secondary font-button hover:bg-purple-subtle transition-all"
              type="button"
              @click="emit('close')"
            >
              Cancel
            </button>
            <button
              class="min-w-[140px] py-[13px] px-8 rounded-xl bg-primary-container text-white font-button shadow-[0px_4px_24px_rgba(0,0,0,0.03)] active:scale-[0.98] transition-all hover:bg-purple-deep"
              type="submit"
            >
              {{ task ? 'Save Changes' : 'Create Task' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    </Transition>
  </div>
  </Transition>
  </Teleport>
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

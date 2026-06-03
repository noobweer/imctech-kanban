<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { Plus, ListChecks, Flag, CalendarDays, Users, Check, AlignLeft, Tag as TagIcon, X } from 'lucide-vue-next'
import type { TaskIn, TaskUpdateIn, Task, ChecklistItem } from '@/types/task'
import { useTasksStore } from '@/stores/tasks'
import { useBoardsStore } from '@/stores/boards'
import { useAuthStore } from '@/stores/auth'
import Modal from '@/components/ui/Modal.vue'
import MarkdownEditor from '@/components/features/MarkdownEditor.vue'
import ChecklistEditor from '@/components/features/ChecklistEditor.vue'
import Button from '@/components/ui/Button.vue'

const props = defineProps<{
  isOpen: boolean
  task?: Task | null
  boardId?: string
  defaultColumnId?: string
}>()

const boardsStore = useBoardsStore()
const tasksStore = useTasksStore()
const authStore = useAuthStore()
const isMentor = computed(() => authStore.user?.role === 'mentor')

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
const tags = ref<string[]>([])
const tagInput = ref('')
const isAssigneesDropdownOpen = ref(false)
const assigneesDropdownRef = ref<HTMLElement | null>(null)
const activeTab = ref<'details' | 'checklist'>('details')

function closeAssigneesDropdown(e: MouseEvent) {
  if (assigneesDropdownRef.value && !assigneesDropdownRef.value.contains(e.target as Node)) {
    isAssigneesDropdownOpen.value = false
  }
}

async function toggleAssignee(username: string) {
  const index = assignees.value.indexOf(username)
  if (index === -1) {
    assignees.value.push(username)
    if (props.task) {
      await tasksStore.assignTask(props.task.id, username)
    }
  } else {
    assignees.value.splice(index, 1)
    if (props.task) {
      await tasksStore.unassignTask(props.task.id, username)
    }
  }
}

function addTag() {
  const val = tagInput.value.trim()
  if (val && !tags.value.includes(val)) {
    tags.value.push(val)
  }
  tagInput.value = ''
}

function removeTag(tag: string) {
  tags.value = tags.value.filter(t => t !== tag)
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
      tags.value = [...(props.task.tags || [])]
    } else {
      title.value = ''
      content.value = ''
      priority.value = 1
      deadline.value = ''
      checklist.value = []
      assignees.value = []
      tags.value = []
    }
    tagInput.value = ''
    activeTab.value = 'details'
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

const isShaking = ref(false)

function handleSave() {
  if (!title.value.trim()) {
    isShaking.value = true
    setTimeout(() => { isShaking.value = false }, 500)
    return
  }

  const data: TaskIn = {
    title: title.value.trim(),
    content: content.value.trim(),
    priority: priority.value,
    deadline: deadline.value ? new Date(deadline.value).toISOString() : null,
    checklist: checklist.value.filter(i => i.title.trim()),
    assignees: assignees.value,
    tags: tags.value
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
    <form @submit.prevent="handleSave" id="task-form" class="flex flex-col md:flex-row gap-6 md:gap-8 min-h-[450px]">
      
      <!-- Left Main Content -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Seamless Title -->
        <div class="mb-6">
          <input
            id="task-title"
            v-model="title"
            class="t-input w-full bg-transparent border-none outline-none font-section-heading text-2xl md:text-3xl font-bold text-on-surface placeholder:text-neutral-gray/50 transition-colors"
            :class="{ 'is-shaking text-error placeholder:text-error/50': isShaking }"
            placeholder="Task Title..."
            type="text"
            :readonly="isMentor"
            required
            autofocus
          />
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-border-gray mb-6 gap-6 shrink-0">
          <button 
            type="button" 
            @click="activeTab = 'details'" 
            :class="[
              'pb-3 font-semibold text-sm transition-all border-b-2 flex items-center gap-2 cursor-pointer', 
              activeTab === 'details' ? 'border-primary-container text-primary-container' : 'border-transparent text-text-secondary hover:text-primary-container'
            ]"
          >
            <AlignLeft :size="16" />
            Details
          </button>
          <button 
            type="button" 
            @click="activeTab = 'checklist'" 
            :class="[
              'pb-3 font-semibold text-sm transition-all border-b-2 flex items-center gap-2 cursor-pointer', 
              activeTab === 'checklist' ? 'border-primary-container text-primary-container' : 'border-transparent text-text-secondary hover:text-primary-container'
            ]"
          >
            <ListChecks :size="16" />
            Checklist
            <span v-if="checklist.length" class="ml-1 px-2 py-0.5 rounded-full bg-surface-container-high text-[10px] text-text-primary">
              {{ checklist.length }}
            </span>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <div v-show="activeTab === 'details'" class="flex-1 flex flex-col h-full animate-in fade-in duration-300">
            <MarkdownEditor v-model="content" placeholder="Add a description to explain the task requirements..." class="flex-1 h-full min-h-[300px]" />
          </div>
          
          <div v-show="activeTab === 'checklist'" class="flex-1 flex flex-col h-full animate-in fade-in duration-300">
            <ChecklistEditor v-model="checklist" :task="task" class="flex-1 h-full min-h-[300px]" />
          </div>
        </div>
      </div>

      <!-- Right Sidebar -->
      <div class="w-full md:w-[280px] shrink-0 bg-surface-container-lowest rounded-2xl p-5 flex flex-col gap-6 border border-border-gray">
        
        <!-- Priority Segments -->
        <div>
          <label class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2">
            <Flag :size="14" /> Priority
          </label>
          <div class="flex bg-surface-container-low rounded-xl p-1 gap-1">
            <button 
              type="button"
              :disabled="isMentor"
              @click="priority = 0" 
              :class="[
                'flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                priority === 0 ? 'bg-white shadow-sm text-primary-container' : 'text-text-secondary hover:bg-black/5'
              ]"
            >
              Low
            </button>
            <button 
              type="button"
              :disabled="isMentor"
              @click="priority = 1" 
              :class="[
                'flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                priority === 1 ? 'bg-white shadow-sm text-primary-container' : 'text-text-secondary hover:bg-black/5'
              ]"
            >
              Medium
            </button>
            <button 
              type="button"
              :disabled="isMentor"
              @click="priority = 2" 
              :class="[
                'flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                priority === 2 ? 'bg-white shadow-sm text-error' : 'text-text-secondary hover:bg-black/5'
              ]"
            >
              High
            </button>
          </div>
        </div>

        <!-- Deadline Picker -->
        <div>
          <label class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2" for="due-date">
            <CalendarDays :size="14" /> Deadline
          </label>
          <input
            id="due-date"
            v-model="deadline"
            class="w-full bg-white border border-border-gray rounded-xl px-3 py-2.5 text-sm text-on-surface focus:ring-2 focus:ring-primary-container focus:border-transparent transition-all outline-none"
            :readonly="isMentor"
            type="date"
          />
        </div>

        <!-- Assignees -->
        <div>
          <label class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2">
            <Users :size="14" /> Assignees
          </label>
          <div class="flex flex-wrap gap-2 items-center">
            <img 
              v-for="username in assignees" 
              :key="username"
              :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(boardsStore.members.find(m => m.username === username)?.name || username)}&background=7132f5&color=fff`"
              class="w-8 h-8 rounded-full border-2 border-white shadow-sm hover:-translate-y-0.5 transition-transform"
              :title="boardsStore.members.find(m => m.username === username)?.name || username"
            />
            
            <div class="relative" ref="assigneesDropdownRef">
              <button
                v-if="!isMentor"
                type="button"
                class="w-8 h-8 rounded-full border-2 border-dashed border-border-gray flex items-center justify-center text-text-secondary hover:border-primary-container hover:text-primary-container transition-all cursor-pointer"
                @click.stop="isAssigneesDropdownOpen = !isAssigneesDropdownOpen"
              >
                <Plus :size="16" />
              </button>
              
              <Transition name="t-dropdown">
                <div v-if="isAssigneesDropdownOpen" class="absolute top-full mt-2 left-0 md:right-0 md:left-auto origin-top-left md:origin-top-right w-64 bg-white border border-border-gray rounded-xl shadow-dropdown z-50 py-2 max-h-60 overflow-y-auto custom-scrollbar">
                  <div v-if="boardsStore.membersLoading" class="px-4 py-3 text-sm text-text-secondary">Loading members...</div>
                  <div v-else-if="boardsStore.members.length === 0" class="px-4 py-3 text-sm text-text-secondary">No members found</div>
                  <button
                    v-else
                    v-for="member in boardsStore.members"
                    :key="member.username"
                    type="button"
                    class="w-full text-left px-4 py-2 hover:bg-surface-container-lowest flex items-center justify-between transition-colors cursor-pointer"
                    @click="toggleAssignee(member.username)"
                  >
                    <div class="flex items-center gap-3">
                      <img 
                        :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(member.name)}&background=f1f3f4&color=333`"
                        class="w-7 h-7 rounded-full border border-border-gray"
                      />
                      <span class="text-sm font-medium text-on-surface">{{ member.name }}</span>
                    </div>
                    <Check v-if="assignees.includes(member.username)" :size="16" class="text-primary-container" />
                  </button>
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <!-- Tags -->
        <div>
          <label class="font-button text-[11px] text-text-secondary uppercase tracking-wider font-bold mb-3 flex items-center gap-2">
            <TagIcon :size="14" /> Tags
          </label>
          <div class="space-y-3">
            <input
              v-if="!isMentor"
              v-model="tagInput"
              @keydown.enter.prevent="addTag"
              @keydown.,.prevent="addTag"
              placeholder="Add tag and press Enter..."
              class="w-full bg-white border border-border-gray rounded-xl px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary-container focus:border-transparent transition-all outline-none"
            />
            <TransitionGroup 
              name="t-list" 
              tag="div" 
              class="flex flex-wrap gap-2"
            >
              <div 
                v-for="tag in tags" 
                :key="tag"
                class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container-high text-on-surface text-[12px] font-semibold border border-border-gray/50 hover:bg-surface-container-highest transition-colors"
              >
                {{ tag }}
                <button 
                  v-if="!isMentor"
                  type="button" 
                  @click="removeTag(tag)" 
                  class="opacity-50 hover:opacity-100 transition-opacity cursor-pointer"
                >
                  <X :size="12" />
                </button>
              </div>
            </TransitionGroup>
          </div>
        </div>
      </div>
    </form>

    <!-- Action Footer via slot -->
    <template #footer>
      <div class="flex items-center justify-end gap-3 px-2">
        <Button variant="ghost" size="md" @click="emit('close')">
          Cancel
        </Button>
        <Button v-if="!isMentor" variant="primary" size="md" type="submit" form="task-form">
          {{ task ? 'Save Changes' : 'Create Task' }}
        </Button>
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

/* Transitions for tags */
.t-list-enter-active,
.t-list-leave-active {
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.t-list-enter-from,
.t-list-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  Plus,
  FileEdit,
  Columns,
  PlusCircle,
  GripVertical,
  Trash2,
  Info,
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import UserProfileDropdown from '@/components/features/UserProfileDropdown.vue'
import { useBoardsStore } from '@/stores/boards'

const router = useRouter()
const boardsStore = useBoardsStore()

const boardName = ref('')
const boardDescription = ref('')
const columns = ref([
  { id: '2', name: 'To Do' },
  { id: '3', name: 'In Progress' },
  { id: '4', name: 'Done' },
])

const draggedColumnId = ref<string | null>(null)
const dropTargetId = ref<string | null>(null)
const loading = ref(false)

let nextColumnId = 5

function addColumn() {
  columns.value.push({
    id: String(nextColumnId++),
    name: '',
  })
}

function removeColumn(id: string) {
  columns.value = columns.value.filter((col) => col.id !== id)
}

function handleDragStart(columnId: string) {
  draggedColumnId.value = columnId
}

function handleDragOver(event: DragEvent, columnId: string) {
  event.preventDefault()
  dropTargetId.value = columnId
}

function handleDragLeave() {
  dropTargetId.value = null
}

function handleDrop(event: DragEvent, targetColumnId: string) {
  event.preventDefault()
  if (!draggedColumnId.value || draggedColumnId.value === targetColumnId) return

  const draggedIndex = columns.value.findIndex((c) => c.id === draggedColumnId.value)
  const targetIndex = columns.value.findIndex((c) => c.id === targetColumnId)

  const [removed] = columns.value.splice(draggedIndex, 1)
  if (removed) {
    columns.value.splice(targetIndex, 0, removed)
  }
}

function handleDragEnd() {
  draggedColumnId.value = null
  dropTargetId.value = null
}

function handleCancel() {
  router.back()
}

async function handleCreate() {
  if (!boardName.value.trim()) return

  loading.value = true
  try {
    await boardsStore.createBoard({
      name: boardName.value.trim(),
      description: boardDescription.value.trim(),
    })
    router.push('/boards')
  } catch (error) {
    console.error('Failed to create board:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="bg-white border-b border-border-gray sticky top-0 z-50">
      <!-- Mobile Layout -->
      <div class="md:hidden flex items-center justify-between px-4 py-3">
        <button
          class="p-2 -ml-2 text-neutral-gray hover:text-primary-container transition-colors"
          @click="handleCancel"
        >
          <ArrowLeft :size="24" />
        </button>
        <h1 class="font-['Space_Grotesk'] text-xl font-bold tracking-tight text-primary-container">
          New Board
        </h1>
        <div class="w-10"></div>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden md:flex justify-between items-center w-full px-6 py-3">
        <div class="flex items-center gap-4">
          <button
            class="p-2 -ml-2 text-neutral-gray hover:text-primary-container transition-colors cursor-pointer"
            @click="handleCancel"
          >
            <ArrowLeft :size="24" />
          </button>
          <h1 class="font-['Space_Grotesk'] text-xl font-bold tracking-tight text-primary-container">
            New Board
          </h1>
        </div>

        <div class="flex items-center justify-end gap-6 flex-1">
          <UserProfileDropdown />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-16 pb-24 md:pb-10 flex items-center justify-center p-4">
      <div class="max-w-[1000px] w-full mx-auto">
        <!-- Compact Header -->
        <header class="mb-6 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <h1 class="font-['Space_Grotesk'] text-2xl md:text-3xl text-on-background font-bold">
            Initialize New Board
          </h1>
          <p class="text-neutral-gray text-sm md:text-right">
            Define workspace structure, columns, and metadata to begin task tracking.
          </p>
        </header>

        <div class="space-y-4">
          <!-- Section 1: Identity -->
          <section
            class="bg-white rounded-xl p-6 shadow-[0_4px_16px_rgba(0,0,0,0.02)] border border-border-gray"
          >
            <div class="flex flex-col md:flex-row gap-6">
              <div class="md:w-1/4">
                <div class="flex items-center gap-3 mb-2">
                  <div class="p-2 bg-purple-subtle rounded-lg text-primary-container">
                    <FileEdit :size="20" />
                  </div>
                  <h2 class="font-semibold text-base">Identity</h2>
                </div>
                <p class="text-xs text-neutral-gray">Core name and project details.</p>
              </div>
              <div class="md:w-3/4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-neutral-badge-text mb-2">
                    Board Name
                  </label>
                  <input
                    v-model="boardName"
                    class="w-full bg-white border border-border-gray rounded-lg px-3 py-2 text-sm text-on-background placeholder-neutral-gray focus:ring-2 focus:ring-primary-container transition-all outline-none"
                    placeholder="e.g., Q4 Product Launch"
                    type="text"
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-neutral-badge-text mb-2">
                    Description (Optional)
                  </label>
                  <input
                    v-model="boardDescription"
                    class="w-full bg-white border border-border-gray rounded-lg px-3 py-2 text-sm text-on-background placeholder-neutral-gray focus:ring-2 focus:ring-primary-container transition-all outline-none"
                    placeholder="Brief purpose..."
                    type="text"
                  />
                </div>
              </div>
            </div>
          </section>

          <!-- Section 2: Board Structure -->
          <section
            class="bg-white rounded-xl p-6 shadow-[0_4px_16px_rgba(0,0,0,0.02)] border border-border-gray relative overflow-hidden"
          >
            <!-- Overlay for Coming Soon -->
            <div class="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex items-center justify-center">
              <div class="bg-primary-container text-white px-4 py-2 rounded-lg font-bold shadow-lg">
                Coming Soon (Task 3)
              </div>
            </div>
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-purple-subtle rounded-lg text-primary-container">
                  <Columns :size="20" />
                </div>
                <div>
                  <h2 class="font-semibold text-base">Board Structure</h2>
                  <p class="text-xs text-neutral-gray">Workflow stages</p>
                </div>
              </div>
              <button
                class="flex items-center gap-1.5 text-primary-container font-bold text-xs px-3 py-1.5 rounded-lg hover:bg-purple-subtle transition-all"
                @click="addColumn"
              >
                <PlusCircle :size="16" />
                Add Column
              </button>
            </div>

            <!-- Info Banner -->
            <div class="mb-3 p-3 bg-purple-subtle/30 border border-primary-container/20 rounded-lg">
              <p class="text-xs text-primary-container font-medium flex items-center gap-1">
                <Info :size="14" />
                Backlog tasks will be managed in a separate view
              </p>
            </div>

            <div class="flex flex-nowrap gap-3 overflow-x-auto pb-2 custom-scrollbar">
              <!-- Column Cards -->
              <div
                v-for="column in columns"
                :key="column.id"
                draggable="true"
                :class="[
                  'flex-shrink-0 w-48 bg-surface-container-low border rounded-xl p-3 group transition-all duration-200',
                  draggedColumnId === column.id ? 'opacity-50 cursor-grabbing scale-95 border-border-gray' : 'cursor-grab border-border-gray',
                  dropTargetId === column.id && draggedColumnId !== column.id ? 'border-primary-container border-2 shadow-lg' : '',
                ]"
                @dragstart="handleDragStart(column.id)"
                @dragover="handleDragOver($event, column.id)"
                @dragleave="handleDragLeave"
                @drop="handleDrop($event, column.id)"
                @dragend="handleDragEnd"
              >
                <div class="flex justify-between items-center mb-2">
                  <GripVertical :size="16" class="text-neutral-gray" />
                  <button
                    class="opacity-0 group-hover:opacity-100 text-neutral-gray hover:text-error transition-all"
                    @click="removeColumn(column.id)"
                  >
                    <Trash2 :size="16" />
                  </button>
                </div>
                <input
                  v-model="column.name"
                  class="w-full bg-white border border-border-gray rounded-lg px-2 py-1.5 text-xs font-semibold text-on-background outline-none focus:ring-2 focus:ring-primary-container transition-all"
                  type="text"
                />
              </div>

              <!-- Placeholder for New -->
              <button
                class="flex-shrink-0 w-48 border-2 border-dashed border-neutral-gray/20 rounded-xl p-3 flex flex-col items-center justify-center gap-1 hover:border-primary-container/40 hover:bg-purple-subtle/10 transition-all text-neutral-gray hover:text-primary-container"
                @click="addColumn"
              >
                <Plus :size="20" />
                <span class="text-[10px] font-bold uppercase">New Column</span>
              </button>
            </div>
          </section>

          <!-- Footer CTA -->
          <div class="flex flex-col md:flex-row items-center justify-between pt-2 gap-3">
            <div class="flex items-center gap-3 w-full md:w-auto">
              <Button
                variant="outlined"
                size="sm"
                class="flex-1 md:flex-none"
                @click="handleCancel"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                class="flex-1 md:flex-none"
                :loading="loading"
                @click="handleCreate"
              >
                Create Board
              </Button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: var(--color-surface-container-low);
  border-radius: 4px;
  margin: 0 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-neutral-gray);
}

/* Firefox */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--color-border-gray) var(--color-surface-container-low);
}
</style>

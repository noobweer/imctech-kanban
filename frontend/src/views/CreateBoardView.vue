<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  Search,
  Plus,
  Settings,
  FileEdit,
  Columns,
  PlusCircle,
  GripVertical,
  Trash2,
  ChevronRight,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const boardName = ref('')
const boardDescription = ref('')
const columns = ref([
  { id: '1', name: 'Backlog' },
  { id: '2', name: 'To Do' },
  { id: '3', name: 'In Progress' },
  { id: '4', name: 'Done' },
])

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

function handleCancel() {
  router.back()
}

function handleCreate() {
  console.log('Create board:', {
    name: boardName.value,
    description: boardDescription.value,
    columns: columns.value,
  })
  // TODO: API call when backend ready
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

        <div class="flex items-center gap-6">
          <nav class="flex items-center gap-6 text-sm font-semibold tracking-tight">
            <button class="text-neutral-gray hover:text-primary-container transition-colors">
              Settings
            </button>
          </nav>
          <div class="h-8 w-8 rounded-full overflow-hidden border border-border-gray">
            <img
              v-if="authStore.user"
              :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(authStore.user.name)}&background=7132f5&color=fff`"
              :alt="authStore.user.name"
              class="w-full h-full object-cover"
            />
          </div>
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
                  <label class="block text-xs font-semibold text-neutral-badge-text mb-1.5">
                    Project Name
                  </label>
                  <input
                    v-model="boardName"
                    class="w-full bg-white border border-border-gray rounded-lg px-3 py-2 text-sm text-on-background placeholder-neutral-gray focus:ring-2 focus:ring-primary-container transition-all outline-none"
                    placeholder="e.g., Q4 Product Launch"
                    type="text"
                  />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-neutral-badge-text mb-1.5">
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
            class="bg-white rounded-xl p-6 shadow-[0_4px_16px_rgba(0,0,0,0.02)] border border-border-gray"
          >
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

            <div class="flex flex-nowrap gap-3 overflow-x-auto pb-2 scrollbar-hide">
              <!-- Column Cards -->
              <div
                v-for="column in columns"
                :key="column.id"
                :class="[
                  'flex-shrink-0 w-48 bg-surface-container-low border rounded-xl p-3 group cursor-grab',
                  column.name === 'In Progress'
                    ? 'border-primary-container/20 bg-purple-subtle/20'
                    : 'border-border-gray',
                ]"
              >
                <div class="flex justify-between items-center mb-2">
                  <GripVertical
                    :size="16"
                    :class="[
                      column.name === 'In Progress' ? 'text-primary-container/40' : 'text-neutral-gray',
                    ]"
                  />
                  <button
                    class="opacity-0 group-hover:opacity-100 text-neutral-gray hover:text-error transition-all"
                    @click="removeColumn(column.id)"
                  >
                    <Trash2 :size="16" />
                  </button>
                </div>
                <input
                  v-model="column.name"
                  :class="[
                    'w-full bg-white border rounded-lg px-2 py-1.5 text-xs font-bold text-on-background outline-none focus:ring-2 focus:ring-primary-container transition-all',
                    column.name === 'In Progress'
                      ? 'border-primary-container/30'
                      : 'border-border-gray',
                  ]"
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
              <button
                class="flex-1 cursor-pointer md:flex-none px-6 py-2.5 border border-border-gray rounded-xl text-on-background font-semibold text-sm hover:bg-gray-50 transition-all"
                @click="handleCancel"
              >
                Cancel
              </button>
              <button
                class="flex-1 cursor-pointer md:flex-none px-8 py-2.5 bg-primary-container text-white rounded-xl font-semibold text-sm shadow-lg shadow-primary-container/20 hover:opacity-90 transition-all"
                @click="handleCreate"
              >
                Create Board
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

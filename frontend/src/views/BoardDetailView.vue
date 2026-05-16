<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { Plus, Layout } from 'lucide-vue-next'
import { useColumnsStore } from '@/stores/columns'
import type { Board } from '@/types/board'
import type { Task } from '@/types/task'
import Button from '@/components/ui/Button.vue'
import ColumnCard from '@/components/features/ColumnCard.vue'

const props = defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const columnsStore = useColumnsStore()
const loadingColumns = ref(columnsStore.columns.length === 0)

// Mock tasks for High Fidelity demonstration
const mockTasks = ref<Task[]>([
  {
    id: '1',
    title: 'Task1',
    description: 'DescriptionDescription...',
    dueDate: 'May 10, 12:00',
    subtasksTotal: 8,
    subtasksCompleted: 0,
    type: 'Bug',
    assignee: {
      name: 'Jhon Doe',
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDutyfEHuBhv7E3xrJAEn_00ctnVY6C2pEzxvGcjnY261gMVa7W9X5IAeym7AmcKVtXmkhW7aJRIG-jTFZkFs_3peVMeCmCKEoZLsmwpRj7gaiJnUnqSKXjsGXf-dFeI9eJSYoZ0QaAC_8fBfwxZg-IcaWrIJ_sShjvzGKdIMvOVvrbdh-UWo5t172bd3bFBM74QgiGiolbgICZHGOCJ-AWvrk82x0tu4QbirykzzFLDZRpicL0Dn1qIluiUUqClIpYYBOUUky2i1A'
    },
    status: 'todo'
  },
  {
    id: '2',
    title: 'Task1',
    description: 'DescriptionDescription...',
    dueDate: 'May 10, 12:00',
    subtasksTotal: 8,
    subtasksCompleted: 2,
    type: 'Bug',
    assignee: {
      name: 'Jhon Doe',
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD6Nn9iBOsDPGdLl35ZpwRYaeGkQ75-B_PDzzG30sIfquWaVrDU7B9kt4GZnotbbk9t7TVhKyiGHbK_SuImNTMaxnC94c9OEYXiYbvw0sG4uBaow5lfN69YT_NBVVAsuA4IUp5nQUV1kl-9vTFTei8xRe7AzGxZ2wNqFpNW1a2nyJmgKJ8s80MCDvxbCQBlnbmJawKichk3S5Mq_qj-Od2LtjfFDrvfNxmlwL_6zecCakFYlwXyApcUkvviMCGQvp0rxotRbB_o0gs'
    },
    status: 'inprogress'
  },
  {
    id: '3',
    title: 'Task1',
    description: 'DescriptionDescription...',
    dueDate: 'May 10, 12:00',
    subtasksTotal: 8,
    subtasksCompleted: 8,
    type: 'Bug',
    assignee: {
      name: 'Jhon Doe',
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDbxiERC4mKzWjX1kAaIVwbGEROFWT255knyI7chsrQ-rPQ-ouzaM9yCvrcCWq3ODndKR3aQHypyqCUkOigBMSxmz0Y8BCSpvHbDGJaGbPVx3wUGfb7qiUPyh36zXeRF1SV-_G17QMRHU38z_PRv09BG1k5T_AwMPaYg8tuHwHnJFYv3a76G94sZWSakJRplipU_WGAlyyRgKDbo1esD8TgxKQhK-czVMBeMDfLD7YpaiRUnxz1yeyNqMdr12hd74PUG1hlZo73Xhc'
    },
    status: 'review'
  },
  {
    id: '4',
    title: 'Task1',
    description: 'DescriptionDescription...',
    completedDate: 'May 09',
    subtasksTotal: 8,
    subtasksCompleted: 8,
    type: 'Bug',
    assignee: {
      name: 'Jhon Doe',
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAJUp8B0m_1c-pDWWTsdKCbh9-p-FEmUGpYDvlVT1760i85eeoU4MQB5_3wvszhFzrzC6zLHGxiiXgr0ApTbRS_WUxhqGT3pSRUgNMLmUDIu2ak3qvlnyWYsRyMXmoEg8-yzQfD8ymQn2VVvg6FyjabLQVKcfRbjdbkKvikJ3h4-jtoKuo_gWtZFhjbxMQ1fwe5SU2gvs7V44kNRCU1nox0ox_vEcQ81Sdi9gz33KEGSkIQN0kOgfNqp3msWHKxkWyvpw7okp70m4E'
    },
    status: 'done'
  }
])

async function loadColumns() {
  if (!props.board) return
  
  // If we already have columns, load silently in the background
  const isSilent = columnsStore.columns.length > 0
  
  if (!isSilent) loadingColumns.value = true
  try {
    await columnsStore.fetchColumns(props.board.id, isSilent)
    // Start polling after successful initial fetch
    columnsStore.startPolling(props.board.id)
  } finally {
    loadingColumns.value = false
  }
}

function getTasksForColumn(columnName: string) {
  const name = columnName.toLowerCase()
  if (name.includes('to do')) return mockTasks.value.filter(t => t.status === 'todo')
  if (name.includes('in progress')) return mockTasks.value.filter(t => t.status === 'inprogress')
  if (name.includes('review')) return mockTasks.value.filter(t => t.status === 'review')
  if (name.includes('done')) return mockTasks.value.filter(t => t.status === 'done')
  return []
}

async function handleCreateDefaultColumns() {
  if (!props.board) return
  await columnsStore.createDefaultColumns(props.board.id)
}

async function handleCreateColumn() {
  if (!props.board) return
  const name = prompt('Enter column name')
  if (name?.trim()) {
    await columnsStore.createColumn(props.board.id, { name: name.trim() })
  }
}

async function handleRenameColumn(id: string, name: string) {
  await columnsStore.updateColumn(id, { name })
}

async function handleArchiveColumn(id: string) {
  if (confirm('Are you sure you want to archive this column?')) {
    await columnsStore.archiveColumn(id)
  }
}

async function handleMoveColumn(id: string, direction: 'left' | 'right') {
  const currentColumns = columnsStore.activeColumns
  const index = currentColumns.findIndex(c => c.id === id)
  if (index === -1) return

  const targetColumn = direction === 'left' ? currentColumns[index - 1] : currentColumns[index + 1]
  if (!targetColumn) return

  await columnsStore.moveColumn(id, targetColumn.position)
}

function handleAddTask(columnId: string) {
  console.log('Add task to column:', columnId)
}

watch(() => props.board, (newBoard) => {
  if (newBoard) {
    loadColumns()
  }
}, { immediate: true })

onMounted(loadColumns)
onUnmounted(columnsStore.stopPolling)
</script>

<template>
  <!-- Column Canvas -->
  <main v-dragscroll class="h-full overflow-x-auto p-6 bg-[#fcfcfc] custom-scrollbar-x cursor-grab active:cursor-grabbing">
    <div v-if="loadingBoard || loadingColumns" class="flex gap-6 max-w-[1600px] mx-auto">
      <div v-for="i in 4" :key="i" class="w-80 h-[500px] border border-border-gray rounded-xl animate-pulse"></div>
    </div>
    
    <div v-else-if="columnsStore.activeColumns.length > 0" class="flex items-start gap-6 pb-4 min-h-full max-w-[1600px] mx-auto">
      <ColumnCard 
        v-for="(column, index) in columnsStore.activeColumns" 
        :key="column.id"
        :column="column"
        :tasks="getTasksForColumn(column.name)"
        :is-first="index === 0"
        :is-last="index === columnsStore.activeColumns.length - 1"
        @move-left="handleMoveColumn($event, 'left')"
        @move-right="handleMoveColumn($event, 'right')"
        @rename="handleRenameColumn"
        @archive="handleArchiveColumn"
        @add-task="handleAddTask"
      />
      
      <!-- Add Column Placeholder -->
      <button 
        class="w-80 h-16 flex items-center justify-center gap-2 border-2 border-dashed border-border-gray/30 rounded-xl text-text-secondary hover:border-primary-container/30 hover:text-primary-container transition-all shrink-0 cursor-pointer bg-surface-container-low/20"
        @click="handleCreateColumn"
      >
        <Plus :size="20" />
        Add Another Column
      </button>
    </div>

    <div v-else class="h-full flex flex-col items-center justify-center text-center">
      <div class="bg-surface-white p-12 rounded-2xl shadow-xl border border-border-gray max-w-lg">
        <div class="w-20 h-20 bg-surface-container-low rounded-full flex items-center justify-center mx-auto mb-6">
          <Layout :size="40" class="text-primary-container opacity-40" />
        </div>
        <h2 class="text-2xl font-bold text-text-primary mb-3">No columns yet</h2>
        <p class="text-text-secondary mb-8 leading-relaxed">Your board is empty. Start by loading default columns or design your custom workflow from scratch.</p>
        <div class="flex items-center justify-center gap-4">
          <Button variant="primary" @click="handleCreateDefaultColumns">Load Defaults</Button>
          <Button variant="outlined" @click="handleCreateColumn">Create Custom</Button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.custom-scrollbar-x::-webkit-scrollbar {
  height: 8px;
}
.custom-scrollbar-x::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar-x::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 10px;
}
.custom-scrollbar-x::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}
</style>

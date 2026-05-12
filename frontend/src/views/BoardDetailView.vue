<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBoardsStore } from '@/stores/boards'
import { useColumnsStore } from '@/stores/columns'
import { boardsApi } from '@/api/boards'
import type { Board } from '@/types/board'
import Button from '@/components/ui/Button.vue'
import Icon from '@/components/ui/Icon.vue'
import ColumnCard from '@/components/features/ColumnCard.vue'

const route = useRoute()
const router = useRouter()
const boardsStore = useBoardsStore()
const columnsStore = useColumnsStore()

const boardId = route.params.id as string
const board = ref<Board | null>(null)
const loading = ref(true)

async function loadData() {
  loading.value = true
  try {
    board.value = await boardsApi.getBoard(boardId)
    await columnsStore.fetchColumns(boardId)
  } catch (error) {
    console.error('Failed to load board details:', error)
    router.push('/boards')
  } finally {
    loading.value = false
  }
}

async function handleCreateDefaultColumns() {
  if (!board.value) return
  await columnsStore.createDefaultColumns(board.value.id)
}

async function handleCreateColumn() {
  if (!board.value) return
  const name = prompt('Enter column name')
  if (name?.trim()) {
    await columnsStore.createColumn(board.value.id, { name: name.trim() })
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

  const newPosition = direction === 'left' ? currentColumns[index - 1].position : currentColumns[index + 1].position
  await columnsStore.moveColumn(id, newPosition)
}

onMounted(loadData)
</script>

<template>
  <div class="h-full flex flex-col bg-white overflow-hidden">
    <!-- Header -->
    <header class="flex items-center justify-between p-4 border-b border-gray-200 shrink-0">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="sm" @click="router.push('/boards')">
          <Icon name="arrow-left" size="18" />
        </Button>
        <div v-if="board">
          <h1 class="text-xl font-bold text-gray-900">{{ board.name }}</h1>
          <p class="text-sm text-gray-500">{{ board.project_name }}</p>
        </div>
        <div v-else-if="loading" class="animate-pulse flex flex-col gap-2">
          <div class="h-6 w-48 bg-gray-200 rounded"></div>
          <div class="h-4 w-32 bg-gray-100 rounded"></div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <Button v-if="columnsStore.activeColumns.length === 0 && !columnsStore.loading" variant="outline" size="sm" class="gap-2" @click="handleCreateDefaultColumns">
          <Icon name="layout" size="16" />
          Load Defaults
        </Button>
        <Button variant="primary" size="sm" class="gap-2" @click="handleCreateColumn">
          <Icon name="plus" size="16" />
          Add Column
        </Button>
      </div>
    </header>

    <!-- Column Canvas -->
    <main class="flex-1 overflow-x-auto p-6 bg-gray-100/50">
      <div v-if="loading" class="flex gap-6">
        <div v-for="i in 3" :key="i" class="w-72 h-[400px] bg-gray-200/50 rounded-lg animate-pulse"></div>
      </div>
      
      <div v-else-if="columnsStore.activeColumns.length > 0" class="flex items-start gap-6 pb-4 min-h-full">
        <ColumnCard 
          v-for="(column, index) in columnsStore.activeColumns" 
          :key="column.id"
          :column="column"
          :is-first="index === 0"
          :is-last="index === columnsStore.activeColumns.length - 1"
          @move-left="handleMoveColumn($event, 'left')"
          @move-right="handleMoveColumn($event, 'right')"
          @rename="handleRenameColumn"
          @archive="handleArchiveColumn"
        />
        
        <!-- Add Column Placeholder -->
        <button 
          class="w-72 h-12 flex items-center justify-center gap-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors shrink-0"
          @click="handleCreateColumn"
        >
          <Icon name="plus" size="18" />
          Add Another Column
        </button>
      </div>

      <div v-else class="h-full flex flex-col items-center justify-center text-center">
        <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 max-w-md">
          <Icon name="layout" size="48" class="text-gray-300 mx-auto mb-4" />
          <h2 class="text-xl font-bold text-gray-900 mb-2">No columns yet</h2>
          <p class="text-gray-500 mb-6">Start by loading default columns or create your own custom structure.</p>
          <div class="flex items-center justify-center gap-3">
            <Button variant="primary" @click="handleCreateDefaultColumns">Load Default Columns</Button>
            <Button variant="outline" @click="handleCreateColumn">Create Custom</Button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Custom scrollbar for column canvas */
main::-webkit-scrollbar {
  height: 8px;
}
main::-webkit-scrollbar-track {
  background: transparent;
}
main::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}
main::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>

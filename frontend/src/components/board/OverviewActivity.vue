<script setup lang="ts">
import { computed, ref } from 'vue'
import { useOverviewStore } from '@/stores/overview'
import type { Board } from '@/types/board'
import { ArrowRight } from 'lucide-vue-next'
import UserTasksModal from './UserTasksModal.vue'

const props = defineProps<{
  board: Board
}>()

const overviewStore = useOverviewStore()
const data = computed(() => overviewStore.activityData)
const loading = computed(() => overviewStore.isLoadingActivity)

const selectedUserForModal = ref<string | null>(null)
const isModalOpen = ref(false)

const columns = computed(() => {
  if (!data.value || !data.value.members || data.value.members.length === 0) return []
  return data.value.members[0]?.columns.map(c => c.column_name) || []
})

function openUserTasks(username: string) {
  selectedUserForModal.value = username
  isModalOpen.value = true
}

function closeUserTasks() {
  isModalOpen.value = false
}
</script>

<template>
  <div class="bg-white rounded-[16px] shadow-[0_4px_24px_rgba(0,0,0,0.03)] overflow-hidden flex flex-col">
    <div v-if="loading && !data" class="p-6 flex flex-col gap-4">
      <div v-for="i in 5" :key="i" class="h-10 bg-[rgba(148,151,169,0.12)] rounded-lg animate-pulse w-full"></div>
    </div>
    
    <div v-else-if="data" class="overflow-x-auto w-full custom-scrollbar">
      <table class="w-full text-left border-collapse min-w-[600px]">
        <thead>
          <tr>
            <th class="sticky left-0 bg-[#f9fafc] p-4 text-xs font-semibold text-cool-gray uppercase tracking-wider border-b border-border-gray shadow-[1px_0_0_#dedee5] z-10 w-[200px]">
              Member
            </th>
            <th 
              v-for="colName in columns" 
              :key="colName"
              class="p-4 text-xs font-semibold text-cool-gray uppercase tracking-wider border-b border-border-gray whitespace-nowrap"
            >
              {{ colName }}
            </th>
            <th class="p-4 text-xs font-semibold text-cool-gray uppercase tracking-wider border-b border-border-gray w-16 text-center">
              Action
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="member in data.members" 
            :key="member.username"
            class="group border-b border-border-gray/50 hover:bg-[#101114]/5 transition-colors"
          >
            <td class="sticky left-0 p-4 shadow-[1px_0_0_#dedee5] z-10 bg-white group-hover:bg-[#f6f6f9] transition-colors">
              <div class="flex items-center gap-3">
                <img 
                  :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(member.name)}&background=7132f5&color=fff&size=64`" 
                  alt="avatar" 
                  class="w-8 h-8 rounded-full shadow-sm"
                />
                <div>
                  <div class="text-sm font-semibold text-near-black leading-tight">{{ member.name }}</div>
                  <div class="text-xs text-cool-gray">@{{ member.username }}</div>
                </div>
              </div>
            </td>
            
            <td 
              v-for="col in member.columns" 
              :key="col.column_name"
              class="p-4 whitespace-nowrap"
            >
              <div class="text-sm text-cool-gray">
                <span class="font-bold" :class="col.task_count > 0 ? 'text-near-black' : ''">{{ col.task_count }}</span> 
                <span class="text-xs ml-1">({{ col.percent }}%)</span>
              </div>
            </td>
            
            <td class="p-4 text-center">
              <button 
                class="w-8 h-8 flex items-center justify-center rounded-[8px] text-cool-gray hover:text-[#7132f5] hover:bg-[rgba(133,91,251,0.16)] transition-all mx-auto cursor-pointer"
                @click="openUserTasks(member.username)"
                aria-label="View user tasks"
              >
                <ArrowRight :size="16" class="group-hover:translate-x-1 transition-transform duration-300" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- User Tasks Modal -->
    <Teleport to="body">
      <UserTasksModal 
        :is-open="isModalOpen"
        :board="board"
        :initial-username="selectedUserForModal || ''"
        :members="data?.members || []"
        @close="closeUserTasks" 
      />
    </Teleport>
  </div>
</template>

<style scoped>
.text-near-black {
  color: #101114;
}
.text-cool-gray {
  color: #686b82;
}
.border-border-gray {
  border-color: #dedee5;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f4f5f8;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c3c4ce;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9497a9;
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Search } from 'lucide-vue-next'
import type { Board } from '@/types/board'
import type { Task } from '@/types/task'
import Button from '@/components/ui/Button.vue'
import TaskCard from '@/components/features/TaskCard.vue'

defineProps<{
  board: Board | null
  loadingBoard: boolean
}>()

const searchQuery = ref('')

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
  },
  {
    id: '5',
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
    id: '6',
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
    id: '7',
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
    id: '8',
    title: 'Task1',
    description: 'DescriptionDescription...',
    dueDate: 'May 10, 12:00',
    subtasksTotal: 8,
    subtasksCompleted: 8,
    type: 'Bug',
    assignee: {
      name: 'Jhon Doe',
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAJUp8B0m_1c-pDWWTsdKCbh9-p-FEmUGpYDvlVT1760i85eeoU4MQB5_3wvszhFzrzC6zLHGxiiXgr0ApTbRS_WUxhqGT3pSRUgNMLmUDIu2ak3qvlnyWYsRyMXmoEg8-yzQfD8ymQn2VVvg6FyjabLQVKcfRbjdbkKvikJ3h4-jtoKuo_gWtZFhjbxMQ1fwe5SU2gvs7V44kNRCU1nox0ox_vEcQ81Sdi9gz33KEGSkIQN0kOgfNqp3msWHKxkWyvpw7okp70m4E'
    },
    status: 'todo'
  }
])

function handleAddTask() {
  console.log('Add task to backlog')
}
</script>

<template>
  <!-- Main Content -->
  <main v-dragscroll class="h-full overflow-y-auto p-6 bg-[#fcfcfc] custom-scrollbar cursor-grab active:cursor-grabbing">
    <div class="max-w-[1600px] mx-auto">
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-4 flex-1">
          <h2 class="text-3xl font-bold text-text-primary whitespace-nowrap font-sub-heading">
            Backlog Tasks
          </h2>
          <span class="px-3 py-1 bg-surface-container-high rounded-full text-xs font-bold text-neutral-gray">
            {{ mockTasks.length }} Tasks
          </span>
          
          <!-- Integrated Search Bar -->
          <div class="relative w-full max-w-md hidden md:block">
            <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-gray" />
            <input
              v-model="searchQuery"
              class="w-full pl-10 pr-4 py-2 bg-white border border-border-gray rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all text-sm"
              placeholder="Search tasks..."
              type="text"
            />
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <!-- Search for mobile -->
          <button class="p-2 border border-border-gray rounded-xl hover:bg-white transition-colors md:hidden text-neutral-gray">
            <Search :size="20" />
          </button>
          <Button variant="primary" class="gap-2 whitespace-nowrap" @click="handleAddTask">
            <Plus :size="20" /> 
            Add Task
          </Button>
        </div>      </div>

      <!-- 4-column Grid -->
      <div v-if="loadingBoard" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div v-for="i in 8" :key="i" class="h-48 border border-border-gray rounded-xl animate-pulse bg-surface-container-low/50"></div>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <TaskCard 
          v-for="task in mockTasks" 
          :key="task.id" 
          :task="task" 
        />
      </div>
    </div>
  </main>
</template>

<style scoped>
.font-sub-heading {
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
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}
</style>

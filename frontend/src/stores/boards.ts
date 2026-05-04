import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Board } from '@/types/board'

export const useBoardsStore = defineStore('boards', () => {
  const boards = ref<Board[]>([
    {
      id: '1',
      title: 'Strategy Roadmap',
      category: 'Infrastructure Development',
      dueDate: '2026-11-24',
      progress: 65,
      members: [
        { username: 'alice', name: 'Alice Johnson', avatar: 'https://i.pravatar.cc/150?img=1' },
        { username: 'bob', name: 'Bob Smith', avatar: 'https://i.pravatar.cc/150?img=2' },
        { username: 'charlie', name: 'Charlie Brown' },
        { username: 'diana', name: 'Diana Prince' },
        { username: 'eve', name: 'Eve Wilson' },
      ],
      createdBy: 'mentor1',
      archived: false,
    },
    {
      id: '2',
      title: 'API Integration',
      category: 'Product Engineering',
      dueDate: '2026-12-05',
      progress: 42,
      members: [
        { username: 'frank', name: 'Frank Miller', avatar: 'https://i.pravatar.cc/150?img=3' },
        { username: 'grace', name: 'Grace Lee' },
        { username: 'henry', name: 'Henry Ford' },
        { username: 'iris', name: 'Iris West' },
        { username: 'jack', name: 'Jack Ryan' },
        { username: 'kate', name: 'Kate Bishop' },
        { username: 'leo', name: 'Leo Valdez' },
        { username: 'mia', name: 'Mia Wallace' },
        { username: 'noah', name: 'Noah Calhoun' },
      ],
      createdBy: 'mentor1',
      archived: false,
    },
    {
      id: '3',
      title: 'Q4 Marketing',
      category: 'Growth & Operations',
      dueDate: '2026-12-20',
      progress: 88,
      members: [
        { username: 'olivia', name: 'Olivia Pope', avatar: 'https://i.pravatar.cc/150?img=4' },
        { username: 'peter', name: 'Peter Parker', avatar: 'https://i.pravatar.cc/150?img=5' },
        { username: 'quinn', name: 'Quinn Fabray' },
        { username: 'rachel', name: 'Rachel Green' },
        { username: 'sam', name: 'Sam Winchester' },
        { username: 'tina', name: 'Tina Cohen-Chang' },
      ],
      createdBy: 'mentor1',
      archived: false,
    },
    {
      id: '4',
      title: 'Design System',
      category: 'UI/UX Standards',
      dueDate: '2026-10-30',
      progress: 15,
      members: [
        { username: 'uma', name: 'Uma Thurman', avatar: 'https://i.pravatar.cc/150?img=6' },
        { username: 'victor', name: 'Victor Stone' },
        { username: 'wendy', name: 'Wendy Darling' },
      ],
      createdBy: 'mentor1',
      archived: false,
    },
  ])

  const loading = ref(false)
  const activeTab = ref<'active' | 'archived'>('active')
  const searchQuery = ref('')

  const filteredBoards = computed(() => {
    let result = boards.value.filter((board) => {
      const matchesTab = activeTab.value === 'active' ? !board.archived : board.archived
      const matchesSearch =
        searchQuery.value === '' ||
        board.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        board.category.toLowerCase().includes(searchQuery.value.toLowerCase())
      return matchesTab && matchesSearch
    })
    return result
  })

  async function fetchBoards() {
    loading.value = true
    try {
      // TODO: API call when backend ready
      await new Promise((resolve) => setTimeout(resolve, 500))
    } finally {
      loading.value = false
    }
  }

  function createBoard() {
    // TODO: API call when backend ready
    console.log('Create board clicked')
  }

  return {
    boards,
    loading,
    activeTab,
    searchQuery,
    filteredBoards,
    fetchBoards,
    createBoard,
  }
})

<script setup lang="ts">
import { ref } from 'vue'
import type { Board } from '@/types/board'
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import BoardSettingsModal from './BoardSettingsModal.vue'
import BoardMembersModal from './BoardMembersModal.vue'
import { MoreVertical } from 'lucide-vue-next'

interface Props {
  board: Board
}

const props = defineProps<Props>()

const showSettingsModal = ref(false)
const showMembersModal = ref(false)

function openSettings() {
  showSettingsModal.value = true
}

function openMembers() {
  showMembersModal.value = true
}
</script>

<template>
  <div>
    <Dropdown position="bottom-right">
      <template #trigger>
        <button class="text-neutral-gray hover:text-text-primary transition-colors p-1 rounded-lg bg-white hover:bg-gray-100 cursor-pointer">
          <MoreVertical :size="20" />
        </button>
      </template>

      <DropdownItem icon="settings" @click="openSettings">
        General Settings
      </DropdownItem>
      <DropdownItem icon="users" @click="openMembers">
        Members & Invites
      </DropdownItem>
    </Dropdown>

    <BoardSettingsModal v-model="showSettingsModal" :board="board" />
    <BoardMembersModal v-model="showMembersModal" :board="board" />
  </div>
</template>

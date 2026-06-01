<script setup lang="ts">
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import { useAuthStore } from '@/stores/auth'
import type { TaskComment } from '@/types/comment'
import { MoreHorizontal } from 'lucide-vue-next'
import { computed, ref, nextTick } from 'vue'

const props = defineProps<{
  comment: TaskComment
  hideAvatar?: boolean
}>()

const emit = defineEmits<{
  edit: [comment: TaskComment]
  delete: [comment: TaskComment]
}>()

const authStore = useAuthStore()

const canEdit = computed(() => {
  if (!authStore.user) return false
  return authStore.user.username === props.comment.owner_username
})

const formattedTime = computed(() => {
  const date = new Date(props.comment.created_at)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})

const isEditing = ref(false)
const editContent = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

async function startEdit() {
  editContent.value = props.comment.content
  isEditing.value = true
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.focus()
    textareaRef.value.selectionStart = textareaRef.value.value.length
  }
}

function saveEdit() {
  if (!editContent.value.trim() || editContent.value === props.comment.content) {
    isEditing.value = false
    return
  }
  emit('edit', { ...props.comment, content: editContent.value })
  isEditing.value = false
}

function cancelEdit() {
  isEditing.value = false
}
</script>

<template>
  <div class="group flex gap-3 w-full" :class="{ 'mt-1': hideAvatar, 'mt-2': !hideAvatar }">
    <!-- Avatar column -->
    <div class="w-8 shrink-0 flex flex-col items-center">
      <img
        v-if="!hideAvatar"
        :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(comment.owner_name)}&background=f1f3f4&color=333`"
        class="w-8 h-8 rounded-full border border-border-gray"
      />
    </div>

    <!-- Content column -->
    <div class="flex-1 min-w-0">
      <div v-if="!hideAvatar" class="flex items-baseline gap-2 mb-1">
        <span class="font-bold text-sm text-on-surface">{{ comment.owner_name }}</span>
        <span
          class="text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-surface-container-high text-text-secondary"
        >
          {{ comment.owner_role }}
        </span>
        <span class="text-xs text-text-secondary ml-auto">{{ formattedTime }}</span>
      </div>

      <div class="relative flex items-start gap-2">
        <!-- Edit Mode -->
        <div v-if="isEditing" class="w-full min-w-[200px]">
          <div class="bg-white border border-border-gray rounded-xl overflow-hidden focus-within:border-[#5800d8] focus-within:ring-2 focus-within:ring-[#5800d8]/20 transition-all">
            <textarea
              ref="textareaRef"
              v-model="editContent"
              rows="2"
              class="w-full bg-transparent p-3 outline-none text-on-surface text-[15px] resize-y custom-scrollbar min-h-[60px]"
              @keydown.enter.exact.prevent="saveEdit"
              @keydown.esc.prevent="cancelEdit"
            ></textarea>
            <div class="flex justify-end gap-2 p-2 border-t border-border-gray bg-surface-container-lowest">
              <button @click="cancelEdit" class="px-3 py-1.5 text-xs font-semibold text-text-secondary hover:bg-surface-container rounded transition-colors cursor-pointer">Cancel</button>
              <button @click="saveEdit" class="px-3 py-1.5 text-xs font-semibold text-white bg-primary-container hover:bg-primary rounded transition-colors shadow-sm cursor-pointer">Save</button>
            </div>
          </div>
        </div>

        <!-- View Mode -->
        <div v-else
          class="bg-surface-container hover:bg-surface-container-high transition-colors rounded-xl px-3 py-2 text-[15px] text-on-surface/90 w-fit min-w-[120px] max-w-full break-words whitespace-pre-wrap leading-[1.4]"
          :class="{ 'rounded-tl-sm': !hideAvatar }"
        >
          {{ comment.content }}

          <div
            v-if="comment.is_edited"
            class="inline-block text-[10px] text-text-secondary ml-2 relative -top-[1px]"
          >
            (edited)
          </div>
        </div>

        <!-- Actions Dropdown -->
        <div
          v-if="canEdit && !isEditing"
          class="opacity-0 group-hover:opacity-100 transition-opacity shrink-0 pt-1 lg:opacity-0 max-lg:opacity-100"
        >
          <Dropdown position="bottom-right">
            <template #trigger>
              <button
                class="w-6 h-6 flex items-center justify-center rounded hover:bg-surface-container text-neutral-gray transition-colors cursor-pointer"
              >
                <MoreHorizontal :size="16" />
              </button>
            </template>
            <div class="py-1">
              <DropdownItem icon="pencil" @click="startEdit">Edit</DropdownItem>
              <DropdownItem icon="trash" variant="danger" @click="emit('delete', comment)"
                >Delete</DropdownItem
              >
            </div>
          </Dropdown>
        </div>
      </div>
    </div>
  </div>
</template>

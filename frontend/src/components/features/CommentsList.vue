<script setup lang="ts">
import { useCommentsStore } from '@/stores/comments'
import type { TaskComment } from '@/types/comment'
import { computed, ref } from 'vue'
import CommentInput from './CommentInput.vue'
import CommentItem from './CommentItem.vue'

const props = defineProps<{
  taskId: string
  canCreate: boolean
}>()

const commentsStore = useCommentsStore()

import MentorRequestBlock from './MentorRequestBlock.vue'

const emit = defineEmits<{
  edit: [comment: TaskComment]
  delete: [comment: TaskComment]
}>()

function handleCommentSubmit(content: string) {
  commentsStore.createComment(props.taskId, { content })
}

async function handleEdit(comment: TaskComment) {
  await commentsStore.updateComment(comment.id, { content: comment.content })
}

async function handleDelete(comment: TaskComment) {
  if (confirm('Are you sure you want to delete this comment?')) {
    await commentsStore.deleteComment(comment.id)
  }
}

function shouldHideAvatar(comment: TaskComment, index: number) {
  if (index === 0) return false
  const prev = commentsStore.activeTaskComments[index - 1]
  if (!prev) return false

  // Group if same owner and within 5 minutes
  if (prev.owner_username === comment.owner_username) {
    const prevTime = new Date(prev.created_at).getTime()
    const currTime = new Date(comment.created_at).getTime()
    return currTime - prevTime < 5 * 60 * 1000
  }
  return false
}
</script>

<template>
  <div class="flex flex-col h-full relative overflow-hidden bg-transparent">
    <!-- Comments Scroll Area -->
    <div class="flex-1 overflow-y-auto px-4 py-4 custom-scrollbar flex flex-col">
      <MentorRequestBlock :taskId="taskId" />

      <div
        v-if="commentsStore.loading && commentsStore.activeTaskComments.length === 0"
        class="m-auto text-neutral-gray text-sm"
      >
        Loading comments...
      </div>
      <div
        v-else-if="commentsStore.activeTaskComments.length === 0"
        class="m-auto text-neutral-gray text-sm text-center"
      >
        No comments yet.<br />
        <span v-if="canCreate">Start the discussion!</span>
      </div>

      <div v-else class="flex flex-col pb-4">
        <CommentItem
          v-for="(comment, idx) in commentsStore.activeTaskComments"
          :key="comment.id"
          :comment="comment"
          :hideAvatar="shouldHideAvatar(comment, idx)"
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </div>
    </div>

    <!-- Input -->
    <CommentInput v-if="canCreate" @submit="handleCommentSubmit" />
    <div v-else class="p-4 text-center text-xs text-neutral-gray border-t border-border-gray">
      You do not have permission to post a comment here.
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border-gray);
  border-radius: 10px;
}
</style>

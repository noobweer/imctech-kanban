<script setup lang="ts">
import { computed } from 'vue'
import type { MentorRequest } from '@/types/mentorRequest'
import { LifeBuoy, Search } from 'lucide-vue-next'
import { format } from 'date-fns'

const props = defineProps<{
  request: MentorRequest
}>()

const emit = defineEmits<{
  click: [request: MentorRequest]
}>()

const badgeClass = computed(() => {
  return props.request.request_type === 'help'
    ? 'bg-[#ff9800]/10 text-[#e65100]'
    : 'bg-[#2196f3]/10 text-[#0d47a1]'
})

const statusClass = computed(() => {
  return props.request.status === 'open'
    ? 'bg-[var(--color-error)]'
    : props.request.status === 'in_progress'
      ? 'bg-primary-container'
      : 'bg-neutral-gray'
})

const formattedDate = computed(() => {
  return format(new Date(props.request.created_at), 'MMM d, HH:mm')
})
</script>

<template>
  <div
    class="bg-white p-4 md:p-5 rounded-xl border border-border-gray shadow-sm hover:shadow-lg hover:border-primary-container/50 transition-all duration-200 flex flex-col gap-3 cursor-pointer group relative overflow-hidden"
    @click="emit('click', request)"
  >
    <!-- Left Indicator -->
    <div class="absolute left-0 top-0 bottom-0 w-1" :class="statusClass"></div>

    <div class="flex justify-between items-start gap-2">
      <div class="flex flex-col gap-1.5">
        <div class="flex items-center gap-2">
          <span
            class="px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wide uppercase"
            :class="badgeClass"
          >
            <component
              :is="request.request_type === 'help' ? LifeBuoy : Search"
              :size="12"
              class="inline mr-0.5 -mt-0.5"
            />
            {{ request.request_type === 'help' ? 'Help Needed' : 'Review Requested' }}
          </span>
          <span
            class="text-[10px] font-bold tracking-wide uppercase flex items-center gap-1"
            :class="
              request.status === 'open' ? 'text-[var(--color-error)]' : 'text-primary-container'
            "
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="[statusClass, request.status === 'open' ? 'animate-pulse' : '']"
            ></span>
            {{ request.status.replace('_', ' ') }}
          </span>
        </div>

        <h3
          class="font-sub-heading text-[16px] font-bold text-on-surface leading-tight mt-1 group-hover:text-primary-container transition-colors"
        >
          {{ request.task_title }}
        </h3>
      </div>
    </div>

    <p class="text-sm text-on-surface/90 line-clamp-2 mt-1">
      <span class="font-bold">{{ request.created_by_username }}:</span> {{ request.message }}
    </p>

    <div class="flex items-end justify-between mt-auto pt-3">
      <span class="text-[11px] text-neutral-gray/80 font-medium">
        {{ formattedDate }}
      </span>

      <img
        :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(request.created_by_username)}&background=7132f5&color=fff&size=64`"
        class="w-6 h-6 rounded-full shadow-sm"
        :title="request.created_by_username"
      />
    </div>
  </div>
</template>

<style scoped>
.font-sub-heading {
  font-family: 'Space Grotesk', sans-serif;
}
</style>

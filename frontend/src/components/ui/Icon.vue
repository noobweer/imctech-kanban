<script setup lang="ts">
import { computed } from 'vue'
import { Mail, LockOpen, User, GraduationCap, Star } from 'lucide-vue-next'

interface Props {
  name: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

const sizeMap = {
  sm: 20,
  md: 24,
  lg: 32,
}

const iconMap: Record<string, any> = {
  alternate_email: Mail,
  lock_open: LockOpen,
  person: User,
  school: GraduationCap,
  star: Star,
}

const IconComponent = computed(() => iconMap[props.name])
const iconSize = computed(() => sizeMap[props.size])
</script>

<template>
  <component :is="IconComponent" v-if="IconComponent" :size="iconSize" :stroke-width="2" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { AtSign, LockOpen, User, GraduationCap, Star, Settings, LogOut, Users, Archive, Trash2, X } from 'lucide-vue-next'

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
  alternate_email: AtSign,
  lock_open: LockOpen,
  person: User,
  school: GraduationCap,
  star: Star,
  settings: Settings,
  logout: LogOut,
  users: Users,
  archive: Archive,
  trash: Trash2,
  x: X,
}

const IconComponent = computed(() => iconMap[props.name])
const iconSize = computed(() => sizeMap[props.size])
</script>

<template>
  <component :is="IconComponent" v-if="IconComponent" :size="iconSize" :stroke-width="2" />
</template>

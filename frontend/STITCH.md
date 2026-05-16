# Stitch → Vue3 Migration Guide

Quick reference for migrating Stitch screens to Vue3.

## Critical Rules

1. **NEVER use `mcp_stitch_get_screen` to fetch HTML** - it returns "OK" without code. Always ask the user for raw HTML.
2. **Copy exact HTML structure** - match classes, nesting, spacing exactly
3. **Use lucide-vue-next for icons** - Material Symbols cause DOMException errors
4. **CSS custom properties for Tailwind 4** - no @theme syntax, use :root vars
5. **Inline styles in components** - don't extract to separate Input/Button components unless reused 3+ times

## Process

### 1. Get Screen HTML

```typescript
mcp__stitch__get_screen({
  name: "projects/{projectId}/screens/{screenId}",
  projectId: "5379286775200031920",
  screenId: "..."
})
```

Download `htmlCode.downloadUrl` - this is source of truth.

### 2. Analyze Structure

Open HTML, identify:
- Layout (split, centered, grid)
- Form fields and validation
- Interactive elements (tabs, toggles, buttons)
- Icons used
- Spacing/padding patterns

### 3. Create Types

```typescript
// types/auth.ts
export interface LoginCredentials {
  email: string
  password: string
}
```

### 4. Build View

Copy HTML structure exactly. Match:
- Class names (especially spacing: `pl-4 pr-12 py-3`)
- Border radius (`rounded-xl`)
- Colors (`border-border-gray/50`)
- Icon positions (`right-3 top-1/2 -translate-y-1/2`)
- Focus states (`focus:border-primary-container focus:ring-2`)

Example:
```vue
<input
  class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50 bg-surface-container-lowest text-[16px] font-medium transition-colors focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-primary-container/20"
/>
<div class="absolute right-3 top-1/2 -translate-y-1/2">
  <Icon name="alternate_email" size="sm" />
</div>
```

### 5. Add Icons

Use lucide-vue-next with static imports:

```vue
<script setup lang="ts">
import { Mail, LockOpen, User, GraduationCap, Star } from 'lucide-vue-next'

const iconMap: Record<string, any> = {
  alternate_email: Mail,
  lock_open: LockOpen,
  person: User,
  school: GraduationCap,
  star: Star,
}

const IconComponent = computed(() => iconMap[props.name])
</script>

<template>
  <component :is="IconComponent" :size="iconSize" :stroke-width="2" />
</template>
```

### 6. Add CSS Custom Properties

If Tailwind classes don't work, add to `style.css`:

```css
:root {
  --color-primary: #5800d8;
  --color-primary-container: #7132f5;
  --color-border-gray: #dedee5;
}

.bg-primary { background-color: var(--color-primary); }
.border-border-gray { border-color: var(--color-border-gray); }
.border-border-gray\/50 { border-color: rgba(222, 222, 229, 0.5); }
.focus\:ring-2:focus { box-shadow: 0 0 0 2px rgba(113, 50, 245, 0.2); }
```

### 7. Add Route

```typescript
// router/index.ts
{
  path: '/auth',
  name: 'auth',
  component: () => import('@/views/AuthView.vue'),
}
```

### 8. Create Store (if needed)

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const loading = ref(false)
  
  async function login(credentials: LoginCredentials) {
    loading.value = true
    try {
      // API call
    } finally {
      loading.value = false
    }
  }
  
  return { user, loading, login }
})
```

## Design Tokens

**Colors:**
- `primary` (#5800d8), `primary-container` (#7132f5)
- `surface-white` (#ffffff), `surface-container-low` (#f8f1ff)
- `text-primary` (#101114), `text-secondary` (#9497a9)
- `border-gray` (#dedee5), `outline` (#7a7488)

**Spacing:**
- `p-xs` (4px), `p-sm` (8px), `p-md` (12px), `p-gutter` (16px), `p-lg` (24px)

**Typography:**
- Body: Inter 16px
- Headings: Space Grotesk

## Common Patterns

**Input with icon:**
```vue
<div class="relative">
  <input class="w-full pl-4 pr-12 py-3 rounded-xl border border-border-gray/50" />
  <div class="absolute right-3 top-1/2 -translate-y-1/2">
    <Icon name="alternate_email" size="sm" />
  </div>
</div>
```

**Toggle buttons:**
```vue
<div class="bg-surface-container-low p-xs rounded-xl flex">
  <button :class="active ? 'bg-surface-white shadow-[0_4px_24px_rgba(0,0,0,0.03)]' : 'text-neutral-gray'">
    Option 1
  </button>
</div>
```

**Primary button:**
```vue
<button class="w-full bg-primary-container text-white py-md px-lg rounded-xl text-[16px] font-semibold shadow-[0_4px_24px_rgba(113,50,245,0.2)] hover:opacity-90 active:scale-[0.98] transition-all">
  Submit
</button>
```

## Verification

1. `bun run dev` - no errors
2. Navigate to route - page renders
3. Compare with Stitch HTML - structure matches exactly
4. Test interactions - validation, toggles, focus states work
5. Check responsive - mobile/desktop layouts correct

## Troubleshooting

**Icons not showing:** Check lucide-vue-next installed, imports correct
**Styles broken:** Add CSS custom properties to style.css
**Input borders wrong:** Use explicit rgba values for opacity variants
**Spacing off:** Copy exact Tailwind classes from Stitch HTML (pl-4 not pl-3)

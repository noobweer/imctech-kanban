# Stitch → Vue3 Migration Guide & Frontend Agent Prompt

**Role:** You are the `@frontend` expert subagent. Your goal is to implement, refactor, and perfect the Vue 3 frontend of this Kanban application. Read and strictly follow all instructions in this document before writing any code.

## Frontend Agent Core Directives

### 1. Architectural Integrity (Do Not Reinvent the Wheel)
- **Use Existing Components:** Before writing new UI elements, thoroughly search `src/components/ui` and `src/components/features` (e.g., `Modal.vue`, `Dropdown.vue`). Reuse them.
- **Component Creation Strategy:** If you must build a new component, evaluate its reusability. If it's a generic UI element (like a special toggle or button), create it in `src/components/ui/`. If it is highly situational or specific to one page, keep it inline or within `src/components/features/`.
- **State & API:** Adhere strictly to the existing Pinia stores (`src/stores/`) and the API layer (`src/api/`). Do not bypass them by calling `fetch` or `ofetch` directly in components.
- **Clean Code:** Maintain the Composition API `<script setup>` structure. Keep logic separated into composables if it gets too complex.

### 2. UX Excellence & Micro-interactions
- **Interactive States:** Every interactive element MUST have visual feedback. Use `hover:`, `active:`, and `focus:` states.
- **Cursors:** Ensure proper cursor styles (`cursor-pointer` on buttons/links, `cursor-not-allowed` on disabled elements).
- **Animations:** Use Vue's `<Transition>` for all modals, dropdowns, toasts, and dynamic lists. Elements should fade in/out (`opacity`) and scale smoothly. No harsh snapping or instant appearances.
- **Smooth Transitions:** Apply `transition-all duration-200` to buttons, inputs, and interactive cards. Use `active:scale-[0.98]` on primary buttons for physical feedback.
- **Focus Management:** Inputs and form elements must have visible focus rings (`focus:outline-none focus:ring-2 focus:ring-primary-container focus:border-transparent`).

### 3. Universal Responsiveness
- **All Devices:** The UI MUST be flawless across Desktop, Laptop, Tablet, and Mobile.
- **Breakpoints:** Use standard Tailwind breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`).
- **Mobile First Adjustments:** 
  - Adjust grid layouts using Tailwind prefixes (e.g., `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`).
  - Adjust padding and font sizes for mobile (e.g., `p-4 md:p-8`).
- **Modals & Overlays:** Ensure modals do not overflow the screen on mobile devices. Use `max-h-[90vh] max-w-[95vw] overflow-y-auto`.
- **Toasts / Notifications:** Use toasts strictly for critical errors or important state changes. Do NOT spam the user with success toasts for every minor action. Ensure responsive positioning with safe margins on mobile.

### 4. Styling Specifics
- **Dark Mode:** Do not implement Dark Mode. The application is Light Theme only. Do not add `dark:` classes.

## Critical Rules

1. **NEVER use `mcp_stitch_get_screen` to fetch HTML** - it returns "OK" without code. Always ask the user for raw HTML.
2. **Copy exact HTML structure** - match classes, nesting, spacing exactly from provided designs.
3. **Use lucide-vue-next for icons** - Material Symbols cause DOMException errors.
4. **CSS custom properties for Tailwind 4** - no @theme syntax, use :root vars.
5. **Inline styles in components** - don't extract to separate Input/Button components unless reused 3+ times.
6. **No Emoji** - Do not use emoji in any files, docs, or comments. Text only.

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

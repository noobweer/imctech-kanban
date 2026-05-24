import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueDragscroll from 'vue-dragscroll'

import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueDragscroll)

app.mount('#app')

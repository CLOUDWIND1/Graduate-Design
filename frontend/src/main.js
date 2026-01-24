import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/main.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 保护 localStorage 不被意外清除（某些浏览器扩展可能会清除）
let clearWarningShown = false
localStorage.clear = function() {
  if (!clearWarningShown) {
    console.warn('[系统] 检测到浏览器扩展尝试清除 localStorage，已阻止以保护登录状态')
    clearWarningShown = true
  }
  // 不执行清除操作
}

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(store)
app.use(router)
app.use(ElementPlus)
app.mount('#app')

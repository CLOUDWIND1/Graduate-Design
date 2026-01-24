/**
 * Pinia Store
 * 文件名：src/store/index.js
 */

import { createPinia, defineStore } from 'pinia'
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '@/api/auth'

// 创建 Pinia 实例
const pinia = createPinia()

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userInfo: (state) => state.user,
    isAdmin: (state) => state.user?.role === 'admin'
  },
  
  actions: {
    async login(username, password) {
      try {
        const res = await apiLogin(username, password)
        console.log('[Store] 登录响应:', res)
        this.token = res.access_token
        localStorage.setItem('token', res.access_token)
        console.log('[Store] Token已保存:', res.access_token?.substring(0, 20) + '...')
        
        // 获取用户信息
        await this.fetchUserInfo()
        return true
      } catch (error) {
        console.error('[Store] 登录失败:', error)
        return false
      }
    },
    
    async fetchUserInfo() {
      try {
        console.log('[Store] 开始获取用户信息, token:', localStorage.getItem('token')?.substring(0, 20) + '...')
        const user = await getCurrentUser()
        console.log('[Store] 用户信息:', user)
        this.user = user
        localStorage.setItem('user', JSON.stringify(user))
      } catch (error) {
        console.error('[Store] 获取用户信息失败', error)
      }
    },
    
    async logout() {
      try {
        await apiLogout()
      } finally {
        this.token = ''
        this.user = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }
})

// 兼容Vuex的mapGetters
export const mapGetters = (getters) => {
  const result = {}
  const store = useUserStore()
  getters.forEach(getter => {
    result[getter] = () => store[getter]
  })
  return result
}

// 默认导出 Pinia 实例
export default pinia

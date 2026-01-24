/**
 * API客户端配置
 * 文件名：src/api/index.js
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 防止重复跳转
let isRedirecting = false

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    console.log('[API] ========== 请求开始 ==========')
    console.log('[API] URL:', config.url)
    console.log('[API] localStorage token:', token ? token.substring(0, 50) + '...' : 'NULL')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('[API] 已设置 Authorization header')
    } else {
      console.log('[API] 警告：没有 token！')
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // console.log('[API] Response:', response.config.url, response.data)
    return response.data
  },
  error => {
    console.error('[API] Error:', error.config?.url, error.response?.status, error.response?.data)
    const message = error.response?.data?.detail || '请求失败'
    
    if (error.response?.status === 401) {
      // 防止重复跳转
      if (!isRedirecting && window.location.pathname !== '/login') {
        isRedirecting = true
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login').finally(() => {
          isRedirecting = false
        })
      }
    } else {
      ElMessage.error(message)
    }
    
    return Promise.reject(error)
  }
)

export default api

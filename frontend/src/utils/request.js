/**
 * HTTP请求封装
 * 文件名：src/utils/request.js
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_BASE_API || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    console.log(`[Request] ${config.method?.toUpperCase()} ${config.url}`)
    console.log(`[Request] Token存在: ${!!token}, 值: ${token ? token.substring(0, 30) + '...' : 'null'}`)
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data
    // 后端直接返回数据对象，无 code 包装
    if (res.code !== undefined) {
      // 兼容有 code 包装的响应
      if (res.code === 200 || res.code === 0) {
        return res.data || res
      } else {
        ElMessage.error(res.message || '请求失败')
        return Promise.reject(new Error(res.message || '请求失败'))
      }
    }
    // 直接返回数据
    return res
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // token过期，只在非登录页时跳转，避免循环
        if (window.location.pathname !== '/login') {
          localStorage.removeItem('token')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
        }
      } else {
        ElMessage.error(data?.message || data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
    return Promise.reject(error)
  }
)

export default service
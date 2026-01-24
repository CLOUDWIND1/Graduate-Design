/**
 * 认证相关API
 * 文件名：src/api/auth.js
 */

import api from './index'

// 登录
export const login = (username, password) => {
  return api.post('/auth/login', { username, password })
}

// 注册
export const register = (userData) => {
  return api.post('/auth/register', userData)
}

// 登出
export const logout = () => {
  return api.post('/auth/logout')
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return api.get('/users/me')
}

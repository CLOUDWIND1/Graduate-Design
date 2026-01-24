/**
 * 用户相关API
 * 文件名：src/api/user.js
 */

import api from './index'

// 获取用户画像
export const getUserProfile = () => {
  return api.get('/users/profile')
}

// 更新用户画像
export const updateUserProfile = (profileData) => {
  return api.put('/users/profile', profileData)
}

// 获取用户列表（管理员）
export const getUsers = (skip = 0, limit = 20) => {
  return api.get('/admin/users', { params: { skip, limit } })
}

// 更新用户状态（管理员）
export const updateUserStatus = (userId, status) => {
  return api.put(`/admin/users/${userId}/status`, { status })
}

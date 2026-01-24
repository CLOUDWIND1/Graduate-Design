/**
 * 管理端 API
 * 文件名：src/api/admin.js
 */

import request from '@/utils/request'

/**
 * 获取仪表盘统计数据
 */
export function getDashboardStats() {
  return request({
    url: '/admin/dashboard',
    method: 'get'
  })
}

/**
 * 获取用户列表
 * @param {Object} params - 分页参数 { page, page_size }
 */
export function getUserList(params) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

/**
 * 获取用户统计信息
 */
export function getUserStats() {
  return request({
    url: '/admin/users/stats',
    method: 'get'
  })
}

/**
 * 获取活动统计信息
 */
export function getActivityStats() {
  return request({
    url: '/admin/activities/stats',
    method: 'get'
  })
}

/**
 * 更新用户状态
 * @param {number} userId - 用户ID
 * @param {Object} data - 状态数据
 */
export function updateUserStatus(userId, data) {
  return request({
    url: `/admin/users/${userId}/status`,
    method: 'put',
    data
  })
}

/**
 * 获取系统配置
 */
export function getSystemConfig() {
  return request({
    url: '/admin/config',
    method: 'get'
  })
}

/**
 * 更新系统配置
 * @param {Object} config - 配置数据
 */
export function updateSystemConfig(config) {
  return request({
    url: '/admin/config',
    method: 'put',
    data: config
  })
}

/**
 * 获取推荐系统配置
 */
export function getRecommendationConfig() {
  return request({
    url: '/admin/recommendation-config',
    method: 'get'
  })
}

/**
 * 更新推荐系统配置
 * @param {Object} config - 推荐配置
 */
export function updateRecommendationConfig(config) {
  return request({
    url: '/admin/recommendation-config',
    method: 'put',
    data: config
  })
}

/**
 * 获取用户潜力分析数据
 */
export function getUserPotentialAnalysis() {
  return request({
    url: '/admin/potential-analysis/',
    method: 'get'
  })
}

/**
 * 获取各维度策略建议
 */
export function getDimensionStrategies() {
  return request({
    url: '/admin/dimension-strategies/',
    method: 'get'
  })
}

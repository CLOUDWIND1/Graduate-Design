/**
 * 活动相关 API
 * 文件名：src/api/activities.js
 */

import api from './index'

/**
 * 获取活动列表
 * @param {Object} params - 查询参数
 */
export function getActivities(params = {}) {
  return api.get('/activities/', { params })
}

/**
 * 获取活动详情
 * @param {number} id - 活动ID
 */
export function getActivity(id) {
  return api.get(`/activities/${id}`)
}

/**
 * 创建活动
 * @param {Object} data - 活动数据
 */
export function createActivity(data) {
  return api.post('/activities/', data)
}

/**
 * 更新活动
 * @param {number} id - 活动ID
 * @param {Object} data - 活动数据
 */
export function updateActivity(id, data) {
  return api.put(`/activities/${id}`, data)
}

/**
 * 删除活动
 * @param {number} id - 活动ID
 */
export function deleteActivity(id) {
  return api.delete(`/activities/${id}`)
}

/**
 * 参与活动
 * @param {number} id - 活动ID
 */
export function participateActivity(id) {
  return api.post(`/activities/${id}/participate`)
}

/**
 * 获取活动统计
 */
export function getActivityStats() {
  return api.get('/admin/activities/stats')
}

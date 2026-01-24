/**
 * 推荐相关API
 * 文件名：src/api/recommendation.js
 */

import api from './index'

// 获取推荐列表
export const getRecommendations = (limit = 10, refresh = false) => {
  return api.get('/recommendations/', { params: { limit, refresh } })
}

// 记录反馈
export const recordFeedback = (activityId, feedback) => {
  return api.post(`/recommendations/${activityId}/feedback`, feedback)
}

// 记录点击
export const recordClick = (activityId) => {
  return api.post(`/recommendations/${activityId}/click`)
}

// 记录接受
export const recordAccept = (activityId) => {
  return api.post(`/recommendations/${activityId}/accept`)
}

// 获取推荐解释
export const getExplanation = (activityId) => {
  return api.get(`/recommendations/explain/${activityId}`)
}

// 获取推荐统计
export const getStats = () => {
  return api.get('/recommendations/stats')
}

// 获取推荐历史
export const getHistory = (skip = 0, limit = 20) => {
  return api.get('/recommendations/history', { params: { skip, limit } })
}

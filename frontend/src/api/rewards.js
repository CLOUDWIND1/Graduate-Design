/**
 * 奖励相关 API
 * 文件名：src/api/rewards.js
 */

import api from './index'

/**
 * 获取奖励列表
 * @param {Object} params - 分页参数 { page, page_size, reward_type, status }
 */
export function getRewards(params = {}) {
  return api.get('/rewards/', { params })
}

/**
 * 获取奖励汇总
 */
export function getRewardsSummary() {
  return api.get('/rewards/summary')
}

/**
 * 领取奖励
 * @param {number} rewardId - 奖励ID
 */
export function claimReward(rewardId) {
  return api.post(`/rewards/${rewardId}/claim`)
}

/**
 * 获取奖励详情
 * @param {number} rewardId - 奖励ID
 */
export function getRewardDetail(rewardId) {
  return api.get(`/rewards/${rewardId}`)
}

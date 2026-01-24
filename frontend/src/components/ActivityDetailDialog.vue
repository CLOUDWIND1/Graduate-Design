<template>
  <el-dialog 
    :model-value="visible" 
    @update:model-value="$emit('update:visible', $event)"
    title="活动详情" 
    width="600px"
    :append-to-body="true"
    :destroy-on-close="false"
  >
    <div v-if="activity" class="activity-detail">
      <div class="detail-header">
        <h2>{{ activity.title || activity.name }}</h2>
        <el-tag :type="getIncentiveTagType(activity.incentive_type)">
          {{ getIncentiveLabel(activity.incentive_type) }}
        </el-tag>
      </div>
      
      <div class="detail-meta">
        <div class="meta-item reward-item" :class="'reward-' + activity.incentive_type">
          <el-icon><Money /></el-icon>
          <span class="reward-text">{{ getRewardDisplay(activity) }}</span>
        </div>
        <div class="meta-item" v-if="activity.start_time">
          <el-icon><Clock /></el-icon>
          <span>开始: {{ formatDate(activity.start_time) }}</span>
        </div>
        <div class="meta-item" v-if="activity.end_time">
          <el-icon><Clock /></el-icon>
          <span>截止: {{ formatDate(activity.end_time) }}</span>
        </div>
        <div class="meta-item" v-if="activity.type">
          <el-icon><Ticket /></el-icon>
          <span>类型: {{ activity.type }}</span>
        </div>
      </div>
      
      <div class="detail-section">
        <h4>活动描述</h4>
        <p>{{ activity.description || '暂无描述' }}</p>
      </div>
      
      <div class="detail-section" v-if="activity.reason">
        <h4>推荐理由</h4>
        <p class="reason-text">{{ activity.reason }}</p>
      </div>
      
      <div class="detail-section" v-if="activity.score">
        <h4>匹配度</h4>
        <el-progress 
          :percentage="Math.round(activity.score * 100)" 
          :format="(p) => p.toFixed(1) + '%'"
          :color="getScoreColor(activity.score)"
        />
      </div>

      <div class="detail-section" v-if="activity.rules">
        <h4>活动规则</h4>
        <p>{{ activity.rules }}</p>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:visible', false)">关闭</el-button>
      <el-button type="primary" @click="$emit('participate', activity)">
        立即参与
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { Money, Clock, Ticket } from '@element-plus/icons-vue'

defineProps({
  visible: Boolean,
  activity: Object
})

defineEmits(['update:visible', 'participate'])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getScoreColor = (score) => {
  if (score >= 0.8) return '#67C23A'
  if (score >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

const getIncentiveLabel = (type) => {
  const labels = {
    'red_packet': '现金红包',
    'points': '积分奖励',
    'coupon': '优惠券'
  }
  return labels[type] || '奖励'
}

const getIncentiveUnit = (type) => {
  return type === 'points' ? '积分' : '元'
}

const getRewardDisplay = (activity) => {
  const amount = activity.incentive_amount || activity.points || 0
  const type = activity.incentive_type
  
  switch (type) {
    case 'red_packet':
      return `🧧 现金红包 ${amount} 元`
    case 'points':
      return `⭐ 积分奖励 ${amount} 积分`
    case 'coupon':
      return `🎫 优惠券 ${amount} 元`
    default:
      return `奖励 ${amount}`
  }
}

const getIncentiveTagType = (type) => {
  const types = {
    'red_packet': 'success',
    'points': 'warning',
    'coupon': 'danger'
  }
  return types[type] || 'info'
}
</script>

<style scoped>
.activity-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.detail-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.detail-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
}

.reward-item {
  font-weight: 600;
}

.reward-item.reward-red_packet {
  color: #f56c6c;
}

.reward-item.reward-points {
  color: #e6a23c;
}

.reward-item.reward-coupon {
  color: #409eff;
}

.reward-text {
  font-size: 15px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.detail-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.reason-text {
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  border-left: 3px solid #409EFF;
}
</style>

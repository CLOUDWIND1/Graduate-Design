<!--
推荐卡片组件
文件名：src/components/RecommendationCard.vue
-->

<template>
  <div class="recommendation-card" @click="handleClick">
    <div class="card-header">
      <h3 class="card-title">{{ activity.title }}</h3>
      <div class="card-badges">
        <el-tag :type="incentiveTagType" size="small" effect="light" round>
          {{ incentiveLabel }}
        </el-tag>
      </div>
    </div>
    
    <p class="card-description">{{ activity.description }}</p>
    
    <div class="card-body">
      <div class="reward-pill">
        <el-icon class="reward-icon"><Money /></el-icon>
        <span>{{ activity.incentive_amount }} {{ incentiveUnit }}</span>
      </div>
      
      <div class="reason-box">
        <el-icon class="reason-icon"><MagicStick /></el-icon>
        <span class="reason-text">{{ activity.reason }}</span>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="match-score">
        <span class="score-label">匹配度</span>
        <div class="score-bar">
          <div class="score-fill" :style="{ width: (activity.score * 100) + '%', background: scoreColor }"></div>
        </div>
        <span class="score-val" :style="{ color: scoreColor }">{{ (activity.score * 100).toFixed(0) }}%</span>
      </div>
      
      <el-button type="primary" size="default" class="action-btn" @click.stop="handleParticipate">
        立即参与
      </el-button>
    </div>
  </div>
</template>

<script>
import { Money, MagicStick } from '@element-plus/icons-vue'

export default {
  name: 'RecommendationCard',
  components: { Money, MagicStick },
  props: {
    activity: {
      type: Object,
      required: true
    }
  },
  computed: {
    incentiveLabel() {
      const labels = {
        'red_packet': '现金红包',
        'points': '积分奖励',
        'coupon': '优惠券'
      }
      return labels[this.activity.incentive_type] || '奖励'
    },
    incentiveUnit() {
      return this.activity.incentive_type === 'points' ? '积分' : '元'
    },
    incentiveTagType() {
      const types = {
        'red_packet': 'success',
        'points': 'warning',
        'coupon': 'danger'
      }
      return types[this.activity.incentive_type] || 'info'
    },
    scoreColor() {
      const score = this.activity.score
      if (score >= 0.8) return '#10B981' // emerald
      if (score >= 0.6) return '#3B82F6' // blue
      return '#F59E0B' // amber
    }
  },
  methods: {
    handleClick() {
      this.$emit('click', this.activity)
    },
    handleParticipate() {
      this.$emit('participate', this.activity)
    }
  }
}
</script>

<style scoped>
.recommendation-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid rgba(229, 231, 235, 0.5); /* gray-200 */
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.recommendation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border-color: rgba(59, 130, 246, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-description {
  color: #6B7280;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex-grow: 1;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.reward-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #FEF2F2;
  color: #EF4444;
  padding: 6px 12px;
  border-radius: 99px;
  font-size: 14px;
  font-weight: 600;
  width: fit-content;
}

.reason-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #F9FAFB;
  padding: 10px;
  border-radius: 12px;
  font-size: 13px;
  color: #4B5563;
}

.reason-icon {
  margin-top: 2px;
  color: #8B5CF6;
}

.card-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.match-score {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  font-size: 12px;
  color: #9CA3AF;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #F3F4F6;
  border-radius: 3px;
  overflow: hidden;
  max-width: 80px;
}

.score-fill {
  height: 100%;
  border-radius: 3px;
}

.score-val {
  font-size: 14px;
  font-weight: 700;
}

.action-btn {
  border-radius: 10px;
  padding: 8px 20px;
  font-weight: 600;
  transition: all 0.2s;
}

.action-btn:hover {
  transform: scale(1.05);
}
</style>
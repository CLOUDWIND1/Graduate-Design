<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>
      
      <!-- 用户基本信息 -->
      <div class="user-info">
        <el-avatar :size="80" :src="avatarUrl">
          {{ userInfo && userInfo.username ? userInfo.username.charAt(0).toUpperCase() : '' }}
        </el-avatar>
        <div class="user-details">
          <h2>{{ userInfo ? userInfo.username : '' }}</h2>
          <p>{{ userInfo ? userInfo.email : '' }}</p>
          <el-tag :type="isAdminUser ? 'danger' : 'primary'">
            {{ isAdminUser ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 用户画像 -->
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>我的画像</span>
          <div class="header-actions">
            <el-button 
              v-if="!questionnaireCompleted" 
              type="warning" 
              size="small" 
              @click="goToQuestionnaire"
            >
              完善问卷
            </el-button>
            <el-button type="primary" size="small" @click="refreshProfile" :loading="loading">
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 未完成问卷提示 -->
      <el-alert 
        v-if="!questionnaireCompleted"
        title="您还未完成偏好问卷"
        type="warning"
        description="完成问卷后，系统将为您提供更精准的个性化推荐"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <div v-if="profile" class="profile-factors">
        <div class="factor-item" v-for="factor in factors" :key="factor.key">
          <div class="factor-header">
            <span class="factor-name">{{ factor.name }}</span>
            <span class="factor-value">{{ (profile[factor.key] * 100).toFixed(0) }}%</span>
          </div>
          <el-progress 
            :percentage="profile[factor.key] * 100" 
            :color="factor.color"
            :stroke-width="12"
          />
        </div>
        
        <div class="cluster-info" v-if="profile.cluster_id !== undefined">
          <el-divider />
          <div class="cluster-label">
            <span>用户分群：</span>
            <el-tag type="success">{{ clusterLabels[profile.cluster_id] || '未分类' }}</el-tag>
          </div>
        </div>
      </div>
      
      <el-empty v-else description="暂无画像数据" />
    </el-card>

    <!-- 偏好设置 -->
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>偏好设置</span>
        </div>
      </template>
      
      <el-form :model="preferences" label-width="120px">
        <el-form-item label="推荐频率">
          <el-select v-model="preferences.frequency" placeholder="选择推荐频率">
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="实时" value="realtime" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="偏好活动类型">
          <el-checkbox-group v-model="preferences.activityTypes">
            <el-checkbox label="invite">邀请活动</el-checkbox>
            <el-checkbox label="quiz">答题活动</el-checkbox>
            <el-checkbox label="share">分享活动</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="偏好激励类型">
          <el-checkbox-group v-model="preferences.incentiveTypes">
            <el-checkbox label="red_packet">红包</el-checkbox>
            <el-checkbox label="points">积分</el-checkbox>
            <el-checkbox label="coupon">优惠券</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="savePreferences" :loading="saving">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计数据 -->
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>我的统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalRecommendations }}</div>
            <div class="stat-label">收到推荐</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-value">{{ stats.acceptedCount }}</div>
            <div class="stat-label">已接受</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalRewards }}</div>
            <div class="stat-label">获得奖励</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

const loading = ref(false)
const saving = ref(false)
const profile = ref(null)
const avatarUrl = ref('')
const questionnaireCompleted = ref(false)

const factors = [
  { key: 'factor_social', name: '社会因素', color: '#409EFF' },
  { key: 'factor_psych', name: '心理因素', color: '#67C23A' },
  { key: 'factor_incent', name: '激励因素', color: '#E6A23C' },
  { key: 'factor_tech', name: '技术因素', color: '#F56C6C' },
  { key: 'factor_env', name: '环境因素', color: '#909399' },
  { key: 'factor_personal', name: '个人因素', color: '#9B59B6' }
]

const clusterLabels = {
  0: '社交活跃型',
  1: '品牌忠诚型',
  2: '观望保守型',
  3: '高价值型',
  4: '互动参与型',
  5: '低频使用型',
  6: '稳定忠实型',
  7: '积极响应型',
  8: '潜在流失型',
  9: '深度粘性型'
}

const preferences = ref({
  frequency: 'daily',
  activityTypes: ['invite', 'quiz', 'share'],
  incentiveTypes: ['red_packet', 'points', 'coupon']
})

const stats = ref({
  totalRecommendations: 0,
  acceptedCount: 0,
  totalRewards: 0
})

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await api.get('/users/profile') // Fix: remove /me/ and trailing slash
    profile.value = res
  } catch (error) {
    console.error('获取画像失败', error)
  } finally {
    loading.value = false
  }
}

const fetchQuestionnaireStatus = async () => {
  try {
    const res = await api.get('/users/me') // Fix: use /me to get status
    questionnaireCompleted.value = !!res.questionnaire_completed
  } catch (error) {
    console.error('获取问卷状态失败', error)
  }
}

const goToQuestionnaire = () => {
  router.push('/questionnaire')
}

const fetchStats = async () => {
  try {
    // Parallel fetch for recommendations and rewards stats
    const [recStats, rewardSummary] = await Promise.all([
      api.get('/recommendations/stats'),
      api.get('/rewards/summary')
    ])
    
    // Map responses to stats object
    // recStats: { total_recommendations, click_rate, accept_rate, ... }
    // rewardSummary: { totalAmount, totalPoints, pendingCount }
    const totalRecs = recStats.total_recommendations || 0
    const acceptRate = recStats.accept_rate || 0
    
    stats.value = {
      totalRecommendations: totalRecs,
      acceptedCount: Math.round(totalRecs * acceptRate),
      totalRewards: rewardSummary.totalAmount || 0
    }
  } catch (error) {
    console.error('获取统计失败', error)
    // Fallback to zeros on error
    stats.value = {
      totalRecommendations: 0,
      acceptedCount: 0,
      totalRewards: 0
    }
  }
}

const refreshProfile = () => {
  fetchProfile()
}

const savePreferences = async () => {
  saving.value = true
  try {
    // Mock API call since backend doesn't support preferences yet
    await new Promise(resolve => setTimeout(resolve, 800))
    // await api.put('/users/me/preferences/', preferences.value) 
    ElMessage.success('保存成功 (模拟)')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProfile()
  fetchStats()
  fetchQuestionnaireStatus()
})
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.profile-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px 0;
}

.user-details h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.user-details p {
  margin: 0 0 12px 0;
  color: #909399;
}

.profile-factors {
  padding: 10px 0;
}

.factor-item {
  margin-bottom: 20px;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.factor-name {
  font-weight: 500;
}

.factor-value {
  color: #409EFF;
  font-weight: bold;
}

.cluster-info {
  text-align: center;
}

.cluster-label {
  font-size: 16px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  margin-top: 8px;
  color: #909399;
}
</style>

<template>
  <div class="recommendations-container">
    <div class="page-header">
      <h1>个性化推荐</h1>
      <p>基于您的画像和偏好，为您精选以下活动</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_recommendations }}</div>
          <div class="stat-label">推荐总数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ (stats.click_rate * 100).toFixed(1) }}%</div>
          <div class="stat-label">点击率</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ (stats.accept_rate * 100).toFixed(1) }}%</div>
          <div class="stat-label">接受率</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ recommendations.length }}</div>
          <div class="stat-label">当前推荐</div>
        </div>
      </el-col>
    </el-row>

    <!-- 推荐列表 -->
    <div class="recommendations-list" v-loading="loading">
      <el-row :gutter="16" v-if="recommendations.length > 0">
        <el-col :span="8" v-for="item in recommendations" :key="item.activity_id">
          <el-card class="rec-card" shadow="hover" @click="showDetail(item)">
            <div class="rec-header">
              <span class="rec-score">{{ (item.score * 100).toFixed(0) }}%</span>
              <span class="rec-type">{{ item.activity_type || '活动' }}</span>
            </div>
            <h3 class="rec-title">{{ item.title }}</h3>
            <p class="rec-desc">{{ item.description || '暂无描述' }}</p>
            <div class="rec-reason">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ item.reason || '根据您的偏好推荐' }}</span>
            </div>
            <div class="rec-actions">
              <el-button type="primary" size="small" @click.stop="handleAccept(item)">
                参与活动
              </el-button>
              <el-button size="small" @click.stop="showExplanation(item)">
                查看解释
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-else-if="!loading" description="暂无推荐内容" />
    </div>

    <!-- 解释弹窗 -->
    <el-dialog v-model="explainVisible" title="推荐解释" width="500px">
      <div v-if="explanation" class="explanation-content">
        <div class="explain-score">
          <span>预测接受概率：</span>
          <el-progress 
            :percentage="explanation.score * 100" 
            :format="(p) => p.toFixed(1) + '%'"
          />
        </div>
        <div class="explain-text">
          <h4>推荐理由</h4>
          <p>{{ explanation.explanation }}</p>
        </div>
        <div class="explain-factors" v-if="explanation.feature_importance && explanation.feature_importance.length > 0">
          <h4>影响因素</h4>
          <div v-for="item in explanation.feature_importance" :key="item.feature" class="factor-item">
            <span class="factor-name">{{ item.label || getFeatureName(item.feature) }}</span>
            <el-progress 
              :percentage="Math.round((item.importance || 0) * 100)" 
              :color="(item.contribution || item.importance) > 0 ? '#67C23A' : '#F56C6C'"
              :format="() => ((item.importance || 0) * 100).toFixed(1) + '%'"
            />
          </div>
        </div>
      </div>
      <div v-else class="loading-explain">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Loading } from '@element-plus/icons-vue'
import { getRecommendations, getStats, getExplanation, recordAccept } from '@/api/recommendation'

const loading = ref(false)
const recommendations = ref([])
const stats = ref({
  total_recommendations: 0,
  click_rate: 0,
  accept_rate: 0,
  top_features: []
})
const explainVisible = ref(false)
const explanation = ref(null)

// 特征名称映射
const featureNameMap = {
  factor_social: '社会因素',
  factor_psych: '心理因素',
  factor_incent: '激励因素',
  factor_tech: '技术因素',
  factor_env: '环境因素',
  factor_personal: '个人因素',
  incentive_amount: '激励金额',
  incentive_type_encoded: '激励类型',
  activity_type_encoded: '活动类型'
}

const getFeatureName = (name) => featureNameMap[name] || name

const loadData = async () => {
  loading.value = true
  try {
    const [recData, statsData] = await Promise.all([
      getRecommendations(12),
      getStats()
    ])
    recommendations.value = recData
    stats.value = statsData
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const showDetail = (item) => {
  // 可以跳转到详情页或显示弹窗
  console.log('查看详情', item)
}

const showExplanation = async (item) => {
  explainVisible.value = true
  explanation.value = null
  try {
    explanation.value = await getExplanation(item.activity_id)
  } catch (error) {
    ElMessage.error('获取解释失败')
    explainVisible.value = false
  }
}

const handleAccept = async (item) => {
  try {
    // 1. 记录接受反馈（更新用户画像）
    await recordAccept(item.activity_id)
    
    // 2. 参与活动（创建奖励）- 使用尾部斜杠避免307重定向
    const api = (await import('@/api')).default
    await api.post(`/activities/${item.activity_id}/participate/`)
    
    ElMessage.success(`已参与活动：${item.title}，奖励已发放！`)
    
    // 刷新统计数据
    const statsData = await getStats()
    stats.value = statsData
  } catch (error) {
    if (error.response?.data?.detail === '您已参与过该活动') {
      ElMessage.warning('您已参与过该活动')
    } else {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.recommendations-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  color: #fff;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 4px;
}

.rec-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.rec-card:hover {
  transform: translateY(-4px);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.rec-score {
  background: #67C23A;
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.rec-type {
  color: #909399;
  font-size: 12px;
}

.rec-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.rec-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rec-reason {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 12px;
  margin-bottom: 12px;
}

.rec-actions {
  display: flex;
  gap: 8px;
}

.explanation-content {
  padding: 10px 0;
}

.explain-score {
  margin-bottom: 20px;
}

.explain-text h4,
.explain-factors h4 {
  margin: 16px 0 8px 0;
  color: #303133;
}

.factor-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.factor-name {
  width: 100px;
  font-size: 13px;
  color: #606266;
}

.loading-explain {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>

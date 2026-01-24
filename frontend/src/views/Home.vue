<!--
推荐首页
文件名：src/views/Home.vue
-->

<template>
  <div class="home-container">
    <!-- 欢迎头部 & 用户画像 -->
    <div class="welcome-section glass-panel" v-if="userProfile">
      <div class="welcome-content">
        <h1 class="welcome-title">
          早安，<span class="highlight">{{ userInfo?.username || '用户' }}</span>
        </h1>
        <p class="welcome-subtitle">
          基于您的 <span class="tag-badge">{{ userProfile.cluster_tag }}</span> 特质，我们为您精选了以下活动
        </p>
      </div>
      
      <div class="factors-grid">
        <div class="factor-item" v-for="factor in factorList" :key="factor.name">
          <el-progress 
            type="dashboard" 
            :percentage="factor.score" 
            :width="54"
            :stroke-width="6"
            :color="factor.color"
          >
            <template #default="{ percentage }">
              <span class="factor-val">{{ percentage }}</span>
            </template>
          </el-progress>
          <span class="factor-label">{{ factor.label }}</span>
        </div>
      </div>
    </div>
    
    <!-- 推荐列表 -->
    <div class="recommendations-section">
      <div class="section-header">
        <div class="header-left">
          <h2>为您推荐</h2>
          <div class="header-decoration"></div>
        </div>
        <el-button text bg icon="Refresh" @click="refreshRecommendations">换一批</el-button>
      </div>
      
      <div v-loading="loading" class="rec-list-container">
        <el-row :gutter="24" v-if="recommendations.length > 0">
          <transition-group name="list">
            <el-col :span="8" v-for="(item, index) in recommendations" :key="item.activity_id" class="card-col" :style="{ '--delay': index * 0.1 + 's' }">
              <RecommendationCard 
                :activity="item"
                @click="viewDetail"
                @participate="handleParticipate"
              />
            </el-col>
          </transition-group>
        </el-row>
        
        <el-empty 
          v-else-if="!loading" 
          description="暂无推荐内容，请稍后再来" 
          :image-size="200"
        />
      </div>
    </div>
    
    <!-- 活动详情弹窗 -->
    <ActivityDetailDialog
      :visible="detailDialogVisible"
      :activity="selectedActivity"
      @update:visible="detailDialogVisible = $event"
      @participate="confirmParticipate"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import RecommendationCard from '@/components/RecommendationCard.vue'
import ActivityDetailDialog from '@/components/ActivityDetailDialog.vue'
import { getRecommendations, recordFeedback } from '@/api/recommendation'
import { getUserProfile } from '@/api/user'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)
const recommendations = ref([])
const userProfile = ref(null)
const detailDialogVisible = ref(false)
const selectedActivity = ref(null)

const userInfo = computed(() => userStore.userInfo)

const factorList = computed(() => {
  if (!userProfile.value) return []
  return [
    { name: 'social', label: '社会', score: Math.round(userProfile.value.factor_social * 100), color: '#3B82F6' },
    { name: 'psych', label: '心理', score: Math.round(userProfile.value.factor_psych * 100), color: '#10B981' },
    { name: 'incent', label: '激励', score: Math.round(userProfile.value.factor_incent * 100), color: '#F59E0B' },
    { name: 'tech', label: '技术', score: Math.round(userProfile.value.factor_tech * 100), color: '#6366F1' },
    { name: 'personal', label: '个人', score: Math.round(userProfile.value.factor_personal * 100), color: '#EC4899' }
  ]
})

const loadData = async () => {
  const token = userStore.token || localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }

  // Initial load
  loading.value = true
  try {
    const [_, profileData] = await Promise.allSettled([
      fetchRecommendations(),
      getUserProfile()
    ])
    
    if (profileData.status === 'fulfilled') {
      userProfile.value = profileData.value
    } else {
      userProfile.value = {
        cluster_tag: '新用户',
        factor_social: 0.5,
        factor_psych: 0.5,
        factor_incent: 0.5,
        factor_tech: 0.5,
        factor_env: 0.5,
        factor_personal: 0.5
      }
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const fetchRecommendations = async (refresh = false) => {
  try {
    const res = await getRecommendations(6, refresh)
    recommendations.value = res || []
    return true
  } catch (e) {
    console.error('获取推荐失败', e)
    recommendations.value = []
    return false
  }
}

const refreshRecommendations = async () => {
  loading.value = true
  try {
    await fetchRecommendations(true)
    ElMessage.success('已更新推荐内容')
  } finally {
    loading.value = false
  }
}

const viewDetail = (activity) => {
  selectedActivity.value = activity
  detailDialogVisible.value = true
}

const handleParticipate = (activity) => {
  selectedActivity.value = activity
  detailDialogVisible.value = true
}

const confirmParticipate = async (activity) => {
  try {
    const api = (await import('@/api')).default
    const actId = activity.activity_id || activity.id
    await api.post(`/activities/${actId}/participate/`)
    
    ElMessage.success(`参与成功！`)
    if (actId) {
      recordFeedback(actId, { is_clicked: true, is_accepted: true })
    }
    detailDialogVisible.value = false
  } catch (error) {
    ElMessage.warning('参与失败或已参与')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* User Profile Section */
.glass-panel {
  background: white;
  border-radius: 20px;
  padding: 32px 40px;
  margin-bottom: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.03);
  position: relative;
  overflow: hidden;
}

.glass-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), #3B82F6);
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #1F2937;
  margin: 0 0 12px 0;
}

.highlight {
  color: var(--primary-color);
  position: relative;
  z-index: 1;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 0;
  width: 100%;
  height: 8px;
  background: rgba(59, 130, 246, 0.15);
  z-index: -1;
  border-radius: 4px;
}

.welcome-subtitle {
  color: #6B7280;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-badge {
  background: #EFF6FF;
  color: var(--primary-color);
  padding: 2px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

.factors-grid {
  display: flex;
  gap: 24px;
}

.factor-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.factor-val {
  font-size: 12px;
  font-weight: 700;
  color: #374151;
}

.factor-label {
  font-size: 12px;
  color: #6B7280;
}

/* Recommendations Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.header-decoration {
  width: 40px;
  height: 2px;
  background: #E5E7EB;
  border-radius: 2px;
}

.card-col {
  margin-bottom: 24px;
  transition: all 0.5s ease;
}

/* List Transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.card-col {
  animation: slideIn 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
  animation-delay: var(--delay);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .glass-panel {
    flex-direction: column;
    align-items: flex-start;
    gap: 24px;
    padding: 24px;
  }
  
  .factors-grid {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
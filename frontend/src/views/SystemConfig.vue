<template>
  <div class="system-config">
    <el-tabs v-model="activeTab">
      <!-- 推荐参数配置 -->
      <el-tab-pane label="推荐参数" name="recommendation">
        <el-card>
          <template #header>
            <span>推荐算法参数</span>
          </template>
          
          <el-form :model="recommendConfig" label-width="180px">
            <el-form-item label="推荐数量上限">
              <el-input-number 
                v-model="recommendConfig.max_recommendations" 
                :min="1" 
                :max="50"
              />
              <span class="form-tip">每次推荐返回的最大活动数量</span>
            </el-form-item>
            
            <el-form-item label="冷启动推荐数量">
              <el-input-number 
                v-model="recommendConfig.cold_start_count" 
                :min="1" 
                :max="20"
              />
              <span class="form-tip">新用户推荐的热门活动数量</span>
            </el-form-item>
            
            <el-form-item label="最低推荐分数">
              <el-slider 
                v-model="recommendConfig.min_score" 
                :min="0" 
                :max="1" 
                :step="0.05"
                show-input
              />
              <span class="form-tip">低于此分数的活动不会被推荐</span>
            </el-form-item>
            
            <el-form-item label="多样性权重">
              <el-slider 
                v-model="recommendConfig.diversity_weight" 
                :min="0" 
                :max="1" 
                :step="0.1"
                show-input
              />
              <span class="form-tip">控制推荐结果的多样性程度</span>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveRecommendConfig" :loading="saving">
                保存配置
              </el-button>
              <el-button @click="resetRecommendConfig">重置默认</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 模型配置 -->
      <el-tab-pane label="模型配置" name="model">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>机器学习模型</span>
              <el-button type="primary" @click="trainModel" :loading="training">
                重新训练
              </el-button>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="模型类型">
              {{ modelInfo.model_type || 'RandomForest' }}
            </el-descriptions-item>
            <el-descriptions-item label="训练时间">
              {{ modelInfo.trained_at || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="准确率">
              {{ modelInfo.accuracy ? (modelInfo.accuracy * 100).toFixed(2) + '%' : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="AUC">
              {{ modelInfo.auc ? modelInfo.auc.toFixed(4) : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="训练样本数">
              {{ modelInfo.train_samples || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="测试样本数">
              {{ modelInfo.test_samples || '-' }}
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <h4>特征重要性</h4>
          <div class="feature-importance" v-if="modelInfo.feature_importance && Object.keys(modelInfo.feature_importance).length > 0">
            <div 
              v-for="(value, name) in modelInfo.feature_importance" 
              :key="name"
              class="feature-item"
            >
              <span class="feature-name">{{ getFeatureName(name) }}</span>
              <el-progress 
                :percentage="Math.round(Number(value) * 100)" 
                :stroke-width="16"
                :format="() => (Number(value) * 100).toFixed(1) + '%'"
              />
            </div>
          </div>
          <el-empty v-else description="暂无特征重要性数据" />
        </el-card>
      </el-tab-pane>

      <!-- 聚类配置 -->
      <el-tab-pane label="用户分群" name="clustering">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户聚类配置</span>
              <el-button type="primary" @click="recluster" :loading="clustering">
                重新聚类
              </el-button>
            </div>
          </template>
          
          <el-form :model="clusterConfig" label-width="120px">
            <el-form-item label="聚类数量">
              <el-input-number 
                v-model="clusterConfig.n_clusters" 
                :min="2" 
                :max="10"
              />
            </el-form-item>
          </el-form>
          
          <el-divider />
          
          <h4>聚类分布</h4>
          <el-table :data="clusterStats" stripe>
            <el-table-column prop="cluster_tag" label="聚类标签" />
            <el-table-column prop="count" label="用户数" width="100" />
            <el-table-column label="主导因子" min-width="180">
              <template #default="{ row }">
                {{ row.dominant_factor || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="平均因子" min-width="220">
              <template #default="{ row }">
                <div class="avg-factors" v-if="row.avg_factors">
                  <span v-for="(v, k) in row.avg_factors" :key="k" class="avg-factor">{{ getFactorLabel(k) }}: {{ v }}</span>
                </div>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 系统日志 -->
      <el-tab-pane label="系统日志" name="logs">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>操作日志</span>
              <el-button @click="fetchLogs">刷新</el-button>
            </div>
          </template>
          
          <el-form :inline="true" :model="logFilters" class="filter-form">
            <el-form-item label="日志级别">
              <el-select v-model="logFilters.level" placeholder="全部" clearable style="width: 180px">
                <el-option
                  v-for="item in logLevelOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="logFilters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchLogs">查询</el-button>
            </el-form-item>
          </el-form>
          
          <el-table :data="logs" v-loading="loadingLogs" stripe max-height="400">
            <el-table-column prop="timestamp" label="时间" width="180" />
            <el-table-column label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="getLogLevelTag(row.level)">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="消息" />
            <el-table-column prop="user" label="操作人" width="120" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const activeTab = ref('recommendation')
const saving = ref(false)
const training = ref(false)
const clustering = ref(false)
const loadingLogs = ref(false)

// 推荐配置
const recommendConfig = ref({
  max_recommendations: 10,
  cold_start_count: 5,
  min_score: 0.3,
  diversity_weight: 0.2
})

// 模型信息
const modelInfo = ref({})

// 聚类配置
const clusterConfig = ref({
  n_clusters: 10
})
const clusterStats = ref([])

// 日志
const logs = ref([])
const logFilters = ref({
  level: '',
  dateRange: []
})

const logLevelOptions = [
  { label: '全部', value: '' },
  { label: 'INFO', value: 'INFO' },
  { label: 'WARNING', value: 'WARNING' },
  { label: 'ERROR', value: 'ERROR' }
]

const featureNameMap = {
  factor_social: '社会因素',
  factor_psych: '心理因素',
  factor_incent: '激励因素',
  factor_tech: '技术因素',
  factor_env: '环境因素',
  factor_personal: '个人因素',
  social: '社会因素',
  psych: '心理因素',
  incent: '激励因素',
  tech: '技术因素',
  env: '环境因素',
  personal: '个人因素',
  factor_7: '因子7',
  factor_8: '因子8',
  factor_9: '因子9',
  incentive_amount: '激励金额',
  incentive_type_encoded: '激励类型',
  activity_type_encoded: '活动类型',
  feature_0: '特征0',
  feature_1: '特征1',
  feature_2: '特征2',
  feature_3: '特征3',
  feature_4: '特征4',
  feature_5: '特征5',
  feature_6: '特征6',
  feature_7: '特征7',
  feature_8: '特征8'
}

const fetchRecommendConfig = async () => {
  try {
    const res = await api.get('/admin/config/')
    recommendConfig.value = res
  } catch (error) {
    console.error('获取推荐配置失败', error)
  }
}

const saveRecommendConfig = async () => {
  saving.value = true
  try {
    await api.put('/admin/config/', recommendConfig.value)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetRecommendConfig = () => {
  recommendConfig.value = {
    max_recommendations: 10,
    cold_start_count: 5,
    min_score: 0.3,
    diversity_weight: 0.2
  }
}

const fetchModelInfo = async () => {
  try {
    const res = await api.get('/admin/model/info/')
    modelInfo.value = res
  } catch (error) {
    console.error('获取模型信息失败', error)
  }
}

const trainModel = async () => {
  training.value = true
  try {
    await api.post('/admin/model/train/')
    ElMessage.success('模型训练已启动')
    setTimeout(fetchModelInfo, 5000)
  } catch (error) {
    ElMessage.error('训练启动失败')
  } finally {
    training.value = false
  }
}

const fetchClusterStats = async () => {
  try {
    const res = await api.get('/admin/clusters/')
    const list = Array.isArray(res) ? res : []
    clusterStats.value = list.map((stat) => {
      const avgFactors = stat.avg_factors || {}
      return {
        cluster_tag: stat.cluster_tag || stat.label || '未分类',
        count: stat.count || stat.user_count || 0,
        avg_factors: avgFactors,
        dominant_factor: getDominantFactor(avgFactors)
      }
    })
  } catch (error) {
    console.error('获取聚类统计失败', error)
  }
}

const recluster = async () => {
  clustering.value = true
  try {
    await api.post('/admin/clusters/rebuild/', clusterConfig.value)
    ElMessage.success('重新聚类完成')
    fetchClusterStats()
  } catch (error) {
    ElMessage.error('聚类失败')
  } finally {
    clustering.value = false
  }
}

const fetchLogs = async () => {
  loadingLogs.value = true
  try {
    const params = { ...logFilters.value }
    if (params.dateRange?.length === 2) {
      params.start_date = params.dateRange[0]
      params.end_date = params.dateRange[1]
    }
    delete params.dateRange
    const res = await api.get('/admin/logs/', { params })
    logs.value = res.items || res
  } catch (error) {
    console.error('获取日志失败', error)
  } finally {
    loadingLogs.value = false
  }
}

const getFeatureName = (name) => featureNameMap[name] || name
const getFactorLabel = (key) => featureNameMap[key] || key

const getDominantFactor = (avgFactors) => {
  if (!avgFactors || Object.keys(avgFactors).length === 0) return ''
  const [top] = Object.entries(avgFactors).sort((a, b) => Number(b[1]) - Number(a[1]))
  return `${getFactorLabel(top[0])} (${top[1]})`
}

const getLogLevelTag = (level) => {
  const map = { INFO: 'info', WARNING: 'warning', ERROR: 'danger' }
  return map[level] || 'info'
}

onMounted(() => {
  fetchRecommendConfig()
  fetchModelInfo()
  fetchClusterStats()
  fetchLogs()
})
</script>

<style scoped>
.system-config {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

.feature-importance {
  margin-top: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.feature-name {
  width: 100px;
  flex-shrink: 0;
}

.avg-factor {
  margin-right: 12px;
  display: inline-block;
}

.filter-form {
  margin-bottom: 16px;
}
</style>

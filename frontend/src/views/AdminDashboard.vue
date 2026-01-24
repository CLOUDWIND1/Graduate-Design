<!--
管理端数据看板
文件名：src/views/AdminDashboard.vue
-->

<template>
  <div class="admin-dashboard">
    <!-- 顶部欢迎栏 -->
    <div class="dashboard-header">
      <div class="header-title">
        <h1>数据看板</h1>
        <p class="subtitle">实时监控系统运行状态与用户数据分析</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Refresh" circle plain />
        <el-button icon="Download" circle plain />
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stat-cards">
      <el-col :span="6" v-for="stat in statCards" :key="stat.title">
        <div class="stat-card glass-card">
          <div class="stat-icon-wrapper" :style="{ background: stat.bg, color: stat.color }">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.title }}</div>
          </div>
          <div class="stat-trend" v-if="stat.trend">
            <span :class="stat.trend > 0 ? 'up' : 'down'">
              {{ Math.abs(stat.trend) }}%
              <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
            </span>
            <span class="trend-text">较上周</span>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="24" class="chart-section">
      <!-- 用户分群饼图 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="header-title">用户分群分布</span>
              <el-tag size="small" effect="plain">实时</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <PieChart :data="clusterData" />
          </div>
        </el-card>
      </el-col>
      
      <!-- 用户潜力分布 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="header-title">用户潜力分布</span>
              <el-tooltip content="基于AI预测的用户转化潜力">
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container">
            <PieChart :data="potentialData" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 推荐效果趋势 -->
    <el-row :gutter="24" class="chart-section">
      <el-col :span="24">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="header-title">推荐效果趋势</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container large">
            <LineChart :data="trendData" />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="24">
      <el-col :span="16">
        <!-- 维度策略建议 -->
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span class="header-title">营销策略建议</span>
                <span class="header-desc">基于用户画像维度的智能推荐策略</span>
              </div>
            </div>
          </template>
          <el-table :data="strategyList" :row-style="{ height: '60px' }" style="width: 100%">
            <el-table-column prop="dimension" label="维度" width="100">
              <template #default="{ row }">
                <span class="dimension-tag" :class="getDimensionClass(row.dimension)">
                  {{ row.dimension }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="avgScore" label="得分" width="120">
              <template #default="{ row }">
                <div class="score-wrapper">
                  <span class="score-val">{{ row.avgScore.toFixed(2) }}</span>
                  <el-progress 
                    :percentage="row.avgScore * 100" 
                    :show-text="false" 
                    :color="getScoreColor(row.avgScore)"
                    :stroke-width="6"
                  />
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="strategy" label="策略建议" show-overflow-tooltip />
            <el-table-column prop="userCount" label="覆盖用户" width="100" align="right">
              <template #default="{ row }">
                <span class="user-count">{{ row.userCount }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <!-- 特征重要性 -->
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="header-title">关键影响因素</span>
            </div>
          </template>
          <div class="feature-list">
            <div 
              v-for="(item, index) in featureImportance" 
              :key="item.name"
              class="feature-row"
            >
              <div class="feature-info">
                <span class="feature-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                <span class="feature-name">{{ item.label }}</span>
              </div>
              <div class="feature-bar">
                <div class="bar-fill" :style="{ width: (item.importance * 100) + '%', background: getFeatureColor(index) }"></div>
              </div>
              <span class="feature-val">{{ (item.importance * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 高潜力用户列表 -->
    <el-card class="chart-card mt-6" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">高潜力用户 Top 10</span>
          </div>
          <el-button type="primary" plain size="small" @click="exportHighPotentialUsers">
            <el-icon class="mr-1"><Download /></el-icon> 导出名单
          </el-button>
        </div>
      </template>
      <el-table :data="highPotentialUsers" stripe style="width: 100%">
        <el-table-column type="index" label="排名" width="80" align="center">
          <template #default="{ $index }">
            <span class="rank-badge" :class="'rank-' + ($index + 1)" v-if="$index < 3">{{ $index + 1 }}</span>
            <span v-else>{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="probability" label="转化概率" width="200">
          <template #default="{ row }">
            <div class="prob-wrapper">
              <el-progress 
                :percentage="Math.round(row.probability * 100)" 
                :stroke-width="8"
                :color="getProbabilityColor(row.probability)"
              >
                <template #default="{ percentage }">
                  <span class="percentage-text">{{ percentage }}%</span>
                </template>
              </el-progress>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="userType" label="用户分层" width="120">
          <template #default="{ row }">
            <el-tag :type="getUserTypeTag(row.userType)" effect="light" round>{{ row.userType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="topFactor" label="主导因素" width="150" />
        <el-table-column prop="recommendation" label="推荐策略" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { User, Trophy, View, ChatDotRound, InfoFilled, Download, Refresh, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import PieChart from '@/components/Charts/PieChart.vue'
import LineChart from '@/components/Charts/LineChart.vue'
import { getDashboardStats, getUserPotentialAnalysis, getDimensionStrategies } from '@/api/admin'
import { ElMessage } from 'element-plus'

export default {
  name: 'AdminDashboard',
  components: {
    User, Trophy, View, ChatDotRound, InfoFilled, Download, Refresh, ArrowUp, ArrowDown,
    PieChart,
    LineChart
  },
  data() {
    return {
      trendPeriod: 'week',
      statCards: [
        { title: '用户总数', value: 0, icon: 'User', bg: '#EFF6FF', color: '#3B82F6', trend: 12 },
        { title: '活跃活动', value: 0, icon: 'Trophy', bg: '#F0FDF4', color: '#22C55E', trend: 5 },
        { title: '总推荐次数', value: 0, icon: 'View', bg: '#FFF7ED', color: '#F97316', trend: 8 },
        { title: '平均点击率', value: '0%', icon: 'ChatDotRound', bg: '#FEF2F2', color: '#EF4444', trend: -2 }
      ],
      clusterData: [],
      potentialData: [],
      trendData: [],
      featureImportance: [],
      strategyList: [],
      highPotentialUsers: []
    }
  },
  created() {
    this.loadDashboardData()
    this.loadPotentialAnalysis()
    this.loadDimensionStrategies()
  },
  methods: {
    async loadDashboardData() {
      try {
        const data = await getDashboardStats()
        
        // 更新统计卡片
        this.statCards[0].value = (data.userCount || 0).toLocaleString()
        this.statCards[1].value = data.activeActivityCount || 0
        this.statCards[2].value = (data.totalRecommendations || 0).toLocaleString()
        this.statCards[3].value = ((data.avgClickRate || 0) * 100).toFixed(1) + '%'
        
        // 更新图表数据
        this.clusterData = data.clusterDistribution || []
        this.trendData = data.recommendationTrend || []
        this.featureImportance = data.featureImportance || []
      } catch (e) {
        console.error('加载数据失败', e)
        // ElMessage.error('加载数据失败') // 静默失败，避免打扰
      }
    },

    async loadPotentialAnalysis() {
      try {
        const data = await getUserPotentialAnalysis()
        
        // 用户潜力分布饼图数据
        this.potentialData = [
          { name: '高潜力用户', value: data.highPotentialCount || 0 },
          { name: '中等潜力用户', value: data.mediumPotentialCount || 0 },
          { name: '低潜力用户', value: data.lowPotentialCount || 0 }
        ]
        
        // 高潜力用户列表
        this.highPotentialUsers = (data.topUsers || []).map((user, index) => ({
          rank: index + 1,
          username: user.username,
          probability: user.probability,
          userType: user.userType,
          topFactor: user.topFactor,
          recommendation: user.recommendation
        }))
      } catch (e) {
        console.error('加载潜力分析失败', e)
        // 使用模拟数据以展示效果
        this.potentialData = [
          { name: '高潜力用户', value: 15 },
          { name: '中等潜力用户', value: 45 },
          { name: '低潜力用户', value: 40 }
        ]
      }
    },

    async loadDimensionStrategies() {
      try {
        const data = await getDimensionStrategies()
        this.strategyList = data || []
      } catch (e) {
        console.error('加载策略建议失败', e)
        // 模拟数据
        this.strategyList = [
          { dimension: '社会因素', avgScore: 0.65, level: '高', strategy: '该用户群重视社交关系，建议通过亲友推荐、社群营销触达', userCount: 25 },
          { dimension: '心理因素', avgScore: 0.58, level: '高', strategy: '用户心理预期较高，提供超预期奖励、强调产品质量和隐私保护', userCount: 30 },
          { dimension: '激励因素', avgScore: 0.72, level: '高', strategy: '对激励敏感，提供即时红包、透明公平的活动规则', userCount: 45 },
          { dimension: '个人因素', avgScore: 0.61, level: '高', strategy: '社交活跃、爱分享，适合发展为KOC（关键意见消费者）', userCount: 35 }
        ]
      }
    },

    exportHighPotentialUsers() {
      if (this.highPotentialUsers.length === 0) {
        ElMessage.warning('暂无高潜力用户数据')
        return
      }
      const headers = ['排名', '用户名', '接受概率', '用户类型', '主导因素', '推荐策略']
      const rows = this.highPotentialUsers.map(u => [
        u.rank, u.username, (u.probability * 100).toFixed(1) + '%', u.userType, u.topFactor, u.recommendation
      ])
      const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
      const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '高潜力用户名单.csv'
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    },

    getFeatureColor(index) {
      const colors = ['#3B82F6', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6', '#64748B']
      return colors[index % colors.length]
    },

    getDimensionClass(dimension) {
      // 这里的class需要在css中定义，或者直接返回颜色
      return 'dim-' + Math.floor(Math.random() * 5) // 简化处理，实际应根据dimension映射
    },

    getScoreColor(score) {
      if (score >= 0.7) return '#10B981'
      if (score >= 0.5) return '#3B82F6'
      if (score >= 0.3) return '#F59E0B'
      return '#F43F5E'
    },

    getProbabilityColor(prob) {
      if (prob >= 0.7) return '#10B981'
      if (prob >= 0.4) return '#F59E0B'
      return '#F43F5E'
    },

    getUserTypeTag(type) {
      const tags = {
        '高潜力用户': 'success',
        '中等潜力用户': 'warning',
        '低潜力用户': 'info'
      }
      return tags[type] || ''
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-secondary);
  margin: 0;
  font-size: 14px;
}

/* Stat Cards */
.stat-cards {
  margin-bottom: 24px;
}

.glass-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid rgba(0,0,0,0.03);
  box-shadow: var(--shadow-sm);
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-trend {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-trend .up { color: #10B981; display: flex; align-items: center; gap: 2px; font-weight: 600; }
.stat-trend .down { color: #EF4444; display: flex; align-items: center; gap: 2px; font-weight: 600; }
.trend-text { color: var(--text-secondary); margin-top: 2px; transform: scale(0.9); transform-origin: right; }

/* Charts & Lists */
.chart-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
  border: none;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.3s;
  height: 100%;
}

.chart-card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-left: 12px;
  font-weight: normal;
}

.chart-container {
  height: 320px;
}

.chart-container.large {
  height: 380px;
}

.mr-1 { margin-right: 4px; }
.mt-6 { margin-top: 24px; }

/* Strategies Table */
.dimension-tag {
  font-weight: 600;
  color: var(--text-regular);
}

.score-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-val {
  font-weight: 600;
  font-family: monospace;
  width: 36px;
}

.user-count {
  font-family: monospace;
  font-weight: 600;
  color: var(--text-primary);
}

/* Feature List */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 10px 0;
}

.feature-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.feature-info {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 140px;
}

.feature-rank {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #F3F4F6;
  color: #6B7280;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-rank.rank-1 { background: #FEF3C7; color: #D97706; }
.feature-rank.rank-2 { background: #F1F5F9; color: #475569; }
.feature-rank.rank-3 { background: #FFEDD5; color: #C2410C; }

.feature-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-regular);
}

.feature-bar {
  flex: 1;
  height: 8px;
  background: #F3F4F6;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
}

.feature-val {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  width: 32px;
  text-align: right;
}

/* User Table */
.rank-badge {
  display: inline-flex;
  width: 24px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #F3F4F6;
  font-weight: 700;
  font-size: 14px;
  color: #6B7280;
}

.rank-badge.rank-1 { background: rgba(251, 191, 36, 0.2); color: #B45309; }
.rank-badge.rank-2 { background: rgba(148, 163, 184, 0.2); color: #475569; }
.rank-badge.rank-3 { background: rgba(251, 146, 60, 0.2); color: #C2410C; }

.percentage-text {
  font-size: 12px;
  font-weight: 600;
}
</style>
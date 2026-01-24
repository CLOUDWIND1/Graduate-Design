<template>
  <div class="rewards-container">
    <el-card class="rewards-header-card">
      <div class="rewards-summary">
        <div class="summary-item">
          <div class="summary-value">{{ summary.totalAmount }}</div>
          <div class="summary-label">累计奖励(元)</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ summary.totalPoints }}</div>
          <div class="summary-label">累计积分</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ summary.pendingCount }}</div>
          <div class="summary-label">待领取</div>
        </div>
      </div>
    </el-card>

    <!-- 筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="奖励类型">
          <el-select v-model="filters.rewardType" placeholder="全部" clearable style="width: 150px">
            <el-option label="红包" value="red_packet" />
            <el-option label="积分" value="points" />
            <el-option label="优惠券" value="coupon" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 150px">
            <el-option label="待领取" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchRewards">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 奖励列表 -->
    <el-card>
      <template #header>
        <span>奖励记录</span>
      </template>
      
      <el-table :data="rewards" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="奖励类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getRewardTypeTag(row.reward_type)">
              {{ getRewardTypeName(row.reward_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额/数量" width="120">
          <template #default="{ row }">
            <span class="amount">
              {{ row.reward_type === 'points' ? row.amount + '积分' : '¥' + row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="activity_name" label="来源活动" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'"
              type="primary" 
              size="small"
              @click="claimReward(row)"
            >
              领取
            </el-button>
            <span v-else class="claimed-text">
              {{ row.status === 'completed' ? '已领取' : '已过期' }}
            </span>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="total > 0"
        class="pagination"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
      
      <el-empty v-if="!loading && rewards.length === 0" description="暂无奖励记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const rewards = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = ref({
  rewardType: '',
  status: ''
})

const summary = ref({
  totalAmount: 0,
  totalPoints: 0,
  pendingCount: 0
})

const fetchRewards = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    // 添加筛选条件
    if (filters.value.rewardType) {
      params.reward_type = filters.value.rewardType
    }
    if (filters.value.status) {
      params.status = filters.value.status
    }
    // 使用尾部斜杠避免307重定向丢失Authorization header
    const res = await api.get('/rewards/', { params })
    console.log('奖励列表响应:', res)
    rewards.value = res.items || res
    total.value = res.total || rewards.value.length
  } catch (error) {
    console.error('获取奖励列表失败', error)
  } finally {
    loading.value = false
  }
}

const fetchSummary = async () => {
  try {
    // 使用尾部斜杠避免307重定向丢失Authorization header
    const res = await api.get('/rewards/summary/')
    summary.value = res
  } catch (error) {
    console.error('获取奖励汇总失败', error)
  }
}

const claimReward = async (reward) => {
  try {
    await ElMessageBox.confirm('确定领取该奖励吗？', '提示')
    // 使用尾部斜杠避免307重定向丢失Authorization header
    await api.post(`/rewards/${reward.id}/claim/`)
    ElMessage.success('领取成功')
    fetchRewards()
    fetchSummary()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('领取失败')
    }
  }
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchRewards()
}

const getRewardTypeName = (type) => {
  const map = { red_packet: '红包', points: '积分', coupon: '优惠券' }
  return map[type] || type
}

const getRewardTypeTag = (type) => {
  const map = { red_packet: 'danger', points: 'warning', coupon: 'success' }
  return map[type] || 'info'
}

const getStatusName = (status) => {
  const map = { pending: '待领取', completed: '已完成', expired: '已过期' }
  return map[status] || status
}

const getStatusTag = (status) => {
  const map = { pending: 'warning', completed: 'success', expired: 'info' }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchRewards()
  fetchSummary()
})
</script>

<style scoped>
.rewards-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

.rewards-header-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.rewards-summary {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.summary-item {
  text-align: center;
  color: #fff;
}

.summary-value {
  font-size: 36px;
  font-weight: bold;
}

.summary-label {
  margin-top: 8px;
  opacity: 0.9;
}

.filter-card {
  margin-bottom: 20px;
}

.amount {
  font-weight: bold;
  color: #E6A23C;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}

.claimed-text {
  color: #909399;
  font-size: 12px;
}
</style>

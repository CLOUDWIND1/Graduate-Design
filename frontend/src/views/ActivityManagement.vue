<template>
  <div class="activity-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>活动管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建活动
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="活动名称">
          <el-input v-model="filters.name" placeholder="搜索活动名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="paused" />
            <el-option label="已结束" value="ended" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.type" placeholder="全部" clearable style="width: 120px">
            <el-option label="邀请" value="invite" />
            <el-option label="答题" value="quiz" />
            <el-option label="分享" value="share" />
            <el-option label="签到" value="checkin" />
            <el-option label="任务" value="task" />
            <el-option label="学习" value="learn" />
            <el-option label="购买" value="purchase" />
            <el-option label="评价" value="review" />
            <el-option label="抽奖" value="lottery" />
            <el-option label="社区" value="community" />
            <el-option label="会员" value="member" />
            <el-option label="节日" value="festival" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchActivities">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 活动列表 -->
      <el-table :data="activities" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="活动名称" min-width="150" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="激励" width="150">
          <template #default="{ row }">
            <span>{{ getIncentiveTypeName(row.incentive_type) }} ¥{{ row.incentive_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间范围" width="200">
          <template #default="{ row }">
            <div class="time-range">
              <div>{{ formatDate(row.start_time) }}</div>
              <div>至 {{ formatDate(row.end_time) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="参与人数" width="100">
          <template #default="{ row }">
            {{ row.participate_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editActivity(row)">
              编辑
            </el-button>
            <el-button 
              :type="row.status === 'active' ? 'warning' : 'success'" 
              size="small"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '暂停' : '启用' }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteActivity(row)">
              删除
            </el-button>
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
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑活动' : '新建活动'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="活动名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入活动名称" />
        </el-form-item>
        <el-form-item label="活动描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入活动描述" 
          />
        </el-form-item>
        <el-form-item label="活动类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择活动类型">
            <el-option label="邀请活动" value="invite" />
            <el-option label="答题活动" value="quiz" />
            <el-option label="分享活动" value="share" />
            <el-option label="签到活动" value="checkin" />
            <el-option label="任务活动" value="task" />
            <el-option label="学习活动" value="learn" />
            <el-option label="购买活动" value="purchase" />
            <el-option label="评价活动" value="review" />
            <el-option label="抽奖活动" value="lottery" />
            <el-option label="社区活动" value="community" />
            <el-option label="会员活动" value="member" />
            <el-option label="节日活动" value="festival" />
          </el-select>
        </el-form-item>
        <el-form-item label="激励类型" prop="incentive_type">
          <el-select v-model="form.incentive_type" placeholder="请选择激励类型">
            <el-option label="红包" value="red_packet" />
            <el-option label="积分" value="points" />
            <el-option label="优惠券" value="coupon" />
          </el-select>
        </el-form-item>
        <el-form-item label="激励金额" prop="incentive_amount">
          <el-input-number 
            v-model="form.incentive_amount" 
            :min="0" 
            :precision="2"
            placeholder="请输入激励金额"
          />
        </el-form-item>
        <el-form-item label="活动时间" prop="time_range">
          <el-date-picker
            v-model="form.time_range"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const submitting = ref(false)
const activities = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = ref({
  name: '',
  status: '',
  type: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = ref({
  title: '',
  description: '',
  type: '',
  incentive_type: '',
  incentive_amount: 0,
  time_range: []
})

const rules = {
  title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  incentive_type: [{ required: true, message: '请选择激励类型', trigger: 'change' }],
  incentive_amount: [{ required: true, message: '请输入激励金额', trigger: 'blur' }],
  time_range: [{ required: true, message: '请选择活动时间', trigger: 'change' }]
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value, ...filters.value }
    // 注意：URL末尾加斜杠，避免FastAPI重定向导致Authorization头丢失
    const res = await api.get('/activities/', { params })
    activities.value = res.items || res
    total.value = res.total || activities.value.length
  } catch (error) {
    console.error('获取活动列表失败', error)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = {
    title: '', description: '', type: '', 
    incentive_type: '', incentive_amount: 0, time_range: []
  }
  dialogVisible.value = true
}

const editActivity = (activity) => {
  isEdit.value = true
  form.value = {
    ...activity,
    time_range: [new Date(activity.start_time), new Date(activity.end_time)]
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      ...form.value,
      start_time: form.value.time_range[0],
      end_time: form.value.time_range[1]
    }
    delete data.time_range

    if (isEdit.value) {
      await api.put(`/activities/${form.value.id}/`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/activities/', data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchActivities()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (activity) => {
  const newStatus = activity.status === 'active' ? 'paused' : 'active'
  try {
    await api.patch(`/activities/${activity.id}/status/`, { status: newStatus })
    ElMessage.success('状态更新成功')
    fetchActivities()
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

const deleteActivity = async (activity) => {
  try {
    await ElMessageBox.confirm('确定删除该活动吗？', '警告', { type: 'warning' })
    await api.delete(`/activities/${activity.id}`)
    ElMessage.success('删除成功')
    fetchActivities()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const resetFilters = () => {
  filters.value = { name: '', status: '', type: '' }
  fetchActivities()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchActivities()
}

const getTypeName = (type) => {
  const map = { 
    invite: '邀请', 
    quiz: '答题', 
    share: '分享',
    purchase: '购买',
    register: '注册',
    checkin: '签到',
    task: '任务',
    learn: '学习',
    review: '评价',
    lottery: '抽奖',
    community: '社区',
    member: '会员',
    festival: '节日'
  }
  return map[type] || type || '未知类型'
}

const getIncentiveTypeName = (type) => {
  const map = { 
    red_packet: '红包', 
    points: '积分', 
    coupon: '优惠券',
    cash: '现金',
    gift: '礼品'
  }
  return map[type] || '未知激励'
}

const getStatusName = (status) => {
  const map = { 
    draft: '草稿',
    active: '活跃', 
    paused: '暂停', 
    ended: '已结束' 
  }
  return map[status] || '未知状态'
}

const getStatusTag = (status) => {
  const map = { draft: '', active: 'success', paused: 'warning', ended: 'info' }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchActivities()
})
</script>

<style scoped>
.activity-management {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.filter-form .el-select {
  width: 120px;
}

.filter-form .el-input {
  width: 180px;
}

.time-range {
  font-size: 12px;
  color: #909399;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>

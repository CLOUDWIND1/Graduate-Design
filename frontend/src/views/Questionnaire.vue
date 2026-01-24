<template>
  <div class="questionnaire-container">
    <el-card class="questionnaire-card">
      <template #header>
        <div class="card-header">
          <h2>用户偏好调查</h2>
          <p>请回答以下问题，帮助我们更好地为您推荐活动</p>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" simple class="steps">
        <el-step title="社会因素" />
        <el-step title="心理因素" />
        <el-step title="激励因素" />
        <el-step title="技术因素" />
        <el-step title="环境因素" />
        <el-step title="个人因素" />
      </el-steps>

      <div class="questions-section" v-loading="submitting">
        <!-- 第一步：社会因素 (3题) -->
        <div v-show="currentStep === 0" class="step-content">
          <h3>社会因素相关问题</h3>
          <div v-for="(q, idx) in questions.social" :key="'social-'+idx" class="question-item">
            <p class="question-text">{{ idx + 1 }}. {{ q.text }}</p>
            <el-radio-group v-model="answers.social[idx]">
              <el-radio v-for="opt in options" :key="opt.value" :label="opt.value">
                {{ opt.label }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 第二步：心理因素 (4题) -->
        <div v-show="currentStep === 1" class="step-content">
          <h3>心理因素相关问题</h3>
          <div v-for="(q, idx) in questions.psych" :key="'psych-'+idx" class="question-item">
            <p class="question-text">{{ idx + 1 }}. {{ q.text }}</p>
            <el-radio-group v-model="answers.psych[idx]">
              <el-radio v-for="opt in options" :key="opt.value" :label="opt.value">
                {{ opt.label }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 第三步：激励因素 (3题) -->
        <div v-show="currentStep === 2" class="step-content">
          <h3>激励因素相关问题</h3>
          <div v-for="(q, idx) in questions.incent" :key="'incent-'+idx" class="question-item">
            <p class="question-text">{{ idx + 1 }}. {{ q.text }}</p>
            <el-radio-group v-model="answers.incent[idx]">
              <el-radio v-for="opt in options" :key="opt.value" :label="opt.value">
                {{ opt.label }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 第四步：技术因素 (3题) -->
        <div v-show="currentStep === 3" class="step-content">
          <h3>技术因素相关问题</h3>
          <div v-for="(q, idx) in questions.tech" :key="'tech-'+idx" class="question-item">
            <p class="question-text">{{ idx + 1 }}. {{ q.text }}</p>
            <el-radio-group v-model="answers.tech[idx]">
              <el-radio v-for="opt in options" :key="opt.value" :label="opt.value">
                {{ opt.label }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 第五步：环境因素 (3题) -->
        <div v-show="currentStep === 4" class="step-content">
          <h3>环境因素相关问题</h3>
          <div v-for="(q, idx) in questions.env" :key="'env-'+idx" class="question-item">
            <p class="question-text">{{ idx + 1 }}. {{ q.text }}</p>
            <el-radio-group v-model="answers.env[idx]">
              <el-radio v-for="opt in options" :key="opt.value" :label="opt.value">
                {{ opt.label }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 第六步：个人因素 (4题) -->
        <div v-show="currentStep === 5" class="step-content">
          <h3>个人因素相关问题</h3>
          <div v-for="(q, idx) in questions.personal" :key="'personal-'+idx" class="question-item">
            <p class="question-text">{{ idx + 1 }}. {{ q.text }}</p>
            <el-radio-group v-model="answers.personal[idx]">
              <el-radio v-for="opt in options" :key="opt.value" :label="opt.value">
                {{ opt.label }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>
      </div>

      <div class="button-group">
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="currentStep < 5" type="primary" @click="nextStep" :disabled="!canNext">
          下一步
        </el-button>
        <el-button v-if="currentStep === 5" type="success" @click="submitQuestionnaire" 
          :loading="submitting" :disabled="!canSubmit">
          提交问卷
        </el-button>
        <el-button v-if="canSkip" type="info" text @click="skipQuestionnaire">
          跳过问卷
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const currentStep = ref(0)
const submitting = ref(false)

// 问卷选项模板 (李克特5级量表)
const options = [
  { label: '非常不同意', value: 1 },
  { label: '不同意', value: 2 },
  { label: '一般', value: 3 },
  { label: '同意', value: 4 },
  { label: '非常同意', value: 5 }
]

// 问卷问题 - 基于全民获客理念下消费者行为影响因素指标体系
const questions = {
  // 社会因素 (3题)
  social: [
    { text: '我更愿意接受关系较为亲密的人的推荐' },
    { text: '关系较为疏远的人的推荐可能需要额外激励（如折扣或利益承诺）才能有效' },
    { text: '我通过他人的行为来判断某个产品或服务是否值得购买。如果推荐人数多、评价积极，我会更快地接受推荐' }
  ],
  // 心理因素 (4题)
  psych: [
    { text: '如果奖励（如折扣、现金、积分）符合或高于我的心理预期，我更可能接受推荐并参与推荐' },
    { text: '我因为害怕"错过奖励"或"比别人少得到好处"，可能更容易参与推荐' },
    { text: '我会担心隐私泄露（如手机号、个人信息）从而阻碍推荐或被推荐行为的发生' },
    { text: '我会因为担心质量而选择最可靠的产品或服务' }
  ],
  // 激励因素 (3题)
  incent: [
    { text: '我更愿意参与规则简单、透明的推荐活动' },
    { text: '我认为推荐活动机制应该对所有参与者公平' },
    { text: '相比于累积奖励（如积分兑换等）和非金钱奖励（如会员赠送等），我更倾向于选择即时奖励（如红包返现）' }
  ],
  // 技术因素 (3题)
  tech: [
    { text: '我会因为操作流程简便而参与推荐活动' },
    { text: '我会因为系统卡顿或奖励发放延迟而失去参与的兴趣' },
    { text: '我希望根据我的兴趣接收到个性化的推荐活动' }
  ],
  // 环境因素 (3题)
  env: [
    { text: '我愿意接受推荐和被推荐政府政策支持下的产品或服务' },
    { text: '产品口碑对我参与推荐活动的影响很大' },
    { text: '我更愿意参与推荐市场前景好的产品' }
  ],
  // 个人因素 (4题)
  personal: [
    { text: '我对价格比较敏感' },
    { text: '我更倾向于参与自己熟悉品牌的推荐活动' },
    { text: '我认为自己是社交活跃的消费者' },
    { text: '我喜欢分享自己的购物体验和推荐给他人' }
  ]
}

// 答案 (共20题: 3+4+3+3+3+4=20)
const answers = ref({
  social: Array(questions.social.length).fill(null),
  psych: Array(questions.psych.length).fill(null),
  incent: Array(questions.incent.length).fill(null),
  tech: Array(questions.tech.length).fill(null),
  env: Array(questions.env.length).fill(null),
  personal: Array(questions.personal.length).fill(null)
})

// 步骤对应的答案key
const stepKeys = ['social', 'psych', 'incent', 'tech', 'env', 'personal']

// 是否可以进入下一步
const canNext = computed(() => {
  const currentAnswers = answers.value[stepKeys[currentStep.value]]
  return currentAnswers.every(a => a !== null)
})

// 是否可以提交
const canSubmit = computed(() => {
  return Object.values(answers.value).every(arr => arr.every(a => a !== null))
})

// 是否可以跳过
const canSkip = computed(() => {
  return currentStep.value === 0
})

const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--
}

const nextStep = () => {
  if (currentStep.value < 5 && canNext.value) currentStep.value++
}

const skipQuestionnaire = () => {
  ElMessage.info('您可以稍后在个人中心完成问卷')
  router.push('/recommendations')
}

const submitQuestionnaire = async () => {
  submitting.value = true
  try {
    // 将答案转换为20维数组（按顺序：social 3 + psych 4 + incent 3 + tech 3 + env 3 + personal 4 = 20）
    const allAnswers = [
      ...answers.value.social,
      ...answers.value.psych,
      ...answers.value.incent,
      ...answers.value.tech,
      ...answers.value.env,
      ...answers.value.personal
    ]
    
    await api.post('/users/questionnaire/', { answers: allAnswers })
    ElMessage.success('问卷提交成功！系统已为您生成个性化推荐')
    router.push('/recommendations')
  } catch (error) {
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.questionnaire-container {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(-45deg, #093028, #237a57, #667eea, #764ba2);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.questionnaire-card {
  width: 100%;
  max-width: 900px;
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: none;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(40px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.card-header {
  text-align: center;
  padding: 10px 0;
}

.card-header h2 {
  margin: 0 0 12px 0;
  color: #1a202c;
  font-size: 24px;
}

.card-header p {
  margin: 0;
  color: #718096;
}

.steps {
  margin: 30px 0 40px;
  background: transparent !important;
  padding: 0 !important;
}

.step-content {
  min-height: 400px;
  padding: 0 20px;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(10px); }
  to { opacity: 1; transform: translateX(0); }
}

.step-content h3 {
  margin-bottom: 24px;
  color: #409EFF;
  font-size: 20px;
  display: flex;
  align-items: center;
}

.step-content h3::before {
  content: '';
  display: block;
  width: 4px;
  height: 24px;
  background: #409EFF;
  margin-right: 12px;
  border-radius: 2px;
}

.question-item {
  margin-bottom: 28px;
  padding: 24px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #edf2f7;
  transition: all 0.3s ease;
}

.question-item:hover {
  background: #fff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-color: #e2e8f0;
}

.question-text {
  margin: 0 0 16px 0;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.6;
  font-size: 16px;
}

.el-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  width: 100%;
}

.el-radio {
  background: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin: 0 !important;
  flex: 1;
  min-width: 120px;
  transition: all 0.2s;
}

.el-radio.is-checked {
  background: #ebf5ff;
  border-color: #409EFF;
  box-shadow: 0 0 0 1px #409EFF;
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #edf2f7;
}
</style>

<template>
  <div class="prediction-page">
    <div class="header-action">
      <el-button type="info" plain @click="goBack" class="back-btn">&lt; 返回大屏指挥中心</el-button>
    </div>

    <div class="prediction-content">
      <div class="match-teams">
        <div class="team-side">
          <span class="ha-tag ha-home">主</span>
          <h1 class="team-text">{{ team1 }}</h1>
        </div>
        <div class="vs-text">VS</div>
        <div class="team-side">
          <span class="ha-tag ha-away">客</span>
          <h1 class="team-text">{{ team2 }}</h1>
        </div>
      </div>

      <!-- 模型选择区 -->
      <div class="model-selector glass-panel">
        <div class="selector-header">
          <h3>选择预测模型</h3>
          <el-checkbox v-model="selectAll" @change="toggleSelectAll">全选</el-checkbox>
        </div>
        <div class="model-list">
          <el-checkbox
            v-for="m in availableModels"
            :key="m.id"
            v-model="selectedModels[m.id]"
            class="model-checkbox"
          >
            <span class="model-name">{{ m.name }}</span>
            <el-tag size="small" :type="m.provider === 'anthropic' ? 'warning' : 'info'" class="provider-tag">
              {{ m.provider }}
            </el-tag>
          </el-checkbox>
          <div v-if="availableModels.length === 0" class="no-models">
            暂无可用模型，请在 backend/.env 中配置 MODEL_N_* API_KEY
          </div>
        </div>
        <el-button
          type="primary"
          @click="runAnalysis"
          :loading="isRunning"
          :disabled="selectedModelIds.length === 0"
          class="cyber-btn run-btn"
        >
          <span v-if="isRunning">分析中...</span>
          <span v-else>启动 {{ selectedModelIds.length }} 个模型分析</span>
        </el-button>
      </div>

      <!-- 结果展示区 -->
      <div v-if="hasResults" class="results-area">
        <!-- ★ 多模型分列对比：四维数据横向并排（每列一个模型） -->
        <div class="models-grid">
          <div class="model-card" v-for="m in resultModels" :key="m.id">
            <div class="mc-header">
              <span class="mc-name">{{ m.name }}</span>
              <el-tag size="small" :type="m.provider === 'anthropic' ? 'warning' : 'info'" class="mc-provider">
                {{ m.provider }}
              </el-tag>
            </div>
            <div class="mc-stats">
              <div class="mc-item" v-for="field in statFields" :key="field.key">
                <span class="mc-label">{{ field.label }}</span>
                <span class="mc-value" :class="{ highlight: field.key === 'score' }">
                  {{ getFieldResult(m.id, field.key) || '-' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- ★ 投注建议：竖向排列（每个模型一块） -->
        <div class="advice-stack glass-panel">
          <h4 class="stack-title">投注建议</h4>
          <div class="advice-block" v-for="m in resultModels" :key="m.id">
            <div class="ab-header">
              <span class="ab-name">{{ m.name }}</span>
              <el-tag size="small" :type="m.provider === 'anthropic' ? 'warning' : 'info'">{{ m.provider }}</el-tag>
            </div>
            <div class="advice-content" v-html="formatText(getFieldResult(m.id, 'advice'))"></div>
          </div>
        </div>

        <!-- ★ 综合评判 -->
        <div v-if="aggregateData" class="aggregate-section glass-panel">
          <h4>★ 综合评判结论</h4>
          <div class="agg-stats">
            <div class="agg-item">
              <span class="agg-label">最终比分</span>
              <span class="agg-value highlight">{{ aggregateData.final_score }}</span>
            </div>
            <div class="agg-item">
              <span class="agg-label">总进球</span>
              <span class="agg-value">{{ aggregateData.final_goals }}</span>
            </div>
            <div class="agg-item">
              <span class="agg-label">红牌预警</span>
              <span class="agg-value">{{ aggregateData.final_red_cards }}</span>
            </div>
            <div class="agg-item">
              <span class="agg-label">点球预测</span>
              <span class="agg-value">{{ aggregateData.final_penalties }}</span>
            </div>
          </div>
          <div class="agg-advice">
            <h4>综合建议</h4>
            <div class="advice-content" v-html="formatText(aggregateData.final_advice)"></div>
          </div>
          <div class="agg-meta">
            基于 {{ aggregateData.model_count }} 个模型的投票聚合
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = 'http://localhost:10086'

const route = useRoute()
const router = useRouter()

const team1 = computed(() => route.query.team1 || '主队')
const team2 = computed(() => route.query.team2 || '客队')

// 模型相关
const availableModels = ref<{ id: string; name: string; provider: string }[]>([])
const selectedModels = reactive<Record<string, boolean>>({})
const selectAll = ref(true)
const isRunning = ref(false)

// 结果相关
const modelResults = ref<Record<string, Record<string, string>>>({})
const aggregateData = ref<any>(null)

const statFields = [
  { key: 'score', label: '预测比分' },
  { key: 'total_goals', label: '总进球数' },
  { key: 'red_cards', label: '红牌预警' },
  { key: 'penalties', label: '点球预测' },
]

const selectedModelIds = computed(() =>
  Object.entries(selectedModels).filter(([_, v]) => v).map(([k]) => k)
)

const resultModels = computed(() =>
  availableModels.value.filter(m => modelResults.value[m.id])
)

const hasResults = computed(() => Object.keys(modelResults.value).length > 0)

function toggleSelectAll(val: boolean) {
  for (const m of availableModels.value) {
    selectedModels[m.id] = val
  }
}

function getFieldResult(modelId: string, field: string): string {
  return modelResults.value[modelId]?.[field] || ''
}

function formatText(text: string): string {
  if (!text) return ''
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

async function fetchModels() {
  try {
    const res = await axios.get(`${API_BASE}/api/models`)
    availableModels.value = res.data.models || []
    // 默认全选
    for (const m of availableModels.value) {
      selectedModels[m.id] = true
    }
  } catch (e) {
    ElMessage.error('获取模型列表失败')
  }
}

async function runAnalysis() {
  if (selectedModelIds.value.length === 0) {
    ElMessage.warning('请至少选择一个模型')
    return
  }

  isRunning.value = true
  modelResults.value = {}
  aggregateData.value = null

  try {
    // 如果多个模型，用 aggregate 接口一次性获取结果+汇总
    // 如果单模型，用 multi 接口
    const ids = selectedModelIds.value

    if (ids.length >= 2) {
      // 多模型：调用 aggregate（内部会调 multi + 投票）
      const res = await axios.post(`${API_BASE}/api/predict/aggregate`, {
        team1_name: team1.value,
        team2_name: team2.value,
        model_ids: ids,
        force_refresh: true,
      })
      if (res.data.status === 'success') {
        const data = res.data.data
        modelResults.value = data.model_details || {}
        aggregateData.value = data
      } else {
        ElMessage.error('分析失败: ' + (res.data.message || '未知错误'))
      }
    } else {
      // 单模型：调用 multi
      const res = await axios.post(`${API_BASE}/api/predict/multi`, {
        team1_name: team1.value,
        team2_name: team2.value,
        model_ids: ids,
        force_refresh: true,
      })
      if (res.data.status === 'success') {
        modelResults.value = res.data.results || {}
      } else {
        ElMessage.error('分析失败')
      }
    }
  } catch (e: any) {
    ElMessage.error('请求失败: ' + (e.message || '网络错误'))
  } finally {
    isRunning.value = false
  }
}

const goBack = () => {
  router.push('/')
}

// 加载历史缓存结果
async function loadCachedResults() {
  try {
    const res = await axios.get(`${API_BASE}/api/predictions/history/${team1.value}/${team2.value}`)
    if (res.data.status === 'success' && Object.keys(res.data.data).length > 0) {
      modelResults.value = res.data.data
      // 自动勾选有缓存的模型
      const keys = Object.keys(res.data.data)
      for (const mid of keys) {
        if (mid in selectedModels) {
          selectedModels[mid] = true
        }
      }
    }
  } catch (e) {
    // 无缓存，忽略
  }
}

onMounted(async () => {
  await fetchModels()
  await loadCachedResults()
})
</script>

<style scoped>
.prediction-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  color: #fff;
  padding: 40px;
  overflow-y: auto;
  pointer-events: auto;
}

.header-action {
  pointer-events: auto;
}

.back-btn {
  background: rgba(30, 26, 23, 0.6) !important;
  border-color: #D2A76D !important;
  color: #D2A76D !important;
  backdrop-filter: blur(5px);
  transition: all 0.3s;
}
.back-btn:hover {
  background: rgba(210, 167, 109, 0.1) !important;
  box-shadow: 0 0 10px rgba(210, 167, 109, 0.3);
}

.prediction-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.match-teams {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-bottom: 30px;
}

.team-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

/* 主客场标签 */
.ha-tag {
  font-size: 0.8rem;
  font-weight: 700;
  padding: 2px 14px;
  border-radius: 10px;
  letter-spacing: 2px;
}
.ha-home {
  color: #1a1410;
  background: linear-gradient(135deg, #E8C389 0%, #D2A76D 100%);
  box-shadow: 0 0 12px rgba(210, 167, 109, 0.5);
}
.ha-away {
  color: #c9d1d9;
  background: rgba(100, 100, 100, 0.25);
  border: 1px solid rgba(160, 160, 160, 0.4);
}

.team-text {
  font-size: 3.5rem;
  font-weight: 900;
  text-shadow: 0 5px 15px rgba(0,0,0,0.8);
}

.vs-text {
  font-size: 2.5rem;
  font-style: italic;
  font-weight: 900;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 模型选择区 */
.model-selector {
  background: rgba(18, 18, 18, 0.75);
  backdrop-filter: blur(12px);
  padding: 20px 30px;
  border-radius: 12px;
  width: 80%;
  max-width: 1000px;
  pointer-events: auto;
  margin-bottom: 25px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid rgba(210, 167, 109, 0.2);
  padding-bottom: 10px;
}

.selector-header h3 {
  margin: 0;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.1rem;
}

.model-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.model-checkbox {
  pointer-events: auto;
}

.model-name {
  font-weight: 600;
  color: #fff;
  margin-right: 6px;
}

.provider-tag {
  vertical-align: middle;
}

.no-models {
  color: #A0A0A0;
  font-style: italic;
  padding: 10px 0;
}

.run-btn {
  pointer-events: auto;
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important;
  color: #D2A76D !important;
  font-weight: bold;
  letter-spacing: 2px;
  transition: all 0.3s;
}
.run-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 20px rgba(210, 167, 109, 0.4);
}

/* 结果展示区 */
.results-area {
  width: 90%;
  max-width: 1200px;
  display: flex;
  flex-direction: column;
  gap: 25px;
  margin-bottom: 40px;
}

/* 多模型分列对比（四维数据横向并排） */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  pointer-events: auto;
}

.model-card {
  background: rgba(30, 26, 23, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(210, 167, 109, 0.25);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(210, 167, 109, 0.15);
  padding-bottom: 10px;
}

.mc-name {
  font-weight: 700;
  font-size: 1.05rem;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.mc-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mc-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(18, 18, 18, 0.6);
  border-radius: 8px;
  padding: 10px 14px;
  border: 1px solid rgba(210, 167, 109, 0.08);
}

.mc-label {
  font-size: 0.78rem;
  color: #A0A0A0;
  letter-spacing: 1px;
}

.mc-value {
  font-size: 1.1rem;
  font-weight: 800;
  color: #fff;
  font-family: 'Courier New', Courier, monospace;
}

.mc-value.highlight {
  color: #D2A76D;
  text-shadow: 0 0 10px rgba(210, 167, 109, 0.5);
  font-size: 1.4rem;
}

/* 投注建议竖向堆叠 */
.advice-stack {
  background: rgba(30, 26, 23, 0.8);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 22px 26px;
  border: 1px solid rgba(210, 167, 109, 0.2);
  pointer-events: auto;
}

.stack-title {
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.1rem;
  letter-spacing: 2px;
  border-bottom: 1px solid rgba(210, 167, 109, 0.15);
  padding-bottom: 10px;
}

.advice-block {
  background: rgba(18, 18, 18, 0.5);
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 14px;
  border-left: 3px solid rgba(210, 167, 109, 0.5);
}

.advice-block:last-child {
  margin-bottom: 0;
}

.ab-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.ab-name {
  font-weight: 700;
  color: #D2A76D;
  font-size: 0.95rem;
}

.advice-content {
  line-height: 1.8;
  font-size: 0.9rem;
  color: #A0A0A0;
}

.highlight {
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 汇总结论区 */
.aggregate-section {
  background: rgba(30, 26, 23, 0.8);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 25px 30px;
  border: 1px solid rgba(210, 167, 109, 0.3);
  position: relative;
}

.aggregate-section h4 {
  margin: 0 0 18px 0;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.3rem;
  letter-spacing: 2px;
}

.agg-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.agg-item {
  background: rgba(18, 18, 18, 0.6);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 1px solid rgba(210, 167, 109, 0.1);
}

.agg-label {
  display: block;
  font-size: 0.7rem;
  color: #A0A0A0;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.agg-value {
  font-size: 1.2rem;
  font-weight: 900;
  color: #fff;
  font-family: 'Courier New', Courier, monospace;
}

.agg-value.highlight {
  color: #D2A76D;
  text-shadow: 0 0 10px rgba(210, 167, 109, 0.5);
  font-size: 1.5rem;
}

.agg-advice {
  margin-bottom: 15px;
}

.agg-advice h4 {
  font-size: 1rem;
  margin-bottom: 10px;
}

.agg-meta {
  text-align: right;
  font-size: 0.75rem;
  color: #6e7681;
  border-top: 1px solid rgba(210, 167, 109, 0.1);
  padding-top: 10px;
}

/* 深度分析按钮 */
.cyber-btn {
  pointer-events: auto;
  margin-top: 5px;
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important;
  color: #D2A76D !important;
  border-radius: 4px;
  padding: 8px 20px;
  font-size: 0.9rem;
  font-weight: bold;
  letter-spacing: 2px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.cyber-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 20px rgba(210, 167, 109, 0.4);
}

/* Element Plus 暗色覆盖 */
:deep(.el-checkbox__label) {
  color: #c9d1d9 !important;
}
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #D2A76D;
  border-color: #D2A76D;
}
:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #D2A76D !important;
}
:deep(.el-tag--warning) {
  --el-tag-bg-color: rgba(210, 167, 109, 0.15);
  --el-tag-text-color: #D2A76D;
  --el-tag-border-color: rgba(210, 167, 109, 0.3);
}
:deep(.el-tag--info) {
  --el-tag-bg-color: rgba(100, 100, 100, 0.2);
  --el-tag-text-color: #A0A0A0;
  --el-tag-border-color: rgba(100, 100, 100, 0.3);
}
</style>

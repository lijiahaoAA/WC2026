<template>
  <div class="prediction-page">
    <div class="header-action">
      <el-button type="info" plain @click="goBack" class="back-btn">&lt; 返回大屏指挥中心</el-button>
    </div>
    
    <div class="prediction-content">
      <div class="match-teams">
        <h1 class="team-text">{{ team1 }}</h1>
        <div class="vs-text">VS</div>
        <h1 class="team-text">{{ team2 }}</h1>
      </div>
      
      <div class="analysis-panel glass-panel">
        <div class="panel-header">
          <h2>智能赛事分析 (Qwen-3.7-Max)</h2>
          <el-button type="primary" @click="fetchAnalysis(true)" :loading="loading" class="cyber-btn">
            重新深度分析
          </el-button>
        </div>
        
        <div class="analysis-grid">
          <div class="grid-row">
            <div class="stat-box glass-panel">
              <h4>预测比分</h4>
              <div v-if="loadingScore" class="mini-loader"></div>
              <div v-else class="stat-value highlight">{{ analysisResult.score || '-' }}</div>
            </div>
            <div class="stat-box glass-panel">
              <h4>总进球数预测</h4>
              <div v-if="loadingGoals" class="mini-loader"></div>
              <div v-else class="stat-value">{{ analysisResult.total_goals || '-' }}</div>
            </div>
          </div>
          
          <div class="grid-row">
            <div class="stat-box glass-panel">
              <h4>红牌概率预警</h4>
              <div v-if="loadingRedCards" class="mini-loader"></div>
              <div v-else class="stat-value warning">{{ analysisResult.red_cards || '-' }}</div>
            </div>
            <div class="stat-box glass-panel">
              <h4>点球预测</h4>
              <div v-if="loadingPenalties" class="mini-loader"></div>
              <div v-else class="stat-value">{{ analysisResult.penalties || '-' }}</div>
            </div>
          </div>
          
          <div class="advice-box glass-panel">
            <h4>专家投注建议</h4>
            <div v-if="loadingAdvice" class="loading-box">
              <div class="loader"></div>
              <p>正在进行基本面与让球盘深度推演，请稍候...</p>
            </div>
            <div v-else class="advice-content" v-html="formatText(analysisResult.advice)"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const team1 = computed(() => route.query.team1 || '主队')
const team2 = computed(() => route.query.team2 || '客队')

const loading = computed(() => loadingScore.value || loadingGoals.value || loadingRedCards.value || loadingPenalties.value || loadingAdvice.value)

const loadingScore = ref(false)
const loadingGoals = ref(false)
const loadingRedCards = ref(false)
const loadingPenalties = ref(false)
const loadingAdvice = ref(false)

const analysisResult = ref<any>({
  score: '',
  total_goals: '',
  red_cards: '',
  penalties: '',
  advice: ''
})

const formatText = (text: string) => {
  if (!text) return ''
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const fetchField = async (field: string, endpoint: string, forceRefresh: boolean) => {
  const loadingRefs: Record<string, any> = {
    'score': loadingScore,
    'total_goals': loadingGoals,
    'red_cards': loadingRedCards,
    'penalties': loadingPenalties,
    'advice': loadingAdvice
  }
  
  const loadingRef = loadingRefs[field]
  loadingRef.value = true
  
  try {
    const res = await axios.post(`http://localhost:10086/api/predict/${endpoint}`, {
      team1_name: team1.value,
      team2_name: team2.value,
      force_refresh: forceRefresh
    })
    if (res.data.status === 'success') {
      analysisResult.value[field] = res.data.data
    } else {
      analysisResult.value[field] = '分析失败'
    }
  } catch (e: any) {
    analysisResult.value[field] = '请求错误'
  } finally {
    loadingRef.value = false
  }
}

const fetchAnalysis = (forceRefresh = false) => {
  if (forceRefresh) {
    analysisResult.value = { score: '', total_goals: '', red_cards: '', penalties: '', advice: '' }
  }
  
  fetchField('score', 'score', forceRefresh)
  fetchField('total_goals', 'goals', forceRefresh)
  fetchField('red_cards', 'red_cards', forceRefresh)
  fetchField('penalties', 'penalties', forceRefresh)
  fetchField('advice', 'advice', forceRefresh)
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  fetchAnalysis() // 首次进入自动获取（非强制刷新，优先取缓存）
})
</script>

<style scoped>
.prediction-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  color: #fff;
  pointer-events: none;
  padding: 40px;
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
  justify-content: center;
  align-items: center;
  pointer-events: none;
}

.match-teams {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-bottom: 40px;
}

.team-text {
  font-size: 4rem;
  font-weight: 900;
  text-shadow: 0 5px 15px rgba(0,0,0,0.8);
  -webkit-text-stroke: 1px rgba(0,0,0,0.5);
}

.vs-text {
  font-size: 3rem;
  font-style: italic;
  font-weight: 900;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(210, 167, 109, 0.5);
}

.analysis-panel {
  background: rgba(18, 18, 18, 0.75); /* 黑曜石底色 */
  backdrop-filter: blur(12px);
  padding: 30px;
  border-radius: 15px;
  width: 80%;
  max-width: 1000px;
  max-height: 80vh;
  overflow-y: auto;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(210, 167, 109, 0.2);
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.panel-header h2 {
  margin: 0;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

.cyber-btn {
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important; 
  color: #D2A76D !important;
  transition: all 0.3s;
}
.cyber-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 15px rgba(210, 167, 109, 0.4);
}

.analysis-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.grid-row {
  display: flex;
  gap: 20px;
}

.stat-box {
  flex: 1;
  background: rgba(30, 26, 23, 0.6); /* 古铜底色 */
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.stat-box h4 {
  margin: 0 0 10px 0;
  color: #A0A0A0; /* 中灰色 */
  font-size: 0.9rem;
  letter-spacing: 1px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #FFFFFF;
}

.stat-value.highlight {
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.2rem;
  text-shadow: 0 0 15px rgba(210, 167, 109, 0.4);
}

.stat-value.warning {
  color: #D2A76D; /* 统一使用香槟金 */
}

.advice-box {
  background: rgba(30, 26, 23, 0.4);
  border-radius: 8px;
  padding: 20px;
  flex: 1;
}

.advice-box h4 {
  margin: 0 0 15px 0;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.1rem;
}

.advice-content {
  line-height: 1.8;
  font-size: 1rem;
  color: #A0A0A0; /* 中灰色 */
}

.empty-box {
  text-align: center;
  padding: 40px;
  color: #A0A0A0;
}

/* 简单的加载动画 */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 40px 0;
  color: #A0A0A0;
  height: 100%;
}
.loader {
  border: 4px solid rgba(255,255,255,0.1);
  border-top: 4px solid #D2A76D; /* 香槟金 */
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

.mini-loader {
  border: 3px solid rgba(255,255,255,0.1);
  border-top: 3px solid #D2A76D; /* 香槟金 */
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 10px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
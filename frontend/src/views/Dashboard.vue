<template>
  <div class="dashboard-fullscreen">
    <!-- 最底层：超弱透明度的暗蓝灰数据网格 -->
    <div class="tech-grid"></div>
    
    <!-- 巨型柔和暗金环境光晕 (Ethereal backlight) -->
    <div class="ethereal-glow"></div>
    
    <!-- 顶部数据挂件区 -->
    <div class="top-widgets">
      <div class="widget-box glass-panel">
        <div class="w-title">下一场倒计时</div>
        <div class="w-value highlight">{{ countdownDays }} <span class="unit">天</span></div>
      </div>
      <div class="widget-box glass-panel">
        <div class="w-title">参赛队伍</div>
        <div class="w-value">48 <span class="unit">支</span></div>
      </div>
      <div class="widget-box glass-panel">
        <div class="w-title">总比赛场次</div>
        <div class="w-value">104 <span class="unit">场</span></div>
      </div>
    </div>

    <!-- 核心聚焦区：下一场比赛 (改为左右布局避开中心) -->
    <div class="focus-section" v-if="focusMatch">
      <div class="focus-title">
        <div class="live-dot"></div>
        <span>NEXT MATCH // {{ focusMatch?.group || '即将开赛' }}</span>
      </div>
      
      <div class="focus-match-display" @click="goToDetail(focusMatch)">
        <!-- 左侧面板：主队数据展示 -->
        <div class="side-data-panel left-data">
          <!-- 核心球员 -->
          <div class="data-card key-player glass-panel" v-if="team1Data && getTopPlayer(team1Data)">
            <div class="card-header">
              <h3>STAR PLAYER</h3>
              <p>战术核心</p>
            </div>
            <div class="card-body">
              <div class="kp-header">
                <span class="kp-name">{{ getTopPlayer(team1Data).name }}</span>
                <span class="kp-rating" :class="getRatingClass(getTopPlayer(team1Data).overall_rating)">{{ getTopPlayer(team1Data).overall_rating }}</span>
              </div>
              <div class="kp-stats" v-if="getTopPlayer(team1Data).stats">
                <span v-for="(val, key) in getTopPlayer(team1Data).stats" :key="key">{{ key }}: <strong class="highlight">{{ val }}</strong></span>
              </div>
            </div>
          </div>
          
          <!-- 预计首发 -->
          <div class="data-card starting-xi glass-panel" v-if="team1Data && team1Data.players">
            <div class="card-header">
              <h3>STARTING XI</h3>
              <p>预计首发</p>
            </div>
            <div class="card-body player-list">
              <div class="player-item" v-for="player in team1Data.players.filter((p: any) => p.is_starter)" :key="player.name">
                <div class="p-pos" :class="getPosClass(player.position)">{{ player.position }}</div>
                <div class="p-info">
                  <div class="p-name">
                    {{ player.name }} 
                    <span class="p-club" v-if="player.club">({{ player.club }})</span>
                    <span class="starter-badge">首发</span>
                  </div>
                  <div class="p-meta">
                    <span v-if="player.age">{{ player.age }}岁</span>
                    <span v-if="player.height"> | {{ player.height }}cm</span>
                    <span v-if="player.weight"> | {{ player.weight }}kg</span>
                    <span v-if="player.preferred_foot"> | {{ player.preferred_foot }}</span>
                    <span v-if="player.market_value"> | {{ player.market_value }}</span>
                  </div>
                </div>
                <div class="p-rating" :class="getRatingClass(player.overall_rating)">{{ player.overall_rating || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- 无数据缺省态 -->
          <div class="data-card glass-panel" v-if="!team1Data">
            <div class="card-body empty-data">
              暂无球队数据，待录入...
            </div>
          </div>
        </div>

        <!-- 左侧主队名与档案 -->
        <div class="team-panel left-team">
          <div class="team-card glass-panel">
            <h1 class="team-name">{{ focusMatch.team1 }}</h1>
            <div class="team-info-blocks" v-if="team1Data">
              <div class="info-block">
                <span class="block-label">FIFA</span>
                <strong class="block-value highlight">{{ team1Data.fifa_ranking }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">总身价</span>
                <strong class="block-value highlight">{{ team1Data.total_value }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">主帅</span>
                <strong class="block-value">{{ team1Data.coach }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">阵型</span>
                <strong class="block-value">{{ team1Data.formation }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">平均年龄</span>
                <strong class="block-value">{{ team1Data.avg_age }} 岁</strong>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 中间信息(包含主客场标签) -->
        <div class="vs-panel-wrapper">
          <div class="side-tag home-tag">主场</div>
          <div class="vs-panel">
            <div class="vs-text">VS</div>
            <div class="match-info-pill">
              <span class="group">{{ focusMatch.group }}</span>
              <span class="time">{{ focusMatch.date }} {{ focusMatch.time }}</span>
            </div>
            <div class="stadium"><el-icon><Location /></el-icon> {{ focusMatch.stadium }}</div>
            <el-button type="primary" class="cyber-btn" @click.stop="goToDetail(focusMatch)">
              <span>启动分析引擎</span>
            </el-button>
          </div>
          <div class="side-tag away-tag">客场</div>
        </div>
        
        <!-- 右侧客队名与档案 -->
        <div class="team-panel right-team">
          <div class="team-card glass-panel">
            <h1 class="team-name">{{ focusMatch.team2 }}</h1>
            <div class="team-info-blocks" v-if="team2Data">
              <div class="info-block">
                <span class="block-label">FIFA</span>
                <strong class="block-value highlight">{{ team2Data.fifa_ranking }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">总身价</span>
                <strong class="block-value highlight">{{ team2Data.total_value }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">主帅</span>
                <strong class="block-value">{{ team2Data.coach }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">阵型</span>
                <strong class="block-value">{{ team2Data.formation }}</strong>
              </div>
              <div class="info-block">
                <span class="block-label">平均年龄</span>
                <strong class="block-value">{{ team2Data.avg_age }} 岁</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧面板：客队数据展示 -->
        <div class="side-data-panel right-data">
          <!-- 核心球员 -->
          <div class="data-card key-player glass-panel" v-if="team2Data && getTopPlayer(team2Data)">
            <div class="card-header">
              <h3>STAR PLAYER</h3>
              <p>战术核心</p>
            </div>
            <div class="card-body">
              <div class="kp-header">
                <span class="kp-name">{{ getTopPlayer(team2Data).name }}</span>
                <span class="kp-rating" :class="getRatingClass(getTopPlayer(team2Data).overall_rating)">{{ getTopPlayer(team2Data).overall_rating }}</span>
              </div>
              <div class="kp-stats" v-if="getTopPlayer(team2Data).stats">
                <span v-for="(val, key) in getTopPlayer(team2Data).stats" :key="key">{{ key }}: <strong class="highlight">{{ val }}</strong></span>
              </div>
            </div>
          </div>
          
          <!-- 预计首发 -->
          <div class="data-card starting-xi glass-panel" v-if="team2Data && team2Data.players">
            <div class="card-header">
              <h3>STARTING XI</h3>
              <p>预计首发</p>
            </div>
            <div class="card-body player-list">
              <div class="player-item" v-for="player in team2Data.players.filter((p: any) => p.is_starter)" :key="player.name">
                <div class="p-pos" :class="getPosClass(player.position)">{{ player.position }}</div>
                <div class="p-info">
                  <div class="p-name">
                    {{ player.name }} 
                    <span class="p-club" v-if="player.club">({{ player.club }})</span>
                    <span class="starter-badge">首发</span>
                  </div>
                  <div class="p-meta">
                    <span v-if="player.age">{{ player.age }}岁</span>
                    <span v-if="player.height"> | {{ player.height }}cm</span>
                    <span v-if="player.weight"> | {{ player.weight }}kg</span>
                    <span v-if="player.preferred_foot"> | {{ player.preferred_foot }}</span>
                    <span v-if="player.market_value"> | {{ player.market_value }}</span>
                  </div>
                </div>
                <div class="p-rating" :class="getRatingClass(player.overall_rating)">{{ player.overall_rating || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- 无数据缺省态 -->
          <div class="data-card glass-panel" v-if="!team2Data">
            <div class="card-body empty-data">
              暂无球队数据，待录入...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部赛程区 -->
    <div class="schedule-section">
      <div class="section-header">
        <div class="section-title">
          <span class="bracket">[</span> MATCH SCHEDULE <span class="bracket">]</span>
        </div>
        <!-- 搜索框 -->
        <div class="search-box">
          <el-input
            v-model="searchTeam"
            placeholder="搜索球队..."
            clearable
            size="small"
            class="search-input"
            prefix-icon="Search"
          />
        </div>
      </div>
      <div class="match-grid" ref="matchGridRef">
        <div
          class="grid-card glass-panel"
          :class="{ 'is-past': isPast(match), 'has-prediction': match.has_prediction }"
          v-for="(match, index) in filteredMatches"
          :key="index"
          @click="goToDetail(match)"
        >
          <div class="card-glow" style="pointer-events:none;"></div>
          <div class="card-header">
            <span class="card-group">{{ match.group }}</span>
            <span class="card-time">{{ match.time }}</span>
          </div>
          <!-- 有比分时显示比分，否则显示 vs -->
          <div v-if="match.team1_score !== null && match.team1_score !== undefined" class="card-score">
            <span class="s-team">{{ match.team1 }}</span>
            <span class="s-num">{{ match.team1_score }}</span>
            <span class="s-sep">-</span>
            <span class="s-num">{{ match.team2_score }}</span>
            <span class="s-team">{{ match.team2 }}</span>
          </div>
          <div v-else class="card-teams">
            <span class="t-name">{{ match.team1 }}</span>
            <span class="t-vs">vs</span>
            <span class="t-name">{{ match.team2 }}</span>
          </div>
          <div class="card-footer">
            {{ match.date }}<br/>{{ match.stadium }}
          </div>
          <!-- 状态标签：左下角赛事状态 + 右下角分析状态 -->
          <div class="card-badges">
            <div v-if="isPast(match)" class="card-badge past">已开赛</div>
            <div v-else class="card-badge upcoming">未开赛</div>
            <div v-if="match.has_prediction" class="card-badge predicted">已分析</div>
          </div>
        </div>
        <div v-if="filteredMatches.length === 0" class="no-matches">
          暂无匹配的赛程
        </div>
      </div>
    </div>

    <!-- 比赛结果弹窗：传送到 body 避免 pointer-events 问题 -->
    <Teleport to="body">
      <el-dialog v-model="resultDialogVisible" width="600px" class="result-dialog" :show-close="true" destroy-on-close>
      <template #header>
        <div class="result-title">
          <span>{{ resultMatch?.group }}</span>
        </div>
      </template>
      <div v-if="resultMatch" class="result-content">
        <!-- 比分 -->
        <div class="result-score-row">
          <div class="result-team">
            <h2>{{ resultMatch.team1 }}</h2>
          </div>
          <div class="result-score-box">
            <span class="result-num">{{ resultMatch.team1_score ?? '-' }}</span>
            <span class="result-sep">:</span>
            <span class="result-num">{{ resultMatch.team2_score ?? '-' }}</span>
          </div>
          <div class="result-team">
            <h2>{{ resultMatch.team2 }}</h2>
          </div>
        </div>
        <div class="result-info">
          <span>{{ resultMatch.date }} {{ resultMatch.time }}</span>
          <span>{{ resultMatch.stadium }}</span>
        </div>

        <!-- 预测结果（如有） -->
        <div v-if="resultMatch.has_prediction" class="result-prediction">
          <h4>赛前预测 vs 实际结果</h4>
          <div v-for="(pred, mid) in matchPredictions" :key="mid" class="pred-block">
            <div class="pred-model">{{ mid }}</div>
            <div class="pred-detail">
              <span>预测比分: <strong>{{ pred.score || '-' }}</strong></span>
              <span>总进球: <strong>{{ pred.total_goals || '-' }}</strong></span>
            </div>
          </div>
          <div v-if="Object.keys(matchPredictions).length === 0" class="pred-empty">
            加载预测数据中...
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <el-button type="primary" class="cyber-btn" @click="viewPrediction(resultMatch)">
            查看完整预测分析
          </el-button>
        </div>
      </div>
    </el-dialog>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Location } from '@element-plus/icons-vue'

const router = useRouter()
const scheduleData = ref<any[]>([])
const team1Data = ref<any>(null)
const team2Data = ref<any>(null)
const searchTeam = ref('')
const matchGridRef = ref<HTMLElement | null>(null)

// 将赛程中的日期时间字符串转为 Date 对象
function parseMatchDate(match: any): Date {
  const dateStr = match.date.replace(/年|月/g, '-').replace('日', '')
  return new Date(`${dateStr}T${match.time}:00`)
}

function isPast(match: any): boolean {
  return parseMatchDate(match) <= new Date()
}

// 过滤出尚未开赛的比赛（用于焦点比赛）
const upcomingSchedule = computed(() => {
  const now = new Date()
  return scheduleData.value.filter(m => parseMatchDate(m) > now)
})

const focusMatch = computed(() => {
  return upcomingSchedule.value.length > 0 ? upcomingSchedule.value[0] : null
})

const countdownDays = computed(() => {
  if (!focusMatch.value) return 0
  const now = new Date()
  const kickoff = parseMatchDate(focusMatch.value)
  const diff = kickoff.getTime() - now.getTime()
  return diff > 0 ? Math.ceil(diff / (1000 * 3600 * 24)) : 0
})

// 搜索过滤后的所有比赛（已赛+未赛）
const filteredMatches = computed(() => {
  const q = searchTeam.value.trim().toLowerCase()
  if (!q) return scheduleData.value
  return scheduleData.value.filter(m =>
    m.team1.toLowerCase().includes(q) || m.team2.toLowerCase().includes(q)
  )
})

const fetchTeamData = async (teamName: string, isTeam1: boolean) => {
  try {
    const res = await axios.get(`http://localhost:10086/api/team/${teamName}`)
    if (res.data.status === 'success') {
      if (isTeam1) team1Data.value = res.data.data
      else team2Data.value = res.data.data
    } else {
      if (isTeam1) team1Data.value = null
      else team2Data.value = null
    }
  } catch (e) {
    if (isTeam1) team1Data.value = null
    else team2Data.value = null
  }
}

watch(focusMatch, (newMatch) => {
  if (newMatch) {
    fetchTeamData(newMatch.team1, true)
    fetchTeamData(newMatch.team2, false)
  }
}, { immediate: true })

const fetchSchedule = async () => {
  try {
    const res = await axios.get('http://localhost:10086/api/schedule/all')
    scheduleData.value = res.data
    // 赛程加载完成后，立即获取焦点比赛的球队数据
    if (focusMatch.value) {
      fetchTeamData(focusMatch.value.team1, true)
      fetchTeamData(focusMatch.value.team2, false)
    }
    // 自动滚动到下一场未开赛比赛
    scrollToNextMatch()
  } catch (error) {
    ElMessage.error('无法加载赛程数据，请检查后端服务')
  }
}

function scrollToNextMatch() {
  nextTick(() => {
    if (!matchGridRef.value) return
    const cards = matchGridRef.value.querySelectorAll('.grid-card')
    const now = new Date()
    // 找到第一个未开赛的卡片
    for (let i = 0; i < filteredMatches.value.length; i++) {
      if (!isPast(filteredMatches.value[i])) {
        const card = cards[i] as HTMLElement
        if (card) {
          // 滚动到该卡片的左边缘对齐容器左边缘
          const offsetLeft = card.offsetLeft
          matchGridRef.value.scrollTo({ left: offsetLeft - 10, behavior: 'smooth' })
        }
        break
      }
    }
  })
}

const getPosClass = (pos: string) => {
  if (pos === '门将') return 'pos-gk'
  if (pos === '后卫') return 'pos-df'
  if (pos === '中场') return 'pos-mf'
  if (pos === '前锋') return 'pos-fw'
  return ''
}

const getTopPlayer = (teamData: any) => {
  if (!teamData || !teamData.players) return null;
  const players = teamData.players.filter((p: any) => p.position !== '教练' && p.overall_rating);
  if (players.length === 0) return null;
  return players.reduce((prev: any, current: any) => (prev.overall_rating > current.overall_rating) ? prev : current);
}

const getRatingClass = (rating: number) => {
  if (!rating) return 'rating-gray';
  if (rating >= 80) return 'rating-gold';
  if (rating >= 70) return 'rating-silver';
  return 'rating-bronze';
}

// 比赛结果弹窗
const resultDialogVisible = ref(false)
const resultMatch = ref<any>(null)
const matchPredictions = ref<Record<string, any>>({})

const goToDetail = (match: any) => {
  // 已完赛且有比分 → 弹出比赛结果
  if (match.team1_score !== null && match.team1_score !== undefined) {
    showMatchResult(match)
  } else {
    // 未开赛 → 跳转预测页
    router.push({
      path: '/prediction',
      query: { team1: match.team1, team2: match.team2 }
    })
  }
}

async function showMatchResult(match: any) {
  resultMatch.value = match
  resultDialogVisible.value = true
  matchPredictions.value = {}

  // 加载该比赛的预测数据
  try {
    const res = await axios.get(`http://localhost:10086/api/predictions/history/${match.team1}/${match.team2}`)
    if (res.data.status === 'success') {
      matchPredictions.value = res.data.data
    }
  } catch (e) {
    // ignore
  }
}

function viewPrediction(match: any) {
  resultDialogVisible.value = false
  router.push({
    path: '/prediction',
    query: { team1: match.team1, team2: match.team2 }
  })
}

onMounted(async () => {
  await fetchSchedule()
})
</script>

<style scoped>
/* 全局网格背景 */
.dashboard-fullscreen::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(210, 167, 109, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(210, 167, 109, 0.03) 1px, transparent 1px);
  background-size: 30px 30px;
  z-index: 0;
  pointer-events: none;
}

.dashboard-fullscreen {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  color: #fff;
  overflow: hidden;
  position: relative;
  pointer-events: none; /* 让顶层穿透 */
  background: transparent; /* 确保自身透明 */
}

/* ================= 科幻指挥中心环境底座 ================= */
.tech-grid {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  /* 极微弱的暗蓝灰色网格，透明度 < 4% */
  background-image: 
    linear-gradient(rgba(44, 58, 71, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(44, 58, 71, 0.035) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: 0;
  pointer-events: none;
}

/* 巨型、柔和、无边界的暗金环境光晕 */
.ethereal-glow {
  position: absolute;
  top: -10%; /* 定位在顶部偏上，从 "VS" 后方向下辐射 */
  left: 50%;
  transform: translateX(-50%);
  width: 1600px;
  height: 1200px;
  background: radial-gradient(ellipse at top center, rgba(210, 167, 109, 0.45) 0%, rgba(210, 167, 109, 0.2) 40%, transparent 70%);
  filter: blur(100px); /* 极大的高斯模糊，消除任何可见边界 */
  z-index: 1; /* 在网格之上，3D 模型之下 */
  pointer-events: none;
}

/* ======= 顶部挂件优化 ======= */
.top-widgets {
  position: absolute;
  top: 60px; /* 从 90px 上移到 60px，与中央球队卡片的视觉顶部保持完全一致 */
  right: 30px;
  display: flex;
  gap: 15px;
  z-index: 20;
}

.widget-box {
  background: rgba(30, 26, 23, 0.6); /* 深古铜底色 */
  padding: 6px 15px;
  border-radius: 6px;
  backdrop-filter: blur(5px);
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 80px;
}

.w-title {
  font-size: 0.7rem;
  color: #A0A0A0; /* 中灰色文本 */
  text-transform: uppercase;
  letter-spacing: 1px;
}

.w-value {
  font-size: 1.2rem;
  font-weight: 900;
  font-family: 'Courier New', Courier, monospace;
  color: #D2A76D; /* 香槟金 */
  text-shadow: 0 0 10px rgba(210, 167, 109, 0.3);
}

.w-value.highlight {
  color: #D2A76D; /* 统一为香槟金 */
  text-shadow: 0 0 15px rgba(210, 167, 109, 0.6);
}

.unit {
  font-size: 0.7rem;
  color: #A0A0A0;
}

/* ================= 核心聚焦区 ================= */
.focus-section {
  flex: 1; 
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 改为靠上，避免挡住中心模型 */
  align-items: center;
  padding-top: 50px;
  width: 100%;
  height: 100%;
  z-index: 10;
}

.focus-title {
  position: absolute;
  top: 20px;
  left: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 800;
  color: #D2A76D; /* 香槟金 */
  letter-spacing: 3px;
  text-shadow: 0 0 10px rgba(210, 167, 109, 0.5);
  background: rgba(30, 26, 23, 0.8);
  padding: 6px 15px;
  border-radius: 4px;
  border-left: 4px solid #D2A76D;
}

.live-dot {
  width: 8px;
  height: 8px;
  background-color: #D2A76D; /* 香槟金闪烁点 */
  border-radius: 50%;
  box-shadow: 0 0 10px #D2A76D;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.5); opacity: 1; box-shadow: 0 0 20px #D2A76D; }
  100% { transform: scale(0.9); opacity: 0.7; }
}

.focus-match-display {
  display: flex;
  justify-content: space-between; /* 极大地拉开两队距离 */
  align-items: center;
  width: 95%;
  max-width: 1700px;
  pointer-events: none; 
}

/* ======= 两侧数据面板 (效果图还原) ======= */
.side-data-panel {
  position: absolute;
  top: 140px; /* 从 70px 下移到 140px，远离顶部状态栏 */
  width: 420px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 10;
  max-height: calc(100vh - 250px); /* 相应减少 max-height 防止触底 */
}
.left-data { left: 20px; }
.right-data { right: 20px; }

.data-card {
  background: rgba(18, 18, 18, 0.75); /* 黑曜石底色 */
  border-radius: 8px;
  padding: 12px;
  backdrop-filter: blur(12px);
}

.starting-xi {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 8px;
  margin-bottom: 10px;
  text-align: center;
  flex-shrink: 0;
}
.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}
.card-header p {
  margin: 3px 0 0;
  font-size: 0.85rem;
  color: #A0A0A0;
}

/* 球队信息与首发球员样式 */
.empty-data {
  text-align: center;
  color: #A0A0A0;
  font-style: italic;
  padding: 20px 0;
}

.team-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 15px;
}
.team-info .info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  font-size: 0.85rem;
  border-bottom: 1px dashed rgba(210, 167, 109, 0.15); /* 香槟金弱虚线 */
  padding-bottom: 4px;
}
.team-info .info-row span:first-child {
  color: #A0A0A0;
}
.team-info .info-row .highlight {
  color: #D2A76D; /* 香槟金 */
  font-weight: bold;
}
.truncate-text {
  max-width: 90px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: right;
}

/* 核心球员 */
.kp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.kp-name {
  font-weight: 900;
  font-size: 1.1rem;
  color: #fff;
  text-shadow: 0 0 10px rgba(255,255,255,0.3);
}
.kp-rating {
  font-size: 1.3rem;
  font-weight: 900;
  font-family: 'Courier New', Courier, monospace;
  color: #D2A76D;
}
.kp-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  font-size: 0.75rem;
  color: #A0A0A0;
}
.kp-stats span {
  background: rgba(210, 167, 109, 0.05);
  padding: 4px;
  border-radius: 4px;
  text-align: center;
  border: 1px solid rgba(210, 167, 109, 0.15);
}

.player-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  padding-right: 5px;
}
.player-list::-webkit-scrollbar {
  width: 4px;
}
.player-list::-webkit-scrollbar-thumb {
  background: rgba(210, 167, 109, 0.5); /* 香槟金滚动条 */
  border-radius: 4px;
}
.player-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed rgba(210, 167, 109, 0.15);
}
.player-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.p-pos {
  font-size: 0.75rem;
  padding: 3px 6px;
  border-radius: 4px;
  min-width: 35px;
  text-align: center;
  font-weight: bold;
}
.pos-gk { color: #A0A0A0; border: 1px solid #A0A0A0; background: rgba(160, 160, 160, 0.1); } 
.pos-df { color: #D2A76D; border: 1px solid #D2A76D; background: rgba(210, 167, 109, 0.1); } 
.pos-mf { color: #D2A76D; border: 1px solid #D2A76D; background: rgba(210, 167, 109, 0.1); } 
.pos-fw { color: #D2A76D; border: 1px solid #D2A76D; background: rgba(210, 167, 109, 0.1); }

.p-info {
  display: flex;
  flex-direction: column;
  min-width: 0; /* 防止文本溢出 */
  line-height: 1.2;
}
.p-name {
  font-size: 1rem;
  font-weight: bold;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
}
.p-club {
  font-size: 0.75rem;
  font-weight: normal;
  color: #A0A0A0;
  margin-left: 4px;
}
.starter-badge {
  font-size: 0.6rem;
  background: rgba(210, 167, 109, 0.15);
  color: #D2A76D;
  border: 1px solid rgba(210, 167, 109, 0.4);
  padding: 1px 4px;
  border-radius: 3px;
  margin-left: 6px;
  font-weight: normal;
  letter-spacing: 1px;
}
.p-meta {
  font-size: 0.7rem;
  color: #A0A0A0;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.p-rating {
  font-weight: 900;
  font-family: 'Courier New', Courier, monospace;
  font-size: 1.1rem;
  margin-left: auto;
}
.rating-gold { color: #D2A76D; text-shadow: 0 0 8px rgba(210, 167, 109, 0.6); } 
.rating-silver { color: #A67C41; text-shadow: 0 0 8px rgba(166, 124, 65, 0.6); } 
.rating-bronze { color: #8A6327; text-shadow: 0 0 8px rgba(138, 99, 39, 0.6); } 
.rating-gray { color: #A0A0A0; }

/* ======= 球队面板科技感排版 ======= */
.team-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  flex: 1;
  position: relative;
  margin-top: -60px; /* 下移，避免贴近顶部状态栏 */
}

.left-team { align-items: flex-end; text-align: right; padding-right: 40px; }
.right-team { align-items: flex-start; text-align: left; padding-left: 40px; }

.team-card {
  background: rgba(18, 18, 18, 0.75);
  padding: 20px 30px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center; /* 让内部的球队名和数据方块整体居中 */
  backdrop-filter: blur(12px);
  max-width: 600px; /* 增加宽度，防止小方块换行 */
}

.left-team .team-card { /* 移除覆盖 align-items */ }
.right-team .team-card { /* 移除覆盖 align-items */ }

/* 废弃旧的 team-tag */
.team-tag { display: none; }

.team-name {
  font-size: 3rem; /* 略微缩小，避免喧宾夺主 */
  font-weight: 900;
  margin: 0 0 10px 0; /* 调整 margin */
  letter-spacing: 2px;
  text-align: center; /* 文字居中 */
  color: #ffffff; /* 纯白文字 */
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.4), 0 0 30px rgba(255, 255, 255, 0.2); /* 柔和的高级发光 */
  -webkit-text-stroke: 0; /* 移除描边 */
  position: relative;
  z-index: 2;
  white-space: nowrap;
}

/* 队名下方横向排列的球队档案模块框 */
.team-info-blocks {
  display: flex;
  flex-wrap: nowrap; /* 强制不换行 */
  justify-content: center; /* 方块整体居中 */
  gap: 12px;
}

.left-team .team-info-blocks { /* 移除覆盖 justify-content */ }
.right-team .team-info-blocks { /* 移除覆盖 justify-content */ }

.info-block {
  background: rgba(30, 26, 23, 0.4); /* 弱化背景，融入大卡片 */
  border: 1px solid rgba(210, 167, 109, 0.15); /* 弱化边框 */
  padding: 6px 12px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
}

.info-block .block-label {
  color: #A0A0A0;
  text-transform: uppercase;
  font-size: 0.65rem;
  letter-spacing: 1px;
  margin-bottom: 3px;
}

.info-block .block-value {
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: bold;
}

.info-block .block-value.highlight {
  color: #D2A76D;
  text-shadow: 0 0 10px rgba(210, 167, 109, 0.4);
}

/* 彻底删除 team-glitch 特效类 */

/* ======= 中间 VS 面板及侧边标签 ======= */
.vs-panel-wrapper {
  display: flex;
  align-items: center;
  gap: 15px; /* 缩小标签和 VS 中心的距离 */
  transform: translateY(-20px);
}

.side-tag {
  font-size: 1rem;
  font-weight: bold;
  color: #D2A76D; /* 浅香槟金文本 */
  letter-spacing: 2px;
  background: rgba(30, 26, 23, 0.6); /* 古铜底色 */
  backdrop-filter: blur(10px);
  padding: 5px 15px;
  border-radius: 20px;
  border: 1px solid rgba(210, 167, 109, 0.2);
  text-shadow: none;
  opacity: 1;
  white-space: nowrap;
  margin-top: -30px;
}
.home-tag { 
  background: linear-gradient(90deg, rgba(210, 167, 109, 0.15), transparent);
  border-left: 3px solid #D2A76D;
  border-right: none;
  padding-left: 20px;
}
.away-tag { 
  background: linear-gradient(-90deg, rgba(210, 167, 109, 0.15), transparent);
  border-right: 3px solid #D2A76D;
  border-left: none;
  padding-right: 20px;
}

.vs-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  flex: 0 0 300px;
  background: radial-gradient(circle at center, rgba(0,0,0,0.6) 0%, transparent 70%);
  padding: 15px;
  border-radius: 50%;
  margin-top: -30px;
}

.vs-text {
  font-size: 1.8rem;
  font-weight: 900;
  color: #D2A76D; /* 香槟金 VS */
  text-shadow: 0 0 15px rgba(210, 167, 109, 0.6);
  font-style: italic;
  margin-bottom: -5px;
}

.match-info-pill {
  display: flex;
  gap: 12px;
  background: rgba(30, 26, 23, 0.8);
  border: 1px solid #D2A76D; /* 香槟金 */
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  box-shadow: 0 0 15px rgba(210, 167, 109, 0.2);
}

.group { color: #D2A76D; font-weight: bold; }

.stadium {
  font-size: 0.85rem;
  color: #A0A0A0;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(0,0,0,0.4);
  padding: 5px 12px;
  border-radius: 20px;
}

/* 赛博朋克按钮 -> 奢华金属按钮 */
.cyber-btn {
  pointer-events: auto;
  margin-top: 5px;
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important; /* 香槟金按钮 */
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
.cyber-btn::before {
  content: '';
  position: absolute;
  top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(210, 167, 109, 0.4), transparent);
  transition: all 0.5s;
}
.cyber-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 20px rgba(210, 167, 109, 0.4);
}
.cyber-btn:hover::before {
  left: 100%;
}

/* ================= 底部赛程滑动区 ================= */
.schedule-section {
  flex: 0 0 auto; 
  padding: 5px 30px 10px;
  background: linear-gradient(to top, rgba(18,18,18,0.9) 0%, rgba(18,18,18,0.4) 50%, transparent 100%);
  z-index: 10;
  pointer-events: auto; 
}

.section-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: #A0A0A0;
  margin-bottom: 10px;
  letter-spacing: 2px;
}
.bracket { color: #D2A76D; }

.match-grid {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding-bottom: 5px;
  scrollbar-width: thin;
  scrollbar-color: #D2A76D transparent;
}
.match-grid::-webkit-scrollbar {
  height: 4px;
}
.match-grid::-webkit-scrollbar-thumb {
  background: #D2A76D;
  border-radius: 4px;
}

.grid-card {
  flex: 0 0 200px;
  height: 90px;
  background: rgba(30, 26, 23, 0.6);
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  border-radius: 6px;
  pointer-events: auto;
}

.grid-card:hover {
  transform: translateY(-5px);
  background: rgba(45, 38, 30, 0.8);
  box-shadow: 0 20px 40px rgba(0,0,0,0.8), inset 4px 0 10px rgba(210, 167, 109, 0.5), inset 2px 2px 15px rgba(255, 193, 7, 0.05), inset -2px -2px 15px rgba(255, 193, 7, 0.05) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #A0A0A0;
}

.card-group { color: #D2A76D; font-weight: bold; }

.card-teams {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  font-size: 1rem;
  font-weight: bold;
}

.t-vs { font-size: 0.75rem; color: #A67C41; font-style: italic; }

/* 比分显示 */
.card-score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
  font-weight: bold;
}

.s-team {
  max-width: 70px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.s-num {
  font-size: 1.3rem;
  font-weight: 900;
  font-family: 'Courier New', Courier, monospace;
  color: #D2A76D;
  text-shadow: 0 0 8px rgba(210, 167, 109, 0.4);
  min-width: 20px;
  text-align: center;
}

.s-sep {
  color: #6e7681;
  font-size: 1rem;
}

.card-footer {
  font-size: 0.65rem;
  color: #6e7681;
  text-align: center;
  margin-bottom: 14px; /* 给底部标签留空间 */
}

/* ====== 赛程区头部 + 搜索框 ====== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.search-box {
  pointer-events: auto;
}

.search-input {
  width: 180px;
}
:deep(.search-input .el-input__wrapper) {
  background: rgba(30, 26, 23, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(210, 167, 109, 0.3) inset !important;
  border-radius: 4px;
}
:deep(.search-input .el-input__inner) {
  color: #c9d1d9 !important;
  font-size: 0.8rem;
}
:deep(.search-input .el-input__inner::placeholder) {
  color: #6e7681 !important;
}
:deep(.search-input .el-input__prefix .el-icon) {
  color: #D2A76D;
}

/* ====== 已赛卡片样式 ====== */
.grid-card.is-past {
  opacity: 0.7;
  background: rgba(20, 20, 25, 0.6);
  border: 1px solid rgba(100, 100, 100, 0.15);
}

.grid-card.is-past:hover {
  opacity: 1;
  border-color: rgba(210, 167, 109, 0.4);
}

.grid-card.has-prediction {
  border: 1px solid rgba(210, 167, 109, 0.25);
}

.grid-card.has-prediction:hover {
  border-color: #D2A76D;
}

/* ====== 卡片状态标签 ====== */
.card-badges {
  position: absolute;
  bottom: 4px;
  left: 4px;
  right: 4px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.card-badge {
  font-size: 0.5rem;
  padding: 1px 5px;
  border-radius: 3px;
  letter-spacing: 1px;
  font-weight: bold;
  line-height: 1.4;
}

.card-badge.predicted {
  background: rgba(210, 167, 109, 0.2);
  color: #D2A76D;
  border: 1px solid rgba(210, 167, 109, 0.4);
}

.card-badge.past {
  background: rgba(100, 100, 100, 0.2);
  color: #8b949e;
  border: 1px solid rgba(100, 100, 100, 0.3);
}

.card-badge.upcoming {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.grid-card {
  position: relative;
}

.no-matches {
  color: #6e7681;
  font-style: italic;
  padding: 20px;
  text-align: center;
  width: 100%;
}

/* ====== 比赛结果弹窗（Teleport 到 body，用全局样式） ====== */
</style>
<style>
.result-dialog .el-dialog {
  background: #161b22 !important;
  border: 1px solid rgba(210, 167, 109, 0.2) !important;
  border-radius: 12px;
}
.result-dialog .el-dialog__header {
  border-bottom: 1px solid rgba(210, 167, 109, 0.15);
  padding: 15px 20px;
}
.result-dialog .el-dialog__body {
  padding: 20px;
}
</style>
<style scoped>

.result-title {
  color: #D2A76D;
  font-size: 1rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.result-content {
  color: #c9d1d9;
}

.result-score-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
  margin-bottom: 15px;
}

.result-team h2 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 900;
  text-align: center;
  color: #fff;
}

.result-score-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(30, 26, 23, 0.8);
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid rgba(210, 167, 109, 0.3);
}

.result-num {
  font-size: 2.5rem;
  font-weight: 900;
  font-family: 'Courier New', Courier, monospace;
  color: #D2A76D;
  text-shadow: 0 0 15px rgba(210, 167, 109, 0.5);
  min-width: 40px;
  text-align: center;
}

.result-sep {
  font-size: 2rem;
  color: #6e7681;
}

.result-info {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 0.8rem;
  color: #A0A0A0;
  margin-bottom: 20px;
}

.result-prediction {
  background: rgba(30, 26, 23, 0.6);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.result-prediction h4 {
  margin: 0 0 12px 0;
  color: #D2A76D;
  font-size: 0.9rem;
  letter-spacing: 1px;
}

.pred-block {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px dashed rgba(210, 167, 109, 0.1);
}
.pred-block:last-child {
  border-bottom: none;
}

.pred-model {
  color: #A0A0A0;
  font-size: 0.8rem;
}

.pred-detail {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
  color: #c9d1d9;
}

.pred-detail strong {
  color: #D2A76D;
}

.pred-empty {
  color: #6e7681;
  font-style: italic;
  text-align: center;
  padding: 10px;
}

.result-actions {
  text-align: center;
  margin-top: 15px;
}

.cyber-btn {
  pointer-events: auto;
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important;
  color: #D2A76D !important;
  border-radius: 4px;
  padding: 8px 20px;
  font-size: 0.9rem;
  font-weight: bold;
  letter-spacing: 2px;
  transition: all 0.3s;
}
.cyber-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 20px rgba(210, 167, 109, 0.4);
}
</style>
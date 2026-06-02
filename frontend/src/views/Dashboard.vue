<template>
  <div class="dashboard-fullscreen">
    <!-- 装饰性背景网格和科技光线 -->
    <div class="tech-grid"></div>
    <div class="tech-lines">
      <div class="line line-1"></div>
      <div class="line line-2"></div>
      <div class="line line-3"></div>
    </div>

    <!-- 顶部数据挂件区 -->
    <div class="top-widgets">
      <div class="widget-box">
        <div class="w-title">赛事倒计时</div>
        <div class="w-value highlight">{{ countdownDays }} <span class="unit">天</span></div>
      </div>
      <div class="widget-box">
        <div class="w-title">参赛队伍</div>
        <div class="w-value">48 <span class="unit">支</span></div>
      </div>
      <div class="widget-box">
        <div class="w-title">总比赛场次</div>
        <div class="w-value">104 <span class="unit">场</span></div>
      </div>
    </div>

    <!-- 核心聚焦区：下一场比赛 (改为左右布局避开中心) -->
    <div class="focus-section" v-if="focusMatch">
      <div class="focus-title">
        <div class="live-dot"></div>
        <span>NEXT MATCH // 揭幕战</span>
      </div>
      
      <div class="focus-match-display" @click="goToDetail(focusMatch)">
        <!-- 左侧面板：主队数据展示 -->
        <div class="side-data-panel left-data">
          <!-- 球队档案 -->
          <div class="data-card" v-if="team1Data">
            <div class="card-header">
              <h3>TEAM INFO</h3>
              <p>球队档案</p>
            </div>
            <div class="card-body team-info">
              <div class="info-row"><span>FIFA排名:</span> <span class="highlight">{{ team1Data.fifa_ranking }}</span></div>
              <div class="info-row"><span>总身价:</span> <span class="highlight">{{ team1Data.total_value }}</span></div>
              <div class="info-row"><span>主教练:</span> <span>{{ team1Data.coach }}</span></div>
              <div class="info-row"><span>阵型偏好:</span> <span>{{ team1Data.formation }}</span></div>
              <div class="info-row"><span>平均年龄:</span> <span>{{ team1Data.avg_age }} 岁</span></div>
              <div class="info-row"><span>主场馆:</span> <span class="truncate-text" :title="team1Data.stadium">{{ team1Data.stadium }}</span></div>
            </div>
          </div>

          <!-- 核心球员 -->
          <div class="data-card key-player" v-if="team1Data && getTopPlayer(team1Data)">
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
          <div class="data-card starting-xi" v-if="team1Data && team1Data.players">
            <div class="card-header">
              <h3>STARTING XI</h3>
              <p>预计首发</p>
            </div>
            <div class="card-body player-list">
              <div class="player-item" v-for="player in team1Data.players.filter((p: any) => p.is_starter)" :key="player.name">
                <div class="p-pos" :class="getPosClass(player.position)">{{ player.position }}</div>
                <div class="p-info">
                  <div class="p-name">{{ player.name }}</div>
                  <div class="p-meta">{{ player.age }}岁 | {{ player.height || '-' }}cm | {{ player.weight || '-' }}kg | {{ player.preferred_foot || '-' }}</div>
                </div>
                <div class="p-rating" :class="getRatingClass(player.overall_rating)">{{ player.overall_rating || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- 无数据缺省态 -->
          <div class="data-card" v-if="!team1Data">
            <div class="card-header">
              <h3>TEAM INFO</h3>
              <p>球队档案</p>
            </div>
            <div class="card-body empty-data">
              暂无球队数据，待录入...
            </div>
          </div>
        </div>

        <!-- 左侧主队名 -->
        <div class="team-panel left-team">
          <h1 class="team-name">{{ focusMatch.team1 }}</h1>
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
        
        <!-- 右侧客队名 -->
        <div class="team-panel right-team">
          <h1 class="team-name">{{ focusMatch.team2 }}</h1>
        </div>

        <!-- 右侧面板：客队数据展示 -->
        <div class="side-data-panel right-data">
          <!-- 球队档案 -->
          <div class="data-card" v-if="team2Data">
            <div class="card-header">
              <h3>TEAM INFO</h3>
              <p>球队档案</p>
            </div>
            <div class="card-body team-info">
              <div class="info-row"><span>FIFA排名:</span> <span class="highlight">{{ team2Data.fifa_ranking }}</span></div>
              <div class="info-row"><span>总身价:</span> <span class="highlight">{{ team2Data.total_value }}</span></div>
              <div class="info-row"><span>主教练:</span> <span>{{ team2Data.coach }}</span></div>
              <div class="info-row"><span>阵型偏好:</span> <span>{{ team2Data.formation }}</span></div>
              <div class="info-row"><span>平均年龄:</span> <span>{{ team2Data.avg_age }} 岁</span></div>
              <div class="info-row"><span>主场馆:</span> <span class="truncate-text" :title="team2Data.stadium">{{ team2Data.stadium }}</span></div>
            </div>
          </div>

          <!-- 核心球员 -->
          <div class="data-card key-player" v-if="team2Data && getTopPlayer(team2Data)">
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
          <div class="data-card starting-xi" v-if="team2Data && team2Data.players">
            <div class="card-header">
              <h3>STARTING XI</h3>
              <p>预计首发</p>
            </div>
            <div class="card-body player-list">
              <div class="player-item" v-for="player in team2Data.players.filter((p: any) => p.is_starter)" :key="player.name">
                <div class="p-pos" :class="getPosClass(player.position)">{{ player.position }}</div>
                <div class="p-info">
                  <div class="p-name">{{ player.name }}</div>
                  <div class="p-meta">{{ player.age }}岁 | {{ player.height || '-' }}cm | {{ player.weight || '-' }}kg | {{ player.preferred_foot || '-' }}</div>
                </div>
                <div class="p-rating" :class="getRatingClass(player.overall_rating)">{{ player.overall_rating || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- 无数据缺省态 -->
          <div class="data-card" v-if="!team2Data">
            <div class="card-header">
              <h3>TEAM INFO</h3>
              <p>球队档案</p>
            </div>
            <div class="card-body empty-data">
              暂无球队数据，待录入...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部赛程滑动区 -->
    <div class="schedule-section">
      <div class="section-title">
        <span class="bracket">[</span> UPCOMING SCHEDULE <span class="bracket">]</span>
      </div>
      <div class="match-grid">
        <div
          class="grid-card"
          v-for="(match, index) in upcomingMatches"
          :key="index"
          @click="goToDetail(match)"
        >
          <div class="card-glow"></div>
          <div class="card-header">
            <span class="card-group">{{ match.group }}</span>
            <span class="card-time">{{ match.time }}</span>
          </div>
          <div class="card-teams">
            <span class="t-name">{{ match.team1 }}</span>
            <span class="t-vs">vs</span>
            <span class="t-name">{{ match.team2 }}</span>
          </div>
          <div class="card-footer">
            {{ match.date }}<br/>{{ match.stadium }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Location } from '@element-plus/icons-vue'

const router = useRouter()
const scheduleData = ref<any[]>([])
const team1Data = ref<any>(null)
const team2Data = ref<any>(null)

const countdownDays = computed(() => {
  const today = new Date()
  const kickoff = new Date('2026-06-11T00:00:00') // 2026美加墨世界杯揭幕战时间
  const diff = kickoff.getTime() - today.getTime()
  return diff > 0 ? Math.ceil(diff / (1000 * 3600 * 24)) : 0
})

const focusMatch = computed(() => {
  return scheduleData.value.length > 0 ? scheduleData.value[0] : null
})

const upcomingMatches = computed(() => {
  return scheduleData.value.length > 1 ? scheduleData.value.slice(1) : []
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
})

const fetchSchedule = async () => {
  try {
    const res = await axios.get('http://localhost:10086/api/schedule')
    scheduleData.value = res.data
  } catch (error) {
    ElMessage.error('无法加载赛程数据，请检查后端服务')
  }
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

const goToDetail = (match: any) => {
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
    linear-gradient(rgba(64, 158, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 158, 255, 0.05) 1px, transparent 1px);
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
}

/* ================= 科技感背景装饰 ================= */
.tech-grid {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: 
    linear-gradient(rgba(64, 158, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 158, 255, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: 1;
  pointer-events: none;
  opacity: 0.5;
}

.tech-lines {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1;
  pointer-events: none;
}

.line {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(103, 194, 58, 0.8), transparent);
  height: 1px;
  width: 100%;
  opacity: 0.3;
}

.line-1 { top: 20%; animation: scan 8s linear infinite; }
.line-2 { top: 60%; animation: scan 12s linear infinite reverse; background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.8), transparent); }
.line-3 { top: 85%; animation: scan 10s linear infinite; }

@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* ======= 顶部挂件优化 ======= */
.top-widgets {
  position: absolute;
  top: 15px;
  right: 30px;
  display: flex;
  gap: 15px;
  z-index: 20;
}

.widget-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  color: #FFC107; /* 辅助色：琥珀黄 */
  text-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
}

.w-value.highlight {
  color: #39FF14; /* 次强调色：霓虹绿 */
  text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
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
  color: #00BFFF; /* 科技蓝 */
  letter-spacing: 3px;
  text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
  background: rgba(0,0,0,0.5);
  padding: 6px 15px;
  border-radius: 4px;
  border-left: 4px solid #00BFFF;
}

.live-dot {
  width: 8px;
  height: 8px;
  background-color: #39FF14; /* 霓虹绿闪烁点 */
  border-radius: 50%;
  box-shadow: 0 0 10px #39FF14;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.5); opacity: 1; box-shadow: 0 0 20px #39FF14; }
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
  top: 70px;
  width: 420px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 10;
  max-height: calc(100vh - 180px);
}
.left-data { left: 20px; }
.right-data { right: 20px; }

.data-card {
  background: rgba(13, 17, 23, 0.6);
  border: 1px solid rgba(0, 191, 255, 0.3); /* 科技蓝边框 */
  border-radius: 8px;
  padding: 12px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
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
  color: #00BFFF; /* 科技蓝 */
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
  border-bottom: 1px dashed rgba(255,255,255,0.05);
  padding-bottom: 4px;
}
.team-info .info-row span:first-child {
  color: #A0A0A0;
}
.team-info .info-row .highlight {
  color: #39FF14; /* 霓虹绿 */
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
}
.kp-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  font-size: 0.75rem;
  color: #A0A0A0;
}
.kp-stats span {
  background: rgba(255,255,255,0.05);
  padding: 4px;
  border-radius: 4px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.1);
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
  background: rgba(0, 191, 255, 0.5); /* 科技蓝滚动条 */
  border-radius: 4px;
}
.player-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
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
.pos-gk { color: #FFC107; border: 1px solid #FFC107; background: rgba(255, 193, 7, 0.1); } /* 琥珀黄 */
.pos-df { color: #00BFFF; border: 1px solid #00BFFF; background: rgba(0, 191, 255, 0.1); } /* 科技蓝 */
.pos-mf { color: #39FF14; border: 1px solid #39FF14; background: rgba(57, 255, 20, 0.1); } /* 霓虹绿 */
.pos-fw { color: #F56C6C; border: 1px solid #F56C6C; background: rgba(245, 108, 108, 0.1); }

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
.rating-gold { color: #39FF14; text-shadow: 0 0 8px rgba(57, 255, 20, 0.6); } /* 金卡改为霓虹绿发光 */
.rating-silver { color: #00BFFF; text-shadow: 0 0 8px rgba(0, 191, 255, 0.6); } /* 银卡改为科技蓝 */
.rating-bronze { color: #FFC107; text-shadow: 0 0 8px rgba(255, 193, 7, 0.6); } /* 铜卡改为琥珀黄 */
.rating-gray { color: #A0A0A0; }

/* ======= 球队面板科技感排版 ======= */
.team-panel {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  position: relative;
  margin-top: -100px;
}

.left-team { align-items: flex-end; text-align: right; padding-right: 40px; }
.right-team { align-items: flex-start; text-align: left; padding-left: 40px; }

/* 废弃旧的 team-tag */
.team-tag { display: none; }

.team-name {
  font-size: 3.5rem;
  font-weight: 900;
  margin: 0;
  letter-spacing: 2px;
  color: #ffffff; /* 纯白文字 */
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.4), 0 0 30px rgba(255, 255, 255, 0.2); /* 柔和的高级发光 */
  -webkit-text-stroke: 0; /* 移除描边 */
  position: relative;
  z-index: 2;
  white-space: nowrap;
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
  color: #fff;
  letter-spacing: 2px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 5px 15px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-shadow: none;
  opacity: 1;
  white-space: nowrap;
  margin-top: -30px;
}
.home-tag { 
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.2), transparent);
  border-left: 3px solid #409EFF;
  border-right: none;
  padding-left: 20px;
}
.away-tag { 
  background: linear-gradient(-90deg, rgba(245, 108, 108, 0.2), transparent);
  border-right: 3px solid #F56C6C;
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
  color: #39FF14; /* 霓虹绿 VS */
  text-shadow: 0 0 15px rgba(57, 255, 20, 0.6);
  font-style: italic;
  margin-bottom: -5px;
}

.match-info-pill {
  display: flex;
  gap: 12px;
  background: rgba(13, 17, 23, 0.8);
  border: 1px solid #00BFFF; /* 科技蓝 */
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  box-shadow: 0 0 15px rgba(0, 191, 255, 0.2);
}

.group { color: #00BFFF; font-weight: bold; }

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

/* 赛博朋克按钮 */
.cyber-btn {
  pointer-events: auto;
  margin-top: 5px;
  background: transparent !important;
  border: 1px solid #00BFFF !important; /* 科技蓝按钮 */
  color: #00BFFF !important;
  border-radius: 0;
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
  background: linear-gradient(90deg, transparent, rgba(0, 191, 255, 0.4), transparent);
  transition: all 0.5s;
}
.cyber-btn:hover {
  background: rgba(0, 191, 255, 0.1) !important;
  box-shadow: 0 0 20px rgba(0, 191, 255, 0.4);
}
.cyber-btn:hover::before {
  left: 100%;
}

/* ================= 底部赛程滑动区 ================= */
.schedule-section {
  flex: 0 0 auto; 
  padding: 5px 30px 10px;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 50%, transparent 100%);
  z-index: 10;
  pointer-events: auto; 
}

.section-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: #8b949e;
  margin-bottom: 10px;
  letter-spacing: 2px;
}
.bracket { color: #409EFF; }

.match-grid {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding-bottom: 5px;
  scrollbar-width: thin;
  scrollbar-color: #409EFF transparent;
}
.match-grid::-webkit-scrollbar {
  height: 4px;
}
.match-grid::-webkit-scrollbar-thumb {
  background: #409EFF;
  border-radius: 4px;
}

.grid-card {
  flex: 0 0 200px;
  height: 90px;
  background: rgba(13, 17, 23, 0.6);
  border: 1px solid #30363d;
  border-left: 3px solid transparent;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.grid-card:hover {
  transform: translateY(-5px);
  border-left-color: #409EFF;
  background: rgba(30, 40, 55, 0.8);
  box-shadow: 0 10px 20px rgba(0,0,0,0.5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #8b949e;
}

.card-group { color: #409EFF; font-weight: bold; }

.card-teams {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  font-size: 1rem;
  font-weight: bold;
}

.t-vs { font-size: 0.75rem; color: #e6a23c; font-style: italic; }

.card-footer {
  font-size: 0.65rem;
  color: #6e7681;
  text-align: center;
}
</style>
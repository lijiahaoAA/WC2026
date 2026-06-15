<template>
  <div class="settings-page">
    <h1 class="page-title">模型配置管理</h1>
    <p class="page-desc">配置 LLM 模型的 API 连接信息，支持 OpenAI 兼容接口和 Anthropic 接口。配置保存在 <code>backend/.env</code> 文件中。</p>

    <!-- 模型列表 -->
    <div class="model-list">
      <div v-for="m in models" :key="m.id" class="model-card glass-panel">
        <div class="card-top">
          <div class="card-info">
            <span class="card-name">{{ m.name || '未命名' }}</span>
            <el-tag size="small" :type="m.provider === 'anthropic' ? 'warning' : 'info'">{{ m.provider }}</el-tag>
            <el-tag v-if="m.api_key_set" size="small" type="success">Key 已配置</el-tag>
            <el-tag v-else size="small" type="danger">Key 未配置</el-tag>
          </div>
          <div class="card-actions">
            <el-button size="small" type="primary" plain @click="testModel(m)" :loading="testingId === m.id">
              测试连通
            </el-button>
            <el-button size="small" plain @click="editModel(m)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="deleteModel(m)">删除</el-button>
          </div>
        </div>
        <div class="card-detail">
          <span>Base URL: <code>{{ m.base_url }}</code></span>
          <span>Model: <code>{{ m.model }}</code></span>
          <span>API Key: <code>{{ m.api_key_masked || '未设置' }}</code></span>
        </div>
        <!-- 测试结果 -->
        <div v-if="testResults[m.id] !== undefined" class="test-result" :class="testResults[m.id].success ? 'success' : 'fail'">
          {{ testResults[m.id].message }}
        </div>
      </div>

      <div v-if="models.length === 0" class="empty-state">
        暂无模型配置，点击下方按钮添加
      </div>
    </div>

    <!-- 添加按钮 -->
    <el-button type="primary" class="add-btn" @click="addModel">
      + 添加模型
    </el-button>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模型' : '添加模型'" width="560px" class="model-dialog">
      <el-form :model="form" label-width="100px">
        <el-form-item label="显示名称">
          <el-input v-model="form.name" placeholder="如：GLM-4、GPT-4o、Claude-Sonnet" />
        </el-form-item>
        <el-form-item label="接口协议">
          <el-radio-group v-model="form.provider">
            <el-radio value="openai">OpenAI 兼容</el-radio>
            <el-radio value="anthropic">Anthropic</el-radio>
          </el-radio-group>
          <div class="form-hint">GLM / 小米 / MiniMax 等均选 "OpenAI 兼容"</div>
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="Model">
          <el-input v-model="form.model" placeholder="如 gpt-4o、glm-4、claude-sonnet-4-20250514" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="form.api_key" type="password" show-password placeholder="sk-..." />
          <div class="form-hint">留空则不更新已有的 Key</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 数据同步配置 -->
    <div class="section-divider"></div>
    <h2 class="section-title">比赛数据同步</h2>
    <p class="page-desc">系统会依次尝试多个数据源获取比赛数据，直到成功为止。TheSportsDB 免费无需 Key，其他源可选填。</p>

    <div class="sync-card glass-panel">
      <!-- 数据源状态 -->
      <div class="sync-row">
        <span class="sync-label">数据源状态</span>
        <div class="source-tags">
          <el-tag :type="syncStatus?.sources?.thesportsdb ? 'success' : 'info'" size="small">TheSportsDB (免费)</el-tag>
          <el-tag :type="syncStatus?.sources?.football_data ? 'success' : 'warning'" size="small">football-data.org</el-tag>
          <el-tag :type="syncStatus?.sources?.api_football ? 'success' : 'warning'" size="small">API-Football</el-tag>
        </div>
      </div>

      <!-- API Keys -->
      <div class="sync-row">
        <span class="sync-label">football-data Key</span>
        <el-input v-model="footballDataKey" type="password" show-password placeholder="从 football-data.org 获取（可选）" class="key-input" />
        <el-button type="primary" size="small" @click="saveFootballDataKey" :loading="savingKey">保存</el-button>
      </div>
      <div class="sync-row">
        <span class="sync-label">API-Football Key</span>
        <el-input v-model="footballApiKey" type="password" show-password placeholder="从 api-sports.io 获取（可选）" class="key-input" />
        <el-button type="primary" size="small" @click="saveApiKey" :loading="savingKey">保存</el-button>
      </div>

      <!-- 同步状态 -->
      <div class="sync-row">
        <span class="sync-label">同步状态</span>
        <span class="sync-value" v-if="syncStatus">
          已同步 {{ syncStatus.matches_synced }} 场比赛 |
          {{ syncStatus.player_stats_count }} 条球员数据 |
          {{ syncStatus.active_injuries }} 个伤病 |
          最后更新: {{ syncStatus.last_sync || '从未同步' }}
        </span>
        <span class="sync-value" v-else>加载中...</span>
      </div>

      <div class="sync-actions">
        <el-button type="primary" @click="triggerSync" :loading="syncing" class="sync-btn">
          {{ syncing ? '同步中...' : '立即同步' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const API_BASE = 'http://localhost:10086'

interface ModelConfig {
  id: string
  name: string
  provider: string
  api_key_masked: string
  api_key_set: boolean
  base_url: string
  model: string
}

const models = ref<ModelConfig[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const testingId = ref<string | null>(null)
const testResults = reactive<Record<string, { success: boolean; message: string }>>({})

const form = reactive({
  id: 'new',
  name: '',
  provider: 'openai',
  api_key: '',
  base_url: '',
  model: '',
})

async function fetchModels() {
  try {
    const res = await axios.get(`${API_BASE}/api/config/models`)
    models.value = res.data.models || []
  } catch (e) {
    ElMessage.error('获取模型配置失败')
  }
}

function addModel() {
  isEdit.value = false
  form.id = 'new'
  form.name = ''
  form.provider = 'openai'
  form.api_key = ''
  form.base_url = ''
  form.model = ''
  dialogVisible.value = true
}

function editModel(m: ModelConfig) {
  isEdit.value = true
  form.id = m.id
  form.name = m.name
  form.provider = m.provider
  form.api_key = ''  // 不回填，留空表示不更新
  form.base_url = m.base_url
  form.model = m.model
  dialogVisible.value = true
}

async function submitForm() {
  if (!form.name.trim()) {
    ElMessage.warning('请填写显示名称')
    return
  }
  if (!form.base_url.trim()) {
    ElMessage.warning('请填写 Base URL')
    return
  }
  if (!form.model.trim()) {
    ElMessage.warning('请填写模型名称')
    return
  }

  saving.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/config/models`, {
      model_id: form.id,
      name: form.name,
      provider: form.provider,
      api_key: form.api_key,
      base_url: form.base_url,
      model: form.model,
    })
    if (res.data.status === 'success') {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      await fetchModels()
    } else {
      ElMessage.error('保存失败: ' + res.data.message)
    }
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.message || '网络错误'))
  } finally {
    saving.value = false
  }
}

async function deleteModel(m: ModelConfig) {
  try {
    await ElMessageBox.confirm(`确定删除模型 "${m.name}" 吗？`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await axios.post(`${API_BASE}/api/config/models/delete`, { model_id: m.id })
    if (res.data.status === 'success') {
      ElMessage.success('已删除')
      delete testResults[m.id]
      await fetchModels()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (e) {
    // 用户取消
  }
}

async function testModel(m: ModelConfig) {
  testingId.value = m.id
  delete testResults[m.id]
  try {
    const res = await axios.post(`${API_BASE}/api/config/models/test`, { model_id: m.id })
    testResults[m.id] = {
      success: res.data.status === 'success',
      message: res.data.message,
    }
  } catch (e: any) {
    testResults[m.id] = {
      success: false,
      message: '请求失败: ' + (e.message || '网络错误'),
    }
  } finally {
    testingId.value = null
  }
}

// 数据同步相关
const footballApiKey = ref('')
const footballDataKey = ref('')
const syncStatus = ref<any>(null)
const syncing = ref(false)
const savingKey = ref(false)

async function fetchSyncStatus() {
  try {
    const res = await axios.get(`${API_BASE}/api/data/status`)
    if (res.data.status === 'success') {
      syncStatus.value = res.data.data
    }
  } catch (e) {
    // ignore
  }
}

async function saveApiKey() {
  savingKey.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/data/api_key`, { key: footballApiKey.value })
    if (res.data.status === 'success') {
      ElMessage.success('API-Football Key 已保存')
      await fetchSyncStatus()
    } else {
      ElMessage.error('保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingKey.value = false
  }
}

async function saveFootballDataKey() {
  savingKey.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/data/football_data_key`, { key: footballDataKey.value })
    if (res.data.status === 'success') {
      ElMessage.success('football-data Key 已保存')
      await fetchSyncStatus()
    } else {
      ElMessage.error('保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingKey.value = false
  }
}

async function triggerSync() {
  syncing.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/data/sync`)
    if (res.data.status === 'success') {
      const d = res.data.data
      ElMessage.success(`同步完成：${d.fixtures} 场比赛`)
      await fetchSyncStatus()
    } else {
      ElMessage.error('同步失败: ' + res.data.message)
    }
  } catch (e: any) {
    ElMessage.error('同步失败: ' + (e.message || '网络错误'))
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchModels()
  fetchSyncStatus()
})
</script>

<style scoped>
.settings-page {
  padding: 30px 40px;
  color: #c9d1d9;
  max-width: 1100px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px 0;
}

.page-desc {
  color: #A0A0A0;
  font-size: 0.9rem;
  margin-bottom: 25px;
}

.page-desc code {
  background: rgba(210, 167, 109, 0.15);
  color: #D2A76D;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.85rem;
}

/* 模型卡片 */
.model-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.model-card {
  background: rgba(18, 18, 18, 0.75);
  backdrop-filter: blur(12px);
  border-radius: 10px;
  padding: 18px 22px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-detail {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 0.8rem;
  color: #A0A0A0;
}

.card-detail code {
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 6px;
  border-radius: 3px;
  color: #c9d1d9;
  font-size: 0.78rem;
}

.test-result {
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
}

.test-result.success {
  background: rgba(103, 194, 58, 0.1);
  border: 1px solid rgba(103, 194, 58, 0.3);
  color: #67c23a;
}

.test-result.fail {
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.3);
  color: #f56c6c;
}

.empty-state {
  text-align: center;
  color: #6e7681;
  padding: 40px;
  font-style: italic;
}

.add-btn {
  pointer-events: auto;
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important;
  color: #D2A76D !important;
  font-weight: bold;
  letter-spacing: 2px;
  transition: all 0.3s;
}
.add-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 20px rgba(210, 167, 109, 0.4);
}

.form-hint {
  font-size: 0.75rem;
  color: #6e7681;
  margin-top: 4px;
}

/* Element Plus 暗色覆盖 */
:deep(.el-dialog) {
  background: #161b22 !important;
  border: 1px solid #30363d !important;
}
:deep(.el-dialog__header) {
  border-bottom: 1px solid #30363d;
}
:deep(.el-dialog__title) {
  color: #D2A76D !important;
}
:deep(.el-form-item__label) {
  color: #A0A0A0 !important;
}
:deep(.el-input__wrapper) {
  background: #0d1117 !important;
  box-shadow: 0 0 0 1px #30363d inset !important;
}
:deep(.el-input__inner) {
  color: #c9d1d9 !important;
}
:deep(.el-radio__label) {
  color: #c9d1d9 !important;
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
:deep(.el-tag--success) {
  --el-tag-bg-color: rgba(103, 194, 58, 0.15);
  --el-tag-text-color: #67c23a;
  --el-tag-border-color: rgba(103, 194, 58, 0.3);
}
:deep(.el-tag--danger) {
  --el-tag-bg-color: rgba(245, 108, 108, 0.15);
  --el-tag-text-color: #f56c6c;
  --el-tag-border-color: rgba(245, 108, 108, 0.3);
}

/* 数据同步区 */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(210, 167, 109, 0.3), transparent);
  margin: 40px 0 20px;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px 0;
}

.sync-card {
  background: rgba(18, 18, 18, 0.75);
  backdrop-filter: blur(12px);
  border-radius: 10px;
  padding: 20px 25px;
}

.sync-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
}

.sync-label {
  min-width: 140px;
  color: #A0A0A0;
  font-size: 0.85rem;
}

.sync-value {
  color: #c9d1d9;
  font-size: 0.85rem;
}

.key-input {
  flex: 1;
  max-width: 400px;
}

.sync-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(210, 167, 109, 0.1);
}

.sync-btn {
  pointer-events: auto;
  background: rgba(210, 167, 109, 0.1) !important;
  border: 1px solid #D2A76D !important;
  color: #D2A76D !important;
  font-weight: bold;
  letter-spacing: 2px;
}
.sync-btn:hover {
  background: rgba(210, 167, 109, 0.2) !important;
  box-shadow: 0 0 20px rgba(210, 167, 109, 0.4);
}

.source-tags {
  display: flex;
  gap: 8px;
}
</style>

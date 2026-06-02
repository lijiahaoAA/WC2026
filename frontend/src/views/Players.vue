<template>
  <div class="players-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>参赛球员信息录入</span>
          <el-button type="primary" @click="dialogVisible = true">新增球员</el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="球员姓名" width="180" />
        <el-table-column prop="team_name" label="所属球队" width="120" />
        <el-table-column prop="position" label="场上位置" width="120" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="jersey_number" label="号码" width="80" />
        <el-table-column prop="is_key_player" label="核心球员" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_key_player ? 'success' : 'info'">
              {{ scope.row.is_key_player ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑球员' : '新增球员'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="球员姓名" prop="name">
          <el-input v-model="form.name" placeholder="例如：梅西" />
        </el-form-item>
        <el-form-item label="所属球队" prop="team_id">
          <!-- 这里应该从后端拉取球队列表，暂时用假数据 -->
          <el-select v-model="form.team_id" placeholder="请选择球队">
            <el-option label="阿根廷" :value="1" />
            <el-option label="法国" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="场上位置" prop="position">
          <el-select v-model="form.position" placeholder="请选择位置">
            <el-option label="前锋" value="前锋" />
            <el-option label="中场" value="中场" />
            <el-option label="后卫" value="后卫" />
            <el-option label="门将" value="门将" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="15" :max="50" />
        </el-form-item>
        <el-form-item label="球衣号码" prop="jersey_number">
          <el-input-number v-model="form.jersey_number" :min="1" :max="99" />
        </el-form-item>
        <el-form-item label="核心球员" prop="is_key_player">
          <el-switch v-model="form.is_key_player" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const tableData = ref([])

const fetchPlayers = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:10086/api/players')
    tableData.value = res.data
  } catch (error) {
    ElMessage.error('获取球员数据失败，请检查后端或数据库连接')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPlayers()
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  id: null as number | null,
  name: '',
  team_id: null as number | null,
  position: '',
  age: 25,
  jersey_number: 10,
  is_key_player: false
})

const rules = {
  name: [{ required: true, message: '请输入球员姓名', trigger: 'blur' }],
  team_id: [{ required: true, message: '请选择所属球队', trigger: 'change' }],
  position: [{ required: true, message: '请选择场上位置', trigger: 'change' }]
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = (row: any) => {
  ElMessage.warning('此处将调用后端删除API，暂未实现')
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(isEdit.value ? '修改成功(模拟)' : '新增成功(模拟)')
      dialogVisible.value = false
      // 待后端开发完成后调用 axios 发送数据
    }
  })
}
</script>

<style scoped>
.players-container {
  padding: 30px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<template>
  <div class="teams-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>参赛球队信息录入</span>
          <el-button type="primary" @click="dialogVisible = true">新增球队</el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="球队名称" width="180" />
        <el-table-column prop="country_code" label="国家代码" width="120" />
        <el-table-column prop="group_name" label="所在小组" width="120" />
        <el-table-column prop="fifa_ranking" label="FIFA排名" width="120" />
        <el-table-column prop="coach" label="主教练" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑球队' : '新增球队'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="球队名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：阿根廷" />
        </el-form-item>
        <el-form-item label="国家代码" prop="country_code">
          <el-input v-model="form.country_code" placeholder="例如：ARG" />
        </el-form-item>
        <el-form-item label="所在小组" prop="group_name">
          <el-select v-model="form.group_name" placeholder="请选择">
            <el-option v-for="g in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']" :key="g" :label="g + '组'" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="FIFA排名" prop="fifa_ranking">
          <el-input-number v-model="form.fifa_ranking" :min="1" />
        </el-form-item>
        <el-form-item label="主教练" prop="coach">
          <el-input v-model="form.coach" />
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

const fetchTeams = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:10086/api/teams')
    tableData.value = res.data
  } catch (error) {
    ElMessage.error('获取球队数据失败，请检查后端或数据库连接')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTeams()
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  id: null as number | null,
  name: '',
  country_code: '',
  group_name: '',
  fifa_ranking: 1,
  coach: ''
})

const rules = {
  name: [{ required: true, message: '请输入球队名称', trigger: 'blur' }],
  country_code: [{ required: true, message: '请输入国家代码', trigger: 'blur' }]
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
.teams-container {
  padding: 30px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<div align="center">
  <img src="frontend/public/favicon.png" width="120" alt="Logo">
  <h1>🏆 2026美加墨世界杯 智能投注辅助决策引擎</h1>
  <p><i>基于多模型协同与海量足球数据的赛事分析系统</i></p>
</div>

---

## 🖥️ 系统展示

<img width="2559" height="1271" alt="系统大屏展示" src="https://github.com/user-attachments/assets/5204f44d-b2f2-4526-8334-66191593a268" />
*现代科技风格的数据大屏：包含沉浸式 3D 体育场模型、实时赛程、球队与球员数据面板。*

---

## 📖 项目简介

2026美加墨世界杯 智能投注辅助决策引擎是一款专为 2026 年美加墨世界杯打造的数据分析系统。项目通过聚合球队基本面数据与多个大语言模型的协同预测能力，为赛事分析提供客观、多维度的参考依据。

系统支持同时接入任意数量的 LLM（兼容 OpenAI / Anthropic 双协议），对每场比赛的**比分、总进球数、红牌预警、点球概率**等维度进行多模型并行预测，结果分列对比、互为校验，并通过投票聚合给出综合结论。

---

## 🚀 核心特性

*   **多模型协同预测**：可同时配置多个大模型（智谱 GLM、小米 MiMo、MiniMax、OpenAI、Anthropic Claude、DeepSeek 等），对同一比赛并行输出预测，前端以分列卡片直观对比各模型结论。
*   **投票聚合结论**：对多模型结果做规则投票，输出综合的最终比分、进球、红牌、点球结论与投注建议。
*   **高并发架构**：后端基于线程池并发拆分，多模型 × 多预测维度异步执行，显著降低分析等待时间。
*   **统一 LLM 抽象**：`llm_client.py` 统一封装 OpenAI 兼容接口与 Anthropic 接口，自动处理思考模型（ThinkingBlock）的混合输出。
*   **详尽数据底座**：内置本届世界杯 48 支参赛球队资料，包含球队身价、平均年龄、教练团队，以及球员六维能力雷达图、伤病史和转会记录。
*   **现代科技 UI**：前端采用 Vue 3 构建，运用玻璃拟态 (Glassmorphism)、暗金环境光晕与 3D 渲染技术，提供沉浸式视觉体验。

---

## 🛠️ 技术栈

*   **前端**：Vue 3, Vite, Element Plus, Three.js, ECharts, GSAP
*   **后端**：Python 3.10, FastAPI, Uvicorn, ThreadPoolExecutor
*   **数据库**：PostgreSQL 14（大量运用 JSONB 处理复杂嵌套数据）
*   **大模型**：多模型可配置，兼容 OpenAI 协议（GLM / 小米 / MiniMax / OpenAI 等）与 Anthropic 协议（Claude / MiMo / DeepSeek 等）

---

## 🏃 部署指南

### 环境要求
*   Python 3.10（推荐使用 conda 独立环境）
*   Node.js 18+
*   PostgreSQL 14+

### 1. 数据库准备
项目使用 PostgreSQL 默认的 `postgres` 库。安装并启动 PostgreSQL 后，先在 `backend/.env` 中配置连接密码：

```
DB_PASSWORD=您的数据库密码
```

随后一键初始化表结构，并导入 48 支球队、赛程与球员数据：

```bash
cd backend
python init_db.py
```

### 2. 后端配置与启动
```bash
cd backend

# （推荐）使用 conda 独立环境，避免与系统 Python 冲突
conda create -n py310 python=3.10 -y
conda activate py310

# 安装依赖
pip install fastapi uvicorn psycopg2-binary pydantic openai anthropic python-dotenv requests

# 启动服务（默认端口 10086）
python main.py
```

#### `.env` 模型配置说明
除数据库密码外，所有 LLM 均以 `MODEL_N_` 前缀配置，支持任意数量模型。`provider` 取 `openai`（兼容 GLM / 小米 / MiniMax 等）或 `anthropic`；**API_KEY 留空的模型会被自动跳过**，不会出现在前端选择列表：

```
DB_PASSWORD=您的数据库密码

# --- 模型 1 ---
MODEL_1_NAME=GLM-5.2
MODEL_1_PROVIDER=anthropic
MODEL_1_API_KEY=您的Key
MODEL_1_BASE_URL=https://open.bigmodel.cn/api/anthropic
MODEL_1_MODEL=glm-5.2

# --- 模型 2 ---
MODEL_2_NAME=小米MiMo
MODEL_2_PROVIDER=anthropic
MODEL_2_API_KEY=您的Key
MODEL_2_BASE_URL=https://token-plan-cn.xiaomimimo.com/anthropic
MODEL_2_MODEL=mimo-v2.5-pro
```

> 💡 模型也可在前端「模型配置」页可视化管理（增删改、连通性测试），改动即时写回 `.env`。

### 3. 前端启动
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 10087）
npm run dev
```

启动后浏览器访问 **http://localhost:10087** 即可使用，后端 API 文档位于 http://localhost:10086/docs。

---

## ⚠️ 声明

本系统提供的所有赛事分析及预测结果，仅基于现有数据和算法模型生成。足球比赛具有不可预见性，分析结果仅供参考，不构成任何形式的投资或投注建议。

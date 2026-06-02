<div align="center">
  <img src="frontend/public/favicon.png" width="120" alt="Logo">
  <h1>🏆 WC2026 智能辅助决策引擎</h1>
  <p><i>基于大模型与海量足球数据的赛事分析系统</i></p>
</div>

---

## 🖥️ 系统展示

![WC2026 智能大屏截图](screenshot.png)
*现代科技风格的数据大屏：包含沉浸式 3D 体育场模型、实时赛程、球队与球员数据面板。*

---

## 📖 项目简介

WC2026 智能辅助决策引擎是一款专为 2026 年美加墨世界杯打造的数据分析系统。项目旨在通过聚合球队基本面数据与大模型预测能力，为赛事分析提供客观、多维度的参考依据。

## 🚀 核心特性

*   **智能 AI 分析**: 接入阿里云 DashScope Qwen-3.7-Max 大语言模型，基于客观数据输出包括胜率、比分、总进球数等维度的结构化分析。
*   **高并发架构**: 后端 AI 接口采用并发拆分设计，实现多个预测指标（比分、进球、红牌等）的异步渲染，显著降低分析等待时间。
*   **详尽数据底座**: 数据库内置本届世界杯 48 支参赛球队的详细资料，包含球队身价、平均年龄、教练团队，以及球员的六维能力雷达图、伤病史和转会记录。
*   **现代科技 UI**: 前端采用 Vue 3 构建，设计风格为“现代科技奢华风”，运用玻璃拟态 (Glassmorphism)、暗金环境光晕和 3D 渲染技术，提供极佳的视觉体验。

---

## 🛠️ 技术栈

*   **前端**: Vue 3, Vite, Element Plus, Three.js, ECharts
*   **后端**: Python, FastAPI
*   **数据库**: PostgreSQL (大量运用 JSONB 处理复杂嵌套数据)
*   **大模型**: 阿里云 DashScope (Qwen)

---

## 🏃 部署指南

### 环境要求
*   Python 3.10+
*   Node.js 18+
*   PostgreSQL 14+

### 1. 后端配置与启动
```bash
cd backend

# 配置环境变量
# 请在 backend 目录下创建 .env 文件，并填入以下内容：
# DB_PASSWORD=您的数据库密码
# ALIYUN_API_KEY=您的阿里云DashScope Key

# 安装依赖
pip install fastapi uvicorn psycopg2-binary pydantic openai python-dotenv

# 启动服务 (默认端口 10086)
python main.py
```

### 2. 前端配置与启动
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## ⚠️ 声明

本系统提供的所有赛事分析及预测结果，仅基于现有数据和算法模型生成。足球比赛具有不可预见性，分析结果仅供参考，不构成任何形式的投资或投注建议。

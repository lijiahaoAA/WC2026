<template>
  <div class="app-wrapper">
    <!-- 全局 3D 背景组件 -->
    <StadiumBackground />
    
    <el-container class="layout-container">
      <el-header class="app-header">
        <div class="logo">
          <img src="/favicon.png" alt="Logo" class="logo-img" />
          <span class="title" >2026美加墨世界杯 智能投注辅助决策引擎</span>
        </div>
        <el-menu mode="horizontal" :router="true" :default-active="$route.path" class="nav-menu" background-color="transparent" text-color="#A0A0A0" active-text-color="#D2A76D">
          <el-menu-item index="/">赛事大屏</el-menu-item>
          <el-menu-item index="/teams">球队库</el-menu-item>
          <el-menu-item index="/players">球员库</el-menu-item>
          <el-menu-item index="/settings">模型配置</el-menu-item>
        </el-menu>
      </el-header>
      
      <el-main class="main-content" :class="{ 'is-dashboard': $route.path === '/' }">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import StadiumBackground from './components/StadiumBackground.vue'
</script>

<style>
/* 终极清零策略，抹除所有浏览器默认样式和 ElementPlus 的潜在干扰 */
*, *::before, *::after {
  box-sizing: border-box;
}

body, html {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background-color: #0d1117;
  color: #c9d1d9;
  overflow: hidden !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
}

#app {
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 100vw !important;
}

.app-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at 50% 30%, #141416 0%, #08080A 100%); /* Deep charcoal to warm black */
}
.layout-container {
  height: 100vh;
  width: 100vw;
  background: transparent; /* 必须透明才能露出底层的3D模型 */
  color: #fff;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  pointer-events: none; /* 让鼠标穿透布局容器以操作底层 3D 模型 */
}

/* 恢复导航栏和主内容区内部 UI 元素的交互 */
.app-header, .main-content > * {
  pointer-events: auto;
}

.el-main {
  padding: 0 !important; /* 强制干掉 el-main 的默认 padding */
  overflow: hidden !important;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(18, 18, 18, 0.85); /* 更接近黑曜石 */
  backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(210, 167, 109, 0.15); /* 香槟金弱边框 */
  padding: 0 40px;
  height: 60px;
  position: relative;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #D2A76D 0%, #A67C41 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-img {
  height: 32px;
  width: auto;
}

.title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 2px;
}

.nav-menu {
  border-bottom: none !important;
  font-size: 16px;
}

.el-menu-item {
  font-size: 16px !important;
  font-weight: 500;
}

.el-menu-item:hover {
  background-color: rgba(255,255,255,0.05) !important;
}

.main-content {
  padding: 30px;
  flex: 1;
  height: calc(100vh - 70px);
  overflow-y: auto;
  overflow-x: hidden;
  pointer-events: auto;
}

/* 当处于大屏页面时，取消 padding，实现真正的全屏铺满 */
.main-content.is-dashboard {
  padding: 0 !important;
  overflow: hidden; /* 大屏内部自己处理布局，不出现全局滚动条 */
}

/* 覆盖 Element Plus 暗黑模式样式 */
.el-card {
  background-color: #161b22 !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
}

.el-card__header {
  border-bottom: 1px solid #30363d !important;
}

.el-table {
  background-color: transparent !important;
  --el-table-border-color: #30363d;
  --el-table-header-bg-color: #21262d;
  --el-table-row-hover-bg-color: #21262d;
}

.el-table th.el-table__cell {
  background-color: #21262d !important;
  color: #8b949e;
}

.el-table tr {
  background-color: #161b22 !important;
  color: #c9d1d9;
}

/* ================= 全局玻璃拟态面板光照边缘优化 ================= */
.glass-panel {
  border: none !important;
  position: relative;
  /* 基础底色由各自组件决定，这里只控制光照边缘和阴影 */
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), /* 若隐若现的接地阴影，增加悬浮感 */
              inset 2px 2px 15px rgba(255, 193, 7, 0.05), /* 左上内边缘柔和琥珀色 */
              inset -2px -2px 15px rgba(255, 193, 7, 0.05) !important; /* 右下内边缘柔和琥珀色 */
}

/* 顶部边缘：柔和、弥漫的古铜金“眉毛” */
.glass-panel::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, rgba(62, 51, 36, 0) 0%, rgba(146, 122, 89, 0.4) 15%, rgba(146, 122, 89, 0.15) 30%, rgba(62, 51, 36, 0) 100%);
  filter: blur(1px);
  mix-blend-mode: screen;
  pointer-events: none;
  z-index: 2;
  border-top-left-radius: inherit;
  border-top-right-radius: inherit;
}

/* 底部边缘：稍重的弥漫光，进一步模糊 */
.glass-panel::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(62, 51, 36, 0) 10%, rgba(146, 122, 89, 0.5) 50%, rgba(62, 51, 36, 0) 90%);
  filter: blur(3px);
  mix-blend-mode: screen;
  pointer-events: none;
  z-index: 2;
  border-bottom-left-radius: inherit;
  border-bottom-right-radius: inherit;
}
</style>

<template>
  <div class="app">
    <!-- 导航区 -->
    <div class="navigate">
      <h1 class="logo">智慧交通平台</h1>
      <RouterLink replace to="/">首页</RouterLink>
      <RouterLink replace to="/traffic-map">交通地图</RouterLink>
      <RouterLink replace to="/real-time-data">实时监控</RouterLink>
      <RouterLink replace to="/statistics">统计分析</RouterLink>
    </div>
    <!-- 展示区 -->
    <div class="main-content">
      <RouterView></RouterView>
    </div>
  </div>
</template>
<script>
export default {
  name: 'App'
} 
</script>

<script setup>
  import {RouterView,RouterLink} from 'vue-router'
</script>
   <style>
/* 全局样式 - 应用背景到整个页面 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  width: 100vw;
  min-height: 100vh;
  background: #001a40; /* 深蓝色背景，与导航栏和地图颜色呼应 */
  background-attachment: fixed;
  color: #333;
  font-size: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
  line-height: 1.6;
  margin: 0;
  padding: 0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>

<style scoped>
.app {
  width: calc(100% - 20px); /* 留出页面边框 */
  min-height: calc(100vh - 20px); /* 留出页面边框 */
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: stretch;
  padding: 0;
  box-sizing: border-box;
  margin: 10px auto; /* 居中显示，形成页面边框 */
  border-radius: 8px; /* 圆角边框 */
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5); /* 增加阴影效果 */
}

.navigate {
  width: 220px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  background: linear-gradient(135deg, #001a40 0%, #003366 50%, #004d99 100%); /* 深蓝色渐变，与地图背景呼应 */
  border-right: 1px solid rgba(100, 210, 255, 0.2); /* 主题色边框，增加层次感 */
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.3); /* 深色阴影，与深色背景更协调 */
  transition: all 0.3s ease;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.logo {
  font-size: 1.6rem;
  margin: 0 0 30px 0;
  text-align: center;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  font-weight: bold;
  padding: 15px 0;
}

/* 导航项样式 */
.navigate a {
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  margin: 8px 0;
  padding: 16px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: rgba(100, 210, 255, 0.1); /* 主题色半透明背景，与导航栏背景呼应 */
  text-align: left;
  font-weight: 500;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(100, 210, 255, 0.2); /* 主题色边框，增加层次感 */
}

/* 导航项图标 */
.navigate a::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  width: 20px;
  height: 20px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}
.navigate a {
  padding-left: 55px;
}

.navigate a:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 选中状态样式 */
.navigate a.router-link-active {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.main-content {
  flex: 1;
  width: calc(100% - 220px);
  margin-left: 220px;
  padding: 20px;
  box-sizing: border-box;
  overflow-y: auto;
  min-height: 100vh;
  background: #f5f7fa; /* 稍微调整为更柔和的浅色，与深蓝色边框更协调 */
}

/* 首页背景图片 - 仅在首页路由时显示 */
.router-view-home {
  min-height: 100vh;
  background-image: url('@/backgroundpicture/hongludeng.jpeg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}
</style>

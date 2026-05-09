<template>
  <div class="nanxu-app">
    <!-- 侧边栏 -->
    <aside class="nanxu-sidebar">
      <div class="sidebar-header">
        <h1 class="logo-text">南序岛</h1>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </router-link>
        <router-link to="/account-management" class="nav-item" :class="{ active: $route.path === '/account-management' }">
          <el-icon><User /></el-icon>
          <span>账号管理</span>
        </router-link>
        <router-link to="/material-management" class="nav-item" :class="{ active: $route.path === '/material-management' }">
          <el-icon><Folder /></el-icon>
          <span>素材管理</span>
        </router-link>
        <router-link to="/publish-center" class="nav-item" :class="{ active: $route.path === '/publish-center' }">
          <el-icon><Upload /></el-icon>
          <span>发布中心</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="nav-item">
          <el-icon><Link /></el-icon>
          <span>网站</span>
        </div>
        <div class="nav-item">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据</span>
        </div>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="nanxu-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { HomeFilled, User, Folder, Upload, Link, DataAnalysis } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap');

// 颜色变量
$sidebar-bg: rgba(45, 30, 20, 0.85);
$sidebar-text: #FFF8DC;
$sidebar-hover: rgba(255, 191, 0, 0.2);
$sidebar-active: rgba(255, 191, 0, 0.4);
$amber-primary: #FFBF00;

.nanxu-app {
  display: flex;
  min-height: 100vh;
}

.nanxu-sidebar {
  width: 200px;
  background: $sidebar-bg;
  backdrop-filter: blur(15px);
  border-right: 2px solid rgba(139, 111, 71, 0.5);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  box-shadow: 5px 0 20px rgba(0, 0, 0, 0.3);
  
  .sidebar-header {
    padding: 30px 20px;
    border-bottom: 1px solid rgba(139, 111, 71, 0.3);
    
    .logo-text {
      font-family: 'Noto Serif SC', 'Cinzel', serif;
      font-size: 28px;
      font-weight: 700;
      color: $amber-primary;
      text-shadow: 
        0 0 10px rgba(255, 191, 0, 0.5),
        2px 2px 4px rgba(0, 0, 0, 0.5);
      margin: 0;
      text-align: center;
      letter-spacing: 3px;
    }
  }
  
  .sidebar-nav {
    flex: 1;
    padding: 20px 0;
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 24px;
    color: $sidebar-text;
    text-decoration: none;
    font-size: 15px;
    transition: all 0.3s ease;
    border-left: 3px solid transparent;
    cursor: pointer;
    
    .el-icon {
      font-size: 18px;
    }
    
    &:hover {
      background: $sidebar-hover;
      border-left-color: $amber-primary;
      
      .el-icon {
        color: $amber-primary;
      }
    }
    
    &.active {
      background: $sidebar-active;
      border-left-color: $amber-primary;
      color: $amber-primary;
      
      .el-icon {
        color: $amber-primary;
      }
    }
  }
  
  .sidebar-footer {
    padding: 20px 0;
    border-top: 1px solid rgba(139, 111, 71, 0.3);
  }
}

.nanxu-main {
  flex: 1;
  margin-left: 200px;
  min-height: 100vh;
}
</style>

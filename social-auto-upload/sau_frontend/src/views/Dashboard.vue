<template>
  <div class="cyberpunk-dashboard nanxu-theme">
    <!-- Animated Background Grid -->
    <div class="grid-background"></div>
    
    <!-- Scanline Effect -->
    <div class="scanline"></div>
    
    <!-- Page Header -->
    <div class="terminal-header">
      <div class="terminal-prompt">
        <span class="prompt-symbol">root@sau-matrix:~$</span>
        <span class="cursor-blink">█</span>
      </div>
      <h1 class="glitch-text" data-text="SOCIAL AUTO UPLOAD MATRIX">
        SOCIAL AUTO UPLOAD MATRIX
      </h1>
      <div class="system-status">
        <span class="status-indicator pulse"></span>
        <span class="status-text">SYSTEM ONLINE</span>
      </div>
    </div>
    
    <!-- Stats Dashboard - Data Cockpit Style -->
    <div class="data-cockpit">
      <el-row :gutter="20">
        <!-- Account Stats -->
        <el-col :span="6">
          <div class="cyber-card">
            <div class="card-header">
              <span class="status-tag">[ACCOUNTS]</span>
              <div class="signal-bars">
                <span></span><span></span><span></span>
              </div>
            </div>
            <div class="card-body">
              <div class="stat-value glow-green">{{ accountStats.total }}</div>
              <div class="stat-label">TOTAL NODES</div>
            </div>
            <div class="card-footer">
              <div class="mini-stat">
                <span class="label">ACTIVE:</span>
                <span class="value success">{{ accountStats.normal }}</span>
              </div>
              <div class="mini-stat">
                <span class="label">ERROR:</span>
                <span class="value danger">{{ accountStats.abnormal }}</span>
              </div>
            </div>
            <div class="card-border"></div>
          </div>
        </el-col>
        
        <!-- Platform Stats -->
        <el-col :span="6">
          <div class="cyber-card">
            <div class="card-header">
              <span class="status-tag">[PLATFORMS]</span>
              <div class="signal-bars">
                <span></span><span></span><span></span>
              </div>
            </div>
            <div class="card-body">
              <div class="stat-value glow-blue">{{ platformStats.total }}</div>
              <div class="stat-label">CONNECTED</div>
            </div>
            <div class="card-footer">
              <div class="platform-badges">
                <span class="badge" title="Kuaishou">KS:{{ platformStats.kuaishou }}</span>
                <span class="badge" title="Douyin">DY:{{ platformStats.douyin }}</span>
                <span class="badge" title="Channels">CH:{{ platformStats.channels }}</span>
                <span class="badge" title="Xiaohongshu">XHS:{{ platformStats.xiaohongshu }}</span>
              </div>
            </div>
            <div class="card-border"></div>
          </div>
        </el-col>
        
        <!-- Task Stats -->
        <el-col :span="6">
          <div class="cyber-card">
            <div class="card-header">
              <span class="status-tag">[TASKS]</span>
              <div class="signal-bars">
                <span></span><span></span><span></span>
              </div>
            </div>
            <div class="card-body">
              <div class="stat-value glow-purple">{{ taskStats.total }}</div>
              <div class="stat-label">QUEUED</div>
            </div>
            <div class="card-footer">
              <div class="mini-stat">
                <span class="label">DONE:</span>
                <span class="value success">{{ taskStats.completed }}</span>
              </div>
              <div class="mini-stat">
                <span class="label">RUNNING:</span>
                <span class="value warning">{{ taskStats.inProgress }}</span>
              </div>
              <div class="mini-stat">
                <span class="label">FAILED:</span>
                <span class="value danger">{{ taskStats.failed }}</span>
              </div>
            </div>
            <div class="card-border"></div>
          </div>
        </el-col>
        
        <!-- Content Stats -->
        <el-col :span="6">
          <div class="cyber-card">
            <div class="card-header">
              <span class="status-tag">[CONTENT]</span>
              <div class="signal-bars">
                <span></span><span></span><span></span>
              </div>
            </div>
            <div class="card-body">
              <div class="stat-value glow-cyan">{{ contentStats.total }}</div>
              <div class="stat-label">FILES</div>
            </div>
            <div class="card-footer">
              <div class="mini-stat">
                <span class="label">PUBLISHED:</span>
                <span class="value success">{{ contentStats.published }}</span>
              </div>
              <div class="mini-stat">
                <span class="label">DRAFT:</span>
                <span class="value info">{{ contentStats.draft }}</span>
              </div>
            </div>
            <div class="card-border"></div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- Quick Actions -->
    <div class="quick-actions-section">
      <div class="section-title">
        <span class="bracket">[</span>
        <span class="text">QUICK ACCESS</span>
        <span class="bracket">]</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="action-card" @click="navigateTo('/account-management')">
            <div class="action-icon">&gt;_</div>
            <div class="action-title">ACCOUNT_MGMT</div>
            <div class="action-desc">Manage platform nodes</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-card">
            <div class="action-icon">↑</div>
            <div class="action-title">UPLOAD_CONTENT</div>
            <div class="action-desc">Deploy media files</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-card">
            <div class="action-icon">⏱</div>
            <div class="action-title">SCHEDULE_TASK</div>
            <div class="action-desc">Set publish timer</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-card">
            <div class="action-icon">📊</div>
            <div class="action-title">DATA_ANALYSIS</div>
            <div class="action-desc">View metrics</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Web Terminal Integration -->
    <WebTerminal />
    
    <!-- Task List -->
    <div class="task-list-section">
      <div class="section-title">
        <span class="bracket">[</span>
        <span class="text">RECENT OPERATIONS</span>
        <span class="bracket">]</span>
        <button class="terminal-button">VIEW_ALL</button>
      </div>
      
      <div class="terminal-table">
        <div class="table-header">
          <div class="col col-title">TASK_NAME</div>
          <div class="col col-platform">PLATFORM</div>
          <div class="col col-account">ACCOUNT</div>
          <div class="col col-time">TIMESTAMP</div>
          <div class="col col-status">STATUS</div>
          <div class="col col-actions">ACTIONS</div>
        </div>
        
        <div class="table-body">
          <div 
            v-for="task in recentTasks" 
            :key="task.id" 
            class="table-row"
          >
            <div class="col col-title">{{ task.title }}</div>
            <div class="col col-platform">
              <span :class="['platform-tag', getPlatformClass(task.platform)]">
                {{ task.platform }}
              </span>
            </div>
            <div class="col col-account">{{ task.account }}</div>
            <div class="col col-time">{{ task.createTime }}</div>
            <div class="col col-status">
              <span :class="['status-badge', getStatusClass(task.status)]">
                {{ getStatusLabel(task.status) }}
              </span>
            </div>
            <div class="col col-actions">
              <button class="action-btn view" @click="viewTaskDetail(task)">VIEW</button>
              <button 
                v-if="task.status === '待执行'" 
                class="action-btn execute" 
                @click="executeTask(task)"
              >
                EXEC
              </button>
              <button 
                v-if="task.status !== '已完成' && task.status !== '已失败'" 
                class="action-btn cancel" 
                @click="cancelTask(task)"
              >
                KILL
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import WebTerminal from './WebTerminal.vue'

const router = useRouter()

// Stats data - 从API获取真实数据
const accountStats = reactive({
  total: 0,
  normal: 0,
  abnormal: 0
})

const platformStats = reactive({
  total: 0,
  kuaishou: 0,
  douyin: 0,
  channels: 0,
  xiaohongshu: 0
})

const taskStats = reactive({
  total: 0,
  completed: 0,
  inProgress: 0,
  failed: 0
})

const contentStats = reactive({
  total: 0,
  published: 0,
  draft: 0
})

// 从后端API获取真实统计数据
const fetchDashboardStats = async () => {
  try {
    const response = await axios.get('http://localhost:5409/getDashboardStats')
    if (response.data.code === 200) {
      const data = response.data.data
      
      // 更新账号统计
      Object.assign(accountStats, data.accountStats)
      
      // 更新平台统计
      Object.assign(platformStats, data.platformStats)
      
      // 更新任务统计
      Object.assign(taskStats, data.taskStats)
      
      // 更新内容统计
      Object.assign(contentStats, data.contentStats)
      
      console.log('📊 Dashboard stats loaded:', data)
    }
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
    ElMessage.error('Failed to load dashboard statistics')
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDashboardStats()
})

// Recent tasks
const recentTasks = ref([
  {
    id: 1,
    title: '快手视频自动发布',
    platform: '快手',
    account: '快手账号1',
    createTime: '2024-05-01 10:30:00',
    status: '已完成'
  },
  {
    id: 2,
    title: '抖音视频定时发布',
    platform: '抖音',
    account: '抖音账号1',
    createTime: '2024-05-01 11:15:00',
    status: '进行中'
  },
  {
    id: 3,
    title: '视频号内容上传',
    platform: '视频号',
    account: '视频号账号1',
    createTime: '2024-05-01 14:20:00',
    status: '待执行'
  },
  {
    id: 4,
    title: '小红书图文发布',
    platform: '小红书',
    account: '小红书账号1',
    createTime: '2024-05-01 16:45:00',
    status: '已失败'
  },
  {
    id: 5,
    title: '快手短视频批量上传',
    platform: '快手',
    account: '快手账号2',
    createTime: '2024-05-02 09:10:00',
    status: '待执行'
  }
])

// Helper functions
const getPlatformClass = (platform) => {
  const classMap = {
    '快手': 'ks',
    '抖音': 'dy',
    '视频号': 'ch',
    '小红书': 'xhs'
  }
  return classMap[platform] || 'default'
}

const getStatusClass = (status) => {
  const classMap = {
    '已完成': 'success',
    '进行中': 'running',
    '待执行': 'pending',
    '已失败': 'failed'
  }
  return classMap[status] || 'default'
}

const getStatusLabel = (status) => {
  const labelMap = {
    '已完成': '[SUCCESS]',
    '进行中': '[RUNNING]',
    '待执行': '[PENDING]',
    '已失败': '[FAILED]'
  }
  return labelMap[status] || '[UNKNOWN]'
}

const navigateTo = (path) => {
  router.push(path)
}

const viewTaskDetail = (task) => {
  ElMessage.info(`> Viewing task: ${task.title}`)
}

const executeTask = (task) => {
  ElMessageBox.confirm(
    `Execute task: ${task.title}?`,
    'CONFIRM',
    {
      confirmButtonText: 'EXECUTE',
      cancelButtonText: 'ABORT',
      type: 'info',
    }
  )
    .then(() => {
      const index = recentTasks.value.findIndex(t => t.id === task.id)
      if (index !== -1) {
        recentTasks.value[index].status = '进行中'
      }
      ElMessage({
        type: 'success',
        message: '> Task execution started',
      })
    })
    .catch(() => {})
}

const cancelTask = (task) => {
  ElMessageBox.confirm(
    `Kill task: ${task.title}?`,
    'WARNING',
    {
      confirmButtonText: 'KILL',
      cancelButtonText: 'ABORT',
      type: 'warning',
    }
  )
    .then(() => {
      const index = recentTasks.value.findIndex(t => t.id === task.id)
      if (index !== -1) {
        recentTasks.value[index].status = '已取消'
      }
      ElMessage({
        type: 'success',
        message: '> Task terminated',
      })
    })
    .catch(() => {})
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

// Color Variables
$bg-dark: #0a0e17;
$bg-card: rgba(15, 25, 40, 0.7);
$terminal-green: #39ff14;
$aurora-blue: #00d9ff;
$aurora-purple: #b537f2;
$aurora-cyan: #00ffff;
$text-primary: #e0e0e0;
$text-secondary: #8a8a8a;
$border-glow: rgba(57, 255, 20, 0.3);
$success: #00ff00;
$warning: #ffaa00;
$danger: #ff0055;
$info: #00d9ff;

.cyberpunk-dashboard {
  min-height: 100vh;
  background: $bg-dark;
  color: $text-primary;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  padding: 30px;
  position: relative;
  overflow: hidden;
  
  // Animated Grid Background
  .grid-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(57, 255, 20, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(57, 255, 20, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    z-index: 0;
    animation: gridMove 20s linear infinite;
  }
  
  @keyframes gridMove {
    0% { transform: translate(0, 0); }
    100% { transform: translate(50px, 50px); }
  }
  
  // Scanline Effect
  .scanline {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      to bottom,
      transparent 50%,
      rgba(57, 255, 20, 0.02) 50%
    );
    background-size: 100% 4px;
    z-index: 1;
    pointer-events: none;
    animation: scanline 8s linear infinite;
  }
  
  @keyframes scanline {
    0% { transform: translateY(0); }
    100% { transform: translateY(100%); }
  }
  
  > * {
    position: relative;
    z-index: 2;
  }
  
  // Terminal Header
  .terminal-header {
    margin-bottom: 40px;
    
    .terminal-prompt {
      color: $terminal-green;
      font-size: 14px;
      margin-bottom: 10px;
      
      .prompt-symbol {
        opacity: 0.8;
      }
      
      .cursor-blink {
        animation: blink 1s step-end infinite;
      }
    }
    
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
    
    h1 {
      font-size: 36px;
      font-weight: 700;
      color: $terminal-green;
      text-shadow: 
        0 0 10px rgba(57, 255, 20, 0.8),
        0 0 20px rgba(57, 255, 20, 0.5),
        0 0 30px rgba(57, 255, 20, 0.3);
      margin: 10px 0;
      position: relative;
      
      &.glitch-text {
        animation: glitch 3s infinite;
      }
    }
    
    @keyframes glitch {
      0%, 90%, 100% {
        transform: translate(0);
      }
      92% {
        transform: translate(-2px, 2px);
      }
      94% {
        transform: translate(2px, -2px);
      }
      96% {
        transform: translate(-2px, -2px);
      }
    }
    
    .system-status {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 15px;
      
      .status-indicator {
        width: 12px;
        height: 12px;
        background: $success;
        border-radius: 50%;
        box-shadow: 0 0 10px $success;
        
        &.pulse {
          animation: pulse 2s infinite;
        }
      }
      
      @keyframes pulse {
        0%, 100% {
          opacity: 1;
          transform: scale(1);
        }
        50% {
          opacity: 0.6;
          transform: scale(1.1);
        }
      }
      
      .status-text {
        color: $success;
        font-size: 14px;
        letter-spacing: 2px;
      }
    }
  }
  
  // Data Cockpit (Stats Cards)
  .data-cockpit {
    margin-bottom: 40px;
    
    .cyber-card {
      background: $bg-card;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(57, 255, 20, 0.2);
      border-radius: 8px;
      padding: 20px;
      position: relative;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: $terminal-green;
        box-shadow: 
          0 0 20px rgba(57, 255, 20, 0.2),
          inset 0 0 20px rgba(57, 255, 20, 0.05);
        transform: translateY(-2px);
      }
      
      .card-border {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 8px;
        pointer-events: none;
        
        &::before,
        &::after {
          content: '';
          position: absolute;
          width: 20px;
          height: 20px;
          border: 2px solid $terminal-green;
        }
        
        &::before {
          top: -1px;
          left: -1px;
          border-right: none;
          border-bottom: none;
        }
        
        &::after {
          bottom: -1px;
          right: -1px;
          border-left: none;
          border-top: none;
        }
      }
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        .status-tag {
          color: $aurora-blue;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 1px;
        }
        
        .signal-bars {
          display: flex;
          gap: 3px;
          
          span {
            width: 3px;
            height: 12px;
            background: $terminal-green;
            opacity: 0.3;
            animation: signal 1.5s infinite;
            
            &:nth-child(1) { animation-delay: 0s; }
            &:nth-child(2) { animation-delay: 0.2s; }
            &:nth-child(3) { animation-delay: 0.4s; }
          }
        }
        
        @keyframes signal {
          0%, 100% { opacity: 0.3; height: 8px; }
          50% { opacity: 1; height: 16px; }
        }
      }
      
      .card-body {
        text-align: center;
        margin: 20px 0;
        
        .stat-value {
          font-size: 48px;
          font-weight: 700;
          line-height: 1;
          margin-bottom: 10px;
          
          &.glow-green {
            color: $terminal-green;
            text-shadow: 0 0 20px rgba(57, 255, 20, 0.8);
          }
          
          &.glow-blue {
            color: $aurora-blue;
            text-shadow: 0 0 20px rgba(0, 217, 255, 0.8);
          }
          
          &.glow-purple {
            color: $aurora-purple;
            text-shadow: 0 0 20px rgba(181, 55, 242, 0.8);
          }
          
          &.glow-cyan {
            color: $aurora-cyan;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
          }
        }
        
        .stat-label {
          font-size: 12px;
          color: $text-secondary;
          letter-spacing: 2px;
        }
      }
      
      .card-footer {
        border-top: 1px solid rgba(57, 255, 20, 0.1);
        padding-top: 15px;
        
        .mini-stat {
          display: flex;
          justify-content: space-between;
          margin-bottom: 5px;
          font-size: 12px;
          
          .label {
            color: $text-secondary;
          }
          
          .value {
            font-weight: 700;
            
            &.success { color: $success; }
            &.warning { color: $warning; }
            &.danger { color: $danger; }
            &.info { color: $info; }
          }
        }
        
        .platform-badges {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          
          .badge {
            background: rgba(57, 255, 20, 0.1);
            border: 1px solid rgba(57, 255, 20, 0.3);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            color: $terminal-green;
          }
        }
      }
    }
  }
  
  // Quick Actions
  .quick-actions-section {
    margin-bottom: 40px;
    
    .action-card {
      background: $bg-card;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(0, 217, 255, 0.2);
      border-radius: 8px;
      padding: 30px 20px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: $aurora-blue;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
        transform: translateY(-5px);
        
        .action-icon {
          transform: scale(1.2);
          text-shadow: 0 0 20px $aurora-blue;
        }
      }
      
      .action-icon {
        font-size: 36px;
        color: $aurora-blue;
        margin-bottom: 15px;
        transition: all 0.3s ease;
      }
      
      .action-title {
        font-size: 14px;
        font-weight: 700;
        color: $text-primary;
        margin-bottom: 8px;
        letter-spacing: 1px;
      }
      
      .action-desc {
        font-size: 12px;
        color: $text-secondary;
      }
    }
  }
  
  // Section Title
  .section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    
    .bracket {
      color: $terminal-green;
      font-size: 20px;
      font-weight: 700;
    }
    
    .text {
      color: $text-primary;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 2px;
    }
    
    .terminal-button {
      margin-left: auto;
      background: transparent;
      border: 1px solid $terminal-green;
      color: $terminal-green;
      padding: 6px 16px;
      font-family: inherit;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(57, 255, 20, 0.1);
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
      }
    }
  }
  
  // Terminal Table
  .task-list-section {
    .terminal-table {
      background: $bg-card;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(57, 255, 20, 0.2);
      border-radius: 8px;
      overflow: hidden;
      
      .table-header,
      .table-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1.2fr 1.5fr 1fr 1.5fr;
        gap: 15px;
        padding: 15px 20px;
        align-items: center;
      }
      
      .table-header {
        background: rgba(57, 255, 20, 0.05);
        border-bottom: 1px solid rgba(57, 255, 20, 0.2);
        
        .col {
          color: $terminal-green;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 1px;
        }
      }
      
      .table-row {
        border-bottom: 1px solid rgba(57, 255, 20, 0.1);
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(57, 255, 20, 0.05);
        }
        
        &:last-child {
          border-bottom: none;
        }
        
        .col {
          font-size: 13px;
          
          &.col-title {
            color: $text-primary;
          }
          
          &.col-account,
          &.col-time {
            color: $text-secondary;
            font-size: 12px;
          }
        }
        
        .platform-tag {
          display: inline-block;
          padding: 4px 10px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 700;
          
          &.ks {
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            color: #00ff00;
          }
          
          &.dy {
            background: rgba(255, 0, 85, 0.1);
            border: 1px solid rgba(255, 0, 85, 0.3);
            color: #ff0055;
          }
          
          &.ch {
            background: rgba(255, 170, 0, 0.1);
            border: 1px solid rgba(255, 170, 0, 0.3);
            color: #ffaa00;
          }
          
          &.xhs {
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid rgba(0, 217, 255, 0.3);
            color: #00d9ff;
          }
        }
        
        .status-badge {
          display: inline-block;
          padding: 4px 10px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 700;
          font-family: 'JetBrains Mono', monospace;
          
          &.success {
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            color: #00ff00;
          }
          
          &.running {
            background: rgba(255, 170, 0, 0.1);
            border: 1px solid rgba(255, 170, 0, 0.3);
            color: #ffaa00;
          }
          
          &.pending {
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid rgba(0, 217, 255, 0.3);
            color: #00d9ff;
          }
          
          &.failed {
            background: rgba(255, 0, 85, 0.1);
            border: 1px solid rgba(255, 0, 85, 0.3);
            color: #ff0055;
          }
        }
        
        .col-actions {
          display: flex;
          gap: 8px;
          
          .action-btn {
            background: transparent;
            border: 1px solid;
            padding: 4px 12px;
            font-family: inherit;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            
            &.view {
              border-color: $info;
              color: $info;
              
              &:hover {
                background: rgba(0, 217, 255, 0.1);
                box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
              }
            }
            
            &.execute {
              border-color: $success;
              color: $success;
              
              &:hover {
                background: rgba(0, 255, 0, 0.1);
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
              }
            }
            
            &.cancel {
              border-color: $danger;
              color: $danger;
              
              &:hover {
                background: rgba(255, 0, 85, 0.1);
                box-shadow: 0 0 10px rgba(255, 0, 85, 0.5);
              }
            }
          }
        }
      }
    }
  }
}
</style>
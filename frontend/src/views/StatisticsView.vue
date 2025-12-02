<template>
  <div class="statistics">
    <h2>路段红绿灯状态</h2>
    
    <div class="report-section">
      <div class="traffic-light-selector">
        <select 
          v-model="selectedRoad" 
          class="road-select"
          @change="onRoadSelect"
        >
          <option value="">请选择路段</option>
          <option v-for="road in roads" :key="road.id" :value="road.id">
            {{ road.name }} - {{ getLightStatusText(road.lightStatus) }}
          </option>
        </select>
        
        <div v-if="selectedRoadData" class="light-details">
          <div class="detail-item">
            <span class="label">当前状态:</span>
            <span class="value">{{ selectedRoadData.currentState }}</span>
          </div>
          <div class="detail-item">
            <span class="label">绿灯时长:</span>
            <span class="value">{{ selectedRoadData.greenTime }}s</span>
          </div>
          <div class="detail-item">
            <span class="label">红灯时长:</span>
            <span class="value">{{ selectedRoadData.redTime }}s</span>
          </div>
          <div class="detail-item">
            <span class="label">剩余时间:</span>
            <span class="value countdown">{{ selectedRoadData.countdown }}s</span>
          </div>
        </div>
      </div>
      
      <div class="lights-section">
        <div class="lights-container">
          <div class="light-card" v-for="road in roads" :key="road.id">
            <div class="light-header">
              <h3>{{ road.name }}</h3>
              <span :class="['status-indicator', road.lightStatus]"></span>
            </div>
            <div class="light-info">
              <div class="info-item">
                <span class="label">当前状态:</span>
                <span class="value">{{ road.currentState }}</span>
              </div>
              <div class="info-item">
                <span class="label">绿灯时长:</span>
                <span class="value">{{ road.greenTime }}s</span>
              </div>
              <div class="info-item">
                <span class="label">红灯时长:</span>
                <span class="value">{{ road.redTime }}s</span>
              </div>
              <div class="info-item">
                <span class="label">剩余时间:</span>
                <span class="value countdown">{{ road.countdown }}s</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const selectedRoad = ref('')
let countdownTimer = null

// 路段数据（包含红绿灯状态）
const roads = ref([
  { id: 1, name: '中山路', lightStatus: 'green', currentState: '绿灯', greenTime: 60, redTime: 45, countdown: 45 },
  { id: 2, name: '解放路', lightStatus: 'red', currentState: '红灯', greenTime: 50, redTime: 50, countdown: 15 },
  { id: 3, name: '人民路', lightStatus: 'yellow', currentState: '黄灯', greenTime: 55, redTime: 40, countdown: 3 },
  { id: 4, name: '和平路', lightStatus: 'green', currentState: '绿灯', greenTime: 45, redTime: 35, countdown: 28 },
  { id: 5, name: '幸福路', lightStatus: 'red', currentState: '红灯', greenTime: 60, redTime: 45, countdown: 30 },
  { id: 6, name: '建设路', lightStatus: 'green', currentState: '绿灯', greenTime: 55, redTime: 40, countdown: 50 },
  { id: 7, name: '文化路', lightStatus: 'yellow', currentState: '黄灯', greenTime: 45, redTime: 35, countdown: 2 },
  { id: 8, name: '科技路', lightStatus: 'red', currentState: '红灯', greenTime: 50, redTime: 50, countdown: 45 }
])

// 选中路段的数据
const selectedRoadData = computed(() => {
  if (!selectedRoad.value) return null
  return roads.value.find(road => road.id === selectedRoad.value)
})

// 红绿灯状态文本
const getLightStatusText = (status) => {
  const statusMap = {
    'green': '绿灯',
    'red': '红灯',
    'yellow': '黄灯'
  }
  return statusMap[status] || '未知'
}

// 路段选择事件
const onRoadSelect = () => {
  console.log('选择路段:', selectedRoad.value)
}

// 更新单个红绿灯的状态
const updateLightState = (light) => {
  if (light.countdown > 0) {
    light.countdown--
  } else {
    // 状态切换逻辑：绿灯 -> 黄灯 -> 红灯 -> 绿灯
    if (light.lightStatus === 'green') {
      // 绿灯结束，切换到黄灯
      light.lightStatus = 'yellow'
      light.currentState = '黄灯'
      light.countdown = 3 // 黄灯固定3秒
    } else if (light.lightStatus === 'yellow') {
      // 黄灯结束，切换到红灯
      light.lightStatus = 'red'
      light.currentState = '红灯'
      light.countdown = light.redTime
    } else if (light.lightStatus === 'red') {
      // 红灯结束，切换到绿灯
      light.lightStatus = 'green'
      light.currentState = '绿灯'
      light.countdown = light.greenTime
    }
  }
}

// 随机调整时间长度（模拟实际情况中的时间动态调整）
const adjustTimeDynamically = (baseTime) => {
  // 在基础时间的基础上随机调整±10%
  const variation = Math.random() * 0.2 - 0.1 // -0.1 到 0.1
  const adjustedTime = Math.max(10, Math.round(baseTime * (1 + variation)))
  return adjustedTime
}

// 启动定时器更新所有红绿灯和时间
const startCountdown = () => {
  countdownTimer = setInterval(() => {
    // 更新路段红绿灯
    roads.value.forEach(road => {
      updateLightState(road)
      
      // 每30秒随机调整一次绿灯和红灯时长
      if (Math.random() < 0.033) { // 大约30秒一次
        road.greenTime = adjustTimeDynamically(road.greenTime)
        road.redTime = adjustTimeDynamically(road.redTime)
      }
    })
  }, 1000)
}

// 组件挂载时启动定时器
onMounted(() => {
  startCountdown()
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.statistics {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-image: url('@/backgroundpicture/hongludeng.jpeg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

h2 {
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  color: #fff;
}

/* 报告部分样式 */
.report-section {
  width: 100%;
  max-width: 1200px;
}

/* 红绿灯状态选择栏 */
.traffic-light-selector {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  margin-bottom: 20px;
}

/* 路段选择器 */
.road-select {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.2);
  color: white;
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 15px;
}

.road-select option {
  background: #003366;
  color: white;
}

/* 红绿灯详情 */
.light-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-item .label {
  opacity: 0.8;
  font-size: 0.9rem;
}

.detail-item .value {
  font-weight: 500;
  font-size: 1rem;
}

.countdown {
  color: #FFC107;
  font-weight: bold;
}

/* 所有交通信号灯区域 */
.lights-section {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  margin-bottom: 20px;
}

/* 交通信号灯样式 */
.lights-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.light-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.light-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.2);
}

.light-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.light-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.online {
  background-color: #4CAF50;
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.8);
}

.status-indicator.offline {
  background-color: #9E9E9E;
  box-shadow: 0 0 10px rgba(158, 158, 158, 0.8);
}

.light-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item .label {
  opacity: 0.8;
  font-size: 0.9rem;
}

.info-item .value {
  font-weight: 500;
  font-size: 1rem;
}
</style>
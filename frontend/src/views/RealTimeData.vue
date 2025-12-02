<template>
  <div class="real-time-data">
    <h2 class="page-title">实时数据监控</h2>
    
    <div class="main-layout">
      <!-- 左右布局容器 -->
      <div class="content-container">
        <!-- 左侧：路段监控视频区域 -->
        <div class="video-section">
          <h3>路段监控视频</h3>
          <div class="video-controls">
            <select 
              v-model="selectedRoad" 
              class="road-select custom-select"
              @change="onRoadSelect"
            >
              <option value="">请选择路段</option>
              <option v-for="road in roads" :key="road.id" :value="road.id">
                {{ road.name }}
              </option>
            </select>
            
            <select 
              v-model="selectedCamera" 
              class="camera-select"
              @change="onCameraSelect"
              v-if="filteredCameras.length > 0"
            >
              <option value="">请选择摄像头</option>
              <option v-for="camera in filteredCameras" :key="camera.id" :value="camera.id">
                {{ camera.name }} - {{ camera.status === 'online' ? '在线' : '离线' }}
              </option>
            </select>
          </div>
          
          <!-- 视频播放区域 -->
          <div class="video-player-container">
            <div v-if="selectedCameraData" class="video-player">
              <div class="video-header">
                <h4>{{ selectedCameraData.name }}</h4>
                <span :class="['status-indicator', selectedCameraData.status]"></span>
              </div>
              <div class="video-content">
                <div v-if="selectedCameraData.status === 'online'" class="video-frame">
                  <template v-if="selectedCameraData.isVideo">
                    <video 
                      :src="selectedCameraData.streamUrl" 
                      alt="监控视频" 
                      class="video-element"
                      autoplay 
                      loop 
                      muted
                    />
                  </template>
                  <template v-else>
                    <img 
                      :src="selectedCameraData.streamUrl" 
                      alt="监控视频" 
                      class="video-element"
                    />
                  </template>
                  <div class="video-overlay">
                    <div class="video-time">{{ selectedCameraData.lastUpdate }}</div>
                  </div>
                  <!-- 车辆识别覆盖层 -->
                  <div class="vehicle-detection-overlay">
                    <div v-for="vehicle in detectedVehicles.slice(0, 3)" :key="vehicle.id" class="vehicle-detection-tag">
                      <span class="vehicle-type">{{ vehicle.type }}</span>
                      <span class="vehicle-plate">{{ vehicle.plateNumber }}</span>
                      <span class="vehicle-speed">{{ vehicle.speed }} km/h</span>
                    </div>
                  </div>
                </div>
                <div v-else class="video-offline">
                  <p>摄像头离线</p>
                </div>
              </div>
            </div>
            <div v-else class="video-placeholder">
              <p>请选择摄像头查看监控视频</p>
            </div>
          </div>
        </div>
        
        <!-- 右侧：车数量检测区域 -->
        <div class="vehicle-detection-section">
          <!-- 路段选择提示（移动端优化） -->
          <div class="mobile-road-info" v-if="selectedRoadData">
            当前监控：{{ selectedRoadData.name }}
          </div>
          <h3>车数量检测</h3>
          
          <!-- 预警通知已移除 -->
          
          <!-- 当前路段车流量信息 -->
          <div v-if="selectedRoadData" class="current-road-stats">
            <h4>{{ selectedRoadData.name }} 实时车流量</h4>
            <div class="vehicle-count-display">
              <div class="count-number">{{ currentVehicleCount }}</div>
              <div class="count-label">当前车辆数</div>
            </div>
            <div class="traffic-status">
              <span class="status-text">交通状态：</span>
              <span class="status-badge" :class="trafficStatusClass">{{ trafficStatusText }}</span>
            </div>
          </div>
          <div v-else class="no-road-selected">
            <p>请选择路段查看车流量信息</p>
          </div>
          
          <!-- 车流量历史趋势已移除 -->
          
          <!-- 车辆速度检测区域 -->
          <div class="speed-detection-section">
            <h4>车辆速度检测</h4>
            
            <!-- 速度统计概览 -->
            <div class="speed-overview">
              <div class="speed-stat">
                <div class="speed-stat-number">{{ averageSpeed }}</div>
                <div class="speed-stat-label">平均速度 (km/h)</div>
              </div>
              <div class="speed-stat">
                <div class="speed-stat-number" :class="{ 'speed-warning': maxSpeed > 80 }">{{ maxSpeed }}</div>
                <div class="speed-stat-label">最大速度 (km/h)</div>
              </div>
              <div class="speed-stat">
                <div class="speed-stat-number">{{ speedingVehicles.length }}</div>
                <div class="speed-stat-label">超速车辆</div>
              </div>
            </div>
            
            <!-- 速度分布图表 -->
            <div class="speed-distribution">
              <h5>速度分布</h5>
              <div class="distribution-chart">
                <div 
                  v-for="(count, range) in speedDistribution" 
                  :key="range" 
                  class="distribution-bar"
                  :style="{ 
                    height: `${Object.values(speedDistribution).some(v => v > 0) ? 
                      Math.min(100, (count / Math.max(...Object.values(speedDistribution))) * 100) : 0}%` 
                  }"
                  :class="{ 'speeding': range === '超速(>80)' }"
                >
                  <span class="distribution-value">{{ count }}</span>
                </div>
              </div>
              <div class="distribution-labels">
                <span 
                  v-for="(count, range) in speedDistribution" 
                  :key="range" 
                  class="range-label"
                  :class="{ 'speeding-label': range === '超速(>80)' }"
                >
                  {{ range }}
                </span>
              </div>
            </div>
            
            <!-- 超速车辆警告 -->
            <div v-if="speedingVehicles.length > 0" class="speeding-warning">
              <h5>🚨 超速车辆警告</h5>
              <div class="speeding-vehicles">
                <div 
                  v-for="vehicle in speedingVehicles" 
                  :key="vehicle.id" 
                  class="speeding-vehicle-item"
                >
                  <span class="speeding-plate">{{ vehicle.plateNumber }}</span>
                  <span class="speeding-type">{{ vehicle.type }}</span>
                  <span class="speeding-speed">{{ vehicle.speed }} km/h</span>
                  <span class="speeding-time">{{ vehicle.timestamp }}</span>
                </div>
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
const selectedCamera = ref('')
let countdownTimer = null
let vehicleDetectionTimer = null

// 路段监控视频数据
const cameras = ref([
  { id: 1, roadId: 1, name: '中山路-东向西', status: 'online', streamUrl: require('@/video/video2.mp4'), isVideo: true, lastUpdate: new Date().toLocaleTimeString() },
  { id: 2, roadId: 1, name: '中山路-西向东', status: 'online', streamUrl: require('@/video/video2.mp4'), isVideo: true, lastUpdate: new Date().toLocaleTimeString() },
  { id: 3, roadId: 2, name: '解放路-南向北', status: 'online', streamUrl: require('@/video/video3.mp4'), isVideo: true, lastUpdate: new Date().toLocaleTimeString() },
  { id: 4, roadId: 2, name: '解放路-北向南', status: 'online', streamUrl: require('@/video/video3.mp4'), isVideo: true, lastUpdate: new Date().toLocaleTimeString() },
  { id: 5, roadId: 3, name: '人民路-东向西', status: 'offline', streamUrl: 'https://picsum.photos/800/450?random=5', lastUpdate: new Date().toLocaleTimeString() },
  { id: 6, roadId: 4, name: '和平路-西向东', status: 'online', streamUrl: 'https://picsum.photos/800/450?random=6', lastUpdate: new Date().toLocaleTimeString() },
  { id: 7, roadId: 5, name: '幸福路-南向北', status: 'online', streamUrl: 'https://picsum.photos/800/450?random=7', lastUpdate: new Date().toLocaleTimeString() },
  { id: 8, roadId: 6, name: '建设路-北向南', status: 'online', streamUrl: 'https://picsum.photos/800/450?random=8', lastUpdate: new Date().toLocaleTimeString() }
])

// 路段数据（包含车流量信息）
const roads = ref([
  { id: 1, name: '中山路', vehicleBaseCount: 45 },
  { id: 2, name: '解放路', vehicleBaseCount: 38 },
  { id: 3, name: '人民路', vehicleBaseCount: 25 },
  { id: 4, name: '和平路', vehicleBaseCount: 40 },
  { id: 5, name: '幸福路', vehicleBaseCount: 32 },
  { id: 6, name: '建设路', vehicleBaseCount: 30 },
  { id: 7, name: '文化路', vehicleBaseCount: 20 },
  { id: 8, name: '科技路', vehicleBaseCount: 28 }
])

// 车流量相关数据
const currentVehicleCount = ref(0)

// 车辆类型识别相关数据
const detectedVehicles = ref([])
const vehicleTypes = ['轿车', 'SUV', '货车', '公交车']
const vehicleCountByType = ref({
  '轿车': 0,
  'SUV': 0,
  '货车': 0,
  '公交车': 0
})

// 速度检测相关数据
const speedDistribution = ref({
  '低速(20-40)': 0,
  '中速(41-60)': 0,
  '高速(61-80)': 0,
  '超速(>80)': 0
})
const averageSpeed = ref(0)
const maxSpeed = ref(0)
const speedingVehicles = ref([])

// 根据选中的路段过滤摄像头
const filteredCameras = computed(() => {
  if (!selectedRoad.value) return cameras.value
  return cameras.value.filter(camera => camera.roadId === selectedRoad.value)
})

// 选中的摄像头数据
const selectedCameraData = computed(() => {
  if (!selectedCamera.value) return null
  return cameras.value.find(camera => camera.id === selectedCamera.value)
})

// 选中的路段数据
const selectedRoadData = computed(() => {
  if (!selectedRoad.value) return null
  return roads.value.find(road => road.id === selectedRoad.value)
})

// 移除了车流量趋势相关的计算属性

// 交通状态文本（使用固定阈值判断）- 已移除拥堵状态
const trafficStatusText = computed(() => {
  if (currentVehicleCount.value >= 35) {
    return '缓行'
  } else {
    return '畅通'
  }
})

// 交通状态样式类（使用固定阈值判断）- 已移除拥堵状态
const trafficStatusClass = computed(() => {
  if (currentVehicleCount.value >= 35) {
    return 'caution'
  } else {
    return 'normal'
  }
})

// 路段选择事件
const onRoadSelect = () => {
  console.log('选择路段:', selectedRoad.value)
  // 重置选中的摄像头
  selectedCamera.value = ''
  
  // 初始化当前路段车流量
  if (selectedRoadData.value) {
    const baseCount = selectedRoadData.value.vehicleBaseCount
    currentVehicleCount.value = Math.floor(baseCount + (Math.random() * 10 - 5)) // 下调车辆数波动范围
    // 预警功能已移除，无需重置状态
  }
}

// 摄像头选择事件
const onCameraSelect = () => {
  console.log('选择摄像头:', selectedCamera.value)
  // 重置车辆识别数据
  resetVehicleDetectionData()
  // 如果选择了摄像头，开始模拟车辆检测
  if (selectedCamera.value) {
    startVehicleDetectionSimulation()
  }
}

// 重置车辆检测数据
  const resetVehicleDetectionData = () => {
    detectedVehicles.value = []
    speedingVehicles.value = []
    Object.keys(vehicleCountByType.value).forEach(type => {
      vehicleCountByType.value[type] = 0
    })
    Object.keys(speedDistribution.value).forEach(range => {
      speedDistribution.value[range] = 0
    })
    averageSpeed.value = 0
    maxSpeed.value = 0
  }

// 开始模拟车辆检测
const startVehicleDetectionSimulation = () => {
  // 清除可能存在的定时器
  if (window.vehicleDetectionInterval) {
    clearInterval(window.vehicleDetectionInterval)
  }
  
  // 每3秒模拟一次车辆检测
  window.vehicleDetectionInterval = setInterval(() => {
    if (selectedCameraData.value && selectedCameraData.value.status === 'online') {
      simulateVehicleDetection()
    }
  }, 3000)
}

// 模拟车辆检测
  const simulateVehicleDetection = () => {
  // 随机生成1-2辆车辆
  const count = Math.floor(Math.random() * 2) + 1
  // 获取当前道路ID
  const currentRoadId = selectedRoadData.value ? selectedRoadData.value.id : null;
  const isZhongshanRoad = currentRoadId === 1;
  const isJiefangRoad = currentRoadId === 2;
  
  // 设置超速概率：中山路不允许超速，解放路提高超速概率到40%
  let speedingProbability = 0.1; // 默认10%
  if (isZhongshanRoad) speedingProbability = 0; // 中山路无超速
  else if (isJiefangRoad) speedingProbability = 0.4; // 解放路40%概率超速
  
  const hasSpeedingVehicle = Math.random() < speedingProbability;
  let speedingAdded = false
  
  for (let i = 0; i < count; i++) {
    // 随机选择车辆类型
    const randomType = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)]
    // 生成速度，如果需要生成超速车辆且还没有添加，则生成一辆超速车辆(85-120 km/h)
    let speed;
    if (hasSpeedingVehicle && !speedingAdded) {
      speed = Math.floor(Math.random() * 35) + 85; // 85-120 km/h
      speedingAdded = true;
    } else {
      speed = Math.floor(Math.random() * 25) + 5; // 5-30 km/h 正常速度
    }
    // 随机生成车牌号
    const plateNumber = generateRandomPlateNumber()
    
    // 创建车辆对象
    const vehicle = {
      id: Date.now() + i,
      type: randomType,
      speed: speed,
      plateNumber: plateNumber,
      timestamp: new Date().toLocaleTimeString()
    }
    
    // 添加到检测到的车辆列表
    detectedVehicles.value.unshift(vehicle)
    // 只保留最近10辆车的记录
    if (detectedVehicles.value.length > 10) {
      detectedVehicles.value.pop()
    }
    
    // 更新车辆类型统计
    vehicleCountByType.value[randomType]++
    
    // 对于解放路，降低超速阈值至60km/h，使警告更明显
    const speedingThreshold = isJiefangRoad ? 60 : 80;
    
    // 更新速度分布
    if (speed <= 40) {
      speedDistribution.value['低速(20-40)']++
    } else if (speed <= 60) {
      speedDistribution.value['中速(41-60)']++
    } else if (speed <= speedingThreshold) {
      speedDistribution.value['高速(61-80)']++
    } else {
      // 解放路超速标记
      const speedingLabel = isJiefangRoad ? '解放路超速' : '普通超速';
      vehicle.speedingType = speedingLabel;
      
      speedDistribution.value['超速(>80)']++
      // 添加到超速车辆列表
      speedingVehicles.value.unshift(vehicle)
      // 只保留最近5辆超速车辆
      if (speedingVehicles.value.length > 5) {
        speedingVehicles.value.pop()
      }
    }
  }
  
  // 更新平均速度和最大速度
  if (detectedVehicles.value.length > 0) {
    const allSpeeds = detectedVehicles.value.map(v => v.speed)
    averageSpeed.value = Math.round(allSpeeds.reduce((sum, speed) => sum + speed, 0) / allSpeeds.length)
    maxSpeed.value = Math.max(...allSpeeds)
  }
}

// 生成随机车牌号
const generateRandomPlateNumber = () => {
  // 根据道路ID决定车牌号前缀：解放路(roadId=2)使用粤，其他使用浙
  const isJiefangRoad = selectedRoadData.value && selectedRoadData.value.id === 2;
  const prefix = isJiefangRoad ? '粤' : '浙'
  // 浙江各地市字母（简化版，不使用容易混淆的字母）
  const cityLetters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'.replace(/[OI]/g, '') // 移除O和I，避免与数字0和1混淆
  // 90%的概率选择浙B，10%的概率随机选择其他字母
  const cityLetter = Math.random() < 0.9 ? 'B' : cityLetters[Math.floor(Math.random() * cityLetters.length)]
  
  // 生成5位部分，以数字居多，只包含一个字母
  const digits = '0123456789'
  const letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'.replace(/[OI]/g, '') // 移除O和I，避免与数字0和1混淆
  let numberPart = ''
  
  // 随机决定字母的位置（0-4）
  const letterPosition = Math.floor(Math.random() * 5)
  
  // 生成5位字符，其中只有指定位置是字母，其余都是数字
  for (let i = 0; i < 5; i++) {
    if (i === letterPosition) {
      // 字母位置
      numberPart += letters[Math.floor(Math.random() * letters.length)]
    } else {
      // 数字位置
      numberPart += digits[Math.floor(Math.random() * digits.length)]
    }
  }
  
  return `${prefix}${cityLetter}${numberPart}`
}

// 预警功能已移除

// 模拟车辆数量变化
const simulateVehicleCount = () => {
  if (!selectedRoadData.value) return
  
  // 调整为更低的车流量
  let baseCount = selectedRoadData.value.vehicleBaseCount
  
  // 下调基础车流量10-20%
  baseCount = Math.floor(baseCount * 0.85)
  
  // 随机波动，模拟真实车流量变化，但范围更小
  const variation = Math.random() * 4 - 2 // -2 到 2 的随机波动
  currentVehicleCount.value = Math.max(0, Math.floor(baseCount + variation + (Math.random() * 5 - 2.5)))
  
  // 移除了历史数据更新逻辑
  
  // 预警功能已移除
}

// 预警功能已移除，相关函数已删除

// 启动定时器更新摄像头时间和车流量
const startCountdown = () => {
  countdownTimer = setInterval(() => {
    // 更新在线摄像头的时间戳
    cameras.value.forEach(camera => {
      if (camera.status === 'online') {
        camera.lastUpdate = new Date().toLocaleTimeString()
      }
    })
  }, 1000)
  
  // 启动车流量检测定时器（每5秒更新一次）
  vehicleDetectionTimer = setInterval(() => {
    simulateVehicleCount()
  }, 5000)
}

// 组件挂载时启动定时器
onMounted(() => {
  startCountdown()
})

// 组件卸载时清除定时器
  onUnmounted(() => {
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
    if (vehicleDetectionTimer) {
      clearInterval(vehicleDetectionTimer)
      vehicleDetectionTimer = null
    }
    // 清除车辆检测定时器
    if (window.vehicleDetectionInterval) {
      clearInterval(window.vehicleDetectionInterval)
      window.vehicleDetectionInterval = null
    }
  })
</script>

<style scoped>
.real-time-data {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    background-image: url('@/backgroundpicture/mapbg.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    /* 添加透明度 */
    background-color: rgba(0, 0, 0, 0.5);
    background-blend-mode: overlay;
    /* 边框虚化效果 */
    position: relative;
    overflow: hidden;
  }

  .real-time-data::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('@/backgroundpicture/mapbg.png');
    background-size: cover;
    background-position: center;
    opacity: 0.6;
    z-index: -1;
    filter: blur(8px);
    margin: -20px;
  }

  .page-title {
    font-size: 2rem;
    margin-bottom: 2rem;
    text-align: center;
    background: linear-gradient(135deg, #1a91ff 0%, #0056b3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 2px 10px rgba(26, 145, 255, 0.3);
    padding: 10px;
  }

/* 主布局 */
.main-layout {
  width: 100%;
  height: calc(100% - 100px);
  padding: 0 20px;
  overflow: hidden;
}

/* 内容容器 - 左右布局 */
.content-container {
  display: flex;
  gap: 20px;
  width: 100%;
  height: 100%;
}

/* 左侧：监控视频区域 */
.video-section {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  width: 60%;
  display: flex;
  flex-direction: column;
}

/* 右侧：车数量检测区域 */
.vehicle-detection-section {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  width: 40%;
  display: flex;
  flex-direction: column;
  color: white;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-weight: 500;
}

.vehicle-detection-section h3 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 1.3rem;
    color: white;
    text-align: center;
    background: linear-gradient(135deg, #1a91ff 0%, #0056b3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 10px;
  }
  
  .mobile-road-info {
    display: none; /* 默认隐藏，移动端显示 */
    background: rgba(102, 126, 234, 0.2);
    padding: 10px;
    border-radius: 6px;
    text-align: center;
    font-weight: 500;
    margin-bottom: 15px;
  }
  
  @media (max-width: 768px) {
    .mobile-road-info {
      display: block;
    }
  }

/* 预警通知 */
.warning-notification {
  background: linear-gradient(135deg, rgba(26, 145, 255, 0.9), rgba(0, 86, 179, 0.8));
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  animation: pulse 1.5s infinite alternate;
  box-shadow: 0 4px 20px rgba(26, 145, 255, 0.6);
}

@keyframes pulse {
  0% {
    box-shadow: 0 4px 20px rgba(26, 145, 255, 0.6);
  }
  100% {
    box-shadow: 0 4px 30px rgba(26, 145, 255, 0.9), 0 0 15px rgba(102, 187, 255, 0.6);
  }
}

.warning-icon {
  font-size: 2rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.warning-content {
  flex: 1;
}

.warning-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.warning-message {
  font-size: 0.9rem;
  margin-bottom: 10px;
  opacity: 0.9;
}

.dispatch-button {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.dispatch-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 当前路段车流量信息 */
.current-road-stats {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.current-road-stats.traffic-warning {
  background: rgba(26, 145, 255, 0.2);
  border: 1px solid rgba(26, 145, 255, 0.4);
}

.current-road-stats h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.1rem;
  text-align: center;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.vehicle-count-display {
  text-align: center;
  margin-bottom: 15px;
}

.count-number {
  font-size: 3rem;
  font-weight: bold;
  color: #4CAF50;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8), 0 0 10px rgba(76, 175, 80, 0.7);
  transition: all 0.3s ease;
}

.count-number.warning-text {
  color: #1a91ff;
  text-shadow: 0 0 15px rgba(26, 145, 255, 0.8);
  animation: glow 1s infinite alternate;
}

@keyframes glow {
  0% {
    text-shadow: 0 0 15px rgba(26, 145, 255, 0.8);
  }
  100% {
    text-shadow: 0 0 25px rgba(26, 145, 255, 1), 0 0 15px rgba(102, 187, 255, 0.8);
  }
}

.count-label {
  font-size: 0.95rem;
  opacity: 1;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.traffic-status {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.status-text {
  font-size: 0.95rem;
  opacity: 1;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  transition: all 0.3s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-badge.normal {
  background: rgba(76, 175, 80, 0.3);
  color: #4CAF50;
}

.status-badge.caution {
  background: rgba(255, 152, 0, 0.3);
  color: #FF9800;
}

.status-badge.warning {
  background: rgba(26, 145, 255, 0.3);
  color: #1a91ff;
  animation: pulse 1.5s infinite alternate;
}

.threshold-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  font-size: 0.9rem;
  opacity: 0.8;
}

.threshold-value {
  font-weight: bold;
  color: #2196F3;
}

.no-road-selected {
  text-align: center;
  padding: 30px;
  opacity: 0.6;
}

/* 速度检测区域 */
  .speed-detection-section {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .speed-detection-section h4 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 1.1rem;
    text-align: center;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }
  
  /* 速度统计概览 */
  .speed-overview {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
    gap: 10px;
  }
  
  .speed-stat {
    flex: 1;
    text-align: center;
    background: rgba(0, 0, 0, 0.2);
    padding: 15px 10px;
    border-radius: 8px;
  }
  
  .speed-stat-number {
    font-size: 1.8rem;
    font-weight: bold;
    color: #4CAF50;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8), 0 0 10px rgba(76, 175, 80, 0.7);
    margin-bottom: 5px;
  }
  
  .speed-stat-number.speed-warning {
    color: #ff5722;
    text-shadow: 0 0 15px rgba(255, 87, 34, 0.8);
    animation: speedGlow 1s infinite alternate;
  }
  
  @keyframes speedGlow {
    0% {
      text-shadow: 0 0 15px rgba(255, 87, 34, 0.8);
    }
    100% {
      text-shadow: 0 0 25px rgba(255, 87, 34, 1), 0 0 15px rgba(255, 152, 0, 0.8);
    }
  }
  
  .speed-stat-label {
    font-size: 0.85rem;
    opacity: 1;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }
  
  /* 速度分布图 */
  .speed-distribution {
    margin-bottom: 20px;
  }
  
  .speed-distribution h5 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 0.95rem;
    text-align: center;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }
  
  .distribution-chart {
    height: 120px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 8px;
    padding: 15px 10px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    margin-bottom: 10px;
  }
  
  .distribution-bar {
    flex: 1;
    background: rgba(33, 150, 243, 0.6);
    border-radius: 4px 4px 0 0;
    transition: height 0.5s ease;
    position: relative;
    min-height: 15px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 4px;
  }
  
  .distribution-bar.speeding {
    background: rgba(255, 87, 34, 0.8);
    box-shadow: 0 0 10px rgba(255, 87, 34, 0.7);
  }
  
  .distribution-value {
    font-size: 0.7rem;
    font-weight: bold;
    color: white;
    text-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
  }
  
  .distribution-labels {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    padding: 0 10px;
  }
  
  .range-label {
    flex: 1;
    font-size: 0.75rem;
    text-align: center;
    opacity: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }
  
  .range-label.speeding-label {
    color: #ff5722;
    font-weight: bold;
    opacity: 1;
  }
  
  /* 超速车辆警告 */
  .speeding-warning {
    background: linear-gradient(135deg, rgba(255, 87, 34, 0.3), rgba(255, 152, 0, 0.2));
    border: 1px solid rgba(255, 87, 34, 0.4);
    border-radius: 8px;
    padding: 15px;
  }
  
  .speeding-warning h5 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 0.95rem;
    color: #ff5722;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }
  
  .speeding-vehicles {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .speeding-vehicle-item {
    background: rgba(255, 255, 255, 0.1);
    padding: 8px 12px;
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .speeding-plate {
    font-weight: bold;
    color: #ffeb3b;
  }
  
  .speeding-speed {
    color: #ff5722;
    font-weight: bold;
    font-size: 0.9rem;
  }
  
  .speeding-time {
    opacity: 1;
    font-size: 0.8rem;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }

/* 移除了车流量趋势相关样式 */

.video-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.3rem;
  color: white;
  text-align: center;
}

/* 视频控制区域 */
  .video-controls {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .camera-select {
    flex: 1;
    min-width: 200px;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(0, 0, 0, 0.2);
    color: white;
    font-size: 1rem;
    cursor: pointer;
  }

  .camera-select option {
    background: #003366;
    color: white;
  }

  .custom-select {
    padding: 10px 15px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
  }

  .custom-select:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }

  .custom-select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(26, 145, 255, 0.5);
}

  /* 视频播放容器 - 缩小尺寸 */
  .video-player-container {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 15px;
    min-height: 0; /* 移除最小高度限制，让容器自适应 */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s ease;
  }
  
  .video-player-container:hover {
    transform: scale(1.01);
  }

.video-player {
  width: 100%;
  max-width: 800px;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.video-header h4 {
  margin: 0;
  color: white;
  font-size: 1.1rem;
}

/* 视频内容 */
  .video-content {
    position: relative;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    aspect-ratio: 16/9;
  }

  .video-frame {
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  /* 车辆识别覆盖层 */
  .vehicle-detection-overlay {
    position: absolute;
    top: 10px;
    left: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    z-index: 10;
  }
  
  .vehicle-detection-tag {
    background: rgba(0, 150, 136, 0.8);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    backdrop-filter: blur(4px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    gap: 2px;
    animation: fadeInSlide 0.5s ease-out;
  }
  
  @keyframes fadeInSlide {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .vehicle-type {
    font-weight: bold;
  }
  
  .vehicle-plate {
    font-size: 0.8rem;
  }
  
  .vehicle-speed {
    font-size: 0.8rem;
    color: #b2ebf2;
  }

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.video-offline {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
}

.video-placeholder {
  text-align: center;
  color: white;
  opacity: 0.7;
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
}

.road-select option {
  background: #003366;
  color: white;
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
    animation: status-pulse 2s infinite;
  }
  
  @keyframes status-pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  .status-indicator.offline {
     background-color: #9E9E9E;
     box-shadow: 0 0 10px rgba(158, 158, 158, 0.8);
    }
  
  /* 响应式布局 */
  @media (max-width: 1024px) {
    .content-container {
      flex-direction: column;
    }
    
    .video-section,
    .vehicle-detection-section {
      width: 100% !important;
    }
    
    .vehicle-detection-section {
      margin-top: 30px;
      min-height: 500px;
    }
  }
  
  @media (max-width: 768px) {
    .main-layout {
      padding: 15px;
    }
    
    .page-title {
      font-size: 1.5rem;
      margin-bottom: 20px;
    }
    
    .video-controls {
      flex-direction: column;
    }
    
    .custom-select,
    .camera-select {
      width: 100%;
      margin-top: 10px;
    }
    
    .video-player {
      max-height: 300px;
    }
    
    .vehicle-history {
      min-height: 300px;
    }
  }
  
  @media (max-width: 480px) {
    .count-number {
      font-size: 2.5rem;
    }
    
    .warning-notification {
      padding: 12px;
    }
    
    .warning-content {
      font-size: 0.9rem;
    }
    
    .dispatch-button {
      padding: 6px 12px;
      font-size: 0.8rem;
    }
  }
</style>
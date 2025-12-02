<template>
  <div class="home router-view-home">
    <div class="hero-section">
      <h1>智慧交通平台</h1>
      <p class="subtitle">实时监控城市交通，智能分析路况信息</p>
    </div>
    
    <div class="overview">
      <div class="stat-card flow">
        <div class="stat-icon">🚗</div>
        <h3>实时车流量</h3>
        <p class="stat-number" ref="flowRef">{{ displayFlow }}</p>
      </div>
      <div class="stat-card speed">
        <div class="stat-icon">⚡</div>
        <h3>平均车速</h3>
        <p class="stat-number" ref="speedRef">{{ displaySpeed }} km/h</p>
      </div>
      <div class="stat-card congestion">
        <div class="stat-icon">🚧</div>
        <h3>拥堵路段</h3>
        <p class="stat-number" ref="congestionRef">{{ displayCongestion }}</p>
      </div>
      <div class="stat-card accident">
        <div class="stat-icon">⚠️</div>
        <h3>事故数量</h3>
        <p class="stat-number" ref="accidentRef">{{ displayAccident }}</p>
      </div>
    </div>
    
    <div class="features">
      <div class="feature-card map">
        <div class="feature-icon">🗺️</div>
        <h3>实时交通地图</h3>
        <p>查看城市交通拥堵情况，了解各路段实时流量和路况信息</p>
        <RouterLink to="/traffic-map" class="btn">查看地图</RouterLink>
      </div>
      <div class="feature-card monitor">
        <div class="feature-icon">📊</div>
        <h3>实时数据监控</h3>
        <p>监控交通信号灯、摄像头等设备的实时状态，确保交通顺畅</p>
        <RouterLink to="/real-time-data" class="btn">查看数据</RouterLink>
      </div>
      <div class="feature-card statistics">
        <div class="feature-icon">📈</div>
        <h3>统计分析报告</h3>
        <p>查看历史交通数据统计和分析报告，优化交通管理决策</p>
        <RouterLink to="/statistics" class="btn">查看统计</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

// 模拟数据
const trafficFlow = ref(12580)
const averageSpeed = ref(35.2)
const congestedRoads = ref(12)
const accidentCount = ref(3)

// 用于数字动画显示的值
const displayFlow = ref(0)
const displaySpeed = ref(0)
const displayCongestion = ref(0)
const displayAccident = ref(0)

// 动画引用
const flowRef = ref(null)
const speedRef = ref(null)
const congestionRef = ref(null)
const accidentRef = ref(null)

// 数字动画函数
const animateNumber = (target, start, duration, callback) => {
  const increment = target > start ? 1 : -1
  const range = Math.abs(target - start)
  const stepTime = Math.abs(Math.floor(duration / range))
  let current = start
  
  const timer = setInterval(() => {
    current += increment
    callback(current)
    
    if (current === target) {
      clearInterval(timer)
    }
  }, stepTime)
}

// 浮点数动画函数
const animateFloat = (target, start, duration, callback) => {
  const increment = (target - start) / (duration / 16) // 60fps
  let current = start
  
  const timer = setInterval(() => {
    current += increment
    
    if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
      current = target
      clearInterval(timer)
    }
    
    callback(current.toFixed(1))
  }, 16)
}

// 组件挂载后执行动画
onMounted(() => {
  animateNumber(trafficFlow.value, 0, 2000, (val) => displayFlow.value = val)
  animateFloat(averageSpeed.value, 0, 2000, (val) => displaySpeed.value = val)
  animateNumber(congestedRoads.value, 0, 1500, (val) => displayCongestion.value = val)
  animateNumber(accidentCount.value, 0, 1000, (val) => displayAccident.value = val)
})
</script>

<style scoped>
.home {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  overflow: hidden;
  padding: 20px;
  box-sizing: border-box;
}

/* 英雄区 */
.hero-section {
  text-align: center;
  padding: 20px;
  animation: fadeInUp 1s ease-out;
  flex: 0 0 auto;
}

.hero-section h1 {
  font-size: 2.5rem;
  margin-bottom: 0.8rem;
  text-align: center;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: bold;
}

.subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

/* 概览区域 */
.overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  width: 100%;
  max-width: 1200px;
  flex: 0 0 auto;
}

/* 统计卡片 */
.stat-card {
  padding: 20px 15px;
  text-align: center;
  backdrop-filter: blur(15px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.8s ease-out;
  transition: all 0.4s ease;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--card-color-start), var(--card-color-end));
}

.stat-card.flow {
  background: linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.2));
  --card-color-start: #4facfe;
  --card-color-end: #00f2fe;
}

.stat-card.speed {
  background: linear-gradient(135deg, rgba(120, 219, 226, 0.2), rgba(255, 239, 186, 0.2));
  --card-color-start: #78dbe2;
  --card-color-end: #ffe5b4;
}

.stat-card.congestion {
  background: linear-gradient(135deg, rgba(255, 193, 193, 0.2), rgba(255, 140, 105, 0.2));
  --card-color-start: #ffc1c1;
  --card-color-end: #ff8c69;
}

.stat-card.accident {
  background: linear-gradient(135deg, rgba(255, 182, 193, 0.2), rgba(255, 105, 180, 0.2));
  --card-color-start: #ffb6c1;
  --card-color-end: #ff69b4;
}

.stat-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.2);
}

.stat-icon {
  font-size: 2.2rem;
  margin-bottom: 10px;
  animation: pulse 2s ease-in-out infinite;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  opacity: 0.95;
  color: #fff;
}

.stat-number {
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

/* 功能区域 */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  width: 100%;
  max-width: 1200px;
  flex: 0 0 auto;
  margin-bottom: 20px;
}

/* 功能卡片 */
.feature-card {
  padding: 25px 20px;
  text-align: center;
  backdrop-filter: blur(15px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.8s ease-out 0.2s both;
  transition: all 0.4s ease;
  height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--feature-color-start), var(--feature-color-end));
}

.feature-card.map {
  background: linear-gradient(135deg, rgba(79, 172, 254, 0.15), rgba(0, 242, 254, 0.15));
  --feature-color-start: #4facfe;
  --feature-color-end: #00f2fe;
}

.feature-card.monitor {
  background: linear-gradient(135deg, rgba(120, 219, 226, 0.15), rgba(255, 239, 186, 0.15));
  --feature-color-start: #78dbe2;
  --feature-color-end: #ffe5b4;
}

.feature-card.statistics {
  background: linear-gradient(135deg, rgba(255, 193, 193, 0.15), rgba(255, 140, 105, 0.15));
  --feature-color-start: #ffc1c1;
  --feature-color-end: #ff8c69;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.2);
}

.feature-icon {
  font-size: 2.8rem;
  margin-bottom: 15px;
  animation: float 3s ease-in-out infinite;
}

.feature-card h3 {
  margin: 0 0 15px 0;
  font-size: 1.4rem;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.feature-card p {
  margin: 0 0 20px 0;
  opacity: 0.9;
  line-height: 1.5;
  font-size: 0.95rem;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.15));
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  font-size: 0.9rem;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0.25));
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .features {
    grid-template-columns: repeat(1, 1fr);
    gap: 15px;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 15px;
    gap: 20px;
  }
  
  .hero-section h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 0.9rem;
  }
  
  .overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .features {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-card {
    height: 180px;
    padding: 15px 10px;
  }
  
  .feature-card {
    height: 220px;
    padding: 20px 15px;
  }
  
  .stat-number {
    font-size: 1.8rem;
  }
  
  .stat-icon {
    font-size: 1.8rem;
  }
  
  .feature-icon {
    font-size: 2.2rem;
  }
  
  .feature-card h3 {
    font-size: 1.2rem;
  }
  
  .btn {
    padding: 10px 20px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .stat-card {
    height: 160px;
    padding: 12px 8px;
  }
  
  .hero-section h1 {
    font-size: 1.8rem;
  }
}
</style>
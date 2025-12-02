<template>
  <div class="traffic-map">
    <h2>交通地图监测</h2>
    <div class="map-container">
      <div id="amap-container" class="map"></div>
    </div>
    
    <div class="legend">
      <h3>交通状态</h3>
      <div class="legend-item">
        <span class="legend-color" style="background-color: #4CAF50;"></span>
        <span>畅通 (≥40 km/h)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: #FFC107;"></span>
        <span>缓行 (20-40 km/h)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: #F44336;"></span>
        <span>拥堵 (&lt;20 km/h)</span>
      </div>
    </div>
    
    <div class="road-status">
      <h3>实时路段状态</h3>
      <!-- 表头容器 -->
      <div class="header-container">
        <table>
          <thead>
            <tr>
              <th>路段名称</th>
              <th>状态</th>
              <th>速度</th>
              <th>流量</th>
            </tr>
          </thead>
        </table>
      </div>
      
      <!-- 表体容器 -->
      <div class="table-container">
        <table>
          <tbody>
            <tr v-for="(road, index) in roadList" :key="road.id" :class="['road-row', { 'active': activeIndex === index }]">
              <td>{{ road.name }}</td>
              <td>
                <span :class="['status-badge', road.status]">{{ road.statusText }}</span>
              </td>
              <td>{{ road.speed }} km/h</td>
              <td>{{ road.flow }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- 雷达图容器 -->
    <div class="radar-chart-container">
      <div id="radar-chart" class="radar-chart"></div>
    </div>
    <!-- 道路流量分布饼图容器 -->
    <div class="pie-chart-container">
      <div id="pie-chart" class="pie-chart"></div>
    </div>
    <!-- 实时车流量统计图表容器 -->
    <div class="traffic-flow-container">
      <div id="traffic-flow-chart" class="traffic-flow-chart"></div>
    </div>
    
    <!-- 周流量柱状图容器 -->
    <div class="week-flow-container">
      <div id="week-flow-chart" class="week-flow-chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import * as echarts from 'echarts'

const roadList = ref([
  { id: 1, name: '东方红大道', status: 'smooth', statusText: '畅通', speed: 45, flow: 850, longitude: 114.085947, latitude: 32.131746 },
  { id: 2, name: '中山路', status: 'slow', statusText: '缓行', speed: 28, flow: 1200, longitude: 114.090123, latitude: 32.128976 },
  { id: 3, name: '南京路', status: 'congested', statusText: '拥堵', speed: 15, flow: 1800, longitude: 114.079834, latitude: 32.135642 },
  { id: 4, name: '浉河南路', status: 'smooth', statusText: '畅通', speed: 52, flow: 950, longitude: 114.073567, latitude: 32.120345 },
  { id: 5, name: '平西路', status: 'slow', statusText: '缓行', speed: 32, flow: 1350, longitude: 114.102345, latitude: 32.138765 },
  { id: 6, name: '新五大道', status: 'congested', statusText: '拥堵', speed: 18, flow: 1600, longitude: 114.089765, latitude: 32.142345 },
  { id: 7, name: '羊山大道', status: 'smooth', statusText: '畅通', speed: 48, flow: 900, longitude: 114.095678, latitude: 32.130123 },
  { id: 8, name: '鸡公山大街', status: 'slow', statusText: '缓行', speed: 30, flow: 1400, longitude: 114.078901, latitude: 32.125432 }
])

// 当前激活的行索引
const activeIndex = ref(0)

// 地图实例
let map = null
// 标记数组
let markers = []


// 已移除图层实例引用


// 初始化地图
const initMap = async () => {
  try {
    // 检查地图容器是否存在
    const container = document.getElementById('amap-container')
    if (!container) {
      throw new Error('地图容器不存在')
    }
    
    // 检查容器尺寸
    const rect = container.getBoundingClientRect()
    if (rect.width === 0 || rect.height === 0) {
      throw new Error('地图容器尺寸为0，请检查CSS样式')
    }
    
    // 加载高德地图SDK - 加载必要的基础插件
    await AMapLoader.load({
      key: 'YOUR_MAP_API_KEY', // 请替换为实际的地图API密钥
      version: '2.0',
      plugins: ['MapType'], // 预先加载地图类型控件
      AMapUI: { // 加载UI组件库
        version: '1.1',
        plugins: []
      }
    })

    // 创建地图实例
    map = new window.AMap.Map('amap-container', {
      zoom: 11,
      center: [114.075031, 32.123274], // 河南信阳坐标
      viewMode: '3D',
      mapStyle: 'amap://styles/blue', // 使用蓝色主题样式
      defaultLayer: 'base' // 使用默认的矢量底图图层
    })
    
    // 添加高德内置的地图类型控件，确保显示标准图层和路网
    map.plugin('AMap.MapType', () => {
      try {
        const mapTypeControl = new window.AMap.MapType({
          defaultType: 0, // 默认显示标准图层
          showRoadNet: true, // 强制显示路网
          position: 'RT', // 右上角位置
          offset: [10, -50] // 向右偏移10px，向上偏移50px
        })
        map.addControl(mapTypeControl)
        console.log('地图类型控件添加成功')
        
        // 确保地图显示路网
        map.setRoadNet(true)
      } catch (err) {
        console.error('添加地图类型控件失败:', err)
      }
    })
    
    // 已移除交通图层加载代码，直接使用标准图层加路网

    // 添加地图控件 - 使用异步加载方式
    window.AMap.plugin(['AMap.ToolBar', 'AMap.Scale', 'AMap.Geolocation'], () => {
      try {
        // 添加工具栏
        if (window.AMap.ToolBar) {
          map.addControl(new window.AMap.ToolBar())
        }
        // 添加比例尺
        if (window.AMap.Scale) {
          map.addControl(new window.AMap.Scale())
        }
        // 添加定位控件
        if (window.AMap.Geolocation) {
          map.addControl(new window.AMap.Geolocation())
        }
      } catch (err) {
        console.error('添加地图控件失败:', err)
      }
    })

    // 添加地图点击事件，支持标记位点和显示经纬度
    map.on('click', (e) => {
      const { lng, lat } = e.lnglat
      
      // 创建标记
      const marker = new window.AMap.Marker({
        position: [lng, lat],
        title: '标记位点',
        map: map
      })
      
      // 存储标记
      markers.push(marker)
      
      // 创建信息窗口
      const infoWindow = new window.AMap.InfoWindow({
        content: `<div style="padding: 10px;">
                   <p>经度: ${lng.toFixed(6)}</p>
                   <p>纬度: ${lat.toFixed(6)}</p>
                 </div>`,
        offset: new window.AMap.Pixel(0, -30)
      })
      
      // 打开信息窗口
      infoWindow.open(map, [lng, lat])
    })
    


  } catch (error) {
    console.error('初始化地图失败:', error)
  }
}

// 滚动定时器引用
let scrollTimer = null

// 组件挂载时初始化地图、自动滚动和雷达图
onMounted(() => {
  initMap()
  
  // 启动自动滚动
  nextTick(() => {
    const tableContainer = document.querySelector('.table-container')
    const rows = document.querySelectorAll('.road-row')
    if (tableContainer && rows.length > 0) {
      // 计算行高
      const rowHeight = rows[0].offsetHeight
      
      scrollTimer = setInterval(() => {
        // 更新激活行索引
        activeIndex.value = (activeIndex.value + 1) % roadList.value.length
        
        // 滚动到当前激活行
        const scrollPosition = activeIndex.value * rowHeight
        tableContainer.scrollTop = scrollPosition
      }, 2000) // 每2秒滚动一行
    }
    
    // 初始化雷达图
    initRadarChart()
    
    // 初始化实时车流量统计图表
    initTrafficFlowChart()
    
    // 初始化道路流量分布饼图
    initPieChart()
    
    // 初始化周流量柱状图
    initWeekFlowChart()
    

  })
})

// 雷达图实例引用和区域索引
let radarChart = null;
let currentAreaIndex = 0;
let areaInterval = null;

// 实时车流量统计图表实例
let trafficFlowChart = null;
let trafficFlowInterval = null;

// 道路流量分布饼图实例
let pieChart = null;

// 周流量柱状图实例
let weekFlowChart = null;

// 初始化雷达图
const initRadarChart = () => {
  const chartDom = document.getElementById('radar-chart')
  if (!chartDom) return
  
  radarChart = echarts.init(chartDom)
  
  const dataBJ = [ 
    [55, 9, 56, 0.46, 18, 6, 1], 
    [25, 11, 21, 0.65, 34, 9, 2], 
    [56, 7, 63, 0.3, 14, 5, 3], 
    [33, 7, 29, 0.33, 16, 6, 4], 
    [42, 24, 44, 0.76, 40, 16, 5], 
    [82, 58, 90, 1.77, 68, 33, 6], 
    [74, 49, 77, 1.46, 48, 27, 7], 
    [78, 55, 80, 1.29, 59, 29, 8], 
    [267, 216, 280, 4.8, 108, 64, 9], 
    [185, 127, 216, 2.52, 61, 27, 10], 
    [39, 19, 38, 0.57, 31, 15, 11], 
    [41, 11, 40, 0.43, 21, 7, 12], 
    [64, 38, 74, 1.04, 46, 22, 13], 
    [108, 79, 120, 1.7, 75, 41, 14], 
    [108, 63, 116, 1.48, 44, 26, 15], 
    [33, 6, 29, 0.34, 13, 5, 16], 
    [94, 66, 110, 1.54, 62, 31, 17], 
    [186, 142, 192, 3.88, 93, 79, 18], 
    [57, 31, 54, 0.96, 32, 14, 19], 
    [22, 8, 17, 0.48, 23, 10, 20], 
    [39, 15, 36, 0.61, 29, 13, 21], 
    [94, 69, 114, 2.08, 73, 39, 22], 
    [99, 73, 110, 2.43, 76, 48, 23], 
    [31, 12, 30, 0.5, 32, 16, 24], 
    [42, 27, 43, 1, 53, 22, 25], 
    [154, 117, 157, 3.05, 92, 58, 26], 
    [234, 185, 230, 4.09, 123, 69, 27], 
    [160, 120, 186, 2.77, 91, 50, 28], 
    [134, 96, 165, 2.76, 83, 41, 29], 
    [52, 24, 60, 1.03, 50, 21, 30], 
    [46, 5, 49, 0.28, 10, 6, 31] 
  ] 
  const dataGZ = [ 
    [26, 37, 27, 1.163, 27, 13, 1], 
    [85, 62, 71, 1.195, 60, 8, 2], 
    [78, 38, 74, 1.363, 37, 7, 3], 
    [21, 21, 36, 0.634, 40, 9, 4], 
    [41, 42, 46, 0.915, 81, 13, 5], 
    [56, 52, 69, 1.067, 92, 16, 6], 
    [64, 30, 28, 0.924, 51, 2, 7], 
    [55, 48, 74, 1.236, 75, 26, 8], 
    [76, 85, 113, 1.237, 114, 27, 9], 
    [91, 81, 104, 1.041, 56, 40, 10], 
    [84, 39, 60, 0.964, 25, 11, 11], 
    [64, 51, 101, 0.862, 58, 23, 12], 
    [70, 69, 120, 1.198, 65, 36, 13], 
    [77, 105, 178, 2.549, 64, 16, 14], 
    [109, 68, 87, 0.996, 74, 29, 15], 
    [73, 68, 97, 0.905, 51, 34, 16], 
    [54, 27, 47, 0.592, 53, 12, 17], 
    [51, 61, 97, 0.811, 65, 19, 18], 
    [91, 71, 121, 1.374, 43, 18, 19], 
    [73, 102, 182, 2.787, 44, 19, 20], 
    [73, 50, 76, 0.717, 31, 20, 21], 
    [84, 94, 140, 2.238, 68, 18, 22], 
    [93, 77, 104, 1.165, 53, 7, 23], 
    [99, 130, 227, 3.97, 55, 15, 24], 
    [146, 84, 139, 1.094, 40, 17, 25], 
    [113, 108, 137, 1.481, 48, 15, 26], 
    [81, 48, 62, 1.619, 26, 3, 27], 
    [56, 48, 68, 1.336, 37, 9, 28], 
    [82, 92, 174, 3.29, 0, 13, 29], 
    [106, 116, 188, 3.628, 101, 16, 30], 
    [118, 50, 0, 1.383, 76, 11, 31] 
  ] 
  const dataSH = [ 
    [91, 45, 125, 0.82, 34, 23, 1], 
    [65, 27, 78, 0.86, 45, 29, 2], 
    [83, 60, 84, 1.09, 73, 27, 3], 
    [109, 81, 121, 1.28, 68, 51, 4], 
    [106, 77, 114, 1.07, 55, 51, 5], 
    [109, 81, 121, 1.28, 68, 51, 6], 
    [106, 77, 114, 1.07, 55, 51, 7], 
    [89, 65, 78, 0.86, 51, 26, 8], 
    [53, 33, 47, 0.64, 50, 17, 9], 
    [80, 55, 80, 1.01, 75, 24, 10], 
    [117, 81, 124, 1.03, 45, 24, 11], 
    [99, 71, 142, 1.1, 62, 42, 12], 
    [95, 69, 130, 1.28, 74, 50, 13], 
    [116, 87, 131, 1.47, 84, 40, 14], 
    [108, 80, 121, 1.3, 85, 37, 15], 
    [134, 83, 167, 1.16, 57, 43, 16], 
    [79, 43, 107, 1.05, 59, 37, 17], 
    [71, 46, 89, 0.86, 64, 25, 18], 
    [97, 71, 113, 1.17, 88, 31, 19], 
    [84, 57, 91, 0.85, 55, 31, 20], 
    [87, 63, 101, 0.9, 56, 41, 21], 
    [104, 77, 119, 1.09, 73, 48, 22], 
    [87, 62, 100, 1, 72, 28, 23], 
    [168, 128, 172, 1.49, 97, 56, 24], 
    [65, 45, 51, 0.74, 39, 17, 25], 
    [39, 24, 38, 0.61, 47, 17, 26], 
    [39, 24, 39, 0.59, 50, 19, 27], 
    [93, 68, 96, 1.05, 79, 29, 28], 
    [188, 143, 197, 1.66, 99, 51, 29], 
    [174, 131, 174, 1.55, 108, 50, 30], 
    [187, 143, 201, 1.39, 89, 53, 31] 
  ] 
  const lineStyle = { 
    width: 1, 
    opacity: 0.5 
  } 
  
  // 区域数据和名称映射
  const areaData = [
    { name: '浉河区', data: dataBJ },
    { name: '羊山区', data: dataSH },
    { name: '平桥区', data: dataGZ }
  ];
  
  // 更新雷达图数据的函数
  const updateRadarData = () => {
    // 创建区域选择状态
    const selected = {};
    areaData.forEach((area, index) => {
      selected[area.name] = index === currentAreaIndex;
    });
    
    const radarOption = {
      backgroundColor: 'transparent', // 透明背景，与容器背景融合
      title: {
        text: '常见车辆统计',
        left: 'center',
        top: '2%',
        textStyle: {
          color: '#64d2ff',
          fontSize: 14,
          fontWeight: 600
        }
      },
      legend: {
        bottom: 5,
        data: ['浉河区', '羊山区', '平桥区'],
        itemGap: 10,
        itemWidth: 8,
        itemHeight: 8,
        textStyle: {
          color: '#fff',
          fontSize: 12
        },
        selectedMode: 'single',
        selected: selected // 设置当前选中的区域
      },
      radar: {
        indicator: [
          { name: '客车', max: 300 },
          { name: '货车', max: 250 },
          { name: '公交车', max: 300 },
          { name: '电动车', max: 5 },
          { name: '自行车', max: 200 },
          { name: '摩托车', max: 100 }
        ],
        shape: 'circle',
        splitNumber: 5,
        axisName: {
          color: 'rgba(100, 200, 255, 0.8)'
        },
        splitLine: {
          lineStyle: {
            color: [
              'rgba(100, 200, 255, 0.1)',
              'rgba(100, 200, 255, 0.2)',
              'rgba(100, 200, 255, 0.3)',
              'rgba(100, 200, 255, 0.4)',
              'rgba(100, 200, 255, 0.5)',
              'rgba(100, 200, 255, 0.6)'
            ].reverse()
          }
        },
        splitArea: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(100, 200, 255, 0.4)'
          }
        }
      },
      series: [
        {
          name: '浉河区',
          type: 'radar',
          lineStyle: lineStyle,
          data: dataBJ,
          symbol: 'circle',
          symbolSize: 4,
          itemStyle: {
            color: '#F9713C'
          },
          areaStyle: {
            opacity: 0.1
          },
          show: currentAreaIndex === 0
        },
        {
          name: '羊山区',
          type: 'radar',
          lineStyle: lineStyle,
          data: dataSH,
          symbol: 'circle',
          symbolSize: 4,
          itemStyle: {
            color: '#B3E4A1'
          },
          areaStyle: {
            opacity: 0.05
          },
          show: currentAreaIndex === 1
        },
        {
          name: '平桥区',
          type: 'radar',
          lineStyle: lineStyle,
          data: dataGZ,
          symbol: 'circle',
          symbolSize: 4,
          itemStyle: {
            color: 'rgba(100, 200, 255, 0.8)'
          },
          areaStyle: {
            opacity: 0.05
          },
          show: currentAreaIndex === 2
        }
      ]
    };
    
    radarChart.setOption(radarOption);
  };
  
  // 初始更新数据
  updateRadarData();
  
  // 启动区域自动跳转定时器
  areaInterval = setInterval(() => {
    currentAreaIndex = (currentAreaIndex + 1) % areaData.length;
    updateRadarData();
  }, 2000); // 每2秒切换一个区域
  
  // 监听窗口大小变化，自适应调整雷达图
  window.addEventListener('resize', () => {
    radarChart.resize()
  })
}

// 初始化实时车流量统计图表
const initTrafficFlowChart = () => {
  const chartDom = document.getElementById('traffic-flow-chart')
  if (!chartDom) return
  
  trafficFlowChart = echarts.init(chartDom)
  
  // 生成精确到秒的初始数据
  let now = new Date();
  let oneSecond = 1000; // 1秒 = 1000毫秒
  let value = Math.random() * 1000;
  
  // 随机数据生成函数（精确到秒）
  function randomData() {
    now = new Date(+now + oneSecond);
    value = value + Math.random() * 21 - 10;
    return {
      name: now,
      value: [
        now,
        Math.round(value)
      ]
    };
  }
  
  // 生成初始500个数据点
  let data = [];
  for (var i = 0; i < 500; i++) {
    data.unshift(randomData()); // 从前面插入，这样最新的数据在最后
  }
  
  // 图表配置
  const option = {
    backgroundColor: 'transparent', // 透明背景，与容器背景融合
    title: {
      text: '实时车流量统计',
      left: 'center',
      textStyle: {
        color: '#64d2ff',
        fontSize: 14,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        params = params[0];
        var date = new Date(params.value[0]); // 使用params.value[0]而不是params.name获取时间
        return (
          date.getHours() + ':' +
          (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':' +
          (date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()) + ' : ' +
          params.value[1]
        );
      },
      axisPointer: {
        animation: false
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      splitLine: {
        show: false
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(100, 200, 255, 0.6)'
        }
      },
      axisLabel: {
        color: 'rgba(100, 200, 255, 0.8)',
        fontSize: 11,
        interval: 30000, // 只显示间隔30秒的标签
        rotate: 30, // 旋转30度避免拥挤
        formatter: function (value) {
          // 简化时间格式，只显示小时:分钟:秒
          const date = new Date(value);
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`;
        }
      },
      splitNumber: 5
    },
    yAxis: {
      type: 'value',
      boundaryGap: [0, '100%'],
      splitLine: {
        show: false
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(100, 200, 255, 0.6)'
        }
      },
      axisLabel: {
        color: 'rgba(100, 200, 255, 0.8)',
        fontSize: 11
      }
    },
    series: [
      {
        name: '车流量',
        type: 'line',
        showSymbol: false,
        sampling: 'lttb',
        itemStyle: {
          color: 'rgba(100, 210, 255, 0.8)'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(100, 210, 255, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(100, 210, 255, 0.05)'
            }
          ])
        },
        data: data
      }
    ]
  };
  
  trafficFlowChart.setOption(option);
  
  // 每秒更新一次数据
  trafficFlowInterval = setInterval(function () {
    for (var i = 0; i < 1; i++) {
      data.shift();
      data.push(randomData());
    }
    trafficFlowChart.setOption({
      series: [
        {
          data: data
        }
      ]
    });
  }, 1000); // 每秒更新一次
  
  // 监听窗口大小变化，自适应调整图表
  window.addEventListener('resize', () => {
    trafficFlowChart.resize()
  })
}

// 初始化道路流量分布饼图
const initPieChart = () => {
  const chartDom = document.getElementById('pie-chart')
  if (!chartDom) return
  
  pieChart = echarts.init(chartDom)
  
  // 饼图配置 - 使用用户提供的配置并调整背景
  const option = {
    backgroundColor: 'transparent', // 透明背景，与容器背景融合
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)' // 显示名称、数值和百分比
    },
    title: {
      text: '道路流量分布',
      left: 'center',
      top: '2%',
      textStyle: {
        color: '#64d2ff',
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    legend: {
      bottom: '5%', // 将图例移到底部
      left: 'center',
      orient: 'horizontal', // 水平排列图例
      textStyle: {
        color: '#64d2ff', // 与主题一致的文字颜色
        fontSize: 11
      }
    },
    series: [
      {
        name: '道路流量', // 使用中文名称
        type: 'pie',
        radius: ['30%', '55%'], // 调整饼图大小，更大的内边距
        center: ['50%', '48%'], // 调整饼图位置，为底部图例留出空间
        avoidLabelOverlap: true, // 避免标签重叠
        label: {
            show: true, // 显示饼图上的文字标签
            position: 'inside', // 在饼图内部显示
            formatter: '{d}%', // 只显示百分比
            color: '#ffffff', // 使用固定白色文字
            fontSize: 12, // 合适的字体大小
            fontWeight: 'bold', // 加粗文字
            textShadowBlur: 5, // 增强文字阴影效果，增强可读性
            textShadowColor: 'rgba(0, 0, 0, 0.8)' // 加深阴影颜色
          },
        emphasis: {
          label: {
            show: true,
            fontSize: 13, // 适当调整强调时的字体大小
            fontWeight: 'bold',
            color: '#64d2ff',
            position: 'outside' // 强调时标签也显示在外部
          },
          itemStyle: {
            shadowBlur: 15,
            shadowOffsetX: 0,
            shadowColor: 'rgba(100, 210, 255, 0.5)' // 使用主题色阴影
          }
        },
        labelLine: {
          show: false // 去除标签连接线
        },
        itemStyle: {
          // 添加与主题一致的渐变色效果
          color: function(params) {
            const colors = [
              'rgba(100, 210, 255, 0.8)',
              'rgba(100, 255, 180, 0.8)',
              'rgba(255, 210, 100, 0.8)',
              'rgba(255, 150, 100, 0.8)',
              'rgba(200, 150, 255, 0.8)'
            ];
            return colors[params.dataIndex];
          }
        },
        data: [
          { value: 1048, name: '高速公路流量' },
          { value: 735, name: '城市主干道流量' },
          { value: 580, name: '快速路' },
          { value: 484, name: '次要道路流量' },
          { value: 300, name: '其他' }
        ]
      }
    ]
  };
  
  pieChart.setOption(option);
  
  // 动态更新饼图数据的函数
  function updatePieData() {
    // 道路类型数据
    const roadTypes = ['高速公路流量', '城市主干道流量', '快速路', '次要道路流量', '其他'];
    // 生成随机数据，确保总和在3000左右
    let total = 0;
    const newData = roadTypes.map(() => {
      const value = Math.floor(Math.random() * 1200) + 200; // 生成200-1400的随机数
      total += value;
      return value;
    });
    
    // 归一化数据，保持总和一致
    const normalizedData = newData.map(value => Math.round(value / total * 3000));
    
    // 更新饼图数据
    const updatedData = roadTypes.map((name, index) => ({
      name: name,
      value: normalizedData[index]
    }));
    
    pieChart.setOption({
      series: [
        {
          data: updatedData
        }
      ]
    });
  }
  
  // 设置定时器，每5秒更新一次数据
  setInterval(updatePieData, 5000);
}

// 初始化周流量柱状图
const initWeekFlowChart = () => {
  const chartDom = document.getElementById('week-flow-chart')
  if (!chartDom) return
  
  weekFlowChart = echarts.init(chartDom)
  
  // 柱状图配置 - 与主题一致的样式
  const option = {
    backgroundColor: 'transparent', // 透明背景，与容器背景融合
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(0, 20, 60, 0.8)', // 半透明深色背景
      borderColor: 'rgba(100, 210, 255, 0.5)', // 主题色边框
      textStyle: {
        color: '#ffffff' // 白色文字
      }
    },
    title: {
      text: '周流量统计',
      left: 'center',
      top: '5%',
      textStyle: {
        color: '#64d2ff', // 与主题一致的文字颜色
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '5%',
      top: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      axisLine: {
        lineStyle: {
          color: 'rgba(100, 210, 255, 0.5)' // 主题色轴线
        }
      },
      axisLabel: {
        color: '#64d2ff', // 主题色标签
        fontSize: 12
      },
      axisTick: {
        lineStyle: {
          color: 'rgba(100, 210, 255, 0.3)' // 主题色刻度线
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: 'rgba(100, 210, 255, 0.5)' // 主题色轴线
        }
      },
      axisLabel: {
        color: '#64d2ff', // 主题色标签
        fontSize: 12
      },
      axisTick: {
        lineStyle: {
          color: 'rgba(100, 210, 255, 0.3)' // 主题色刻度线
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(100, 210, 255, 0.1)' // 主题色网格线
        }
      }
    },
    series: [
      {
        data: [9637, 6402, 5155, 6920, 8250, 4901, 11570],
        type: 'bar',
        barWidth: '40%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(100, 210, 255, 0.8)' }, // 顶部透明主题色
            { offset: 1, color: 'rgba(100, 210, 255, 0.4)' } // 底部更透明
          ]),
          borderRadius: [5, 5, 0, 0] // 顶部圆角
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(100, 210, 255, 1)' }, // 强调时更不透明
              { offset: 1, color: 'rgba(100, 210, 255, 0.6)' }
            ])
          }
        }
      }
    ]
  }
  
  weekFlowChart.setOption(option)
  
  // 监听窗口大小变化，自适应调整图表
  window.addEventListener('resize', () => {
    weekFlowChart.resize()
  })
}  
  // 监听窗口大小变化，自适应调整图表
  window.addEventListener('resize', () => {
    pieChart.resize()
  })

// 组件卸载时销毁地图和清除定时器
onUnmounted(() => {
  if (map) {
    map.destroy()
  }
  
  // 清除滚动定时器
  if (scrollTimer) {
    clearInterval(scrollTimer)
  }
  
  // 清除雷达图定时器和实例
  if (areaInterval) {
    clearInterval(areaInterval)
  }
  
  if (radarChart) {
    radarChart.dispose()
  }
  
  // 清除实时车流量统计图表定时器和实例
  if (trafficFlowInterval) {
    clearInterval(trafficFlowInterval)
  }
  
  if (trafficFlowChart) {
    trafficFlowChart.dispose()
  }
  
  // 清除周流量柱状图实例
  if (weekFlowChart) {
    weekFlowChart.dispose()
  }
})
</script>

<style scoped>
.traffic-map {
  width: 100%;
  height: 100vh;
  background-image: url('@/backgroundpicture/mapbg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h2 {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  margin: 0;
  padding: 12px 24px;
  background: rgba(20, 33, 61, 0.8);
  border-radius: 25px;
  z-index: 100;
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(100, 200, 255, 0.3);
  box-shadow: 0 4px 20px rgba(100, 200, 255, 0.2);
}

.map-container {
  position: relative;
  width: 80%;
  height: 500px;
  margin: 40px auto 0;
  overflow: hidden;
  z-index: 1;
  border-radius: 10px;
}

.map {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  overflow: hidden;
}

#amap-container {
  width: 100%;
  height: 100%;
  background-color: blue;
}

.legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(20, 33, 61, 0.7);
  border-radius: 15px;
  padding: 15px;
  backdrop-filter: blur(12px);
  width: 220px;
  z-index: 100;
  box-shadow: 0 5px 25px rgba(0, 140, 255, 0.2);
  border: 1px solid rgba(100, 200, 255, 0.3);
}

.legend h3 {
  margin: 0 0 12px 0;
  text-align: center;
  color: #64d2ff;
  font-size: 1rem;
  font-weight: 600;
  text-shadow: 0 1px 5px rgba(100, 200, 255, 0.5);
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: white;
  font-size: 0.85rem;
  opacity: 0.9;
}

.legend-color {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  margin-right: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.road-status {
  position: absolute;
  top: 90px;
  left: 0;
  background: linear-gradient(to right, rgba(20, 33, 61, 0.2), rgba(20, 33, 61, 0.7), rgba(20, 33, 61, 0.5));
  border-radius: 15px;
  padding: 15px;
  backdrop-filter: blur(12px);
  width: 320px;
  max-height: 40vh;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 5px 25px rgba(0, 140, 255, 0.2);
  border: 1px solid rgba(100, 200, 255, 0.1);
}

.road-status h3 {
  margin: 0 0 12px 0;
  text-align: center;
  color: #64d2ff;
  font-size: 1rem;
  font-weight: 600;
  text-shadow: 0 1px 5px rgba(100, 200, 255, 0.5);
}

/* 表头容器 - 完全独立的块 */
.header-container {
  margin-bottom: 5px;
  border-bottom: 2px solid rgba(100, 200, 255, 0.5);
  background-color: rgba(0, 20, 60, 0.7);
  border: 1px solid rgba(100, 210, 255, 0.2);
  overflow: hidden;
}

.header-container table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.8rem;
  table-layout: fixed;
}

/* 雷达图容器样式 */
.radar-chart-container {
  position: absolute;
  top: 90px;
  right: 0;
  background: linear-gradient(to left, rgba(20, 33, 61, 0.2), rgba(20, 33, 61, 0.7), rgba(20, 33, 61, 0.5));
  border-radius: 15px;
  padding: 15px;
  backdrop-filter: blur(12px);
  width: 320px;
  height: 280px;
  z-index: 100;
  box-shadow: 0 5px 25px rgba(0, 140, 255, 0.2);
  border: 1px solid rgba(100, 200, 255, 0.1);
}

.radar-chart {
  width: 100%;
  height: 100%;
}

/* 道路流量分布饼图容器样式 */
.pie-chart-container {
  position: absolute;
  top: calc(90px + 280px + 3px); /* 雷达图下方3px */
  right: 0;
  background: linear-gradient(to left, rgba(20, 33, 61, 0.2), rgba(20, 33, 61, 0.7), rgba(20, 33, 61, 0.5));
  border-radius: 15px;
  padding: 15px;
  backdrop-filter: blur(12px);
  width: 320px;
  height: 280px;
  z-index: 100;
  box-shadow: 0 5px 25px rgba(0, 140, 255, 0.2);
  border: 1px solid rgba(100, 200, 255, 0.1); /* 弱化边框，降低透明度 */
}

.pie-chart {
  width: 100%;
  height: 100%;
}

/* 实时车流量统计图表容器样式 */
.traffic-flow-container {
  position: absolute;
  top: calc(90px + 40vh + 3px); /* 道路状态表格下方，增加一丢丢间距 */
  left: 0;
  background: linear-gradient(to right, rgba(20, 33, 61, 0.2), rgba(20, 33, 61, 0.7), rgba(20, 33, 61, 0.5));
  border-radius: 15px;
  padding: 15px;
  backdrop-filter: blur(12px);
  width: 320px;
  height: 220px;
  z-index: 100;
  box-shadow: 0 5px 25px rgba(0, 140, 255, 0.2);
  border: 1px solid rgba(100, 200, 255, 0.1); /* 弱化边框，降低透明度 */
}

.traffic-flow-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

/* 表体容器 - 完全独立的块 */
.table-container {
  max-height: calc(35vh - 80px);
  overflow-y: auto;
  background-color: rgba(0, 20, 60, 0.7);
  border: 1px solid rgba(100, 210, 255, 0.2);
  overflow: hidden;
}

/* 表体表格样式 */
.table-container table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.8rem;
  table-layout: fixed;
}

/* 激活行样式 - 增强高亮效果 */
.road-row.active {
  background: rgba(100, 210, 255, 0.25);
  box-shadow: inset 0 0 15px rgba(100, 210, 255, 0.4);
  font-weight: 600;
  transition: all 0.3s ease;
  z-index: 10;
  position: relative;
  border-radius: 5px;
  padding: 5px 0;
}

/* 表头样式 */
th {
  padding: 12px 8px;
  text-align: left;
  background: rgba(100, 200, 255, 0.2);
  font-weight: 600;
  color: #64d2ff;
  border-bottom: 2px solid rgba(100, 200, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 数据单元格样式 */
td {
  padding: 9px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(100, 200, 255, 0.2);
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 调整列宽 */
th:nth-child(1), td:nth-child(1) { width: 40%; }
th:nth-child(2), td:nth-child(2) { width: 25%; }
th:nth-child(3), td:nth-child(3) { width: 17%; }
th:nth-child(4), td:nth-child(4) { width: 18%; }
.road-row {
  transition: background-color 0.2s ease;
}

.road-row:hover {
  background: rgba(100, 200, 255, 0.15);
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.2s ease;
}

.status-badge.smooth {
  background: rgba(76, 175, 80, 0.4);
  color: #a8e6cf;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.status-badge.slow {
  background: rgba(255, 193, 7, 0.4);
  color: #fff9c4;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}

.status-badge.congested {
  background: rgba(244, 67, 54, 0.4);
  color: #ffccbc;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}


/* 周流量柱状图容器样式 */
.week-flow-container {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%; /* 减小宽度，向中间集中 */
  height: 250px; /* 适当减小高度 */
  background: rgba(0, 20, 60, 0.6); /* 减小不透明度，显示背景图片 */
  border: 1px solid rgba(100, 210, 255, 0.1); /* 弱化边框，降低透明度 */
  border-radius: 8px; /* 所有角都有圆角 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  z-index: 50; /* 提高z-index，避免被其他图表覆盖 */
}

/* 周流量柱状图样式 */
.week-flow-chart {
  width: 100%;
  height: 100%;
}


</style>
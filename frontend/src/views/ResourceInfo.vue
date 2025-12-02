<template>
  <div class="resource-info">
    <div class="header-section">
      <h1>资源信息管理</h1>
      <div class="search-box">
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索地点、资源名称..."
          @keyup.enter="searchLocation"
        />
        <button @click="searchLocation" class="search-button">搜索</button>
      </div>
    </div>
    
    <div class="map-and-controls">
      <div class="map-controls">
        <div class="layer-controls">
          <h3>图层控制</h3>
          <label class="control-item">
            <input 
              v-model="showPoliceMarkers" 
              type="checkbox" 
              @change="togglePoliceMarkers"
            />
            <span>警力资源</span>
          </label>
          <label class="control-item">
            <input 
              v-model="showConstructionMarkers" 
              type="checkbox" 
              @change="toggleConstructionMarkers"
            />
            <span>施工区域</span>
          </label>
          <label class="control-item">
            <input 
              v-model="showTrafficJamAreas" 
              type="checkbox" 
              @change="toggleTrafficJamAreas"
            />
            <span>交通拥堵</span>
          </label>
        </div>
        
        <div class="function-controls">
          <button @click="locateCurrentPosition" class="control-button locate-button">
             定位到当前位置
          </button>
          <button @click="fitAllMarkers" class="control-button">
             显示所有资源
          </button>
          <button @click="clearAllInfoWindows" class="control-button">
             关闭信息窗口
          </button>
        </div>
        
        <div class="traffic-info">
          <h3>实时交通状况</h3>
          <div class="traffic-level">
            <div class="level-item">
              <div class="level-indicator smooth"></div>
              <span>畅通</span>
            </div>
            <div class="level-item">
              <div class="level-indicator slow"></div>
              <span>缓行</span>
            </div>
            <div class="level-item">
              <div class="level-indicator congested"></div>
              <span>拥堵</span>
            </div>
          </div>
        </div>
      </div>
      
      <div id="map-container" class="map-container"></div>
    </div>
    
    <div v-if="searchResults.length > 0" class="search-results">
      <h3>搜索结果 ({{ searchResults.length }})</h3>
      <div class="results-list">
        <div 
          v-for="result in searchResults" 
          :key="result.id"
          class="result-item"
          @click="selectSearchResult(result)"
        >
          <span class="result-name">{{ result.name }}</span>
          <span class="result-type">{{ result.type }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AMapLoader from '@amap/amap-jsapi-loader'
import shiheImage from '@/source/ShiHePlice.jpg'
import yangshanImage from '@/source/YangShanPolice.jpg'
import pingqiaoImage from '@/source/PingQiaoPolice.jpg'

export default {
  name: 'ResourceInfo',
  data() {
      return {
        map: null,
        policeMarkers: [],
        constructionMarkers: [],
        trafficJams: [], // 存储交通拥堵区域多边形
        AMap: null,
        mapLoading: false,
        mapLoaded: false,
        mapObserver: null,
        // 控制开关
        showPoliceMarkers: true,
        showConstructionMarkers: true,
        showTrafficJamAreas: true,
        // 搜索相关
        searchKeyword: '',
        searchResults: [],
        // 实时路况图层
        trafficLayer: null
      }
    },
  mounted() {
      // 使用Intersection Observer进行懒加载，只有当地图容器进入视口才加载地图
      const mapContainer = document.getElementById('map-container');
      if (mapContainer) {
        this.mapObserver = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting && !this.mapLoading && !this.mapLoaded) {
              this.mapLoading = true;
              this.initMap();
              this.mapObserver.disconnect(); // 只加载一次
            }
          });
        }, { threshold: 0.1 }); // 当10%的元素可见时触发
        
        this.mapObserver.observe(mapContainer);
      } else {
        // 如果容器不存在，回退到立即加载
        this.initMap();
      }
    },
  methods: {
    initMap() {
      // 添加加载指示器
      const mapContainer = document.getElementById('map-container');
      if (mapContainer) {
        mapContainer.innerHTML = '<div class="map-loading">地图加载中...</div>';
      }
      
      AMapLoader.load({
        key: 'YOUR_MAP_API_KEY', // 请替换为实际的地图API密钥
        version: '2.0',
        plugins: ['AMap.ToolBar', 'AMap.Scale', 'AMap.MapType']
      }).then(() => {
        this.AMap = window.AMap; // 保存AMap实例以便后续使用
        
        // 创建地图实例，优化配置
        this.map = new window.AMap.Map('map-container', {
          zoom: 11,
          center: [114.075031, 32.123274], // 河南信阳坐标
          viewMode: '3D',
          mapStyle: 'amap://styles/darkblue', // 设置为深蓝色（科技感）样式
          defaultLayer: 'base', // 使用默认的矢量底图图层
          resizeEnable: true,
          pitch: 0, // 保持2D视角以提高性能
          showLabel: true,
          buildingAnimation: false, // 禁用建筑动画以提高性能
          animateEnable: true,
          // 性能优化配置
          layers: [new window.AMap.TileLayer()], // 只加载基础图层
          optimizePanAnimation: true // 优化平移动画
        })
        
        // 添加实时路况图层
        this.trafficLayer = new window.AMap.TileLayer.Traffic({
          zIndex: 1000,
          autoRefresh: true,
          interval: 180,
          isOutline: false
        })
        this.trafficLayer.setMap(this.map)
        
        // 添加地图控件
        this.map.plugin('AMap.MapType', () => {
          const mapTypeControl = new window.AMap.MapType({
            defaultType: 0, // 默认显示标准图层
            showRoadNet: false, // 禁用路网显示
            position: 'RT', // 右上角位置
            offset: [20, -100] // 向右偏移10px，向上偏移50px
          })
          this.map.addControl(mapTypeControl)
        })
        
        // 批量添加地图控件
        window.AMap.plugin(['AMap.ToolBar', 'AMap.Scale'], () => {
          const controls = [];
          if (window.AMap.ToolBar) {
            controls.push(new window.AMap.ToolBar({
              liteStyle: true // 简洁风格
            }))
          }
          if (window.AMap.Scale) {
            controls.push(new window.AMap.Scale())
          }
          
          // 正确方式：逐个添加控件
          controls.forEach(control => {
            this.map.addControl(control);
          });
        })
        
        // 使用requestAnimationFrame确保DOM更新后再添加标记
        requestAnimationFrame(() => {
          // 批量添加各类标记
          this.addAllMarkers();
          
          this.mapLoaded = true;
          this.mapLoading = false;
        });
      }).catch(err => {
        console.error('地图初始化失败:', err);
        this.mapLoading = false;
        // 显示错误信息
        if (mapContainer) {
          mapContainer.innerHTML = '<div class="map-error">地图加载失败，请刷新页面重试</div>';
        }
      })
    },
    
    // 批量添加所有标记，减少多次调用带来的性能消耗
    addAllMarkers() {
      // 使用setTimeout分散执行，避免阻塞主线程
      setTimeout(() => {
        this.addPoliceMarkers();
      }, 100);
      
      setTimeout(() => {
        this.addConstructionMarkers();
      }, 200);
      
      setTimeout(() => {
        this.addTrafficJamAreas();
        // 交通拥堵区域添加完成后增强交互体验
        setTimeout(() => {
          this.enhanceTrafficJamInteraction();
        }, 100);
      }, 300);
    },
    addPoliceMarkers() {
      // 清除已存在的警力标记
      this.policeMarkers.forEach(marker => {
        marker.setMap(null)
      })
      this.policeMarkers = []
      
      // 模拟警力资源数据
      const policeResources = [
        { id: 1, name: '信阳市公安局', address: '信阳市浉河区东方红大道', longitude: 114.075031, latitude: 32.123274, type: '公安局', strength: '100人' },
        { id: 2, name: '浉河区分局', address: '信阳市浉河区民权路', longitude: 114.083567, latitude: 32.119876, type: '分局', strength: '50人' },
        { id: 3, name: '平桥区分局', address: '信阳市平桥区中心大道', longitude: 114.102345, latitude: 32.126789, type: '分局', strength: '60人' },
        { id: 4, name: '羊山派出所', address: '信阳市羊山新区新五大道', longitude: 114.098765, latitude: 32.135432, type: '派出所', strength: '30人' },
        { id: 5, name: '南湾湖派出所', address: '信阳市南湾湖风景区', longitude: 114.034567, latitude: 32.098765, type: '派出所', strength: '25人' }
      ]
      
      // 创建信息窗口实例（复用，提高性能）
      const infoWindow = new window.AMap.InfoWindow({
        offset: new window.AMap.Pixel(0, -40), // 调整信息窗口位置
        closeWhenClickMap: true, // 点击地图关闭信息窗口
        autoMove: true // 自动调整地图视野以完整显示信息窗口
      })
      
      // 添加警力资源标记
      policeResources.forEach(resource => {
        // 为特定派出所设置自定义图标
        let icon = '//webapi.amap.com/theme/v1.3/markers/n/mark_b.png';
        let isCustomIcon = false;
        
        if (resource.name === '浉河区分局') {
          icon = new window.AMap.Icon({
            size: new window.AMap.Size(60, 60), // 增大图标尺寸
            imageSize: new window.AMap.Size(60, 60), // 增大图片尺寸
            image: shiheImage // 使用导入的图片
          });
          isCustomIcon = true;
        } else if (resource.name === '羊山派出所') {
          icon = new window.AMap.Icon({
            size: new window.AMap.Size(60, 60), // 增大图标尺寸
            imageSize: new window.AMap.Size(60, 60), // 增大图片尺寸
            image: yangshanImage // 使用导入的图片
          });
          isCustomIcon = true;
        } else if (resource.name === '平桥区分局') {
          icon = new window.AMap.Icon({
            size: new window.AMap.Size(60, 60), // 增大图标尺寸
            imageSize: new window.AMap.Size(60, 60), // 增大图片尺寸
            image: pingqiaoImage // 使用导入的图片
          });
          isCustomIcon = true;
        }
        
        // 创建动画标记
        const marker = new window.AMap.Marker({
          position: [resource.longitude, resource.latitude],
          icon: icon,
          title: resource.name,
          map: this.map,
          animation: 'AMAP_ANIMATION_DROP', // 添加掉落动画
          clickable: true,
          // 优化交互配置
          cursor: 'pointer',
          bubble: true
        })
        
        // 保存原始图标尺寸，用于悬停效果
        const originalIcon = icon;
        
        // 添加鼠标悬停效果
        marker.on('mouseover', () => {
          // 显示自定义标签 - 使用Marker实现标签功能
          const labelContent = document.createElement('div');
          labelContent.className = 'custom-label';
          labelContent.innerText = resource.name;
          
          const label = new window.AMap.Marker({
            content: labelContent,
            offset: new window.AMap.Pixel(0, -60),
            position: marker.getPosition(),
            map: this.map,
            zIndex: 1001
          });
          marker._hoverLabel = label;
          
          // 放大图标效果
          if (isCustomIcon) {
            const hoverIcon = new window.AMap.Icon({
              size: new window.AMap.Size(70, 70), // 放大图标尺寸
              imageSize: new window.AMap.Size(70, 70),
              image: icon.image
            });
            marker.setIcon(hoverIcon);
          } else {
            // 非自定义图标也添加放大效果
            const defaultHoverIcon = new window.AMap.Icon({
              size: new window.AMap.Size(40, 50),
              imageSize: new window.AMap.Size(40, 50),
              image: '//webapi.amap.com/theme/v1.3/markers/n/mark_b.png'
            });
            marker.setIcon(defaultHoverIcon);
          }
          
          // 轻微上浮效果
          marker.setTop(true);
        })
        
        marker.on('mouseout', () => {
          // 移除标签
          if (marker._hoverLabel) {
            this.map.remove(marker._hoverLabel);
            marker._hoverLabel = null;
          }
          
          // 恢复原始图标
          marker.setIcon(originalIcon);
          marker.setTop(false);
        })
        
        // 添加点击事件，显示信息窗口
        marker.on('click', () => {
          // 动态设置信息窗口内容
          const content = `
            <div class="info-window">
              <div class="info-header">
                <h3>${resource.name}</h3>
              </div>
              <div class="info-body">
                <p class="info-address"><strong>地址:</strong> ${resource.address}</p>
                <p class="info-type"><strong>类型:</strong> ${resource.type}</p>
                <p class="info-strength"><strong>人员配备:</strong> ${resource.strength}</p>
                <div class="info-footer">
                  <button class="info-button">查看详情</button>
                </div>
              </div>
            </div>
          `;
          
          infoWindow.setContent(content);
          infoWindow.open(this.map, marker.getPosition());
          
          // 添加点击后的视觉反馈
          marker.setAnimation('AMAP_ANIMATION_BOUNCE');
          setTimeout(() => {
            marker.setAnimation(null);
          }, 1000);
          
          // 绑定信息窗口按钮事件
          this.bindInfoWindowEvents(resource.name);
        })
        
        this.policeMarkers.push(marker)
      })
      
      console.log('警力资源标记添加完成')
    },
    
    // 为信息窗口按钮添加事件监听
    bindInfoWindowEvents(resourceName) {
      setTimeout(() => {
        const buttons = document.querySelectorAll('.info-button');
        buttons.forEach(button => {
          button.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止事件冒泡
            this.showResourceDetails(resourceName);
          });
        });
      }, 100);
    },
    
    // 显示资源详情
    showResourceDetails(resourceName) {
      // 这里可以实现跳转到详情页面或显示更详细的信息弹窗
      console.log('显示资源详情:', resourceName);
      alert(`查看${resourceName}的详细信息`);
    },
    
    // 切换警力标记显示
    togglePoliceMarkers() {
      this.policeMarkers.forEach(marker => {
        marker.setMap(this.showPoliceMarkers ? this.map : null);
      });
    },
    
    // 切换施工标记显示
    toggleConstructionMarkers() {
      this.constructionMarkers.forEach(marker => {
        marker.setMap(this.showConstructionMarkers ? this.map : null);
        // 处理脉冲动画
        if (marker._pulseCircle) {
          marker._pulseCircle.setMap(this.showConstructionMarkers ? this.map : null);
        }
      });
    },
    
    // 切换交通拥堵区域显示
    toggleTrafficJamAreas() {
      this.trafficJams.forEach(area => {
        area.setMap(this.showTrafficJamAreas ? this.map : null);
      });
      // 控制实时路况图层
      if (this.trafficLayer) {
        this.trafficLayer.setMap(this.showTrafficJamAreas ? this.map : null);
      }
    },
    
    // 定位到当前位置
    locateCurrentPosition() {
      if (!this.map) return;
      
      // 创建定位控件
      const geolocation = new window.AMap.Geolocation({
        enableHighAccuracy: true, // 是否使用高精度定位，默认:true
        timeout: 10000,           // 超过10秒后停止定位，默认：5s
        maximumAge: 0,            // 定位结果缓存0毫秒，默认：0
        convert: true,            // 自动偏移坐标，偏移后的坐标为高德坐标，默认：true
        showButton: false,        // 显示定位按钮，默认：true
        buttonPosition: 'RB',     // 定位按钮停靠位置，默认：'LB'
        buttonOffset: new window.AMap.Pixel(10, 20), // 定位按钮与设置的停靠位置的偏移量，默认：Pixel(10, 20)
        showMarker: true,         // 定位成功后在定位到的位置显示点标记，默认：true
        showCircle: true,         // 定位成功后用圆圈表示定位精度范围，默认：true
        panToLocation: true,      // 定位成功后将定位到的位置作为地图中心点，默认：true
        zoomToAccuracy: true      // 定位成功后调整地图视野范围使定位位置及精度范围视野内可见，默认：false
      });
      
      // 添加到地图
      this.map.addControl(geolocation);
      
      // 监听定位成功事件
      geolocation.getCurrentPosition();
      window.AMap.event.addListener(geolocation, 'complete', (data) => {
        console.log('定位成功:', data);
        // 定位成功后可以自定义处理
      });
      
      // 监听定位失败事件
      window.AMap.event.addListener(geolocation, 'error', (err) => {
        console.log('定位失败:', err);
        alert('定位失败，请检查定位权限设置');
      });
    },
    
    // 调整地图视野以显示所有标记
    fitAllMarkers() {
      if (!this.map) return;
      
      const positions = [];
      
      // 收集所有显示中的标记位置
      if (this.showPoliceMarkers) {
        this.policeMarkers.forEach(marker => {
          positions.push(marker.getPosition());
        });
      }
      
      if (this.showConstructionMarkers) {
        this.constructionMarkers.forEach(marker => {
          positions.push(marker.getPosition());
        });
      }
      
      // 如果有标记位置，调整视野
      if (positions.length > 0) {
        const bounds = new window.AMap.Bounds(positions);
        this.map.setFitView([bounds], true, 100);
      } else {
        alert('没有显示中的标记');
      }
    },
    
    // 关闭所有信息窗口
    clearAllInfoWindows() {
      if (this.map) {
        this.map.clearInfoWindow();
      }
    },
    
    // 搜索地点
    searchLocation() {
      if (!this.searchKeyword.trim()) return;
      
      // 模拟搜索功能
      const keyword = this.searchKeyword.toLowerCase();
      const allResources = [
        // 警力资源
        ...this.policeMarkers.map((marker, index) => ({
          id: `police-${index}`,
          name: marker.getTitle(),
          position: marker.getPosition(),
          type: '警力资源'
        })),
        // 施工信息
        ...this.constructionMarkers.map((marker, index) => ({
          id: `construction-${index}`,
          name: marker.getTitle(),
          position: marker.getPosition(),
          type: '施工区域'
        }))
      ];
      
      // 过滤搜索结果
      this.searchResults = allResources.filter(resource => 
        resource.name.toLowerCase().includes(keyword)
      );
      
      console.log('搜索结果:', this.searchResults);
    },
    
    // 选择搜索结果
    selectSearchResult(result) {
      if (!this.map || !result.position) return;
      
      // 移动地图到选择的位置
      this.map.panTo(result.position, true);
      
      // 设置一个短暂的动画效果
      const marker = new window.AMap.Marker({
        position: result.position,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(30, 30),
          imageSize: new window.AMap.Size(30, 30),
          image: '//webapi.amap.com/theme/v1.3/markers/n/mark_b.png'
        }),
        animation: 'AMAP_ANIMATION_BOUNCE'
      });
      
      marker.setMap(this.map);
      
      // 3秒后移除标记
      setTimeout(() => {
        marker.setMap(null);
      }, 3000);
    },

    addConstructionMarkers() {
      // 清除已存在的施工标记
      this.constructionMarkers.forEach(marker => {
        marker.setMap(null)
      })
      this.constructionMarkers = []
      
      // 模拟施工信息数据
      const constructionInfo = [
        { id: 1, name: '东方红大道道路维修', address: '信阳市浉河区东方红大道', longitude: 114.078901, latitude: 32.124567, type: '道路维修', startTime: '2023-06-01', endTime: '2023-06-15', status: '进行中' },
        { id: 2, name: '羊山大道扩建工程', address: '信阳市羊山新区羊山大道', longitude: 114.095678, latitude: 32.132345, type: '道路扩建', startTime: '2023-05-10', endTime: '2023-07-30', status: '进行中' },
        { id: 3, name: '南湾湖景区道路改造', address: '信阳市南湾湖风景区', longitude: 114.045678, latitude: 32.089012, type: '道路改造', startTime: '2023-06-10', endTime: '2023-08-10', status: '进行中' },
        { id: 4, name: '新五大道管网铺设', address: '信阳市羊山新区新五大道', longitude: 114.092345, latitude: 32.140123, type: '管网铺设', startTime: '2023-06-05', endTime: '2023-06-25', status: '进行中' },
        { id: 5, name: '平西路绿化工程', address: '信阳市平桥区平西路', longitude: 114.105678, latitude: 32.131234, type: '绿化工程', startTime: '2023-06-15', endTime: '2023-07-05', status: '进行中' }
      ]
      
      // 创建施工区域自定义图标
      const constructionIcon = new window.AMap.Icon({
        size: new window.AMap.Size(36, 36),
        imageSize: new window.AMap.Size(36, 36),
        image: '//webapi.amap.com/theme/v1.3/markers/n/mark_r.png'
      });
      
      // 创建复用的信息窗口
      const infoWindow = new window.AMap.InfoWindow({
        offset: new window.AMap.Pixel(0, -40),
        closeWhenClickMap: true
      });
      
      // 添加施工区域标记
      constructionInfo.forEach(info => {
        // 创建带有脉冲动画的标记
        const marker = new window.AMap.Marker({
          position: [info.longitude, info.latitude],
          icon: constructionIcon,
          title: info.name,
          map: this.map,
          animation: 'AMAP_ANIMATION_DROP',
          cursor: 'pointer'
        });
        
        // 创建脉冲动画效果（通过添加一个动态更新的圆形覆盖物）
        this.createPulseAnimation(marker, '#ff4d4f', 3);
        
        // 鼠标悬停效果
        marker.on('mouseover', () => {
          const labelContent = document.createElement('div');
          labelContent.className = 'construction-label';
          labelContent.innerText = info.name;
          
          const label = new window.AMap.Marker({
            content: labelContent,
            offset: new window.AMap.Pixel(0, -40),
            position: marker.getPosition(),
            map: this.map,
            zIndex: 1001
          });
          marker._hoverLabel = label;
          
          // 放大图标效果
          const hoverIcon = new window.AMap.Icon({
            size: new window.AMap.Size(44, 44),
            imageSize: new window.AMap.Size(44, 44),
            image: '//webapi.amap.com/theme/v1.3/markers/n/mark_r.png'
          });
          marker.setIcon(hoverIcon);
          marker.setTop(true);
        });
        
        marker.on('mouseout', () => {
          if (marker._hoverLabel) {
            this.map.remove(marker._hoverLabel);
            marker._hoverLabel = null;
          }
          
          // 恢复原始图标
          marker.setIcon(constructionIcon);
          marker.setTop(false);
        });
        
        // 点击事件
        marker.on('click', () => {
          const content = `
            <div class="construction-info-window">
              <h3 class="construction-title">${info.name}</h3>
              <p class="construction-address"><strong>地址:</strong> ${info.address}</p>
              <p class="construction-type"><strong>类型:</strong> ${info.type}</p>
              <div class="construction-time">
                <p><strong>施工周期:</strong> ${info.startTime} 至 ${info.endTime}</p>
              </div>
              <p class="construction-status"><strong>状态:</strong> <span class="status-badge">${info.status}</span></p>
              <div class="construction-warning">
                <span class="warning-icon">⚠️</span>
                <span>请注意绕行</span>
              </div>
            </div>
          `;
          
          infoWindow.setContent(content);
          infoWindow.open(this.map, marker.getPosition());
          
          // 添加点击动画
          marker.setAnimation('AMAP_ANIMATION_BOUNCE');
          setTimeout(() => {
            marker.setAnimation(null);
          }, 800);
        });
        
        this.constructionMarkers.push(marker);
      });
      
      console.log('施工信息标记添加完成')
    },
    
    // 创建脉冲动画效果
    createPulseAnimation(marker, color, duration) {
      let radius = 0;
      let circle = null;
      
      const animate = () => {
        if (!marker.getMap()) return; // 标记已移除则停止动画
        
        if (circle) {
          this.map.remove(circle);
        }
        
        radius += 5;
        if (radius > 50) {
          radius = 0;
        }
        
        circle = new window.AMap.Circle({
          center: marker.getPosition(),
          radius: radius,
          strokeColor: color,
          strokeOpacity: 0.8 - radius/50,
          strokeWeight: 2,
          fillColor: color,
          fillOpacity: 0.2 - radius/250,
          map: this.map
        });
        
        // 保存引用以便后续清理
        marker._pulseCircle = circle;
        
        setTimeout(animate, (duration * 1000) / 10);
      };
      
      animate();
    },

    addTrafficJamAreas() {
      // 清除已存在的拥堵区域
      this.trafficJams.forEach(area => {
        area.setMap(null)
      })
      this.trafficJams = []
      
      // 模拟交通拥堵区域数据（多边形坐标点）
      const jamAreas = [
        {
          id: 1,
          name: '东方红大道拥堵区',
          description: '早晚高峰期严重拥堵',
          points: [[114.072345, 32.124567], [114.078901, 32.125678], [114.077654, 32.128901], [114.071234, 32.127890]],
          level: '严重拥堵' // 拥堵等级：严重拥堵、中度拥堵、轻度拥堵
        },
        {
          id: 2,
          name: '民权路拥堵区',
          description: '商业区人流量大，交通拥堵',
          points: [[114.080123, 32.120123], [114.084567, 32.121234], [114.083456, 32.123456], [114.079012, 32.122345]],
          level: '中度拥堵'
        },
        {
          id: 3,
          name: '羊山大道拥堵区',
          description: '道路施工导致拥堵',
          points: [[114.094321, 32.131234], [114.098765, 32.132345], [114.097654, 32.134567], [114.093210, 32.133456]],
          level: '中度拥堵'
        },
        {
          id: 4,
          name: '新五大道拥堵区',
          description: '学校周边，上下学高峰期拥堵',
          points: [[114.090123, 32.139876], [114.094567, 32.140987], [114.093456, 32.143123], [114.088901, 32.142012]],
          level: '轻度拥堵'
        },
        {
          id: 5,
          name: '南京路拥堵区',
          description: '批发市场周边，货运车辆多',
          points: [[114.085678, 32.135432], [114.089012, 32.136543], [114.087901, 32.138765], [114.084567, 32.137654]],
          level: '严重拥堵'
        }
      ]
      
      // 添加拥堵区域多边形
      jamAreas.forEach(area => {
        // 根据拥堵等级设置不同的颜色和透明度
        let fillColor = '#FF0000'; // 默认红色（严重拥堵）
        let fillOpacity = 0.5;
        
        switch(area.level) {
          case '中度拥堵':
            fillColor = '#FFA500'; // 橙色
            fillOpacity = 0.4;
            break;
          case '轻度拥堵':
            fillColor = '#FFFF00'; // 黄色
            fillOpacity = 0.3;
            break;
        }
        
        // 创建多边形
        const polygon = new window.AMap.Polygon({
          path: area.points,
          strokeColor: fillColor,
          strokeOpacity: 1,
          strokeWeight: 2,
          fillColor: fillColor,
          fillOpacity: fillOpacity
        })
        
        // 添加信息窗口
        const infoWindow = new window.AMap.InfoWindow({
          content: `
            <div style="padding: 10px;">
              <h3 style="margin: 0 0 10px 0;">${area.name}</h3>
              <p><strong>描述:</strong> ${area.description}</p>
              <p><strong>拥堵等级:</strong> ${area.level}</p>
            </div>
          `,
          size: new window.AMap.Size(300, 0)
        })
        
        // 添加点击事件
        polygon.on('click', () => {
          // 计算多边形中心点
          const center = this.calculatePolygonCenter(area.points)
          infoWindow.open(this.map, center)
        })
        
        // 添加到地图
        polygon.setMap(this.map)
        this.trafficJams.push(polygon)
      })
      
      console.log('交通拥堵区域添加完成')
    },
    
    // 计算多边形中心点
    calculatePolygonCenter(points) {
      let x = 0, y = 0;
      points.forEach(point => {
        x += point[0];
        y += point[1];
      });
      return [x / points.length, y / points.length];
    },
    
    // 销毁地图实例，释放资源
    destroyMap() {
      if (this.map) {
        // 清理实时路况图层
        if (this.trafficLayer) {
          this.trafficLayer.setMap(null);
          this.trafficLayer = null;
        }
        
        // 清理警力标记的动画和自定义元素
        this.policeMarkers.forEach(marker => {
          if (marker._hoverLabel) {
            this.map.remove(marker._hoverLabel);
          }
          if (marker._pulseCircle) {
            this.map.remove(marker._pulseCircle);
          }
          marker.setMap(null);
        });
        
        // 清理施工标记的动画和自定义元素
        this.constructionMarkers.forEach(marker => {
          if (marker._hoverLabel) {
            this.map.remove(marker._hoverLabel);
          }
          if (marker._pulseCircle) {
            this.map.remove(marker._pulseCircle);
          }
          marker.setMap(null);
        });
        
        // 清理交通拥堵区域
        this.trafficJams.forEach(area => {
          area.setMap(null);
        });
        
        // 清理搜索结果
        this.searchResults = [];
        
        // 先移除所有覆盖物
        const allOverlays = this.map.getAllOverlays();
        if (allOverlays && allOverlays.length > 0) {
          this.map.remove(allOverlays);
        }
        
        // 移除事件监听
        this.map.clearEvents();
        
        // 销毁地图实例
        this.map.destroy();
        this.map = null;
        this.AMap = null;
      }
    },
    
    // 增强交通拥堵区域的交互体验
     enhanceTrafficJamInteraction() {
       // 为每个拥堵区域添加悬停效果
       this.trafficJams.forEach(polygon => {
        // 保存原始样式
        const originalStyle = {
          fillOpacity: polygon.getOptions().fillOpacity,
          strokeWeight: polygon.getOptions().strokeWeight
        };
        
        // 鼠标悬停效果
        polygon.on('mouseover', () => {
          // 增加透明度和边框宽度以突出显示
          polygon.setOptions({
            fillOpacity: originalStyle.fillOpacity + 0.2,
            strokeWeight: originalStyle.strokeWeight + 2,
            cursor: 'pointer'
          });
        });
        
        polygon.on('mouseout', () => {
          // 恢复原始样式
          polygon.setOptions({
            fillOpacity: originalStyle.fillOpacity,
            strokeWeight: originalStyle.strokeWeight
          });
        });
      });
    },
    
    beforeUnmount() {
      // 组件销毁前清理地图资源
      this.destroyMap();
      // 断开Intersection Observer连接
      if (this.mapObserver) {
        this.mapObserver.disconnect();
      }
    }
  }
}
</script>

<style scoped>
.resource-info {
  width: 100%;
  height: 100vh;
  padding: 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
}

.header-section h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.search-box {
  display: flex;
  gap: 10px;
  max-width: 400px;
  width: 100%;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  outline: none;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.search-box input:focus {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.search-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
}

.map-and-controls {
  display: flex;
  flex: 1;
  gap: 20px;
  min-height: 0;
}

.map-controls {
  width: 280px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 20px;
  backdrop-filter: blur(10px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.layer-controls, .function-controls, .traffic-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.layer-controls h3, .traffic-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 8px;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.control-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.control-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #4facfe;
  cursor: pointer;
}

.control-item span {
  font-size: 14px;
  color: #fff;
}

.function-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-button {
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.control-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.locate-button {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
}

.locate-button:hover {
  background: linear-gradient(135deg, #38f9d7 0%, #4facfe 100%);
}

.traffic-level {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.level-indicator.smooth {
  background: #52c41a;
}

.level-indicator.slow {
  background: #faad14;
}

.level-indicator.congested {
  background: #f5222d;
}

.map-container {
  flex: 1;
  height: calc(100vh - 200px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.05);
}

.search-results {
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  backdrop-filter: blur(10px);
  max-height: 200px;
  overflow-y: auto;
}

.search-results h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.result-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(5px);
}

.result-name {
  font-weight: 500;
  color: #fff;
}

.result-type {
  background: rgba(79, 172, 254, 0.3);
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 12px;
  color: #fff;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .map-and-controls {
    flex-direction: column;
  }
  
  .map-controls {
    width: 100%;
    max-height: 200px;
    flex-direction: row;
  }
  
  .layer-controls, .function-controls, .traffic-info {
    flex: 1;
    min-width: 0;
  }
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .header-section h1 {
    font-size: 24px;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .map-controls {
    flex-direction: column;
    max-height: none;
  }
  
  .map-container {
    height: calc(100vh - 350px);
  }
}
    .map-loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
      color: #00a0e9;
      font-size: 16px;
    }
    
    .map-error {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
      color: #ff4d4f;
      font-size: 16px;
    }
    
    /* 信息窗口样式优化 */
    :deep(.info-window) {
      min-width: 250px;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    :deep(.info-header) {
      background: linear-gradient(135deg, #00a0e9, #0066cc);
      color: white;
      padding: 12px 16px;
    }
    
    :deep(.info-header h3) {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
    
    :deep(.info-body) {
      background: white;
      padding: 16px;
    }
    
    :deep(.info-address),
    :deep(.info-type),
    :deep(.info-strength) {
      margin: 0 0 8px 0;
      font-size: 14px;
      color: #666;
    }
    
    :deep(.info-footer) {
      text-align: center;
      margin-top: 12px;
    }
    
    :deep(.info-button) {
      background: #00a0e9;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: background-color 0.3s;
    }
    
    :deep(.info-button:hover) {
      background: #0066cc;
    }
    
    /* 自定义标签样式 */
    :deep(.custom-label) {
      background: rgba(0, 160, 233, 0.9);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      white-space: nowrap;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* 施工区域信息窗口样式 */
    :deep(.construction-info-window) {
      min-width: 240px;
      border-radius: 6px;
      overflow: hidden;
      background: white;
    }
    
    :deep(.construction-title) {
      margin: 0 0 10px 0;
      color: #ff4d4f;
      font-size: 16px;
      font-weight: 600;
    }
    
    :deep(.construction-address),
    :deep(.construction-type) {
      margin: 0 0 6px 0;
      color: #666;
      font-size: 14px;
    }
    
    :deep(.construction-time) {
      margin: 6px 0;
      font-size: 14px;
      color: #888;
    }
    
    :deep(.construction-status) {
      margin: 6px 0 10px 0;
      font-size: 14px;
    }
    
    :deep(.status-badge) {
      background: #ff4d4f;
      color: white;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 12px;
    }
    
    :deep(.construction-warning) {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #ff4d4f;
      font-size: 14px;
      padding: 8px;
      background: #fff2f0;
      border-radius: 4px;
    }
    
    :deep(.construction-label) {
      background: rgba(255, 77, 79, 0.9);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      white-space: nowrap;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
  </style>
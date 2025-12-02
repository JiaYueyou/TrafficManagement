import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TrafficMap from '../views/TrafficMap.vue'
import RealTimeData from '../views/RealTimeData.vue'
import StatisticsView from '../views/StatisticsView.vue'
import ResourceInfo from '../views/ResourceInfo.vue'

export default createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/traffic-map',
      name: 'trafficMap',
      component: TrafficMap
    },
    {
      path: '/real-time-data',
      name: 'realTimeData',
      component: RealTimeData
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: StatisticsView
    },
    {
      path: '/resource-info',
      name: 'resourceInfo',
      component: ResourceInfo
    }
  ]
})
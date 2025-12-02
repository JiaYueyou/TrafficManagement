//引入createApp用于创建应用
import { createApp } from 'vue'
//引入App根组件
import App from './App.vue'
//引入路由配置
import router from './router/index.js'

//调用createApp创建应用并挂载
const app = createApp(App)
//使用路由
app.use(router)
app.mount('#app')
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus'
import ElementPlus from 'element-plus';

// 初始化应用
const initApp = async () => {
    const app = createApp(App)

    // 配置全局属性
    app.config.globalProperties.$message = ElMessage

    // 挂载插件
    app.use(router)
        .use(store).use(ElementPlus)
    try {
        // 异步初始化
        await store.dispatch('initialize')
    } catch (error) {
        console.error('Store initialization failed:', error)
    } finally {
        // 确保应用挂载
        app.mount('#app')
    }
}

// 启动应用
initApp()
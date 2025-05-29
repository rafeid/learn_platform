import { createRouter, createWebHistory } from 'vue-router'
import HomeA from '../views/Home.vue'
import AboutA from '../views/About.vue'
import VideoPlayer from "@/views/VideoPlay.vue"
// import SettingA from "@/views/SettingA.vue"
import CollectionList from "@/views/CollectionList.vue"
import AuthA from "@/views/Auth.vue"
import SearchResults from "@/views/SearchResults.vue";
import testConnect from "@/views/testConnect.vue";

const routes = [
    { path: '/test', component: testConnect },
    { path: '/about', component: AboutA },
    {
        path: '/user-center',
        name: 'UserCenter',
        component: () => import('@/views/UserCenter.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/auth',  // 统一使用小写路径
        name: 'Auth',
        component: AuthA,
        meta: { guestOnly: true }
    },
    {
        path: '/player/:collectionId/:categoryId/:videoId',
        name: 'VideoPlayer',
        component: VideoPlayer,
        props: true
    },
    // {
    //     path: '/SettingA',
    //     component: SettingA,
    //     meta: { requiresAuth: true }  // 添加权限要求
    // },
    {
        path: '/',
        name: 'Collections',
        component: CollectionList,
        meta: { requiresAuth: true }  // 首页也需要登录
    },
    {
        path: '/home/:collectionId',
        component: HomeA,
        props: true,
        meta: { requiresAuth: true } // 新增权限要求
    },
    {
        path: '/search',
        name: 'SearchResults',
        component: SearchResults
    },
    {
        path: '/homework/:homeworkId',
        name: 'HomeworkDetail',
        component: () => import('../views/HomeworkDetail.vue'),
        props: true
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('user')
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    const guestOnly = to.matched.some(record => record.meta.guestOnly)

    // 已登录用户访问guestOnly页面
    if (guestOnly && isAuthenticated) {
        next('/') // 或跳转到用户上次尝试访问的页面
        return
    }

    // 需要登录但未认证
    if (requiresAuth && !isAuthenticated) {
        next({
            path: '/auth',
            query: { redirect: to.fullPath }
        })
        return
    }

    next()
})
export default router;
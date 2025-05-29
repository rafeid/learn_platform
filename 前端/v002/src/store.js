import { createStore } from 'vuex'
import api from '@/api/service.js'  // 导入 service.js

export default createStore({
    state: {
        user: null,
        currentCollection: null,
        recentViewed: []
    },
    mutations: {
        SET_USER(state, user) {
            state.user = user
            localStorage.setItem('user', JSON.stringify(user))
        },
        SET_COLLECTION(state, collection) {
            state.currentCollection = collection
        },
        ADD_VIEW_RECORD(state, homeworkId) {
            state.recentViewed = [homeworkId, ...state.recentViewed.filter(id => id !== homeworkId)].slice(0,5)
        }
    },
    actions: {
        async loadCollection({ commit }, collectionId) {
            const { data } = await api.getCollection(collectionId)  // 使用 service.js 中的 getCollection 方法
            commit('SET_COLLECTION', data)
        },
        async initialize({ commit }) {
            const user = localStorage.getItem('user')
            if (user) commit('SET_USER', JSON.parse(user))
        }
    },
})
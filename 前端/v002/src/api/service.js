import axios from 'axios';

const api = axios.create({
    baseURL: "http://localhost:8000/api",
    timeout: 10000,
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    },
    transformRequest: [
        function (data, headers) {
            if (data instanceof FormData) {
                // 如果是 FormData，设置 Content-Type 为 multipart/form-data
                headers['Content-Type'] = 'multipart/form-data';
            } else {
                // 否则，默认使用 application/json
                headers['Content-Type'] = 'application/json';
            }
            return data;
        },
    ],
});

// 请求拦截器（处理Django CSRF token）
api.interceptors.request.use(config => {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }

    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

// 响应拦截器（适配Django格式）
api.interceptors.response.use(
    response => ({
        data: response.data,
        status: response.status
    }),
    error => {
        const res = error.response || {};
        const message = res.data?.detail ||
            (typeof res.data === 'string' ? res.data : '请求错误');
        return Promise.reject({
            message,
            status: res.status,
            data: res.data
        });
    }
);

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

export default {
    // 测试用例
    hello: () => api.get('/hello/'),

    // 认证相关
    login: (cred) => api.post('/auth/login/', cred),
    register: (cred) => api.post('/auth/register/', cred),

    // 用户相关
    getCurrentUser: () => api.get('/user-center/get_user_info/'),
    updateUser: (data) => api.put('/user-center/update_user_info/', data),
    resetPassword: (oldPwd, newPwd) => api.post('/user-center/reset_password/', { oldPwd, newPwd }),
    deleteUser: (userId) => api.delete(`/users/${userId}/`),
    getUserName:(id)=>api.get(`/users/${id}/get_name/`),
    // 合辑相关
    getCollections: () => api.get('/collections/'),
    getCollection: (id) => api.get(`/collections/${id}/`),
    createCollection: (data) => api.post('/collections/', data),
    updateCollection: (id, data) => api.patch(`/collections/${id}/`, data),
    deleteCollection: (id) => api.delete(`/collections/${id}/`),
    favoriteCollection: (id) => api.post(`/collections/${id}/favorite/`),
    unfavoriteCollection: (id) => api.post(`/collections/${id}/unfavorite/`),
    getFavoriteCollections: () => api.get('/collections/favorites/'),
    getCreatedCollections: () => api.get('/collections/get_created_collections/'),
    getCourseVideoStats:(id)=>api.get(`/collections/${id}/video_stats`),
    // 分类相关
    getCategory: (id) => api.get(`/categories/${id}/`),
    getCategoryResources: (id) => api.get(`/categories/${id}/get_category_resources/`),
    createCategory: (data) => api.post('/categories/', data),
    updateCategory: (id, data) => api.patch(`/categories/${id}/`, data),
    deleteCategory: (id) => api.delete(`/categories/${id}/`),

    // 视频相关
    getVideos: () => api.get('/videos/'),
    getVideo: (id) => api.get(`/videos/${id}/`),
    getVideoDetail: (id) => api.get(`/videos/${id}/get_video_detail/`),
    addVideo: (data) => api.post('/videos/', data),
    updateVideo: (id, data) => api.patch(`/videos/${id}/`, data),
    deleteVideo: (id) => api.delete(`/videos/${id}/`),

    // 作业相关
    getHomeworks: () => api.get('/homeworks/'),
    getHomework: (id) => api.get(`/homeworks/${id}/`),
    getHomeworkDetail: (id) => api.get(`/homework-details/${id}/get_homework_detail/`),
    addHomework: (data) => api.post('/homeworks/', data),
    updateHomework: (id, data) => api.patch(`/homeworks/${id}/`, data),
    deleteHomework: (id) => api.delete(`/homeworks/${id}/`),
    getHomeworkQuestions: (id) => api.get(`/homeworks/${id}/questions/`),
    saveQuestions: (id, questions) => api.post(`/homeworks/${id}/save_questions/`,questions),
    submitAnswers: (id, answers) => api.post(`/homeworks/${id}/submit_answers/`, answers),
    getScores: (id) => api.get(`/homeworks/${id}/scores/`),
    getCurrentUserScores:(id)=>api.get(`/homeworks/${id}/get_current_user_scores/`),
    // 资料相关
    getMaterials: () => api.get('/materials/'),
    getMaterial: (id) => api.get(`/materials/${id}/`),
    addMaterial: (data) => api.post('/materials/', data),
    updateMaterial: (id, data) => api.patch(`/materials/${id}/`, data),
    deleteMaterial: (id) => api.delete(`/materials/${id}/`),
    getCategoryMaterials: (id) => api.get(`/categories/${id}/materials/`),
    // 播放记录相关
    getPlaybackStats: () => api.get('/playback-stats/'),
    updatePlaybackProgress: (data) => api.post('/playback-stats/update_progress/', data),
    getPlaybackUse:(id)=>api.get(`/analyze_course_stats/${id}`),
    getFavoriteCourseStats: () => api.get('/favorite-course-stats/'),
    // 搜索功能
    search: (query) => api.get('/search/search/?q=' + query),
    //成绩相关
    getCourseScores:(id) => api.get(`course-scores/${id}/`),
    getScoresByCourse:(params)=>api.get('/score/get_course_scores/', {params}),
    // 文件上传
    uploadFile: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    }

};
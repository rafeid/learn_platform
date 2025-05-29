<template>
  <div class="user-center">
    <div class="profile-card">
      <div class="avatar">
<!--        <img :src="'@/assets/logo.png'" alt="用户头像">-->
      </div>

      <div class="user-info">
        <h2>{{ userInfo.username }}</h2>
        <div class="meta-info">
          <p>用户ID：{{ userInfo.id }}</p>
          <p>教授课程的数量：{{ teachingCoursesCount }}</p>
          <p>在学课程的数量：{{ learningCoursesCount }}</p>
        </div>
      </div>

      <!-- 将操作按钮移动到用户卡片右侧 -->
      <div class="actions">
        <LogoutButton />
        <button class="delete-account-btn" @click="handleDeleteAccount">
          注销账户
        </button>
      </div>
    </div>
    <video-progress class="video-progress" />
    <course-video-stats class="course-video-stats" />
    <HomeworkProgress class="homework-progress" />
    <course-homework-stats class="course-homework-stats" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/service'
import LogoutButton from '../components/LogoutButton.vue' // 引入退出登录按钮组件
import videoProgress from "../components/VideoProgress.vue";
import CourseVideoStats from "../components/CourseVideoStats.vue";
import HomeworkProgress from "../components/HomeworkProgress.vue";
import CourseHomeworkStats from "@/components/CourseHomeworkStats.vue";
const router = useRouter()

// 用户信息
const userInfo = ref({
  id: '',
  username: '未登录'
})

// 课程数据
const teachingCoursesCount = ref(0)
const learningCoursesCount = ref(0)

// 获取教授课程的数量
const loadTeachingCoursesCount = async () => {
  try {
    const { data } = await api.getCreatedCollections(userInfo.value)
    teachingCoursesCount.value = data.length
  } catch (error) {
    console.error('获取教授课程数量失败:', error)
  }
}

// 获取在学的课程数量
const loadLearningCoursesCount = async () => {
  try {
    const { data } = await api.getFavoriteCollections(userInfo.value)
    learningCoursesCount.value = data.length
  } catch (error) {
    console.error('获取在学的课程数量失败:', error)
  }
}

// 初始化
onMounted(async () => {
  try {
    const storedUser = JSON.parse(localStorage.getItem('user'))
    if (!storedUser) {
      await router.push('/auth')
      return
    }

    userInfo.value = storedUser

    // 加载数据
    await loadTeachingCoursesCount()
    await loadLearningCoursesCount()
  } catch (error) {
    console.error('初始化失败:', error)
    await router.push('/error')
  }
})

// 注销账户
const handleDeleteAccount = async () => {
  if (confirm('确定要注销账户吗？此操作不可恢复！')) {
    try {
      await api.deleteUser(userInfo.value.id)
      localStorage.removeItem('user')
      await router.push('/auth')
    } catch (error) {
      console.error('注销账户失败:', error)
    }
  }
}
</script>

<style scoped>
.user-center {
  max-width: 800px; /* 增加宽度以容纳更多内容 */
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info {
  flex: 1; /* 让用户信息部分占据剩余空间 */
}

.user-info h2 {
  margin: 0 0 0.5rem;
  color: #333;
}

.meta-info p {
  margin: 0.4rem 0;
  color: #666;
  font-size: 0.95em;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* 按钮之间的间距 */
  align-items: flex-end; /* 按钮右对齐 */
}

.delete-account-btn {
  padding: 0.8rem 2rem;
  background: #666;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.delete-account-btn:hover {
  background: #444;
}
.video-progress,
.course-video-stats,
.homework-progress,
.course-homework-stats {
  border: 1px solid #ddd; /* 简约的灰色线条 */
  border-radius: 8px; /* 圆角效果 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 轻微的阴影 */
  padding: 1rem; /* 内边距，避免内容紧贴边框 */
  margin-bottom: 1.5rem; /* 组件之间的间距 */
  background: #fff; /* 白色背景，确保组件内容清晰 */
}
</style>
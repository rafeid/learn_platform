<template>
  <button class="logout-btn" @click="handleLogout">
    退出登录
  </button>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    localStorage.removeItem('user')
    router.push('/auth')
  }
}
</script>

<style scoped>
.logout-btn {
  padding: 0.8rem 2rem;
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #cc0000;
}
</style>
<template>
  <div class="btn-dropdown">
    <!-- 主按钮 -->
    <button class="main-btn" @click.stop="toggleMenu">
      个人中心
    </button>

    <!-- 下拉按钮组 -->
    <transition name="fade">
      <div v-if="showMenu" class="dropdown-btn">
        <router-link to="/user-center" class="ac-btn save-btn">个人中心</router-link>
<!--        <router-link to="/SettingA" class="ac-btn saves-btn">设置</router-link>-->
        <LogoutButton />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import LogoutButton from '../components/LogoutButton.vue' // 引入退出登录按钮组件

const showMenu = ref(false)

// 切换菜单可见性
const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

// 点击外部关闭
const handleClickOutside = (e) => {
  if (!e.target.closest('.btn-dropdown')) {
    showMenu.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.btn-dropdown :deep(.logout-btn)  {
  font-size: 15px;
  padding: 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  background: #fef0f0;
  color: #f56c6c;
}

.btn-dropdown :deep(.logout-btn:hover)  {
  background: #fde2e2;
}
.btn-dropdown {
  position: relative;
  display: inline-block;
}

.main-btn {
  padding: 9px 14px;
  background: linear-gradient(135deg, #514549, #AFAC90); /* 按钮背景渐变 */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.main-btn:hover {
  background: #AFAC90;
}

.dropdown-btn {
  position: absolute;
  top: 110%;
  left: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
  padding: 6px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.ac-btn {
  margin: 0;
  padding: 8px;
  font-size: 15px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}
.ac-btn:hover {
  text-decoration: none;
}
.save-btn {
  background: #f0f9ec;
  color: #e6a23c;
}

.save-btn:hover {
  background: #faecd8;
}

.saves-btn {
  background: #fdf6ec;
  color: #e6a23c;
}

.saves-btn:hover {
  background: #faecd8;
}
</style>
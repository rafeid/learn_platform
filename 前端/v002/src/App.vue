<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar">
      <router-link to="/" class="logo">在线学习平台</router-link>
      <!-- 搜索框 -->
      <div class="search-bar">
        <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索课程..."
            @keyup.enter="searchVideos"
        />
        <button @click="searchVideos">搜索</button>
      </div>
      <div class="nav-links">
        <button class="sn-jun" @click="goToHome">首页</button>
        <MenuA class="menua" />
        <router-link to="/About">关于平台</router-link>
      </div>
    </nav>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <h3>搜索结果</h3>
      <ul>
        <li v-for="collection in searchResults" :key="collection.id">
          <router-link :to="`/collection/${collection.id}`">
            {{ collection.name }}
          </router-link>
          <p>{{ collection.description }}</p>
        </li>
      </ul>
    </div>

    <!-- 路由视图 -->
    <router-view class="router-view"/>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; 2025 在线学习平台. 保留所有权利.</p>
    </footer>
  </div>
</template>

<script>
import MenuA from "./components/MenuA.vue";
export default {
  name: 'App',
  components: { MenuA },
  data() {
    return {
      searchQuery: '', // 搜索框的输入内容
      collections: [], // 存储所有合辑
      searchResults: [] // 存储搜索结果
    };
  },
  methods: {
    searchVideos() {
      if (!this.searchQuery) {
        alert('请输入搜索关键字');
        return;
      }
      // 跳转到搜索页面，并传递搜索关键字
      this.$router.push({ path: '/search', query: { q: this.searchQuery } });
    },
    goToHome() {
      this.$router.push('/');
    }
  }
}
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #f8f5f0; /* 路由视图背景色为米白色 */
  color: #4a4a4a;
  line-height: 1.6;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 导航栏 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 5%;
  background-color: #E2CFCB; /* 导航栏颜色为#E2CFCB */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  position: relative;
}

.navbar .logo {
  font-size: 26px;
  font-weight: 600;
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.3s;
}

.navbar .logo:hover {
  color: #AFAC90;
}

/* 搜索框 */
.search-bar {
  position: absolute;
  left: 48%;
  transform: translateX(-50%);
}

.search-bar input {
  padding: 12px 24px;
  width: 400px;
  border: 2px solid #e0e0e0;
  border-radius: 30px;
  font-size: 15px;
  transition: all 0.3s;
  background: #f8f8f8;
}

.search-bar input:focus {
  outline: none;
  border-color: #AFAC90;
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.15);
}

.search-bar button {
  padding: 12px 28px;
  border: none;
  border-radius: 30px;
  background: linear-gradient(135deg, #514549, #AFAC90);
  color: white;
  font-weight: 500;
  margin-left: 10px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.search-bar button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.15);
}

/* 导航链接 */
.nav-links {
  display: flex;
  align-items: center;
}

.nav-links a {
  margin-left: 28px;
  color: #514549;
  text-decoration: none;
  font-weight: 500;
  position: relative;
  padding-bottom: 4px;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #007bff;
  transition: width 0.3s;
}

.nav-links a:hover::after {
  width: 100%;
}


/* 按钮统一风格 */
button {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  font-weight: 500;
  background: #514549; /* 按钮背景颜色为#514549 */
  color: white;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
}

.sn-jun {
  padding: 10px 20px;
  background: linear-gradient(135deg, #514549, #AFAC90); /* 按钮背景渐变 */
  color: white;
  border: none;
  border-radius: 6px;
  transition: transform 0.2s;
}

.sn-jun:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px;
  background: #AFAC90;
}
.menua{
  right: -5%;
}
/* 路由视图 */
.router-view {
  flex: 1;
  min-width: 1000px;
  margin: 0 auto;
  padding: 10px 5%;
  background-color: #f8f5f0; /* 路由视图背景色为米白色 */
}

/* 搜索结果 */
.search-results {
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 30px;
  margin: 20px auto;
  max-width: 800px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.search-results h3 {
  color: #2c3e50;
  font-size: 22px;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.search-results ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-results li {
  padding: 18px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.search-results li:last-child {
  border-bottom: none;
}

.search-results li:hover {
  transform: translateX(8px);
}

.search-results a {
  color: #2c3e50;
  font-size: 17px;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.search-results a:hover {
  color: #007bff;
}

.search-results p {
  color: #666;
  font-size: 14px;
  margin-top: 8px;
  line-height: 1.5;
}

/* 页脚 */
.footer {
  text-align: center;
  padding: 24px 5%;
  background: #E2CFCB; /* 页脚颜色为#E2CFCB */
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  color: #514549; /* 使用#AFAC9D颜色 */
  margin-top: auto;
}

.footer p {
  margin: 0;
  font-size: 14px;
}
</style>
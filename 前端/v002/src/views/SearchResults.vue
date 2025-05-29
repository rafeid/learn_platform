<template>
  <div class="search-results-page">
    <h3>搜索结果</h3>
    <div v-if="searchResults.length > 0" class="collection-grid">
      <div
          class="collection-item"
          v-for="collection in searchResults"
          :key="collection.id"
          @click="enterCollection(collection.id)"
      >
        <!-- 缩略图 -->
        <div class="collection-thumbnail">
          <img :src="collection.thumbnail" :alt="collection.name" />
        </div>

        <!-- 合辑信息 -->
        <div class="collection-info">
          <h2>{{ collection.name }}</h2>
          <p>{{ collection.description }}</p>
          <small>创建者：{{ collection.creator }}</small>
          <small>创建时间：{{ formatDate(collection.createdAt) }}</small>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <p>无相关课程</p>
    </div>
  </div>
</template>

<script>
import api from "../api/service";

export default {
  name: 'SearchResults',
  data() {
    return {
      searchQuery: '',
      searchResults: []
    };
  },
  async created() {
    // 从路由查询参数中获取搜索关键字
    this.searchQuery = this.$route.query.q || '';
    if (this.searchQuery) {
      await this.performSearch();
    }
  },
  methods: {
    // 进入合辑
    enterCollection(id) {
      this.$router.push(`/home/${id}`);
    },

    // 日期格式化方法
    formatDate(timestamp) {
      try {
        return new Date(Number(timestamp)).toLocaleDateString('zh-CN');
      } catch {
        return '无效日期';
      }
    },

    // 执行搜索
    async performSearch() {
      try {
        const response = await api.getCollections();
        const collections = response.data;
        this.searchResults = collections.filter(collection =>
            collection.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            collection.description.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      } catch (err) {
        alert('搜索失败，请稍后重试');
      }
    }
  }
};
</script>

<style scoped>
/* 搜索结果页面 */
.search-results-page {
  padding: 20px;
}

/* 合辑列表 */
.collection-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: flex-start;
}

.collection-item {
  flex: 1 1 calc(33% - 10px); /* 每行显示 3 个，减去 gap 的宽度 */
  display: flex;
  flex-direction: column;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  cursor: pointer;
  min-width: calc(30% - 15px); /* 确保最小宽度 */
  max-width: calc(30% - 15px); /* 确保最大宽度 */
}

.collection-item:hover {
  transform: translateY(-2px);
}

.collection-thumbnail {
  width: 80%;
  height: 120px;
  margin-bottom: 15px;
  overflow: hidden;
  border-radius: 8px;
}

.collection-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.collection-info h2 {
  margin: 0 0 8px;
  color: #333;
  font-size: 1.1em;
}

.collection-info p {
  margin: 0 0 6px;
  color: #666;
  font-size: 0.9em;
}

.collection-info small {
  display: block;
  color: #999;
  font-size: 0.8em;
}

.empty-state {
  width: 100%;
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 16px;
}
</style>
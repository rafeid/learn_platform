<template>
  <div class="home">
    <!-- 分类侧边栏 -->
    <classification-a
        :collection-id="collectionId"
        @category-change="handleCategoryChange"
    />

    <!-- 主内容区域 -->
    <div class="main-content">
      <VideoAndHomework
          :collection-id="collectionId"
          :category-id="activeCategoryId"
      />
    </div>
  </div>
</template>

<script>
import ClassificationA from "../components/Classificaltion.vue" // 注意组件名大小写
import VideoAndHomework from "../components/VideoAndHomework.vue"
import api from "../api/service";

export default {
  name: 'HomeA',
  props: ['collectionId'],
  components: {
    ClassificationA,
    VideoAndHomework
  },
  data() {
    return {
      activeCategoryId: null // 新增的分类状态
    }
  },
  watch: {
    collectionId: {
      immediate: true,
      async handler(newVal) {
        if (newVal) {
          await this.loadCollectionData(newVal)
          this.activeCategoryId = null
        }
      }
    }
  },
  methods: {
    async loadCollectionData(id) {
      try {
        const { data } = await api.getCollection(id)
        if (data?.categories) {
          this.categories = data.categories
          // 自动选择第一个可用分类
          const firstUnlocked = data.categories.find(c => !c.locked)
          this.activeCategoryId = firstUnlocked?.id || null
        }
      } catch (error) {
        console.error('合辑加载失败:', error)
      }
    },
    handleCategoryChange({ categoryId }) {
      this.activeCategoryId = categoryId;
    },
  },
  mounted() {
    this.loadCollectionData(this.collectionId)
    // 可选：从路由参数获取合辑ID（如果props未传）
    // if (!this.collectionId) {
    //   this.collectionId = this.$route.params.id
    // }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  min-height: calc(100vh - 120px); /* 留出页头页脚空间 */
  padding: 24px 5%; /* 与全局布局对齐 */
  background-color: #f8f5f0; /* 统一米白底色 */
  gap: 24px; /* 现代布局间距 */
}



.main-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  min-height: 600px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .home {
    flex-direction: column;
    padding: 16px;
  }

  .classification-a {
    flex: none;
    width: 100%;
    margin-right: 0;
    margin-bottom: 24px;
    max-height: 400px;
  }

  .main-content {
    padding: 24px;
  }
}
</style>
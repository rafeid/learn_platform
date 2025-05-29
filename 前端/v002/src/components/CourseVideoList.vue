<template>
  <div class="course-video-list">
    <h2 class="course-video-list-title">课程视频列表</h2>
    <div class="scroll-container">
      <div v-for="category in categoriesWithVideos" :key="category.id" class="category-section">
        <h3 class="category-title">{{ category.name }}</h3>
        <ul class="video-items" @click="handleVideoClick">
          <!-- 修改li元素，添加class绑定 -->
          <li
              v-for="video in category.videos"
              :key="video.id"
              :class="{ active: video.id === currentVideoId }"
              :data-video-id="video.id"
              :data-category-id="category.id"
          >
            <span class="video-title">{{ video.title }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseVideoList',
  props: {
    categoriesWithVideos: {
      type: Array,
      default: () => []
    },
    currentVideoId: {
      type: Number,
      required: true
    }
  },
  methods: {
    handleVideoClick(event) {
      const liElement = event.target.closest('li');
      if (!liElement) return;

      const videoId = Number(liElement.dataset.videoId);
      const categoryId = Number(liElement.dataset.categoryId);

      this.$emit('navigate', { videoId, categoryId });
    }
  }
};
</script>
<style scoped>
.course-video-list {
  width: 25%;
  height: 100vh;
  padding: 20px;
  background: #f8f9fa;
  box-shadow: 2px 0 12px rgba(0,0,0,0.05);
  contain: strict;
}

.scroll-container {
  height: calc(100% - 60px);
  overflow-y: auto;
  padding-right: 8px;
}

/* 分类区块样式 */
.category-section {
  margin-bottom: 0;
  background: none;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  transition: none;
}

.category-section:hover {
  transform: none;
}

.category-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  padding: 8px 0;
  margin-bottom: 12px;
  border-bottom: 2px solid #e8ecef;
  contain: content;
}

/* 视频列表样式 */
.video-items {
  padding: 0;
  margin: 0;
  list-style: none;
  contain: content;
}

.video-items > li {
  padding: 12px;
  margin: 6px 0;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: #f8fafc;
  position: relative;
  contain: content;
  display: flex;
  align-items: center;
}

.video-items > li:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.video-items > li.active {
  background: #AFAC90;
  color: white;
  box-shadow: 0 2px 6px rgba(64,158,255,0.3);
}

.video-items > li.active::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #fff;
  border-radius: 2px;
}

.video-title {
  font-size: 0.95rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .course-video-list {
    width: 100%;
    height: auto;
    padding: 16px;
    box-shadow: none;
    border-top: 1px solid #eee;
  }

  .scroll-container {
    max-height: 50vh;
  }

  .category-section {
    margin-bottom: 1rem;
    padding: 10px;
  }

  .video-title {
    font-size: 0.9rem;
  }
}

/* 滚动条美化 */
.scroll-container::-webkit-scrollbar {
  width: 6px;
}

.scroll-container::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.05);
}

.scroll-container::-webkit-scrollbar-thumb {
  background: #c1c9d2;
  border-radius: 4px;
}
</style>
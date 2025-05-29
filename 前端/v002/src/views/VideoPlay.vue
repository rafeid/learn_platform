<template>
  <div class="video-container">
    <div class="video-content">
      <div v-if="loading" class="status-container">
        <div class="loading-tip">视频加载中...</div>
      </div>
      <div v-else-if="error" class="status-container">
        <div class="error-tip">
          {{ error }}
          <button @click="retryLoading" class="retry-btn">重试</button>
        </div>
      </div>
      <div v-else class="video-main">
        <h1 class="video-title">{{ currentVideo.title }}</h1>
        <div class="player-wrapper">
          <video
              ref="videoPlayer"
              :src="'http://localhost:8000'+currentVideo.url"
              controls
              autoplay
              class="video-element"
              @loadeddata="handleVideoReady"
          ></video>
        </div>
        <div class="video-meta">
          <div class="video-info">
            <span class="duration">时长 {{ currentVideo.duration }}</span>
            <span class="divider">|</span>
            <span class="category">所属分类 {{ categoryName }}</span>
          </div>
          <p class="video-description">{{ currentVideo.description }}</p>
        </div>
<!--        <MessageBoard />-->
      </div>
    </div>
    <CourseVideoList
        :categories-with-videos="categoriesWithVideos"
        :current-video-id="currentVideo.id"
        @navigate="handleVideoNavigation"
    />
  </div>
</template>

<script>
// import MessageBoard from "../components/MessageBoard.vue";
import CourseVideoList from "../components/CourseVideoList.vue";
import api from "../api/service";

export default {
  name: 'VideoPlayer',
  components: {
    // MessageBoard,
    CourseVideoList,
  },
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      currentVideo: {
        id: null,
        title: '',
        description: '',
        duration: '',
        url: '',
      },
      categoryName: '',
      loading: true,
      error: null,
      categoriesWithVideos: [],
    };
  },
  computed: {
    routeParams() {
      return {
        collectionId: Number(this.$route.params.collectionId),
        categoryId: Number(this.$route.params.categoryId),
        videoId: Number(this.$route.params.videoId),
      };
    },
  },
  watch: {
    routeParams: {
      immediate: true,
      async handler(newVal) {
        if (newVal.videoId && newVal.categoryId) {
          await this.loadVideoData();
        }
      },
    },
  },
  methods: {
    async loadVideoData() {
      this.loading = true;
      this.error = null;

      try {
        // 并行获取集合数据和视频详情
        const [collectionRes, videoRes] = await Promise.all([
          api.getCollection(this.routeParams.collectionId),
          this.fetchVideoDetails(),
        ]);

        // 处理分类结构数据（核心修正部分）
        const categoriesWithVideos = await Promise.all(
            collectionRes.data.categories.map(async (category) => {
              // 获取每个分类的完整资源
              const { data } = await api.getCategoryResources(category.id);
              return {
                ...category,
                videos: data.videos || [], // 转换为视频对象数组
              };
            })
        );

        // 设置分类名称
        const currentCategory = collectionRes.data.categories.find(
            (c) => c.id === this.routeParams.categoryId
        );
        this.categoryName = currentCategory?.name || '未知分类';

        // 设置当前播放视频
        if (videoRes) {
          this.currentVideo = videoRes;
        } else {
          throw new Error('找不到指定的视频资源');
        }

        // 更新分类数据（包含视频对象）
        this.categoriesWithVideos = categoriesWithVideos;
      } catch (error) {
        console.error('视频加载失败:', error);
        this.error = error.message || '视频加载失败，请检查网络连接';
        // 清空错误数据
        this.currentVideo = { id: null };
        this.categoriesWithVideos = [];
      } finally {
        this.loading = false;
      }
    },

    async fetchVideoDetails() {
      const { data } = await api.getCategoryResources(this.routeParams.categoryId);
      return data.videos.find((v) => v.id === this.routeParams.videoId);
    },

    async handleVideoReady() {
      const videoElement = this.$refs.videoPlayer;
      //尝试读取上一次记录
      try {
        const playbackStats = await api.getPlaybackStats(this.user.id);
        const currentVideoStats = playbackStats.data.find(
            (stats) => stats.video === this.routeParams.videoId
        );
        const lastDuration = currentVideoStats?.duration;
        if (lastDuration) {
          if (videoElement.readyState >= 2) { // readyState >= 2 表示视频已加载足够数据
            videoElement.currentTime = lastDuration;
          } else {
            // 如果视频未加载完成，监听 loadeddata 事件
            videoElement.addEventListener('loadeddata', () => {
              videoElement.currentTime = lastDuration;
            });
          }
        }
      } catch (error) {
        console.error('获取播放记录失败:', error);
      }
      //视频记录更新逻辑
      videoElement.addEventListener('timeupdate', async () => {
        const progress = (videoElement.currentTime / videoElement.duration) * 100;
        const duration = Math.floor(videoElement.currentTime); // 播放时长（秒）
        await api.updatePlaybackProgress(JSON.stringify({
          videoId: this.routeParams.videoId,
          userId: this.user.id,
          progress: progress,
          duration: duration,
          lastPlayedAt: Date.now(),
        }));
      });
      videoElement.play().catch((error) => {
        console.warn('自动播放失败:', error);
      });
    },

    retryLoading() {
      this.loadVideoData();
    },

    handleVideoNavigation({ videoId, categoryId }) {
      this.$router.push({
        name: 'VideoPlayer',
        params: {
          collectionId: this.routeParams.collectionId,
          categoryId: categoryId,
          videoId: videoId
        }
      });
    },
  },
};
</script>

<style scoped>
.video-container {
  display: flex;
  position: relative;
  width: 95%;
  max-width: 1500px;
  margin: 0 auto;
  padding: 20px;
}

.video-content {
  flex: 1;
  margin-right: 24px; /* 为视频列表预留空间 */
}
.video-main{
  width: 100%;
}
.player-wrapper {
  margin-top: 40px;
  width: 100%;
  position: relative;
  padding-top: 56.25%; /* 16:9 比例 */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: #000;
}

.video-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  outline: none;
}

.video-meta {
  margin: 24px 0;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
}

.video-title {
  font-size: 2rem;
  margin-bottom: 12px;
  color: #333;
}

.video-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  color: #666;
}

.duration {
  font-weight: 500;
}

.divider {
  margin: 0 12px;
  opacity: 0.6;
}

.video-description {
  line-height: 1.6;
  color: #666;
}

.status-container {
  text-align: center;
  padding: 40px 20px;
}

.loading-tip {
  color: #666;
  font-size: 1.2rem;
}

.error-tip {
  color: #f56c6c;
  font-size: 1.1rem;
}

.retry-btn {
  margin-left: 12px;
  padding: 6px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.retry-btn:hover {
  background: #66b1ff;
}

@media (max-width: 768px) {
  .video-container {
    padding: 0 10px;
  }

  .video-title {
    font-size: 1.5rem;
  }

  .video-content {
    margin-right: 0; /* 移动端取消右侧列表 */
  }
}
</style>
<template>
  <div class="video-list">
    <!-- 视频列表部分 -->
    <div v-if="loading" class="loading-tip">加载中...</div>
    <div v-else-if="error" class="error-tip">{{ error }}</div>
    <div v-else class="video-grid">
      <!-- 视频卡片 -->
      <div
          v-for="video in videos"
          :key="video.id"
          class="video-card"
          @click="playVideo(video)"
      >
        <!-- 视频缩略图 -->
        <div class="video-thumbnail-wrapper">
          <img
              :src="'http://localhost:8000' + video.thumbnail"
              :alt="video.title"
              class="video-thumbnail"
              loading="lazy"
          />
          <div class="thumbnail-overlay"></div>
        </div>
        <!-- 视频信息 -->
        <div class="video-info">
          <h3 class="video-title">{{ video.title }}</h3>
          <p class="video-description">{{ video.description }}</p>
          <div class="video-progress">
            <div class="progress-bar">
              <div class="progress" :style="{ width: video.progress + '%' }"></div>
            </div>
            <span class="duration">{{ video.duration }}</span>
          </div>
        </div>
        <!-- 编辑和删除按钮 -->
        <div v-if="isCreator" class="video-actions">
          <button class="edit-btn" @click.stop="openEditVideoModal(video)">
            <el-icon-edit />
          </button>
          <button class="delete-btn" @click.stop="deleteVideo(video)">
            <el-icon-delete />
          </button>
        </div>
      </div>
    </div>

    <!-- 添加视频按钮 -->
    <button v-if="isCreator" class="add-video-btn" @click="openAddVideoModal">
      <el-icon-plus />
    </button>

    <!-- 添加视频弹窗 -->
    <el-dialog
        v-model="addVideoModalVisible"
        title="添加视频"
        width="50%"
        @close="resetAddVideoForm"
    >
      <el-form :model="addVideoForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="addVideoForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="addVideoForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="缩略图" required>
          <el-upload
              :http-request="handleUploadThumbnail"
              :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
          <img v-if="addVideoForm.thumbnail" :src="addVideoForm.thumbnail" class="thumbnail-preview" />
        </el-form-item>
        <el-form-item label="视频文件" required>
          <el-upload
              :http-request="handleUploadFile"
              :before-upload="beforeVideoUpload"
              :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
          <span v-if="addVideoForm.url" class="video-preview">视频已上传</span>
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="addVideoModalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddVideo">提交</el-button>
      </template>
    </el-dialog>

    <!-- 编辑视频弹窗 -->
    <el-dialog
        v-model="editVideoModalVisible"
        title="编辑视频"
        width="50%"
        @close="resetEditVideoForm"
    >
      <el-form :model="editVideoForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editVideoForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="editVideoForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="缩略图" required>
          <el-upload
              :http-request="handleUploadThumbnail"
              :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
          <img v-if="editVideoForm.thumbnail" :src="editVideoForm.thumbnail" class="thumbnail-preview" />
        </el-form-item>
        <el-form-item label="视频文件" required>
          <el-upload
              :http-request="handleUploadFile"
              :before-upload="beforeVideoUpload"
              :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
          <span v-if="editVideoForm.url" class="video-preview">视频已上传</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVideoModalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditVideo">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api/service';
import { Edit, Delete, Plus } from '@element-plus/icons-vue';

export default {
  components: {
    'el-icon-edit': Edit,
    'el-icon-delete': Delete,
    'el-icon-plus': Plus,
  },
  props: {
    categoryId: {
      type: Number,
      required: true,
    },
    collectionId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      videos: [],
      loading: true,
      error: null,
      currentFetchId: 0,
      isCreator: false,

      // 添加视频弹窗相关
      addVideoModalVisible: false,
      addVideoForm: {
        title: '',
        description: '',
        thumbnail: '',
        url: '',
        duration: '',
        categoryId: this.categoryId,
      },

      // 编辑视频弹窗相关
      editVideoModalVisible: false,
      editVideoForm: {
        id: null,
        title: '',
        description: '',
        thumbnail: '',
        url: '',
        duration: '',
        isNewThumbnail: false, // 是否上传了新缩略图
        isNewVideo: false, // 是否上传了新视频
      },
    };
  },
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user')) || {};
    },
  },
  watch: {
    categoryId: {
      immediate: true,
      handler(newVal) {
        if (newVal) this.loadVideos();
      },
    },
  },
  methods: {
    async loadVideos() {
      const fetchId = ++this.currentFetchId;
      try {
        this.loading = true;
        this.error = null;

        const resources = await api.getCategoryResources(this.categoryId);
        const stats = await api.getPlaybackStats(this.user.id);
        const collection = await api.getCollection(this.collectionId);

        if (fetchId !== this.currentFetchId) return;

        this.isCreator = collection.data.creator === this.user.id;
        const statsMap = new Map((stats.data || []).map((s) => [s.video, s.progress]));
        this.videos = resources.data.videos.map((video) => ({
          ...video,
          progress: statsMap.get(video.id) || 0,
        }));
      } catch (error) {
        console.error('视频加载失败:', error);
        this.error = error.message || '视频加载失败，请稍后重试';
      } finally {
        if (fetchId === this.currentFetchId) {
          this.loading = false;
        }
      }
    },

    playVideo(video) {
      this.$router.push({
        name: 'VideoPlayer',
        params: {
          collectionId: this.collectionId,
          categoryId: this.categoryId,
          videoId: video.id,
        },
      });
    },

    // 打开添加视频弹窗
    openAddVideoModal() {
      this.addVideoModalVisible = true;
    },

    // 提交添加视频表单
    async submitAddVideo() {
      try {
        const formData = new FormData();
        formData.append('title', this.addVideoForm.title);
        formData.append('description', this.addVideoForm.description);
        formData.append('duration', this.addVideoForm.duration);
        formData.append('categoryId', this.categoryId);
        if (this.addVideoForm.thumbnail) {
          formData.append('thumbnail', this.addVideoForm.thumbnail);
        }
        if (this.addVideoForm.url) {
          formData.append('url', this.addVideoForm.url);
        }

        await api.addVideo(formData);
        this.$message.success('视频添加成功！');
        this.addVideoModalVisible = false;
        await this.loadVideos();
      } catch (error) {
        console.error('添加视频失败:', error);
        this.$message.error('添加视频失败，请稍后重试');
      }
    },

    // 重置添加视频表单
    resetAddVideoForm() {
      this.addVideoForm = {
        title: '',
        description: '',
        thumbnail: '',
        url: '',
        duration: '',
        categoryId: this.categoryId,
      };
    },

    // 打开编辑视频弹窗
    openEditVideoModal(video) {
      this.editVideoForm = { ...video, isNewThumbnail: false, isNewVideo: false };
      this.editVideoModalVisible = true;
    },

    // 提交编辑视频表单
    async submitEditVideo() {
      try {
        const formData = new FormData();
        formData.append('title', this.editVideoForm.title);
        formData.append('description', this.editVideoForm.description);
        formData.append('duration', this.editVideoForm.duration);

        // 如果用户上传了新缩略图，传递缩略图 URL
        if (this.editVideoForm.isNewThumbnail) {
          formData.append('thumbnail_url', this.editVideoForm.thumbnail);
        }

        // 如果用户上传了新视频，传递视频 URL
        if (this.editVideoForm.isNewVideo) {
          formData.append('video_url', this.editVideoForm.url);
        }

        await api.updateVideo(this.editVideoForm.id, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.$message.success('视频更新成功！');
        this.editVideoModalVisible = false;
        await this.loadVideos();
      } catch (error) {
        console.error('更新视频失败:', error);
        this.$message.error('更新视频失败，请稍后重试');
      }
    },

    // 重置编辑视频表单
    resetEditVideoForm() {
      this.editVideoForm = {
        id: null,
        title: '',
        description: '',
        thumbnail: '',
        url: '',
        duration: '',
        isNewThumbnail: false,
        isNewVideo: false,
      };
    },

    // 删除视频
    async deleteVideo(video) {
      try {
        await api.deleteVideo(video.id);
        this.videos = this.videos.filter((v) => v.id !== video.id);
        this.$message.success('视频删除成功！');
      } catch (error) {
        console.error('删除视频失败:', error);
        this.$message.error('删除视频失败，请稍后重试');
      }
    },

    // 自定义文件上传方法
    async handleUploadFile({ file }) {
      try {
        const response = await api.uploadFile(file);
        if (response.data && response.data.url) {
          this.addVideoForm.url = response.data.url;
          this.editVideoForm.url = response.data.url;
          this.editVideoForm.isNewVideo = true; // 标记为新视频
          this.$message.success('视频上传成功！');
        } else {
          throw new Error('上传失败，未获取到文件 URL');
        }
      } catch (error) {
        console.error('视频上传失败:', error);
        this.$message.error('视频上传失败，请稍后重试');
      }
    },

    // 自定义缩略图上传方法
    async handleUploadThumbnail({ file }) {
      try {
        const response = await api.uploadFile(file);
        if (response.data && response.data.url) {
          this.addVideoForm.thumbnail = response.data.url;
          this.editVideoForm.thumbnail = response.data.url;
          this.editVideoForm.isNewThumbnail = true; // 标记为新缩略图
          this.$message.success('缩略图上传成功！');
        } else {
          throw new Error('上传失败，未获取到文件 URL');
        }
      } catch (error) {
        console.error('缩略图上传失败:', error);
        this.$message.error('缩略图上传失败，请稍后重试');
      }
    },

    // 视频上传前的校验
    beforeVideoUpload(file) {
      const allowedTypes = ['video/mp4', 'video/avi', 'video/mov'];
      const isVideo = allowedTypes.includes(file.type);
      const isLt500M = file.size / 1024 / 1024 < 500;

      if (!isVideo) {
        this.$message.error('只能上传 MP4、AVI 或 MOV 格式的视频文件');
      }
      if (!isLt500M) {
        this.$message.error('视频大小不能超过 500MB');
      }

      return isVideo && isLt500M;
    },
  },
};
</script>
<style scoped>
/* 样式部分保持不变 */
.video-list {
  padding: 20px;
  position: relative;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.video-card {
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  will-change: transform;
  position: relative;
}

.video-card:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.video-thumbnail-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.video-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.6));
}

.video-info {
  padding: 16px;
}

.video-title {
  margin: 0 0 10px;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.video-description {
  margin: 0 0 16px;
  font-size: 14px;
  color: #666;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-progress {
  margin-top: 10px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background-color: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
}

.duration {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.loading-tip,
.error-tip {
  padding: 20px;
  text-align: center;
  color: #666;
}

.error-tip {
  color: #f56c6c;
}

.video-actions {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  background: rgb(128, 128, 128);
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.3s ease;
}

.edit-btn:hover {
  background: #409eff;
  color: white;
}

.delete-btn:hover {
  background: #f56c6c;
  color: white;
}

.add-video-btn {
  position: fixed;
  top: 70px;
  right: 60px;
  background: rgba(0, 0, 0, 0.8);
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 24px;
  transition: background 0.3s ease;
}

.add-video-btn:hover {
  background: rgba(0, 0, 0, 1);
}

.thumbnail-preview {
  max-width: 100%;
  max-height: 100px;
  margin-top: 10px;
  border-radius: 4px;
}

.video-preview {
  font-size: 12px;
  color: #666;
  margin-top: 10px;
}
</style>
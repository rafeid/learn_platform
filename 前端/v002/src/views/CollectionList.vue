<template>
  <div class="collection-container">
    <!-- 左侧筛选按钮 -->
    <div class="filter-sidebar">
      <button
          :class="{ active: currentFilter === 'all' }"
          @click="filterCollections('all')"
      >
        全部课程
      </button>
      <button
          :class="{ active: currentFilter === 'created' }"
          @click="filterCollections('created')"
      >
        我教的课
      </button>
      <button
          :class="{ active: currentFilter === 'favorite' }"
          @click="filterCollections('favorite')"
      >
        我学的课
      </button>
    </div>

    <!-- 右侧内容 -->
    <div class="collection-content">
      <!-- 操作工具栏 -->
      <div class="toolbar">
        <button class="create-btn" @click="showCreateDialog">新建课程</button>
        <button class="edit-mode-btn" @click="toggleEditMode">
          {{ isEditMode ? '退出编辑' : '编辑课程' }}
        </button>
      </div>

      <!-- 合辑列表 -->
      <div class="collection-grid">
        <template v-if="collections.length > 0">
          <div
              class="collection-item"
              v-for="collection in collections"
              :key="collection.id"
              @click="enterCollection(collection.id)"
          >
            <!-- 缩略图 -->
            <div class="collection-thumbnail">
              <img :src="collection.thumbnail" :alt="collection.name"/>
              <button
                  class="favorite-btn"
                  @click.stop="toggleFavorite(collection)"
                  :title="collection.isFavorite ? '取消收藏' : '收藏课程'"
              >
                <i :class="['icon', collection.isFavorite ? 'fas fa-heart' : 'far fa-heart']"></i>
              </button>
            </div>

            <!-- 合辑信息 -->
            <div class="collection-info">
              <h2>{{ collection.name }}</h2>
              <p>{{ collection.description }}</p>
              <small>创建者：{{ collection.creator }}</small>
              <small>创建时间：{{ formatDate(collection.created_at) }}</small>
            </div>

            <!-- 操作按钮 -->
            <div class="actions" v-if="isEditMode">
              <button class="edit-btn" @click.stop="handleEdit(collection)">编辑</button>
              <button class="delete-btn" @click.stop="handleDelete(collection.id)">删除</button>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="empty-state">
            {{ emptyStateText }}
          </div>
        </template>
      </div>

      <!-- 编辑/创建对话框 -->
      <div v-if="showDialog" class="dialog-overlay">
        <div class="dialog-content">
          <h3>{{ isEditing ? '编辑课程' : '新建课程' }}</h3>
          <form @submit.prevent="submitForm">
            <div class="form-group">
              <label>课程名称</label>
              <input
                  v-model="formData.name"
                  required
                  maxlength="50"
                  placeholder="请输入课程名称"
              />
            </div>
            <div class="form-group">
              <label>课程描述</label>
              <textarea
                  v-model="formData.description"
                  rows="3"
                  maxlength="200"
                  placeholder="请输入课程描述"
              ></textarea>
            </div>
            <div class="form-group">
              <label>缩略图</label>
              <input
                  type="file"
                  @change="handleThumbnailUpload"
                  accept="image/*"
              />
            </div>
            <div class="dialog-actions">
              <button type="button" @click="closeDialog">取消</button>
              <button type="submit">{{ isEditing ? '保存修改' : '创建合辑' }}</button>
            </div>
          </form>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading">加载中...</div>
    </div>
  </div>
</template>

<script>
import api from '../api/service';
import dayjs from 'dayjs';
export default {
  name: 'CollectionList',
  data() {
    return {
      collections: [],
      showDialog: false,
      isEditing: false,
      loading: false,
      formData: { id: null, name: '', description: '', thumbnail: '' },
      isEditMode: false,
      currentFilter: 'all',
      currentFetchId: 0,
      abortController: null
    };
  },
  computed: {
    emptyStateText() {
      return {
        all: '暂无数据',
        created: '暂无我教的课',
        favorite: '暂无我学的课'
      }[this.currentFilter];
    }
  },
  async created() {
    await this.fetchCollections();
  },
  methods: {
    formatDate(timestamp) {
      try {
        return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss');
      } catch {
        return '无效日期';
      }
    },

    async fetchCollections() {
      if (this.abortController) {
        this.abortController.abort();
      }

      this.abortController = new AbortController();
      const fetchId = ++this.currentFetchId;
      this.loading = true;

      try {
        let res;
        const user = JSON.parse(localStorage.getItem('user')) || {};
        // 确保获取favoriteIds完成
        const favoriteResponse = await api.getFavoriteCollections();
        const favoriteIds = favoriteResponse.data.map(item => item.id);
        if (this.currentFilter === 'all') {
          res = await api.getCollections();
          this.collections = await Promise.all(res?.data.map(async c => ({
            ...c,
            creator: (await api.getUserName(Number(c.creator))).data[0],
            isFavorite: favoriteIds.includes(c.id)
          }))) || [];
        } else if (this.currentFilter === 'created') {
          res = await api.getCreatedCollections();
          this.collections = await Promise.all(res?.data.map(async c => ({
            ...c,
            creator: (await api.getUserName(Number(c.creator))).data[0],
            isFavorite: favoriteIds.includes(c.id)
          }))) || [];
        } else if (this.currentFilter === 'favorite') {
          res = await api.getFavoriteCollections();
          this.collections = await Promise.all(res?.data.map(async c => ({
            ...c,
            creator: (await api.getUserName(Number(c.creator))).data[0],
            isFavorite: favoriteIds.includes(c.id)
          }))) || [];
        }
        //if (fetchId !== this.currentFetchId) return;

      } catch (err) {
        if (err.name !== 'AbortError' && this.currentFilter === 'all') {
          alert('加载失败');
        }
      } finally {
        if (fetchId === this.currentFetchId) {
          this.loading = false;
          this.abortController = null;
        }
      }
    },

    async filterCollections(filter) {
      if (this.currentFilter === filter) return;
      this.currentFilter = filter;
      await this.fetchCollections();
    },

    async submitForm() {
      try {
        const formData = new FormData();
        formData.append('name', this.formData.name);
        formData.append('description', this.formData.description);
        if (this.formData.thumbnail instanceof File) {
          formData.append('thumbnail', this.formData.thumbnail);
        }
        const user = JSON.parse(localStorage.getItem('user')) || {};
        formData.append('creator', user.id);

        if (this.isEditing) {
          formData.append('id', this.formData.id);
          const response = await api.updateCollection(this.formData.id, formData);
          const updatedCollection = response.data; // 获取更新后的数据

          // 更新本地数据
          const index = this.collections.findIndex(c => c.id === updatedCollection.id);
          if (index !== -1) {
            // 直接更新本地数据
            this.collections.splice(index, 1, updatedCollection);
          }
        } else {
          const response = await api.createCollection(formData);
          const newCollection = response.data; // 获取新创建的数据
          this.collections.unshift(newCollection); // 将新数据添加到列表开头
        }

        this.showDialog = false;
        alert('操作成功');
      } catch (err) {
        alert(err.message || '操作失败');
      }
    },

    async handleDelete(id) {
      if (!confirm('确定删除？')) return;
      try {
        await api.deleteCollection(id);
        this.collections = this.collections.filter((c) => c.id !== id);
        alert('删除成功');
      } catch {
        alert('删除失败');
      }
    },

    showCreateDialog() {
      this.formData = { name: '', description: '', thumbnail: '' };
      this.isEditing = false;
      this.showDialog = true;
    },

    handleEdit(collection) {
      this.formData = { ...collection };
      this.isEditing = true;
      this.showDialog = true;
    },

    closeDialog() {
      this.showDialog = false;
    },

    enterCollection(id) {
      this.$router.push(`/home/${id}`);
    },

    handleThumbnailUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      if (file.size > 1024 * 1024*10) {
        alert('图片大小不能超过10MB');
        event.target.value = '';
        return;
      }
      this.formData.thumbnail = file;

    },

    toggleEditMode() {
      this.isEditMode = !this.isEditMode;
    },
    async toggleFavorite(collection) {
      try {
        // 保存原始状态用于错误回退
        const originalIsFavorite = collection.isFavorite;

        // 立即更新UI状态
        collection.isFavorite = !originalIsFavorite;

        // 根据新状态调用对应API
        if (originalIsFavorite) {
          await api.unfavoriteCollection(collection.id);
        } else {
          await api.favoriteCollection(collection.id);
        }

        // 重新获取收藏列表以确保数据同步
        const favoriteResponse = await api.getFavoriteCollections();
        const favoriteIds = favoriteResponse.data.map(item => item.id);

        // 更新 collections 中的 isFavorite 状态
        this.collections = this.collections.map(c => ({
          ...c,
          isFavorite: favoriteIds.includes(c.id)
        }));

        // 特殊处理 "我学的课" 筛选状态
        if (this.currentFilter === 'favorite' && originalIsFavorite) {
          // 从收藏列表中移除已取消收藏的课程
          this.collections = this.collections.filter(c => c.id !== collection.id);
        }
      } catch (err) {
        // 如果 API 调用失败，回退到原始状态
        collection.isFavorite = originalIsFavorite;
        alert('操作失败，请重试');
      }
    }
  }
};
</script>

<style scoped>
/* 原有样式保持不变 */
.collection-container {
  display: flex;
  height: 100vh;
}

.filter-sidebar {
  position: fixed;
  top: 50%;
  left: 20px;
  transform: translateY(-50%);
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.filter-sidebar button {
  display: block;
  width: 150px;
  padding: 15px 20px;
  margin-bottom: 15px;
  background-color: #AFAC90;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.filter-sidebar button.active {
  background: linear-gradient(135deg, #514549, #AFAC90);
}

.filter-sidebar button:hover {
  background-color: #514549;
}

.collection-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  margin-left: 200px;
}

.toolbar {
  margin-bottom: 30px;
  text-align: left;
}

.create-btn {
  padding: 10px 25px;
  background: #AFAC90;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-mode-btn {
  padding: 10px 25px;
  background: #AFAC90;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.collection-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: flex-start;
}

.collection-item {
  flex: 1 1 calc(33% - 10px);
  display: flex;
  flex-direction: column;
  padding: 15px;
  background: #f8f5f0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  cursor: pointer;
  min-width: calc(30% - 15px);
  max-width: calc(30% - 15px);
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

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.edit-btn {
  padding: 8px 20px;
  background: #e6a23c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn {
  padding: 8px 20px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-content {
  background: white;
  padding: 25px;
  border-radius: 8px;
  width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.dialog-actions {
  margin-top: 20px;
  text-align: right;
}

.dialog-actions button {
  padding: 8px 20px;
  margin-left: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dialog-actions button[type="submit"] {
  background: #409eff;
  color: white;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty-state {
  width: 100%;
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 16px;
}
.collection-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin: 10px 0;
  color: #333;
}

.collection-info h2 {
  margin: 0 0 8px;
  color: #333;
  font-size: 1.1em;
  font-weight: 600;
  transition: color 0.3s ease; /* 给标题单独添加过渡 */
}

.collection-item:hover .collection-info h2 {
  color: #AFAC90; /* 使用主题色 */
}
.favorite-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
  transition: all 0.3s;
}

.favorite-btn .icon {
  color: #ff4757;
  font-size: 16px;
}

.favorite-btn:hover {
  transform: scale(1.1);
}

.collection-thumbnail {
  position: relative;
}
</style>
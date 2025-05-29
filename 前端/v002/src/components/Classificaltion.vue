<template>
  <div class="classification-container">
    <h3 class="section-title">{{ collectionName }} 课程单元</h3>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-tip">加载中...</div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-tip">
      {{ error }}
      <el-button type="text" @click="retryLoad">重试</el-button>
    </div>

    <!-- 数据展示 -->
    <div v-else class="category-scroll">
      <div class="action-buttons">
      <button v-if="isCreator" class="add-category" @click="handleAddCategory">
        <el-icon-plus class="el-icon-plus" />新增单元
      </button>
        <button v-if="isCreator" class="toggle-delete-buttons" @click="toggleDeleteButtons">
          <el-icon-delete />
        </button>
      </div>
      <template v-for="(category, index) in categories" :key="category.id">
        <div
            class="category-item"
            :class="{
            'active': activeCategory === category.id
          }"
            @click="handleCategoryClick(category)"
        >
          <div class="category-content">
            <span class="order">第{{ index + 1 }}单元</span> <!-- 动态生成序号 -->
            <span class="name">{{ category.name }}</span>
            <span v-if="category.progress" class="progress">
              {{ category.progress }}%
            </span>
          </div>
          <div v-if="isCreator && showDeleteButtons" class="delete-category" @click.stop="handleDeleteCategory(category)">
            <button class="delete-btn"><el-icon-delete /></button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import api from '../api/service';
import axios from 'axios';
import SvgIcon from '../components/SvgIcon.vue';
import { ElButton, ElMessageBox } from 'element-plus';
import {Delete, Plus} from '@element-plus/icons-vue';

export default {
  name: 'ClassificationA',
  components: {
    SvgIcon,
    ElButton,
    'el-icon-delete': Delete,
    'el-icon-plus': Plus,
  },
  props: {
    collectionId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      categories: [],
      activeCategory: null,
      collectionName: '',
      cancelToken: null,
      cacheKey: `classification_${this.collectionId}`,
      isCreator: false,
      showDeleteButtons: false
    };
  },
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user')) || {};
    }
  },
  watch: {
    collectionId: {
      immediate: true,
      handler() {
        this.loadData();
      }
    }
  },
  mounted() {
    this.loadData().then(() => {
      if (this.categories.length > 0) {
        this.handleCategoryClick(this.categories[0]);
      }
    });
  },
  methods: {
    async loadData() {
      if (this.cancelToken) {
        this.cancelToken.cancel('请求已取消');
      }
      const CancelToken = axios.CancelToken;
      this.cancelToken = CancelToken.source();

      try {
        this.loading = true;
        this.error = null;
        const data=(await api.getCollection(this.collectionId)).data
        // 检查缓存
        const cachedData = localStorage.getItem(this.cacheKey);
        if (cachedData) {
          const { categories, collectionName } = JSON.parse(cachedData);
          this.isCreator = data.creator === this.user.id;
          this.categories = categories;
          this.collectionName = collectionName;
          this.activeCategory = null;
          return;
        }

        // 获取合辑详情
        const { data: collection } = await api.getCollection(this.collectionId, {
          cancelToken: this.cancelToken.token
        });

        if (!collection?.categories) {
          throw new Error('无效的课程数据');
        }

        this.categories = collection.categories || [];
        this.collectionName = collection.name || '未知课程';
        this.activeCategory = null;

        // 缓存数据
        localStorage.setItem(this.cacheKey, JSON.stringify({
          categories: this.categories,
          collectionName: this.collectionName
        }));
      } catch (error) {
        if (axios.isCancel(error)) {
          console.log('请求取消:', error.message);
          return;
        }
        console.error('[课程单元数据加载失败]', error);
        this.error = error.message || '数据加载失败，请稍后重试';
        this.showErrorMsg(this.error);
      } finally {
        this.loading = false;
        this.cancelToken = null;
      }
    },
    // 新增分类
    async handleAddCategory() {
      try {
        const { value: name } = await ElMessageBox.prompt('请输入单元名称', '新增单元', {
          inputPattern: /^.{1,20}$/,
          inputErrorMessage: '单元名称长度应在1到20个字符之间'
        });

        const newCategory = {
          name,
          collection: Number(this.collectionId),
          progress: 0
        };
        // 调用API创建分类
        const { data: createdCategory } = await api.createCategory(JSON.stringify(newCategory));

        // 更新本地数据
        this.categories = [...this.categories, createdCategory]; // 使用展开运算符确保响应式更新

        // 更新缓存
        localStorage.setItem(this.cacheKey, JSON.stringify({
          categories: this.categories,
          collectionName: this.collectionName,
          isCreator: this.isCreator
        }));

        this.showErrorMsg('单元创建成功', 'success');
      } catch (error) {
        if (error !== 'cancel') {
          this.showErrorMsg(error.message || '单元创建失败');
        }
      }
    },

    // 删除分类
    async handleDeleteCategory(category) {
      try {
        await ElMessageBox.confirm(`确定要删除单元 "${category.name}" 吗？`, '删除单元', {
          type: 'warning'
        });

        // 调用API删除课程单元
        await api.deleteCategory(category.id);

        // 更新本地数据
        this.categories = this.categories.filter(c => c.id !== category.id); // 过滤掉已删除的分类

        // 更新缓存
        localStorage.setItem(this.cacheKey, JSON.stringify({
          categories: this.categories,
          collectionName: this.collectionName,
          isCreator: this.isCreator
        }));

        this.showErrorMsg('单元删除成功', 'success');
      } catch (error) {
        if (error !== 'cancel') {
          this.showErrorMsg(error.message || '单元删除失败');
        }
      }
    },

    handleCategoryClick(category) {
      this.activeCategory = category.id;
      this.$emit('category-change', {
        collectionId: this.collectionId,
        categoryId: category.id
      });
    },

    retryLoad() {
      this.loadData();
    },

    showErrorMsg(message, type = 'error') {
      if (typeof this.$message?.[type] === 'function') {
        this.$message[type](message);
      } else {
        alert(message);
      }
    },
    toggleDeleteButtons() {
      this.showDeleteButtons = !this.showDeleteButtons;
    }
  }
};
</script>

<style scoped>
.add-category {
  display: flex;
  align-items: center;
  font-size: 20px;
  white-space: nowrap;
  min-width: 132px;
  max-height: 50px;
  border: #2c3e50;
  background: white;
  color: #2c3e50;
}
.el-icon-plus{
  max-width: 50px;
}
/* 删除分类按钮样式 */
.delete-category {
  margin-left: 8px;
}
.delete-btn {
  background: red;
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
.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.toggle-delete-buttons {
  display: flex;
  align-items: center;
  font-size: 20px;
  white-space: nowrap;
  min-width: 50px;
  max-height: 50px;
  border: #2c3e50;
  background: white;
  color: #2c3e50;
}
/* 提示信息样式 */
.loading-tip,
.error-tip {
  padding: 20px;
  text-align: center;
  color: #666;
}

.error-tip {
  color: #f56c6c;
}

/* 分类容器样式 */
.category-scroll {
  height: calc(100vh - 50px);
  overflow-y: auto;
}

/* 分类项基础样式 */
.category-item {
  padding: 16px;
  margin: 8px 0;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  background-color: #f5f7fa;
}

/* 分类内容样式 */
.category-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order {
  font-size: 14px;
  color: #666;
}

.name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.progress {
  font-size: 14px;
  color: #409eff;
}

/* 激活状态样式 */
.category-item.active {
  background-color: #409eff;
  color: #ffffff;
}

.category-item.active .order,
.category-item.active .name,
.category-item.active .progress {
  color: inherit;
}

.category-item.active:hover {
  background-color: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .classification-container {
    width: 100%;
    box-shadow: none;
  }

  .category-scroll {
    height: auto;
    max-height: 60vh;
  }

  .category-item {
    padding: 12px;
    margin: 6px 0;
  }

  .name {
    font-size: 14px;
  }

  .order,
  .progress {
    font-size: 12px;
  }
}
</style>
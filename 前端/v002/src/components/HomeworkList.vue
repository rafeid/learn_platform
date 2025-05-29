<template>
  <div class="homework-container">
    <div class="section-header">
      <h2>课后作业列表</h2>
    </div>

    <div class="homework-list">
      <div
          v-for="(item, index) in homeworkData"
          :key="index"
          class="homework-item"
          @click="handleItemClick(item)"
      >
        <div class="content">
          <span class="index">作业 {{ index + 1 }}</span>
          <h3 class="title">{{ item.title }}</h3>
          <p class="description">{{ item.description }}</p>
          <div class="meta">
            <span class="deadline">截止时间：{{ formatDate(item.deadline) }}</span>
          </div>
        </div>
        <!-- 编辑和删除按钮 -->
        <div v-if="isCreator" class="homework-actions">
          <button class="edit-btn" @click.stop="openEditHomeworkModal(item)">
            <el-icon-edit />
          </button>
          <button class="delete-btn" @click.stop="deleteHomework(item)">
            <el-icon-delete />
          </button>
        </div>
      </div>
    </div>

    <!-- 添加作业按钮 -->
    <button v-if="isCreator" class="add-homework-btn" @click="openAddHomeworkModal">
      <el-icon-plus />
    </button>

    <!-- 添加作业弹窗 -->
    <el-dialog
        v-model="addHomeworkModalVisible"
        title="添加作业"
        width="50%"
        @close="resetAddHomeworkForm"
    >
      <el-form :model="addHomeworkForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="addHomeworkForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="addHomeworkForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="截止时间" required>
          <el-date-picker
              v-model="addHomeworkForm.deadline"
              type="datetime"
              placeholder="选择截止时间"
              value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addHomeworkModalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddHomework">提交</el-button>
      </template>
    </el-dialog>

    <!-- 编辑作业弹窗 -->
    <el-dialog
        v-model="editHomeworkModalVisible"
        title="编辑作业"
        width="50%"
        @close="resetEditHomeworkForm"
    >
      <el-form :model="editHomeworkForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editHomeworkForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="editHomeworkForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="截止时间" required>
          <el-date-picker
              v-model="editHomeworkForm.deadline"
              type="datetime"
              placeholder="选择截止时间"
              value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editHomeworkModalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditHomework">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api/service'
import { Edit, Delete, Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs';


export default {
  name: 'HomeworkList',
  components: {
    'el-icon-edit': Edit,
    'el-icon-delete': Delete,
    'el-icon-plus': Plus,
  },
  props: {
    collectionId: Number,
    categoryId: Number,
  },
  data() {
    return {
      homeworkData: [],
      currentRequestId: 0,
      isCreator: false,

      // 添加作业弹窗相关
      addHomeworkModalVisible: false,
      addHomeworkForm: {
        title: '',
        description: '',
        deadline: '',
        categoryId: this.categoryId,
      },

      // 编辑作业弹窗相关
      editHomeworkModalVisible: false,
      editHomeworkForm: {
        id: null,
        title: '',
        description: '',
        deadline: '',
      },
    }
  },
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user')) || {}
    },
  },
  watch: {
    categoryId: {
      handler: 'loadHomework',
      immediate: true,
    },
  },
  methods: {
    formatDate(timestamp) {
      try {
        return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss');
      } catch {
        return '无效日期';
      }
    },
    async loadHomework(categoryId) {
      const requestId = ++this.currentRequestId
      try {
        const [resources, collection] = await Promise.all([
          api.getCategoryResources(categoryId),
          api.getCollection(this.collectionId),
        ])
        if (requestId === this.currentRequestId) {
          this.isCreator = collection.data.creator === this.user.id
          this.homeworkData = resources.data.homeworks || []
        }
      } catch (error) {
        if (requestId === this.currentRequestId) {
          const errorMessage = error.message || '作业加载失败'
          console.error('[作业数据]', errorMessage, error)
          this.$message?.error?.(errorMessage)
        }
      }
    },

    handleItemClick(item) {
      this.navigateToDetail(item.id)
    },

    navigateToDetail(homeworkId) {
      this.$router.push({
        path: `/homework/${homeworkId}`,
        query: {
          collectionId: this.collectionId,
          categoryId: this.categoryId,
        },
      })
    },

    // 打开添加作业弹窗
    openAddHomeworkModal() {
      this.addHomeworkModalVisible = true
    },

    // 提交添加作业表单
    async submitAddHomework() {
      try {
        const formData = new FormData();
        formData.append('title', this.addHomeworkForm.title);
        formData.append('description', this.addHomeworkForm.description);
        formData.append('deadline', dayjs(this.addHomeworkForm.deadline).format('YYYY-MM-DD HH:mm:ss'));
        formData.append('category', this.addHomeworkForm.categoryId);

        await api.addHomework(formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        this.addHomeworkModalVisible = false;
        await this.loadHomework(this.categoryId);
        this.$message.success('作业添加成功！');
      } catch (error) {
        console.error('添加作业失败:', error);
        this.$message.error('添加作业失败，请稍后重试');
      }
    },

    // 重置添加作业表单
    resetAddHomeworkForm() {
      this.addHomeworkForm = {
        title: '',
        description: '',
        deadline: '',
        categoryId: this.categoryId,
      }
    },

    // 打开编辑作业弹窗
    openEditHomeworkModal(homework) {
      this.editHomeworkForm = {
        id: homework.id,
        title: homework.title,
        description: homework.description,
        deadline: dayjs(homework.deadline).toDate(), // 将字符串日期转换为 Date 对象
      };
      this.editHomeworkModalVisible = true;
    },

    // 提交编辑作业表单
    async submitEditHomework() {
      try {
        const formData = new FormData();
        formData.append('title', this.editHomeworkForm.title);
        formData.append('description', this.editHomeworkForm.description);
        formData.append('deadline', dayjs(this.editHomeworkForm.deadline).format('YYYY-MM-DD HH:mm:ss'));
        formData.append('id', this.editHomeworkForm.id);

        await api.updateHomework(this.editHomeworkForm.id, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        this.editHomeworkModalVisible = false;
        await this.loadHomework(this.categoryId);
        this.$message.success('作业更新成功！');
      } catch (error) {
        console.error('更新作业失败:', error);
        this.$message.error('更新作业失败，请稍后重试');
      }
    },

    // 重置编辑作业表单
    resetEditHomeworkForm() {
      this.editHomeworkForm = {
        id: null,
        title: '',
        description: '',
        deadline: '',
      }
    },

    async deleteHomework(homework) {
      try {
        await api.deleteHomework(homework.id)
        this.homeworkData = this.homeworkData.filter((item) => item.id !== homework.id)
      } catch (error) {
        console.error('删除作业失败:', error)
        this.$message?.error?.('删除作业失败，请稍后重试')
      }
    },
  },
}
</script>

<style scoped>
.homework-container {
  padding: 20px;
  position: relative;
}

.section-header {
  margin-bottom: 24px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.homework-list {
  display: grid;
  gap: 16px;
}

.homework-item {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.homework-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.title {
  margin: 8px 0;
  color: #333;
}

.description {
  color: #666;
  font-size: 14px;
}

.meta {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  font-size: 12px;
}

.deadline {
  color: #999;
}


.homework-actions {
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

.add-homework-btn {
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

.add-homework-btn:hover {
  background: rgba(0, 0, 0, 1);
}
</style>
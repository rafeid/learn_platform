<template>
  <div class="material-container">
    <div class="section-header">
      <h2>学习资料库</h2>
    </div>

    <div class="material-grid">
      <div v-for="(item, index) in materialData" :key="index" class="material-card">
        <div class="card-header">
          <h3 class="title">{{ item.title }}</h3>
        </div>
        <p class="description">{{ item.description }}</p>
        <div class="card-footer">
          <span class="date">{{ formatDate(item.date) }}</span>
          <div class="actions" >
            <button class="download-btn" @click="handleDownload(item)">下载</button>
<!--            <button class="preview-btn" @click="handlePreview(item)">预览</button>-->
            <div v-if="isCreator">
              <button class="edit-btn" @click.stop="openEditMaterialModal(item)">编辑</button>
              <button class="delete-btn" @click.stop="deleteMaterial(item)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加资料按钮 -->
    <button v-if="isCreator" class="add-material-btn" @click="openAddMaterialModal">
      <el-icon-plus />
    </button>

    <!-- 添加资料弹窗 -->
    <el-dialog
        v-model="addMaterialModalVisible"
        title="添加资料"
        width="50%"
        @close="resetAddMaterialForm"
    >
      <el-form :model="addMaterialForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="addMaterialForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="addMaterialForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="文件" required>
          <el-upload
              :action="uploadUrl"
              :on-success="handleFileSuccess"
              :before-upload="beforeFileUpload"
              :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
          <span v-if="addMaterialForm.url" class="file-preview">文件已上传</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMaterialModalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddMaterial">提交</el-button>
      </template>
    </el-dialog>

    <!-- 编辑资料弹窗 -->
    <el-dialog
        v-model="editMaterialModalVisible"
        title="编辑资料"
        width="50%"
        @close="resetEditMaterialForm"
    >
      <el-form :model="editMaterialForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editMaterialForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="editMaterialForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="文件" required>
          <el-upload
              :http-request="handleUploadFile"
              :on-success="handleFileSuccess"
              :before-upload="beforeFileUpload"
              :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
          <span v-if="editMaterialForm.url" class="file-preview">文件已上传</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editMaterialModalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditMaterial">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from "../api/service";
import { Plus } from '@element-plus/icons-vue';
import axios from "axios";
import dayjs from "dayjs";

export default {
  name: 'MaterialList',
  components: {
    'el-icon-plus': Plus,
  },
  props: {
    collectionId: Number,
    categoryId: Number
  },
  data() {
    return {
      materialData: [],
      addMaterialModalVisible: false,
      addMaterialForm: {
        title: '',
        description: '',
        url: '',
        date: new Date().toLocaleDateString(),
        categoryId: this.categoryId,
        creatorId: JSON.parse(localStorage.getItem('user'))?.id || null,
      },
      editMaterialModalVisible: false,
      editMaterialForm: {
        id: null,
        title: '',
        description: '',
        url: '',
        date: '',
        creatorId: JSON.parse(localStorage.getItem('user'))?.id || null,
      },
      uploadUrl: 'http://localhost:8000/api/upload/', // 替换为实际的上传接口地址
      isCreator: false,
    }
  },
  async created() {
    await this.loadMaterials();
    await this.checkCreator();
  },

  methods: {
    formatDate(timestamp) {
      try {
        return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss');
      } catch {
        return '无效日期';
      }
    },
    async loadMaterials() {
      try {
        const { data } = await api.getCategoryResources(this.categoryId);
        this.materialData = data.materials || [];
      } catch (error) {
        console.error('资料加载失败:', error);
      }
    },
    async checkCreator() {
      try {
        const user = JSON.parse(localStorage.getItem('user')) || {};
        const collection = await api.getCollection(this.collectionId);
        this.isCreator = collection.data.creator === user.id;
      } catch (error) {
        console.error('获取创建者信息失败:', error);
      }
    },
    async handleUploadFile({ file }) {
      try {
        const response = await api.uploadFile(file);
        if (response.data && response.data.url) {
          this.addMaterialForm.url = response.data.url; // 更新添加表单的文件URL
          this.editMaterialForm.url = response.data.url; // 更新编辑表单的文件URL
          this.$message.success('文件上传成功！');
        } else {
          throw new Error('上传失败，未获取到文件 URL');
        }
      } catch (error) {
        console.error('文件上传失败:', error);
        this.$message.error('文件上传失败，请稍后重试');
      }
    },
    decodeFilename(header) {
      if (!header) return null;

      // 检查是否是 filename* 格式
      if (header.includes('filename*=')) {
        const encoded = header.split('filename*=')[1].split(';')[0];
        return decodeURIComponent(encoded.replace(/UTF-8''/, ''));
      }

      // 默认情况，直接提取 filename
      const match = header.match(/filename="([^"]+)"/);
      if (match) {
        return decodeURIComponent(match[1]);
      }

      return null;
    },
    async handleDownload(item) {
      try {
        const response = await axios.get(`http://localhost:8000/api/materials/${item.id}/download/`, {
          responseType: 'blob', // 确保响应类型是 blob
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`, // 携带 token
          },
        });

        // 检查响应头是否存在
        if (!response.headers) {
          throw new Error('响应头未返回');
        }

        // 解析文件名
        const contentDisposition = response.headers['content-disposition'];
        let filename = this.decodeFilename(contentDisposition) || item.title || 'file';

        // 提取文件后缀
        const fileExtension = filename.split('.').pop(); // 获取文件后缀（如 docx）
        const newFilename = `${item.title}.${fileExtension}`; // 新文件名：item.title + 文件后缀

        // 创建 Blob URL
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', newFilename); // 设置下载文件名
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url); // 释放内存
      } catch (error) {
        console.error('文件下载失败:', error);
        this.$message.error('文件下载失败，请稍后重试');
      }
    },
    //
    // handlePreview(item) {
    //   if (item.url) {
    //     if (item.url.endsWith('.pdf')) {
    //       // PDF 文件使用 iframe 预览
    //       window.open(item.url, '_blank');
    //     } else if (item.url.match(/\.(jpg|jpeg|png|gif)$/)) {
    //       // 图片文件直接在新标签页打开
    //       window.open(item.url, '_blank');
    //     } else if (item.url.endsWith('.mp4')) {
    //       // 视频文件使用 video 标签预览
    //       const videoUrl = item.url;
    //       const videoElement = document.createElement('video');
    //       videoElement.src = videoUrl;
    //       videoElement.controls = true;
    //       document.body.appendChild(videoElement);
    //       videoElement.play();
    //     } else {
    //       this.$message.error('不支持预览该文件类型');
    //     }
    //   } else {
    //     this.$message.error('文件链接无效');
    //   }
    // },
    openAddMaterialModal() {
      this.addMaterialModalVisible = true;
    },
    async submitAddMaterial() {
      try {
        const formData = new FormData();
        formData.append('title', this.addMaterialForm.title);
        formData.append('description', this.addMaterialForm.description);
        formData.append('categoryId', this.addMaterialForm.categoryId);

        // 处理文件上传
        if (this.addMaterialForm.url) {
          formData.append('url', this.addMaterialForm.url);
        }

        const response = await api.addMaterial(formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        this.addMaterialModalVisible = false;
        await this.loadMaterials();
        this.$message.success('资料添加成功！');
      } catch (error) {
        console.error('添加资料失败:', error);
        this.$message.error('添加资料失败，请稍后重试');
      }
    },
    resetAddMaterialForm() {
      this.addMaterialForm = {
        title: '',
        description: '',
        type: '',
        url: '',
        date: new Date().toLocaleDateString(),
        categoryId: this.categoryId,
        creatorId: JSON.parse(localStorage.getItem('user'))?.id || null,
      };
    },
    openEditMaterialModal(item) {
      if (!this.isCreator) {
        this.$message.error('只有创建者可以编辑资料');
        return;
      }
      this.editMaterialForm = { ...item };
      this.editMaterialModalVisible = true;
    },
    async submitEditMaterial() {
      try {
        const formData = new FormData();
        formData.append('title', this.editMaterialForm.title);
        formData.append('description', this.editMaterialForm.description);
        formData.append('categoryId', this.editMaterialForm.categoryId);
        formData.append('creatorId', this.editMaterialForm.creatorId);

        // 处理文件上传
        if (this.editMaterialForm.url) {
          formData.append('url', this.editMaterialForm.url);
        }

        const response = await api.updateMaterial(this.editMaterialForm.id, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        this.editMaterialModalVisible = false;
        await this.loadMaterials();
        this.$message.success('资料更新成功！');
      } catch (error) {
        console.error('更新资料失败:', error);
        this.$message.error('更新资料失败，请稍后重试');
      }
    },
    resetEditMaterialForm() {
      this.editMaterialForm = {
        id: null,
        title: '',
        description: '',
        type: '',
        url: '',
        date: '',
        creatorId: JSON.parse(localStorage.getItem('user'))?.id || null,
      };
    },
    async deleteMaterial(item) {
      try {
        if (!this.isCreator) {
          this.$message.error('只有创建者可以删除资料');
          return;
        }
        await api.deleteMaterial(item.id);
        this.materialData = this.materialData.filter(m => m.id !== item.id);
      } catch (error) {
        console.error('删除资料失败:', error);
      }
    },
    handleFileSuccess(response, file) {
      this.addMaterialForm.url = response.url; // 更新添加表单的文件URL
      this.editMaterialForm.url = response.url; // 更新编辑表单的文件URL
    },
    beforeFileUpload(file) {
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png','application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
      const isFileTypeValid = allowedTypes.includes(file.type);
      const isLt10M = file.size / 1024 / 1024 < 10;

      if (!isFileTypeValid) {
        this.$message.error('只能上传 PDF、Word、ppt 或图片文件');
      }
      if (!isLt10M) {
        this.$message.error('文件大小不能超过 10MB');
      }

      return isFileTypeValid && isLt10M;
    },
  }
}
</script>

<style scoped>
.material-container {
  padding: 20px;
}

.section-header {
  margin-bottom: 24px;
}



.filter-bar button {
  color: #AFAC90;
  padding: 4px 12px;
  border: 1px solid #AFAC90;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;

  &.active {
    border-color: #1890ff;
    color: #1890ff;
  }
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.material-card {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-header {
  margin-bottom: 12px;
}

.title {
  margin: 8px 0;
  color: #333;
}

.description {
  color: #666;
  font-size: 14px;
  height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.date {
  color: #999;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.download-btn,
.preview-btn,
.edit-btn,
.delete-btn {
  color: #AFAC90;
  padding: 4px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;

  &:hover {
    border-color: #1890ff;
    color: #1890ff;
  }
}

.add-material-btn {
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

.add-material-btn:hover {
  background: rgba(0, 0, 0, 1);
}

.file-preview {
  font-size: 12px;
  color: #666;
  margin-top: 10px;
}
</style>
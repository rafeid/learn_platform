<template>
  <div class="message-board">
    <h2>留言板</h2>
    <!-- 输入框 -->
    <div class="input-area">
      <textarea v-model="newMessage" placeholder="请输入留言内容"></textarea>
      <button @click="addMessage" class="a0">提交留言</button>
    </div>
    <!-- 留言列表 -->
    <ul class="message-list">
      <li v-for="(message, index) in messages" :key="index" class="message-item">
        <div class="message-content">
          <span class="message-time">{{ message.time }}</span>
          <p>{{ message.text }}</p>
        </div>
        <button @click="deleteMessage(index)" class="delete-btn">删除</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newMessage: '', // 新留言内容
      messages: [] // 留言列表
    };
  },
  methods: {
    // 添加留言
    addMessage() {
      if (this.newMessage.trim() === '') {
        alert('留言内容不能为空！');
        return;
      }
      const message = {
        text: this.newMessage,
        time: new Date().toLocaleString() // 获取当前时间
      };
      this.messages.push(message); // 添加到留言列表
      this.newMessage = ''; // 清空输入框
    },
    // 删除留言
    deleteMessage(index) {
      this.messages.splice(index, 1); // 从留言列表中移除
    }
  }
};
</script>

<style scoped>
.message-board {
  max-width: 800px;
  margin: 0 auto;
  padding: 35px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.input-area {
  margin-bottom: 20px;
}
.a0{
  float: right;
}
textarea {
  width: 100%;
  height: 100px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
}

button {
  margin-top: 10px;
  padding: 8px 16px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #66b1ff;
}

.message-list {
  list-style: none;
  padding: 0;
}

.message-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.message-item:last-child {
  border-bottom: none;
}

.message-content {
  flex: 1;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.delete-btn {
  background: #ff4d4f;
}

.delete-btn:hover {
  background: #ff7875;
}
</style>
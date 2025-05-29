<template>
  <div class="auth-container">
    <div class="auth-box">
      <!-- 模式切换标题 -->
      <h2>{{ isLoginMode ? '用户登录' : '用户注册' }}</h2>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <!-- 表单区域 -->
      <div class="input-group">
        <!-- 用户名输入 -->
        <input
            v-model="form.username"
            placeholder="用户名"
            :disabled="isSubmitting"
            @keyup.enter="handleSubmit"
        >

        <!-- 密码输入 -->
        <input
            v-model="form.password"
            type="password"
            placeholder="密码（至少6位）"
            :disabled="isSubmitting"
            @keyup.enter="handleSubmit"
        >

        <!-- 注册模式显示确认密码 -->
        <input
            v-if="!isLoginMode"
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            :disabled="isSubmitting"
            @keyup.enter="handleSubmit"
        >
      </div>

      <!-- 提交按钮 -->
      <button
          @click="handleSubmit"
          :disabled="isSubmitting || !formValid"
          :class="{ loading: isSubmitting }"
      >
        {{ isSubmitting ? '处理中...' : isLoginMode ? '登录' : '注册' }}
      </button>

      <!-- 模式切换链接 -->
      <p class="toggle-mode" @click="toggleMode">
        {{ isLoginMode ? '没有账号？立即注册' : '已有账号？立即登录' }}
      </p>
    </div>
  </div>
</template>

<script>
import api from '../api/service'

export default {
  name: 'AuthA',
  data() {
    return {
      isLoginMode: true,
      isSubmitting: false,
      errorMessage: '',
      form: {
        username: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  computed: {
    // 表单验证逻辑
    formValid() {
      const { username, password, confirmPassword } = this.form
      if (!username || !password) return false
      if (!this.isLoginMode) {
        return password.length >= 6 && password === confirmPassword
      }
      return password.length >= 6
    }
  },
  methods: {
    // 切换登录/注册模式
    toggleMode() {
      this.isLoginMode = !this.isLoginMode
      this.clearForm()
      this.errorMessage = ''
    },

    // 清空表单
    clearForm() {
      this.form = {
        username: '',
        password: '',
        confirmPassword: ''
      }
    },

    // 表单提交处理
    async handleSubmit() {
      if (!this.formValid || this.isSubmitting) return

      this.isSubmitting = true
      this.errorMessage = ''

      try {
        if (this.isLoginMode) {
          await this.handleLogin()
        } else {
          await this.handleRegister()
        }
      } catch (error) {
        this.errorMessage = error.message || '操作失败，请重试'
      } finally {
        this.isSubmitting = false
      }
    },

    // 登录处理
    async handleLogin() {
      const formData = JSON.stringify({
        username: this.form.username,
        password: this.form.password
      });

      try {
        const response = await api.login(formData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!response.data) throw new Error('用户名或密码错误');

        // 登录成功后存储完整的用户数据
        localStorage.setItem('user', JSON.stringify({
          token: response.data.token,
          id: response.data.user.id,
          username: response.data.user.username
        }));
        localStorage.setItem('token', response.data.token);

        this.redirectAfterLogin();
      } catch (error) {
        throw new Error(error.data.error || '登录失败，请重试');
      }
    },

    // 注册处理
    async handleRegister() {
      const formData = JSON.stringify({
        username: this.form.username,
        password: this.form.password
      });

      try {
        // 调用注册接口
        await api.register(formData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        // 注册成功后自动登录
        const loginResponse = await api.login(formData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        // 登录成功后存储完整的用户数据
        localStorage.setItem('user', JSON.stringify({
          token: loginResponse.data.token,
          id: loginResponse.data.user.id,
          username: loginResponse.data.user.username
        }));
        localStorage.setItem('token', loginResponse.data.token);

        this.redirectAfterLogin();
      } catch (error) {
        throw new Error(error.message || '注册失败，请重试');
      }
    },

    // 登录后重定向
    redirectAfterLogin() {
      const redirect = this.$route.query.redirect || '/'
      this.$router.replace(redirect)
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.auth-box {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.input-group {
  margin-bottom: 1.5rem;
}

input {
  width: 95%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #3498db;
  outline: none;
}

button {
  width: 100%;
  padding: 0.8rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.loading {
  position: relative;
  color: transparent;
}

.loading::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: 20px;
  height: 20px;
  border: 2px solid #fff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 0.8s linear infinite;
  transform: translate(-50%, -50%);
}

@keyframes spin {
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.toggle-mode {
  text-align: center;
  color: #3498db;
  margin-top: 1rem;
  cursor: pointer;
  transition: color 0.3s ease;
}

.toggle-mode:hover {
  color: #2980b9;
}

.error-message {
  color: #e74c3c;
  padding: 0.8rem;
  margin-bottom: 1rem;
  background: #f8d7da;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}
</style>
<template>
  <div>{{ message }}</div>
</template>

<script>
import api from '../api/service'

export default {
  data() {
    return {
      message: ''
    }
  },
  async created() {
    try {
      const response = await api.hello();
      this.message = response.data.message;
    } catch (error) {
      console.error('API调用失败:', error);
    }
  }
}
</script>
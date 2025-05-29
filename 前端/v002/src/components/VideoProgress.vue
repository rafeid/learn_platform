<template>
  <div>
    <h2 class="chart-title">我学的课视频学习进度</h2>
    <div class="button-container">
      <button
          v-for="course in courses"
          :key="course.id"
          @click="selectCourse(course)"
          :class="{ active: selectedCourse?.id === course.id }"
      >
        {{ course.name }}
      </button>
    </div>
    <div ref="chart" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import api from "../api/service";

export default {
  data() {
    return {
      courses: [],
      selectedCourse: null,
      // 新增视频数据
      videoStats: {
        completed: 0,
        total: 0
      }
    };
  },
  async mounted() {
    await this.fetchCourses();
    if (this.courses.length > 0) {
      this.selectCourse(this.courses[0]);
    }
  },
  methods: {
    async fetchCourses() {
      const response = await api.getCollections();
      this.courses = response.data.filter(c => c.is_favorited === true);
    },
    async selectCourse(course) {
      this.selectedCourse = course;
      // 获取该课程的视频数据
      const statsResponse = await api.getCourseVideoStats(course.id);
      this.videoStats = {
        completed: statsResponse.data.completed,
        total: statsResponse.data.total
      };
      this.renderChart();
    },
    renderChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        tooltip: {
          trigger: 'item',
        },
        title: {
          text: `${this.selectedCourse.name} 视频学习进度`,
          left: 'center'
        },
        series: [
          {
            name: '视频学习进度',
            type: 'pie',
            radius: '50%',
            data: [
              { value: this.videoStats.completed, name: '已学完' },
              { value: this.videoStats.total - this.videoStats.completed, name: '未学完' },
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
            label: {
              formatter: '{b}: {c} ({d}%)'
            }
          },
        ],
      };
      chart.setOption(option);
    },
  },
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.chart-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}
/* 按钮容器样式 */
.button-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

/* 按钮样式 */
button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #f0f0f0;
  color: #333;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

/* 按钮悬停效果 */
button:hover {
  background-color: #007bff;
  color: #fff;
  transform: scale(1.05);
}

/* 选中按钮样式 */
button.active {
  background-color: #007bff;
  color: #fff;
}
.chart {
  width: 100%;
  height: 400px;
}
</style>
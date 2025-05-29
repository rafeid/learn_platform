<template>
  <div>
    <!-- 标题 -->
    <h2 class="chart-title">我学的课成绩变化曲线</h2>
    <!-- 按钮容器 -->
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
    <!-- 图表容器 -->
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
      scores: [],
      homeworks: [],
    };
  },
  async mounted() {
    await this.fetchCourses();
    // 默认选中第一个按钮
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
      const response = await api.getCourseScores(course.id);
      this.scores = response.data;
      const homeworkPromises = this.scores.map(score => api.getHomework(score.homework));
      const homeworkResults = await Promise.all(homeworkPromises);
      // 将 homework 数据存储到 this.homeworks
      this.homeworks = homeworkResults.map(result => result.data);
      console.log(this.homeworks);
      this.renderChart();
    },
    renderChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: this.homeworks.map(homework => homework.title),
        },
        yAxis: {
          type: 'value',
        },
        series: [
          {
            data: this.scores.map(score => score.score),
            type: 'line',
          },
        ],
      };
      chart.setOption(option);
    },
  },
};
</script>

<style scoped>
/* 标题样式 */
.chart-title {
  text-align: center;
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

/* 图表样式 */
.chart {
  width: 100%;
  height: 400px;
  margin-bottom: 20px;
}
</style>
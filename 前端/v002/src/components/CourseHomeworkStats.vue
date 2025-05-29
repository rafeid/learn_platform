<template>
  <div>
    <!-- 标题 -->
    <h2 style="text-align: center;">我教的课学生成绩分布</h2>
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
      const user = JSON.parse(localStorage.getItem('user'));
      this.courses = response.data.filter(collection => collection.creator === user.id);
    },
    async selectCourse(course) {
      this.selectedCourse = course;
      const response = await api.getScoresByCourse({ course_id: course.id });
      this.scores = response.data;
      this.renderChart();
    },
    renderChart() {
      const chart = echarts.init(this.$refs.chart);

      // 计算成绩分布
      const scoreGroups = {};
      this.scores.forEach(score => {
        const scoreValue = Math.min(Math.floor(score.score / 10) * 10, 90); // 确保最大值不超过 90
        if (!scoreGroups[scoreValue]) {
          scoreGroups[scoreValue] = 0;
        }
        scoreGroups[scoreValue]++;
      });

      // 将分组数据转换为ECharts需要的格式
      const xAxisData = Object.keys(scoreGroups).map(key => {
        if (key === "90") {
          return "90-100"; // 最后一个区间改为 90-100
        } else {
          return `${key}-${parseInt(key) + 9}`;
        }
      });
      const yAxisData = Object.values(scoreGroups);

      const option = {
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          name: '成绩区间',
        },
        yAxis: {
          type: 'value',
          name: '数量',
        },
        series: [
          {
            data: yAxisData,
            type: 'bar',
            barWidth: '60%',
            itemStyle: {
              color: '#007bff', // 设置柱状图颜色
            },
          },
        ],
      };
      chart.setOption(option);
    }
  },
};
</script>

<style scoped>
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
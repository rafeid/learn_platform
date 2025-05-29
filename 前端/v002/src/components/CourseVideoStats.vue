<template>
  <div class="chart-container">
    <h2 class="chart-title">我教的课视频学习进度</h2>
    <div>
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
      <div class="chart-row">
        <div class="chart-container">
          <h3>视频进度Top10</h3>
          <div ref="topChart" class="chart"></div>
        </div>
        <div class="chart-container">
          <h3>视频进度倒数前十</h3>
          <div ref="bottomChart" class="chart"></div>
        </div>
      </div>
      <div class="chart-container">
        <h3>基本学完用户占比</h3>
        <div ref="pieChart" class="chart"></div>
      </div>
    </div>
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
      topData: [],
      bottomData: [],
      pieData: [],
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
      try {
        const response = await api.getPlaybackUse(course.id);
        const { top_10, bottom_10, pie_data } = response.data;
        this.topData = top_10;
        this.bottomData = bottom_10;
        this.pieData = pie_data;
        this.renderCharts();
      } catch (error) {
        console.error('获取数据失败:', error);
      }
    },
    renderCharts() {
      const topChart = echarts.init(this.$refs.topChart);
      const bottomChart = echarts.init(this.$refs.bottomChart);
      const pieChart = echarts.init(this.$refs.pieChart);

      const topOption = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%', // 在 tooltip 中显示百分比
        },
        xAxis: {
          type: 'category',
          data: this.topData.map(stat => stat.username),
          name: '用户', // 设置 x 轴名称
          nameLocation: 'center', // 名称位置
          nameGap: 25, // 名称与轴线的距离
          nameTextStyle: {
            fontSize: 14, // 名称字体大小
            fontWeight: 'bold', // 名称字体加粗
          },
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: {
            formatter: '{value}%', // 在 y 轴标签上显示百分比
          },
          name: '进度', // 设置 y 轴名称
          nameLocation: 'center', // 名称位置
          nameGap: 30, // 名称与轴线的距离
          nameTextStyle: {
            fontSize: 14, // 名称字体大小
            fontWeight: 'bold', // 名称字体加粗
          },
        },
        series: [
          {
            data: this.topData.map(stat => stat.progress),
            type: 'bar',
          },
        ],
      };

      const bottomOption = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%', // 在 tooltip 中显示百分比
        },
        xAxis: {
          type: 'category',
          data: this.bottomData.map(stat => stat.username),
          name: '用户', // 设置 x 轴名称
          nameLocation: 'center', // 名称位置
          nameGap: 25, // 名称与轴线的距离
          nameTextStyle: {
            fontSize: 14, // 名称字体大小
            fontWeight: 'bold', // 名称字体加粗
          },
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: {
            formatter: '{value}%', // 在 y 轴标签上显示百分比
          },
          name: '进度', // 设置 y 轴名称
          nameLocation: 'center', // 名称位置
          nameGap: 30, // 名称与轴线的距离
          nameTextStyle: {
            fontSize: 14, // 名称字体大小
            fontWeight: 'bold', // 名称字体加粗
          },
        },
        series: [
          {
            data: this.bottomData.map(stat => stat.progress),
            type: 'bar',
          },
        ],
      };

      const pieOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}人', // 在 tooltip 中显示百分比
        },
        series: [
          {
            name: '完成率',
            type: 'pie',
            radius: '50%',
            data: this.pieData,
          },
        ],
      };

      topChart.setOption(topOption);
      bottomChart.setOption(bottomOption);
      pieChart.setOption(pieOption);
    }
  },
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 980px; /* 增加最大宽度以适应两列布局 */
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}
.chart-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
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
/* 图表行样式 */
.chart-row {
  display: flex;
  gap: 10px; /* 减少图表之间的间距 */
  margin-bottom: -50px; /* 减少图表行与饼图之间的间距 */
}
/* 图表容器样式 */
.chart-container {
  flex: 1; /* 使两个图表平分宽度 */
  margin-right: 10px; /* 减少图表容器之间的间距 */
}
/* 图表标题样式 */
h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: -50px; /* 减少标题与图表之间的间距 */
}
/* 图表样式 */
.chart {
  width: 100%;
  height: 400px;
  margin-top: 5px; /* 如果需要，可以进一步调整图表与标题的间距 */
}
</style>
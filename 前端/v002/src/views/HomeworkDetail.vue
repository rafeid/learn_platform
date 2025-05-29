<template>
  <div class="homework-detail">
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div class="header">
        <h2>{{ homework.title }}</h2>
        <p>{{ homework.description }}</p>
      </div>

      <div v-if="isCreator">
        <h3>题目管理</h3>
        <question-editor :questions="questions" @save="handleSaveQuestions" />
      </div>
      <div v-else>
        <div v-if="showScoreList" class="score-container">
          <h3>成绩列表</h3>
          <ul class="score-list">
            <li v-for="(score, index) in scores" :key="index" class="score-item">
              <div class="score-info">
                <span class="score-number">第 {{ index + 1 }} 次成绩: {{ score.score }}</span>
                <span class="score-time">{{ score.submitted_at }}</span>
              </div>
            </li>
          </ul>
          <button @click="startNewAttempt" class="new-attempt-btn">重新作业</button>
        </div>
        <div v-else>
          <h3>答题区域</h3>
          <div v-if="showScore" class="score-display">
            <h4>您的得分：{{ score }}</h4>
          </div>
          <question-list
              :questions="questions"
              :show-score="showScore"
              @submit="submitAnswers"
              @back-to-score-list="backToScoreList"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import QuestionEditor from '../components/QuestionEditor.vue';
import QuestionList from '../components/QuestionList.vue';
import api from '../api/service';

export default {
  components: { QuestionEditor, QuestionList },
  props: {
    homeworkId: { type: Number, required: true }
  },
  data() {
    return {
      homework: {},
      questions: [],
      isCreator: false,
      loading: true,
      error: null,
      showScore: false,
      score: 0,
      showScoreList: false,
      scores: []
    };
  },
  async created() {
    await this.loadData();
    if (!this.isCreator) {
      await this.loadScores();
    }
  },
  methods: {
    async loadData() {
      try {
        const [homework, questions] = await Promise.all([
          api.getHomework(Number(this.homeworkId)),
          api.getHomeworkQuestions(Number(this.homeworkId))
        ]);
        if (!homework) {
          this.error = "未找到作业数据";
          return;
        }

        const user = JSON.parse(localStorage.getItem('user'));
        const ca=(await api.getCategory(homework.data.category)).data.collection
        const creator=(await api.getCollection(ca)).data.creator
        this.isCreator = creator === user.id;
        this.homework = homework.data;
        this.questions = questions.data || [];
        if (!this.isCreator) {
          const scores = await api.getCurrentUserScores(Number(this.homeworkId));
          this.scores = scores.data;
          this.showScoreList = this.scores.length > 0;
        }
      } catch (error) {
        this.error = "加载数据失败，请重试";
        console.error("加载数据失败:", error);
      } finally {
        this.loading = false;
      }
    },
    async handleSaveQuestions(questions) {
      try {
        await api.saveQuestions(Number(this.homeworkId),JSON.stringify({ questions }));
        this.questions = questions;
        this.$message.success("保存成功！");
      } catch (error) {
        console.error("保存失败:", error);
        this.$message.error("保存失败，请重试！");
      }
    },
    async submitAnswers(answers) {
      try {
        this.score = await api.submitAnswers(Number(this.homeworkId), JSON.stringify({answers}));
        this.score=this.score.data.score;
        this.showScore = true;
      } catch (error) {
        console.error("提交答案失败:", error);
        this.$message.error("提交答案失败，请重试！");
      }
    },
    startNewAttempt() {
      this.showScoreList = false;
      this.showScore = false;
    },
    async backToScoreList() {
      // 设置显示成绩列表
      this.showScoreList = true;
      this.showScore = false;
      // 重新加载成绩数据
      await this.loadScores();
    },
    async loadScores() {
      try {
        const scores = await api.getCurrentUserScores(Number(this.homeworkId));
        this.scores = scores.data;
      } catch (error) {
        console.error("加载成绩数据失败:", error);
        this.$message.error("加载成绩数据失败，请重试！");
      }
    }
  }
};
</script>

<style scoped>
.homework-detail {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}
.header {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}
.score-display {
  margin-top: 30px;
  padding: 20px;
  background: #e3f2fd;
  border-radius: 8px;
}
h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee;
}
.score-list {
  list-style: none;
  padding: 0;
}
.score-item {
  background: #fff;
  margin-bottom: 10px;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}
.score-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
.score-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.score-number {
  font-weight: bold;
  color: #2c3e50;
}
.score-time {
  color: #666;
  font-size: 0.9em;
}
.score-container{
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 200px;
}
.new-attempt-btn {
  justify-self: end;
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.new-attempt-btn:hover {
  background-color: #3aa876;
}
</style>
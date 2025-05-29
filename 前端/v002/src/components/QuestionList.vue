<template>
  <div class="question-list">
    <div v-for="(question, index) in questions" :key="index" class="question-item">
      <h4>题目 {{ index + 1 }} ({{ question.score }}分)</h4>
      <p class="question-content">{{ question.content }}</p>

      <!-- 单选题 -->
      <div v-if="question.type === 'single'" class="options">
        <label v-for="(option, optIndex) in question.options" :key="optIndex" class="option">
          <input type="radio" v-model="answers[index]" :value="option.text">
          {{ option.text }}
        </label>
      </div>

      <!-- 多选题 -->
      <div v-else-if="question.type === 'multi'" class="options">
        <label v-for="(option, optIndex) in question.options" :key="optIndex" class="option">
          <input type="checkbox" v-model="answers[index]" :value="option.text">
          {{ option.text }}
        </label>
      </div>
    </div>
    <button v-if="!showScore" class="submit-btn" @click="submit">提交答案</button>
    <button v-else class="back-to-score-btn" @click="backToScoreList">返回成绩列表</button>
  </div>
</template>

<script>
export default {
  props: {
    questions: {
      type: Array,
      required: true
    },
    showScore: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      answers: []
    };
  },
  watch: {
    questions: {
      immediate: true,
      handler(questions) {
        this.answers = questions.map(q => q.type === 'multi' ? [] : '');
      }
    }
  },
  methods: {
    submit() {
      const formattedAnswers = this.questions.map((q, index) => ({
        questionId: q.id,
        answer: this.answers[index]
      }));
      this.$emit('submit', formattedAnswers);
    },
    backToScoreList() {
      this.$emit('back-to-score-list');
    }
  }
};
</script>
<style scoped>
.question-list {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.question-item {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.question-item h4 {
  color: #333;
  font-size: 18px;
  margin-bottom: 10px;
}

.question-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.option {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.option input[type="radio"],
.option input[type="checkbox"] {
  margin-right: 8px;
  width: 16px;
  height: 16px;
}

.back-to-score-btn {
  display: block;
  width: 100%;
  padding: 12px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.back-to-score-btn:hover {
  background: #fb8c00;
}

.submit-btn {
  display: block;
  width: 100%;
  padding: 12px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.submit-btn:hover {
  background: #3aa87c;
}
</style>
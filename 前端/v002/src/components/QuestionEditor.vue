<template>
  <div class="question-editor">
    <div v-for="(question, qIndex) in workingQuestions" :key="qIndex" class="question-item">
      <h4>题目 {{ qIndex + 1 }}</h4>
      <div class="question-header">
        <input v-model="question.content" placeholder="请输入题目内容" class="question-input" />
        <select v-model="question.type" @change="handleTypeChange(qIndex)" class="type-select">
          <option value="single">单选题</option>
          <option value="multi">多选题</option>
        </select>
      </div>

      <div class="options-section">
        <div v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item">
          <input v-model="option.text" placeholder="输入选项内容" class="option-input" />
          <label class="correct-label">
            <input type="checkbox" v-model="option.isCorrect" class="correct-checkbox" />
            <span>正确答案</span>
          </label>
          <button @click="removeOption(qIndex, optIndex)" class="remove-option-btn">×</button>
        </div>
        <button @click="addOption(qIndex)" class="add-option-btn">+ 添加选项</button>
      </div>

      <div class="question-footer">
        <input v-model.number="question.score" type="number" min="0" placeholder="分值" class="score-input" />
        <button @click="removeQuestion(qIndex)" class="remove-question-btn">删除题目</button>
      </div>
    </div>

    <div class="editor-controls">
      <button @click="addQuestion" class="add-question-btn">+ 新增题目</button>
      <button @click="handleSave" class="save-btn">✓ 提交保存</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    questions: { type: Array, default: () => [] }
  },
  data() {
    return {
      workingQuestions: []
    };
  },
  watch: {
    questions: {
      immediate: true,
      handler(val) {
        if (val && val.length > 0) {
          this.workingQuestions = JSON.parse(JSON.stringify(val));
        } else {
          this.workingQuestions = [
            {
              content: "新题目",
              type: "single",
              options: [{ text: "", isCorrect: false }],
              score: 10
            }
          ];
        }
      }
    }
  },
  methods: {
    addQuestion() {
      this.workingQuestions.push({
        content: "新题目",
        type: "single",
        options: [{ text: "", isCorrect: false }],
        score: 10
      });
    },
    addOption(qIndex) {
      if (!this.workingQuestions[qIndex].options) {
        this.$set(this.workingQuestions[qIndex], "options", []);
      }
      this.workingQuestions[qIndex].options.push({ text: "", isCorrect: false });
    },
    removeOption(qIndex, optIndex) {
      this.workingQuestions[qIndex].options.splice(optIndex, 1);
    },
    removeQuestion(qIndex) {
      this.workingQuestions.splice(qIndex, 1);
    },
    handleTypeChange(qIndex) {
      const question = this.workingQuestions[qIndex];
      if (!question.options) {
        this.$set(question, "options", [{ text: "", isCorrect: false }]);
      }
    },
    handleSave() {
      const cleaned = this.workingQuestions.map(q => {
        return { ...q };
      });
      this.$emit("save", cleaned);
    }
  }
};
</script>

<style scoped>
.question-editor {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.question-item {
  margin-bottom: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  transition: box-shadow 0.2s;
}

.question-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.question-header {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.question-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.type-select {
  width: 150px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.options-section {
  margin: 20px 0;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.option-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.correct-label {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  white-space: nowrap;
}

.correct-checkbox {
  width: 16px;
  height: 16px;
  accent-color: #4CAF50;
}

.remove-option-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #ffebee;
  color: #ff5252;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.add-option-btn {
  margin-top: 10px;
  padding: 8px 15px;
  background: #e3f2fd;
  color: #2196F3;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.question-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.score-input {
  width: 100px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.remove-question-btn {
  padding: 8px 15px;
  background: #ffebee;
  color: #ff5252;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.editor-controls {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 15px;
}

.add-question-btn,
.save-btn {
  padding: 12px 25px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.add-question-btn:hover,
.save-btn:hover {
  opacity: 0.9;
}
</style>
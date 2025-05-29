<template>
  <div class="content-container">
    <div class="view-switch">
      <div
          v-for="tab in tabs"
          :key="tab.value"
          class="tab-item"
          :class="{ active: currentView === tab.value }"
          @click="switchTab(tab.value)"
      >
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>

    <div class="content-wrapper">
      <component
          :is="componentMap[currentView]"
          :key="currentView"
          :collection-id="collectionId"
          :category-id="categoryId"
      />
    </div>
  </div>
</template>

<script>
import VideoList from './VideoList.vue'
import HomeworkList from './HomeworkList.vue'
import MaterialList from './MaterialList.vue'

const STATIC_TABS = Object.freeze([
  { value: 'video', label: '视频课程' },
  { value: 'homework', label: '课后作业' },
  { value: 'material', label: '学习资料' }
])

const COMPONENT_MAP = Object.freeze({
  video: VideoList,
  homework: HomeworkList,
  material: MaterialList
})

export default {
  components: {
    VideoList,
    HomeworkList,
    MaterialList
  },
  props: {
    collectionId: { type: Number, default: 0 },
    categoryId: { type: Number, default: 0 }
  },
  data: () => ({
    currentView: 'video'
  }),
  computed: {
    tabs: () => STATIC_TABS,
    componentMap: () => COMPONENT_MAP
  },
  watch: {
    categoryId() {
      this.currentView = 'video'
    }
  },
  methods: {
    switchTab(view) {
      if (this.currentView !== view) {
        this.currentView = view
        this.$emit('view-change', view)
      }
    }
  }
}
</script>

<style scoped lang="scss">
$primary-color: #1890ff;
$badge-color: #f5222d;
$border-color: #f0f0f0;

.content-container {
  flex: 1;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.view-switch {
  display: flex;
  border-bottom: 1px solid $border-color;
  padding: 0 24px;
}

.tab-item {
  position: relative;
  padding: 16px 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s;

  &:hover {
    color: $primary-color;

    .badge {
      background: $primary-color;
    }
  }

  &.active {
    color: $primary-color;
    border-bottom: 2px solid $primary-color;
    margin-bottom: -1px;

    .badge {
      background: $primary-color;
    }
  }
}

.tab-label {
  font-size: 14px;
}

.badge {
  margin-left: 8px;
  background: $badge-color;
  color: white;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 12px;
  transition: background 0.3s;
}

.content-wrapper {
  padding: 24px;
  min-height: 600px;
}
</style>
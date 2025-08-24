<template>
  <div class="workspace-container">
    <!-- 左侧侧边导航栏 -->
    <WorkspaceSidebar 
      :active-item="activeTab"
      @item-select="handleTabSelect"
      @go-back="goBack"
    />

    <!-- 右侧主内容区域 -->
    <div class="workspace-main">
      <component 
        :is="currentComponent" 
        :mode="mode"
        :project-path="projectPath"
        :project-name="projectName"
        @go-back="goBack"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, markRaw } from 'vue';
import { useI18n } from 'vue-i18n';
import WorkspaceSidebar from '@/components/WorkspaceSidebar.vue';
import WorkspaceMain from './workspace/WorkspaceMain.vue';
import DeckBuilder from './workspace/DeckBuilder.vue';
import TTSItems from './workspace/TTSItems.vue';
import Settings from './workspace/Settings.vue';
import About from './workspace/About.vue';

// 国际化
const { t } = useI18n();

// Props
defineProps<{
  mode: 'file' | 'folder';
  projectPath?: string;
  projectName?: string;
}>();

// Emits
const emit = defineEmits<{
  'navigate-to-home': [];
}>();

// 当前活跃的标签页，默认显示工作区主页面
const activeTab = ref('workspace');

// 组件映射
const componentMap = {
  'workspace': markRaw(WorkspaceMain),
  'deck-builder': markRaw(DeckBuilder),
  'tts-items': markRaw(TTSItems),
  'settings': markRaw(Settings),
  'about': markRaw(About)
};

// 当前组件
const currentComponent = computed(() => {
  return componentMap[activeTab.value as keyof typeof componentMap] || WorkspaceMain;
});

// 处理标签页切换
const handleTabSelect = (key: string) => {
  activeTab.value = key;
};

// 返回首页
const goBack = () => {
  emit('navigate-to-home');
};
</script>

<style scoped>
.workspace-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f8f9fa;
}

.workspace-main {
  flex: 1;
  overflow: hidden;
}

@media (max-width: 768px) {
  .workspace-container {
    flex-direction: column;
  }
  
  .workspace-main {
    flex: 1;
  }
}
</style>

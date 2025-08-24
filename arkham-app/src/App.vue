<script setup lang="ts">
import { ref, computed } from 'vue';
import { NConfigProvider, NGlobalStyle, NMessageProvider, darkTheme, zhCN, dateZhCN } from 'naive-ui';
import type { GlobalTheme } from 'naive-ui';
import HomePage from './pages/HomePage.vue';
import WorkspacePage from './pages/WorkspacePage.vue';

// 主题状态
const theme = ref<GlobalTheme | null>(null);

// 计算属性，方便传递给子组件
const isDark = computed(() => theme.value !== null);

// 切换主题的函数
const toggleTheme = () => {
  theme.value = theme.value === null ? darkTheme : null;
};

// ========== 页面路由状态 ==========
const currentPage = ref<'home' | 'workspace'>('home');

// 工作区页面参数
interface WorkspaceParams {
  mode: 'file' | 'folder';
  projectPath: string;
  projectName: string;
}

const workspaceParams = ref<WorkspaceParams>({
  mode: 'file',
  projectPath: '',
  projectName: ''
});

// 导航到工作区
const navigateToWorkspace = (params: WorkspaceParams) => {
  workspaceParams.value = params;
  currentPage.value = 'workspace';
};

// 返回首页
const navigateToHome = () => {
  currentPage.value = 'home';
};
</script>

<template>
  <n-config-provider :theme="theme" :locale="zhCN" :date-locale="dateZhCN">
    <n-global-style />
    <n-message-provider>
      <!-- 首页 -->
      <HomePage 
        v-if="currentPage === 'home'"
        :is-dark="isDark" 
        @toggle-theme="toggleTheme"
        @navigate-to-workspace="navigateToWorkspace"
      />
      
      <!-- 工作区页面 -->
      <WorkspacePage
        v-else-if="currentPage === 'workspace'"
        :mode="workspaceParams.mode"
        :project-path="workspaceParams.projectPath"
        :project-name="workspaceParams.projectName"
        :is-dark="isDark"
        @toggle-theme="toggleTheme"
        @navigate-to-home="navigateToHome"
      />
    </n-message-provider>
  </n-config-provider>
</template>

<style>
/* ================= 全局样式重置 ================= */
/* 
  从根源上禁止页面滚动，这是桌面端应用的关键。
  内容滚动应在各自的容器内处理。
*/
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden; /* 核心：禁止任何滚动 */
  font-family: 'v-sans', sans-serif; /* 使用 Naive UI 推荐的字体变量 */
}
</style>

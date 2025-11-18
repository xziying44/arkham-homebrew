<template>
  <div class="welcome-container">
    <!-- 隐藏的文件夹选择元素 -->
    <input ref="folderInput" type="file" webkitdirectory style="display: none" @change="handleFolderSelected">

    <!-- ============================================= -->
    <!-- 桌面端：左右分栏布局 -->
    <!-- ============================================= -->
    <template v-if="!isMobile">
      <!-- 左侧操作窗格 -->
      <div class="left-pane">
        <div class="left-content">
          <!-- 语言切换按钮 -->
          <div class="language-switcher-container">
            <n-dropdown :options="languageOptions" @select="handleLanguageChange" trigger="click">
              <n-button quaternary size="small" class="language-btn">
                <template #icon>
                  <n-icon :component="LanguageOutline" />
                </template>
                {{ currentLanguageLabel }}
              </n-button>
            </n-dropdown>
          </div>

          <!-- Logo 和标题 -->
          <div class="logo-area">
            <div class="logo-icon">
              <n-icon size="48" :component="ColorWand" color="white" />
            </div>
            <div class="logo-text">
              <h1>{{ $t('home.title') }}</h1>
              <p>{{ $t('home.subtitle') }}</p>
            </div>
          </div>

          <!-- 主要操作按钮 -->
          <div class="primary-action">
            <button class="open-folder-btn" @click="handleOpenFolder" :disabled="isSelecting">
              <div class="btn-icon">
                <n-icon size="28" :component="FolderOpenOutline" />
              </div>
              <div class="btn-content">
                <span class="btn-title">{{ $t('home.actions.openProject') }}</span>
                <span class="btn-desc">
                  {{ isSelecting ? $t('home.actions.selecting') : $t('home.actions.openProjectDesc') }}
                </span>
              </div>
              <div class="btn-arrow">
                <n-icon size="20" :component="ArrowForwardOutline" />
              </div>
            </button>
          </div>

          <!-- 服务状态指示器 -->
          <div class="service-status">
            <div class="status-item" :class="{ 'online': serviceOnline, 'offline': !serviceOnline }">
              <n-icon :component="serviceOnline ? CheckmarkCircle : AlertCircle" />
              <span>{{ serviceOnline ? $t('home.serviceStatus.connected') : $t('home.serviceStatus.disconnected')
                }}</span>
            </div>
            <div v-if="serviceOnline && hasWorkspace" class="status-item workspace-info">
              <n-icon :component="FolderOpenOutline" />
              <span>{{ $t('home.serviceStatus.workspace', { name: workspaceName }) }}</span>
            </div>
          </div>

          <!-- 快捷说明 -->
          <div class="quick-info">
            <div class="info-item">
              <n-icon :component="FileTrayFullOutline" color="#a855f7" />
              <span>{{ $t('home.features.lightweight') }}</span>
            </div>
            <div class="info-item">
              <n-icon :component="LayersOutline" color="#a855f7" />
              <span>{{ $t('home.features.workspace') }}</span>
            </div>
            <div class="info-item">
              <n-icon :component="ImageOutline" color="#a855f7" />
              <span>{{ $t('home.features.autoTTS') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容窗格 -->
      <div class="right-pane">
        <div class="content-wrapper">
          <header class="content-header">
            <div class="header-with-actions">
              <div>
                <h2>{{ $t('home.recentProjects.title') }}</h2>
                <p class="subtitle">{{ $t('home.recentProjects.subtitle') }}</p>
              </div>
              <div class="header-actions" v-if="recentDirectories.length > 0">
                <n-button size="small" quaternary @click="handleClearRecent" :loading="clearingRecent">
                  <template #icon>
                    <n-icon :component="TrashOutline" />
                  </template>
                  {{ $t('home.recentProjects.clearRecords') }}
                </n-button>
              </div>
            </div>
          </header>

          <!-- 最近项目列表容器 -->
          <div class="recent-list-container">
            <!-- 加载状态 -->
            <div v-if="loadingRecent" class="loading-state">
              <n-spin size="large" />
              <p>{{ $t('home.recentProjects.loading') }}</p>
            </div>

            <!-- 最近目录列表 -->
            <n-list v-else-if="recentDirectories.length > 0" hoverable clickable>
              <n-list-item v-for="directory in recentDirectories" :key="directory.path"
                @click="handleOpenRecent(directory)">
                <n-thing>
                  <template #header>{{ directory.name }}</template>
                  <template #description>
                    <div class="recent-item-details">
                      <span class="recent-item-path">{{ directory.path }}</span>
                      <span class="recent-item-time">{{ directory.formatted_time }}</span>
                    </div>
                  </template>
                  <template #action>
                    <n-button size="small" quaternary circle @click.stop="handleRemoveRecent(directory)"
                      :loading="removingRecentPath === directory.path">
                      <template #icon>
                        <n-icon :component="CloseOutline" />
                      </template>
                    </n-button>
                  </template>
                  <template #header-extra>
                    <n-icon class="hover-arrow" :component="ArrowForwardOutline" />
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>

            <!-- 空状态 -->
            <div v-else class="empty-state-enhanced">
              <div class="empty-icon">
                <n-icon :component="CubeOutline" size="64" color="#cbd5e1" />
              </div>

              <div class="empty-content">
                <h3 class="empty-title">{{ $t('home.recentProjects.emptyStateTitle') }}</h3>
                <p class="empty-description">{{ $t('home.recentProjects.emptyStateDescription') }}</p>

                <div class="empty-guide">
                  <p class="guide-title">{{ $t('home.recentProjects.emptyStateGuide') }}</p>
                  <ul class="guide-options">
                    <li>
                      <n-icon :component="FileTrayFullOutline" color="#667eea" />
                      <span>{{ $t('home.recentProjects.emptyStateOption1') }}</span>
                    </li>
                    <li>
                      <n-icon :component="FolderOpenOutline" color="#667eea" />
                      <span>{{ $t('home.recentProjects.emptyStateOption2') }}</span>
                    </li>
                  </ul>
                </div>

                <div class="empty-actions">
                  <n-button
                    type="primary"
                    size="large"
                    @click="handleOpenFolder"
                    :disabled="isSelecting || !serviceOnline"
                    :loading="isSelecting"
                  >
                    <template #icon>
                      <n-icon :component="FolderOpenOutline" />
                    </template>
                    {{ $t('home.actions.openProject') }}
                  </n-button>

                  <div v-if="!serviceOnline" class="service-warning">
                    <n-icon :component="AlertCircle" color="#f59e0b" />
                    <span>{{ $t('home.messages.serviceOffline') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ============================================= -->
    <!-- 手机端：单页面 + 切换按钮 -->
    <!-- ============================================= -->
    <template v-else>
      <!-- 手机端容器 -->
      <div class="mobile-container">
        <!-- 页面 1：打开文件夹页面 -->
        <div v-show="currentMobileView === 'main'" class="mobile-main-view">
          <!-- 语言切换按钮 -->
          <div class="mobile-language-switcher">
            <n-dropdown :options="languageOptions" @select="handleLanguageChange" trigger="click">
              <n-button quaternary size="small" class="language-btn">
                <template #icon>
                  <n-icon :component="LanguageOutline" />
                </template>
                {{ currentLanguageLabel }}
              </n-button>
            </n-dropdown>
          </div>

          <!-- Logo 和标题 -->
          <div class="mobile-logo-area">
            <div class="mobile-logo-icon">
              <n-icon size="64" :component="ColorWand" color="white" />
            </div>
            <div class="mobile-logo-text">
              <h1>{{ $t('home.title') }}</h1>
              <p>{{ $t('home.subtitle') }}</p>
            </div>
          </div>

          <!-- 主要操作按钮 -->
          <div class="mobile-primary-action">
            <button class="mobile-open-folder-btn" @click="handleOpenFolder" :disabled="isSelecting">
              <div class="mobile-btn-icon">
                <n-icon size="36" :component="FolderOpenOutline" />
              </div>
              <div class="mobile-btn-content">
                <span class="mobile-btn-title">{{ $t('home.actions.openProject') }}</span>
                <span class="mobile-btn-desc">
                  {{ isSelecting ? $t('home.actions.selecting') : $t('home.actions.openProjectDesc') }}
                </span>
              </div>
              <div class="mobile-btn-arrow">
                <n-icon size="24" :component="ArrowForwardOutline" />
              </div>
            </button>
          </div>

          <!-- 服务状态指示器 -->
          <div class="mobile-service-status">
            <div class="mobile-status-item" :class="{ 'online': serviceOnline, 'offline': !serviceOnline }">
              <n-icon :component="serviceOnline ? CheckmarkCircle : AlertCircle" />
              <span>{{ serviceOnline ? $t('home.serviceStatus.connected') : $t('home.serviceStatus.disconnected')
                }}</span>
            </div>
            <div v-if="serviceOnline && hasWorkspace" class="mobile-status-item workspace-info">
              <n-icon :component="FolderOpenOutline" />
              <span>{{ $t('home.serviceStatus.workspace', { name: workspaceName }) }}</span>
            </div>
          </div>

          <!-- 快捷说明 -->
          <div class="mobile-quick-info">
            <div class="mobile-info-item">
              <n-icon :component="FileTrayFullOutline" color="#a855f7" />
              <span>{{ $t('home.features.lightweight') }}</span>
            </div>
            <div class="mobile-info-item">
              <n-icon :component="LayersOutline" color="#a855f7" />
              <span>{{ $t('home.features.workspace') }}</span>
            </div>
            <div class="mobile-info-item">
              <n-icon :component="ImageOutline" color="#a855f7" />
              <span>{{ $t('home.features.autoTTS') }}</span>
            </div>
          </div>
        </div>

        <!-- 页面 2：历史记录页面 -->
        <div v-show="currentMobileView === 'recent'" class="mobile-recent-view">
          <!-- 头部 -->
          <header class="mobile-content-header">
            <div class="mobile-header">
              <h2>{{ $t('home.recentProjects.title') }}</h2>
              <p class="mobile-subtitle">{{ $t('home.recentProjects.subtitle') }}</p>
            </div>
            <div class="mobile-header-actions" v-if="recentDirectories.length > 0">
              <n-button size="small" quaternary @click="handleClearRecent" :loading="clearingRecent">
                <template #icon>
                  <n-icon :component="TrashOutline" />
                </template>
                {{ $t('home.recentProjects.clearRecords') }}
              </n-button>
            </div>
          </header>

          <!-- 最近项目列表容器 -->
          <div class="mobile-recent-list-container">
            <!-- 加载状态 -->
            <div v-if="loadingRecent" class="loading-state">
              <n-spin size="large" />
              <p>{{ $t('home.recentProjects.loading') }}</p>
            </div>

            <!-- 最近目录列表 -->
            <n-list v-else-if="recentDirectories.length > 0" hoverable clickable>
              <n-list-item v-for="directory in recentDirectories" :key="directory.path"
                @click="handleOpenRecent(directory)">
                <n-thing>
                  <template #header>{{ directory.name }}</template>
                  <template #description>
                    <div class="recent-item-details">
                      <span class="recent-item-path">{{ directory.path }}</span>
                      <span class="recent-item-time">{{ directory.formatted_time }}</span>
                    </div>
                  </template>
                  <template #action>
                    <n-button size="small" quaternary circle @click.stop="handleRemoveRecent(directory)"
                      :loading="removingRecentPath === directory.path">
                      <template #icon>
                        <n-icon :component="CloseOutline" />
                      </template>
                    </n-button>
                  </template>
                  <template #header-extra>
                    <n-icon class="hover-arrow" :component="ArrowForwardOutline" />
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>

            <!-- 空状态 -->
            <div v-else class="mobile-empty-state">
              <div class="mobile-empty-icon">
                <n-icon :component="CubeOutline" size="64" color="#cbd5e1" />
              </div>

              <div class="mobile-empty-content">
                <h3 class="mobile-empty-title">{{ $t('home.recentProjects.emptyStateTitle') }}</h3>
                <p class="mobile-empty-description">{{ $t('home.recentProjects.emptyStateDescription') }}</p>

                <div class="mobile-empty-actions">
                  <n-button
                    type="primary"
                    size="large"
                    @click="switchToMainView"
                    :disabled="isSelecting || !serviceOnline"
                    :loading="isSelecting"
                  >
                    <template #icon>
                      <n-icon :component="FolderOpenOutline" />
                    </template>
                    {{ $t('home.actions.openProject') }}
                  </n-button>

                  <div v-if="!serviceOnline" class="service-warning">
                    <n-icon :component="AlertCircle" color="#f59e0b" />
                    <span>{{ $t('home.messages.serviceOffline') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部切换按钮 -->
        <div class="mobile-bottom-nav">
          <button
            class="mobile-nav-btn"
            :class="{ 'active': currentMobileView === 'main' }"
            @click="switchToMainView"
          >
            <n-icon size="24" :component="FolderOpenOutline" />
            <span>{{ $t('home.mobileNav.openProject') }}</span>
          </button>
          <button
            class="mobile-nav-btn"
            :class="{ 'active': currentMobileView === 'recent' }"
            @click="switchToRecentView"
          >
            <n-icon size="24" :component="CubeOutline" />
            <span>{{ $t('home.mobileNav.recentProjects') }}</span>
          </button>
        </div>
      </div>
    </template>

    <!-- 语言欢迎弹窗 -->
    <LanguageWelcomeModal
      v-model:show="showLanguageWelcome"
      @language-selected="handleLanguageSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  FolderOpenOutline,
  ArrowForwardOutline,
  ColorWand,
  CubeOutline,
  FileTrayFullOutline,
  LayersOutline,
  ImageOutline,
  CheckmarkCircle,
  AlertCircle,
  TrashOutline,
  CloseOutline,
  LanguageOutline
} from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';

import { DirectoryService } from '@/api/directory-service';
import { ConfigService } from '@/api'; // ConfigService 导入
import { ApiError } from '@/api/http-client';
import { setLanguage } from '@/locales';
import LanguageWelcomeModal from '@/components/LanguageWelcomeModal.vue';

// ----------- Types -----------
interface RecentDirectory {
  path: string;
  name: string;
  timestamp: number;
  formatted_time: string;
}

interface ServiceStatus {
  service: string;
  version: string;
  is_selecting: boolean;
  has_workspace: boolean;
  workspace_path: string | null;
}

// ----------- Props 和 Emits -----------
const emit = defineEmits<{
  'navigate-to-workspace': [params: {
    mode: 'file' | 'folder';
    projectPath: string;
    projectName: string;
  }];
}>();

// ----------- 国际化 -----------
const { t, locale } = useI18n();

// 语言选项
const languageOptions = [
  {
    label: '中文',
    key: 'zh'
  },
  {
    label: 'English',
    key: 'en'
  }
];

const currentLanguageLabel = computed(() => {
  const current = languageOptions.find(lang => lang.key === locale.value);
  return current?.label || '中文';
});

// ----------- 文件选择相关 -----------
const folderInput = ref<HTMLInputElement>();
const message = useMessage();

// ----------- 状态管理 -----------
const isSelecting = ref(false);
const serviceOnline = ref(false);
const hasWorkspace = ref(false);
const workspaceName = ref<string>('');
let statusCheckInterval: NodeJS.Timeout | null = null;

// ----------- 手机端相关 -----------
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value <= 768);
const currentMobileView = ref<'main' | 'recent'>('main');

// ----------- 手机端页面切换 -----------
const switchToMainView = () => {
  currentMobileView.value = 'main';
};

const switchToRecentView = () => {
  currentMobileView.value = 'recent';
};

// ----------- 窗口大小监听 -----------
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

// ----------- 最近目录数据 -----------
const recentDirectories = ref<RecentDirectory[]>([]);
const loadingRecent = ref(false);
const clearingRecent = ref(false);
const removingRecentPath = ref<string | null>(null);

// ----------- 语言切换保存状态 -----------
const savingLanguage = ref(false);

// ----------- 首次访问语言欢迎弹窗 -----------
const showLanguageWelcome = ref(false);

/**
 * 检查是否是首次访问
 */
const checkFirstVisit = async () => {
  try {
    console.log('🔍 [首次访问检测] 检查后端配置...');
    const config = await ConfigService.getConfig();

    const firstVisitCompleted = config.first_visit_completed;
    const hasLanguageSetting = config.language;

    console.log('🔍 [首次访问检测] 配置状态:', {
      firstVisitCompleted,
      hasLanguageSetting
    });

    // 如果首次访问未完成且没有语言设置，则显示欢迎弹窗
    if (!firstVisitCompleted) {
      console.log('🎉 [首次访问] 检测到首次访问，将显示语言选择弹窗');
      showLanguageWelcome.value = true;
    }
  } catch (error) {
    console.error('🔍 [首次访问检测] 检查配置失败:', error);
    // 配置检查失败时，不显示欢迎弹窗
  }
};

/**
 * 处理语言选择完成
 */
const handleLanguageSelected = async (selectedLanguage: string) => {
  console.log('🌐 [语言选择] 用户选择了语言:', selectedLanguage);

  try {
    // 通过后端API保存首次访问状态和语言设置
    const currentConfig = await ConfigService.getConfig();

    const updatedConfig = {
      ...currentConfig,
      language: selectedLanguage,
      first_visit_completed: true
    };

    await ConfigService.saveConfig(updatedConfig);

    console.log('✅ [语言选择] 配置已保存到后端');
    message.success(t('languageWelcome.success'));

  } catch (error) {
    console.error('❌ [语言选择] 保存配置失败:', error);
    message.error(t('languageWelcome.error'));
  }
};

// ----------- 语言配置加载和保存 -----------

/**
 * 加载语言配置并自动切换
 */
const loadLanguageConfig = async () => {
  try {
    console.log('🌐 [语言配置] 开始加载语言配置...');
    const config = await ConfigService.getConfig();

    if (config && config.language) {
      const savedLanguage = config.language;
      console.log('🌐 [语言配置] 读取到保存的语言:', savedLanguage);

      // 验证语言是否有效
      const validLanguages = languageOptions.map(lang => lang.key);
      if (validLanguages.includes(savedLanguage)) {
        // 只有当保存的语言与当前语言不同时才切换
        if (locale.value !== savedLanguage) {
          console.log('🌐 [语言配置] 自动切换语言:', `${locale.value} -> ${savedLanguage}`);
          setLanguage(savedLanguage);
        } else {
          console.log('🌐 [语言配置] 语言已是目标语言，无需切换:', savedLanguage);
        }
      } else {
        console.warn('🌐 [语言配置] 保存的语言无效:', savedLanguage, '使用默认语言');
      }
    } else {
      console.log('🌐 [语言配置] 未找到保存的语言配置，使用默认语言');
    }
  } catch (error) {
    console.warn('🌐 [语言配置] 加载语言配置失败，使用默认语言:', error);
    // 加载失败时静默处理，不影响主要功能
  }
};

/**
 * 保存语言配置
 */
const saveLanguageConfig = async (language: string) => {
  if (savingLanguage.value) {
    console.log('🌐 [语言配置] 正在保存中，跳过重复保存');
    return;
  }

  savingLanguage.value = true;
  try {
    console.log('🌐 [语言配置] 开始保存语言配置:', language);

    // 获取当前配置
    const currentConfig = await ConfigService.getConfig();

    // 更新语言配置
    const updatedConfig = {
      ...currentConfig,
      language: language
    };

    // 保存配置
    await ConfigService.saveConfig(updatedConfig);

    console.log('🌐 [语言配置] 语言配置保存成功:', language);

    // 显示保存成功提示
    message.success(t('settings.messages.languageSaved'));

  } catch (error) {
    console.error('🌐 [语言配置] 保存语言配置失败:', error);

    // 显示保存失败提示，但不阻止语言切换
    if (error instanceof ApiError) {
      message.warning(`${t('settings.messages.languageSaveFailed')}: ${error.message}`);
    } else {
      message.warning(t('settings.messages.languageSaveFailed'));
    }
  } finally {
    savingLanguage.value = false;
  }
};

/**
 * 处理语言切换
 */
const handleLanguageChange = async (key: string) => {
  const oldLanguage = locale.value;

  console.log('🌐 [语言切换] 用户切换语言:', `${oldLanguage} -> ${key}`);

  // 立即切换语言以获得即时反馈
  setLanguage(key);

  // 异步保存语言配置
  await saveLanguageConfig(key);
};

// ----------- 服务状态检查 -----------

/**
 * 检查服务状态
 */
const checkServiceStatus = async () => {
  try {
    const status: ServiceStatus = await DirectoryService.getServiceStatus();
    serviceOnline.value = true;
    isSelecting.value = status.is_selecting;
    hasWorkspace.value = status.has_workspace;

    if (status.workspace_path) {
      workspaceName.value = status.workspace_path.split(/[/\\]/).pop() || status.workspace_path;
    } else {
      workspaceName.value = '';
    }
  } catch (error) {
    serviceOnline.value = false;
    isSelecting.value = false;
    hasWorkspace.value = false;
    workspaceName.value = '';
    console.warn('服务状态检查失败:', error);
  }
};

/**
 * 启动定期状态检查
 */
const startStatusCheck = () => {
  // 立即检查一次
  checkServiceStatus();
  // 每5秒检查一次状态
  statusCheckInterval = setInterval(checkServiceStatus, 5000);
};

/**
 * 停止状态检查
 */
const stopStatusCheck = () => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval);
    statusCheckInterval = null;
  }
};

// ----------- 最近目录管理 -----------

/**
 * 加载最近目录列表
 */
const loadRecentDirectories = async () => {
  if (!serviceOnline.value) return;

  loadingRecent.value = true;
  try {
    const result = await DirectoryService.getRecentDirectories();
    recentDirectories.value = result.directories || [];
    console.log('✅ [获取最近目录] 成功加载', recentDirectories.value.length, '条记录');
  } catch (error) {
    console.error('❌ [获取最近目录] 失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('common.messages.operationFailed')}: ${error.message}`);
    } else {
      message.error(t('common.messages.operationFailed'));
    }
  } finally {
    loadingRecent.value = false;
  }
};

/**
 * 清空最近目录
 */
const handleClearRecent = async () => {
  if (!serviceOnline.value) {
    message.error(t('home.messages.serviceOffline'));
    return;
  }

  clearingRecent.value = true;
  try {
    await DirectoryService.clearRecentDirectories();
    recentDirectories.value = [];
    message.success(t('home.recentProjects.clearSuccess'));
    console.log('✅ [清空最近目录] 操作成功');
  } catch (error) {
    console.error('❌ [清空最近目录] 失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('common.messages.operationFailed')}: ${error.message}`);
    } else {
      message.error(t('common.messages.operationFailed'));
    }
  } finally {
    clearingRecent.value = false;
  }
};

/**
 * 移除指定最近目录
 */
const handleRemoveRecent = async (directory: RecentDirectory) => {
  if (!serviceOnline.value) {
    message.error(t('home.messages.serviceOffline'));
    return;
  }

  removingRecentPath.value = directory.path;
  try {
    await DirectoryService.removeRecentDirectory(directory.path);

    // 从本地列表中移除
    const index = recentDirectories.value.findIndex(d => d.path === directory.path);
    if (index > -1) {
      recentDirectories.value.splice(index, 1);
    }

    message.success(t('home.recentProjects.removeSuccess', { name: directory.name }));
    console.log('✅ [移除最近目录] 操作成功:', directory.path);
  } catch (error) {
    console.error('❌ [移除最近目录] 失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('common.messages.operationFailed')}: ${error.message}`);
    } else {
      message.error(t('common.messages.operationFailed'));
    }
  } finally {
    removingRecentPath.value = null;
  }
};

// ----------- API调用函数 -----------

/**
 * 调用后端目录选择API
 */
const selectDirectoryFromBackend = async (): Promise<string | null> => {
  try {
    console.log('🚀 [前端->后端] 请求选择目录');

    const result = await DirectoryService.selectDirectory();

    if (result && result.directory) {
      console.log('✅ [后端->前端] 目录选择成功:', result.directory);
      return result.directory;
    } else {
      console.log('ℹ️ [后端->前端] 未选择目录');
      return null;
    }
  } catch (error) {
    console.error('❌ [后端->前端] 目录选择失败:', error);
    throw error;
  }
};

// ----------- 事件处理函数 -----------

/**
 * 打开文件夹 - 使用系统目录选择对话框
 */
const handleOpenFolder = async () => {
  if (isSelecting.value) {
    message.warning(t('home.messages.selectingInProgress'));
    return;
  }

  if (!serviceOnline.value) {
    message.error(t('home.messages.serviceOffline'));
    return;
  }

  console.log('📁 [阿卡姆印牌姬] 用户点击：打开文件夹');

  const loadingMessage = message.loading(t('home.messages.openingFolder'), {
    duration: 0 // 持续显示直到手动关闭
  });

  try {
    const selectedPath = await selectDirectoryFromBackend();

    loadingMessage.destroy();

    if (selectedPath) {
      const folderName = selectedPath.split(/[/\\]/).pop() || selectedPath;
      message.success(t('home.messages.folderOpened', { name: folderName }));

      // 重新加载最近目录列表（因为选择目录会自动添加到最近记录）
      await loadRecentDirectories();

      // 导航到工作空间
      emit('navigate-to-workspace', {
        mode: 'folder',
        projectPath: selectedPath,
        projectName: folderName
      });
    } else {
      message.info(t('home.messages.folderNotSelected'));
    }
  } catch (error) {
    loadingMessage.destroy();

    if (error instanceof ApiError) {
      // 处理特定的API错误
      switch (error.code) {
        case 1001:
          message.warning(t('home.errors.selectInProgress'));
          break;
        case 1002:
          message.error(t('home.errors.timeout'));
          break;
        case 1003:
          message.info(t('home.errors.userCancelled'));
          break;
        case 1004:
          message.error(t('home.errors.selectError'));
          break;
        case 1006:
          message.error(t('home.errors.serverError'));
          break;
        default:
          message.error(`${t('common.messages.operationFailed')}: ${error.message}`);
      }
    } else {
      message.error(t('home.errors.unknownError'));
    }
  }
};

/**
 * 处理浏览器文件夹选择（备用方案）
 */
const handleFolderSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;

  if (files && files.length > 0) {
    const firstFile = files[0];
    const relativePath = firstFile.webkitRelativePath;
    const folderName = relativePath.split('/')[0];

    console.log('📁 [浏览器文件夹选择] 已选择文件夹:', folderName);
    console.log('📁 [文件夹选择] 文件夹内包含文件数量:', files.length);

    message.success(t('home.messages.folderOpened', { name: folderName }) + ` (${files.length} 个文件)`);

    emit('navigate-to-workspace', {
      mode: 'folder',
      projectPath: folderName,
      projectName: folderName
    });
  }

  target.value = '';
};

/**
 * 打开最近项目
 */
const handleOpenRecent = async (directory: RecentDirectory) => {
  if (!serviceOnline.value) {
    message.error(t('home.messages.serviceOffline'));
    return;
  }

  console.log('🔄 [阿卡姆印牌姬] 用户点击最近项目:', directory.name);
  console.log('🔄 [最近项目] 目录路径:', directory.path);

  const loadingMessage = message.loading(t('home.messages.openingRecent', { name: directory.name }), {
    duration: 0
  });

  try {
    // 调用后端API打开工作空间
    await DirectoryService.openWorkspace(directory.path);

    loadingMessage.destroy();
    message.success(t('home.messages.opened', { name: directory.name }));

    // 导航到工作空间
    emit('navigate-to-workspace', {
      mode: 'folder',
      projectPath: directory.path,
      projectName: directory.name
    });

  } catch (error) {
    loadingMessage.destroy();
    console.error('❌ [打开最近项目] 失败:', error);

    if (error instanceof ApiError) {
      switch (error.code) {
        case 3001:
          message.error(t('home.errors.workspaceNotExists'));
          break;
        case 3002:
          message.error(t('home.errors.accessDenied'));
          break;
        default:
          message.error(`${t('common.messages.operationFailed')}: ${error.message}`);
      }
    } else {
      message.error(`${t('common.messages.operationFailed')}: ${directory.name}`);
    }
  }
};

// ----------- 生命周期钩子 -----------

onMounted(async () => {
  console.log('🎯 [阿卡姆印牌姬] Welcome组件已挂载');

  // 添加窗口大小监听
  window.addEventListener('resize', handleResize, { passive: true });

  // 检查首次访问（异步）
  await checkFirstVisit();

  // 首先加载语言配置并自动切换
  await loadLanguageConfig();

  // 启动服务状态检查
  startStatusCheck();

  // 等待服务连接后加载最近目录
  const checkAndLoad = async () => {
    await checkServiceStatus();
    if (serviceOnline.value) {
      await loadRecentDirectories();
    }
  };

  await checkAndLoad();
});

onUnmounted(() => {
  console.log('🎯 [阿卡姆印牌姬] Welcome组件已卸载');
  stopStatusCheck();
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* 语言切换按钮加载状态样式 */
.language-btn[loading] {
  opacity: 0.7;
  cursor: not-allowed;
}

/* =========== 顶级容器 =========== */
.welcome-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #f8fafc;
}

/* =========== 左侧窗格 =========== */
.left-pane {
  width: 420px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.left-pane::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.left-content {
  position: relative;
  z-index: 1;
}

/* 语言切换器 */
.language-switcher-container {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.language-btn {
  color: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(10px);
}

.language-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
}

.logo-area {
  text-align: center;
  margin-bottom: 60px;
}

.logo-icon {
  margin-bottom: 20px;
}

.logo-text h1 {
  color: white;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo-text p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  margin: 0;
}

.primary-action {
  margin-bottom: 30px;
}

.open-folder-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 20px;
  text-align: left;
  position: relative;
  overflow: hidden;
}

.open-folder-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.open-folder-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.6s ease;
}

.open-folder-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.open-folder-btn:hover:not(:disabled)::before {
  left: 100%;
}

.btn-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-content {
  flex-grow: 1;
}

.btn-title {
  display: block;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
}

.btn-desc {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.btn-arrow {
  flex-shrink: 0;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.open-folder-btn:hover:not(:disabled) .btn-arrow {
  opacity: 1;
  transform: translateX(4px);
}

/* 服务状态 */
.service-status {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.status-item.online {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.status-item.offline {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.status-item.workspace-info {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.quick-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

/* =========== 右侧窗格 =========== */
.right-pane {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  padding: 40px 60px;
  background: #f8fafc;
}

.content-wrapper {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.content-header {
  flex-shrink: 0;
}

.header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.right-pane h2 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1e293b;
}

.right-pane .subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.recent-list-container {
  flex-grow: 1;
  overflow-y: auto;
  min-height: 0;
  padding-right: 10px;
  margin-right: -10px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 16px;
  color: #64748b;
}

/* 美化滚动条 */
.recent-list-container::-webkit-scrollbar {
  width: 6px;
}

.recent-list-container::-webkit-scrollbar-track {
  background: transparent;
}

.recent-list-container::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.recent-list-container::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

.n-list-item {
  padding: 16px !important;
  border-radius: 8px;
  background: white;
  border: 1px solid #e2e8f0;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.n-list-item:hover {
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.n-thing .n-thing-header {
  font-weight: 500;
  font-size: 16px;
  color: #1e293b;
}

.recent-item-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-item-path {
  font-size: 13px;
  color: #64748b;
  opacity: 0.8;
}

.recent-item-time {
  font-size: 12px;
  color: #9ca3af;
}

.hover-arrow {
  opacity: 0;
  transition: all 0.2s ease;
  color: #667eea;
}

.n-list-item:hover .hover-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.empty-state {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* =========== 增强的空状态样式 =========== */
.empty-state-enhanced {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 24px;
  opacity: 0.6;
}

.empty-content {
  max-width: 500px;
  width: 100%;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.empty-description {
  font-size: 16px;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.empty-guide {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  text-align: left;
}

.guide-title {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  margin: 0 0 16px 0;
}

.guide-options {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.guide-options li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.guide-options li:hover {
  border-color: #667eea;
  background: #f8fafc;
  transform: translateX(4px);
}

.guide-options li span {
  font-size: 14px;
  color: #475569;
  line-height: 1.4;
}

.empty-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.service-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 8px;
  font-size: 14px;
  color: #92400e;
}

/* 响应式样式调整 */
@media (max-width: 768px) {
  .empty-state-enhanced {
    padding: 30px 15px;
  }

  .empty-title {
    font-size: 20px;
  }

  .empty-description {
    font-size: 14px;
  }

  .empty-guide {
    padding: 20px;
  }

  .guide-options li {
    padding: 10px 12px;
  }

  .guide-options li span {
    font-size: 13px;
  }
}

/* =========== 响应式设计 =========== */
@media (max-width: 1024px) {
  .left-pane {
    width: 380px;
    padding: 30px 25px;
  }

  .right-pane {
    padding: 30px 40px;
  }
}

/* ============================================= */
/* 手机端样式 */
/* ============================================= */
@media (max-width: 768px) {
  .welcome-container {
    display: block;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
  }

  /* 手机端容器 */
  .mobile-container {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  /* 手机端主页面 */
  .mobile-main-view {
    flex: 1;
    padding: 20px 16px calc(80px + 20px) 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 0;
  }

  .mobile-language-switcher {
    position: absolute;
    top: 20px;
    right: 16px;
    z-index: 10;
  }

  .mobile-language-btn {
    color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px);
  }

  .mobile-logo-area {
    text-align: center;
    margin-bottom: 40px;
  }

  .mobile-logo-icon {
    margin-bottom: 20px;
  }

  .mobile-logo-text h1 {
    color: white;
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 8px 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .mobile-logo-text p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 16px;
    margin: 0;
  }

  .mobile-primary-action {
    margin-bottom: 30px;
  }

  .mobile-open-folder-btn {
    width: 100%;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 24px;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 20px;
    text-align: left;
    position: relative;
    overflow: hidden;
  }

  .mobile-open-folder-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .mobile-open-folder-btn:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }

  .mobile-btn-icon {
    flex-shrink: 0;
    width: 64px;
    height: 64px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-btn-content {
    flex-grow: 1;
  }

  .mobile-btn-title {
    display: block;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 6px;
  }

  .mobile-btn-desc {
    display: block;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.4;
  }

  .mobile-btn-arrow {
    flex-shrink: 0;
    opacity: 0.6;
    transition: all 0.3s ease;
  }

  .mobile-open-folder-btn:hover:not(:disabled) .mobile-btn-arrow {
    opacity: 1;
    transform: translateX(4px);
  }

  .mobile-service-status {
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .mobile-status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    padding: 10px 14px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    color: white;
  }

  .mobile-status-item.online {
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
  }

  .mobile-status-item.offline {
    color: #f59e0b;
    background: rgba(245, 158, 11, 0.1);
  }

  .mobile-status-item.workspace-info {
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
  }

  .mobile-quick-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .mobile-info-item {
    display: flex;
    align-items: center;
    gap: 12px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    background: rgba(255, 255, 255, 0.1);
    padding: 12px 16px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
  }

  /* 手机端历史记录页面 */
  .mobile-recent-view {
    flex: 1;
    background: #f8fafc;
    padding: 20px 16px calc(80px + 20px) 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .mobile-content-header {
    flex-shrink: 0;
    margin-bottom: 20px;
  }

  .mobile-header h2 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #1e293b;
  }

  .mobile-subtitle {
    font-size: 16px;
    color: #64748b;
    margin: 0;
  }

  .mobile-header-actions {
    margin-top: 16px;
  }

  .mobile-recent-list-container {
    flex-grow: 1;
    overflow-y: auto;
    min-height: 0;
  }

  .mobile-empty-state {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
    text-align: center;
  }

  .mobile-empty-icon {
    margin-bottom: 24px;
    opacity: 0.6;
  }

  .mobile-empty-content {
    max-width: 400px;
    width: 100%;
  }

  .mobile-empty-title {
    font-size: 24px;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 16px 0;
  }

  .mobile-empty-description {
    font-size: 16px;
    color: #64748b;
    line-height: 1.6;
    margin: 0 0 32px 0;
  }

  .mobile-empty-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  /* 底部导航 */
  .mobile-bottom-nav {
    height: 80px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 0 20px;
    flex-shrink: 0;
  }

  .mobile-nav-btn {
    background: none;
    border: none;
    color: #64748b;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    border-radius: 12px;
    min-width: 100px;
  }

  .mobile-nav-btn:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }

  .mobile-nav-btn.active {
    background: rgba(102, 126, 234, 0.15);
    color: #667eea;
  }

  .mobile-nav-btn span {
    font-size: 12px;
    font-weight: 500;
  }
}
</style>

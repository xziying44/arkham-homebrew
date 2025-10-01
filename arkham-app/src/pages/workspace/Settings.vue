<template>
  <div class="settings-container">
    <div class="settings-content">
      <h2>{{ $t('settings.title') }}</h2>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>{{ $t('settings.loading') }}</p>
      </div>

      <div v-else class="settings-sections">
        <!-- GitHub图床设置 -->
        <div class="settings-section">
          <h3>{{ $t('settings.sections.github.title') }}</h3>

          <!-- GitHub Token -->
          <div class="setting-item">
            <label>{{ $t('settings.sections.github.token') }}</label>
            <div class="token-input-container">
              <input v-model="githubConfig.github_token" type="password"
                :placeholder="$t('settings.sections.github.tokenPlaceholder')" :disabled="githubVerifying" />
              <button @click="verifyGitHubToken" :disabled="!githubConfig.github_token || githubVerifying"
                class="verify-btn" :class="{ 'success': githubLoginSuccess, 'error': githubLoginError }">
                {{ githubVerifying ? $t('settings.sections.github.verifying') : githubLoginSuccess ?
                  $t('settings.sections.github.verified') : $t('settings.sections.github.verifyLogin') }}
              </button>
            </div>
            <span class="setting-description">
              {{ $t('settings.sections.github.tokenDesc') }}
              <a href="https://github.com/settings/tokens" target="_blank" class="link">{{
                $t('settings.sections.github.getToken') }}</a>
            </span>
            <div v-if="githubLoginError" class="error-hint">
              {{ githubLoginError }}
            </div>
            <div v-if="githubLoginSuccess" class="success-hint">
              {{ $t('settings.sections.github.loginSuccess', { username: githubUsername }) }}
            </div>
          </div>

          <!-- GitHub 仓库配置（登录成功后显示） -->
          <template v-if="githubLoginSuccess">
            <div class="setting-item">
              <label>{{ $t('settings.sections.github.repo') }}</label>
              <div class="repo-selector">
                <select v-model="githubConfig.github_repo" :disabled="loadingRepositories">
                  <option value="">{{ $t('settings.sections.github.selectRepo') }}</option>
                  <option v-for="repo in githubRepositories" :key="repo.full_name" :value="repo.full_name">
                    {{ repo.full_name }} {{ repo.private ? `(${$t('settings.sections.github.private')})` :
                      `(${$t('settings.sections.github.public')})` }}
                  </option>
                </select>
                <button @click="loadGitHubRepositories" :disabled="loadingRepositories" class="refresh-btn">
                  {{ loadingRepositories ? $t('common.buttons.loading') : $t('common.buttons.refresh') }}
                </button>
              </div>
              <span class="setting-description">{{ $t('settings.sections.github.repoDesc') }}</span>
            </div>

            <div class="setting-item">
              <label>{{ $t('settings.sections.github.branch') }}</label>
              <input v-model="githubConfig.github_branch" type="text" placeholder="main" />
              <span class="setting-description">{{ $t('settings.sections.github.branchDesc') }}</span>
            </div>

            <div class="setting-item">
              <label>{{ $t('settings.sections.github.folder') }}</label>
              <input v-model="githubConfig.github_folder" type="text" placeholder="images" />
              <span class="setting-description">{{ $t('settings.sections.github.folderDesc') }}</span>
            </div>
          </template>
        </div>

        <!-- 工作区配置 -->
        <div class="settings-section">
          <h3>{{ $t('settings.sections.workspace.title') }}</h3>

          <div class="setting-item">
            <label>{{ $t('settings.sections.workspace.encounterGroups') }}</label>
            <div class="directory-selector">
              <select v-model="selectedEncounterGroupsDir" :disabled="!directories.length" @change="onDirectoryChange">
                <option value="">{{ $t('settings.sections.workspace.selectDirectory') }}</option>
                <option v-for="dir in directories" :key="dir.key" :value="dir.relativePath">
                  {{ dir.label }}
                </option>
              </select>
              <button @click="refreshDirectories" :disabled="refreshingDirs" class="refresh-btn">
                {{ refreshingDirs ? $t('common.buttons.loading') : $t('common.buttons.refresh') }}
              </button>
            </div>
            <span v-if="selectedEncounterGroupsDir" class="setting-description">
              {{ $t('settings.sections.workspace.relativePath', { path: selectedEncounterGroupsDir }) }}
            </span>
          </div>

          <div class="setting-item">
            <label>{{ $t('settings.sections.workspace.footerIcon') }}</label>
            <div class="directory-selector">
              <select v-model="selectedFooterIcon" :disabled="!rootImages.length" @change="onImageChange">
                <option value="">{{ $t('settings.sections.workspace.selectImage') }}</option>
                <option v-for="img in rootImages" :key="img.key" :value="img.relativePath">
                  {{ img.label }}
                </option>
              </select>
              <button @click="refreshDirectories" :disabled="refreshingDirs" class="refresh-btn">
                {{ refreshingDirs ? $t('common.buttons.loading') : $t('common.buttons.refresh') }}
              </button>
            </div>
            <span class="setting-description">{{ $t('settings.sections.workspace.footerIconDesc') }}</span>
            <span v-if="selectedFooterIcon" class="setting-description">
              {{ $t('settings.sections.workspace.relativePath', { path: selectedFooterIcon }) }}
            </span>
          </div>

          <div class="setting-item">
            <label>{{ $t('settings.sections.workspace.copyright') }}</label>
            <input v-model="config.footer_copyright" type="text" placeholder="© 2025 DIY" />
          </div>
        </div>

        <!-- 语言设置 -->
        <div class="settings-section">
          <h3>{{ $t('settings.sections.language.title') }}</h3>
          <div class="setting-item">
            <label>{{ $t('settings.sections.language.interface') }}</label>
            <select v-model="config.language" @change="handleLanguageChange">
              <option value="zh">{{ $t('settings.sections.language.chinese') }}</option>
              <option value="en">{{ $t('settings.sections.language.english') }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div v-if="!loading" class="settings-actions">
        <button class="btn-primary" @click="saveSettings" :disabled="saving">
          {{ saving ? $t('common.buttons.saving') : $t('settings.actions.save') }}
        </button>
        <button class="btn-secondary" @click="resetSettings" :disabled="saving">
          {{ $t('settings.actions.reset') }}
        </button>
      </div>

      <!-- 底部占位空间 -->
      <div class="bottom-spacer"></div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="error = ''" class="close-error">×</button>
      </div>

      <!-- 成功提示 -->
      <div v-if="successMessage" class="success-message">
        <p>{{ successMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'; // 添加 onUnmounted
import { useI18n } from 'vue-i18n';
import { ConfigService, WorkspaceService } from '@/api';
import { GitHubService } from '@/api/github-service';
import type { ConfigData, TreeOption, GitHubRepository } from '@/api/types';
import { setLanguage } from '@/locales';

// 扩展TreeOption类型以包含相对路径
interface ExtendedTreeOption extends TreeOption {
  relativePath?: string;
}

// 国际化
const { t } = useI18n();

// 响应式数据
const loading = ref(true);
const saving = ref(false);
const refreshingDirs = ref(false);
const error = ref('');
const successMessage = ref('');

// GitHub相关状态
const githubVerifying = ref(false);
const githubLoginSuccess = ref(false);
const githubLoginError = ref('');
const githubUsername = ref('');
const loadingRepositories = ref(false);
const githubRepositories = ref<GitHubRepository[]>([]);

// 配置数据
const config = reactive<ConfigData>({
  encounter_groups_dir: '',
  footer_icon_dir: '',
  footer_copyright: '',
  language: 'zh'
});

// GitHub配置
const githubConfig = reactive({
  github_token: '',
  github_repo: '',
  github_branch: 'main',
  github_folder: 'images'
});

// 目录和图片列表
const directories = ref<ExtendedTreeOption[]>([]);
const rootImages = ref<ExtendedTreeOption[]>([]);
const workspaceRootPath = ref('');

// 选中的相对路径
const selectedEncounterGroupsDir = ref('');
const selectedFooterIcon = ref('');

/**
 * 语言变化处理
 */
const handleLanguageChange = () => {
  setLanguage(config.language);
};

/**
 * 键盘快捷键处理
 */
const handleKeydown = async (event: KeyboardEvent) => {
  // Ctrl+S 保存
  if ((event.ctrlKey || event.metaKey) && event.code === 'KeyS') {
    event.preventDefault();
    event.stopPropagation();

    // 防止重复保存
    if (saving.value) {
      return;
    }

    await saveSettings();
  }
};
/**
 * 初始化设置页面
 */
onMounted(async () => {
  await loadSettings();
  await loadDirectories();
  await checkGitHubStatus();
  loading.value = false;

  // 添加键盘事件监听器
  document.addEventListener('keydown', handleKeydown);
});
// 组件卸载时移除键盘事件监听器
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});

/**
 * 加载配置设置
 */
const loadSettings = async () => {
  try {
    const configData = await ConfigService.getConfig();

    // 合并配置数据
    Object.assign(config, {
      encounter_groups_dir: configData.encounter_groups_dir || '',
      footer_icon_dir: configData.footer_icon_dir || '',
      footer_copyright: configData.footer_copyright || '© 2025 DIY',
      language: configData.language || 'zh'
    });

    // 加载GitHub配置
    Object.assign(githubConfig, {
      github_token: configData.github_token || '',
      github_repo: configData.github_repo || '',
      github_branch: configData.github_branch || 'main',
      github_folder: configData.github_folder || 'images'
    });

    // 设置选中的相对路径值
    selectedEncounterGroupsDir.value = config.encounter_groups_dir;
    selectedFooterIcon.value = config.footer_icon_dir;
  } catch (err: any) {
    console.warn('加载配置失败，使用默认配置:', err);
    resetToDefaults();
  }
};

/**
 * 检查GitHub状态
 */
const checkGitHubStatus = async () => {
  try {
    const status = await GitHubService.getStatus();

    if (status.data.status.is_logged_in) {
      githubLoginSuccess.value = true;
      githubUsername.value = status.data.status.username || '';
      // 自动加载仓库列表
      await loadGitHubRepositories();
    }
  } catch (err: any) {
    console.warn('获取GitHub状态失败:', err);
  }
};

/**
 * 验证GitHub Token
 */
const verifyGitHubToken = async () => {
  if (!githubConfig.github_token.trim()) {
    githubLoginError.value = t('settings.messages.tokenRequired');
    return;
  }

  githubVerifying.value = true;
  githubLoginError.value = '';
  githubLoginSuccess.value = false;

  try {
    // 1. 先调用登录接口验证token
    await GitHubService.login(githubConfig.github_token.trim());

    // 2. 登录成功后获取GitHub状态来获取用户名
    const status = await GitHubService.getStatus();

    githubLoginSuccess.value = true;
    githubUsername.value = status.data.status.username || '';
    githubLoginError.value = '';

    // 3. 登录成功后自动加载仓库列表
    await loadGitHubRepositories();

  } catch (err: any) {
    githubLoginError.value = err.message || t('settings.messages.githubLoginFailed');
    githubLoginSuccess.value = false;
    githubUsername.value = '';
    githubRepositories.value = [];
  } finally {
    githubVerifying.value = false;
  }
};

/**
 * 加载GitHub仓库列表
 */
const loadGitHubRepositories = async () => {
  if (!githubLoginSuccess.value) {
    console.warn('未登录，跳过加载仓库列表');
    return;
  }

  loadingRepositories.value = true;
  try {
    const repositories = (await GitHubService.getRepositories()).data.repositories;
    githubRepositories.value = repositories;
    console.log('获取到的仓库列表:', githubRepositories.value);
  } catch (err: any) {
    console.error('加载仓库列表失败:', err);
    error.value = t('settings.messages.loadRepoFailed', { error: err.message || t('common.messages.networkError') });
    githubRepositories.value = [];
  } finally {
    loadingRepositories.value = false;
  }
};

/**
 * 加载目录列表和根目录图片
 */
const loadDirectories = async () => {
  try {
    const fileTree = await WorkspaceService.getFileTree();

    // 保存工作空间根路径
    workspaceRootPath.value = fileTree.fileTree.path;

    // 提取所有目录（包含相对路径）
    directories.value = extractDirectories(fileTree.fileTree, workspaceRootPath.value);

    // 提取根目录下的PNG图片（包含相对路径）
    rootImages.value = extractRootImages(fileTree.fileTree, workspaceRootPath.value);
  } catch (err: any) {
    console.warn('加载目录列表失败:', err);
    error.value = t('settings.messages.loadError');
  }
};

/**
 * 计算相对路径
 */
const getRelativePath = (absolutePath: string, rootPath: string): string => {
  if (!absolutePath || !rootPath) return '';

  // 确保路径使用统一的分隔符
  const normalizedAbsolute = absolutePath.replace(/\\/g, '/');
  const normalizedRoot = rootPath.replace(/\\/g, '/');

  if (normalizedAbsolute.startsWith(normalizedRoot)) {
    const relative = normalizedAbsolute.slice(normalizedRoot.length);
    // 移除开头的斜杠
    return relative.startsWith('/') ? relative.slice(1) : relative;
  }

  return absolutePath; // 如果不能计算相对路径，返回原始路径
};

/**
 * 从文件树中提取目录
 */
const extractDirectories = (node: TreeOption, rootPath: string): ExtendedTreeOption[] => {
  const dirs: ExtendedTreeOption[] = [];

  if (node.type === 'directory' && node.path) {
    const relativePath = getRelativePath(node.path, rootPath);
    dirs.push({
      label: node.label,
      key: node.key,
      type: node.type,
      path: node.path,
      relativePath: relativePath
    });
  }

  if (node.children) {
    for (const child of node.children) {
      dirs.push(...extractDirectories(child, rootPath));
    }
  }

  return dirs;
};

/**
 * 从文件树根目录中提取PNG图片文件
 */
const extractRootImages = (rootNode: TreeOption, rootPath: string): ExtendedTreeOption[] => {
  const images: ExtendedTreeOption[] = [];

  if (rootNode.children) {
    for (const child of rootNode.children) {
      // 只查找根目录下的直接子文件，且类型为image
      if (child.type === 'image' && child.path && child.label.toLowerCase().endsWith('.png')) {
        const relativePath = getRelativePath(child.path, rootPath);
        images.push({
          label: child.label,
          key: child.key,
          type: child.type,
          path: child.path,
          relativePath: relativePath
        });
      }
    }
  }

  // 按名称排序
  return images.sort((a, b) => a.label.localeCompare(b.label));
};

/**
 * 刷新目录列表
 */
const refreshDirectories = async () => {
  refreshingDirs.value = true;
  try {
    await loadDirectories();
  } finally {
    refreshingDirs.value = false;
  }
};

/**
 * 目录选择变化处理
 */
const onDirectoryChange = () => {
  config.encounter_groups_dir = selectedEncounterGroupsDir.value;
};

/**
 * 图片选择变化处理
 */
const onImageChange = () => {
  config.footer_icon_dir = selectedFooterIcon.value;
};

/**
 * 保存设置
 */
const saveSettings = async () => {
  saving.value = true;
  error.value = '';
  successMessage.value = '';

  try {
    // 合并所有配置
    const configToSave = {
      ...config,
      encounter_groups_dir: selectedEncounterGroupsDir.value,
      footer_icon_dir: selectedFooterIcon.value,
      // GitHub配置
      ...githubConfig
    };

    // 保存配置
    await ConfigService.saveConfig(configToSave);

    // 更新本地配置
    config.encounter_groups_dir = selectedEncounterGroupsDir.value;
    config.footer_icon_dir = selectedFooterIcon.value;

    successMessage.value = t('settings.messages.saveSuccess');
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);

  } catch (err: any) {
    error.value = err.message || t('common.messages.operationFailed');
  } finally {
    saving.value = false;
  }
};

/**
 * 重置设置
 */
const resetSettings = () => {
  if (confirm(t('settings.actions.resetConfirm'))) {
    resetToDefaults();
  }
};

/**
 * 重置为默认值
 */
const resetToDefaults = () => {
  Object.assign(config, {
    encounter_groups_dir: '',
    footer_icon_dir: '',
    footer_copyright: '© 2025 DIY',
    language: 'zh'
  });

  // 重置GitHub配置
  Object.assign(githubConfig, {
    github_token: '',
    github_repo: '',
    github_branch: 'main',
    github_folder: 'images'
  });

  // 重置GitHub状态
  githubLoginSuccess.value = false;
  githubLoginError.value = '';
  githubUsername.value = '';
  githubRepositories.value = [];

  // 重置选中的相对路径
  selectedEncounterGroupsDir.value = '';
  selectedFooterIcon.value = '';
};

// 监听成功消息，自动清除
watch(() => successMessage.value, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  }
});

// 监听GitHub Token变化，重置登录状态
watch(() => githubConfig.github_token, () => {
  if (githubLoginSuccess.value) {
    githubLoginSuccess.value = false;
    githubLoginError.value = '';
    githubUsername.value = '';
    githubRepositories.value = [];
  }
});
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  height: 100%;
  overflow-y: auto;
  background: #f8f9fa;
}

.settings-content {
  max-width: 800px;
  margin: 0 auto;
}

.settings-content h2 {
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #6c757d;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e9ecef;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.settings-sections {
  display: grid;
  gap: 2rem;
}

.settings-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.settings-section h3 {
  color: #34495e;
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.5rem 0;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.setting-item input[type="text"],
.setting-item input[type="password"],
.setting-item select {
  padding: 0.5rem;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  font-size: 0.9rem;
}

.setting-item input[type="text"]:focus,
.setting-item input[type="password"]:focus,
.setting-item select:focus {
  border-color: #3498db;
  outline: none;
}

.setting-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  align-self: flex-start;
}

.setting-description {
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  font-style: italic;
}

.link {
  color: #3498db;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

/* GitHub相关样式 */
.token-input-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.token-input-container input {
  flex: 1;
}

.verify-btn {
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
  transition: background-color 0.2s;
}

.verify-btn:hover:not(:disabled) {
  background: #2980b9;
}

.verify-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.verify-btn.success {
  background: #27ae60;
}

.verify-btn.success:hover {
  background: #229954;
}

.verify-btn.error {
  background: #e74c3c;
}

.error-hint {
  color: #e74c3c;
  font-size: 0.8rem;
  font-weight: 500;
}

.success-hint {
  color: #27ae60;
  font-size: 0.8rem;
  font-weight: 500;
}

.repo-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.repo-selector select {
  flex: 1;
}

.directory-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.directory-selector select {
  flex: 1;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a6268;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.settings-actions {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1rem 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.btn-primary,
.btn-secondary {
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #219a52;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 底部占位空间 */
.bottom-spacer {
  height: 6rem;
}

.error-message,
.success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  max-width: 400px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.error-message {
  background: #e74c3c;
}

.success-message {
  background: #27ae60;
}

.close-error {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-error:hover {
  opacity: 0.7;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 1rem;
  }

  .setting-item {
    gap: 0.25rem;
  }

  .token-input-container,
  .repo-selector,
  .directory-selector {
    flex-direction: column;
    gap: 0.5rem;
  }

  .settings-actions {
    flex-direction: column;
  }

  .bottom-spacer {
    height: 8rem;
  }
}
</style>

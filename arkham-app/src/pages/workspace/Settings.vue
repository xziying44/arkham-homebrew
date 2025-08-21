<template>
  <div class="settings-container">
    <div class="settings-content">
      <h2>工作区设置</h2>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载配置...</p>
      </div>

      <div v-else class="settings-sections">
        <!-- AI设置 -->
        <div class="settings-section">
          <h3>🤖 AI设置</h3>
          <div class="setting-item">
            <label>AI端点</label>
            <input 
              v-model="config.ai_endpoint" 
              type="text" 
              placeholder="https://api.deepseek.com/v1"
            />
          </div>
          <div class="setting-item">
            <label>AI模型</label>
            <input 
              v-model="config.ai_model" 
              type="text" 
              placeholder="deepseek-chat"
            />
          </div>
          <div class="setting-item">
            <label>API密钥</label>
            <input 
              v-model="config.ai_api_key" 
              type="password" 
              placeholder="输入你的API密钥"
            />
          </div>
          <div class="setting-item">
            <label>在编辑区启用AI</label>
            <input 
              v-model="config.ai_enabled_in_editor" 
              type="checkbox"
            />
            <span class="setting-description">在编辑器中启用AI辅助功能</span>
          </div>
        </div>

        <!-- 工作区配置 -->
        <div class="settings-section">
          <h3>🏗️ 工作区配置</h3>
          
          <div class="setting-item">
            <label>遭遇组图标目录</label>
            <div class="directory-selector">
              <select 
                v-model="selectedEncounterGroupsDir"
                :disabled="!directories.length"
                @change="onDirectoryChange"
              >
                <option value="">请选择目录</option>
                <option 
                  v-for="dir in directories" 
                  :key="dir.key" 
                  :value="dir.relativePath"
                >
                  {{ dir.label }}
                </option>
              </select>
              <button 
                @click="refreshDirectories" 
                :disabled="refreshingDirs"
                class="refresh-btn"
              >
                {{ refreshingDirs ? '刷新中...' : '刷新' }}
              </button>
            </div>
            <span v-if="selectedEncounterGroupsDir" class="setting-description">
              相对路径: {{ selectedEncounterGroupsDir }}
            </span>
          </div>

          <div class="setting-item">
            <label>底标图标</label>
            <div class="directory-selector">
              <select 
                v-model="selectedFooterIcon"
                :disabled="!rootImages.length"
                @change="onImageChange"
              >
                <option value="">请选择图片</option>
                <option 
                  v-for="img in rootImages" 
                  :key="img.key" 
                  :value="img.relativePath"
                >
                  {{ img.label }}
                </option>
              </select>
              <button 
                @click="refreshDirectories" 
                :disabled="refreshingDirs"
                class="refresh-btn"
              >
                {{ refreshingDirs ? '刷新中...' : '刷新' }}
              </button>
            </div>
            <span class="setting-description">选择根目录下的PNG图片作为底标图标</span>
            <span v-if="selectedFooterIcon" class="setting-description">
              相对路径: {{ selectedFooterIcon }}
            </span>
          </div>

          <div class="setting-item">
            <label>底标版权信息</label>
            <input 
              v-model="config.footer_copyright" 
              type="text" 
              placeholder="© 2025 DIY"
            />
          </div>
        </div>

        <!-- 语言设置 -->
        <div class="settings-section">
          <h3>🌐 语言设置</h3>
          <div class="setting-item">
            <label>界面语言</label>
            <select v-model="config.language">
              <option value="zh">中文</option>
              <option value="en" disabled>English (待开发)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div v-if="!loading" class="settings-actions">
        <button 
          class="btn-primary" 
          @click="saveSettings"
          :disabled="saving"
        >
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
        <button 
          class="btn-secondary" 
          @click="resetSettings"
          :disabled="saving"
        >
          重置为默认
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
import { ref, reactive, onMounted, watch } from 'vue';
import { ConfigService, WorkspaceService } from '@/api';
import type { ConfigData, TreeOption } from '@/api/types';

// 扩展TreeOption类型以包含相对路径
interface ExtendedTreeOption extends TreeOption {
  relativePath?: string;
}

// 响应式数据
const loading = ref(true);
const saving = ref(false);
const refreshingDirs = ref(false);
const error = ref('');
const successMessage = ref('');

// 配置数据
const config = reactive<ConfigData>({
  ai_endpoint: '',
  ai_model: '',
  ai_api_key: '',
  ai_enabled_in_editor: false,
  encounter_groups_dir: '',
  footer_icon_dir: '',
  footer_copyright: '',
  language: 'zh'
});

// 目录和图片列表
const directories = ref<ExtendedTreeOption[]>([]);
const rootImages = ref<ExtendedTreeOption[]>([]);
const workspaceRootPath = ref('');

// 选中的相对路径
const selectedEncounterGroupsDir = ref('');
const selectedFooterIcon = ref('');

/**
 * 初始化设置页面
 */
onMounted(async () => {
  await loadSettings();
  await loadDirectories();
  loading.value = false;
});

/**
 * 加载配置设置
 */
const loadSettings = async () => {
  try {
    const configData = await ConfigService.getConfig();
    
    // 合并配置数据
    Object.assign(config, {
      ai_endpoint: configData.ai_endpoint || '',
      ai_model: configData.ai_model || 'deepseek-chat',
      ai_api_key: configData.ai_api_key || '',
      ai_enabled_in_editor: configData.ai_enabled_in_editor || false,
      encounter_groups_dir: configData.encounter_groups_dir || '',
      footer_icon_dir: configData.footer_icon_dir || '',
      footer_copyright: configData.footer_copyright || '© 2025 DIY',
      language: configData.language || 'zh'
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
    error.value = '无法加载工作区目录，请确保已打开工作空间';
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
    // 验证必填项
    if (config.ai_enabled_in_editor) {
      if (!config.ai_endpoint || !config.ai_api_key) {
        throw new Error('启用AI功能时，端点和API密钥为必填项');
      }
    }
    
    // 确保配置中存储的是相对路径
    const configToSave = {
      ...config,
      encounter_groups_dir: selectedEncounterGroupsDir.value,
      footer_icon_dir: selectedFooterIcon.value
    };
    
    // 保存配置
    await ConfigService.saveConfig(configToSave);
    
    // 更新本地配置
    config.encounter_groups_dir = selectedEncounterGroupsDir.value;
    config.footer_icon_dir = selectedFooterIcon.value;
    
    successMessage.value = '设置保存成功！（使用相对路径）';
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
    
  } catch (err: any) {
    error.value = err.message || '保存设置失败';
  } finally {
    saving.value = false;
  }
};

/**
 * 重置为默认设置
 */
const resetSettings = () => {
  if (confirm('确定要重置所有设置为默认值吗？此操作不可撤销。')) {
    resetToDefaults();
  }
};

/**
 * 重置为默认值
 */
const resetToDefaults = () => {
  Object.assign(config, {
    ai_endpoint: 'https://api.deepseek.com/v1',
    ai_model: 'deepseek-chat',
    ai_api_key: '',
    ai_enabled_in_editor: false,
    encounter_groups_dir: '',
    footer_icon_dir: '',
    footer_copyright: '© 2025 DIY',
    language: 'zh'
  });
  
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.btn-primary, .btn-secondary {
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

.error-message, .success-message {
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

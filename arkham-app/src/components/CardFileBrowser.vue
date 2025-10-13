<template>
  <div class="card-file-browser">
    <div class="browser-header">
      <div class="breadcrumb">
        <n-button text @click="navigateToParent" v-if="currentPath !== ''" title="返回">
          <template #icon>
            <n-icon :component="ArrowBackOutline" />
          </template>
        </n-button>
        <span class="path-text">{{ getCurrentPathDisplay() }}</span>
      </div>
      <div class="browser-actions">
        <n-button size="small" @click="clearSelection">
          清除选择
        </n-button>
        <n-button type="primary" size="small" @click="confirmSelection" :disabled="selectedItems.length === 0">
          确认 ({{ selectedItems.length }})
        </n-button>
      </div>
    </div>

    <div class="browser-content">
      <n-scrollbar class="content-scroll">
        <div v-if="loading" class="loading-container">
          <n-spin size="large" />
        </div>
        <div v-else-if="currentItems.length === 0" class="empty-container">
          <n-empty description="当前目录没有卡牌文件">
            <template #icon>
              <n-icon :component="FolderOpenOutline" />
            </template>
            <template #extra>
              <n-text depth="3">当前路径: {{ currentPath }}</n-text>
              <br>
              <n-text depth="3">文件夹数量: {{ folders.length }}</n-text>
              <br>
              <n-text depth="3">卡牌文件数量: {{ cardFiles.length }}</n-text>
            </template>
          </n-empty>
        </div>
        <div v-else class="file-grid">
          <!-- 返回上层文件夹项目 -->
          <div v-if="currentPath !== ''" class="file-item back-folder" @dblclick="navigateToParent">
            <div class="item-icon">
              <n-icon :component="ArrowUpOutline" size="32" />
            </div>
            <div class="item-name">返回上一层</div>
          </div>

          <!-- 文件夹项目 -->
          <div
            v-for="folder in folders"
            :key="folder.path"
            class="file-item folder"
            :class="{ 'selected': isSelected(folder) }"
            @dblclick="enterFolder(folder)"
            @click="toggleSelection(folder)"
          >
            <div class="item-icon">
              <n-icon :component="FolderOutline" size="32" />
            </div>
            <div class="item-name">{{ folder.name }}</div>
            <div class="selection-indicator" v-if="isSelected(folder)">
              <n-icon :component="CheckmarkCircle" />
            </div>
          </div>

          <!-- 卡牌文件项目 -->
          <div
            v-for="file in cardFiles"
            :key="file.path"
            class="file-item card-file"
            :class="{ 'selected': isSelected(file) }"
            @click="toggleSelection(file)"
          >
            <div class="item-icon">
              <n-icon :component="DocumentTextOutline" size="32" />
            </div>
            <div class="item-name">{{ file.name }}</div>
            <div class="selection-indicator" v-if="isSelected(file)">
              <n-icon :component="CheckmarkCircle" />
            </div>
          </div>
        </div>
      </n-scrollbar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
  ArrowBackOutline,
  ArrowUpOutline,
  FolderOutline,
  DocumentTextOutline,
  CheckmarkCircle,
  FolderOpenOutline
} from '@vicons/ionicons5';
import { WorkspaceService } from '@/api';

interface FileNode {
  label: string;
  path: string;
  type: 'directory' | 'file' | 'card' | 'image' | 'config' | 'workspace';
  children?: FileNode[];
}

interface BrowserItem {
  name: string;
  path: string;
  type: 'directory' | 'card';
  fullPath: string;
}

interface Props {
  visible: boolean;
}

interface Emits {
  (e: 'update:visible', value: boolean): void;
  (e: 'confirm', items: BrowserItem[]): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const message = useMessage();
const { t } = useI18n();

// 状态管理
const loading = ref(false);
const fileTree = ref<FileNode | null>(null);
const currentPath = ref('');
const selectedItems = ref<BrowserItem[]>([]);

// 计算属性
const currentItems = computed(() => {
  if (!fileTree.value) {
    return [];
  }

  const getCurrentFolderItems = (node: FileNode, path: string): FileNode[] => {
    // 如果路径为空，返回根节点的子项
    if (path === '') {
      return node.children || [];
    }

    // 递归查找目标路径的节点
    const findNodeByPath = (currentNode: FileNode, targetPath: string): FileNode | null => {
      if (currentNode.path === targetPath) {
        return currentNode;
      }

      if (currentNode.children) {
        for (const child of currentNode.children) {
          const result = findNodeByPath(child, targetPath);
          if (result) return result;
        }
      }

      return null;
    };

    const targetNode = findNodeByPath(node, path);
    return targetNode?.children || [];
  };

  return getCurrentFolderItems(fileTree.value, currentPath.value);
});

const folders = computed(() => {
  return currentItems.value
    .filter(item => item.type === 'directory')
    .map(folder => ({
      name: folder.label,
      path: folder.path,
      type: 'directory' as const,
      fullPath: folder.path // 直接使用完整路径
    }));
});

const cardFiles = computed(() => {
  return currentItems.value
    .filter(item => item.type === 'card' || (item.type === 'file' && item.label.endsWith('.card')))
    .map(file => ({
      name: file.label.replace('.card', ''),
      path: file.path,
      type: 'card' as const,
      fullPath: file.path // 直接使用完整路径
    }));
});

// 方法
const loadFileTree = async () => {
  loading.value = true;
  try {
    const response = await WorkspaceService.getFileTree(false);
    fileTree.value = response.fileTree;
  } catch (error) {
    console.error('加载文件树失败:', error);
    message.error('加载文件树失败');
  } finally {
    loading.value = false;
  }
};

const getCurrentPathDisplay = () => {
  return currentPath.value || '工作空间根目录';
};

const navigateToParent = () => {
  if (currentPath.value === '') return;

  // 根据文件树结构找到当前文件夹的父路径
  const findParentPath = (node: FileNode, targetPath: string): string => {
    if (node.children) {
      for (const child of node.children) {
        if (child.path === targetPath) {
          return node.path || '';
        }
        if (child.children) {
          const result = findParentPath(child, targetPath);
          if (result !== undefined) return result;
        }
      }
    }
    return '';
  };

  if (fileTree.value) {
    const parentPath = findParentPath(fileTree.value, currentPath.value);
    currentPath.value = parentPath;
  }
};

const enterFolder = (folder: BrowserItem) => {
  currentPath.value = folder.path;
};

const isSelected = (item: BrowserItem) => {
  return selectedItems.value.some(selected => selected.path === item.path);
};

const toggleSelection = (item: BrowserItem) => {
  const index = selectedItems.value.findIndex(selected => selected.path === item.path);
  if (index > -1) {
    selectedItems.value.splice(index, 1);
  } else {
    selectedItems.value.push(item);
  }
};

const clearSelection = () => {
  selectedItems.value = [];
};

const confirmSelection = () => {
  if (selectedItems.value.length === 0) {
    message.warning('请至少选择一个文件或文件夹');
    return;
  }

  emit('confirm', [...selectedItems.value]);
  emit('update:visible', false);
  clearSelection();
};

// 监听器
watch(() => props.visible, (visible) => {
  if (visible) {
    loadFileTree();
    clearSelection();
    currentPath.value = '';
  }
});

// 生命周期
onMounted(() => {
  loadFileTree();
});
</script>

<style scoped>
.card-file-browser {
  display: flex;
  flex-direction: column;
  height: 600px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.browser-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.path-text {
  font-weight: 500;
  color: #2c3e50;
}

.browser-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.browser-content {
  flex: 1;
  min-height: 0;
}

.content-scroll {
  height: 100%;
}

.loading-container,
.empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
  align-items: start;
}

.file-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0.5rem;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background: #f8f9fa;
  min-height: 100px;
}

.file-item:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.file-item.selected {
  background: #e3f2fd;
  border-color: #2196f3;
}

.file-item.back-folder {
  background: #fff3e0;
  border-color: #ffb74d;
}

.file-item.back-folder:hover {
  background: #ffe0b2;
  border-color: #ff9800;
}

.item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.file-item.back-folder .item-icon {
  color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.file-item.card-file .item-icon {
  color: #4caf50;
  background: rgba(76, 175, 80, 0.1);
}

.item-name {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 500;
  color: #2c3e50;
  word-break: break-word;
  line-height: 1.2;
  max-width: 100%;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.selection-indicator {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 20px;
  height: 20px;
  background: #2196f3;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.5rem;
    padding: 1rem;
  }

  .file-item {
    padding: 0.5rem 0.25rem;
    min-height: 80px;
  }

  .item-icon {
    width: 32px;
    height: 32px;
  }

  .item-name {
    font-size: 0.65rem;
  }

  .browser-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }

  .browser-actions {
    justify-content: center;
  }
}
</style>
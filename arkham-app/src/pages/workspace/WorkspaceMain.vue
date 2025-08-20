<template>
  <div class="workspace-main-container" :class="{ 'is-resizing': isResizing }">
    <!-- 左侧文件树区域 -->
    <FileTreePanel 
      v-if="showFileTree"
      :width="fileTreeWidth"
      ref="fileTreeRef"
      @toggle="toggleFileTree"
      @go-back="goBack"
      @file-select="handleFileSelect"
    />

    <!-- 左侧分割条 -->
    <ResizeSplitter
      v-if="showFileTree"
      :is-active="isResizing && resizeType === 'fileTree'"
      title="拖拽调整文件树宽度"
      @start-resize="startResize('fileTree', $event)"
    />

    <!-- 中间JSON表单编辑区 -->
    <FormEditPanel
      :show-file-tree="showFileTree"
      :show-image-preview="showImagePreview"
      :selected-file="selectedFile"
      @toggle-file-tree="toggleFileTree"
      @toggle-image-preview="toggleImagePreview"
      @update-preview-image="updatePreviewImage"
      @refresh-file-tree="refreshFileTree"
    />

    <!-- 右侧分割条 -->
    <ResizeSplitter
      v-if="showImagePreview"
      :is-active="isResizing && resizeType === 'form'"
      title="拖拽调整预览区宽度"
      @start-resize="startResize('form', $event)"
    />

    <!-- 右侧图片预览区域 -->
    <ImagePreviewPanel
      v-if="showImagePreview"
      :width="imageWidth"
      :current-image="currentImage"
      @toggle="toggleImagePreview"
      ref="imagePreviewRef"
    />

    <!-- 拖拽时的遮罩层 -->
    <div v-if="isResizing" class="resize-overlay"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import { useMessage } from 'naive-ui';
import type { TreeOption } from 'naive-ui';
import FileTreePanel from '@/components/FileTreePanel.vue';
import FormEditPanel from '@/components/FormEditPanel.vue';
import ImagePreviewPanel from '@/components/ImagePreviewPanel.vue';
import ResizeSplitter from '@/components/ResizeSplitter.vue';
import { WorkspaceService } from '@/api';

// Props
defineProps<{
  mode: 'file' | 'folder';
  projectPath?: string;
  projectName?: string;
}>();

// Emits
const emit = defineEmits<{
  'go-back': [];
}>();

const message = useMessage();

// 布局控制
const showFileTree = ref(true);
const showImagePreview = ref(true);
const fileTreeWidth = ref(280);
const imageWidth = ref(600);

// 文件选择
const selectedFile = ref<TreeOption | null>(null);

// 图片预览
const currentImage = ref('');
const imagePreviewRef = ref();
const fileTreeRef = ref();

const toggleFileTree = () => {
  showFileTree.value = !showFileTree.value;
};

const toggleImagePreview = () => {
  showImagePreview.value = !showImagePreview.value;
};

const goBack = () => {
  emit('go-back');
};

// 检查是否是图片文件
const isImageFile = (option: TreeOption): boolean => {
  if (option.type === 'image') return true;
  
  if (typeof option.key === 'string' && option.path) {
    const extension = option.path.split('.').pop()?.toLowerCase() || '';
    return ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'tiff', 'ico'].includes(extension);
  }
  
  return false;
};

// 从文件路径加载图片
const loadImageFromPath = async (imagePath: string): Promise<string | null> => {
  try {
    // 首先检查文件信息，确认是否为图片文件
    const fileInfo = await WorkspaceService.getFileInfo(imagePath);
    
    if (!fileInfo.is_image) {
      console.warn('选中的文件不是图片格式');
      return null;
    }
    
    // 调用新的图片内容API
    const imageContent = await WorkspaceService.getImageContent(imagePath);
    return imageContent;
    
  } catch (error) {
    console.error('加载图片失败:', error);
    message.error('加载图片失败');
    return null;
  }
};



const handleFileSelect = async (keys: Array<string | number>, option?: TreeOption) => {
  // 保存选中的文件信息
  selectedFile.value = option || null;
  
  // 如果选中的是图片文件，加载并显示图片
  if (option && isImageFile(option)) {
    if (option.path) {
      const imageData = await loadImageFromPath(option.path);
      if (imageData) {
        currentImage.value = imageData;
        imagePreviewRef.value?.fitToContainer();
      }
    }
  } else {
    // 如果不是图片文件，清空当前图片预览
    currentImage.value = '';
  }
};

// 更新预览图片（来自表单编辑器的卡图生成）
const updatePreviewImage = (imageBase64: string) => {
  currentImage.value = imageBase64;
  imagePreviewRef.value?.fitToContainer();
};

// 刷新文件树
const refreshFileTree = () => {
  if (fileTreeRef.value && typeof fileTreeRef.value.refreshFileTree === 'function') {
    fileTreeRef.value.refreshFileTree();
  }
};

// 拖拽调整大小 (保持原有逻辑)
const isResizing = ref(false);
const resizeType = ref('');
let startX = 0;
let startWidth = 0;
let animationFrameId: number;

const throttledResize = (callback: Function) => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  animationFrameId = requestAnimationFrame(() => {
    callback();
  });
};

const startResize = (type: string, event: MouseEvent) => {
  isResizing.value = true;
  resizeType.value = type;
  startX = event.clientX;
  startWidth = type === 'fileTree' ? fileTreeWidth.value : imageWidth.value;

  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  document.body.style.pointerEvents = 'none';
  document.documentElement.style.setProperty('--resize-transition', 'none');

  document.addEventListener('mousemove', handleResize, { passive: true });
  document.addEventListener('mouseup', stopResize);
  event.preventDefault();
  event.stopPropagation();
};

const handleResize = (event: MouseEvent) => {
  if (!isResizing.value) return;
  throttledResize(() => {
    const deltaX = event.clientX - startX;
    if (resizeType.value === 'fileTree') {
      const newWidth = Math.max(200, Math.min(600, startWidth + deltaX));
      fileTreeWidth.value = newWidth;
    } else if (resizeType.value === 'form') {
      const newWidth = Math.max(250, Math.min(700, startWidth - deltaX));
      imageWidth.value = newWidth;
    }
  });
};

const stopResize = () => {
  isResizing.value = false;
  resizeType.value = '';
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  document.body.style.pointerEvents = '';
  document.documentElement.style.setProperty('--resize-transition', '0.3s cubic-bezier(0.4, 0, 0.2, 1)');
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
};

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});
</script>

<style scoped>
:root {
  --resize-transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.workspace-main-container {
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.workspace-main-container.is-resizing * {
  transition: none !important;
  pointer-events: none;
}

.resize-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: transparent;
  cursor: col-resize;
  z-index: 9999;
  pointer-events: all;
}

@media (max-width: 1200px) {
  .workspace-main-container {
    flex-direction: column;
  }
}
</style>

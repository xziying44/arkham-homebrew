<template>
  <div class="workspace-main-container" :class="{ 'is-resizing': isResizing }">
    <!-- 左侧文件树区域 -->
    <FileTreePanel 
      v-if="showFileTree"
      :width="fileTreeWidth"
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
import type { TreeOption } from 'naive-ui';
import FileTreePanel from '@/components/FileTreePanel.vue';
import FormEditPanel from '@/components/FormEditPanel.vue';
import ImagePreviewPanel from '@/components/ImagePreviewPanel.vue';
import ResizeSplitter from '@/components/ResizeSplitter.vue';

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

const toggleFileTree = () => {
  showFileTree.value = !showFileTree.value;
};

const toggleImagePreview = () => {
  showImagePreview.value = !showImagePreview.value;
};

const goBack = () => {
  emit('go-back');
};

const handleFileSelect = (keys: Array<string | number>, option?: TreeOption) => {
  // 保存选中的文件信息
  selectedFile.value = option || null;
  
  // 如果选中的是图片文件，更新图片预览
  if (option && (option.type === 'image' || 
      (typeof option.key === 'string' && 
       (option.key.includes('image') || option.key === 'bg1' || option.key === 'portrait1' || 
        option.key === 'icons' || option.key === 'logo' || option.key === 'texture')))) {
    currentImage.value = `https://picsum.photos/600/400?random=${option.key}`;
    imagePreviewRef.value?.resetImageView();
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

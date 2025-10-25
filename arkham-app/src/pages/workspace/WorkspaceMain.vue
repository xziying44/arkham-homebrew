<template>
  <div class="workspace-main-container" :class="{ 'is-resizing': isResizing }">
    <!-- 左侧文件树区域 -->
    <FileTreePanel 
      v-if="showFileTree && shouldShowFileTree"
      :width="fileTreeWidth"
      ref="fileTreeRef"
      @toggle="toggleFileTree"
      @go-back="goBack"
      @file-select="handleFileSelect"
    />

    <!-- 左侧分割条 -->
    <ResizeSplitter
      v-if="showFileTree && shouldShowFileTree"
      :is-active="isResizing && resizeType === 'fileTree'"
      :title="$t('workspaceMain.fileTree.adjustWidth')"
      @start-resize="startResize('fileTree', $event)"
    />

    <!-- 中间JSON表单编辑区 -->
    <FormEditPanel
      ref="formEditPanelRef"
      :show-file-tree="showFileTree && shouldShowFileTree"
      :show-image-preview="showImagePreview && shouldShowImagePreview"
      :selected-file="selectedFile"
      :is-mobile="isMobile"
      @toggle-file-tree="toggleFileTree"
      @toggle-image-preview="toggleImagePreview"
      @update-preview-image="updatePreviewImage"
      @update-preview-side="updatePreviewSide"
      @update-preview-loading="updatePreviewLoading"
      @refresh-file-tree="refreshFileTree"
    />

    <!-- 右侧分割条 -->
    <ResizeSplitter
      v-if="showImagePreview && shouldShowImagePreview"
      :is-active="isResizing && resizeType === 'form'"
      :title="$t('workspaceMain.imagePreview.adjustWidth')"
      @start-resize="startResize('form', $event)"
    />

    <!-- 右侧图片预览区域 -->
    <ImagePreviewPanel
      v-if="showImagePreview && shouldShowImagePreview"
      :width="imageWidth"
      :current-image="currentImage"
      :image-key="typeof selectedFile?.path === 'string' ? selectedFile.path : null"
      :current-side="currentPreviewSide"
      :is-mobile="isMobile"
      :is-loading="imagePreviewLoading"
      @toggle="toggleImagePreview"
      @update-side="updatePreviewSideFromImage"
      ref="imagePreviewRef"
    />

    <!-- 拖拽时的遮罩层 -->
    <div v-if="isResizing" class="resize-overlay"></div>

    <!-- 移动端浮动按钮 -->
    <div v-if="isMobile" class="mobile-controls">
      <button 
        v-if="!shouldShowFileTree && showFileTree"
        class="mobile-button file-tree-btn"
        @click="toggleMobileFileTree"
      >
        📁
      </button>
      <button 
        v-if="!shouldShowImagePreview && showImagePreview && currentImage"
        class="mobile-button image-preview-btn"
        @click="toggleMobileImagePreview"
      >
        🖼️
      </button>
    </div>

    <!-- 移动端全屏模态框 -->
    <div v-if="showMobileFileTree" class="mobile-modal" @click="closeMobileFileTree">
      <div class="mobile-modal-content file-tree-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('workspaceMain.fileTree.title') }}</h3>
          <button class="close-btn" @click="closeMobileFileTree">{{ $t('workspaceMain.modals.close') }}</button>
        </div>
        <FileTreePanel 
          :width="'100%'"
          ref="mobileFileTreeRef"
          @file-select="handleMobileFileSelect"
          @go-back="goBack"
        />
      </div>
    </div>

    <div v-if="showMobileImagePreview" class="mobile-modal" @click="closeMobileImagePreview">
      <div class="mobile-modal-content image-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('workspaceMain.imagePreview.title') }}</h3>
          <button class="close-btn" @click="closeMobileImagePreview">{{ $t('workspaceMain.modals.close') }}</button>
        </div>
        <ImagePreviewPanel
          :width="'100%'"
          :current-image="currentImage"
          :image-key="typeof selectedFile?.path === 'string' ? selectedFile.path : null"
          :current-side="currentPreviewSide"
          :is-mobile="true"
          :is-loading="imagePreviewLoading"
          @update-side="updatePreviewSideFromImage"
          ref="mobileImagePreviewRef"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
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
const { t } = useI18n();

// 响应式断点
const BREAKPOINT_LARGE = 1200;  // 隐藏文件树的断点
const BREAKPOINT_MEDIUM = 800;  // 隐藏图片预览的断点
const BREAKPOINT_MOBILE = 768;  // 移动端断点

// 窗口尺寸状态
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value < BREAKPOINT_MOBILE);

// 基于窗口大小的显示控制
const shouldShowFileTree = computed(() => {
  return windowWidth.value >= BREAKPOINT_LARGE;
});

const shouldShowImagePreview = computed(() => {
  return windowWidth.value >= BREAKPOINT_MEDIUM;
});

// 布局控制
const showFileTree = ref(true);
const showImagePreview = ref(true);
const fileTreeWidth = ref(280);
const imageWidth = ref(600);

// 移动端模态框控制
const showMobileFileTree = ref(false);
const showMobileImagePreview = ref(false);

// 文件选择
const selectedFile = ref<TreeOption | null>(null);

// 图片预览
const currentImage = ref('');
const currentPreviewSide = ref<'front' | 'back'>('front');

// 图片预览加载状态
const imagePreviewLoading = ref(false);
const imagePreviewRef = ref();
const formEditPanelRef = ref();
const fileTreeRef = ref();
const mobileFileTreeRef = ref();
const mobileImagePreviewRef = ref();

// 窗口大小变化监听
const handleResize = () => {
  windowWidth.value = window.innerWidth;
  
  // 当窗口变大时，关闭移动端模态框
  if (!isMobile.value) {
    showMobileFileTree.value = false;
    showMobileImagePreview.value = false;
  }
  
  // 自适应调整面板宽度
  if (windowWidth.value < 1024) {
    fileTreeWidth.value = Math.min(fileTreeWidth.value, 250);
    imageWidth.value = Math.min(imageWidth.value, 400);
  }
};

// 移动端控制函数
const toggleMobileFileTree = () => {
  showMobileFileTree.value = true;
};

const closeMobileFileTree = () => {
  showMobileFileTree.value = false;
};

const toggleMobileImagePreview = () => {
  showMobileImagePreview.value = true;
};

const closeMobileImagePreview = () => {
  showMobileImagePreview.value = false;
};

const handleMobileFileSelect = async (keys: Array<string | number>, option?: TreeOption) => {
  // 处理文件选择
  await handleFileSelect(keys, option);
  // 关闭移动端文件树模态框
  closeMobileFileTree();
  // 如果选中的是图片，自动打开图片预览
  if (option && isImageFile(option) && currentImage.value) {
    showMobileImagePreview.value = true;
  }
};

const toggleFileTree = () => {
  if (isMobile.value && !shouldShowFileTree.value) {
    toggleMobileFileTree();
  } else {
    showFileTree.value = !showFileTree.value;
  }
};

const toggleImagePreview = () => {
  if (isMobile.value && !shouldShowImagePreview.value) {
    toggleMobileImagePreview();
  } else {
    showImagePreview.value = !showImagePreview.value;
  }
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
    const fileInfo = await WorkspaceService.getFileInfo(imagePath);
    
    if (!fileInfo.is_image) {
      console.warn(t('workspaceMain.messages.notImageFormat'));
      return null;
    }
    
    const imageContent = await WorkspaceService.getImageContent(imagePath);
    return imageContent;
    
  } catch (error) {
    console.error('加载图片失败:', error);
    message.error(t('workspaceMain.messages.imageLoadFailed'));
    return null;
  }
};

const handleFileSelect = async (keys: Array<string | number>, option?: TreeOption) => {
  selectedFile.value = option || null;
  
  if (option && isImageFile(option)) {
    if (option.path) {
      const imageData = await loadImageFromPath(option.path);
      if (imageData) {
        currentImage.value = imageData;
        // 移除手动调用 fitToContainer
      }
    }
  } else {
    // 如果选择的不是图片文件（比如一个 .card 文件），清空 currentImage
    // FormEditPanel 会在生成预览时通过 updatePreviewImage 来更新它
    // 这样可以避免切换文件时短暂显示旧图片
    if (option?.type !== 'card') {
      currentImage.value = '';
    }
  }
};

const updatePreviewImage = (imageBase64: string) => {
  currentImage.value = imageBase64;
  // 【重要修改】 移除这里的 fitToContainer 调用
  // 因为子组件现在会根据 imageKey 的变化自动处理
  // const previewRef = shouldShowImagePreview.value ? imagePreviewRef : mobileImagePreviewRef;
  // previewRef.value?.fitToContainer();
};

// 处理图片预览加载状态更新
const updatePreviewLoading = (loading: boolean) => {
  imagePreviewLoading.value = loading;
  console.log(`🔄 WorkspaceMain 接收到加载状态更新: ${loading ? '显示' : '隐藏'} 加载动画`);
};

// 处理编辑器端的面切换
const updatePreviewSide = (side: 'front' | 'back') => {
  currentPreviewSide.value = side;
  console.log(`📝 编辑器切换到${side}面，通知图片预览同步切换`);
};

// 处理图片预览端的面切换
const updatePreviewSideFromImage = (side: 'front' | 'back') => {
  currentPreviewSide.value = side;
  // 需要通知FormEditPanel切换
  if (formEditPanelRef.value && formEditPanelRef.value.setSideFromExternal) {
    formEditPanelRef.value.setSideFromExternal(side);
    console.log(`🖼️ 图片预览切换到${side}面，通知编辑器同步切换`);
  }
};

const refreshFileTree = () => {
  const treeRef = shouldShowFileTree.value ? fileTreeRef : mobileFileTreeRef;
  if (treeRef.value && typeof treeRef.value.refreshFileTree === 'function') {
    treeRef.value.refreshFileTree();
  }
};

// 拖拽调整大小相关代码保持不变
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

  document.addEventListener('mousemove', handleResizeEvent, { passive: true });
  document.addEventListener('mouseup', stopResize);
  event.preventDefault();
  event.stopPropagation();
};

const handleResizeEvent = (event: MouseEvent) => {
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
  document.removeEventListener('mousemove', handleResizeEvent);
  document.removeEventListener('mouseup', stopResize);
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
};

onMounted(() => {
  window.addEventListener('resize', handleResize, { passive: true });
  handleResize(); // 初始化
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  document.removeEventListener('mousemove', handleResizeEvent);
  document.removeEventListener('mouseup', stopResize);
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});
</script>

<!-- style 部分保持不变 -->
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
  position: relative;
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

/* 移动端浮动按钮 */
.mobile-controls {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.mobile-button {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #2080f0;
  color: white;
  border: none;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(32, 128, 240, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-button:hover {
  background: #1c6dd0;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(32, 128, 240, 0.4);
}

.mobile-button:active {
  transform: translateY(0);
}

/* 移动端模态框 */
.mobile-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
  box-sizing: border-box;
}

.mobile-modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  height: 100%;
  max-width: 95vw;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.file-tree-modal {
  max-width: 95vw;
  max-height: 80vh;
}

.image-modal {
  max-width: 90vw;
  max-height: 90vh;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  /* 在此断点隐藏文件树 */
}

@media (max-width: 800px) {
  /* 在此断点隐藏图片预览 */
}

@media (max-width: 768px) {
  .workspace-main-container {
    flex-direction: column;
    height: 100%;
    width: 100%;
  }

  /* 移动端样式调整 */
  .mobile-controls {
    bottom: 90px; /* 避免与底部导航冲突 */
  }

  .mobile-modal {
    padding: 10px;
  }

  .mobile-modal-content {
    max-width: 95vw;
    max-height: 95vh;
  }

  .file-tree-modal {
    max-width: 95vw;
    max-height: 75vh; /* 为顶部和底部导航预留空间 */
  }

  .image-modal {
    max-width: 95vw;
    max-height: 75vh;
  }
}

/* 超小屏幕适配 */
@media (max-width: 480px) {
  .mobile-button {
    width: 45px;
    height: 45px;
    font-size: 18px;
  }

  .mobile-controls {
    bottom: 80px;
    right: 15px;
  }

  .modal-header {
    padding: 12px 16px;
  }

  .modal-header h3 {
    font-size: 16px;
  }

  .file-tree-modal {
    max-width: 90vw;
    max-height: 70vh;
  }

  .image-modal {
    max-width: 95vw;
    max-height: 70vh;
  }

  /* 确保模态框内容在小屏幕上不溢出 */
  .mobile-modal-content {
    box-sizing: border-box;
  }
}
</style>

<template>
  <div class="image-pane" :style="{ width: width + 'px' }">
    <div class="pane-header">
      <n-space align="center" justify="space-between">
        <span class="pane-title">{{ $t('workspaceMain.imagePreview.title') }}</span>
        <n-button size="tiny" quaternary @click="$emit('toggle')">
          <n-icon :component="Close" />
        </n-button>
      </n-space>
    </div>

    <div class="image-content" ref="imageContainer">
      <!-- 双面卡牌切换按钮 -->
      <div v-if="isDoubleSided" class="card-side-switch">
        <n-button-group size="small">
          <n-button
            :type="currentDisplaySide === 'front' ? 'primary' : 'default'"
            @click="switchSide('front')"
          >
            {{ $t('workspaceMain.imagePreview.frontSide') }}
          </n-button>
          <n-button
            :type="currentDisplaySide === 'back' ? 'primary' : 'default'"
            @click="switchSide('back')"
          >
            {{ $t('workspaceMain.imagePreview.backSide') }}
          </n-button>
        </n-button-group>
      </div>

      <!-- 加载动画 - 卡牌形状毛玻璃背景 -->
      <div v-if="props.isLoading" class="card-loading-animation">
        <div class="card-shape">
          <div class="card-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">{{ $t('workspaceMain.imagePreview.loadingText') }}</div>
          </div>
        </div>
      </div>

      <!-- 实际图片显示 -->
      <div v-else-if="displayedImage" class="image-viewer" :class="{ 'is-dragging': isDragging }" @wheel="handleImageWheel"
        @mousedown="startImageDrag">
        <img :src="displayedImage" alt="预览图片" :style="{
          transform: `scale(${imageScale}) translate(${imageOffsetX}px, ${imageOffsetY}px)`,
          transformOrigin: 'center center'
        }" draggable="false" class="preview-image" @load="onImageLoad" />
      </div>

      <!-- 空状态占位符 -->
      <div v-else class="image-placeholder">
        <n-empty :description="$t('workspaceMain.imagePreview.emptyText')" size="large">
          <template #icon>
            <n-icon :component="ImageOutline" />
          </template>
        </n-empty>
      </div>

      <!-- 图片控制工具栏 -->
      <div v-if="displayedImage" class="image-controls">
        <n-button-group size="small">
          <n-button @click="zoomIn" :title="$t('workspaceMain.imagePreview.controls.zoomIn')">
            <n-icon :component="AddOutline" />
          </n-button>
          <n-button @click="resetImageView">
            {{ Math.round(imageScale * 100) }}%
          </n-button>
          <n-button @click="zoomOut" :title="$t('workspaceMain.imagePreview.controls.zoomOut')">
            <n-icon :component="RemoveOutline" />
          </n-button>
          <n-button @click="fitToContainer" :title="$t('workspaceMain.imagePreview.controls.fitToWindow')">
            {{ $t('workspaceMain.imagePreview.controls.fitToWindow') }}
          </n-button>
          <n-button @click="copyImageToClipboard" :loading="isCopying"
            :title="$t('workspaceMain.imagePreview.controls.copyImage')">
            <n-icon :component="CopyOutline" />
            <span style="margin-left: 8px;">{{ $t('workspaceMain.imagePreview.controls.copyImage') }}</span>
          </n-button>
        </n-button-group>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch, nextTick } from 'vue';
import { ImageOutline, Close, AddOutline, RemoveOutline, CopyOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';

interface Props {
  width: number;
  currentImage: string | { front: string; back?: string };
  // 新增：用于识别图片是否为新文件的唯一标识
  imageKey: string | null;
  // 新增：当前要显示的面
  currentSide: 'front' | 'back';
  // 新增：是否显示加载动画
  isLoading?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'toggle': [];
  'update-side': [side: 'front' | 'back'];
}>();

const message = useMessage();
const { t } = useI18n();

// 双面卡牌状态
const currentDisplaySide = ref<'front' | 'back'>('front');

// 监听外部传入的currentSide变化
watch(() => props.currentSide, (newSide) => {
    if (newSide !== currentDisplaySide.value) {
        currentDisplaySide.value = newSide;
        console.log(`🖼️ 图片预览响应外部面切换: ${newSide}`);
    }
});

// 切换面方法
const switchSide = (side: 'front' | 'back') => {
    if (side !== currentDisplaySide.value) {
        currentDisplaySide.value = side;
        emit('update-side', side);
        console.log(`🖼️ 图片预览主动切换到${side}面，通知编辑器同步`);
    }
};

// 判断是否为双面卡牌
const isDoubleSided = computed(() => {
  return typeof props.currentImage === 'object' && props.currentImage.front;
});

// 获取当前显示的图片URL
const displayedImage = computed(() => {
  if (isDoubleSided.value) {
    const imageObj = props.currentImage as { front: string; back?: string };
    return currentDisplaySide.value === 'back' && imageObj.back
      ? imageObj.back
      : imageObj.front;
  }
  return props.currentImage as string;
});

// 图片预览状态
const imageScale = ref(1);
const imageOffsetX = ref(0);
const imageOffsetY = ref(0);
const imageContainer = ref<HTMLElement>();
const isDragging = ref(false);
const isCopying = ref(false);

// 新增：核心状态，用于判断视图是否由用户控制
const isViewUserControlled = ref(false);

let dragStartX = 0;
let dragStartY = 0;
let dragStartOffsetX = 0;
let dragStartOffsetY = 0;
let dragAnimationFrameId: number;

// 复制图片到剪贴板
const copyImageToClipboard = async () => {
  if (!displayedImage.value || isCopying.value) return;

  try {
    isCopying.value = true;

    // 检查浏览器是否支持 Clipboard API
    if (!navigator.clipboard || !navigator.clipboard.write) {
      message.warning(t('workspaceMain.imagePreview.messages.copyNotSupported'));
      return;
    }

    // 获取图片数据
    const response = await fetch(displayedImage.value);
    if (!response.ok) {
      throw new Error('获取图片失败');
    }

    const blob = await response.blob();

    // 检查是否为图片类型
    if (!blob.type.startsWith('image/')) {
      throw new Error('不是有效的图片格式');
    }

    // 复制到剪贴板
    await navigator.clipboard.write([
      new ClipboardItem({
        [blob.type]: blob
      })
    ]);

    message.success(t('workspaceMain.imagePreview.messages.copySuccess'));
  } catch (error) {
    console.error('复制图片失败:', error);

    // 如果是权限错误，给出特殊提示
    if (error instanceof Error && error.name === 'NotAllowedError') {
      message.error(t('workspaceMain.imagePreview.messages.copyPermissionDenied'));
    } else if (error instanceof Error && error.message.includes('获取图片失败')) {
      message.error(t('workspaceMain.imagePreview.messages.copyImageFetchFailed'));
    } else if (error instanceof Error && error.message.includes('不是有效的图片格式')) {
      message.error(t('workspaceMain.imagePreview.messages.copyInvalidFormat'));
    } else {
      message.error(t('workspaceMain.imagePreview.messages.copyFailed'));
    }
  } finally {
    isCopying.value = false;
  }
};

// 计算图片的适应缩放比例
const calculateFitScale = (imageElement: HTMLImageElement) => {
  if (!imageContainer.value) return 1;

  const containerRect = imageContainer.value.getBoundingClientRect();
  const containerWidth = containerRect.width - 40; // 留一些边距
  const containerHeight = containerRect.height - 80; // 留一些边距给工具栏

  const imageWidth = imageElement.naturalWidth;
  const imageHeight = imageElement.naturalHeight;

  if (imageWidth === 0 || imageHeight === 0) return 1;

  // 计算适应容器的缩放比例
  const scaleX = containerWidth / imageWidth;
  const scaleY = containerHeight / imageHeight;

  // 取较小的缩放比例以保持图片完整显示，并限制最大缩放比例
  return Math.min(scaleX, scaleY, 1);
};

// 【核心修改】图片加载完成时的处理
const onImageLoad = (event: Event) => {
  // 只有在视图不是由用户控制时，才自动适应
  if (!isViewUserControlled.value) {
    const img = event.target as HTMLImageElement;
    nextTick(() => {
      const fitScale = calculateFitScale(img);
      imageScale.value = fitScale;
      imageOffsetX.value = 0;
      imageOffsetY.value = 0;
      console.log('🖼️ 自动适应图片尺寸:', fitScale);
    });
  } else {
    console.log('🔒 用户控制模式，跳过自动适应');
  }
};

// 适应窗口 - 用户主动操作，将视图控制权交还给自动适应
const fitToContainer = () => {
  const imageElement = document.querySelector('.preview-image') as HTMLImageElement;
  if (imageElement) {
    // 允许下一次加载时自动适应
    isViewUserControlled.value = false;

    // 立即执行一次适应
    const fitScale = calculateFitScale(imageElement);
    imageScale.value = fitScale;
    imageOffsetX.value = 0;
    imageOffsetY.value = 0;
    console.log('🎯 手动适应窗口，重置用户控制状态');
  }
};

// 【核心修改】鼠标滚轮缩放 - 标记为用户控制
const handleImageWheel = (event: WheelEvent) => {
  event.preventDefault();
  isViewUserControlled.value = true;
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  imageScale.value = Math.max(0.1, Math.min(5, imageScale.value + delta));
};

// 【核心修改】放大 - 标记为用户控制
const zoomIn = () => {
  isViewUserControlled.value = true;
  imageScale.value = Math.min(5, imageScale.value + 0.2);
};

// 【核心修改】缩小 - 标记为用户控制
const zoomOut = () => {
  isViewUserControlled.value = true;
  imageScale.value = Math.max(0.1, imageScale.value - 0.2);
};

// 【核心修改】重置视图 - 标记为用户控制
const resetImageView = () => {
  isViewUserControlled.value = true;
  imageScale.value = 1;
  imageOffsetX.value = 0;
  imageOffsetY.value = 0;
};

// 【核心修改】开始拖拽 - 标记为用户控制
const startImageDrag = (event: MouseEvent) => {
  isViewUserControlled.value = true;
  isDragging.value = true;
  dragStartX = event.clientX;
  dragStartY = event.clientY;
  dragStartOffsetX = imageOffsetX.value;
  dragStartOffsetY = imageOffsetY.value;

  document.addEventListener('mousemove', handleImageDrag, { passive: true });
  document.addEventListener('mouseup', stopImageDrag);
  event.preventDefault();
};

const handleImageDrag = (event: MouseEvent) => {
  if (!isDragging.value) return;

  if (dragAnimationFrameId) {
    cancelAnimationFrame(dragAnimationFrameId);
  }

  dragAnimationFrameId = requestAnimationFrame(() => {
    const deltaX = event.clientX - dragStartX;
    const deltaY = event.clientY - dragStartY;

    imageOffsetX.value = dragStartOffsetX + deltaX;
    imageOffsetY.value = dragStartOffsetY + deltaY;
  });
};

const stopImageDrag = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', handleImageDrag);
  document.removeEventListener('mouseup', stopImageDrag);

  if (dragAnimationFrameId) {
    cancelAnimationFrame(dragAnimationFrameId);
  }
};

// 【核心修改】监听 imageKey 的变化
watch(() => props.imageKey, (newKey, oldKey) => {
  // 当 key 变化时，说明加载了一个全新的文件，此时应重置视图控制状态，允许自动适应
  if (newKey !== oldKey) {
    isViewUserControlled.value = false;
    // 如果是新图片，重置显示面为正面
    currentDisplaySide.value = 'front';
    console.log(`✨ New image key detected: ${newKey}. Auto-fit re-enabled, reset to front side.`);
  }
});

// 新增：监听 currentImage 的变化，特别是双面卡牌数据结构的变化
watch(() => props.currentImage, (newImage, oldImage) => {
  // 检测双面卡牌数据结构的变化
  const wasDoubleSided = typeof oldImage === 'object' && oldImage.front;
  const isDoubleSidedNow = typeof newImage === 'object' && newImage.front;

  if (isDoubleSidedNow && !wasDoubleSided) {
    // 从单面卡牌切换到双面卡牌，或加载新的双面卡牌
    console.log('🔄 双面卡牌数据加载，重置为正面显示');
    currentDisplaySide.value = 'front';
    // 允许自动适应新图片
    isViewUserControlled.value = false;
  }

  // 如果图片被清空，重置所有状态
  if (!newImage) {
    isViewUserControlled.value = false;
    imageScale.value = 1;
    imageOffsetX.value = 0;
    imageOffsetY.value = 0;
    currentDisplaySide.value = 'front';
    console.log('🗑️ 图片被清空，重置所有状态');
  }
}, { deep: true });

// 注意：上面的watch已经包含了图片为空的情况处理，不需要重复监听

// 导出方法供父组件调用
defineExpose({
  resetImageView,
  fitToContainer,
  copyImageToClipboard
});

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('mousemove', handleImageDrag);
  document.removeEventListener('mouseup', stopImageDrag);

  if (dragAnimationFrameId) {
    cancelAnimationFrame(dragAnimationFrameId);
  }
});
</script>


<style scoped>
.image-pane {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: width var(--resize-transition);
  will-change: width;
}

.pane-header {
  flex-shrink: 0;
  padding: 12px 16px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.pane-title {
  font-weight: 600;
  font-size: 14px;
  color: white;
}

.image-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
}

.image-viewer {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: grab;
  overflow: hidden;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
}

.image-viewer:active,
.image-viewer.is-dragging {
  cursor: grabbing;
}

.preview-image {
  max-width: none;
  max-height: none;
  user-select: none;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  will-change: transform;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle at center, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
}

.card-side-switch {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.card-side-switch :deep(.n-button) {
  min-width: 60px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.card-side-switch :deep(.n-button--primary-type) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.image-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 卡牌加载动画样式 */
.card-loading-animation {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle at center, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
}

.card-shape {
  width: 280px;
  height: 390px;
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.05) 50%,
    rgba(255, 255, 255, 0.1) 100%);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 80px rgba(102, 126, 234, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  animation: cardFloat 3s ease-in-out infinite;
}

.card-shape::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg,
    transparent 30%,
    rgba(102, 126, 234, 0.1) 50%,
    transparent 70%);
  animation: cardShine 4s ease-in-out infinite;
}

.card-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 2;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(102, 126, 234, 0.1);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spinnerRotation 1s linear infinite;
  margin-bottom: 20px;
}

.loading-text {
  font-size: 16px;
  font-weight: 500;
  color: #667eea;
  text-align: center;
  animation: textPulse 2s ease-in-out infinite;
}

/* 加载动画关键帧 */
@keyframes cardFloat {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-8px) scale(1.02);
  }
}

@keyframes cardShine {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  50% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
  100% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
}

@keyframes spinnerRotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes textPulse {
  0%, 100% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .card-shape {
    width: 220px;
    height: 308px;
  }

  .loading-spinner {
    width: 36px;
    height: 36px;
    border-width: 3px;
    margin-bottom: 16px;
  }

  .loading-text {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .card-shape {
    width: 180px;
    height: 252px;
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
    margin-bottom: 12px;
  }

  .loading-text {
    font-size: 12px;
  }
}
</style>

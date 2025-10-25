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
      <!-- 双面卡牌切换按钮 - 仅PC端显示 -->
      <div v-if="isDoubleSided && !isMobile" class="card-side-switch">
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
      <div
        v-else-if="displayedImage"
        class="image-viewer"
        :class="{
          'is-dragging': isDragging,
          'is-mobile': isMobile
        }"
        @wheel="handleImageWheel"
        @mousedown="startImageDrag"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @touchcancel="handleTouchEnd"
      >
        <img
          :src="displayedImage"
          alt="预览图片"
          :style="{
            transform: `scale(${imageScale}) translate(${imageOffsetX}px, ${imageOffsetY}px)`,
            transformOrigin: 'center center',
            cursor: isMobile ? 'default' : 'grab'
          }"
          draggable="false"
          class="preview-image"
          @load="onImageLoad"
        />
      </div>

      <!-- 空状态占位符 -->
      <div v-else class="image-placeholder">
        <n-empty :description="$t('workspaceMain.imagePreview.emptyText')" size="large">
          <template #icon>
            <n-icon :component="ImageOutline" />
          </template>
        </n-empty>
      </div>

      <!-- 图片控制工具栏 - PC端显示完整控件，移动端只显示必要的 -->
      <div v-if="displayedImage && !isMobile" class="image-controls">
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

      <!-- 移动端简化控制 - 显示双面切换按钮 -->
      <div v-if="displayedImage && isMobile" class="mobile-controls">
        <div class="mobile-card-side-switch">
          <n-button-group size="medium">
            <n-button
              :type="currentDisplaySide === 'front' ? 'primary' : 'default'"
              @click="switchSide('front')"
              round
            >
              {{ $t('workspaceMain.imagePreview.frontSide') }}
            </n-button>
            <n-button
              v-if="isDoubleSided"
              :type="currentDisplaySide === 'back' ? 'primary' : 'default'"
              @click="switchSide('back')"
              round
            >
              {{ $t('workspaceMain.imagePreview.backSide') }}
            </n-button>
          </n-button-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch, nextTick, onMounted } from 'vue';
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

// 移动端检测
const isMobile = ref(false);

// 双面卡牌状态
const currentDisplaySide = ref<'front' | 'back'>('front');

// 移动端触摸状态
const touchStartDistance = ref(0);
const touchStartScale = ref(1);
const touchStartX = ref(0);
const touchStartY = ref(0);
const touchStartOffsetX = ref(0);
const touchStartOffsetY = ref(0);
const isTouching = ref(false);

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

// 检测是否为移动端设备
const checkIsMobile = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  const isMobileDevice = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
  const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const isSmallScreen = window.innerWidth <= 768;

  isMobile.value = isMobileDevice || (hasTouch && isSmallScreen);
  console.log('📱 设备检测:', { isMobileDevice, hasTouch, isSmallScreen, result: isMobile.value });
};

// 初始化移动端检测
onMounted(() => {
  checkIsMobile();
  window.addEventListener('resize', checkIsMobile);
});

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

  // 移动端和PC端使用不同的边距计算
  const isMobileDevice = isMobile.value;
  const horizontalMargin = isMobileDevice ? 20 : 40;
  const verticalMargin = isMobileDevice ? 60 : 80; // 移动端减少顶部工具栏占用的空间

  const containerWidth = containerRect.width - horizontalMargin;
  const containerHeight = containerRect.height - verticalMargin;

  const imageWidth = imageElement.naturalWidth;
  const imageHeight = imageElement.naturalHeight;

  if (imageWidth === 0 || imageHeight === 0) return 1;

  // 计算适应容器的缩放比例
  const scaleX = containerWidth / imageWidth;
  const scaleY = containerHeight / imageHeight;

  // 移动端允许稍微放大以确保更好的视觉效果
  const maxScale = isMobileDevice ? 1.2 : 1;

  // 取较小的缩放比例以保持图片完整显示
  const fitScale = Math.min(scaleX, scaleY);

  // 移动端特殊处理：如果图片太小，适当放大
  if (isMobileDevice && fitScale < 0.5) {
    return Math.min(0.8, fitScale * 1.6);
  }

  return Math.min(fitScale, maxScale);
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

// 【修复】鼠标滚轮缩放 - PC端专用
const handleImageWheel = (event: WheelEvent) => {
  // 如果是移动端，阻止PC端的滚轮缩放
  if (isMobile.value) return;

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

// 【修复】开始拖拽 - PC端专用
const startImageDrag = (event: MouseEvent) => {
  // 如果是移动端，阻止PC端的拖拽
  if (isMobile.value) return;

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

// 计算两点之间的距离
const getDistance = (touch1: Touch, touch2: Touch) => {
  const dx = touch1.clientX - touch2.clientX;
  const dy = touch1.clientY - touch2.clientY;
  return Math.sqrt(dx * dx + dy * dy);
};

// 移动端触摸开始事件
const handleTouchStart = (event: TouchEvent) => {
  if (!isMobile.value) return;

  // 强制阻止所有默认行为
  event.preventDefault();
  event.stopPropagation();
  isTouching.value = true;

  if (event.touches.length === 1) {
    // 单指触摸 - 准备拖动
    const touch = event.touches[0];
    touchStartX.value = touch.clientX;
    touchStartY.value = touch.clientY;
    touchStartOffsetX.value = imageOffsetX.value;
    touchStartOffsetY.value = imageOffsetY.value;
    console.log('👆 单指触摸开始，位置:', touch.clientX, touch.clientY);
  } else if (event.touches.length === 2) {
    // 双指触摸 - 准备缩放
    touchStartDistance.value = getDistance(event.touches[0], event.touches[1]);
    touchStartScale.value = imageScale.value;
    console.log('🤚 双指触摸开始，初始距离:', touchStartDistance.value);
  }
};

// 移动端触摸移动事件
const handleTouchMove = (event: TouchEvent) => {
  if (!isMobile.value || !isTouching.value) return;

  // 强制阻止所有默认行为，包括页面滚动
  event.preventDefault();
  event.stopPropagation();

  if (event.touches.length === 1) {
    // 单指拖动
    const touch = event.touches[0];
    const deltaX = touch.clientX - touchStartX.value;
    const deltaY = touch.clientY - touchStartY.value;

    imageOffsetX.value = touchStartOffsetX.value + deltaX;
    imageOffsetY.value = touchStartOffsetY.value + deltaY;

    // 标记为用户控制
    isViewUserControlled.value = true;
  } else if (event.touches.length === 2) {
    // 双指缩放
    const currentDistance = getDistance(event.touches[0], event.touches[1]);
    const scale = currentDistance / touchStartDistance.value;

    imageScale.value = Math.max(0.1, Math.min(5, touchStartScale.value * scale));

    // 标记为用户控制
    isViewUserControlled.value = true;
    console.log('🔍 双指缩放:', imageScale.value.toFixed(2));
  }
};

// 移动端触摸结束事件
const handleTouchEnd = (event: TouchEvent) => {
  if (!isMobile.value) return;

  event.preventDefault();
  event.stopPropagation();
  isTouching.value = false;
  console.log('👋 触摸结束');
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
  window.removeEventListener('resize', checkIsMobile);

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
  height: 100vh !important; /* 强制占满高度 */
  min-height: 100vh !important; /* 强制最小高度 */
}

.pane-header {
  flex-shrink: 0;
  padding: 8px 12px; /* 减少内边距 */
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 40px; /* 设置最小高度 */
}

.pane-title {
  font-weight: 600;
  font-size: 13px; /* 稍微减小字体 */
  color: white;
}

.image-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  flex-direction: column;
  min-height: 0; /* 确保flex子元素能正确计算高度 */
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
  flex: 1; /* 确保image-viewer能占据所有可用空间 */
  min-height: 0; /* 确保flex子元素能正确计算高度 */
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

/* 移动端专用样式 */
.mobile-controls {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 15;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 8px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 强制移动端占满高度 */
@media (max-width: 768px) {
  .image-pane {
    height: 100vh !important;
    min-height: 100vh !important;
  }

  .image-content {
    flex: 1 !important;
    height: calc(100vh - 40px) !important; /* 减去标题栏高度 */
    min-height: calc(100vh - 40px) !important;
  }

  .image-viewer {
    flex: 1 !important;
    height: calc(100vh - 120px) !important; /* 减去标题栏和控制按钮高度 */
    min-height: calc(100vh - 120px) !important;
  }
}

.mobile-card-side-switch :deep(.n-button) {
  min-width: 70px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.mobile-card-side-switch :deep(.n-button--primary-type) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.mobile-card-side-switch :deep(.n-button--default-type) {
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(226, 232, 240, 0.6);
  color: #64748b;
}

.mobile-card-side-switch :deep(.n-button--default-type:hover) {
  background: rgba(241, 245, 249, 0.95);
  border-color: rgba(203, 213, 225, 0.8);
  color: #475569;
}

.image-viewer.is-mobile {
  cursor: default;
  touch-action: none; /* 防止浏览器默认的触摸行为 */
  user-select: none; /* 防止文本选择 */
  -webkit-user-select: none; /* Safari兼容 */
  -moz-user-select: none; /* Firefox兼容 */
  -ms-user-select: none; /* IE兼容 */
  overscroll-behavior: contain; /* 防止滚动传播 */
}

.image-viewer.is-mobile .preview-image {
  cursor: default;
}

/* 确保PC端光标样式不受影响 */
.image-viewer:not(.is-mobile) {
  cursor: grab;
}

.image-viewer:not(.is-mobile):active,
.image-viewer:not(.is-mobile).is-dragging {
  cursor: grabbing;
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

  /* 移动端隐藏PC端控件 - 只在小屏幕设备上生效 */
  .card-side-switch {
    display: none;
  }

  .image-controls {
    display: none;
  }

  /* 确保移动端控件显示 */
  .mobile-controls {
    display: block !important;
  }

  /* 移动端内容区域优化 - 只在移动设备上生效 */
  .image-content {
    overflow: hidden;
  }

  /* 移动端图片查看器优化 - 只在移动设备上生效 */
  .image-viewer {
    padding: 5px; /* 进一步减少内边距 */
    touch-action: none;
    position: relative;
    /* 强制阻止所有触摸行为 */
    -webkit-touch-callout: none;
    -webkit-tap-highlight-color: transparent;
    flex: 1; /* 确保移动端也能占满空间 */
    min-height: 0; /* 确保flex子元素能正确计算高度 */
  }

  .preview-image {
    max-width: calc(100vw - 20px); /* 减少边距 */
    max-height: calc(100vh - 100px); /* 增加可用高度 */
    pointer-events: none; /* 防止图片本身的触摸事件干扰 */
    object-fit: contain; /* 确保图片适应容器 */
  }
}

@media (max-width: 480px) {
  .image-pane {
    height: 100vh !important;
    min-height: 100vh !important;
  }

  .image-content {
    flex: 1 !important;
    height: calc(100vh - 35px) !important; /* 减去更小的标题栏高度 */
    min-height: calc(100vh - 35px) !important;
  }

  .image-viewer {
    flex: 1 !important;
    height: calc(100vh - 115px) !important; /* 减去标题栏和控制按钮高度 */
    min-height: calc(100vh - 115px) !important;
  }

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

  .mobile-controls {
    bottom: 20px;
    padding: 6px 12px;
  }

  .mobile-card-side-switch :deep(.n-button) {
    min-width: 60px;
    padding: 6px 12px;
    font-size: 14px;
  }

  .preview-image {
    max-width: calc(100vw - 15px); /* 进一步减少边距 */
    max-height: calc(100vh - 85px); /* 进一步增加可用高度 */
    object-fit: contain; /* 确保图片适应容器 */
  }

  /* 更小的标题栏 */
  .pane-header {
    padding: 6px 10px;
    min-height: 35px;
  }

  .pane-title {
    font-size: 12px;
  }
}
</style>

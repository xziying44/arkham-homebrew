<template>
    <n-card title="插画布局设置" size="small" class="form-card illustration-editor-card">
        <n-form label-placement="top" size="small">
            <!-- 布局模式选择 -->
            <n-form-item label="布局模式">
                <n-radio-group v-model:value="internalLayout.mode" @update:value="emitUpdate">
                    <n-radio-button value="auto">自动居中</n-radio-button>
                    <n-radio-button value="custom">自定义</n-radio-button>
                </n-radio-group>
            </n-form-item>

            <!-- 自定义布局选项 -->
            <div v-if="internalLayout.mode === 'custom'" class="custom-layout-container">

                <!-- 内部比例设置 -->
                <!-- <n-form-item label="显示比例">
                    <n-slider v-model:value="internalScaleRatio" :min="0.1" :max="1" :step="0.05"
                        style="flex-grow: 1; margin-right: 16px;" />
                    <n-input-number :show-button="false" v-model:value="internalScaleRatio" :min="0.1" :max="1"
                        :step="0.05" size="small" style="min-width: 80px;" />
                </n-form-item> -->


                <!-- 上方：可视化编辑器 -->
                <div class="visual-editor-container" ref="editorContainerRef" @wheel="handleWheel">
                    <!-- 缩放提示 (已更新为 Alt) -->
                    <div class="zoom-hint">
                        按住 <n-tag size="small" :bordered="false">Alt</n-tag> + 滚动以缩放
                    </div>

                    <div class="visual-editor">
                        <div class="crosshair-x"></div>
                        <div class="crosshair-y"></div>

                        <div class="image-transform-wrapper" :style="imageTransformStyle"
                            @mousedown.prevent="startDrag">
                            <img :src="imageSrc" class="editor-image" draggable="false" ref="imageRef"
                                @load="onImageLoad" />

                            <div v-if="isImageLoaded" class="crop-box" :style="cropBoxStyle">
                                <div class="handle top" :style="handleStyle"
                                    @mousedown.stop.prevent="startResize('top')"></div>
                                <div class="handle bottom" :style="handleStyle"
                                    @mousedown.stop.prevent="startResize('bottom')"></div>
                                <div class="handle left" :style="handleStyle"
                                    @mousedown.stop.prevent="startResize('left')"></div>
                                <div class="handle right" :style="handleStyle"
                                    @mousedown.stop.prevent="startResize('right')"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 下方：数值输入 -->
                <div class="custom-inputs-container" :class="{ 'disabled': !isImageLoaded }">
                    <!-- 第一行：偏移 和 裁剪 - 左右布局 -->
                    <div class="inputs-row-split">
                        <div class="split-column">
                            <n-card size="small" title="偏移 (Offset)">
                                <div class="input-field-group">
                                    <div class="input-field">
                                        <span class="input-label">X 轴</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.offset.x"
                                            :step="10" @update:value="emitUpdate" :disabled="!isImageLoaded"
                                            style="flex-grow: 1;" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">Y 轴</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.offset.y"
                                            :step="10" @update:value="emitUpdate" :disabled="!isImageLoaded"
                                            style="flex-grow: 1;" />
                                    </div>
                                </div>
                            </n-card>
                        </div>

                        <div class="split-column">
                            <n-card size="small"
                                :title="`裁剪 (px) - 原图 ${imageNaturalSize.width}x${imageNaturalSize.height}`">
                                <div class="crop-inputs">
                                    <div class="input-field">
                                        <span class="input-label">上</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.top"
                                            :min="0" :max="imageNaturalSize.height - internalLayout.crop.bottom - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">下</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.bottom"
                                            :min="0" :max="imageNaturalSize.height - internalLayout.crop.top - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">左</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.left"
                                            :min="0" :max="imageNaturalSize.width - internalLayout.crop.right - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">右</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.right"
                                            :min="0" :max="imageNaturalSize.width - internalLayout.crop.left - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                </div>
                            </n-card>
                        </div>
                    </div>

                    <!-- 第二行：缩放 - 独占一行 -->
                    <div class="inputs-row-full">
                        <n-card size="small" title="缩放 (Scale)">
                            <div class="input-field scale-field">
                                <span class="input-label">比例</span>
                                <n-slider v-model:value="internalLayout.scale" :min="0.1" :max="5" :step="0.01"
                                    @update:value="emitUpdate" :disabled="!isImageLoaded" style="flex-grow: 1;" />
                                <n-input-number :show-button="false" v-model:value="internalLayout.scale" :min="0.1"
                                    :max="5" :step="0.01" size="small" class="scale-input-number"
                                    @update:value="emitUpdate" :disabled="!isImageLoaded" />
                            </div>
                        </n-card>
                    </div>
                </div>
            </div>
        </n-form>
    </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, onUnmounted } from 'vue';

// 接口定义
interface PictureLayout {
    mode: 'auto' | 'custom';
    offset: { x: number; y: number };
    scale: number;
    crop: { top: number; right: number; bottom: number; left: number }; // PIXELS
}

// 默认值
const defaultLayout: PictureLayout = {
    mode: 'auto',
    offset: { x: 0, y: 0 },
    scale: 1,
    crop: { top: 0, right: 0, bottom: 0, left: 0 },
};

const props = defineProps<{ imageSrc: string; layout?: Partial<PictureLayout>; card_type?: string }>();
const emit = defineEmits<{ 'update:layout': [layout: PictureLayout]; }>();

// 内部状态
const internalLayout = reactive<PictureLayout>({ ...defaultLayout });
const imageNaturalSize = ref({ width: 0, height: 0 });
const editorContainerRef = ref<HTMLElement | null>(null);
const imageRef = ref<HTMLImageElement | null>(null);
const internalScaleRatio = ref(0.6); // 内部比例，默认0.3
if (props.card_type === '调查员' || props.card_type === '场景卡-大画' || props.card_type === '密谋卡-大画') {
    internalScaleRatio.value = 0.35
}

// 交互状态
const isDragging = ref(false);
const dragStart = { x: 0, y: 0 };
const dragStartOffset = { x: 0, y: 0 };
const isResizing = ref(false);
const resizeHandle = ref('');
const resizeStart = { x: 0, y: 0 };
const resizeStartCrop = { top: 0, right: 0, bottom: 0, left: 0 };

// 计算属性
const isImageLoaded = computed(() => imageNaturalSize.value.width > 0 && imageNaturalSize.value.height > 0);

// 计算实际显示的缩放比例
const actualDisplayScale = computed(() => internalLayout.scale * internalScaleRatio.value);

// 手柄样式：使用反向缩放保持固定像素大小
const handleStyle = computed(() => {
    const inverseScale = 1 / actualDisplayScale.value;
    return {
        transform: `scale(${inverseScale})`,
        transformOrigin: 'center'
    };
});

// 模拟后端渲染逻辑的变换样式
const imageTransformStyle = computed(() => {
    // 后端逻辑：先缩放(scale)，再偏移(offset)
    // 前端需要同样的顺序：scale() translate()
    // 但由于CSS transform的执行顺序是从右到左，所以要写成: translate() scale()
    // 偏移量在缩放后应用，所以需要除以实际缩放比例来补偿视觉效果
    const visualOffsetX = internalLayout.offset.x * internalScaleRatio.value;
    const visualOffsetY = internalLayout.offset.y * internalScaleRatio.value;

    return {
        transform: `translate(${visualOffsetX}px, ${visualOffsetY}px) scale(${actualDisplayScale.value})`,
        cursor: isDragging.value ? 'grabbing' : 'grab',
    };
});

const cropBoxStyle = computed(() => ({
    top: `${internalLayout.crop.top}px`,
    right: `${internalLayout.crop.right}px`,
    bottom: `${internalLayout.crop.bottom}px`,
    left: `${internalLayout.crop.left}px`,
}));

// 监听与更新
watch(() => props.layout, (newLayout) => {
    const mergedLayout = { ...defaultLayout, ...newLayout, offset: { ...defaultLayout.offset, ...newLayout?.offset }, crop: { ...defaultLayout.crop, ...newLayout?.crop } };
    Object.assign(internalLayout, mergedLayout);
}, { immediate: true, deep: true });

const onImageLoad = (event: Event) => {
    const img = event.target as HTMLImageElement;
    imageNaturalSize.value = { width: img.naturalWidth, height: img.naturalHeight };
};

watch(() => props.imageSrc, () => { imageNaturalSize.value = { width: 0, height: 0 }; });

const emitUpdate = () => {
    if (!isImageLoaded.value) return;
    const { width, height } = imageNaturalSize.value;
    ['top', 'bottom', 'left', 'right'].forEach((key) => {
        internalLayout.crop[key] = Math.max(0, Math.round(internalLayout.crop[key]));
    });
    if (internalLayout.crop.top + internalLayout.crop.bottom >= height) { const total = internalLayout.crop.top + internalLayout.crop.bottom; internalLayout.crop.top = (internalLayout.crop.top / total) * (height - 1); internalLayout.crop.bottom = (internalLayout.crop.bottom / total) * (height - 1); }
    if (internalLayout.crop.left + internalLayout.crop.right >= width) { const total = internalLayout.crop.left + internalLayout.crop.right; internalLayout.crop.left = (internalLayout.crop.left / total) * (width - 1); internalLayout.crop.right = (internalLayout.crop.right / total) * (width - 1); }
    emit('update:layout', JSON.parse(JSON.stringify(internalLayout)));
};

// 缩放处理：基于用户感知的比例
const handleWheel = (e: WheelEvent) => {
    if (!e.altKey) {
        return; // 未按 Alt，正常滚动页面
    }
    e.preventDefault(); // 按了 Alt，阻止页面滚动和浏览器默认行为
    const delta = e.deltaY > 0 ? -0.05 : 0.05;
    internalLayout.scale = parseFloat(Math.max(0.1, Math.min(5, internalLayout.scale + delta)).toFixed(2));
    emitUpdate();
};

// 拖拽处理：偏移量直接对应后端的offset值
const startDrag = (e: MouseEvent) => {
    isDragging.value = true;
    dragStart.x = e.clientX;
    dragStart.y = e.clientY;
    dragStartOffset.x = internalLayout.offset.x;
    dragStartOffset.y = internalLayout.offset.y;
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', stopDrag);
};

const onDrag = (e: MouseEvent) => {
    if (!isDragging.value) return;
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;

    // 偏移量转换：前端拖拽的像素需要转换为后端的offset值
    // 由于后端的offset是在缩放后直接应用的，所以需要除以内部比例
    internalLayout.offset.x = dragStartOffset.x + dx / internalScaleRatio.value;
    internalLayout.offset.y = dragStartOffset.y + dy / internalScaleRatio.value;
};

const stopDrag = () => {
    if (!isDragging.value) return;
    isDragging.value = false;
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', stopDrag);
    emitUpdate();
};

// 调整大小处理：基于实际显示比例
const startResize = (handle: string) => {
    isResizing.value = true;
    resizeHandle.value = handle;
    resizeStart.x = event.clientX;
    resizeStart.y = event.clientY;
    Object.assign(resizeStartCrop, internalLayout.crop);
    window.addEventListener('mousemove', onResize);
    window.addEventListener('mouseup', stopResize);
};

const onResize = (e: MouseEvent) => {
    if (!isResizing.value) return;
    // 使用实际显示的比例进行计算
    const dx = (e.clientX - resizeStart.x) / actualDisplayScale.value;
    const dy = (e.clientY - resizeStart.y) / actualDisplayScale.value;
    const currentCrop = { ...resizeStartCrop };
    const { width, height } = imageNaturalSize.value;

    switch (resizeHandle.value) {
        case 'top': currentCrop.top += dy; break;
        case 'bottom': currentCrop.bottom -= dy; break;
        case 'left': currentCrop.left += dx; break;
        case 'right': currentCrop.right -= dx; break;
    }

    currentCrop.top = Math.max(0, Math.min(currentCrop.top, height - currentCrop.bottom - 1));
    currentCrop.bottom = Math.max(0, Math.min(currentCrop.bottom, height - currentCrop.top - 1));
    currentCrop.left = Math.max(0, Math.min(currentCrop.left, width - currentCrop.right - 1));
    currentCrop.right = Math.max(0, Math.min(currentCrop.right, width - currentCrop.left - 1));
    Object.assign(internalLayout.crop, currentCrop);
};

const stopResize = () => {
    if (!isResizing.value) return;
    isResizing.value = false;
    window.removeEventListener('mousemove', onResize);
    window.removeEventListener('mouseup', stopResize);
    emitUpdate();
};

onUnmounted(() => { stopDrag(); stopResize(); });
</script>

<style scoped>
.illustration-editor-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
    border: 1px solid rgba(102, 126, 234, 0.2);
}

.custom-layout-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-top: 16px;
}

.visual-editor-container {
    position: relative;
    background-color: #f0f2f5;
    border-radius: 8px;
    height: 300px;
    overflow: hidden;
    border: 1px solid #e0e0e0;
}

.visual-editor {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 更明显的十字线 */
.crosshair-x,
.crosshair-y {
    position: absolute;
    background-color: rgba(50, 50, 50, 0.8);
    z-index: 1;
    pointer-events: none;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.6);
}

.crosshair-x {
    width: 100%;
    height: 2px;
    top: 50%;
    transform: translateY(-50%);
}

.crosshair-y {
    width: 2px;
    height: 100%;
    left: 50%;
    transform: translateX(-50%);
}

.image-transform-wrapper {
    position: relative;
    display: inline-block;
    will-change: transform;
    transform-origin: center center;
    z-index: 2;
}

.editor-image {
    display: block;
    max-width: none;
    max-height: none;
    user-select: none;
    pointer-events: none;
}

.crop-box {
    position: absolute;
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
    border: 1px dashed rgba(255, 255, 255, 0.8);
    z-index: 3;
    pointer-events: none;
}

/* 固定12px大小的裁剪手柄样式 */
.handle {
    position: absolute;
    background-color: #ffffff;
    border: 2px solid #2080f0;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    z-index: 4;
    pointer-events: all;
    transition: all 0.2s ease;
}

.handle:hover {
    background-color: #2080f0;
    border-color: #ffffff;
    box-shadow: 0 4px 12px rgba(32, 128, 240, 0.5);
}

.handle.top,
.handle.bottom {
    height: 8px;
    width: 24px;
    left: 50%;
    transform-origin: center;
    cursor: ns-resize;
}

.handle.left,
.handle.right {
    width: 8px;
    height: 24px;
    top: 50%;
    transform-origin: center;
    cursor: ew-resize;
}

.handle.top {
    top: -4px;
}

.handle.bottom {
    bottom: -4px;
}

.handle.left {
    left: -4px;
}

.handle.right {
    right: -4px;
}

/* 手动居中，避免与内联的scale变换冲突 */
.handle.top,
.handle.bottom {
    margin-left: -12px;
}

.handle.left,
.handle.right {
    margin-top: -12px;
}

.custom-inputs-container.disabled {
    opacity: 0.5;
    pointer-events: none;
}

.zoom-hint {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background-color: rgba(0, 0, 0, 0.6);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    z-index: 10;
    pointer-events: none;
    opacity: 0.8;
    display: flex;
    align-items: center;
    gap: 4px;
}

.custom-inputs-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    transition: opacity 0.3s;
}

.inputs-row-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.inputs-row-full {
    display: flex;
}

.inputs-row-full .n-card {
    width: 100%;
}

.input-field-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-field {
    display: flex;
    align-items: center;
    gap: 8px;
}

.input-label {
    font-size: 13px;
    color: #555;
    flex-shrink: 0;
    width: 30px;
    text-align: right;
}

.crop-inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 12px;
}

.scale-input-number {
    min-width: 90px !important;
    flex-shrink: 0;
    margin-left: 16px;
}

.scale-field {
    display: flex;
    align-items: center;
    gap: 8px;
}

@media (max-width: 640px) {
    .inputs-row-split {
        grid-template-columns: 1fr;
    }
}
</style>

<template>
    <n-card :title="t('cardEditor.illustrationLayout.title')" size="small" class="form-card illustration-editor-card">
        <n-form label-placement="top" size="small">
            <!-- 布局模式选择 -->
            <n-form-item :label="t('cardEditor.illustrationLayout.layoutMode')">
                <n-radio-group v-model:value="internalLayout.mode" @update:value="emitUpdate">
                    <n-radio-button value="auto">{{ t('cardEditor.illustrationLayout.autoCenter') }}</n-radio-button>
                    <n-radio-button value="custom">{{ t('cardEditor.illustrationLayout.custom') }}</n-radio-button>
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
                        {{ t('cardEditor.illustrationLayout.zoomHint') }}
                    </div>

                    <div class="visual-editor">
                        <div class="crosshair-x"></div>
                        <div class="crosshair-y"></div>

                        <div class="image-transform-wrapper" :style="imageTransformStyle"
                            @mousedown.prevent="startDrag">
                            <img :src="imageSrc" class="editor-image" draggable="false" ref="imageRef"
                                @load="onImageLoad" />

                            <div v-if="isImageLoaded" class="crop-box" :style="cropBoxStyle">
                                <!-- ⚠️ 修改：使用动态计算的光标样式 -->
                                <div class="handle top" :style="getHandleStyle('top')"
                                    @mousedown.stop.prevent="startResize('top')"></div>
                                <div class="handle bottom" :style="getHandleStyle('bottom')"
                                    @mousedown.stop.prevent="startResize('bottom')"></div>
                                <div class="handle left" :style="getHandleStyle('left')"
                                    @mousedown.stop.prevent="startResize('left')"></div>
                                <div class="handle right" :style="getHandleStyle('right')"
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
                            <n-card size="small" :title="t('cardEditor.illustrationLayout.offset')">
                                <div class="input-field-group">
                                    <div class="input-field">
                                        <span class="input-label">{{ t('cardEditor.illustrationLayout.xAxis') }}</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.offset.x"
                                            :step="10" @update:value="emitUpdate" :disabled="!isImageLoaded"
                                            style="flex-grow: 1;" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">{{ t('cardEditor.illustrationLayout.yAxis') }}</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.offset.y"
                                            :step="10" @update:value="emitUpdate" :disabled="!isImageLoaded"
                                            style="flex-grow: 1;" />
                                    </div>
                                </div>
                            </n-card>
                        </div>

                        <div class="split-column">
                            <n-card size="small"
                                :title="t('cardEditor.illustrationLayout.crop', { width: imageNaturalSize.width, height: imageNaturalSize.height })">
                                <div class="crop-inputs">
                                    <div class="input-field">
                                        <span class="input-label">{{ t('cardEditor.illustrationLayout.top') }}</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.top"
                                            :min="0" :max="imageNaturalSize.height - internalLayout.crop.bottom - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">{{ t('cardEditor.illustrationLayout.bottom') }}</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.bottom"
                                            :min="0" :max="imageNaturalSize.height - internalLayout.crop.top - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">{{ t('cardEditor.illustrationLayout.left') }}</span>
                                        <n-input-number :show-button="false" v-model:value="internalLayout.crop.left"
                                            :min="0" :max="imageNaturalSize.width - internalLayout.crop.right - 1"
                                            :step="1" @update:value="emitUpdate" :disabled="!isImageLoaded" />
                                    </div>
                                    <div class="input-field">
                                        <span class="input-label">{{ t('cardEditor.illustrationLayout.right') }}</span>
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
                        <n-card size="small" :title="t('cardEditor.illustrationLayout.scale')">
                            <div class="input-field scale-field">
                                <span class="input-label">{{ t('cardEditor.illustrationLayout.ratio') }}</span>
                                <n-slider v-model:value="internalLayout.scale" :min="0.1" :max="5" :step="0.01"
                                    @update:value="emitUpdate" :disabled="!isImageLoaded" style="flex-grow: 1;" />
                                <n-input-number :show-button="false" v-model:value="internalLayout.scale" :min="0.1"
                                    :max="5" :step="0.01" size="small" class="scale-input-number"
                                    @update:value="emitUpdate" :disabled="!isImageLoaded" />
                            </div>
                        </n-card>
                    </div>

                    <!-- 第三行：旋转 - 独占一行 -->
                    <div class="inputs-row-full">
                        <n-card size="small" :title="t('cardEditor.illustrationLayout.rotation')">
                            <div class="rotation-container">
                                <div class="input-field">
                                    <span class="input-label">{{ t('cardEditor.illustrationLayout.angle') }}</span>
                                    <n-slider v-model:value="internalLayout.rotation" :min="-180" :max="180" :step="1"
                                        @update:value="emitUpdate" :disabled="!isImageLoaded" style="flex-grow: 1;" />
                                    <n-input-number :show-button="false" v-model:value="internalLayout.rotation"
                                        :min="-180" :max="180" :step="1" size="small" @update:value="emitUpdate"
                                        :disabled="!isImageLoaded" style="min-width: 80px;" />
                                </div>
                                <div class="rotation-preset-buttons">
                                    <n-button-group size="small">
                                        <n-button @click="internalLayout.rotation = 0; emitUpdate()"
                                            :disabled="!isImageLoaded">0°</n-button>
                                        <n-button @click="internalLayout.rotation = 90; emitUpdate()"
                                            :disabled="!isImageLoaded">90°</n-button>
                                        <n-button @click="internalLayout.rotation = 180; emitUpdate()"
                                            :disabled="!isImageLoaded">180°</n-button>
                                        <n-button @click="internalLayout.rotation = -90; emitUpdate()"
                                            :disabled="!isImageLoaded">-90°</n-button>
                                    </n-button-group>
                                </div>
                            </div>
                        </n-card>
                    </div>

                    <!-- 第四行：镜像翻转 - 紧凑布局 -->
                    <div class="inputs-row-full">
                        <n-card size="small" :title="t('cardEditor.illustrationLayout.flip')">
                            <div class="flip-controls-compact">
                                <div class="flip-button-compact">
                                    <span class="input-label-compact">{{ t('cardEditor.illustrationLayout.horizontal') }}</span>
                                    <n-switch v-model:value="internalLayout.flip_horizontal" @update:value="emitUpdate"
                                        :disabled="!isImageLoaded" size="small" />
                                </div>
                                <div class="flip-button-compact">
                                    <span class="input-label-compact">{{ t('cardEditor.illustrationLayout.vertical') }}</span>
                                    <n-switch v-model:value="internalLayout.flip_vertical" @update:value="emitUpdate"
                                        :disabled="!isImageLoaded" size="small" />
                                </div>
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
import { useI18n } from 'vue-i18n';

// 接口定义
interface PictureLayout {
    mode: 'auto' | 'custom';
    offset: { x: number; y: number };
    scale: number;
    crop: { top: number; right: number; bottom: number; left: number }; // PIXELS
    rotation: number; // 旋转角度（度数）
    flip_horizontal: boolean; // 水平镜像翻转
    flip_vertical: boolean; // 垂直镜像翻转
}

// 默认值
const defaultLayout: PictureLayout = {
    mode: 'auto',
    offset: { x: 0, y: 0 },
    scale: 1,
    crop: { top: 0, right: 0, bottom: 0, left: 0 },
    rotation: 0,
    flip_horizontal: false,
    flip_vertical: false,
};

const { t } = useI18n();
const props = defineProps<{ imageSrc: string; layout?: Partial<PictureLayout>; card_type?: string }>();
const emit = defineEmits<{ 'update:layout': [layout: PictureLayout]; }>();

// 内部状态
const internalLayout = reactive<PictureLayout>({ ...defaultLayout });
const imageNaturalSize = ref({ width: 0, height: 0 });
const editorContainerRef = ref<HTMLElement | null>(null);
const imageRef = ref<HTMLImageElement | null>(null);
const internalScaleRatio = ref(0.5); // 内部比例，默认0.3
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

// ⚠️ 新增：根据旋转角度计算光标方向
const getCursorForHandle = (handle: string): string => {
    // 归一化旋转角度到 [0, 360)
    let angle = internalLayout.rotation % 360;
    if (angle < 0) angle += 360;

    // 考虑翻转的影响
    const flipH = internalLayout.flip_horizontal;
    const flipV = internalLayout.flip_vertical;

    // 计算有效旋转角度（考虑翻转）
    // 水平+垂直翻转 = 180度旋转
    if (flipH && flipV) {
        angle = (angle + 180) % 360;
    }

    // 根据手柄和旋转角度确定光标类型
    const handleAngles = {
        'top': 0,      // 向上
        'right': 90,   // 向右
        'bottom': 180, // 向下
        'left': 270    // 向左
    };

    // 计算手柄的实际方向
    let effectiveAngle = (handleAngles[handle] + angle) % 360;

    // 单独考虑翻转的影响
    if (flipH && !flipV) {
        // 水平翻转：left ↔ right
        if (handle === 'left' || handle === 'right') {
            effectiveAngle = (effectiveAngle + 180) % 360;
        }
    } else if (!flipH && flipV) {
        // 垂直翻转：top ↔ bottom
        if (handle === 'top' || handle === 'bottom') {
            effectiveAngle = (effectiveAngle + 180) % 360;
        }
    }

    // 根据有效角度返回对应的光标
    // 将角度映射到8个方向
    const cursors = [
        'ns-resize',    // 0°   - 向上/下
        'nesw-resize',  // 45°  - 东北/西南
        'ew-resize',    // 90°  - 向左/右
        'nwse-resize',  // 135° - 西北/东南
        'ns-resize',    // 180° - 向上/下
        'nesw-resize',  // 225° - 东北/西南
        'ew-resize',    // 270° - 向左/右
        'nwse-resize',  // 315° - 西北/东南
    ];

    // 将角度映射到最近的45度倍数
    const index = Math.round(effectiveAngle / 45) % 8;
    return cursors[index];
};
// ⚠️ 修改：合并原有的handleStyle计算和新的光标计算
const getHandleStyle = (handle: string) => {
    const inverseScale = 1 / actualDisplayScale.value;
    return {
        transform: `scale(${inverseScale})`,
        transformOrigin: 'center',
        cursor: getCursorForHandle(handle) // 动态光标
    };
};

// 修复imageTransformStyle计算
const imageTransformStyle = computed(() => {
    const visualOffsetX = internalLayout.offset.x * internalScaleRatio.value;
    const visualOffsetY = internalLayout.offset.y * internalScaleRatio.value;
    let transforms = [];
    // ⚠️ 关键修改：调整顺序，让offset最后应用（写在最前面）
    // CSS transform从右到左执行，所以要反向写

    // 5. 偏移（最后执行，对应后端最后的offset）
    transforms.push(`translate(${visualOffsetX}px, ${visualOffsetY}px)`);

    // 4. 旋转
    if (internalLayout.rotation !== 0) {
        transforms.push(`rotate(${internalLayout.rotation}deg)`);
    }

    // 3. 镜像翻转
    if (internalLayout.flip_vertical) {
        transforms.push('scaleY(-1)');
    }
    if (internalLayout.flip_horizontal) {
        transforms.push('scaleX(-1)');
    }

    // 1. 基础缩放（最先执行，对应后端的scale）
    transforms.push(`scale(${actualDisplayScale.value})`);
    return {
        transform: transforms.join(' '),
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
    const mergedLayout = {
        ...defaultLayout,
        ...newLayout,
        offset: { ...defaultLayout.offset, ...newLayout?.offset },
        crop: { ...defaultLayout.crop, ...newLayout?.crop },
        rotation: newLayout?.rotation ?? 0,
        flip_horizontal: newLayout?.flip_horizontal ?? false,
        flip_vertical: newLayout?.flip_vertical ?? false
    };
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

    // 计算鼠标移动的像素距离
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    // ⚠️ 关键修改：直接映射到画布坐标系，不需要考虑旋转和翻转
    // 因为offset现在是在旋转和翻转之后应用的
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

    // 1. 计算鼠标在屏幕上的移动距离（考虑缩放）
    let dx = (e.clientX - resizeStart.x) / actualDisplayScale.value;
    let dy = (e.clientY - resizeStart.y) / actualDisplayScale.value;

    // 2. 应用旋转的逆变换
    // 将屏幕坐标系的移动转换到图片原始坐标系
    if (internalLayout.rotation !== 0) {
        const rotationRad = (-internalLayout.rotation * Math.PI) / 180; // 负角度做逆变换
        const cos = Math.cos(rotationRad);
        const sin = Math.sin(rotationRad);

        const originalDx = dx;
        const originalDy = dy;

        dx = originalDx * cos - originalDy * sin;
        dy = originalDx * sin + originalDy * cos;
    }

    // 3. 应用翻转的影响
    if (internalLayout.flip_horizontal) {
        dx = -dx;
    }
    if (internalLayout.flip_vertical) {
        dy = -dy;
    }

    // 4. 应用裁剪调整
    const currentCrop = { ...resizeStartCrop };
    const { width, height } = imageNaturalSize.value;
    switch (resizeHandle.value) {
        case 'top':
            currentCrop.top += dy;
            break;
        case 'bottom':
            currentCrop.bottom -= dy;
            break;
        case 'left':
            currentCrop.left += dx;
            break;
        case 'right':
            currentCrop.right -= dx;
            break;
    }
    // 5. 边界限制
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
}

.handle.left,
.handle.right {
    width: 8px;
    height: 24px;
    top: 50%;
    transform-origin: center;
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

/* 旋转和镜像翻转控件样式 */
.rotation-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.rotation-preset-buttons {
    display: flex;
    justify-content: center;
}

.flip-controls-compact {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 40px;
    padding: 8px 0;
}

.flip-button-compact {
    display: flex;
    align-items: center;
    gap: 12px;
}

.input-label-compact {
    font-size: 13px;
    color: #555;
    font-weight: 500;
    min-width: 40px;
}
</style>

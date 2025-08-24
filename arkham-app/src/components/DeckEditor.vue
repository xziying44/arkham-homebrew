<template>
    <div class="deck-builder">
        <!-- 中间牌库编辑区 -->
        <div class="deck-editor-panel" v-if="deck && !showTTSExport">
            <div class="panel-header">
                <h3>{{ deck.name }}</h3>
                <div class="editor-actions">
                    <!-- 导出为TTS物品按钮 -->
                    <n-button type="warning" @click="showTTSExportGuide" size="large" class="export-tts-button">
                        <template #icon>
                            <n-icon :component="DownloadOutline" />
                        </template>
                        {{ t('deckBuilder.actions.exportTTS') }}
                    </n-button>
                    <!-- 显著的保存按钮 -->
                    <n-button type="primary" @click="handleSave" :loading="saving" size="large" class="save-button">
                        <template #icon>
                            <n-icon :component="SaveOutline" />
                        </template>
                        {{ t('deckBuilder.actions.saveDeck') }}
                        <span class="save-shortcut">{{ t('deckBuilder.editor.shortcuts.save') }}</span>
                    </n-button>
                </div>
            </div>

            <!-- 正反面切换标签 -->
            <div class="deck-side-tabs">
                <n-tabs v-model:value="currentSide" type="segment" size="large" @update:value="switchSide">
                    <n-tab-pane name="front" :tab="t('deckBuilder.editor.sides.frontWithIcon')">
                        <template #tab>
                            <div class="side-tab">
                                <n-icon :component="LayersOutline" />
                                <span>{{ t('deckBuilder.editor.sides.front') }}</span>
                                <n-badge :value="getFrontCardCount()" :max="99" show-zero type="info" />
                            </div>
                        </template>
                    </n-tab-pane>
                    <n-tab-pane name="back" :tab="t('deckBuilder.editor.sides.backWithIcon')">
                        <template #tab>
                            <div class="side-tab">
                                <n-icon :component="SwapHorizontalOutline" />
                                <span>{{ t('deckBuilder.editor.sides.back') }}</span>
                                <n-badge :value="getBackCardCount()" :max="99" show-zero type="warning" />
                            </div>
                        </template>
                    </n-tab-pane>
                </n-tabs>
            </div>

            <div class="deck-grid-container">
                <n-scrollbar x-scrollable trigger="hover" style="height: 100%;">
                    <div class="deck-grid-wrapper">
                        <div class="deck-grid" :style="{
                            gridTemplateColumns: `repeat(${deck.width}, 1fr)`,
                            gridTemplateRows: `repeat(${deck.height}, 1fr)`,
                            minWidth: `${Math.max(deck.width * 150, 600)}px`
                        }">
                            <div v-for="index in (deck.width * deck.height)" :key="`${currentSide}-${index - 1}`"
                                class="grid-slot" :class="{
                                    'has-card': getCardAtIndex(index - 1, currentSide),
                                    'drag-over': dragOverIndex === (index - 1),
                                    'front-side': currentSide === 'front',
                                    'back-side': currentSide === 'back'
                                }" @click="selectGridSlot(index - 1)" @dragover.prevent="handleDragOver(index - 1)"
                                @dragleave="handleDragLeave" @drop="handleDrop(index - 1)">
                                <div v-if="getCardAtIndex(index - 1, currentSide)" class="card-in-slot"
                                    :class="{ 'front-card': currentSide === 'front', 'back-card': currentSide === 'back' }"
                                    draggable="true" @dragstart="handleDragStart(index - 1)" @dragend="handleDragEnd">
                                    <!-- 卡牌预览图 -->
                                    <div class="card-preview">
                                        <img v-if="getCardPreviewImage(index - 1, currentSide)"
                                            :src="getCardPreviewImage(index - 1, currentSide)"
                                            :alt="getCardName(getCardAtIndex(index - 1, currentSide)!)"
                                            class="card-preview-image" @error="handleImageError(index - 1, currentSide)" />
                                        <div v-else class="card-placeholder">
                                            <n-icon :component="ImageOutline" size="24" />
                                        </div>
                                    </div>
                                    <div class="card-name">{{ getCardName(getCardAtIndex(index - 1, currentSide)!) }}</div>
                                    <!-- 改进的删除按钮 -->
                                    <div class="remove-card-btn-wrapper">
                                        <n-button class="remove-card-btn"
                                            @click.stop="removeCardFromSlot(index - 1, currentSide)" text type="error"
                                            size="tiny" circle>
                                            <n-icon :component="CloseOutline" size="14" />
                                        </n-button>
                                    </div>
                                </div>
                                <div v-else class="empty-slot">
                                    <div class="slot-index">{{ index - 1 }}</div>
                                    <div class="add-hint">{{ t('deckBuilder.editor.content.clickToAdd') }}</div>
                                    <div class="side-indicator">{{ currentSide === 'front' ? t('deckBuilder.editor.content.sideIndicator.front') : t('deckBuilder.editor.content.sideIndicator.back') }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </n-scrollbar>
            </div>
        </div>

        <!-- TTS导出引导页面 -->
        <TTSExportGuide 
            v-if="deck && showTTSExport"
            :deck="deck"
            @back="showTTSExport = false"
            @update:deck="handleTTSInfoUpdate"
        />

        <!-- 内容选择抽屉 -->
        <n-drawer
            v-model:show="showCardSelector"
            :width="420"
            placement="right"
            :trap-focus="false"
            :block-scroll="false"
            :mask-closable="true"
        >
            <n-drawer-content :title="t('deckBuilder.editor.content.selectContent')" closable>
                <template #header>
                    <div class="drawer-header">
                        <h3>{{ t('deckBuilder.editor.content.selectContentFor', { side: currentSide === 'front' ? t('deckBuilder.editor.sides.front') : t('deckBuilder.editor.sides.back') }) }}</h3>
                    </div>
                </template>
                
                <!-- 选择类型的标签页 -->
                <div class="content-type-tabs">
                    <n-tabs v-model:value="contentType" type="line" @update:value="switchContentType"
                        class="full-height-tabs">
                        <n-tab-pane name="cards" :tab="t('deckBuilder.editor.tabs.cards')" class="full-height-pane">
                            <!-- 搜索框 -->
                            <div class="search-container">
                                <n-input v-model:value="searchKeyword" :placeholder="t('deckBuilder.editor.search.cards')" clearable>
                                    <template #prefix>
                                        <n-icon :component="SearchOutline" />
                                    </template>
                                </n-input>
                            </div>
                            <div class="scrollable-content">
                                <n-scrollbar style="height: 100%;">
                                    <div class="content-list-inner">
                                        <div v-for="card in filteredCards" :key="card.path" class="content-item"
                                            @click="assignContentToSlot('card', card.path)">
                                            <div class="content-icon">🎯</div>
                                            <div class="content-info">
                                                <div class="content-name">{{ card.name }}</div>
                                                <div class="content-path">{{ card.path }}</div>
                                            </div>
                                        </div>
                                        <n-empty v-if="filteredCards.length === 0" :description="t('deckBuilder.editor.empty.noCards')">
                                            <template #icon>
                                                <n-icon :component="SearchOutline" />
                                            </template>
                                        </n-empty>
                                    </div>
                                </n-scrollbar>
                            </div>
                        </n-tab-pane>
                        <n-tab-pane name="cardbacks" :tab="t('deckBuilder.editor.tabs.cardbacks')" class="full-height-pane">
                            <div class="scrollable-content">
                                <n-scrollbar style="height: 100%;">
                                    <div class="cardback-grid">
                                        <div class="cardback-item" @click="assignContentToSlot('cardback', 'player')">
                                            <div class="cardback-preview">
                                                <img src="../assets/cardbacks/player-back.jpg" :alt="t('deckBuilder.editor.cardbacks.player')"
                                                    class="cardback-image" @error="handleCardbackError" />
                                            </div>
                                            <div class="cardback-name">{{ t('deckBuilder.editor.cardbacks.player') }}</div>
                                        </div>
                                        <div class="cardback-item" @click="assignContentToSlot('cardback', 'encounter')">
                                            <div class="cardback-preview">
                                                <img src="../assets/cardbacks/encounter-back.jpg" :alt="t('deckBuilder.editor.cardbacks.encounter')"
                                                    class="cardback-image" @error="handleCardbackError" />
                                            </div>
                                            <div class="cardback-name">{{ t('deckBuilder.editor.cardbacks.encounter') }}</div>
                                        </div>
                                    </div>
                                </n-scrollbar>
                            </div>
                        </n-tab-pane>
                        <n-tab-pane name="images" :tab="t('deckBuilder.editor.tabs.images')" class="full-height-pane">
                            <!-- 图片搜索框 -->
                            <div class="search-container">
                                <n-input v-model:value="imageSearchKeyword" :placeholder="t('deckBuilder.editor.search.images')" clearable>
                                    <template #prefix>
                                        <n-icon :component="SearchOutline" />
                                    </template>
                                </n-input>
                            </div>
                            <div class="scrollable-content">
                                <n-scrollbar style="height: 100%;">
                                    <div class="content-list-inner">
                                        <div v-for="image in filteredImages" :key="image.path" class="content-item"
                                            @click="assignContentToSlot('image', image.path)">
                                            <div class="content-icon">🖼️</div>
                                            <div class="content-info">
                                                <div class="content-name">{{ image.name }}</div>
                                                <div class="content-path">{{ image.path }}</div>
                                            </div>
                                        </div>
                                        <n-empty v-if="filteredImages.length === 0" :description="t('deckBuilder.editor.empty.noImages')">
                                            <template #icon>
                                                <n-icon :component="ImageOutline" />
                                            </template>
                                        </n-empty>
                                    </div>
                                </n-scrollbar>
                            </div>
                        </n-tab-pane>
                    </n-tabs>
                </div>
            </n-drawer-content>
        </n-drawer>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
    SaveOutline,
    ImageOutline,
    CloseOutline,
    SearchOutline,
    LayersOutline,
    SwapHorizontalOutline,
    DownloadOutline
} from '@vicons/ionicons5';
import { WorkspaceService, CardService } from '@/api';
import TTSExportGuide from './TTSExportGuide.vue';

// 导入卡背图片
import playerBack from '@/assets/cardbacks/player-back.jpg';
import encounterBack from '@/assets/cardbacks/encounter-back.jpg';

interface DeckCard {
    index: number;
    type: 'card' | 'cardback' | 'image';
    path: string;
}

interface TTSInfo {
    frontImageUrl?: string;
    backImageUrl?: string;
    imageSource?: 'steam' | 'builtin';
    lastExportTime?: string;
    exportPath?: string;
}

interface DeckFile {
    name: string;
    path: string;
    width: number;
    height: number;
    frontCards: DeckCard[];
    backCards: DeckCard[];
    ttsInfo?: TTSInfo;
}

interface CardFile {
    name: string;
    path: string;
}

interface ImageFile {
    name: string;
    path: string;
}

// Props
interface Props {
    deck: DeckFile | null;
    availableCards: CardFile[];
    availableImages: ImageFile[];
    saving?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    saving: false
});

// Emits
interface Emits {
    (e: 'save'): void;
    (e: 'update:deck', deck: DeckFile): void;
    (e: 'load-images'): void;
}

const emit = defineEmits<Emits>();

const message = useMessage();
const { t } = useI18n();

// 状态管理
const currentSide = ref<'front' | 'back'>('front');
const showCardSelector = ref(false);
const selectedSlotIndex = ref<number | null>(null);
const contentType = ref<'cards' | 'cardbacks' | 'images'>('cards');
const searchKeyword = ref('');
const imageSearchKeyword = ref('');

// TTS导出相关状态
const showTTSExport = ref(false);

// 双面卡牌预览缓存
const frontSlotCardImages = ref(new Map<number, string>());
const backSlotCardImages = ref(new Map<number, string>());

// 拖拽相关
const dragOverIndex = ref<number | null>(null);
const dragSourceIndex = ref<number | null>(null);

// 固定卡背图片
const cardbackImages = {
    player: playerBack,
    encounter: encounterBack
};

// 过滤后的卡牌列表
const filteredCards = computed(() => {
    if (!searchKeyword.value.trim()) {
        return props.availableCards;
    }

    const keyword = searchKeyword.value.toLowerCase().trim();
    return props.availableCards.filter(card =>
        card.name.toLowerCase().includes(keyword) ||
        card.path.toLowerCase().includes(keyword)
    );
});

// 过滤后的图片列表
const filteredImages = computed(() => {
    if (!imageSearchKeyword.value.trim()) {
        return props.availableImages;
    }

    const keyword = imageSearchKeyword.value.toLowerCase().trim();
    return props.availableImages.filter(image =>
        image.name.toLowerCase().includes(keyword) ||
        image.path.toLowerCase().includes(keyword)
    );
});

// 获取正面卡牌数量
const getFrontCardCount = () => {
    return props.deck?.frontCards.length || 0;
};

// 获取背面卡牌数量
const getBackCardCount = () => {
    return props.deck?.backCards.length || 0;
};

// 切换编辑面
const switchSide = (side: 'front' | 'back') => {
    currentSide.value = side;
    showCardSelector.value = false;
};

// 切换内容类型
const switchContentType = (type: 'cards' | 'cardbacks' | 'images') => {
    contentType.value = type;
    if (type === 'images' && props.availableImages.length === 0) {
        emit('load-images');
    }
};

// 压缩图片
const compressImage = (base64: string, maxWidth = 150, quality = 0.7): Promise<string> => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d')!;

            const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
            canvas.width = img.width * ratio;
            canvas.height = img.height * ratio;

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            resolve(canvas.toDataURL('image/jpeg', quality));
        };
        img.src = base64;
    });
};

// 为单个网格位置生成内容预览图
const generateSlotContentPreview = async (index: number, item: DeckCard, side: 'front' | 'back') => {
    try {
        let imageBase64: string | null = null;

        if (item.type === 'card') {
            const content = await WorkspaceService.getFileContent(item.path);
            const cardData = JSON.parse(content);
            imageBase64 = await CardService.generateCard(cardData);
        } else if (item.type === 'cardback') {
            const cardbackPath = cardbackImages[item.path as 'player' | 'encounter'];
            if (cardbackPath) {
                imageBase64 = await loadImageAsBase64(cardbackPath);
            }
        } else if (item.type === 'image') {
            imageBase64 = await loadWorkspaceImageAsBase64(item.path);
        }

        if (imageBase64) {
            const compressedImage = await compressImage(imageBase64, 120, 0.7);
            if (side === 'front') {
                frontSlotCardImages.value.set(index, compressedImage);
            } else {
                backSlotCardImages.value.set(index, compressedImage);
            }
        }
    } catch (error) {
        console.error(`生成内容预览失败: ${item.path}`, error);
    }
};

// 加载图片为Base64
const loadImageAsBase64 = (src: string): Promise<string> => {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d')!;
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            resolve(canvas.toDataURL());
        };
        img.onerror = reject;
        img.src = src;
    });
};

// 加载工作空间图片为Base64
const loadWorkspaceImageAsBase64 = async (path: string): Promise<string> => {
    try {
        const content = await WorkspaceService.getImageContent(path);
        return `${content}`;
    } catch (error) {
        console.error('加载工作空间图片失败:', error);
        throw error;
    }
};

// 获取卡牌在网格中的预览图
const getCardPreviewImage = (index: number, side: 'front' | 'back'): string | null => {
    if (side === 'front') {
        return frontSlotCardImages.value.get(index) || null;
    } else {
        return backSlotCardImages.value.get(index) || null;
    }
};

// 处理图片加载错误
const handleImageError = (index: number, side: 'front' | 'back') => {
    if (side === 'front') {
        frontSlotCardImages.value.delete(index);
    } else {
        backSlotCardImages.value.delete(index);
    }
};

// 处理卡背图片加载错误
const handleCardbackError = (event: Event) => {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
};

// 获取指定位置和面的内容
const getCardAtIndex = (index: number, side: 'front' | 'back'): string | null => {
    if (!props.deck) return null;
    const cards = side === 'front' ? props.deck.frontCards : props.deck.backCards;
    const card = cards.find(c => c.index === index);
    return card ? card.path : null;
};

// 获取内容显示名称
const getCardName = (path: string): string => {
    if (!props.deck) return '';

    const cards = [...props.deck.frontCards, ...props.deck.backCards];
    const item = cards.find(c => c.path === path);

    if (!item) return path;

    if (item.type === 'cardback') {
        return item.path === 'player' ? t('deckBuilder.editor.cardbacks.player') : t('deckBuilder.editor.cardbacks.encounter');
    } else if (item.type === 'card') {
        const card = props.availableCards.find(c => c.path === path);
        return card ? card.name : path.split('/').pop()?.replace('.card', '') || '';
    } else if (item.type === 'image') {
        return path.split('/').pop() || '';
    }

    return path;
};

// 选择网格位置
const selectGridSlot = (index: number) => {
    selectedSlotIndex.value = index;
    showCardSelector.value = true;
};

// 分配内容到位置 - 修改版本
const assignContentToSlot = async (type: 'card' | 'cardback' | 'image', path: string) => {
    if (!props.deck || selectedSlotIndex.value === null) return;
    const updatedDeck = { ...props.deck };
    const index = selectedSlotIndex.value;
    const cards = currentSide.value === 'front' ? [...updatedDeck.frontCards] : [...updatedDeck.backCards];
    // 移除该位置现有的内容
    const filteredCards = cards.filter(c => c.index !== index);
    // 添加新内容
    const newItem: DeckCard = {
        index,
        type,
        path
    };
    filteredCards.push(newItem);
    // 更新对应面的内容
    if (currentSide.value === 'front') {
        updatedDeck.frontCards = filteredCards;
    } else {
        updatedDeck.backCards = filteredCards;
    }
    // 先生成预览图，再更新deck数据
    await generateSlotContentPreview(index, newItem, currentSide.value);

    emit('update:deck', updatedDeck);
    showCardSelector.value = false;
    selectedSlotIndex.value = null;
    
    const typeName = t(`deckBuilder.messages.types.${type}`);
    const sideName = currentSide.value === 'front' ? t('deckBuilder.editor.sides.front') : t('deckBuilder.editor.sides.back');
    message.success(t('deckBuilder.messages.cardAdded', { type: typeName, side: sideName }));
};

// 从位置移除内容 - 修改版本
const removeCardFromSlot = (index: number, side: 'front' | 'back') => {
    if (!props.deck) return;
    const updatedDeck = { ...props.deck };
    if (side === 'front') {
        updatedDeck.frontCards = [...updatedDeck.frontCards.filter(c => c.index !== index)];
        frontSlotCardImages.value.delete(index);
    } else {
        updatedDeck.backCards = [...updatedDeck.backCards.filter(c => c.index !== index)];
        backSlotCardImages.value.delete(index);
    }
    emit('update:deck', updatedDeck);
    message.info(t('deckBuilder.messages.contentRemoved'));
};

// 拖拽开始
const handleDragStart = (index: number) => {
    dragSourceIndex.value = index;
};

// 拖拽结束
const handleDragEnd = () => {
    dragSourceIndex.value = null;
    dragOverIndex.value = null;
};

// 拖拽悬停
const handleDragOver = (index: number) => {
    dragOverIndex.value = index;
};

// 拖拽离开
const handleDragLeave = () => {
    dragOverIndex.value = null;
};

// 拖拽放置 - 修改版本
const handleDrop = (targetIndex: number) => {
    if (!props.deck || dragSourceIndex.value === null) return;
    const sourceIndex = dragSourceIndex.value;
    if (sourceIndex === targetIndex) return;
    const updatedDeck = { ...props.deck };
    const cards = currentSide.value === 'front' ? [...updatedDeck.frontCards] : [...updatedDeck.backCards];
    const sourceCard = cards.find(c => c.index === sourceIndex);
    const targetCard = cards.find(c => c.index === targetIndex);
    // 交换位置
    if (sourceCard && targetCard) {
        sourceCard.index = targetIndex;
        targetCard.index = sourceIndex;
        // 交换预览图
        const images = currentSide.value === 'front' ? frontSlotCardImages.value : backSlotCardImages.value;
        const sourceImage = images.get(sourceIndex);
        const targetImage = images.get(targetIndex);
        if (sourceImage && targetImage) {
            images.set(targetIndex, sourceImage);
            images.set(sourceIndex, targetImage);
        }
    } else if (sourceCard) {
        sourceCard.index = targetIndex;
        // 移动预览图
        const images = currentSide.value === 'front' ? frontSlotCardImages.value : backSlotCardImages.value;
        const sourceImage = images.get(sourceIndex);
        if (sourceImage) {
            images.delete(sourceIndex);
            images.set(targetIndex, sourceImage);
        }
    }
    // 更新对应面的内容
    if (currentSide.value === 'front') {
        updatedDeck.frontCards = cards;
    } else {
        updatedDeck.backCards = cards;
    }
    emit('update:deck', updatedDeck);
    dragSourceIndex.value = null;
    dragOverIndex.value = null;
    message.info(t('deckBuilder.messages.positionSwapped'));
};

// 保存处理
const handleSave = () => {
    emit('save');
};

// TTS导出相关方法
const showTTSExportGuide = () => {
    showTTSExport.value = true;
    showCardSelector.value = false;
};

const handleTTSInfoUpdate = (updatedDeck: DeckFile) => {
    emit('update:deck', updatedDeck);
};

// 监听deck变化，重新生成预览图
watch(() => props.deck, (newDeck, oldDeck) => {
    // 只在真正切换牌库时才完全重新加载
    if (!oldDeck || !newDeck || newDeck.path !== oldDeck.path) {
        if (newDeck) {
            frontSlotCardImages.value.clear();
            backSlotCardImages.value.clear();
            // 为牌库中的正面内容生成预览图
            for (const item of newDeck.frontCards) {
                generateSlotContentPreview(item.index, item, 'front');
            }
            // 为牌库中的背面内容生成预览图
            for (const item of newDeck.backCards) {
                generateSlotContentPreview(item.index, item, 'back');
            }
        }
    }
    // 如果是同一个牌库的数据更新，不需要重新生成所有预览图
}, { immediate: true });
</script>

<style scoped>
.deck-builder {
    display: flex;
    flex: 1;
    min-height: 0;
    width: 100%;
    overflow: hidden;
}

.deck-editor-panel {
    flex: 1;
    width: 100%;
    max-width: 100%;
    background: white;
    margin: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
}

.panel-header {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e9ecef;
    background: #f8f9fa;
}

.panel-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.1rem;
}

.editor-actions {
    display: flex;
    gap: 0;
    align-items: center;
}

/* TTS导出按钮样式 */
.export-tts-button {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
    transition: all 0.3s ease;
    font-weight: 600;
    margin-right: 0.75rem;
}

.export-tts-button:hover {
    background: linear-gradient(135deg, #e55a2b 0%, #e8811a 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
}

/* 正反面切换标签 */
.deck-side-tabs {
    flex-shrink: 0;
    border-bottom: 1px solid #e9ecef;
    background: #fafafa;
    padding: 1rem 1.5rem 0;
}

.side-tab {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* 显著的保存按钮样式 */
.save-button {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    transition: all 0.3s ease;
    font-weight: 600;
}

.save-button:hover {
    background: linear-gradient(135deg, #218838 0%, #17a2b8 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

.save-shortcut {
    font-size: 0.8rem;
    opacity: 0.8;
    margin-left: 0.5rem;
}

/* 改进的网格容器布局 - 支持大网格的横向滚动 */
.deck-grid-container {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    padding: 2rem;
}

.deck-grid-wrapper {
    min-height: 100%;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    padding: 1rem;
    width: 100%;
}

.deck-grid {
    display: grid;
    gap: 1.2rem;
    justify-content: flex-start;
    align-content: flex-start;
    width: fit-content;
    min-width: fit-content;
}

/* 统一网格槽尺寸 */
.grid-slot {
    width: 140px;
    height: 200px;
    border: 2px dashed #ddd;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    background: #fafafa;
    box-sizing: border-box;
}

.grid-slot:hover {
    border-color: #667eea;
    background: #f0f4ff;
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
}

.grid-slot.has-card {
    border: 2px solid #667eea;
    background: white;
}

.grid-slot.front-side.has-card {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.grid-slot.back-side.has-card {
    border-color: #ff6b6b;
    box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2);
}

.grid-slot.drag-over {
    border-color: #28a745;
    background: #e8f5e8;
    transform: scale(1.02);
}

/* 统一卡片容器尺寸 */
.card-in-slot {
    width: 100%;
    height: 100%;
    background: white;
    border-radius: 10px;
    padding: 8px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15);
    position: relative;
    cursor: grab;
    box-sizing: border-box;
}

.card-in-slot.front-card {
    border-left: 4px solid #667eea;
}

.card-in-slot.back-card {
    border-left: 4px solid #ff6b6b;
}

.card-in-slot:active {
    cursor: grabbing;
}

/* 统一卡片预览区域 */
.card-preview {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 8px;
    background: #f8f9fa;
    position: relative;
    min-height: 0;
}

/* 统一图片显示方式 */
.card-preview-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    border-radius: 6px;
    display: block;
}

.card-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6c757d;
    font-size: 2rem;
    width: 100%;
    height: 100%;
}

/* 统一卡片名称显示 */
.card-name {
    font-weight: 500;
    font-size: 0.75rem;
    color: #2c3e50;
    text-align: center;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 4px;
    height: 1.2em;
    flex-shrink: 0;
}

/* 删除按钮样式 */
.remove-card-btn-wrapper {
    position: absolute;
    top: -6px;
    right: -6px;
    z-index: 100;
}

.remove-card-btn {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    min-height: 28px !important;
    background: #dc3545 !important;
    border: 2px solid white !important;
    border-radius: 50% !important;
    box-shadow: 0 3px 10px rgba(220, 53, 69, 0.4) !important;
    opacity: 0;
    transition: all 0.2s ease;
    color: white !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
}

.remove-card-btn:hover {
    background: #c82333 !important;
    transform: scale(1.15) !important;
    box-shadow: 0 5px 15px rgba(220, 53, 69, 0.6) !important;
    color: white !important;
}

.remove-card-btn .n-icon {
    color: white !important;
    font-size: 14px !important;
}

.card-in-slot:hover .remove-card-btn,
.grid-slot:hover .remove-card-btn {
    opacity: 1;
}

/* 空槽样式 */
.empty-slot {
    text-align: center;
    color: #6c757d;
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.slot-index {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #495057;
}

.add-hint {
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
    opacity: 0.7;
}

.side-indicator {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    background: #e9ecef;
    color: #6c757d;
    margin-top: auto;
}

/* 抽屉样式 */
.drawer-header {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.drawer-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.1rem;
}

/* 内容类型标签页 */
.content-type-tabs {
    height: 100%;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
}

/* 修复Naive UI tabs组件的高度问题 */
.full-height-tabs {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.full-height-tabs :deep(.n-tabs-nav) {
    flex-shrink: 0;
}

.full-height-tabs :deep(.n-tabs-content) {
    flex: 1;
    min-height: 0;
    overflow: hidden;
}

.full-height-tabs :deep(.n-tab-pane) {
    height: 100%;
    display: flex;
    flex-direction: column;
    min-height: 0;
}

/* 新增的可滚动内容容器 */
.scrollable-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
}

.content-list-inner {
    padding: 0.5rem;
}

.search-container {
    flex-shrink: 0;
    padding: 1rem;
    border-bottom: 1px solid #e9ecef;
}

.content-item {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 0.5rem;
    border: 1px solid transparent;
}

.content-item:hover {
    background: #f8f9fa;
    border-color: #667eea;
}

.content-icon {
    font-size: 1.25rem;
    margin-right: 0.75rem;
    color: #667eea;
}

.content-info {
    flex: 1;
    min-width: 0;
}

.content-name {
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 0.25rem;
}

.content-path {
    font-size: 0.75rem;
    color: #6c757d;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 卡背网格样式 */
.cardback-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    padding: 1rem;
}

.cardback-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    border: 2px dashed #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.cardback-item:hover {
    border-color: #667eea;
    background: #f0f4ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.cardback-preview {
    width: 80px;
    height: 110px;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 0.5rem;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cardback-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.cardback-name {
    font-size: 0.8rem;
    font-weight: 500;
    color: #2c3e50;
    text-align: center;
}

/* 响应式调整 */
@media (max-width: 1400px) {
    .grid-slot {
        width: 120px;
        height: 170px;
    }

    .deck-grid {
        gap: 1rem;
    }
}

@media (max-width: 1200px) {
    .grid-slot {
        width: 110px;
        height: 150px;
    }

    .deck-grid {
        gap: 0.8rem;
    }

    .card-name {
        font-size: 0.7rem;
    }

    .remove-card-btn {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        min-height: 24px !important;
    }

    .remove-card-btn .n-icon {
        font-size: 12px !important;
    }
}
</style>

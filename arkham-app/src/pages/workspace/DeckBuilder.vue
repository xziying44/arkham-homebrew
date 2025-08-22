<template>
  <div class="deck-builder-container">
    <div class="deck-builder-header">
      <h2>🃏 牌库制作</h2>
      <div class="header-actions">
        <n-button type="primary" @click="showCreateDeckDialog = true" size="large">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          新建牌库
        </n-button>
      </div>
    </div>

    <div class="deck-builder-content">
      <!-- 左侧牌库列表 -->
      <div class="deck-list-panel">
        <div class="panel-header">
          <h3>我的牌库</h3>
          <n-button text @click="loadDecks" :loading="loading" title="刷新">
            <n-icon :component="RefreshOutline" />
          </n-button>
        </div>
        <n-scrollbar class="deck-list">
          <div v-for="deck in deckList" :key="deck.path" class="deck-item"
            :class="{ 'active': selectedDeck?.path === deck.path }" @click="selectDeck(deck)">
            <div class="deck-icon">🎴</div>
            <div class="deck-info">
              <div class="deck-name">{{ deck.name }}</div>
              <div class="deck-meta">{{ deck.width }}×{{ deck.height }} 网格</div>
            </div>
            <n-button text type="error" @click.stop="showDeleteConfirm(deck)" title="删除牌库" size="small">
              <n-icon :component="TrashOutline" />
            </n-button>
          </div>
          <n-empty v-if="deckList.length === 0 && !loading" description="暂无牌库">
            <template #icon>
              <n-icon :component="FolderOpenOutline" />
            </template>
            <template #extra>
              <n-text depth="3">点击上方按钮创建新牌库</n-text>
            </template>
          </n-empty>
        </n-scrollbar>
      </div>

      <!-- 中间牌库编辑区 -->
      <div class="deck-editor-panel" v-if="selectedDeck">
        <div class="panel-header">
          <h3>{{ selectedDeck.name }}</h3>
          <div class="editor-actions">
            <!-- 显著的保存按钮 -->
            <n-button type="primary" @click="saveDeck" :loading="saving" size="large" class="save-button">
              <template #icon>
                <n-icon :component="SaveOutline" />
              </template>
              保存牌库
              <span class="save-shortcut">(Ctrl+S)</span>
            </n-button>
          </div>
        </div>

        <!-- 正反面切换标签 -->
        <div class="deck-side-tabs">
          <n-tabs v-model:value="currentSide" type="segment" size="large" @update:value="switchSide">
            <n-tab-pane name="front" tab="正面 🎯">
              <template #tab>
                <div class="side-tab">
                  <n-icon :component="LayersOutline" />
                  <span>正面</span>
                  <n-badge :value="getFrontCardCount()" :max="99" show-zero type="info" />
                </div>
              </template>
            </n-tab-pane>
            <n-tab-pane name="back" tab="背面 🎲">
              <template #tab>
                <div class="side-tab">
                  <n-icon :component="SwapHorizontalOutline" />
                  <span>背面</span>
                  <n-badge :value="getBackCardCount()" :max="99" show-zero type="warning" />
                </div>
              </template>
            </n-tab-pane>
          </n-tabs>
        </div>

        <n-scrollbar class="deck-grid-container">
          <div class="deck-grid-wrapper">
            <div class="deck-grid" :style="{
              gridTemplateColumns: `repeat(${selectedDeck.width}, 1fr)`,
              gridTemplateRows: `repeat(${selectedDeck.height}, 1fr)`
            }">
              <div v-for="index in (selectedDeck.width * selectedDeck.height)" :key="`${currentSide}-${index - 1}`"
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
                      :alt="getCardName(getCardAtIndex(index - 1, currentSide)!)" class="card-preview-image"
                      @error="handleImageError(index - 1, currentSide)" />
                    <div v-else class="card-placeholder">
                      <n-icon :component="ImageOutline" size="24" />
                    </div>
                  </div>
                  <div class="card-name">{{ getCardName(getCardAtIndex(index - 1, currentSide)!) }}</div>
                  <!-- 改进的删除按钮 -->
                  <div class="remove-card-btn-wrapper">
                    <n-button class="remove-card-btn" @click.stop="removeCardFromSlot(index - 1, currentSide)" text
                      type="error" size="tiny" circle>
                      <n-icon :component="CloseOutline" size="14" />
                    </n-button>
                  </div>
                </div>
                <div v-else class="empty-slot">
                  <div class="slot-index">{{ index - 1 }}</div>
                  <div class="add-hint">点击添加内容</div>
                  <div class="side-indicator">{{ currentSide === 'front' ? '正面' : '背面' }}</div>
                </div>
              </div>
            </div>
          </div>
        </n-scrollbar>
      </div>

      <!-- 右侧内容选择面板 -->
      <div class="card-select-panel" v-if="showCardSelector">
        <div class="panel-header">
          <h3>选择内容 - {{ currentSide === 'front' ? '正面' : '背面' }}</h3>
          <n-button text @click="showCardSelector = false">
            <n-icon :component="CloseOutline" />
          </n-button>
        </div>
        <!-- 选择类型的标签页 -->
        <div class="content-type-tabs">
          <n-tabs v-model:value="contentType" type="line" @update:value="switchContentType" class="full-height-tabs">
            <n-tab-pane name="cards" tab="🎯 卡牌" class="full-height-pane">
              <!-- 搜索框 -->
              <div class="search-container">
                <n-input v-model:value="searchKeyword" placeholder="搜索卡牌名称..." clearable>
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
                    <n-empty v-if="filteredCards.length === 0" description="没有找到匹配的卡牌">
                      <template #icon>
                        <n-icon :component="SearchOutline" />
                      </template>
                    </n-empty>
                  </div>
                </n-scrollbar>
              </div>
            </n-tab-pane>
            <n-tab-pane name="cardbacks" tab="🎴 卡背" class="full-height-pane">
              <div class="scrollable-content">
                <n-scrollbar style="height: 100%;">
                  <div class="cardback-grid">
                    <div class="cardback-item" @click="assignContentToSlot('cardback', 'player')">
                      <div class="cardback-preview">
                        <img src="../../assets/cardbacks/player-back.jpg" alt="玩家卡背" class="cardback-image"
                          @error="handleCardbackError" />
                      </div>
                      <div class="cardback-name">玩家卡背</div>
                    </div>
                    <div class="cardback-item" @click="assignContentToSlot('cardback', 'encounter')">
                      <div class="cardback-preview">
                        <img src="../../assets/cardbacks/encounter-back.jpg" alt="遭遇卡背" class="cardback-image"
                          @error="handleCardbackError" />
                      </div>
                      <div class="cardback-name">遭遇卡背</div>
                    </div>
                  </div>
                </n-scrollbar>
              </div>
            </n-tab-pane>
            <n-tab-pane name="images" tab="🖼️ 图片" class="full-height-pane">
              <!-- 图片搜索框 -->
              <div class="search-container">
                <n-input v-model:value="imageSearchKeyword" placeholder="搜索图片文件..." clearable>
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
                    <n-empty v-if="filteredImages.length === 0" description="没有找到匹配的图片">
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
      </div>
    </div>

    <!-- 新建牌库对话框 -->
    <n-modal v-model:show="showCreateDeckDialog" preset="dialog" title="新建牌库">
      <n-form ref="createFormRef" :model="newDeckForm" :rules="createRules">
        <n-form-item path="name" label="牌库名称">
          <n-input v-model:value="newDeckForm.name" placeholder="请输入牌库名称" @keydown.enter="createDeck" clearable />
        </n-form-item>
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item path="width" label="宽度 (1-10)">
              <n-input-number v-model:value="newDeckForm.width" :min="1" :max="10" placeholder="宽度"
                :show-button="false" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item path="height" label="高度 (1-7)">
              <n-input-number v-model:value="newDeckForm.height" :min="1" :max="7" placeholder="高度"
                :show-button="false" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="closeCreateDialog">取消</n-button>
          <n-button type="primary" @click="createDeck" :loading="creating">
            创建
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal v-model:show="showDeleteDialog" preset="dialog" title="删除确认">
      <n-alert type="warning" title="警告">
        <template #icon>
          <n-icon :component="WarningOutline" />
        </template>
        此操作不可恢复，确定要删除牌库"{{ deckToDelete?.name }}"吗？
      </n-alert>
      <template #action>
        <n-space>
          <n-button @click="showDeleteDialog = false">取消</n-button>
          <n-button type="error" @click="confirmDeleteDeck" :loading="deleting">
            删除
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue';
import {
  useMessage,
  type FormInst,
  type FormRules
} from 'naive-ui';
import {
  AddOutline,
  RefreshOutline,
  TrashOutline,
  FolderOpenOutline,
  SaveOutline,
  ImageOutline,
  CloseOutline,
  SearchOutline,
  WarningOutline,
  LayersOutline,
  SwapHorizontalOutline
} from '@vicons/ionicons5';
import { WorkspaceService, CardService } from '@/api';

interface DeckCard {
  index: number;
  type: 'card' | 'cardback' | 'image'; // 添加类型字段
  path: string; // 对于卡背，这里存储类型（player/encounter）
}

interface DeckData {
  name: string;
  width: number;
  height: number;
  frontCards: DeckCard[]; // 正面卡牌
  backCards: DeckCard[];  // 背面卡牌
}

interface DeckFile {
  name: string;
  path: string;
  width: number;
  height: number;
  frontCards: DeckCard[];
  backCards: DeckCard[];
}

interface CardFile {
  name: string;
  path: string;
}

interface ImageFile {
  name: string;
  path: string;
}

const message = useMessage();

// 状态管理
const loading = ref(false);
const saving = ref(false);
const creating = ref(false);
const deleting = ref(false);

// 牌库相关
const deckList = ref<DeckFile[]>([]);
const selectedDeck = ref<DeckFile | null>(null);
const currentSide = ref<'front' | 'back'>('front'); // 当前编辑的面

// 内容选择相关
const availableCards = ref<CardFile[]>([]);
const availableImages = ref<ImageFile[]>([]);
const showCardSelector = ref(false);
const selectedSlotIndex = ref<number | null>(null);
const contentType = ref<'cards' | 'cardbacks' | 'images'>('cards'); // 当前选择的内容类型
const searchKeyword = ref('');
const imageSearchKeyword = ref('');

// 双面卡牌预览缓存
const frontSlotCardImages = ref(new Map<number, string>());
const backSlotCardImages = ref(new Map<number, string>());

// 拖拽相关
const dragOverIndex = ref<number | null>(null);
const dragSourceIndex = ref<number | null>(null);

// 新建牌库表单
const showCreateDeckDialog = ref(false);
const createFormRef = ref<FormInst | null>(null);
const newDeckForm = ref({
  name: '',
  width: 5 as number | null,
  height: 3 as number | null
});

// 删除确认对话框
const showDeleteDialog = ref(false);
const deckToDelete = ref<DeckFile | null>(null);

// 固定卡背图片（你需要将这些图片放在 public/cardbacks/ 目录下）
// 如果图片在 src/assets 目录下
import playerBack from '@/assets/cardbacks/player-back.jpg'
import encounterBack from '@/assets/cardbacks/encounter-back.jpg'
const cardbackImages = {
  player: playerBack,
  encounter: encounterBack
}

// 表单验证规则
const createRules: FormRules = {
  name: [
    { required: true, message: '请输入牌库名称', trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: '牌库名称长度在1-50个字符', trigger: ['input', 'blur'] },
    {
      pattern: /^[^\\/:*?"<>|]+$/,
      message: '牌库名称不能包含特殊字符 \\/:*?"<>|',
      trigger: ['input', 'blur']
    }
  ],
  width: [
    {
      required: true,
      message: '请输入宽度',
      trigger: ['blur', 'change'],
      validator: (rule: any, value: any) => {
        if (value === null || value === undefined || value === '') {
          return new Error('请输入宽度');
        }
        if (typeof value !== 'number' || value < 1 || value > 10) {
          return new Error('宽度必须在1-10之间');
        }
        return true;
      }
    }
  ],
  height: [
    {
      required: true,
      message: '请输入高度',
      trigger: ['blur', 'change'],
      validator: (rule: any, value: any) => {
        if (value === null || value === undefined || value === '') {
          return new Error('请输入高度');
        }
        if (typeof value !== 'number' || value < 1 || value > 7) {
          return new Error('高度必须在1-7之间');
        }
        return true;
      }
    }
  ]
};

// 过滤后的卡牌列表
const filteredCards = computed(() => {
  if (!searchKeyword.value.trim()) {
    return availableCards.value;
  }

  const keyword = searchKeyword.value.toLowerCase().trim();
  return availableCards.value.filter(card =>
    card.name.toLowerCase().includes(keyword) ||
    card.path.toLowerCase().includes(keyword)
  );
});

// 过滤后的图片列表
const filteredImages = computed(() => {
  if (!imageSearchKeyword.value.trim()) {
    return availableImages.value;
  }

  const keyword = imageSearchKeyword.value.toLowerCase().trim();
  return availableImages.value.filter(image =>
    image.name.toLowerCase().includes(keyword) ||
    image.path.toLowerCase().includes(keyword)
  );
});

// 获取正面卡牌数量
const getFrontCardCount = () => {
  return selectedDeck.value?.frontCards.length || 0;
};

// 获取背面卡牌数量
const getBackCardCount = () => {
  return selectedDeck.value?.backCards.length || 0;
};

// 切换编辑面
const switchSide = (side: 'front' | 'back') => {
  currentSide.value = side;
  showCardSelector.value = false;
};

// 切换内容类型
const switchContentType = (type: 'cards' | 'cardbacks' | 'images') => {
  contentType.value = type;
  if (type === 'images' && availableImages.value.length === 0) {
    loadAvailableImages();
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
      // 加载固定的卡背图片
      const cardbackPath = cardbackImages[item.path as 'player' | 'encounter'];
      if (cardbackPath) {
        // 将路径转换为base64
        imageBase64 = await loadImageAsBase64(cardbackPath);
      }
    } else if (item.type === 'image') {
      // 加载工作目录中的图片文件
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
  // 这里你需要根据你的API实现来获取工作空间中的图片文件
  // 假设WorkspaceService有一个方法可以获取图片的base64
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
  // 可以在这里添加默认图片或占位符
};

// 确保DeckBuilder目录存在
const ensureDeckBuilderDirectory = async () => {
  try {
    await WorkspaceService.createDirectory('DeckBuilder');
  } catch (error) {
    console.log('DeckBuilder目录已存在或创建失败:', error);
  }
};

// 加载所有牌库
const loadDecks = async () => {
  loading.value = true;
  try {
    await ensureDeckBuilderDirectory();

    const response = await WorkspaceService.getFileTree();
    const deckBuilderNode = findDeckBuilderNode(response.fileTree);

    if (deckBuilderNode && deckBuilderNode.children) {
      const deckFiles = deckBuilderNode.children.filter(
        (file: any) => file.label.endsWith('.deck')
      );

      const decks: DeckFile[] = [];
      for (const file of deckFiles) {
        try {
          const content = await WorkspaceService.getFileContent(file.path);
          const deckData: DeckData = JSON.parse(content);

          // 兼容旧格式和新格式
          let frontCards = deckData.frontCards || [];
          let backCards = deckData.backCards || [];

          // 如果是旧格式，转换为新格式
          if ((deckData as any).cards && !deckData.frontCards) {
            frontCards = (deckData as any).cards.map((card: any) => ({
              index: card.index,
              type: 'card',
              path: card.cardPath || card.path
            }));
          }

          decks.push({
            name: deckData.name,
            path: file.path,
            width: deckData.width,
            height: deckData.height,
            frontCards: frontCards,
            backCards: backCards
          });
        } catch (error) {
          console.error(`加载牌库文件失败: ${file.path}`, error);
        }
      }

      deckList.value = decks;
    } else {
      deckList.value = [];
    }

    await loadAvailableCards();
    message.success('牌库列表已刷新');
  } catch (error) {
    console.error('加载牌库列表失败:', error);
    message.error('加载牌库列表失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 查找DeckBuilder节点
const findDeckBuilderNode = (node: any): any => {
  if (node.label === 'DeckBuilder') return node;
  if (node.children) {
    for (const child of node.children) {
      const found = findDeckBuilderNode(child);
      if (found) return found;
    }
  }
  return null;
};

// 加载可用卡牌
const loadAvailableCards = async () => {
  try {
    const response = await WorkspaceService.getFileTree();
    const cards: CardFile[] = [];

    const collectCards = (node: any) => {
      if (node.type === 'card') {
        cards.push({
          name: node.label.replace('.card', ''),
          path: node.path
        });
      }
      if (node.children) {
        node.children.forEach(collectCards);
      }
    };

    collectCards(response.fileTree);
    availableCards.value = cards;
  } catch (error) {
    console.error('加载可用卡牌失败:', error);
    message.error('加载可用卡牌失败');
  }
};

// 加载可用图片
const loadAvailableImages = async () => {
  try {
    const response = await WorkspaceService.getFileTree();
    const images: ImageFile[] = [];

    const collectImages = (node: any) => {
      // 修改：检查图片类型或通过文件扩展名判断
      const isImageByType = node.type === 'image';
      const isImageByExtension = node.type === 'file' && /\.(png|jpg|jpeg|gif|bmp|webp|svg)$/i.test(node.label);

      if (isImageByType || isImageByExtension) {
        images.push({
          name: node.label,
          path: node.path
        });
      }

      if (node.children) {
        node.children.forEach(collectImages);
      }
    };

    collectImages(response.fileTree);
    availableImages.value = images;
    console.log('加载到的图片文件:', images); // 添加调试日志
  } catch (error) {
    console.error('加载可用图片失败:', error);
    message.error('加载可用图片失败');
  }
};


// 选择牌库
const selectDeck = async (deck: DeckFile) => {
  selectedDeck.value = deck;
  showCardSelector.value = false;
  currentSide.value = 'front';

  // 清空之前的预览图
  frontSlotCardImages.value.clear();
  backSlotCardImages.value.clear();

  // 为牌库中的正面内容生成预览图
  for (const item of deck.frontCards) {
    generateSlotContentPreview(item.index, item, 'front');
  }

  // 为牌库中的背面内容生成预览图
  for (const item of deck.backCards) {
    generateSlotContentPreview(item.index, item, 'back');
  }
};

// 创建新牌库
const createDeck = async () => {
  if (!createFormRef.value) return;

  try {
    await createFormRef.value.validate();
    creating.value = true;

    await ensureDeckBuilderDirectory();

    const deckData: DeckData = {
      name: newDeckForm.value.name,
      width: newDeckForm.value.width!,
      height: newDeckForm.value.height!,
      frontCards: [],
      backCards: []
    };

    const fileName = `${newDeckForm.value.name}.deck`;
    const filePath = `DeckBuilder/${fileName}`;

    await WorkspaceService.createFile(fileName, JSON.stringify(deckData, null, 2), 'DeckBuilder');

    deckList.value.push({
      name: deckData.name,
      path: filePath,
      width: deckData.width,
      height: deckData.height,
      frontCards: deckData.frontCards,
      backCards: deckData.backCards
    });

    closeCreateDialog();
    message.success('牌库创建成功');
  } catch (error) {
    if (error && typeof error === 'object' && 'errors' in error) {
      return;
    }
    console.error('创建牌库失败:', error);
    message.error('创建牌库失败，请重试');
  } finally {
    creating.value = false;
  }
};

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreateDeckDialog.value = false;
  newDeckForm.value = {
    name: '',
    width: 5,
    height: 3
  };
  createFormRef.value?.restoreValidation();
};

// 保存牌库
const saveDeck = async () => {
  if (!selectedDeck.value) return;

  saving.value = true;
  try {
    const deckData: DeckData = {
      name: selectedDeck.value.name,
      width: selectedDeck.value.width,
      height: selectedDeck.value.height,
      frontCards: selectedDeck.value.frontCards,
      backCards: selectedDeck.value.backCards
    };

    await WorkspaceService.saveFileContent(
      selectedDeck.value.path,
      JSON.stringify(deckData, null, 2)
    );

    message.success('牌库保存成功');
  } catch (error) {
    console.error('保存牌库失败:', error);
    message.error('保存牌库失败，请重试');
  } finally {
    saving.value = false;
  }
};

// 显示删除确认对话框
const showDeleteConfirm = (deck: DeckFile) => {
  deckToDelete.value = deck;
  showDeleteDialog.value = true;
};

// 确认删除牌库
const confirmDeleteDeck = async () => {
  if (!deckToDelete.value) return;

  deleting.value = true;
  try {
    await WorkspaceService.deleteItem(deckToDelete.value.path);

    const index = deckList.value.findIndex(d => d.path === deckToDelete.value!.path);
    if (index > -1) {
      deckList.value.splice(index, 1);
    }

    if (selectedDeck.value?.path === deckToDelete.value.path) {
      selectedDeck.value = null;
      frontSlotCardImages.value.clear();
      backSlotCardImages.value.clear();
    }

    showDeleteDialog.value = false;
    deckToDelete.value = null;
    message.success('牌库删除成功');
  } catch (error) {
    console.error('删除牌库失败:', error);
    message.error('删除牌库失败，请重试');
  } finally {
    deleting.value = false;
  }
};

// 获取指定位置和面的内容
const getCardAtIndex = (index: number, side: 'front' | 'back'): string | null => {
  if (!selectedDeck.value) return null;
  const cards = side === 'front' ? selectedDeck.value.frontCards : selectedDeck.value.backCards;
  const card = cards.find(c => c.index === index);
  return card ? card.path : null;
};

// 获取内容显示名称
const getCardName = (path: string): string => {
  if (!selectedDeck.value) return '';

  const cards = [...selectedDeck.value.frontCards, ...selectedDeck.value.backCards];
  const item = cards.find(c => c.path === path);

  if (!item) return path;

  if (item.type === 'cardback') {
    return item.path === 'player' ? '玩家卡背' : '遭遇卡背';
  } else if (item.type === 'card') {
    const card = availableCards.value.find(c => c.path === path);
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

// 分配内容到位置
const assignContentToSlot = async (type: 'card' | 'cardback' | 'image', path: string) => {
  if (!selectedDeck.value || selectedSlotIndex.value === null) return;

  const index = selectedSlotIndex.value;
  const cards = currentSide.value === 'front' ? selectedDeck.value.frontCards : selectedDeck.value.backCards;

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
    selectedDeck.value.frontCards = filteredCards;
  } else {
    selectedDeck.value.backCards = filteredCards;
  }

  // 生成预览图
  generateSlotContentPreview(index, newItem, currentSide.value);

  showCardSelector.value = false;
  selectedSlotIndex.value = null;

  let typeName = '';
  if (type === 'card') typeName = '卡牌';
  else if (type === 'cardback') typeName = '卡背';
  else if (type === 'image') typeName = '图片';

  message.success(`${typeName}已添加到${currentSide.value === 'front' ? '正面' : '背面'}`);
};

// 从位置移除内容
const removeCardFromSlot = (index: number, side: 'front' | 'back') => {
  if (!selectedDeck.value) return;

  if (side === 'front') {
    selectedDeck.value.frontCards = selectedDeck.value.frontCards.filter(c => c.index !== index);
    frontSlotCardImages.value.delete(index);
  } else {
    selectedDeck.value.backCards = selectedDeck.value.backCards.filter(c => c.index !== index);
    backSlotCardImages.value.delete(index);
  }

  message.info('内容已移除');
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

// 拖拽放置
const handleDrop = (targetIndex: number) => {
  if (!selectedDeck.value || dragSourceIndex.value === null) return;

  const sourceIndex = dragSourceIndex.value;

  if (sourceIndex === targetIndex) return;

  const cards = currentSide.value === 'front' ? selectedDeck.value.frontCards : selectedDeck.value.backCards;
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

  dragSourceIndex.value = null;
  dragOverIndex.value = null;
  message.info('内容位置已调换');
};

// 键盘快捷键处理
const handleKeydown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault();
    if (selectedDeck.value && !saving.value) {
      saveDeck();
    }
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadDecks();
  document.addEventListener('keydown', handleKeydown);
});

// 组件卸载时清理
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.deck-builder-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.deck-builder-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.deck-builder-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.deck-builder-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.deck-list-panel {
  width: 280px;
  background: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.deck-editor-panel {
  flex: 1;
  background: white;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.card-select-panel {
  width: 380px;
  background: white;
  border-left: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
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
  gap: 0.5rem;
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

/* 内容类型标签页 */
.content-type-tabs {
  flex: 1;
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

.deck-list {
  flex: 1;
  min-height: 0;
  padding: 0.5rem;
}

.deck-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.25rem;
  position: relative;
}

.deck-item:hover {
  background: #f8f9fa;
}

.deck-item.active {
  background: linear-gradient(135deg, #e3f2fd 0%, #e8f5e8 100%);
  border-left: 3px solid #667eea;
}

.deck-icon {
  font-size: 1.25rem;
  margin-right: 0.75rem;
}

.deck-info {
  flex: 1;
}

.deck-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.deck-meta {
  font-size: 0.8rem;
  color: #6c757d;
}

/* 改进的网格容器布局 */
.deck-grid-container {
  flex: 1;
  min-height: 0;
  padding: 2rem; /* 增加padding给删除按钮留空间 */
  overflow-x: auto;
  overflow-y: auto;
}

.deck-grid-wrapper {
  min-height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 1rem;
}

.deck-grid {
  display: grid;
  gap: 1.2rem; /* 稍微增加间距给删除按钮留空间 */
  justify-content: center;
  align-content: flex-start;
  width: fit-content;
  margin: 0 auto;
}

/* 统一网格槽尺寸 - 关键修复：不裁剪删除按钮 */
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
  /* 关键修复：不要设置 overflow: hidden，让删除按钮可以伸出 */
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

/* 统一卡片容器尺寸 - 关键修复：不裁剪删除按钮 */
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
  /* 关键修复：移除 overflow: hidden，让删除按钮可以伸出 */
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

/* 关键修复：删除按钮位置和尺寸 */
.remove-card-btn-wrapper {
  position: absolute;
  top: -6px; /* 调整位置，不要伸出太多 */
  right: -6px; /* 调整位置，不要伸出太多 */
  z-index: 100; /* 确保在最上层 */
}

.remove-card-btn {
  width: 28px !important; /* 增加尺寸让更容易点击 */
  height: 28px !important; /* 增加尺寸让更容易点击 */
  min-width: 28px !important; /* 防止按钮被压缩 */
  min-height: 28px !important; /* 防止按钮被压缩 */
  background: #dc3545 !important;
  border: 2px solid white !important;
  border-radius: 50% !important; /* 确保是圆形 */
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
  transform: scale(1.15) !important; /* 稍微放大让更容易点击 */
  box-shadow: 0 5px 15px rgba(220, 53, 69, 0.6) !important;
  color: white !important;
}

.remove-card-btn .n-icon {
  color: white !important;
  font-size: 14px !important;
}

/* 确保按钮在悬停时显示 */
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

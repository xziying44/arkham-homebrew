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

      <!-- 使用DeckEditor组件 -->
      <DeckEditor v-if="selectedDeck" :deck="selectedDeck" :available-cards="availableCards"
        :available-images="availableImages" :saving="saving" @save="saveDeck" @update:deck="updateSelectedDeck"
        @load-images="loadAvailableImages" />

      <!-- 当没有选择牌库时显示的提示 -->
      <div v-else class="no-deck-selected">
        <n-empty description="请选择一个牌库开始编辑">
          <template #icon>
            <n-icon :component="FolderOpenOutline" size="64" />
          </template>
          <template #extra>
            <n-text depth="3">从左侧列表选择一个牌库，或创建新的牌库</n-text>
          </template>
        </n-empty>
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
import { ref, onMounted, onUnmounted } from 'vue';
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
  WarningOutline
} from '@vicons/ionicons5';
import { WorkspaceService } from '@/api';
import DeckEditor from '@/components/DeckEditor.vue';

interface DeckCard {
  index: number;
  type: 'card' | 'cardback' | 'image';
  path: string;
}

// 在DeckBuilder.vue的interface部分添加TTS相关接口
interface TTSInfo {
  frontImageUrl?: string;
  backImageUrl?: string;
  imageSource?: 'steam' | 'builtin';
  lastExportTime?: string;
  exportPath?: string;
}
interface DeckData {
  name: string;
  width: number;
  height: number;
  frontCards: DeckCard[];
  backCards: DeckCard[];
  ttsInfo?: TTSInfo; // 新增
}
interface DeckFile {
  name: string;
  path: string;
  width: number;
  height: number;
  frontCards: DeckCard[];
  backCards: DeckCard[];
  ttsInfo?: TTSInfo; // 新增
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

// 内容相关
const availableCards = ref<CardFile[]>([]);
const availableImages = ref<ImageFile[]>([]);

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

          // 在loadDecks函数中添加TTS信息的处理
          decks.push({
            name: deckData.name,
            path: file.path,
            width: deckData.width,
            height: deckData.height,
            frontCards: frontCards,
            backCards: backCards,
            ttsInfo: deckData.ttsInfo // 新增
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
    console.log('加载到的图片文件:', images);
  } catch (error) {
    console.error('加载可用图片失败:', error);
    message.error('加载可用图片失败');
  }
};

// 选择牌库
const selectDeck = async (deck: DeckFile) => {
  selectedDeck.value = deck;
};

// 更新选中的牌库 - 修改版本
const updateSelectedDeck = (updatedDeck: DeckFile) => {
  // 只更新引用，避免深度比较
  if (selectedDeck.value && selectedDeck.value.path === updatedDeck.path) {
    // 使用 Object.assign 来更新现有对象，而不是替换整个对象
    Object.assign(selectedDeck.value, updatedDeck);

    // 同时更新牌库列表中的对应项
    const index = deckList.value.findIndex(deck => deck.path === updatedDeck.path);
    if (index > -1) {
      Object.assign(deckList.value[index], updatedDeck);
    }
  } else {
    selectedDeck.value = updatedDeck;
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

    const newDeck: DeckFile = {
      name: deckData.name,
      path: filePath,
      width: deckData.width,
      height: deckData.height,
      frontCards: deckData.frontCards,
      backCards: deckData.backCards
    };

    deckList.value.push(newDeck);

    closeCreateDialog();
    message.success('牌库创建成功');

    // 自动选择新创建的牌库
    selectDeck(newDeck);
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
  padding: 0.5rem 2rem; /* 进一步减少上下padding到0.5rem */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  height: 48px; /* 固定高度为48px */
}

.deck-builder-header h2 {
  margin: 0;
  font-size: 1.1rem; /* 进一步减小字体 */
  font-weight: 600;
  line-height: 1.1;
}

.header-actions .n-button {
  height: 32px; /* 减小按钮高度 */
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

/* 当没有选择牌库时的提示样式 */
.no-deck-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style>

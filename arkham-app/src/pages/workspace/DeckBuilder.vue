<template>
  <div class="deck-builder-container">
    <div class="deck-builder-header">
      <h2>{{ $t('deckBuilder.title') }}</h2>
      <div class="header-actions">
        <n-button type="primary" @click="showCreateDeckDialog = true" size="large">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          {{ $t('deckBuilder.actions.newDeck') }}
        </n-button>
      </div>
    </div>

    <div class="deck-builder-content">
      <!-- 左侧牌库列表 -->
      <div class="deck-list-panel">
        <div class="panel-header">
          <h3>{{ $t('deckBuilder.panels.myDecks') }}</h3>
          <n-button text @click="loadDecks" :loading="loading" :title="$t('deckBuilder.actions.refresh')">
            <n-icon :component="RefreshOutline" />
          </n-button>
        </div>
        <n-scrollbar class="deck-list">
          <div v-for="deck in deckList" :key="deck.path" class="deck-item"
            :class="{ 'active': selectedDeck?.path === deck.path }" @click="selectDeck(deck)">
            <div class="deck-icon">🎴</div>
            <div class="deck-info">
              <div class="deck-name">{{ deck.name }}</div>
              <div class="deck-meta">{{ deck.width }}×{{ deck.height }} {{ $t('deckBuilder.deckList.grid') }}</div>
            </div>
            <n-button text type="error" @click.stop="showDeleteConfirm(deck)" :title="$t('deckBuilder.actions.delete')" size="small">
              <n-icon :component="TrashOutline" />
            </n-button>
          </div>
          <n-empty v-if="deckList.length === 0 && !loading" :description="$t('deckBuilder.deckList.empty')">
            <template #icon>
              <n-icon :component="FolderOpenOutline" />
            </template>
            <template #extra>
              <n-text depth="3">{{ $t('deckBuilder.deckList.emptyDesc') }}</n-text>
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
        <n-empty :description="$t('deckBuilder.noSelection.title')">
          <template #icon>
            <n-icon :component="FolderOpenOutline" size="64" />
          </template>
          <template #extra>
            <n-text depth="3">{{ $t('deckBuilder.noSelection.description') }}</n-text>
          </template>
        </n-empty>
      </div>
    </div>

    <!-- 新建牌库对话框 -->
    <n-modal v-model:show="showCreateDeckDialog" preset="dialog" :title="$t('deckBuilder.forms.newDeck.title')">
      <n-form ref="createFormRef" :model="newDeckForm" :rules="createRules">
        <n-form-item path="name" :label="$t('deckBuilder.forms.newDeck.name')">
          <n-input v-model:value="newDeckForm.name" :placeholder="$t('deckBuilder.forms.newDeck.namePlaceholder')" @keydown.enter="createDeck" clearable />
        </n-form-item>
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item path="width" :label="$t('deckBuilder.forms.newDeck.width')">
              <n-input-number v-model:value="newDeckForm.width" :min="1" :max="10" :placeholder="$t('deckBuilder.forms.newDeck.widthPlaceholder')"
                :show-button="false" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item path="height" :label="$t('deckBuilder.forms.newDeck.height')">
              <n-input-number v-model:value="newDeckForm.height" :min="1" :max="7" :placeholder="$t('deckBuilder.forms.newDeck.heightPlaceholder')"
                :show-button="false" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="closeCreateDialog">{{ $t('deckBuilder.actions.cancel') }}</n-button>
          <n-button type="primary" @click="createDeck" :loading="creating">
            {{ $t('deckBuilder.actions.create') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal v-model:show="showDeleteDialog" preset="dialog" :title="$t('deckBuilder.deleteDialog.title')">
      <n-alert type="warning" :title="$t('deckBuilder.deleteDialog.warning')">
        <template #icon>
          <n-icon :component="WarningOutline" />
        </template>
        {{ $t('deckBuilder.deleteDialog.message', { name: deckToDelete?.name }) }}
      </n-alert>
      <template #action>
        <n-space>
          <n-button @click="showDeleteDialog = false">{{ $t('deckBuilder.actions.cancel') }}</n-button>
          <n-button type="error" @click="confirmDeleteDeck" :loading="deleting">
            {{ $t('deckBuilder.actions.delete') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import {
  useMessage,
  type FormInst,
  type FormRules
} from 'naive-ui';
import { useI18n } from 'vue-i18n';
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
  ttsInfo?: TTSInfo;
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

const message = useMessage();
const { t } = useI18n();

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
const createRules = computed((): FormRules => ({
  name: [
    { required: true, message: t('deckBuilder.forms.validation.nameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: t('deckBuilder.forms.validation.nameLength'), trigger: ['input', 'blur'] },
    {
      pattern: /^[^\\/:*?"<>|]+$/,
      message: t('deckBuilder.forms.validation.namePattern'),
      trigger: ['input', 'blur']
    }
  ],
  width: [
    {
      required: true,
      message: t('deckBuilder.forms.validation.widthRequired'),
      trigger: ['blur', 'change'],
      validator: (rule: any, value: any) => {
        if (value === null || value === undefined || value === '') {
          return new Error(t('deckBuilder.forms.validation.widthRequired'));
        }
        if (typeof value !== 'number' || value < 1 || value > 10) {
          return new Error(t('deckBuilder.forms.validation.widthRange'));
        }
        return true;
      }
    }
  ],
  height: [
    {
      required: true,
      message: t('deckBuilder.forms.validation.heightRequired'),
      trigger: ['blur', 'change'],
      validator: (rule: any, value: any) => {
        if (value === null || value === undefined || value === '') {
          return new Error(t('deckBuilder.forms.validation.heightRequired'));
        }
        if (typeof value !== 'number' || value < 1 || value > 7) {
          return new Error(t('deckBuilder.forms.validation.heightRange'));
        }
        return true;
      }
    }
  ]
}));

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
            backCards: backCards,
            ttsInfo: deckData.ttsInfo
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
    message.success(t('deckBuilder.messages.refreshSuccess'));
  } catch (error) {
    console.error('加载牌库列表失败:', error);
    message.error(t('deckBuilder.messages.loadFailed'));
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
    message.error(t('deckBuilder.messages.loadCardsFailed'));
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
    message.error(t('deckBuilder.messages.loadImagesFailed'));
  }
};

// 选择牌库
const selectDeck = async (deck: DeckFile) => {
  selectedDeck.value = deck;
};

// 更新选中的牌库
const updateSelectedDeck = (updatedDeck: DeckFile) => {
  if (selectedDeck.value && selectedDeck.value.path === updatedDeck.path) {
    Object.assign(selectedDeck.value, updatedDeck);
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
    message.success(t('deckBuilder.messages.createSuccess'));
    selectDeck(newDeck);
  } catch (error) {
    if (error && typeof error === 'object' && 'errors' in error) {
      return;
    }
    console.error('创建牌库失败:', error);
    message.error(t('deckBuilder.messages.createFailed'));
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
      backCards: selectedDeck.value.backCards,
      ttsInfo: selectedDeck.value.ttsInfo
    };

    await WorkspaceService.saveFileContent(
      selectedDeck.value.path,
      JSON.stringify(deckData, null, 2)
    );

    message.success(t('deckBuilder.messages.saveSuccess'));
  } catch (error) {
    console.error('保存牌库失败:', error);
    message.error(t('deckBuilder.messages.saveFailed'));
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
    message.success(t('deckBuilder.messages.deleteSuccess'));
  } catch (error) {
    console.error('删除牌库失败:', error);
    message.error(t('deckBuilder.messages.deleteFailed'));
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
  padding: 0.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  height: 48px;
}

.deck-builder-header h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.1;
}

.header-actions .n-button {
  height: 32px;
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

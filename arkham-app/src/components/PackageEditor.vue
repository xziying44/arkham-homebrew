<template>
  <div class="package-editor-container">
    <!-- 编辑器头部 -->
    <div class="editor-header">
      <div class="package-info">
        <h3>{{ packageData.meta.name }}</h3>
        <div class="package-meta">
          <n-tag type="info" size="small">{{ t(`contentPackage.languages.${packageData.meta.language}`) }}</n-tag>
          <n-tag v-for="type in packageData.meta.types" :key="type" type="default" size="small">
            {{ t(`contentPackage.packageTypes.${type}`) }}
          </n-tag>
          <n-tag type="success" size="small">ID: {{ packageData.meta.code }}</n-tag>
        </div>
      </div>
      <div class="editor-actions">
        <n-button @click="showEditMetaDialog = true" size="small">
          <template #icon>
            <n-icon :component="CreateOutline" />
          </template>
          编辑信息
        </n-button>
        <n-button type="primary" @click="handleSave" :loading="saving" size="small">
          <template #icon>
            <n-icon :component="SaveOutline" />
          </template>
          保存
        </n-button>
      </div>
    </div>

    <!-- 编辑器内容 -->
    <div class="editor-content">
      <n-tabs type="card" default-value="info" animated>
        <!-- 基础信息标签页 -->
        <n-tab-pane name="info" :tab="$t('contentPackage.editor.tabs.info')">
          <div class="info-panel">
            <!-- 封面预览 -->
            <div class="banner-section">
              <h4>{{ $t('contentPackage.editor.sections.banner') }}</h4>
              <div class="banner-preview">
                <img v-if="packageData.meta.banner_url" :src="packageData.meta.banner_url" alt="封面" />
                <img v-else-if="packageData.banner_base64" :src="packageData.banner_base64" alt="封面" />
                <div v-else class="no-banner">
                  <n-icon :component="ImageOutline" size="48" />
                  <span>{{ $t('contentPackage.editor.noBanner') }}</span>
                </div>
              </div>
            </div>

            <!-- 基础信息显示 -->
            <div class="info-section">
              <h4>{{ $t('contentPackage.editor.sections.basicInfo') }}</h4>
              <n-descriptions :column="2" bordered>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.code')">
                  <n-text code>{{ packageData.meta.code }}</n-text>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.name')">
                  <n-tag type="info" size="small">{{ packageData.meta.name }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.author')">
                  <n-tag type="success" size="small">{{ packageData.meta.author }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.language')">
                  <n-tag type="warning" size="small">{{ t(`contentPackage.languages.${packageData.meta.language}`) }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.types')">
                  <n-tag v-for="type in packageData.meta.types" :key="type" :type="getTypeTagColor(type)" size="small">
                    {{ t(`contentPackage.packageTypes.${type}`) }}
                  </n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.status')">
                  <n-tag :type="packageData.meta.status === 'final' ? 'success' : 'warning'" size="small">
                    {{ packageData.meta.status }}
                  </n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.dateUpdated')">
                  <n-tag type="default" size="small">{{ formatDate(packageData.meta.date_updated) }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.generator')">
                  <n-tag type="default" size="small">{{ packageData.meta.generator }}</n-tag>
                </n-descriptions-item>
              </n-descriptions>

              <!-- 描述 -->
              <div class="description-section">
                <h4>{{ $t('contentPackage.editor.fields.description') }}</h4>
                <n-card>
                  <n-text>{{ packageData.meta.description }}</n-text>
                </n-card>
              </div>

              <!-- 外部链接 -->
              <div v-if="packageData.meta.external_link" class="external-link-section">
                <h4>{{ $t('contentPackage.editor.fields.externalLink') }}</h4>
                <n-button text @click="openExternalLink">
                  <template #icon>
                    <n-icon :component="OpenOutline" />
                  </template>
                  {{ packageData.meta.external_link }}
                </n-button>
              </div>
            </div>
          </div>
        </n-tab-pane>

        <!-- 卡牌管理标签页 -->
        <n-tab-pane name="cards" :tab="$t('contentPackage.editor.tabs.cards')">
          <div class="cards-panel">
            <div class="cards-header">
              <h4>{{ $t('contentPackage.editor.sections.cards') }}</h4>
              <n-button type="primary" @click="showAddCardDialog = true" size="small">
                <template #icon>
                  <n-icon :component="AddOutline" />
                </template>
                添加卡牌
              </n-button>
            </div>

            <!-- 卡牌列表 -->
            <div class="cards-content">
              <div v-if="!packageData.cards || packageData.cards.length === 0" class="empty-cards">
                <n-empty description="还没有添加任何卡牌">
                  <template #icon>
                    <n-icon :component="DocumentTextOutline" />
                  </template>
                  <template #extra>
                    <n-text depth="3">点击上方"添加卡牌"按钮开始添加</n-text>
                  </template>
                </n-empty>
              </div>
              <div v-else class="cards-grid">
                <div
                  v-for="(card, index) in packageData.cards"
                  :key="card.filename"
                  class="card-item"
                  :class="{ 'unsupported': getCardStatus(card.filename).version !== '2.0' }"
                >
                  <div class="card-preview">
                    <div v-if="getCardStatus(card.filename).isGenerating" class="preview-loading">
                      <n-spin size="small" />
                    </div>
                    <div v-else-if="getCardStatus(card.filename).generationError" class="preview-error">
                      <n-icon :component="WarningOutline" />
                      <span class="error-text">生成失败</span>
                    </div>
                    <div v-else-if="getCardStatus(card.filename).previewImage" class="preview-image">
                      <img :src="getCardStatus(card.filename).previewImage" :alt="card.filename" />
                    </div>
                    <div v-else class="preview-placeholder">
                      <n-icon :component="DocumentTextOutline" size="24" />
                    </div>
                  </div>
                  <div class="card-info">
                    <div class="card-name">{{ card.filename }}</div>
                    <div class="card-meta">
                      <n-tag v-if="getCardStatus(card.filename).version !== '2.0'" type="error" size="tiny">
                        不支持 (v{{ getCardStatus(card.filename).version }})
                      </n-tag>
                      <n-tag v-else type="success" size="tiny">
                        v{{ getCardStatus(card.filename).version }}
                      </n-tag>
                    </div>
                  </div>
                  <div class="card-actions">
                    <n-button circle size="tiny" type="error" @click="removeCard(index)">
                      <template #icon>
                        <n-icon :component="TrashOutline" />
                      </template>
                    </n-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </n-tab-pane>

        <!-- 导出设置标签页 -->
        <n-tab-pane name="export" :tab="$t('contentPackage.editor.tabs.export')">
          <div class="export-panel">
            <h4>{{ $t('contentPackage.editor.sections.export') }}</h4>

            <!-- 导出设置占位 -->
            <div class="export-content">
              <n-empty description="导出功能开发中">
                <template #icon>
                  <n-icon :component="DownloadOutline" />
                </template>
                <template #extra>
                  <n-text depth="3">该功能将在后续版本中实现</n-text>
                </template>
              </n-empty>
            </div>
          </div>
        </n-tab-pane>
      </n-tabs>
    </div>

    <!-- 编辑元数据对话框 -->
    <n-modal v-model:show="showEditMetaDialog" preset="dialog" :title="$t('contentPackage.editor.editMeta.title')" style="width: 600px;">
      <n-form ref="editFormRef" :model="editForm" :rules="editRules" label-placement="left" label-width="100px">
        <n-form-item path="name" :label="$t('contentPackage.editor.fields.name')">
          <n-input v-model:value="editForm.name" :placeholder="$t('contentPackage.editor.editMeta.namePlaceholder')" clearable />
        </n-form-item>
        <n-form-item path="description" :label="$t('contentPackage.editor.fields.description')">
          <n-input v-model:value="editForm.description" type="textarea" :placeholder="$t('contentPackage.editor.editMeta.descriptionPlaceholder')"
            :rows="3" clearable />
        </n-form-item>
        <n-form-item path="author" :label="$t('contentPackage.editor.fields.author')">
          <n-input v-model:value="editForm.author" :placeholder="$t('contentPackage.editor.editMeta.authorPlaceholder')" clearable />
        </n-form-item>
        <n-form-item path="external_link" :label="$t('contentPackage.editor.fields.externalLink')">
          <n-input v-model:value="editForm.external_link" :placeholder="$t('contentPackage.editor.editMeta.externalLinkPlaceholder')" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.editor.fields.banner')">
          <n-tabs type="line" default-value="url">
            <n-tab-pane name="url" :tab="$t('contentPackage.editor.editMeta.bannerUrl')">
              <n-input v-model:value="editForm.banner_url" :placeholder="$t('contentPackage.editor.editMeta.bannerUrlPlaceholder')" clearable />
            </n-tab-pane>
            <n-tab-pane name="file" :tab="$t('contentPackage.editor.editMeta.bannerFile')">
              <div class="banner-upload-container">
                <div v-if="!editForm.banner_base64" class="upload-area">
                  <n-upload
                    :max="1"
                    accept="image/*"
                    @change="handleEditBannerUpload"
                    :show-download-button="false"
                    :default-upload="false"
                    :show-file-list="false"
                  >
                    <n-upload-dragger>
                      <div style="margin-bottom: 12px">
                        <n-icon size="48" :depth="3">
                          <CloudUploadOutline />
                        </n-icon>
                      </div>
                      <n-text style="font-size: 16px">
                        {{ $t('contentPackage.editor.editMeta.dragToUpload') }}
                      </n-text>
                      <n-p depth="3" style="margin: 8px 0 0 0">
                        {{ $t('contentPackage.editor.editMeta.uploadHint') }}
                      </n-p>
                    </n-upload-dragger>
                  </n-upload>
                </div>
                <div v-else class="banner-preview" @click="triggerEditFileInput">
                  <img :src="editForm.banner_base64" alt="封面预览" />
                  <div class="banner-preview-overlay">
                    <n-button circle type="error" @click.stop="handleEditBannerRemove">
                      <template #icon>
                        <n-icon :component="TrashOutline" />
                      </template>
                    </n-button>
                    <n-button circle type="primary" @click.stop="triggerEditFileInput">
                      <template #icon>
                        <n-icon :component="CreateOutline" />
                      </template>
                    </n-button>
                  </div>
                </div>
                <!-- 隐藏的文件输入框，用于重新上传 -->
                <input
                  ref="editFileInputRef"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleEditFileInputChange"
                />
              </div>
            </n-tab-pane>
          </n-tabs>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="closeEditDialog">{{ $t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="saveMetaChanges">{{ $t('contentPackage.actions.save') }}</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 添加卡牌对话框 -->
    <n-modal v-model:show="showAddCardDialog" preset="card" title="添加卡牌" style="width: 900px; height: 700px;">
      <CardFileBrowser
        v-model:visible="showAddCardDialog"
        @confirm="handleAddCards"
      />
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import {
  useMessage,
  type FormInst,
  type FormRules,
  type UploadFileInfo
} from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
  CreateOutline,
  SaveOutline,
  ImageOutline,
  OpenOutline,
  ConstructOutline,
  DownloadOutline,
  CloudUploadOutline,
  TrashOutline,
  DocumentTextOutline,
  WarningOutline,
  AddOutline
} from '@vicons/ionicons5';
import type { ContentPackageFile, PackageType, ContentPackageCard } from '@/types/content-package';
import { PACKAGE_TYPE_OPTIONS } from '@/types/content-package';
import { WorkspaceService } from '@/api';
import { CardService } from '@/api/card-service';
import CardFileBrowser from '@/components/CardFileBrowser.vue';

interface Props {
  package: ContentPackageFile;
  saving: boolean;
}

interface Emits {
  (e: 'save'): void;
  (e: 'update:package', value: ContentPackageFile): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const message = useMessage();
const { t } = useI18n();

// 编辑器状态
const showEditMetaDialog = ref(false);
const showAddCardDialog = ref(false);
const editFormRef = ref<FormInst | null>(null);

// 文件输入框引用
const editFileInputRef = ref<HTMLInputElement | null>(null);

// 卡牌预览生成队列
const previewGenerationQueue = ref<string[]>([]);
const isGeneratingPreview = ref(false);

// 运行时卡牌状态管理（不保存到文件）
const cardStatusMap = ref<Map<string, {
  version: string;
  previewImage?: string;
  isGenerating: boolean;
  generationError?: string;
}>>(new Map());

// 编辑表单数据
const editForm = ref({
  name: '',
  description: '',
  author: '',
  external_link: '',
  banner_url: '',
  banner_base64: ''
});

// 响应式的包数据
const packageData = computed({
  get: () => props.package,
  set: (value) => emit('update:package', value)
});

// 中止预览生成队列
const abortPreviewGeneration = () => {
  previewGenerationQueue.value = [];
  isGeneratingPreview.value = false;

  // 清除所有正在生成状态
  for (const [filename, status] of cardStatusMap.value.entries()) {
    if (status.isGenerating) {
      cardStatusMap.value.set(filename, {
        ...status,
        isGenerating: false,
        generationError: '已中止'
      });
    }
  }
};

// 表单验证规则
const editRules = computed((): FormRules => ({
  name: [
    { required: true, message: t('contentPackage.forms.validation.nameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 100, message: t('contentPackage.forms.validation.nameLength'), trigger: ['input', 'blur'] }
  ],
  description: [
    { required: true, message: t('contentPackage.forms.validation.descriptionRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 1000, message: t('contentPackage.forms.validation.descriptionLength'), trigger: ['input', 'blur'] }
  ],
  author: [
    { required: true, message: t('contentPackage.forms.validation.authorRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 100, message: t('contentPackage.forms.validation.authorLength'), trigger: ['input', 'blur'] }
  ]
}));

// 获取内容包类型标签
const getPackageTypeLabel = (type: PackageType): string => {
  const option = PACKAGE_TYPE_OPTIONS.find(opt => opt.value === type);
  return option ? option.label : type;
};

// 获取内容包类型标签颜色
const getTypeTagColor = (type: PackageType): string => {
  const colorMap = {
    investigators: 'info',
    player_cards: 'success',
    campaign: 'error'
  };
  return colorMap[type] || 'default';
};

// 格式化日期
const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleString('zh-CN');
  } catch {
    return dateString;
  }
};

// 打开外部链接
const openExternalLink = () => {
  if (packageData.value.meta.external_link) {
    window.open(packageData.value.meta.external_link, '_blank');
  }
};

// 处理保存
const handleSave = () => {
  emit('save');
};

// 处理编辑封面上传
const handleEditBannerUpload = async (data: { file: UploadFileInfo, fileList: UploadFileInfo[] }) => {
  if (data.file.file) {
    handleEditFileUpload(data.file.file);
  }
};

// 处理编辑封面移除
const handleEditBannerRemove = () => {
  editForm.value.banner_base64 = '';
};

// 触发编辑文件输入框
const triggerEditFileInput = () => {
  editFileInputRef.value?.click();
};

// 处理编辑文件输入框变化
const handleEditFileInputChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    handleEditFileUpload(file);
  }
  // 清空输入框，允许重复选择同一个文件
  target.value = '';
};

// 处理编辑文件上传
const handleEditFileUpload = (file: File) => {
  try {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        editForm.value.banner_base64 = e.target.result as string;
      }
    };
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('读取封面文件失败:', error);
    message.error(t('contentPackage.messages.readBannerFailed'));
  }
};

// 保存元数据更改
const saveMetaChanges = () => {
  if (!editFormRef.value) return;

  editFormRef.value.validate((errors) => {
    if (!errors) {
      // 更新包数据
      const updatedPackage = {
        ...packageData.value,
        meta: {
          ...packageData.value.meta,
          name: editForm.value.name,
          description: editForm.value.description,
          author: editForm.value.author,
          external_link: editForm.value.external_link,
          banner_url: editForm.value.banner_url,
          date_updated: new Date().toISOString()
        },
        banner_base64: editForm.value.banner_base64 || packageData.value.banner_base64
      };

      emit('update:package', updatedPackage);
      closeEditDialog();
      message.success(t('contentPackage.editor.editMeta.saveSuccess'));

      // 直接触发保存到文件，避免用户需要再次点击保存按钮
      emit('save');
    }
  });
};

// 关闭编辑对话框
const closeEditDialog = () => {
  showEditMetaDialog.value = false;
  editFormRef.value?.restoreValidation();
};

// 打开编辑对话框时初始化表单数据
const openEditDialog = () => {
  editForm.value = {
    name: packageData.value.meta.name,
    description: packageData.value.meta.description,
    author: packageData.value.meta.author,
    external_link: packageData.value.meta.external_link || '',
    banner_url: packageData.value.meta.banner_url,
    banner_base64: packageData.value.banner_base64
  };
  showEditMetaDialog.value = true;
};

// 监听显示编辑对话框的变化
watch(showEditMetaDialog, (show) => {
  if (show) {
    openEditDialog();
  }
});

// 获取卡牌运行时状态
const getCardStatus = (filename: string) => {
  try {
    if (!cardStatusMap.value.has(filename)) {
      cardStatusMap.value.set(filename, {
        version: '1.0',
        isGenerating: false,
        generationError: undefined,
        previewImage: undefined
      });
    }
    return cardStatusMap.value.get(filename)!;
  } catch (error) {
    console.error('获取卡牌状态时出错:', error);
    return {
      version: '1.0',
      isGenerating: false,
      generationError: undefined,
      previewImage: undefined
    };
  }
};

// 卡牌管理相关方法

// 处理添加卡牌
const handleAddCards = async (items: any[]) => {
  try {
    const newCards: ContentPackageCard[] = [];

    // 处理选中的项目（文件夹和文件）
    for (const item of items) {
      if (item.type === 'directory') {
        // 如果是文件夹，递归获取所有.card文件
        const folderCards = await getCardsFromFolder(item.path);
        newCards.push(...folderCards);
      } else if (item.type === 'card') {
        // 如果是单个文件，读取版本信息
        const cardInfo = await getCardInfo(item.path);
        newCards.push(cardInfo);
      }
    }

    // 合并到现有卡牌列表（去重）
    const existingCards = packageData.value.cards || [];
    const allCards = [...existingCards];

    for (const newCard of newCards) {
      if (!allCards.some(card => card.filename === newCard.filename)) {
        allCards.push(newCard);
      }
    }

    // 更新包数据
    const updatedPackage = {
      ...packageData.value,
      cards: allCards
    };

    emit('update:package', updatedPackage);

    // 立即更新 cardStatusMap 以确保UI显示正确的版本信息
    newCards.forEach(card => {
      cardStatusMap.value.set(card.filename, {
        version: card.version,
        isGenerating: false,
        generationError: undefined,
        previewImage: undefined
      });
    });

    // 开始生成预览图（仅对version 2.0的卡牌）
    startPreviewGeneration(newCards.filter(card => card.version === '2.0'));

    message.success(`成功添加 ${newCards.length} 张卡牌`);
  } catch (error) {
    console.error('添加卡牌失败:', error);
    message.error('添加卡牌失败');
  }
};

// 从文件夹获取所有卡牌
const getCardsFromFolder = async (folderPath: string): Promise<ContentPackageCard[]> => {
  try {
    const response = await WorkspaceService.getFileTree(false);
    const cards: ContentPackageCard[] = [];

    const findCardsInFolder = (node: any): void => {
      if (node.path === folderPath && node.children) {
        // 找到目标文件夹，收集所有.card文件
        node.children.forEach((child: any) => {
          if (child.type === 'card' || (child.type === 'file' && child.label.endsWith('.card'))) {
            const cardInfo = {
              filename: child.path,
              version: '1.0' // 默认版本，后续会更新
            };
            cards.push(cardInfo);
          }
        });
      } else if (node.children) {
        // 递归查找
        node.children.forEach((child: any) => {
          findCardsInFolder(child);
        });
      }
    };

    findCardsInFolder(response.fileTree);

    // 读取每张卡牌的版本信息
    for (const card of cards) {
      try {
        const versionInfo = await checkCardVersion(card.filename);
        card.version = versionInfo.version;
      } catch (error) {
        card.version = '1.0';
      }
    }

    return cards;
  } catch (error) {
    console.error('获取文件夹卡牌失败:', error);
    return [];
  }
};

// 获取单个卡牌信息
const getCardInfo = async (filePath: string): Promise<ContentPackageCard> => {
  try {
    const versionInfo = await checkCardVersion(filePath);

    return {
      filename: filePath,
      version: versionInfo.version
    };
  } catch (error) {
    return {
      filename: filePath,
      version: '1.0'
    };
  }
};

// 删除卡牌
const removeCard = (index: number) => {
  const updatedPackage = {
    ...packageData.value,
    cards: [...(packageData.value.cards || [])]
  };

  updatedPackage.cards?.splice(index, 1);
  emit('update:package', updatedPackage);

  message.success('卡牌已删除');
};

// 检查单张卡牌的版本
const checkCardVersion = async (filename: string): Promise<{
  version: string;
  isV2: boolean;
  error?: string;
}> => {
  try {
    // 直接读取文件内容来检查版本
    const cardData = await WorkspaceService.getFileContent(filename);
    const parsed = JSON.parse(cardData);
    const version = parsed.version || '1.0';
    const isV2 = version === '2.0';

    return {
      version,
      isV2,
      error: undefined
    };
  } catch (error) {
    return {
      version: '1.0',
      isV2: false,
      error: `读取文件失败: ${error.message}`
    };
  }
};

// 刷新卡牌版本信息
const refreshCardVersions = async () => {
  if (!packageData.value?.cards || packageData.value.cards.length === 0) {
    return;
  }

  const cards = packageData.value.cards;
  const v2Cards: ContentPackageCard[] = [];

  // 首先检查所有卡牌的版本
  for (const card of cards) {
    try {
      // 使用 checkCardVersion 函数来检查版本
      const versionInfo = await checkCardVersion(card.filename);

      cardStatusMap.value.set(card.filename, {
        version: versionInfo.version,
        isGenerating: false,
        generationError: versionInfo.error,
        previewImage: undefined
      });

      // 收集v2.0的卡牌用于预览生成
      if (versionInfo.version === '2.0') {
        v2Cards.push(card);
      }
    } catch (error) {
      cardStatusMap.value.set(card.filename, {
        version: '1.0',
        isGenerating: false,
        generationError: '版本检查失败',
        previewImage: undefined
      });
    }
  }

  // 为所有v2.0的卡牌启动预览生成
  if (v2Cards.length > 0) {
    startPreviewGeneration(v2Cards);
  }
};

// 为当前内容包开始预览生成
const startPreviewGenerationForCurrentPackage = async () => {
  try {
    if (!packageData.value?.cards || packageData.value.cards.length === 0) return;

    const validCards = packageData.value.cards.filter(card => {
      const status = getCardStatus(card.filename);
      return status.version === '2.0';
    });

    if (validCards.length === 0) return;

    // 添加到队列
    previewGenerationQueue.value.push(...validCards.map(card => card.filename));

    // 如果当前没有正在生成的，开始生成
    if (!isGeneratingPreview.value) {
      processPreviewQueue();
    }
  } catch (error) {
    // 预览生成失败时的错误处理
  }
};

// 开始预览图生成队列（兼容旧函数）
const startPreviewGeneration = async (cards: ContentPackageCard[]) => {
  const validCards = cards.filter(card => {
    const status = getCardStatus(card.filename);
    return status.version === '2.0';
  });

  if (validCards.length === 0) return;

  // 添加到队列
  previewGenerationQueue.value.push(...validCards.map(card => card.filename));

  // 如果当前没有正在生成的，开始生成
  if (!isGeneratingPreview.value) {
    processPreviewQueue();
  }
};

// 处理预览生成队列
const processPreviewQueue = async () => {
  if (previewGenerationQueue.value.length === 0) {
    isGeneratingPreview.value = false;
    return;
  }

  isGeneratingPreview.value = true;

  while (previewGenerationQueue.value.length > 0) {
    const filename = previewGenerationQueue.value.shift()!;

    try {
      // 标记为正在生成
      cardStatusMap.value.set(filename, {
        ...getCardStatus(filename),
        isGenerating: true,
        generationError: undefined
      });

      // 读取卡牌数据
      const cardData = await WorkspaceService.getFileContent(filename);
      const parsedCard = JSON.parse(cardData);

      // 生成预览图
      const result = await CardService.generateCard(parsedCard);

      // 更新预览图
      cardStatusMap.value.set(filename, {
        ...getCardStatus(filename),
        previewImage: result.image,
        isGenerating: false,
        generationError: undefined
      });

      // 预览图生成成功
    } catch (error) {
      // 预览图生成失败
      cardStatusMap.value.set(filename, {
        ...getCardStatus(filename),
        isGenerating: false,
        generationError: '生成失败'
      });
    }

    // 短暂延迟避免过于频繁的请求
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  isGeneratingPreview.value = false;
};

// 监听内容包变化，自动刷新版本信息
watch(() => packageData.value, async (newPackage, oldPackage) => {
  if (newPackage && (!oldPackage || newPackage.path !== oldPackage.path || JSON.stringify(newPackage.cards) !== JSON.stringify(oldPackage.cards))) {
    // 中止正在进行的预览生成队列
    abortPreviewGeneration();

    // 等待一小段时间确保DOM更新完成
    await nextTick();

    // 刷新版本信息
    await refreshCardVersions();
  }
}, { immediate: true, deep: true });

</script>

<style scoped>
.package-editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0;
}

.editor-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.package-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.package-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.editor-content {
  flex: 1;
  padding: 2rem 3rem 2rem 2.5rem;
  min-height: 0;
  overflow-y: auto;
}

.editor-content :deep(.n-tabs-nav) {
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.editor-content :deep(.n-tabs-tab) {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
}

.info-panel {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.banner-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.banner-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

.banner-preview {
  width: 100%;
  max-width: 400px;
  height: 200px;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #f8f9fa;
}

.banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
}

.info-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

/* 表格标签样式加粗 */
.info-section :deep(.n-descriptions-table .n-descriptions-table-label) {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

/* 表格值颜色调整，降低对比度 */
.info-section :deep(.n-descriptions-table .n-descriptions-table-content) {
  color: #5a6c7d;
  font-size: 0.9rem;
}

.description-section {
  margin-top: 1.5rem;
}

.description-section h4 {
  margin: 0 0 0.75rem 0;
}

.external-link-section {
  margin-top: 1.5rem;
}

.external-link-section h4 {
  margin: 0 0 0.75rem 0;
}

.cards-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.cards-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.cards-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.cards-content {
  flex: 1;
  min-height: 400px;
}

.empty-cards {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  height: 100%;
  overflow-y: auto;
}

.card-item {
  position: relative;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-item.unsupported {
  border-color: #f56565;
  background: #fff5f5;
}

.card-item.unsupported:hover {
  border-color: #e53e3e;
}

.card-preview {
  width: 100%;
  height: 140px;
  border-radius: 6px;
  overflow: hidden;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
  border: 1px solid #e9ecef;
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #e53e3e;
  gap: 0.5rem;
}

.error-text {
  font-size: 0.75rem;
  font-weight: 500;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
}

.card-info {
  margin-bottom: 0.5rem;
}

.card-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  word-break: break-word;
  line-height: 1.2;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.card-item:hover .card-actions {
  opacity: 1;
}

.export-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.export-panel h4 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.export-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 封面上传容器 */
.banner-upload-container {
  width: 100%;
}

.banner-upload-container .n-upload {
  width: 100%;
}

.upload-area {
  width: 100%;
}

.upload-area .n-upload {
  width: 100%;
}

/* 封面预览 */
.banner-preview {
  position: relative;
  width: 100%;
  max-width: 400px;
  height: 225px; /* 16:9 比例 */
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e9ecef;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.banner-preview:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-preview-overlay {
  position: absolute;
  top: 0;
  right: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.5);
  border-bottom-left-radius: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  gap: 8px;
}

.banner-preview:hover .banner-preview-overlay {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .package-meta {
    justify-content: center;
  }

  .editor-actions {
    justify-content: center;
  }

  .editor-content {
    padding: 1rem;
  }

  .banner-preview {
    max-width: 100%;
    height: 150px;
  }
}
</style>
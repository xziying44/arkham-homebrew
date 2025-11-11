<template>
  <div class="universal-upload-dialog">
    <!-- 图床选择 -->
    <div class="upload-section">
      <h4>{{ $t('contentPackage.upload.dialog.selectImageHost') }}</h4>
      <n-radio-group :value="selectedHost" @update:value="handleHostChange" size="medium">
        <n-radio-button value="cloudinary">Cloudinary</n-radio-button>
        <n-radio-button value="imgbb">ImgBB</n-radio-button>
        <n-radio-button value="local">{{ $t('contentPackage.upload.dialog.localMode') }}</n-radio-button>
      </n-radio-group>
      <div v-if="selectedHost === 'local'" class="local-info">
        <n-alert type="info" size="small">
          <template #icon>
            <n-icon :component="InformationCircleOutline" />
          </template>
          {{ $t('contentPackage.upload.dialog.localModeDescription') }}
        </n-alert>
      </div>
    </div>

    <!-- Cloudinary 配置 -->
    <div v-if="selectedHost === 'cloudinary'" class="upload-section">
      <h4>{{ $t('contentPackage.upload.dialog.cloudinaryConfig') }}</h4>
      <n-form :model="cloudinaryConfig" label-placement="top">
        <n-form-item :label="$t('contentPackage.upload.dialog.cloudName')" required>
          <n-input v-model:value="cloudinaryConfig.cloud_name" placeholder="your-cloud-name" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.upload.dialog.apiKey')" required>
          <n-input v-model:value="cloudinaryConfig.api_key" placeholder="your-api-key" type="password"
            show-password-on="click" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.upload.dialog.apiSecret')" required>
          <n-input v-model:value="cloudinaryConfig.api_secret" placeholder="your-api-secret" type="password"
            show-password-on="click" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.upload.dialog.folder')">
          <n-input v-model:value="cloudinaryConfig.folder" :placeholder="$t('contentPackage.upload.dialog.folderPlaceholder')" clearable />
        </n-form-item>
      </n-form>
    </div>

    <!-- ImgBB 配置 -->
    <div v-if="selectedHost === 'imgbb'" class="upload-section">
      <h4>{{ $t('contentPackage.upload.dialog.imgbbConfig') }}</h4>
      <n-form :model="imgbbConfig" label-placement="top">
        <n-form-item :label="$t('contentPackage.upload.dialog.apiKey')" required>
          <n-input v-model:value="imgbbConfig.imgbb_api_key" placeholder="your-imgbb-api-key" type="password"
            show-password-on="click" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.upload.dialog.expirationHours')">
          <n-input-number v-model:value="imgbbConfig.imgbb_expiration" :min="0" :max="30 * 24" :placeholder="$t('contentPackage.upload.dialog.expirationPlaceholder')"
            clearable />
        </n-form-item>
      </n-form>
    </div>

    <!-- 导出格式选择（仅用于卡牌） -->
    <div v-if="uploadType === 'card'" class="upload-section">
      <h4>{{ $t('contentPackage.upload.dialog.exportFormat') }}</h4>
      <n-radio-group v-model:value="exportFormat" size="medium">
        <n-radio-button value="JPG">JPG</n-radio-button>
        <n-radio-button value="PNG">PNG</n-radio-button>
      </n-radio-group>
      <div v-if="exportFormat === 'JPG'" class="quality-setting">
        <n-form-item :label="$t('contentPackage.upload.dialog.imageQuality')">
          <n-slider v-model:value="exportQuality" :min="1" :max="100"
            :marks="{ 1: '1%', 50: '50%', 100: '100%' }" :tooltip="false" />
          <n-input-number v-model:value="exportQuality" :min="1" :max="100" size="small"
            style="width: 100px; margin-left: 12px;" />
        </n-form-item>
      </div>
    </div>

    <!-- 上传内容预览 -->
    <div class="upload-section">
      <h4>{{ getUploadTitle() }}</h4>

      <!-- 单个内容预览 -->
      <div v-if="!isBatch && currentItem" class="item-preview">
        <div class="preview-container">
          <!-- 封面预览 -->
          <div v-if="uploadType === 'banner'" class="banner-preview">
            <img v-if="currentItem.banner_base64" :src="currentItem.banner_base64" :alt="t('contentPackage.upload.dialog.currentBanner')" />
            <div v-else class="no-content">
              <n-icon :component="ImageOutline" size="48" />
              <span>{{ $t('contentPackage.upload.dialog.noBanner') }}</span>
            </div>
          </div>

          <!-- 卡牌预览 -->
          <div v-else-if="uploadType === 'card'" class="card-preview">
            <div class="card-info">
              <n-text strong>{{ currentItem.filename }}</n-text>
            </div>
          </div>

          <!-- 遭遇组预览 -->
          <div v-else-if="uploadType === 'encounter'" class="encounter-preview">
            <div class="encounter-icon">
              <img v-if="currentItem.base64" :src="currentItem.base64" :alt="currentItem.name" />
              <div v-else class="no-icon">
                <n-icon :component="ImagesOutline" size="48" />
                <span>{{ $t('contentPackage.upload.dialog.noIcon') }}</span>
              </div>
            </div>
            <div class="encounter-details">
              <n-descriptions :column="1" bordered>
                <n-descriptions-item :label="$t('contentPackage.upload.dialog.encounterName')">
                  <n-text strong>{{ currentItem.name }}</n-text>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.upload.dialog.currentStatus')">
                  <n-tag v-if="hasCloudUrl(currentItem)" type="success" size="small">
                    {{ $t('contentPackage.upload.status.uploadedToCloud') }}
                  </n-tag>
                  <n-tag v-else-if="hasLocalUrl(currentItem)" type="info" size="small">
                    {{ $t('contentPackage.upload.status.savedToLocal') }}
                  </n-tag>
                  <n-tag v-else type="warning" size="small">
                    {{ $t('contentPackage.upload.status.notUploaded') }}
                  </n-tag>
                </n-descriptions-item>
              </n-descriptions>
            </div>
          </div>
        </div>
      </div>

      <!-- 批量上传预览 -->
      <div v-else-if="isBatch && uploadItems.length > 0" class="batch-preview">
        <div class="batch-info">
          <n-alert type="info" style="margin-bottom: 1rem;">
            <template #icon>
              <n-icon :component="InformationCircleOutline" />
            </template>
            {{ getBatchInfo() }}
          </n-alert>

          <n-descriptions :column="2" bordered>
            <n-descriptions-item :label="getTotalLabel()">
              <n-tag type="info" size="small">{{ uploadItems.length }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item :label="getUploadedLabel()">
              <n-tag type="success" size="small">{{ getUploadedCount() }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="待上传">
              <n-tag type="warning" size="small">{{ getPendingCount() }}</n-tag>
            </n-descriptions-item>
          </n-descriptions>
        </div>

        <div class="items-list">
          <n-scrollbar style="max-height: 300px;">
            <div class="items-grid">
              <div v-for="item in uploadItems" :key="getItemKey(item)" class="item-card">
                <!-- 卡牌项目 -->
                <div v-if="uploadType === 'card'" class="item-info">
                  <n-text>{{ item.filename }}</n-text>
                  <div class="item-status">
                    <n-tag v-if="hasCloudUrl(item)" type="success" size="tiny">
                      {{ $t('contentPackage.upload.status.cloud') }}
                    </n-tag>
                    <n-tag v-else-if="hasLocalUrl(item)" type="info" size="tiny">
                      {{ $t('contentPackage.upload.status.local') }}
                    </n-tag>
                    <n-tag v-else type="warning" size="tiny">
                      {{ $t('contentPackage.upload.status.pending') }}
                    </n-tag>
                  </div>
                </div>

                <!-- 遭遇组项目 -->
                <div v-else-if="uploadType === 'encounter'" class="encounter-item">
                  <div class="encounter-icon">
                    <img v-if="item.base64" :src="item.base64" :alt="item.name" />
                    <div v-else class="no-icon">
                      <n-icon :component="ImagesOutline" size="24" />
                    </div>
                  </div>
                  <div class="encounter-info">
                    <div class="encounter-name">{{ item.name }}</div>
                    <div class="encounter-status">
                      <n-tag v-if="hasCloudUrl(item)" type="success" size="tiny">
                        {{ $t('contentPackage.upload.status.cloud') }}
                      </n-tag>
                      <n-tag v-else-if="hasLocalUrl(item)" type="info" size="tiny">
                        {{ $t('contentPackage.upload.status.local') }}
                      </n-tag>
                      <n-tag v-else type="warning" size="tiny">
                        {{ $t('contentPackage.upload.status.pending') }}
                      </n-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </n-scrollbar>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="isUploading" class="upload-section">
      <h4>{{ $t('contentPackage.upload.dialog.uploadProgress') }}</h4>
      <n-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : 'default'"
        :indicator-placement="'inside'" />
      <div class="upload-status">
        <n-text depth="3">{{ uploadStatus }}</n-text>
      </div>
    </div>

    <!-- 上传日志 -->
    <div v-if="uploadLogs.length > 0" class="upload-section">
      <h4>{{ $t('contentPackage.upload.dialog.uploadLogs') }}</h4>
      <div class="log-container">
        <n-scrollbar style="max-height: 200px;">
          <div v-for="(log, index) in uploadLogs" :key="index" class="log-item">
            <n-text :depth="log.type === 'error' ? 3 : 2" :type="log.type === 'error' ? 'error' : 'default'">
              {{ log.message }}
            </n-text>
          </div>
        </n-scrollbar>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useMessage } from 'naive-ui';
import { ConfigService } from '@/api/config-service';
import { ImageHostService } from '@/api/image-host-service';
import { DirectoryService } from '@/api/directory-service';
import { CardService } from '@/api/card-service';
import { WorkspaceService } from '@/api/workspace-service';
import { InformationCircleOutline, ImageOutline, ImagesOutline } from '@vicons/ionicons5';
import type { ImageHostType } from '@/api/types';
import type { ContentPackageCard, EncounterSet } from '@/types/content-package';
import { useI18n } from 'vue-i18n';
import { v4 as uuidv4 } from 'uuid';

export type UploadType = 'banner' | 'card' | 'encounter';

interface Props {
  uploadType: UploadType;
  currentItem?: any; // 单个上传时的项目
  uploadItems?: any[]; // 批量上传时的项目列表
  config?: any;
  isBatch?: boolean;
}

interface Emits {
  (e: 'confirm', updatedPackage: any): void;
  (e: 'cancel'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const message = useMessage();
const { t } = useI18n();

// 本地化辅助函数
const tMessage = (key: string, params?: Record<string, string | number>) => {
  return params ? t(key, params) : t(key);
};

// 上传状态
const selectedHost = ref<ImageHostType>('cloudinary');
const userSelectedHost = ref(false); // 标记用户是否手动选择过图床
const exportFormat = ref<'JPG' | 'PNG'>('JPG');
const exportQuality = ref(95);
const isUploading = ref(false);
const uploadProgress = ref(0);
const uploadStatus = ref('');
const uploadLogs = ref<Array<{ message: string; type: 'info' | 'error' }>>([]);

// 配置数据
const cloudinaryConfig = ref({
  cloud_name: '',
  api_key: '',
  api_secret: '',
  folder: ''
});

const imgbbConfig = ref({
  imgbb_api_key: '',
  imgbb_expiration: 0
});

const footer_icon = ref('');

// 计算属性
const isBatch = computed(() => props.isBatch || !!props.uploadItems?.length);
const uploadItems = computed(() => props.uploadItems || []);
const currentItem = computed(() => props.currentItem);

// 计算当前配置
const currentConfig = computed(() => {
  return selectedHost.value === 'cloudinary' ? cloudinaryConfig.value : imgbbConfig.value;
});

// 计算项目状态
const hasCloudUrl = (item: any): boolean => {
  const url = getItemUrl(item);
  return !!(url?.startsWith('http://') || url?.startsWith('https://'));
};

const hasLocalUrl = (item: any): boolean => {
  const url = getItemUrl(item);
  return !!(url?.startsWith('file:///'));
};

const getItemUrl = (item: any): string | undefined => {
  if (props.uploadType === 'banner') {
    return item.meta?.banner_url;
  } else if (props.uploadType === 'card') {
    return item.front_url || item.back_url;
  } else if (props.uploadType === 'encounter') {
    return item.icon_url;
  }
  return undefined;
};

// 获取上传标题
const getUploadTitle = (): string => {
  if (props.uploadType === 'banner') {
    return t('contentPackage.upload.dialog.bannerInfo');
  } else if (props.uploadType === 'card') {
    return t('contentPackage.upload.dialog.cardInfo');
  } else if (props.uploadType === 'encounter') {
    return t('contentPackage.upload.dialog.encounterInfo');
  }
  return t('contentPackage.upload.dialog.uploadInfo');
};

// 获取批量信息
const getBatchInfo = (): string => {
  const total = uploadItems.value.length;
  const uploaded = getUploadedCount();
  const pending = getPendingCount();

  if (props.uploadType === 'card') {
    return uploaded > 0
      ? `将上传 ${pending} 张新卡牌，重新上传 ${uploaded} 张已有卡牌`
      : `将重新上传 ${uploaded} 张卡牌到云端`;
  } else if (props.uploadType === 'encounter') {
    return uploaded > 0
      ? `将上传 ${pending} 个新遭遇组，重新上传 ${uploaded} 个已有遭遇组`
      : `将重新上传 ${uploaded} 个遭遇组到云端`;
  }

  return `将上传 ${total} 个项目`;
};

const getTotalLabel = (): string => {
  if (props.uploadType === 'card') {
    return t('contentPackage.upload.info.v2CardCount');
  } else if (props.uploadType === 'encounter') {
    return t('contentPackage.upload.info.totalEncounters');
  }
  return t('contentPackage.upload.info.totalItems');
};

const getUploadedLabel = (): string => {
  return t('contentPackage.upload.info.cloudUploaded');
};

const getUploadedCount = (): number => {
  return uploadItems.value.filter(item => hasCloudUrl(item)).length;
};

const getPendingCount = (): number => {
  return uploadItems.value.filter(item => !hasCloudUrl(item)).length;
};

const getItemKey = (item: any): string => {
  if (props.uploadType === 'card') {
    return item.filename;
  } else if (props.uploadType === 'encounter') {
    return item.code;
  }
  return item.id || JSON.stringify(item);
};

// 处理用户手动选择图床
const handleHostChange = (value: ImageHostType) => {
  selectedHost.value = value;
  userSelectedHost.value = true; // 标记为用户手动选择
};

// 添加日志
const addLog = (message: string, type: 'info' | 'error' = 'info') => {
  uploadLogs.value.push({ message, type });
  // 自动滚动到底部
  nextTick(() => {
    const container = document.querySelector('.log-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
};

// 获取工作空间绝对路径
const getWorkspaceAbsolutePath = async (): Promise<string> => {
  try {
    const workspacePath = await DirectoryService.getCurrentWorkspacePath();
    if (workspacePath) {
      return workspacePath;
    }
    throw new Error('无法获取工作空间路径');
  } catch (error) {
    console.error('获取工作空间路径失败:', error);
    throw error;
  }
};

// 加载配置
const loadConfig = async () => {
  try {
    const config = await ConfigService.getConfig();

    // 加载Cloudinary配置
    if (config.cloud_name) cloudinaryConfig.value.cloud_name = config.cloud_name;
    if (config.api_key) cloudinaryConfig.value.api_key = config.api_key;
    if (config.api_secret) cloudinaryConfig.value.api_secret = config.api_secret;
    if (config.folder) cloudinaryConfig.value.folder = config.folder;

    // 加载ImgBB配置
    if (config.imgbb_api_key) imgbbConfig.value.imgbb_api_key = config.imgbb_api_key;
    if (config.imgbb_expiration !== undefined) imgbbConfig.value.imgbb_expiration = config.imgbb_expiration;

    if (config.footer_icon_dir) {
      footer_icon.value = config.footer_icon_dir;
    }

    // 只在用户未手动选择时，根据配置自动选择对应的图床
    if (!userSelectedHost.value) {
      if (config.cloud_name || config.api_key) {
        selectedHost.value = 'cloudinary';
      } else if (config.imgbb_api_key) {
        selectedHost.value = 'imgbb';
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error);
    addLog(tMessage('contentPackage.upload.error.configLoadFailed', { message: error.message }), 'error');
  }
};

// 保存配置
const saveConfig = async () => {
  try {
    // 本地模式不需要保存配置
    if (selectedHost.value === 'local') {
      addLog(tMessage('contentPackage.upload.success.localModeNoSave'), 'info');
      return;
    }

    const config: any = {};

    // 保存Cloudinary配置
    if (cloudinaryConfig.value.cloud_name) config.cloud_name = cloudinaryConfig.value.cloud_name;
    if (cloudinaryConfig.value.api_key) config.api_key = cloudinaryConfig.value.api_key;
    if (cloudinaryConfig.value.api_secret) config.api_secret = cloudinaryConfig.value.api_secret;
    if (cloudinaryConfig.value.folder) config.folder = cloudinaryConfig.value.folder;

    // 保存ImgBB配置
    if (imgbbConfig.value.imgbb_api_key) config.imgbb_api_key = imgbbConfig.value.imgbb_api_key;
    if (imgbbConfig.value.imgbb_expiration !== undefined) config.imgbb_expiration = imgbbConfig.value.imgbb_expiration;

    await ConfigService.saveConfig(config);
    addLog(tMessage('contentPackage.upload.success.configSaveSuccess'), 'info');
  } catch (error) {
    console.error('保存配置失败:', error);
    addLog(tMessage('contentPackage.upload.error.configSaveFailed', { message: error.message }), 'error');
    throw error;
  }
};

// 验证配置
const validateConfig = (): boolean => {
  if (selectedHost.value === 'local') {
    return true; // 本地模式不需要验证配置
  } else if (selectedHost.value === 'cloudinary') {
    return !!(cloudinaryConfig.value.cloud_name &&
      cloudinaryConfig.value.api_key &&
      cloudinaryConfig.value.api_secret);
  } else {
    return !!imgbbConfig.value.imgbb_api_key;
  }
};

// 上传封面
const uploadBanner = async () => {
  if (props.uploadType !== 'banner' || !currentItem.value) return;

  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    uploadStatus.value = tMessage('contentPackage.upload.dialog.preparingUpload');
    uploadLogs.value = [];

    // 验证配置
    if (!validateConfig()) {
      throw new Error(tMessage('contentPackage.upload.error.configIncomplete'));
    }

    // 保存配置
    await saveConfig();
    uploadProgress.value = 20;
    uploadStatus.value = tMessage('contentPackage.upload.dialog.configSaved');

    // 检查是否有base64数据
    if (!currentItem.value.banner_base64) {
      throw new Error(tMessage('contentPackage.upload.error.noBannerData'));
    }

    uploadProgress.value = 40;
    uploadStatus.value = tMessage('contentPackage.upload.dialog.preparingImages');

    // 创建临时卡牌数据用于生成图片
    const tempCardData = {
      type: '封面制作',
      picture_base64: currentItem.value.banner_base64
    };

    // 导出图片到工作目录
    const savedFiles = await CardService.saveCardEnhanced(tempCardData, 'banner', {
      parentPath: '.banner',
      format: exportFormat.value,
      quality: exportQuality.value,
      rotateLandscape: true
    });

    uploadProgress.value = 60;
    uploadStatus.value = '准备上传到云端...';

    // 依据包唯一标识生成唯一的线上文件名，避免跨包覆盖
    const pkgMeta = (props.config && props.config.meta) ? props.config.meta : {};
    // 优先使用 meta.code；若无则从 path/name 派生一个安全标识，最后回退 UUID
    const deriveSafeId = (v: any): string => {
      try {
        const s = String(v || '').trim();
        if (!s) return '';
        const cleaned = s.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 64);
        return cleaned;
      } catch {
        return '';
      }
    };
    let code = deriveSafeId(pkgMeta.code);
    if (!code) {
      code = deriveSafeId(props.config?.path) || deriveSafeId(pkgMeta.name) || uuidv4();
    }
    const basePublicId = `banners/${code}`;

    // 上传图片（正面作为 banner，背面作为 banner_box）
    const imageUrl = await uploadSingleImage(savedFiles.saved_files.front_url, basePublicId);
    const imageBoxUrl = await uploadSingleImage(savedFiles.saved_files.back_url, `${basePublicId}_box`);
    let footerIconUrl = null;

    // 上传遭遇组图标
    try {
      if (footer_icon.value !== '') {
        footerIconUrl = await uploadSingleImage(footer_icon.value, 'footer_icon');
      }
    } catch (error) {
      console.error(error);
    }

    uploadProgress.value = 80;
    uploadStatus.value = '更新内容包数据...';

    // 更新内容包的banner_url，并清理本地base64以防回退干扰
    const updatedPackage = {
      ...props.config,
      meta: {
        ...props.config.meta,
        banner_url: imageUrl,
        banner_box_url: imageBoxUrl,
        icon_url: footerIconUrl
      },
      banner_base64: ''
    };

    emit('confirm', updatedPackage);
    addLog('封面上传完成', 'info');

    uploadProgress.value = 100;
    uploadStatus.value = '上传成功';

  } catch (error) {
    console.error('上传封面失败:', error);
    message.error(`上传失败: ${error.message}`);
  } finally {
    isUploading.value = false;
  }
};

// 上传单个项目
const uploadSingleItem = async (item: any) => {
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    uploadStatus.value = tMessage('contentPackage.upload.dialog.preparingUpload');
    uploadLogs.value = [];

    // 验证配置
    if (!validateConfig()) {
      throw new Error(tMessage('contentPackage.upload.error.configIncomplete'));
    }

    // 保存配置
    await saveConfig();
    uploadProgress.value = 20;
    uploadStatus.value = tMessage('contentPackage.upload.dialog.configSaved');

    if (props.uploadType === 'card') {
      await uploadCard(item);
    } else if (props.uploadType === 'encounter') {
      await uploadEncounter(item);
    }

  } catch (error) {
    console.error('上传失败:', error);
    addLog(`上传失败: ${error.message}`, 'error');
    throw error;
  } finally {
    isUploading.value = false;
  }
};

// 上传卡牌
const uploadCard = async (card: ContentPackageCard) => {
  uploadProgress.value = 40;
  uploadStatus.value = tMessage('contentPackage.upload.dialog.preparingImages');

  // 读取卡牌数据
  const cardData = await WorkspaceService.getFileContent(card.filename);
  const parsedCard = JSON.parse(cardData);

  uploadProgress.value = 40;
  uploadStatus.value = tMessage('contentPackage.upload.dialog.preparingImages');

  // 导出图片到工作目录 - 使用增强版API
  const result = await CardService.saveCardEnhanced(parsedCard, card.filename.replace('.card', ''), {
    parentPath: '.cards',
    format: exportFormat.value,
    quality: exportQuality.value,
    rotateLandscape: true
  });

  // 获取返回的文件路径对象
  const savedFiles = result.saved_files || {};

  uploadProgress.value = 60;
  uploadStatus.value = '准备上传到云端...';

  // 检查背面卡牌类型
  const backCardType = parsedCard.back?.type || '';
  const filename = card.filename.toLowerCase();
  let useFixedBackUrl = false;
  let fixedBackUrl = '';

  if (backCardType === '玩家卡背' || filename.includes('player_cardback') || filename.includes('玩家卡背')) {
    useFixedBackUrl = true;
    fixedBackUrl = "https://steamusercontent-a.akamaihd.net/ugc/2342503777940352139/A2D42E7E5C43D045D72CE5CFC907E4F886C8C690/";
    addLog(`检测到玩家卡背，使用预定义URL`, 'info');
  } else if (backCardType === '遭遇卡背' || filename.includes('encounter_cardback') || filename.includes('遭遇卡背')) {
    useFixedBackUrl = true;
    fixedBackUrl = "https://steamusercontent-a.akamaihd.net/ugc/2342503777940351785/F64D8EFB75A9E15446D24343DA0A6EEF5B3E43DB/";
    addLog(`检测到遭遇卡背，使用预定义URL`, 'info');
  }

  // 收集需要上传的文件，并去重
  const filesToUpload = new Map();
  const cleanCardName = card.filename.replace(/.*[\\/\\\\]/, '').replace('.card', '');

  // 正面图片
  if (savedFiles.front_url) {
    filesToUpload.set(savedFiles.front_url, `${cleanCardName}_front`);
  }

  // 正面原始图片（如果与正面图片不同）
  if (savedFiles.original_front_url && savedFiles.original_front_url !== savedFiles.front_url) {
    filesToUpload.set(savedFiles.original_front_url, `${cleanCardName}_front_original`);
  }

  // 正面缩略图
  if (savedFiles.front_thumbnail_url) {
    filesToUpload.set(savedFiles.front_thumbnail_url, `${cleanCardName}_front_thumbnail`);
  }

  // 背面图片 - 只有非固定卡背才上传
  if (!useFixedBackUrl) {
    if (savedFiles.back_url) {
      filesToUpload.set(savedFiles.back_url, `${cleanCardName}_back`);
    }

    // 背面原始图片（如果与背面图片不同）
    if (savedFiles.original_back_url && savedFiles.original_back_url !== savedFiles.back_url) {
      filesToUpload.set(savedFiles.original_back_url, `${cleanCardName}_back_original`);
    }

    // 背面缩略图
    if (savedFiles.back_thumbnail_url) {
      filesToUpload.set(savedFiles.back_thumbnail_url, `${cleanCardName}_back_thumbnail`);
    }
  }

  // 上传所有文件
  const uploadedUrls: Record<string, string> = {};

  // 如果使用固定卡背URL，直接设置
  if (useFixedBackUrl) {
    uploadedUrls.back_url = fixedBackUrl;
    uploadedUrls.original_back_url = fixedBackUrl;
    uploadedUrls.back_thumbnail_url = fixedBackUrl;
  }

  let uploadedCount = 0;
  const totalFiles = filesToUpload.size;

  for (const [filePath, onlineName] of filesToUpload.entries()) {
    try {
      uploadedCount++;
      uploadStatus.value = `上传图片 ${uploadedCount}/${totalFiles}...`;

      const url = await uploadSingleImage(filePath, onlineName);

      // 根据在线文件名存储URL
      if (onlineName.includes('_front_original')) {
        uploadedUrls.original_front_url = url;
      } else if (onlineName.includes('_front_thumbnail')) {
        uploadedUrls.front_thumbnail_url = url;
      } else if (onlineName.includes('_front')) {
        uploadedUrls.front_url = url;
      } else if (onlineName.includes('_back_original')) {
        uploadedUrls.original_back_url = url;
      } else if (onlineName.includes('_back_thumbnail')) {
        uploadedUrls.back_thumbnail_url = url;
      } else if (onlineName.includes('_back')) {
        uploadedUrls.back_url = url;
      }

      addLog(`图片上传成功: ${onlineName}`, 'info');
    } catch (error) {
      addLog(`图片上传失败: ${onlineName} - ${error.message}`, 'error');
    }
  }

  uploadProgress.value = 80;
  uploadStatus.value = '更新内容包数据...';

  // 更新卡牌的云端URL
  const updatedPackage = { ...props.config };
  const cardIndex = updatedPackage.cards?.findIndex(c => c.filename === card.filename);
  if (cardIndex !== undefined && cardIndex >= 0) {
    const existing = updatedPackage.cards![cardIndex] || {};
    // 非本地模式上传成功后，记录当前卡牌文件的 content_hash 到 uploaded_hash
    const newUploadedHash = (selectedHost.value !== 'local' && parsedCard?.content_hash)
      ? parsedCard.content_hash
      : existing.uploaded_hash;

    updatedPackage.cards![cardIndex] = {
      ...existing,
      front_url: uploadedUrls.front_url,
      back_url: uploadedUrls.back_url,
      original_front_url: uploadedUrls.original_front_url,
      original_back_url: uploadedUrls.original_back_url,
      front_thumbnail_url: uploadedUrls.front_thumbnail_url,
      back_thumbnail_url: uploadedUrls.back_thumbnail_url,
      uploaded_hash: newUploadedHash
    };
  }

  emit('confirm', updatedPackage);
  addLog('卡牌上传完成', 'info');
  uploadProgress.value = 100;
  uploadStatus.value = '上传成功';
};

// 上传遭遇组
const uploadEncounter = async (encounter: EncounterSet) => {
  uploadProgress.value = 40;
  uploadStatus.value = tMessage('contentPackage.upload.dialog.preparingImages');

  // 检查是否有图标数据
  if (!encounter.base64 && !encounter.relative_path) {
    throw new Error(tMessage('contentPackage.encounters.error.noIconData'));
  }

  uploadProgress.value = 60;
  uploadStatus.value = '准备上传到云端...';

  const onlineName = `${encounter.name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}_icon`;

  let iconUrl: string;
  let imagePath: string;

  if (selectedHost.value === 'local') {
    // 本地模式：创建本地文件并返回file:///URL
    const workspacePath = await getWorkspaceAbsolutePath();
    const fileName = `${onlineName}.png`;
    const fullPath = `${workspacePath}/.encounters/${fileName}`;
    iconUrl = fullPath.includes(':')
      ? `file:///${fullPath.replace(/\\\\/g, '/')}`
      : `file://${fullPath}`;
    imagePath = fullPath;

    addLog(tMessage('contentPackage.upload.dialog.localModeUrl', { url: iconUrl }), 'info');
  } else {
    // 云端模式：上传到图床
    // 优先使用relative_path，如果没有则使用base64
    if (encounter.relative_path) {
      imagePath = encounter.relative_path;
    } else if (encounter.base64) {
      imagePath = encounter.base64;
    } else {
      throw new Error(tMessage('contentPackage.encounters.error.noIconData'));
    }

    const result = await ImageHostService.smartUpload(
      imagePath,
      selectedHost.value,
      onlineName
    );

    if (result.code === 0 && result.data?.url) {
      iconUrl = result.data.url;
      addLog(tMessage('contentPackage.upload.dialog.imageUploadSuccessUrl', { url: result.data.url }), 'info');
    } else {
      throw new Error(result.msg || '上传失败');
    }
  }

  uploadProgress.value = 80;
  uploadStatus.value = '更新内容包数据...';

  // 更新内容包的遭遇组信息
  const updatedPackage = {
    ...props.config,
    encounter_sets: props.config.encounter_sets?.map((enc: EncounterSet) => {
      if (enc.code === encounter.code) {
        return {
          ...enc,
          icon_url: iconUrl
        };
      }
      return enc;
    }) || []
  };

  emit('confirm', updatedPackage);
  addLog('遭遇组图标上传完成', 'info');
  uploadProgress.value = 100;
  uploadStatus.value = '上传成功';
};

// 批量上传
const batchUpload = async () => {
  const itemsToUpload = uploadItems.value;
  if (itemsToUpload.length === 0) {
    message.warning('没有需要上传的项目');
    return;
  }

  isUploading.value = true;
  uploadProgress.value = 0;
  uploadStatus.value = '准备批量上传...';
  uploadLogs.value = [];

  try {
    // 验证配置
    if (!validateConfig()) {
      throw new Error(tMessage('contentPackage.upload.error.configIncomplete'));
    }

    // 保存配置
    await saveConfig();
    uploadProgress.value = 10;
    uploadStatus.value = tMessage('contentPackage.upload.dialog.configSaved');

    // 使用用户选择的图床类型
    const selectedHostType = selectedHost.value;

    uploadProgress.value = 20;
    uploadStatus.value = '开始批量上传...';

    const totalItems = itemsToUpload.length;
    let successCount = 0;
    let failureCount = 0;

    // 更新包数据
    const updatedPackage = { ...props.config };

    // 逐个上传项目
    for (let i = 0; i < itemsToUpload.length; i++) {
      const item = itemsToUpload[i];

      try {
        uploadProgress.value = 20 + Math.round(((i + 1) / totalItems) * 70);
        uploadStatus.value = `正在上传: ${getItemName(item)} (${i + 1}/${totalItems})`;

        if (props.uploadType === 'card') {
          await uploadCardInBatch(item, updatedPackage, selectedHostType);
        } else if (props.uploadType === 'encounter') {
          await uploadEncounterInBatch(item, updatedPackage, selectedHostType);
        }

        successCount++;
        addLog(`${getItemName(item)} 上传成功`, 'info');

      } catch (error) {
        console.error(`上传失败: ${getItemName(item)}`, error);
        addLog(`${getItemName(item)} 上传失败: ${error.message}`, 'error');
        failureCount++;
      }

      // 短暂延迟避免过于频繁的请求
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    uploadProgress.value = 100;
    uploadStatus.value = '批量上传完成';

    // 显示结果
    addLog(tMessage('contentPackage.upload.dialog.batchUploadComplete'), 'info');

    emit('confirm', updatedPackage);

    // 消息提示已移至PackageEditor的handleUploadConfirm方法中统一处理

  } catch (error) {
    console.error('批量上传失败:', error);
    addLog(`批量上传失败: ${error.message}`, 'error');
    message.error('批量上传失败');
  } finally {
    isUploading.value = false;
  }
};

// 批量上传卡牌
const uploadCardInBatch = async (card: ContentPackageCard, updatedPackage: any, selectedHostType: ImageHostType) => {
  // 读取卡牌数据
  const cardData = await WorkspaceService.getFileContent(card.filename);
  const parsedCard = JSON.parse(cardData);

  // 导出图片到工作目录
  const result = await CardService.saveCardEnhanced(parsedCard, card.filename.replace('.card', ''), {
    parentPath: '.cards',
    format: exportFormat.value,
    quality: exportQuality.value,
    rotateLandscape: true
  });

  const savedFiles = result.saved_files || {};

  // 检查背面卡牌类型
  const backCardType = parsedCard.back?.type || '';
  const filename = card.filename.toLowerCase();
  let useFixedBackUrl = false;
  let fixedBackUrl = '';

  if (backCardType === '玩家卡背' || filename.includes('player_cardback') || filename.includes('玩家卡背')) {
    useFixedBackUrl = true;
    fixedBackUrl = "https://steamusercontent-a.akamaihd.net/ugc/2342503777940352139/A2D42E7E5C43D045D72CE5CFC907E4F886C8C690/";
  } else if (backCardType === '遭遇卡背' || filename.includes('encounter_cardback') || filename.includes('遭遇卡背')) {
    useFixedBackUrl = true;
    fixedBackUrl = "https://steamusercontent-a.akamaihd.net/ugc/2342503777940351785/F64D8EFB75A9E15446D24343DA0A6EEF5B3E43DB/";
  }

  // 收集需要上传的文件 - 修复：添加所有6个文件
  const filesToUpload = new Map();
  const cleanCardName = card.filename.replace(/.*[\/\\]/, '').replace('.card', '');

  // 正面图片
  if (savedFiles.front_url) {
    filesToUpload.set(savedFiles.front_url, `${cleanCardName}_front`);
  }

  // ✅ 添加：正面原始图片
  if (savedFiles.original_front_url && savedFiles.original_front_url !== savedFiles.front_url) {
    filesToUpload.set(savedFiles.original_front_url, `${cleanCardName}_front_original`);
  }

  // ✅ 添加：正面缩略图
  if (savedFiles.front_thumbnail_url) {
    filesToUpload.set(savedFiles.front_thumbnail_url, `${cleanCardName}_front_thumbnail`);
  }

  // 背面图片 - 只有非固定卡背才上传
  if (!useFixedBackUrl) {
    if (savedFiles.back_url) {
      filesToUpload.set(savedFiles.back_url, `${cleanCardName}_back`);
    }

    // ✅ 添加：背面原始图片
    if (savedFiles.original_back_url && savedFiles.original_back_url !== savedFiles.back_url) {
      filesToUpload.set(savedFiles.original_back_url, `${cleanCardName}_back_original`);
    }

    // ✅ 添加：背面缩略图
    if (savedFiles.back_thumbnail_url) {
      filesToUpload.set(savedFiles.back_thumbnail_url, `${cleanCardName}_back_thumbnail`);
    }
  }

  // 上传所有文件
  const uploadedUrls: Record<string, string> = {};

  if (useFixedBackUrl) {
    uploadedUrls.back_url = fixedBackUrl;
    uploadedUrls.original_back_url = fixedBackUrl;
    uploadedUrls.back_thumbnail_url = fixedBackUrl;
  }

  for (const [filePath, onlineName] of filesToUpload.entries()) {
    try {
      let url: string;

      if (selectedHostType === 'local') {
        const workspacePath = await getWorkspaceAbsolutePath();
        const fullPath = filePath.startsWith('/') || filePath.includes(':')
          ? filePath
          : `${workspacePath}/${filePath}`;
        url = fullPath.includes(':')
          ? `file:///${fullPath.replace(/\\/g, '/')}`
          : `file://${fullPath}`;
      } else {
        const uploadResult = await ImageHostService.smartUpload(
          filePath,
          selectedHostType,
          onlineName
        );
        if (uploadResult.code === 0 && uploadResult.data?.url) {
          url = uploadResult.data.url;
        } else {
          throw new Error(uploadResult.msg || '上传失败');
        }
      }

      // ✅ 修复：根据在线文件名存储所有6个URL
      if (onlineName.includes('_front_original')) {
        uploadedUrls.original_front_url = url;
      } else if (onlineName.includes('_front_thumbnail')) {
        uploadedUrls.front_thumbnail_url = url;
      } else if (onlineName.includes('_front')) {
        uploadedUrls.front_url = url;
      } else if (onlineName.includes('_back_original')) {
        uploadedUrls.original_back_url = url;
      } else if (onlineName.includes('_back_thumbnail')) {
        uploadedUrls.back_thumbnail_url = url;
      } else if (onlineName.includes('_back')) {
        uploadedUrls.back_url = url;
      }

      addLog(`图片上传成功: ${onlineName}`, 'info');
    } catch (error) {
      addLog(`图片上传失败: ${onlineName} - ${error.message}`, 'error');
    }
  }

  // 更新卡牌的云端URL
  const cardIndex = updatedPackage.cards?.findIndex(c => c.filename === card.filename);
  if (cardIndex !== undefined && cardIndex >= 0) {
    const existing = updatedPackage.cards![cardIndex] || {};
    const newUploadedHash = (selectedHostType !== 'local' && parsedCard?.content_hash)
      ? parsedCard.content_hash
      : existing.uploaded_hash;

    updatedPackage.cards![cardIndex] = {
      ...existing,
      front_url: uploadedUrls.front_url,
      back_url: uploadedUrls.back_url,
      original_front_url: uploadedUrls.original_front_url,
      original_back_url: uploadedUrls.original_back_url,
      front_thumbnail_url: uploadedUrls.front_thumbnail_url,
      back_thumbnail_url: uploadedUrls.back_thumbnail_url,
      uploaded_hash: newUploadedHash
    };
  }
};

// 批量上传遭遇组
const uploadEncounterInBatch = async (encounter: EncounterSet, updatedPackage: any, selectedHostType: ImageHostType) => {
  // 检查是否有图标数据
  if (!encounter.base64 && !encounter.relative_path) {
    console.warn(`遭遇组 ${encounter.name} 没有图标数据，跳过上传`);
    return;
  }

  const onlineName = `${encounter.name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}_icon`;

  let imagePath: string;
  if (encounter.relative_path) {
    imagePath = encounter.relative_path;
  } else if (encounter.base64) {
    imagePath = encounter.base64;
  } else {
    return;
  }

  let iconUrl: string;

  if (selectedHostType === 'local') {
    const workspacePath = await getWorkspaceAbsolutePath();
    const fileName = `${onlineName}.png`;
    const fullPath = `${workspacePath}/.encounters/${fileName}`;
    iconUrl = fullPath.includes(':')
      ? `file:///${fullPath.replace(/\\\\/g, '/')}`
      : `file://${fullPath}`;
  } else {
    const result = await ImageHostService.smartUpload(
      imagePath,
      selectedHostType,
      onlineName
    );
    if (result.code === 0 && result.data?.url) {
      iconUrl = result.data.url;
    } else {
      throw new Error(result.msg || '上传失败');
    }
  }

  // 更新遭遇组的icon_url
  const encounterIndex = updatedPackage.encounter_sets?.findIndex(e => e.code === encounter.code);
  if (encounterIndex !== undefined && encounterIndex >= 0) {
    updatedPackage.encounter_sets![encounterIndex] = {
      ...updatedPackage.encounter_sets![encounterIndex],
      icon_url: iconUrl
    };
  }
};

// 上传单个图片
const uploadSingleImage = async (imagePath: string, onlineName: string): Promise<string> => {
  if (selectedHost.value === 'local') {
    // 本地模式：创建本地文件并返回file:///URL
    const workspacePath = await getWorkspaceAbsolutePath();
    const fullPath = imagePath.startsWith('/') || imagePath.includes(':')
      ? imagePath
      : `${workspacePath}/${imagePath}`;
    return fullPath.includes(':')
      ? `file:///${fullPath.replace(/\\\\/g, '/')}`
      : `file://${fullPath}`;
  }

  addLog(tMessage('contentPackage.upload.dialog.imageUploadStart', { filename: onlineName }), 'info');

  const result = await ImageHostService.smartUpload(
    imagePath,
    selectedHost.value,
    onlineName
  );

  if (result.code === 0 && result.data?.url) {
    addLog(tMessage('contentPackage.upload.dialog.imageUploadSuccessUrl', { url: result.data.url }), 'info');
    return result.data.url;
  } else {
    throw new Error(result.msg || '上传失败');
  }
};

// 获取项目名称
const getItemName = (item: any): string => {
  if (props.uploadType === 'card') {
    return item.filename;
  } else if (props.uploadType === 'encounter') {
    return item.name;
  }
  return item.id || JSON.stringify(item);
};

// 确认上传
const handleConfirm = () => {
  if (!isBatch.value && currentItem.value) {
    if (props.uploadType === 'banner') {
      uploadBanner();
    } else {
      uploadSingleItem(currentItem.value);
    }
  } else {
    batchUpload();
  }
};

// 暴露方法给父组件
defineExpose({
  handleConfirm
});

// 监听props变化
watch(() => props.config, (newConfig) => {
  if (newConfig && !cloudinaryConfig.value.cloud_name && !imgbbConfig.value.imgbb_api_key) {
    loadConfig();
  }
}, { immediate: true });

// 组件挂载时加载配置
onMounted(() => {
  loadConfig();
});
</script>

<style scoped>
.universal-upload-dialog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.upload-section {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 1.5rem;
}

.upload-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.upload-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.local-info {
  margin-top: 0.5rem;
}

.quality-setting {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.quality-setting :deep(.n-form-item) {
  margin-bottom: 0;
}

.quality-setting :deep(.n-slider) {
  flex: 1;
  min-width: 200px;
}

.item-preview {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.preview-container {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.banner-preview {
  width: 120px;
  height: 67.5px;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
}

.card-preview {
  flex: 1;
}

.encounter-preview {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.encounter-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.encounter-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.encounter-details {
  flex: 1;
  min-width: 0;
}

.batch-preview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.batch-info {
  /* 样式已定义 */
}

.items-list {
  margin-top: 1rem;
}

.items-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.item-card {
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-status {
  display: flex;
  align-items: center;
}

.encounter-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.encounter-icon {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  background: white;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.encounter-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.no-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
}

.encounter-info {
  flex: 1;
  min-width: 0;
}

.encounter-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.encounter-status {
  display: flex;
  align-items: center;
}

.upload-status {
  margin-top: 0.5rem;
  text-align: center;
}

.log-container {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 0.75rem;
  background: #f8f9fa;
}

.log-item {
  padding: 0.25rem 0;
  font-size: 0.875rem;
  line-height: 1.4;
  word-break: break-all;
}

.log-item:last-child {
  padding-bottom: 0;
}

:deep(.n-radio-group) {
  gap: 1rem;
}

:deep(.n-form-item) {
  margin-bottom: 1rem;
}

:deep(.n-form-item:last-child) {
  margin-bottom: 0;
}
</style>

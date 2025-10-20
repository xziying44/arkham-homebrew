<template>
  <div class="cloud-upload-dialog">
    <!-- 图床选择 -->
    <div class="upload-section">
      <h4>选择图床服务</h4>
      <n-radio-group v-model:value="selectedHost" size="medium">
        <n-radio-button value="cloudinary">Cloudinary</n-radio-button>
        <n-radio-button value="imgbb">ImgBB</n-radio-button>
        <n-radio-button value="local">本地测试</n-radio-button>
      </n-radio-group>
      <div v-if="selectedHost === 'local'" class="local-info">
        <n-alert type="info" size="small">
          <template #icon>
            <n-icon :component="InformationCircleOutline" />
          </template>
          本地测试模式：只导出图片到本地，不上传到云端，使用 file:/// 格式URL
        </n-alert>
      </div>
    </div>

    <!-- Cloudinary 配置 -->
    <div v-if="selectedHost === 'cloudinary'" class="upload-section">
      <h4>Cloudinary 配置</h4>
      <n-form :model="cloudinaryConfig" label-placement="top">
        <n-form-item label="Cloud Name" required>
          <n-input v-model:value="cloudinaryConfig.cloud_name" placeholder="your-cloud-name" clearable />
        </n-form-item>
        <n-form-item label="API Key" required>
          <n-input v-model:value="cloudinaryConfig.api_key" placeholder="your-api-key" type="password"
            show-password-on="click" clearable />
        </n-form-item>
        <n-form-item label="API Secret" required>
          <n-input v-model:value="cloudinaryConfig.api_secret" placeholder="your-api-secret" type="password"
            show-password-on="click" clearable />
        </n-form-item>
        <n-form-item label="文件夹">
          <n-input v-model:value="cloudinaryConfig.folder" placeholder="文件夹名称（可选）" clearable />
        </n-form-item>
      </n-form>
    </div>

    <!-- ImgBB 配置 -->
    <div v-if="selectedHost === 'imgbb'" class="upload-section">
      <h4>ImgBB 配置</h4>
      <n-form :model="imgbbConfig" label-placement="top">
        <n-form-item label="API Key" required>
          <n-input v-model:value="imgbbConfig.imgbb_api_key" placeholder="your-imgbb-api-key" type="password"
            show-password-on="click" clearable />
        </n-form-item>
        <n-form-item label="过期时间（小时）">
          <n-input-number v-model:value="imgbbConfig.imgbb_expiration" :min="0" :max="30 * 24" placeholder="0（永不过期）"
            clearable />
        </n-form-item>
      </n-form>
    </div>

    <!-- 导出格式选择 -->
    <div class="upload-section">
      <h4>导出格式</h4>
      <n-radio-group v-model:value="exportFormat" size="medium">
        <n-radio-button value="JPG">JPG</n-radio-button>
        <n-radio-button value="PNG">PNG</n-radio-button>
      </n-radio-group>
      <div v-if="exportFormat === 'JPG'" class="quality-setting">
        <n-form-item label="图片质量">
          <n-slider v-model:value="exportQuality" :min="1" :max="100"
            :marks="{ 1: '1%', 50: '50%', 95: '95%', 100: '100%' }" :tooltip="false" />
          <n-input-number v-model:value="exportQuality" :min="1" :max="100" size="small"
            style="width: 100px; margin-left: 12px;" />
        </n-form-item>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="isUploading" class="upload-section">
      <h4>上传进度</h4>
      <n-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : 'default'"
        :indicator-placement="'inside'" />
      <div class="upload-status">
        <n-text depth="3">{{ uploadStatus }}</n-text>
      </div>
    </div>

    <!-- 上传日志 -->
    <div v-if="uploadLogs.length > 0" class="upload-section">
      <h4>上传日志</h4>
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
import { CardService } from '@/api/card-service';
import { WorkspaceService } from '@/api/workspace-service';
import { DirectoryService } from '@/api/directory-service';
import { InformationCircleOutline } from '@vicons/ionicons5';
import type { ImageHostType } from '@/api/types';
import type { ContentPackageCard } from '@/types/content-package';

interface Props {
  isBanner?: boolean;
  card?: ContentPackageCard | null;
  config?: any;
  isBatchUpload?: boolean;
}

interface Emits {
  (e: 'confirm', updatedPackage: any): void;
  (e: 'cancel'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const message = useMessage();

// 上传状态
const selectedHost = ref<ImageHostType>('cloudinary');
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

// 计算当前配置
const currentConfig = computed(() => {
  return selectedHost.value === 'cloudinary' ? cloudinaryConfig.value : imgbbConfig.value;
});

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

    // 如果有配置，自动选择对应的图床
    if (config.cloud_name || config.api_key) {
      selectedHost.value = 'cloudinary';
    } else if (config.imgbb_api_key) {
      selectedHost.value = 'imgbb';
    }
  } catch (error) {
    console.error('加载配置失败:', error);
    addLog('加载配置失败: ' + error.message, 'error');
  }
};

// 保存配置
const saveConfig = async () => {
  try {
    // 本地模式不需要保存配置
    if (selectedHost.value === 'local') {
      addLog('本地测试模式，无需保存配置', 'info');
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
    addLog('配置保存成功', 'info');
  } catch (error) {
    console.error('保存配置失败:', error);
    addLog('保存配置失败: ' + error.message, 'error');
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

// 导出图片到工作目录
const exportImageToWorkspace = async (cardData: any, filename: string): Promise<any> => {
  try {
    addLog(`开始导出图片: ${filename}`, 'info');

    // 创建ContentPackage目录
    const packageName = props.isBanner ? 'banner' : 'cards';
    const contentPackageDir = `.${packageName}`;

    // 调用增强版保存卡牌API
    const savedFiles = await CardService.saveCardEnhanced(cardData, filename, {
      parentPath: contentPackageDir,
      format: exportFormat.value,
      quality: exportQuality.value,
      rotateLandscape: true  // 内容包导出时自动旋转横向图片
    });

    addLog(`图片导出成功: ${savedFiles.saved_files.front_url}`, 'info');
    addLog(`图片导出成功: ${savedFiles.saved_files.back_url}`, 'info');
    return savedFiles.saved_files;
  } catch (error) {
    addLog(`图片导出失败: ${error.message}`, 'error');
    throw error;
  }
};

// 上传单个图片
const uploadSingleImage = async (imagePath: string, onlineName: string): Promise<string> => {
  try {
    // 如果是本地模式，直接返回file:///格式URL
    if (selectedHost.value === 'local') {
      // 获取当前工作空间的绝对路径
      const workspacePath = await getWorkspaceAbsolutePath();
      // 构建完整的绝对路径
      const fullPath = imagePath.startsWith('/') || imagePath.includes(':')
        ? imagePath
        : `${workspacePath}/${imagePath}`;
      // 创建file:/// URL，处理Windows路径
      const fileUrl = fullPath.includes(':')
        ? `file:///${fullPath.replace(/\\/g, '/')}`
        : `file://${fullPath}`;
      addLog(`本地模式，使用本地URL: ${fileUrl}`, 'info');
      return fileUrl;
    }

    addLog(`开始上传图片: ${imagePath}`, 'info');

    const result = await ImageHostService.smartUpload(
      imagePath,
      selectedHost.value,
      onlineName
    );

    if (result.code === 0 && result.data?.url) {
      addLog(`图片上传成功: ${result.data.url}`, 'info');
      return result.data.url;
    } else {
      throw new Error(result.msg || '上传失败');
    }
  } catch (error) {
    addLog(`图片上传失败: ${error.message}`, 'error');
    throw error;
  }
};

// 上传封面
const uploadBanner = async () => {
  if (!props.isBanner) return;

  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    uploadStatus.value = '准备上传...';
    uploadLogs.value = [];

    // 验证配置
    if (!validateConfig()) {
      throw new Error('请完善图床配置信息');
    }

    // 保存配置
    await saveConfig();

    uploadProgress.value = 20;
    uploadStatus.value = '配置已保存';

    // 检查是否有base64数据
    if (!props.config?.banner_base64) {
      throw new Error('没有找到封面图片数据');
    }

    uploadProgress.value = 40;
    uploadStatus.value = '准备导出图片...';

    // 创建临时卡牌数据用于生成图片
    const tempCardData = {
      type: '封面制作',
      picture_base64: props.config.banner_base64
    };

    // 导出图片到工作目录
    const savedFiles = await exportImageToWorkspace(tempCardData, 'banner');

    uploadProgress.value = 60;
    uploadStatus.value = '准备上传到云端...';

    // 上传图片
    const imageUrl = await uploadSingleImage(savedFiles.front_url, 'banner');
    const imageBoxUrl = await uploadSingleImage(savedFiles.back_url, 'banner_box');

    uploadProgress.value = 80;
    uploadStatus.value = '更新内容包数据...';

    // 更新内容包的banner_url
    const updatedPackage = {
      ...props.config,
      meta: {
        ...props.config.meta,
        banner_url: imageUrl,
        banner_box_url: imageBoxUrl
      }
    };

    emit('confirm', updatedPackage);
    addLog('封面上传完成', 'info');

    uploadProgress.value = 100;
    uploadStatus.value = '上传成功';

    // 延迟关闭对话框
    setTimeout(() => {
      emit('cancel');
    }, 1000);

  } catch (error) {
    console.error('上传封面失败:', error);
    message.error(`上传失败: ${error.message}`);
  } finally {
    isUploading.value = false;
  }
};

// 上传卡牌
const uploadCard = async () => {
  if (!props.card) return;
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    uploadStatus.value = '准备上传...';
    uploadLogs.value = [];
    // 验证配置
    if (!validateConfig()) {
      throw new Error('请完善图床配置信息');
    }
    // 保存配置
    await saveConfig();
    uploadProgress.value = 20;
    uploadStatus.value = '配置已保存';
    // 读取卡牌数据
    const cardData = await WorkspaceService.getFileContent(props.card.filename);
    const parsedCard = JSON.parse(cardData);
    uploadProgress.value = 40;
    uploadStatus.value = '准备导出图片...';
    // 导出图片到工作目录 - 使用增强版API
    const result = await CardService.saveCardEnhanced(parsedCard, props.card.filename.replace('.card', ''), {
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
    const filename = props.card.filename.toLowerCase();
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
    const filesToUpload = new Map(); // 使用Map去重，key为文件路径，value为在线文件名
    const cleanCardName = props.card.filename.replace(/.*[\/\\]/, '').replace('.card', '');
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
    const cardIndex = updatedPackage.cards?.findIndex(c => c.filename === props.card?.filename);
    if (cardIndex !== undefined && cardIndex >= 0) {
      updatedPackage.cards![cardIndex] = {
        ...updatedPackage.cards![cardIndex],
        front_url: uploadedUrls.front_url,
        back_url: uploadedUrls.back_url,
        original_front_url: uploadedUrls.original_front_url,
        original_back_url: uploadedUrls.original_back_url,
        front_thumbnail_url: uploadedUrls.front_thumbnail_url,
        back_thumbnail_url: uploadedUrls.back_thumbnail_url
      };
    }
    emit('confirm', updatedPackage);
    addLog('卡牌上传完成', 'info');
    uploadProgress.value = 100;
    uploadStatus.value = '上传成功';
    // 延迟关闭对话框
    setTimeout(() => {
      emit('cancel');
    }, 1000);
  } catch (error) {
    console.error('上传卡牌失败:', error);
    message.error(`上传失败: ${error.message}`);
  } finally {
    isUploading.value = false;
  }
};
// 批量上传配置
const batchUploadConfig = async () => {
  if (!props.isBatchUpload) return;
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    uploadStatus.value = '准备批量上传配置...';
    uploadLogs.value = [];
    // 验证配置
    if (!validateConfig()) {
      throw new Error('请完善图床配置信息');
    }
    // 保存配置
    await saveConfig();
    uploadProgress.value = 50;
    uploadStatus.value = '配置已保存';
    // 获取所有v2.0卡牌
    const v2Cards = props.config?.cards?.filter((card: ContentPackageCard) => {
      return true;
    }) || [];
    uploadProgress.value = 80;
    uploadStatus.value = '准备批量上传...';
    // 执行批量上传
    const updatedPackage = {
      ...props.config,
      name: props.config?.name || '',
      path: props.config?.path || '',
      banner_base64: props.config?.banner_base64 || '',
      meta: props.config?.meta || {},
      cards: props.config?.cards || []
    };
    const selectedHostType = selectedHost.value;
    for (let i = 0; i < v2Cards.length; i++) {
      const card = v2Cards[i];
      try {
        // 读取卡牌数据
        const cardData = await WorkspaceService.getFileContent(card.filename);
        const parsedCard = JSON.parse(cardData);
        // 导出图片到工作目录 - 使用增强版API
        const result = await CardService.saveCardEnhanced(parsedCard, card.filename.replace('.card', ''), {
          parentPath: '.cards',
          format: exportFormat.value,
          quality: exportQuality.value,
          rotateLandscape: true
        });
        // 获取返回的文件路径对象
        const savedFiles = result.saved_files || {};
        // 检查背面卡牌类型
        const backCardType = parsedCard.back?.type || '';
        const filename = card.filename.toLowerCase();
        let useFixedBackUrl = false;
        let fixedBackUrl = '';
        if (backCardType === '玩家卡背' || filename.includes('player_cardback') || filename.includes('玩家卡背')) {
          useFixedBackUrl = true;
          fixedBackUrl = "https://steamusercontent-a.akamaihd.net/ugc/2342503777940352139/A2D42E7E5C43D045D72CE5CFC907E4F886C8C690/";
          addLog(`${card.filename}: 检测到玩家卡背，使用预定义URL`, 'info');
        } else if (backCardType === '遭遇卡背' || filename.includes('encounter_cardback') || filename.includes('遭遇卡背')) {
          useFixedBackUrl = true;
          fixedBackUrl = "https://steamusercontent-a.akamaihd.net/ugc/2342503777940351785/F64D8EFB75A9E15446D24343DA0A6EEF5B3E43DB/";
          addLog(`${card.filename}: 检测到遭遇卡背，使用预定义URL`, 'info');
        }
        // 收集需要上传的文件，并去重
        const filesToUpload = new Map();
        const cleanCardName = card.filename.replace(/.*[\/\\]/, '').replace('.card', '');
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
        for (const [filePath, onlineName] of filesToUpload.entries()) {
          try {
            let url: string;

            // 如果是本地模式，使用本地URL
            if (selectedHostType === 'local') {
              const workspacePath = await getWorkspaceAbsolutePath();
              const fullPath = filePath.startsWith('/') || filePath.includes(':')
                ? filePath
                : `${workspacePath}/${filePath}`;
              url = fullPath.includes(':')
                ? `file:///${fullPath.replace(/\\/g, '/')}`
                : `file://${fullPath}`;
              addLog(`本地模式，使用本地URL: ${url}`, 'info');
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
        // 更新卡牌的云端URL
        const cardIndex = updatedPackage.cards?.findIndex(c => c.filename === card.filename);
        if (cardIndex !== undefined && cardIndex >= 0) {
          updatedPackage.cards![cardIndex] = {
            ...updatedPackage.cards![cardIndex],
            front_url: uploadedUrls.front_url,
            back_url: uploadedUrls.back_url,
            original_front_url: uploadedUrls.original_front_url,
            original_back_url: uploadedUrls.original_back_url,
            front_thumbnail_url: uploadedUrls.front_thumbnail_url,
            back_thumbnail_url: uploadedUrls.back_thumbnail_url
          };
        }
        addLog(`卡牌 ${card.filename} 上传成功`, 'info');
      } catch (error) {
        addLog(`卡牌 ${card.filename} 上传失败: ${error.message}`, 'error');
      }
      // 短暂延迟避免过于频繁的请求
      await new Promise(resolve => setTimeout(resolve, 300));
    }
    uploadProgress.value = 100;
    uploadStatus.value = '批量上传完成';
    emit('confirm', updatedPackage);
    addLog('批量上传完成', 'info');
    // 延迟关闭对话框
    setTimeout(() => {
      emit('cancel');
    }, 1000);
  } catch (error) {
    console.error('批量上传失败:', error);
    message.error(`批量上传失败: ${error.message}`);
    addLog(`批量上传失败: ${error.message}`, 'error');
  } finally {
    isUploading.value = false;
  }
};

// 确认上传
const handleConfirm = () => {
  if (props.isBatchUpload) {
    batchUploadConfig();
  } else if (props.isBanner) {
    uploadBanner();
  } else if (props.card) {
    uploadCard();
  } else {
    // 如果没有明确指定，默认按批量上传处理
    batchUploadConfig();
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
.cloud-upload-dialog {
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
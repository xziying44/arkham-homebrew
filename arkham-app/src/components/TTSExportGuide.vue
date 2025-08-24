<template>
    <div class="tts-export-guide">
        <div class="guide-header">
            <n-button text @click="handleBack" class="back-button">
                <template #icon>
                    <n-icon :component="ArrowBackOutline" />
                </template>
                {{ t('deckBuilder.actions.back') }}
            </n-button>
        </div>

        <div class="guide-content">
            <div class="progress-bar">
                <div class="progress-item" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                    <div class="step-number">{{ t('deckBuilder.ttsExport.steps.step1.number') }}</div>
                    <div class="step-label">{{ t('deckBuilder.ttsExport.steps.step1.title') }}</div>
                </div>
                <div class="progress-line" :class="{ completed: currentStep > 1 }"></div>
                <div class="progress-item" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                    <div class="step-number">{{ t('deckBuilder.ttsExport.steps.step2.number') }}</div>
                    <div class="step-label">{{ t('deckBuilder.ttsExport.steps.step2.title') }}</div>
                </div>
                <div class="progress-line" :class="{ completed: currentStep > 2 }"></div>
                <div class="progress-item" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
                    <div class="step-number">{{ t('deckBuilder.ttsExport.steps.step3.number') }}</div>
                    <div class="step-label">{{ t('deckBuilder.ttsExport.steps.step3.title') }}</div>
                </div>
            </div>

            <div class="step-content">
                <!-- 第一步：导出图片 -->
                <div v-if="currentStep === 1" class="step-panel">
                    <div class="step-header">
                        <h3>{{ t('deckBuilder.ttsExport.steps.step1.header') }}</h3>
                        <p class="step-description">{{ t('deckBuilder.ttsExport.steps.step1.description') }}</p>
                    </div>

                    <div class="export-section">
                        <n-card :title="t('deckBuilder.ttsExport.export.title')" class="export-card">
                            <div class="export-options">
                                <n-form-item :label="t('deckBuilder.ttsExport.export.format')">
                                    <n-select v-model:value="exportFormat" :options="formatOptions"
                                        :placeholder="t('deckBuilder.ttsExport.export.formatPlaceholder')" />
                                </n-form-item>
                                <n-form-item :label="t('deckBuilder.ttsExport.export.quality')" v-if="exportFormat === 'JPG'">
                                    <n-slider v-model:value="imageQuality" :min="60" :max="100" :step="10"
                                        :marks="qualityMarks" />
                                </n-form-item>
                            </div>

                            <div class="export-actions">
                                <n-space>
                                    <n-button type="primary" size="large" @click="exportImages" :loading="exporting"
                                        :disabled="!deck.frontCards.length && !deck.backCards.length">
                                        <template #icon>
                                            <n-icon :component="DownloadOutline" />
                                        </template>
                                        {{ exporting ? t('deckBuilder.ttsExport.export.exporting') : t('deckBuilder.ttsExport.export.startExport') }}
                                    </n-button>

                                    <n-button size="large" @click="openExportDirectory"
                                        :disabled="!exportResult?.success">
                                        <template #icon>
                                            <n-icon :component="FolderOpenOutline" />
                                        </template>
                                        {{ t('deckBuilder.actions.openDirectory') }}
                                    </n-button>
                                </n-space>
                            </div>

                            <div v-if="exportResult" class="export-result">
                                <n-alert :type="exportResult.success ? 'success' : 'error'" :title="exportResult.title">
                                    {{ exportResult.message }}
                                    <div v-if="exportResult.success && exportResult.paths" class="exported-files">
                                        <p><strong>{{ t('deckBuilder.ttsExport.export.exportedFiles') }}</strong></p>
                                        <ul>
                                            <li v-for="path in exportResult.paths" :key="path">{{ path }}</li>
                                        </ul>
                                    </div>
                                </n-alert>
                            </div>
                        </n-card>
                    </div>

                    <div class="step-actions step-actions-first">
                        <n-button type="primary" @click="nextStep" :disabled="!exportResult?.success" size="large">
                            {{ t('deckBuilder.ttsExport.navigation.nextUpload') }}
                            <template #icon>
                                <n-icon :component="ChevronForwardOutline" />
                            </template>
                        </n-button>
                    </div>
                </div>

                <!-- 第二步：上传图床 -->
                <div v-if="currentStep === 2" class="step-panel">
                    <div class="step-header">
                        <h3>{{ t('deckBuilder.ttsExport.steps.step2.header') }}</h3>
                        <p class="step-description">{{ t('deckBuilder.ttsExport.steps.step2.description') }}</p>
                    </div>

                    <div class="upload-section">
                        <n-card :title="t('deckBuilder.ttsExport.imageHost.title')" class="upload-card">
                            <div class="image-host-options">
                                <div 
                                    class="host-option" 
                                    :class="{ selected: imageHostType === 'steam' }"
                                    @click="selectImageHost('steam')"
                                >
                                    <div class="host-content">
                                        <div class="host-icon">🎮</div>
                                        <div class="host-info">
                                            <div class="host-name">{{ t('deckBuilder.ttsExport.imageHost.steam.name') }}</div>
                                            <div class="host-desc">{{ t('deckBuilder.ttsExport.imageHost.steam.description') }}</div>
                                        </div>
                                        <div class="host-check">
                                            <n-icon v-if="imageHostType === 'steam'" :component="CheckmarkCircleOutline" />
                                        </div>
                                    </div>
                                </div>
                                
                                <div 
                                    class="host-option" 
                                    :class="{ selected: imageHostType === 'github' }"
                                    @click="selectImageHost('github')"
                                >
                                    <div class="host-content">
                                        <div class="host-icon">📦</div>
                                        <div class="host-info">
                                            <div class="host-name">{{ t('deckBuilder.ttsExport.imageHost.github.name') }}</div>
                                            <div class="host-desc">{{ t('deckBuilder.ttsExport.imageHost.github.description') }}</div>
                                        </div>
                                        <div class="host-check">
                                            <n-icon v-if="imageHostType === 'github'" :component="CheckmarkCircleOutline" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </n-card>

                        <!-- Steam 云存储选项 -->
                        <n-card v-if="imageHostType === 'steam'" :title="t('deckBuilder.ttsExport.imageHost.steam.name')" class="upload-card">
                            <div class="steam-upload">
                                <n-alert type="info" :title="t('common.instructions')">
                                    {{ t('deckBuilder.ttsExport.imageHost.steam.instruction') }}
                                    <template #action>
                                        <n-button text type="primary" @click="openSteamWorkshop">
                                            {{ t('deckBuilder.actions.openSteamWorkshop') }}
                                        </n-button>
                                    </template>
                                </n-alert>

                                <div class="url-inputs">
                                    <n-form-item :label="t('deckBuilder.ttsExport.imageHost.urls.frontImage')" required>
                                        <n-input-group>
                                            <n-input v-model:value="ttsInfo.frontImageUrl" :placeholder="t('deckBuilder.ttsExport.imageHost.urls.frontPlaceholder')"
                                                clearable />
                                            <n-button @click="copyToClipboard(ttsInfo.frontImageUrl, t('deckBuilder.ttsExport.imageHost.urls.frontImage'))" 
                                                :disabled="!ttsInfo.frontImageUrl">
                                                <template #icon>
                                                    <n-icon :component="CopyOutline" />
                                                </template>
                                            </n-button>
                                        </n-input-group>
                                    </n-form-item>
                                    <n-form-item :label="t('deckBuilder.ttsExport.imageHost.urls.backImage')" required>
                                        <n-input-group>
                                            <n-input v-model:value="ttsInfo.backImageUrl" :placeholder="t('deckBuilder.ttsExport.imageHost.urls.backPlaceholder')"
                                                clearable />
                                            <n-button @click="copyToClipboard(ttsInfo.backImageUrl, t('deckBuilder.ttsExport.imageHost.urls.backImage'))" 
                                                :disabled="!ttsInfo.backImageUrl">
                                                <template #icon>
                                                    <n-icon :component="CopyOutline" />
                                                </template>
                                            </n-button>
                                        </n-input-group>
                                    </n-form-item>
                                </div>
                            </div>
                        </n-card>

                        <!-- GitHub图床选项 -->
                        <n-card v-if="imageHostType === 'github'" :title="t('deckBuilder.ttsExport.imageHost.github.name')" class="upload-card">
                            <div class="github-upload">
                                <!-- GitHub状态检查中 -->
                                <div v-if="githubChecking" class="github-status">
                                    <n-alert type="info" :title="t('deckBuilder.ttsExport.imageHost.github.checking')">
                                        <div class="checking-spinner">
                                            <n-icon :component="EllipsisHorizontalOutline" class="rotating" />
                                            {{ t('deckBuilder.ttsExport.imageHost.github.verifying') }}
                                        </div>
                                    </n-alert>
                                </div>

                                <!-- GitHub未配置 -->
                                <div v-else-if="!githubStatus.is_logged_in" class="github-status">
                                    <n-alert type="warning" title="GitHub未配置">
                                        {{ t('deckBuilder.ttsExport.imageHost.github.notConfigured') }}
                                        <template #action>
                                            <n-button text type="primary" @click="$emit('openSettings')">
                                                {{ t('common.goToSettings') }}
                                            </n-button>
                                        </template>
                                    </n-alert>
                                </div>

                                <!-- GitHub配置已完成 -->
                                <div v-else class="github-ready">
                                    <div class="github-status-info">
                                        <n-alert type="success" title="GitHub已配置">
                                            {{ t('deckBuilder.ttsExport.imageHost.github.configured', { username: githubStatus.username }) }}
                                        </n-alert>
                                    </div>

                                    <div class="url-display">
                                        <n-form-item :label="t('deckBuilder.ttsExport.imageHost.urls.frontImage')">
                                            <n-input-group>
                                                <n-input :value="ttsInfo.frontImageUrl || t('deckBuilder.ttsExport.imageHost.urls.autoGenerated')" readonly
                                                    :placeholder="t('deckBuilder.ttsExport.imageHost.urls.autoGenerated')" />
                                                <n-button @click="copyToClipboard(ttsInfo.frontImageUrl, t('deckBuilder.ttsExport.imageHost.urls.frontImage'))" 
                                                    :disabled="!ttsInfo.frontImageUrl">
                                                    <template #icon>
                                                        <n-icon :component="CopyOutline" />
                                                    </template>
                                                </n-button>
                                            </n-input-group>
                                        </n-form-item>
                                        <n-form-item :label="t('deckBuilder.ttsExport.imageHost.urls.backImage')">
                                            <n-input-group>
                                                <n-input :value="ttsInfo.backImageUrl || t('deckBuilder.ttsExport.imageHost.urls.autoGenerated')" readonly
                                                    :placeholder="t('deckBuilder.ttsExport.imageHost.urls.autoGenerated')" />
                                                <n-button @click="copyToClipboard(ttsInfo.backImageUrl, t('deckBuilder.ttsExport.imageHost.urls.backImage'))" 
                                                    :disabled="!ttsInfo.backImageUrl">
                                                    <template #icon>
                                                        <n-icon :component="CopyOutline" />
                                                    </template>
                                                </n-button>
                                            </n-input-group>
                                        </n-form-item>
                                    </div>

                                    <!-- 上传进度显示 -->
                                    <div v-if="uploading" class="upload-progress">
                                        <n-card :title="t('deckBuilder.ttsExport.upload.uploadingTitle')" class="progress-card">
                                            <div class="progress-item" v-for="(item, index) in uploadProgress" :key="index">
                                                <div class="progress-info">
                                                    <span class="file-name">{{ item.name }}</span>
                                                    <span class="file-status" :class="item.status">
                                                        <n-icon v-if="item.status === 'uploading'" :component="CloudUploadOutline" class="rotating" />
                                                        <n-icon v-else-if="item.status === 'success'" :component="CheckmarkCircleOutline" />
                                                        <n-icon v-else-if="item.status === 'error'" :component="CloseCircleOutline" />
                                                        <n-icon v-else :component="EllipsisHorizontalOutline" />
                                                    </span>
                                                </div>
                                                <n-progress
                                                    type="line"
                                                    :percentage="item.progress"
                                                    :status="item.status === 'error' ? 'error' : item.status === 'success' ? 'success' : 'info'"
                                                    :show-indicator="false"
                                                />
                                            </div>
                                        </n-card>
                                    </div>

                                    <div class="upload-actions">
                                        <n-button type="primary" size="large" @click="uploadToGitHub"
                                            :loading="uploading" :disabled="!exportResult?.success">
                                            <template #icon>
                                                <n-icon :component="CloudUploadOutline" />
                                            </template>
                                            {{ uploading ? t('deckBuilder.ttsExport.upload.uploading') : t('deckBuilder.actions.uploadToGithub') }}
                                        </n-button>
                                    </div>

                                    <div v-if="uploadResult" class="upload-result">
                                        <n-alert :type="uploadResult.success ? 'success' : 'error'"
                                            :title="uploadResult.title">
                                            {{ uploadResult.message }}
                                            <div v-if="uploadResult.success && uploadResult.urls" class="uploaded-info">
                                                <p><strong>{{ t('deckBuilder.ttsExport.upload.uploadSuccess', { count: uploadResult.urls.length }) }}</strong></p>
                                                <p>{{ t('deckBuilder.ttsExport.upload.urlsGenerated') }}</p>
                                            </div>
                                        </n-alert>
                                    </div>
                                </div>
                            </div>
                        </n-card>
                    </div>

                    <div class="step-actions">
                        <n-button @click="prevStep" size="large">
                            <template #icon>
                                <n-icon :component="ChevronBackOutline" />
                            </template>
                            {{ t('deckBuilder.actions.prev') }}
                        </n-button>
                        <n-button type="primary" @click="nextStep" :disabled="!isStep2Valid" size="large">
                            {{ t('deckBuilder.ttsExport.navigation.nextGenerate') }}
                            <template #icon>
                                <n-icon :component="ChevronForwardOutline" />
                            </template>
                        </n-button>
                    </div>
                </div>

                <!-- 第三步：生成TTS文件 -->
                <div v-if="currentStep === 3" class="step-panel">
                    <div class="step-header">
                        <h3>{{ t('deckBuilder.ttsExport.steps.step3.header') }}</h3>
                        <p class="step-description">{{ t('deckBuilder.ttsExport.steps.step3.description') }}</p>
                    </div>

                    <div class="generate-section">
                        <n-card :title="t('deckBuilder.ttsExport.generate.title')" class="generate-card">
                            <div class="tts-config">
                                <n-descriptions bordered :column="2">
                                    <n-descriptions-item :label="t('deckBuilder.ttsExport.generate.deckName')">
                                        {{ deck.name }}
                                    </n-descriptions-item>
                                    <n-descriptions-item :label="t('deckBuilder.ttsExport.generate.cardCount')">
                                        {{ cardCount }}
                                    </n-descriptions-item>
                                    <n-descriptions-item :label="t('deckBuilder.ttsExport.generate.frontImageUrl')">
                                        <n-ellipsis style="max-width: 200px;">
                                            {{ ttsInfo.frontImageUrl }}
                                        </n-ellipsis>
                                    </n-descriptions-item>
                                    <n-descriptions-item :label="t('deckBuilder.ttsExport.generate.backImageUrl')">
                                        <n-ellipsis style="max-width: 200px;">
                                            {{ ttsInfo.backImageUrl }}
                                        </n-ellipsis>
                                    </n-descriptions-item>
                                </n-descriptions>
                            </div>

                            <div class="tts-info">
                                <n-alert type="info" :title="t('deckBuilder.ttsExport.generate.description')" closable>
                                    {{ t('deckBuilder.ttsExport.generate.description') }}<br>
                                    <strong>{{ t('deckBuilder.ttsExport.generate.location') }}</strong>
                                    <br><br>
                                    {{ t('deckBuilder.ttsExport.generate.includes') }}
                                    <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem;">
                                        <li>{{ t('deckBuilder.ttsExport.generate.includesList.config') }}</li>
                                        <li>{{ t('deckBuilder.ttsExport.generate.includesList.thumbnail') }}</li>
                                    </ul>
                                </n-alert>
                            </div>
                        </n-card>
                    </div>

                    <div class="step-actions">
                        <n-button @click="prevStep" size="large">
                            <template #icon>
                                <n-icon :component="ChevronBackOutline" />
                            </template>
                            {{ t('deckBuilder.actions.prev') }}
                        </n-button>
                        <n-button type="primary" @click="generateTTSFile" :loading="generating" size="large">
                            <template #icon>
                                <n-icon :component="RocketOutline" />
                            </template>
                            {{ generating ? t('deckBuilder.ttsExport.generate.generating') : t('deckBuilder.actions.generateTTS') }}
                        </n-button>
                    </div>

                    <!-- 生成结果 -->
                    <div v-if="generateResult" class="generate-result">
                        <n-result :status="generateResult.success ? 'success' : 'error'" :title="generateResult.title"
                            :description="generateResult.message">
                            <template v-if="generateResult.success" #footer>
                                <n-space>
                                    <n-button type="primary" @click="handleBack">
                                        {{ t('deckBuilder.ttsExport.generate.complete') }}
                                    </n-button>
                                </n-space>
                            </template>
                            <template v-else #footer>
                                <n-space>
                                    <n-button type="primary" @click="generateTTSFile" :loading="generating">
                                        {{ t('deckBuilder.ttsExport.generate.retry') }}
                                    </n-button>
                                    <n-button @click="prevStep">
                                        {{ t('deckBuilder.ttsExport.generate.backToStep') }}
                                    </n-button>
                                </n-space>
                            </template>
                        </n-result>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
    ArrowBackOutline,
    DownloadOutline,
    ChevronForwardOutline,
    ChevronBackOutline,
    CloudUploadOutline,
    RocketOutline,
    FolderOpenOutline,
    CheckmarkCircleOutline,
    CloseCircleOutline,
    EllipsisHorizontalOutline,
    CopyOutline
} from '@vicons/ionicons5';
import { TtsExportService, GitHubService, ConfigService } from '@/api';
import type { GitHubStatus } from '@/api/types';

const { t } = useI18n();

interface DeckCard {
    index: number;
    type: 'card' | 'cardback' | 'image';
    path: string;
}

interface TTSInfo {
    frontImageUrl?: string;
    backImageUrl?: string;
    imageSource?: 'steam' | 'github';
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

interface Props {
    deck: DeckFile;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'back'): void;
    (e: 'update:deck', deck: DeckFile): void;
    (e: 'openSettings'): void;
}

const emit = defineEmits<Emits>();

const message = useMessage();

// 步骤状态
const currentStep = ref(1);

// 第一步：导出图片
const exporting = ref(false);
const exportFormat = ref<'JPG' | 'PNG'>('JPG');
const imageQuality = ref(90);
const exportResult = ref<{
    success: boolean;
    title: string;
    message: string;
    paths?: string[];
} | null>(null);

// 格式选项（支持多语言）
const formatOptions = computed(() => [
    { label: 'JPG (' + t('common.recommended') + ')', value: 'JPG' },
    { label: 'PNG', value: 'PNG' },
]);

// 质量标记（支持多语言）
const qualityMarks = computed(() => ({
    60: t('deckBuilder.ttsExport.export.qualityMarks.60'),
    70: t('deckBuilder.ttsExport.export.qualityMarks.70'),
    80: t('deckBuilder.ttsExport.export.qualityMarks.80'),
    90: t('deckBuilder.ttsExport.export.qualityMarks.90'),
    100: t('deckBuilder.ttsExport.export.qualityMarks.100')
}));

// 第二步：上传图床
const imageHostType = ref<'steam' | 'github'>('steam');
const uploading = ref(false);
const ttsInfo = ref<TTSInfo>({
    frontImageUrl: props.deck.ttsInfo?.frontImageUrl || '',
    backImageUrl: props.deck.ttsInfo?.backImageUrl || '',
    imageSource: props.deck.ttsInfo?.imageSource || 'steam'
});

// 上传进度
const uploadProgress = ref<Array<{
    name: string;
    progress: number;
    status: 'waiting' | 'uploading' | 'success' | 'error';
}>>([]);

// GitHub相关状态
const githubChecking = ref(false);
const githubStatus = ref<GitHubStatus>({
    is_logged_in: false,
    username: null,
    has_config: false,
    last_error: ''
});

const uploadResult = ref<{
    success: boolean;
    title: string;
    message: string;
    urls?: string[];
} | null>(null);

const isStep2Valid = computed(() => {
    return ttsInfo.value.frontImageUrl && ttsInfo.value.backImageUrl;
});

// 第三步：生成TTS文件
const generating = ref(false);
const generateResult = ref<{
    success: boolean;
    title: string;
    message: string;
} | null>(null);

// 卡牌数量计算 - 取正面和背面数量的最大值
const cardCount = computed(() => {
    return Math.max(props.deck.frontCards.length, props.deck.backCards.length);
});

// 组件挂载时检查GitHub状态
onMounted(async () => {
    await checkGitHubStatus();
});

// 检查GitHub状态并尝试静默登录
const checkGitHubStatus = async () => {
    githubChecking.value = true;
    
    try {
        // 先检查当前状态
        let status = await GitHubService.getStatus();
        githubStatus.value = status.data.status;
        
        // 如果未登录，尝试静默登录
        if (!githubStatus.value.is_logged_in) {
            await attemptSilentLogin();
        }
    } catch (error: any) {
        console.warn('获取GitHub状态失败:', error);
        githubStatus.value = {
            is_logged_in: false,
            username: null,
            has_config: false,
            last_error: error?.message || '检查GitHub状态失败'
        };
    } finally {
        githubChecking.value = false;
    }
};

// 尝试静默登录
const attemptSilentLogin = async () => {
    try {
        // 先获取配置中的GitHub token
        const configData = await ConfigService.getConfig();
        const githubToken = configData.github_token;
        
        if (githubToken && githubToken.trim()) {
            console.log('发现GitHub Token，尝试静默登录...');
            
            // 尝试使用已有token登录
            await GitHubService.login(githubToken.trim());
            
            // 登录成功后重新获取状态
            const status = await GitHubService.getStatus();
            githubStatus.value = status.data.status;
            
            if (githubStatus.value.is_logged_in) {
                console.log('GitHub静默登录成功，用户:', githubStatus.value.username);
            }
        } else {
            console.log('未找到GitHub Token，跳过静默登录');
        }
    } catch (error: any) {
        console.warn('GitHub静默登录失败:', error);
        // 静默登录失败不需要显示错误，保持原有的未登录状态即可
    }
};

// 选择图床服务
const selectImageHost = (type: 'steam' | 'github') => {
    imageHostType.value = type;
    uploadResult.value = null; // 清空之前的上传结果
    
    // 如果选择GitHub图床且当前未登录，重新检查状态
    if (type === 'github' && !githubStatus.value.is_logged_in) {
        checkGitHubStatus();
    }
};

// 复制到剪贴板
const copyToClipboard = async (text: string, label: string) => {
    if (!text) {
        message.warning(t('deckBuilder.messages.urlEmpty', { label }));
        return;
    }
    
    try {
        await navigator.clipboard.writeText(text);
        message.success(t('deckBuilder.messages.urlCopied', { label }));
    } catch (error) {
        // 如果 Clipboard API 不支持，使用传统方法
        try {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            message.success(t('deckBuilder.messages.urlCopied', { label }));
        } catch (fallbackError) {
            message.error(t('deckBuilder.messages.copyFailed'));
            console.error('Copy failed:', fallbackError);
        }
    }
};

// 步骤导航
const nextStep = () => {
    if (currentStep.value < 3) {
        currentStep.value++;
        saveTTSInfo();
    }
};

const prevStep = () => {
    if (currentStep.value > 1) {
        currentStep.value--;
    }
};

// 返回编辑
const handleBack = () => {
    saveTTSInfo();
    emit('back');
};

// 保存TTS信息到牌库
const saveTTSInfo = () => {
    const updatedDeck = {
        ...props.deck,
        ttsInfo: {
            ...ttsInfo.value,
            imageSource: imageHostType.value,
            lastExportTime: new Date().toISOString()
        }
    };
    emit('update:deck', updatedDeck);
};

// 第一步：导出图片（使用真实API）
const exportImages = async () => {
    exporting.value = true;
    exportResult.value = null;

    try {
        // 使用牌库文件名作为导出文件名
        const deckName = props.deck.name + '.deck';

        await TtsExportService.exportDeckImage(
            deckName,
            exportFormat.value,
            exportFormat.value === 'JPG' ? imageQuality.value : undefined
        );

        exportResult.value = {
            success: true,
            title: t('deckBuilder.messages.tts.exportSuccess.title'),
            message: t('deckBuilder.messages.tts.exportSuccess.message'),
            paths: [
                `${props.deck.name}_front.${exportFormat.value.toLowerCase()}`,
                `${props.deck.name}_back.${exportFormat.value.toLowerCase()}`
            ]
        };

        ttsInfo.value.exportPath = 'DeckBuilder';
        message.success(t('deckBuilder.messages.exportSuccess'));
    } catch (error: any) {
        exportResult.value = {
            success: false,
            title: t('deckBuilder.messages.tts.exportFailed.title'),
            message: t('deckBuilder.messages.tts.exportFailed.message')
        };
        message.error(t('deckBuilder.messages.exportFailed', { error: error?.message || t('common.unknownError') }));
        console.error('Export error:', error);
    } finally {
        exporting.value = false;
    }
};

// 打开导出目录（使用真实API）
const openExportDirectory = async () => {
    try {
        await TtsExportService.openDirectory('DeckBuilder');
        message.success(t('deckBuilder.messages.directoryOpened'));
    } catch (error: any) {
        message.error(t('deckBuilder.messages.directoryOpenFailed', { error: error?.message || t('common.unknownError') }));
        console.error('Open directory error:', error);
    }
};

// 第二步：打开Steam Workshop
const openSteamWorkshop = () => {
    window.open('https://steamcommunity.com/workshop/', '_blank');
};

// 第二步：上传到GitHub图床 (增强版本)
const uploadToGitHub = async () => {
    uploading.value = true;
    uploadResult.value = null;
    
    // 初始化进度（支持多语言）
    uploadProgress.value = [
        { name: t('deckBuilder.ttsExport.upload.frontImage'), progress: 0, status: 'waiting' },
        { name: t('deckBuilder.ttsExport.upload.backImage'), progress: 0, status: 'waiting' }
    ];

    try {
        // 重新检查GitHub状态
        await checkGitHubStatus();

        if (!githubStatus.value.is_logged_in) {
            throw new Error(t('deckBuilder.ttsExport.imageHost.github.notConfigured'));
        }

        if (!exportResult.value?.success || !exportResult.value.paths) {
            throw new Error(t('common.exportFirstTip'));
        }

        const uploadedUrls: string[] = [];
        const exportDir = 'DeckBuilder';

        // 上传正面图片
        uploadProgress.value[0].status = 'uploading';
        uploadProgress.value[0].progress = 20;
        
        const frontImagePath = `${exportDir}/${exportResult.value.paths[0]}`;
        try {
            uploadProgress.value[0].progress = 50;
            const frontUpload = await GitHubService.uploadImage(frontImagePath);
            ttsInfo.value.frontImageUrl = frontUpload.data.url;
            uploadedUrls.push(frontUpload.data.url);
            
            uploadProgress.value[0].progress = 100;
            uploadProgress.value[0].status = 'success';
        } catch (error: any) {
            uploadProgress.value[0].status = 'error';
            throw new Error(t('common.uploadFrontImageFailed', { error: error?.message || t('common.unknownError') }));
        }

        // 上传背面图片
        uploadProgress.value[1].status = 'uploading';
        uploadProgress.value[1].progress = 20;
        
        const backImagePath = `${exportDir}/${exportResult.value.paths[1]}`;
        try {
            uploadProgress.value[1].progress = 50;
            const backUpload = await GitHubService.uploadImage(backImagePath);
            ttsInfo.value.backImageUrl = backUpload.data.url;
            uploadedUrls.push(backUpload.data.url);
            
            uploadProgress.value[1].progress = 100;
            uploadProgress.value[1].status = 'success';
        } catch (error: any) {
            uploadProgress.value[1].status = 'error';
            throw new Error(t('common.uploadBackImageFailed', { error: error?.message || t('common.unknownError') }));
        }

        uploadResult.value = {
            success: true,
            title: t('deckBuilder.messages.tts.uploadSuccess.title'),
            message: t('deckBuilder.messages.tts.uploadSuccess.message'),
            urls: uploadedUrls
        };

        // 更新图床类型
        imageHostType.value = 'github';
        ttsInfo.value.imageSource = 'github';

        message.success(t('deckBuilder.messages.uploadSuccess'));
    } catch (error: any) {
        uploadResult.value = {
            success: false,
            title: t('deckBuilder.messages.tts.uploadFailed.title'),
            message: error?.message || t('deckBuilder.messages.tts.uploadFailed.message')
        };
        message.error(t('deckBuilder.messages.uploadFailed', { error: error?.message || t('common.unknownError') }));
        console.error('GitHub upload error:', error);
    } finally {
        uploading.value = false;
        // 清空进度状态 (延迟清空以便用户看到结果)
        setTimeout(() => {
            uploadProgress.value = [];
        }, 2000);
    }
};

// 第三步：生成TTS文件（使用真实API）
const generateTTSFile = async () => {
    generating.value = true;
    generateResult.value = null;

    try {
        // 验证必要的参数
        if (!ttsInfo.value.frontImageUrl || !ttsInfo.value.backImageUrl) {
            throw new Error(t('common.completeStepsTip'));
        }

        // 构建牌库文件名
        const deckName = props.deck.name.endsWith('.deck') 
            ? props.deck.name 
            : props.deck.name + '.deck';

        // 调用TTS导出API
        await TtsExportService.exportTtsItem(
            deckName,
            ttsInfo.value.frontImageUrl,
            ttsInfo.value.backImageUrl
        );

        generateResult.value = {
            success: true,
            title: t('deckBuilder.messages.tts.generateSuccess.title'),
            message: t('deckBuilder.messages.tts.generateSuccess.message', { name: props.deck.name })
        };

        // 更新牌库的TTS信息
        ttsInfo.value.lastExportTime = new Date().toISOString();
        saveTTSInfo();

        message.success(t('deckBuilder.messages.generateSuccess'));
    } catch (error: any) {
        let errorMessage = t('deckBuilder.messages.tts.generateFailed.message');
        
        // 根据错误码提供更详细的错误信息
        if (error.code) {
            switch (error.code) {
                case 11001:
                    errorMessage = t('common.ttsErrors.11001');
                    break;
                case 11002:
                    errorMessage = t('common.ttsErrors.11002');
                    break;
                case 11003:
                    errorMessage = t('common.ttsErrors.11003');
                    break;
                case 11004:
                    errorMessage = t('common.ttsErrors.11004');
                    break;
                case 11005:
                    errorMessage = t('common.ttsErrors.11005');
                    break;
                default:
                    errorMessage = error.message || t('common.unknownError');
            }
        } else if (error.message) {
            errorMessage = error.message;
        }

        generateResult.value = {
            success: false,
            title: t('deckBuilder.messages.tts.generateFailed.title'),
            message: errorMessage
        };
        
        message.error(t('deckBuilder.messages.generateFailed', { error: errorMessage }));
        console.error('TTS generation error:', error);
    } finally {
        generating.value = false;
    }
};

// 监听图床类型变化，重置上传结果
watch(() => imageHostType.value, () => {
    uploadResult.value = null;
});

// 初始化TTS信息
watch(() => props.deck.ttsInfo, (newInfo) => {
    if (newInfo) {
        ttsInfo.value = { ...newInfo };
        imageHostType.value = newInfo.imageSource || 'steam';
    }
}, { immediate: true });
</script>

<style scoped>
.tts-export-guide {
    flex: 1;
    background: #f8f9fa;
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.guide-header {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.back-button {
    color: white !important;
    font-size: 0.9rem;
}

.guide-content {
    flex: 1;
    padding: 2rem;
    min-height: 0;
    overflow-y: auto;
}

/* 进度条样式 */
.progress-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.progress-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    z-index: 2;
}

.step-number {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #e9ecef;
    color: #6c757d;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.progress-item.active .step-number {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.1);
}

.progress-item.completed .step-number {
    background: #28a745;
    color: white;
}

.step-label {
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.9rem;
}

.progress-line {
    width: 120px;
    height: 3px;
    background: #e9ecef;
    margin: 0 1rem;
    transition: all 0.3s ease;
    position: relative;
    z-index: 1;
}

.progress-line.completed {
    background: #28a745;
}

/* 步骤面板样式 */
.step-panel {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.step-header {
    margin-bottom: 2rem;
    text-align: center;
}

.step-header h3 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 1.5rem;
}

.step-description {
    color: #6c757d;
    font-size: 1rem;
    margin: 0;
    line-height: 1.6;
}

.step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e9ecef;
}

/* 第一步的按钮布局 - 只有下一步按钮，居右显示 */
.step-actions-first {
    justify-content: flex-end;
}

/* 导出部分样式 */
.export-section,
.upload-section,
.generate-section {
    margin-bottom: 2rem;
}

.export-card,
.upload-card,
.generate-card {
    margin-bottom: 1.5rem;
}

.export-options {
    display: grid;
    gap: 1rem;
    margin-bottom: 2rem;
}

.export-actions,
.upload-actions {
    text-align: center;
}

.export-result,
.upload-result {
    margin-top: 1.5rem;
}

.exported-files ul {
    margin: 0.5rem 0 0 0;
    padding-left: 1.5rem;
}

.exported-files li {
    font-family: monospace;
    font-size: 0.9rem;
    color: #495057;
    margin-bottom: 0.25rem;
}

.uploaded-info {
    margin: 0.5rem 0 0 0;
}

.uploaded-info p {
    margin: 0.25rem 0;
    color: #495057;
}

/* 图床选择样式优化 - 自定义选择样式 */
.image-host-options {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.host-option {
    cursor: pointer;
    transition: all 0.2s ease;
    border-radius: 8px;
    overflow: hidden;
}

.host-option:hover .host-content {
    border-color: #667eea;
    background-color: #f8f9ff;
}

.host-option.selected .host-content {
    border-color: #667eea;
    background: linear-gradient(135deg, #f8f9ff 0%, #e8edff 100%);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.host-content {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.5rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    transition: all 0.2s ease;
    position: relative;
}

.host-icon {
    font-size: 1.8rem;
    flex-shrink: 0;
    margin-top: 0.1rem;
}

.host-info {
    display: flex;
    flex-direction: column;
    flex: 1;
}

.host-name {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 0.5rem;
    font-size: 1rem;
}

.host-desc {
    font-size: 0.9rem;
    color: #6c757d;
    line-height: 1.4;
}

.host-check {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    font-size: 1.3rem;
    color: #667eea;
    flex-shrink: 0;
}

.url-inputs {
    display: grid;
    gap: 1rem;
    margin-top: 1.5rem;
}

.url-display {
    display: grid;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.steam-upload,
.github-upload {
    margin-top: 1rem;
}

/* GitHub相关样式优化 */
.github-status,
.github-ready {
    margin-bottom: 1.5rem;
}

.github-status-info {
    margin-bottom: 2rem;
}

/* GitHub检查状态样式 */
.checking-spinner {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #6c757d;
}

/* 上传进度动画 */
.upload-progress {
    margin-bottom: 1.5rem;
}

.progress-card {
    border: 1px solid #e0e7ff;
    background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
}

.progress-item {
    margin-bottom: 1rem;
}

.progress-item:last-child {
    margin-bottom: 0;
}

.progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.file-name {
    font-weight: 500;
    color: #2c3e50;
}

.file-status {
    display: flex;
    align-items: center;
    font-size: 1.1rem;
}

.file-status.waiting {
    color: #6c757d;
}

.file-status.uploading {
    color: #007bff;
}

.file-status.success {
    color: #28a745;
}

.file-status.error {
    color: #dc3545;
}

/* 旋转动画 */
.rotating {
    animation: rotate 1s linear infinite;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

/* TTS配置样式 */
.tts-config {
    margin-bottom: 1.5rem;
}

.tts-info {
    margin-top: 1.5rem;
}

.generate-result {
    margin-top: 2rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .progress-bar {
        flex-direction: column;
        gap: 1rem;
    }

    .progress-line {
        width: 3px;
        height: 40px;
    }

    .step-actions {
        flex-direction: column;
        gap: 1rem;
    }

    .step-actions-first {
        align-items: center;
    }

    .host-content {
        flex-direction: column;
        text-align: center;
        gap: 0.8rem;
    }

    .host-icon {
        margin-top: 0;
    }
    
    .host-check {
        align-self: center;
    }
}
</style>

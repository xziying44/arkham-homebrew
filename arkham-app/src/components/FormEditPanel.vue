<template>
    <div class="form-pane">
        <!-- 快速导航条 - 收起状态：小圆圈按钮 -->
        <div
            class="quick-nav-toggle"
            v-if="isNavCollapsed && selectedFile && selectedFile.type === 'card' && currentCardType"
            @click="isNavCollapsed = false">
            <n-tooltip placement="left">
                <template #trigger>
                    <n-icon :size="20">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                            <path d="M64 144h384v48H64zm0 112h384v48H64zm0 112h384v48H64z" fill="currentColor"/>
                        </svg>
                    </n-icon>
                </template>
                展开导航
            </n-tooltip>
        </div>

        <!-- 快速导航条 - 展开状态 -->
        <div class="quick-nav" v-if="!isNavCollapsed && selectedFile && selectedFile.type === 'card' && currentCardType">
            <!-- 收起按钮 -->
            <n-tooltip placement="left">
                <template #trigger>
                    <div class="nav-item nav-collapse" @click="isNavCollapsed = true">
                        <n-icon :size="16">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                                <path d="M184 112l144 144-144 144" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48"/>
                            </svg>
                        </n-icon>
                    </div>
                </template>
                收起导航
            </n-tooltip>

            <!-- 分隔线 -->
            <div class="nav-divider"></div>

            <!-- 导航项 -->
            <n-tooltip placement="left" v-for="navItem in navigationItems" :key="navItem.id">
                <template #trigger>
                    <div
                        class="nav-item"
                        :class="{ active: activeSection === navItem.id }"
                        @click="scrollToSection(navItem.id)">
                        <n-icon :size="16">
                            <component :is="navItem.icon" />
                        </n-icon>
                    </div>
                </template>
                {{ navItem.label }}
            </n-tooltip>
        </div>

        <div class="pane-header">
            <n-space align="center" justify="space-between">
                <n-space align="center" size="small">
                    <n-button v-if="!showFileTree" size="tiny" quaternary @click="$emit('toggle-file-tree')"
                        class="header-button">
                        <n-icon :component="FolderOpenOutline" />
                    </n-button>
                    <span class="pane-title">
                        {{ selectedFile?.label || $t('cardEditor.panel.cardEditor') }}
                        <span v-if="hasUnsavedChanges" class="unsaved-indicator">*</span>
                    </span>
                </n-space>
                <n-space size="small">
                    <n-button size="tiny" @click="triggerSaveAll" class="header-button" v-if="hasUnsavedFiles">
                        {{ $t('cardEditor.panel.saveAll') }}
                    </n-button>
                    <n-button size="tiny" @click="showJsonModal = true" class="header-button" v-if="selectedFile">{{
                        $t('cardEditor.panel.viewJson') }}</n-button>
                    <n-button v-if="!showImagePreview" size="tiny" quaternary @click="$emit('toggle-image-preview')"
                        class="header-button">
                        <n-icon :component="ImageOutline" />
                    </n-button>
                </n-space>
            </n-space>
        </div>

        <div class="form-content">
            <!-- 未选择卡牌文件时的提示 -->
            <div v-if="!selectedFile || selectedFile.type !== 'card'" class="empty-state">
                <div class="welcome-guide">
                    <h2 class="welcome-title">{{ $t('cardEditor.panel.noCardSelected') }}</h2>
                    <p class="welcome-subtitle">{{ $t('cardEditor.panel.createOrSelectCard') }}</p>

                    <div class="guide-section">
                        <h3 class="guide-title">{{ $t('cardEditor.panel.howToCreateCard') }}</h3>
                        <div class="guide-steps">
                            <div class="guide-step">
                                <div class="step-icon">➕</div>
                                <div class="step-content">
                                    <span class="step-text">{{ $t('cardEditor.panel.clickPlusButton') }}</span>
                                </div>
                            </div>
                            <div class="guide-step">
                                <div class="step-icon">🖱️</div>
                                <div class="step-content">
                                    <span class="step-text">{{ $t('cardEditor.panel.rightClickFileTree') }}</span>
                                </div>
                            </div>
                            <div class="guide-step">
                                <div class="step-icon">📁</div>
                                <div class="step-content">
                                    <span class="step-text">{{ $t('cardEditor.panel.selectExistingCard') }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="welcome-footer">
                        <p class="encourage-text">{{ $t('cardEditor.panel.getStarted') }}</p>
                    </div>
                </div>
            </div>

            <!-- 卡牌编辑器内容 -->
            <n-scrollbar v-else>
                <div class="form-wrapper">
                    <!-- 双面卡牌标签页切换 -->
                    <div v-if="isDoubleSided" class="card-side-selector">
                        <n-radio-group v-model:value="currentSide" size="medium">
                            <n-radio-button value="front">{{ $t('cardEditor.panel.frontSide') }}</n-radio-button>
                            <n-radio-button value="back">{{ $t('cardEditor.panel.backSide') }}</n-radio-button>
                        </n-radio-group>
                    </div>

                    <!-- 单面卡牌或当前选中面的编辑器 -->
                    <div v-if="!isDoubleSided || currentSide === 'front'">
                        <CardSideEditor
                            ref="frontCardSideEditorRef"
                            side="front"
                            :card-data="currentCardData"
                            :card-type-configs="cardTypeConfigs"
                            :card-type-options="cardTypeOptions"
                            :language-options="languageOptions"
                            @update-card-data="updateCardSideData"
                            @update-card-type="updateCardSideType"
                            @trigger-preview="triggerDebouncedPreviewUpdate" />
                    </div>

                    <!-- 背面编辑器（仅在双面卡牌且选择背面时显示） -->
                    <div v-if="isDoubleSided && currentSide === 'back'">
                        <CardSideEditor
                            ref="backCardSideEditorRef"
                            side="back"
                            :card-data="{ ...currentCardData.back || {}, quantity: currentCardData.quantity || 1 }"
                            :card-type-configs="cardTypeConfigs"
                            :card-type-options="cardTypeOptions"
                            :language-options="languageOptions"
                            @update-card-data="updateCardSideData"
                            @update-card-type="updateCardSideType"
                            @trigger-preview="triggerDebouncedPreviewUpdate" />
                    </div>

                    <!-- 共享组件区域 -->
                    <div class="shared-components" v-if="hasAnyValidCardData">
                        <!-- TTS脚本编辑器 -->
                        <div ref="ttsScriptSection">
                            <TtsScriptEditor :card-data="currentCardData" :card-type="currentCardType"
                                :is-double-sided="isDoubleSided" :current-side="currentSide"
                                @update-tts-script="updateTtsScript" />
                        </div>

                        <!-- 卡牌标签编辑器 -->
                        <div ref="tagsSection">
                            <CardTagsEditor :card-data="currentCardData" :side="currentSide"
                                @update-tags="updateCardTags" />
                        </div>

                        <!-- 牌库选项编辑器 -->
                        <div ref="deckOptionsSection">
                            <DeckOptionEditor :card-data="currentCardData" :card-type="currentSideType"
                                :is-double-sided="isDoubleSided" :current-side="currentSide"
                                @update-deck-options="updateDeckOptions" />
                        </div>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="form-actions">
                        <n-space>
                            <n-button type="primary" @click="saveCard" :loading="saving">
                                {{ $t('cardEditor.panel.saveCard') }}
                                <span class="keyboard-shortcut">{{ $t('cardEditor.panel.ctrlS') }}</span>
                            </n-button>
                            <n-button @click="previewCard" :loading="generating">{{ $t('cardEditor.panel.previewCard')
                                }}</n-button>
                            <n-button @click="exportCard" :loading="exporting" :disabled="!hasValidCardData">{{
                                $t('cardEditor.panel.exportImage') }}</n-button>
                            <!-- 版本转换按钮 - 仅在非2.0版本且有有效卡牌数据时显示 -->
                            <n-button v-if="!isDoubleSided && hasValidCardData" @click="showVersionConvertDialog = true"
                                type="warning" ghost>
                                {{ $t('cardEditor.panel.convertToV2') }}
                            </n-button>
                            <n-button @click="resetForm">{{ $t('cardEditor.panel.reset') }}</n-button>
                        </n-space>
                    </div>
                </div>
            </n-scrollbar>
        </div>

        <!-- JSON查看模态框 -->
        <n-modal v-model:show="showJsonModal" style="width: 80%; max-width: 800px;">
            <n-card :title="$t('cardEditor.panel.currentJsonData')" :bordered="false" size="huge" role="dialog"
                aria-modal="true">
                <div class="json-modal-content">
                    <div class="json-display-container">
                        <n-scrollbar style="max-height: 60vh;">
                            <n-code :code="filteredJsonData" language="json" class="json-code-display" />
                        </n-scrollbar>
                    </div>
                    <div class="json-actions">
                        <n-button type="primary" @click="copyJsonToClipboard" class="copy-button">
                            <template #icon>
                                <n-icon :component="CopyOutline" />
                            </template>
                            {{ $t('cardEditor.panel.copyJson') }}
                        </n-button>
                    </div>
                </div>
                <template #footer>
                    <n-space justify="end">
                        <n-button @click="showJsonModal = false">{{ $t('cardEditor.panel.close') }}</n-button>
                    </n-space>
                </template>
            </n-card>
        </n-modal>

        <!-- 保存确认对话框 -->
        <n-modal v-model:show="showSaveConfirmDialog">
            <n-card style="width: 450px" :title="$t('cardEditor.panel.saveConfirmation')" :bordered="false" size="huge"
                role="dialog" aria-modal="true">
                <n-space vertical>
                    <n-alert type="warning" :title="$t('cardEditor.panel.unsavedChanges')">
                        <template #icon>
                            <n-icon :component="WarningOutline" />
                        </template>
                        {{ $t('cardEditor.panel.hasUnsavedChangesMessage') }}
                    </n-alert>
                    <n-space vertical size="small">
                        <p><strong>{{ selectedFile?.label }}</strong></p>
                        <p style="color: #666; font-size: 12px;">
                            {{ $t('cardEditor.panel.changesWillBeLost') }}
                        </p>
                    </n-space>
                </n-space>
                <template #footer>
                    <n-space justify="end">
                        <n-button @click="discardChanges">{{ $t('cardEditor.panel.dontSave') }}</n-button>
                        <n-button @click="showSaveConfirmDialog = false">{{ $t('cardEditor.panel.cancel') }}</n-button>
                        <n-button type="primary" @click="saveAndSwitch" :loading="saving">{{ $t('cardEditor.panel.save')
                            }}</n-button>
                    </n-space>
                </template>
            </n-card>
        </n-modal>

        <!-- 版本转换确认对话框 -->
        <n-modal v-model:show="showVersionConvertDialog">
            <n-card style="width: 500px" :title="$t('cardEditor.panel.convertToV2Confirm')" :bordered="false"
                size="huge" role="dialog" aria-modal="true">
                <n-space vertical>
                    <n-alert type="info" :title="$t('cardEditor.panel.versionConvertInfo')">
                        <template #icon>
                            <n-icon :component="WarningOutline" />
                        </template>
                        <div>
                            <p>{{ $t('cardEditor.panel.versionConvertDescription') }}</p>
                            <p style="margin-top: 8px; font-weight: 500;">{{
                                $t('cardEditor.panel.convertWillCreateBack') }}</p>
                        </div>
                    </n-alert>
                    <n-space vertical size="small">
                        <p><strong>{{ $t('cardEditor.panel.currentCard') }}:</strong> {{ currentCardData.name || '未命名卡牌'
                            }}</p>
                        <p><strong>{{ $t('cardEditor.panel.currentType') }}:</strong> {{ currentCardData.type || '未知类型'
                            }}</p>
                        <p v-if="currentCardData.type" style="color: #666; font-size: 12px;">
                            {{ $t('cardEditor.panel.autoSetBackType') }}: <strong>{{
                                getDefaultBackType(currentCardData.type)?.type || '标准卡背' }}</strong>
                        </p>
                    </n-space>
                </n-space>
                <template #footer>
                    <n-space justify="end">
                        <n-button @click="showVersionConvertDialog = false">{{ $t('cardEditor.panel.cancel')
                            }}</n-button>
                        <n-button type="warning" @click="convertToVersion2" :loading="converting">
                            {{ $t('cardEditor.panel.confirmConvert') }}
                        </n-button>
                    </n-space>
                </template>
            </n-card>
        </n-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue';
import {
    FolderOpenOutline,
    ImageOutline,
    WarningOutline,
    CopyOutline,
    DocumentTextOutline,
    ImagesOutline,
    ColorPaletteOutline,
    TextOutline,
    InformationCircleOutline,
    CodeSlashOutline,
    PricetagOutline,
    OptionsOutline
} from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import type { TreeOption } from 'naive-ui';
// 【新增】导入新的组件
import IllustrationLayoutEditor from './IllustrationLayoutEditor.vue';
import DeckOptionEditor from './DeckOptionEditor.vue';
import CardSideEditor from './CardSideEditor.vue';

// 导入中文和英文配置
import { cardTypeConfigs as cardTypeConfigsZh, cardTypeOptions as cardTypeOptionsZh, cardBackConfigs as cardBackConfigsZh, type CardTypeConfig, getDefaultBackType as getDefaultBackTypeZh } from '@/config/cardTypeConfigs';
import { cardTypeConfigs as cardTypeConfigsEn, cardTypeOptions as cardTypeOptionsEn, cardBackConfigs as cardBackConfigsEn, getDefaultBackType as getDefaultBackTypeEn } from '@/config/cardTypeConfigsEn';

import { WorkspaceService, CardService, ConfigService, LanguageConfigService, TtsScriptService } from '@/api';
import type { CardData } from '@/api/types';
import TtsScriptEditor from './TtsScriptEditor.vue';
import CardTagsEditor from './CardTagsEditor.vue';
import { generateUpgradePowerWordScript } from '@/config/upgrade-script-generator';

interface Props {
    showFileTree: boolean;
    showImagePreview: boolean;
    selectedFile?: TreeOption | null;
    isMobile?: boolean;
    unsavedFilesCount?: number; // 新增：未保存文件数量
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'toggle-file-tree': [];
    'toggle-image-preview': [];
    'update-preview-image': [image: string | { front: string; back?: string }];
    'update-preview-side': [side: 'front' | 'back'];
    'update-preview-loading': [loading: boolean];
    'refresh-file-tree': [];
    'save-to-cache': [filePath: string, data: any]; // 新增：保存到暂存
    'load-from-cache': [filePath: string]; // 新增：从暂存加载（用于事件通知）
    'clear-cache': [filePath: string]; // 新增：清除暂存
    'trigger-save-all': []; // 新增：触发保存所有未保存文件
}>();

const { t, locale } = useI18n(); // 添加 locale
const message = useMessage();

// 动态获取当前语言的配置
const cardTypeConfigs = computed(() => {
    const baseConfigs = locale.value === 'en' ? cardTypeConfigsEn : cardTypeConfigsZh;
    const cardBacks = locale.value === 'en' ? cardBackConfigsEn : cardBackConfigsZh;
    return { ...baseConfigs, ...cardBacks };
});

const cardTypeOptions = computed(() => {
    return locale.value === 'en' ? cardTypeOptionsEn : cardTypeOptionsZh;
});

// ============== 哈希计算辅助方法 ==============
// 将对象进行深度排序（按键名排序），以获得稳定序列化结果
const deepSortObject = (value: any): any => {
    if (Array.isArray(value)) {
        return value.map(v => deepSortObject(v));
    }
    if (value && typeof value === 'object') {
        const sorted: Record<string, any> = {};
        Object.keys(value).sort().forEach((k) => {
            sorted[k] = deepSortObject(value[k]);
        });
        return sorted;
    }
    return value;
};

// 稳定序列化（排除根级 content_hash 字段）
const stableStringifyExcludingHash = (data: any): string => {
    try {
        // 深拷贝并剔除根级 content_hash
        const cloned = JSON.parse(JSON.stringify(data || {}));
        if (cloned && typeof cloned === 'object') {
            delete cloned.content_hash;
        }
        const sorted = deepSortObject(cloned);
        return JSON.stringify(sorted);
    } catch (e) {
        // 回退到普通序列化
        return JSON.stringify(data || {});
    }
};

// 计算SHA-256（返回hex字符串），若不可用则回退轻量哈希
const computeSHA256Hex = async (text: string): Promise<string> => {
    try {
        // @ts-ignore
        const subtle = (globalThis.crypto && globalThis.crypto.subtle) ? globalThis.crypto.subtle : null;
        if (subtle && typeof TextEncoder !== 'undefined') {
            const enc = new TextEncoder();
            const buf = enc.encode(text);
            const hash = await subtle.digest('SHA-256', buf);
            const bytes = Array.from(new Uint8Array(hash));
            return bytes.map(b => b.toString(16).padStart(2, '0')).join('');
        }
        throw new Error('subtle crypto not available');
    } catch {
        // 简易回退（djb2）
        let h = 5381;
        for (let i = 0; i < text.length; i++) {
            h = ((h << 5) + h) + text.charCodeAt(i);
            h = h >>> 0;
        }
        return ('00000000' + h.toString(16)).slice(-8);
    }
};

// 计算卡牌内容哈希（仅在保存时调用），排除 content_hash 自身
const computeCardContentHash = async (cardObj: any): Promise<string> => {
    const payload = stableStringifyExcludingHash(cardObj);
    return await computeSHA256Hex(payload);
};

// 创建保存用的深拷贝快照，并冻结当次保存的文件路径
const createSaveSnapshot = (filePath?: string | null) => {
    if (!filePath) return null;
    try {
        const snapshot = JSON.parse(JSON.stringify(currentCardData));
        return { filePath, snapshot };
    } catch (error) {
        console.error('创建保存快照失败:', error);
        return null;
    }
};

// 提取 GMNotes 中的脚本 ID
const extractScriptIdFromGMNotes = (gmnotes: string): string => {
    if (!gmnotes || typeof gmnotes !== 'string') return '';
    try {
        const parsed = JSON.parse(gmnotes);
        if (parsed && typeof parsed === 'object' && parsed.id) {
            return String(parsed.id);
        }
    } catch (err) {
        console.warn('解析GMNotes获取脚本ID失败', err);
    }
    return '';
};

// 保存前调用后端生成 GMNotes，写回稳定脚本 ID（保持 v2，不写入旧字段）
const ensureScriptIdByBackend = async (cardObj: any): Promise<string | null> => {
    try {
        const payload = JSON.parse(JSON.stringify(cardObj || {}));
        payload.tts_config = {
            ...(payload.tts_config || {}),
            version: 'v2'
        };
        const result = await TtsScriptService.generateFromCard(payload);
        let sid = extractScriptIdFromGMNotes(result?.GMNotes || '');
        if (!sid && payload.tts_config?.script_id) {
            sid = payload.tts_config.script_id;
        }
        if (sid) {
            if (!cardObj.tts_config || typeof cardObj.tts_config !== 'object') {
                cardObj.tts_config = {};
            }
            cardObj.tts_config.version = 'v2';
            cardObj.tts_config.script_id = sid;
            if ('tts_script' in cardObj) {
                delete cardObj.tts_script;
            }
            return sid;
        }
    } catch (error) {
        console.warn('调用后端生成GMNotes失败，保留现有脚本ID', error);
    }
    return null;
};

// 表单状态
const currentCardData = reactive({
    type: '',
    name: '',
    id: '',
    created_at: '',
    version: '1.0',
    language: 'zh', // 新增：默认语言为中文
});

// 双面卡牌状态
const currentSide = ref<'front' | 'back'>('front');
const isDoubleSided = computed(() => currentCardData.version === '2.0');


// 当前面的语言
const currentLanguage = computed({
    get: () => {
        if (currentSide.value === 'back' && currentCardData.back) {
            return currentCardData.back.language || 'zh';
        }
        return currentCardData.language || 'zh';
    },
    set: (value) => {
        if (currentSide.value === 'back') {
            if (!currentCardData.back) {
                currentCardData.back = {};
            }
            currentCardData.back.language = value;
        } else {
            currentCardData.language = value;
            if (isDoubleSided.value) {
                if (!currentCardData.back) {
                    currentCardData.back = {};
                }
                const backLang = currentCardData.back.language;
                if (!backLang || backLang.trim() === '') {
                    currentCardData.back.language = value;
                }
            }
        }
    }
});

// 当前面的类型
const currentSideType = computed({
    get: () => {
        if (currentSide.value === 'back' && currentCardData.back) {
            return currentCardData.back.type || '';
        }
        return currentCardData.type || '';
    },
    set: (value) => {
        if (currentSide.value === 'back') {
            if (!currentCardData.back) {
                currentCardData.back = {};
            }
            currentCardData.back.type = value;
        } else {
            currentCardData.type = value;
        }
    }
});


// 新增：语言选项（默认值为当前内置四种语言，实际加载时会被语言配置覆盖）
const languageOptions = ref<Array<{ label: string; value: string }>>([
    { label: '简体中文', value: 'zh' },
    { label: '繁體中文', value: 'zh-CHT' },
    { label: 'English', value: 'en' },
    { label: 'Polski', value: 'pl' },
]);

// 获取当前语言对应的默认背面配置函数
const getDefaultBackType = (frontType: string): { type: string; is_back?: boolean } | null => {
    const getDefaultBackTypeFunc = locale.value === 'en' ? getDefaultBackTypeEn : getDefaultBackTypeZh;
    return getDefaultBackTypeFunc(frontType);
};

const ensureRuleMiniBack = () => {
    if (!currentCardData.back) {
        currentCardData.back = {};
    }
    currentCardData.back.type = '规则小卡';
    currentCardData.back.is_back = true;
};

// 原始数据状态 - 用于检测修改
const originalCardData = ref<string>('');

// 原始文件信息 - 用于记住需要保存的文件
const originalFileInfo = ref<{ path: string; label: string } | null>(null);

// 待切换的文件
const pendingSwitchFile = ref<TreeOption | null>(null);

const currentCardType = ref('');
const showJsonModal = ref(false);
const showSaveConfirmDialog = ref(false);
const showVersionConvertDialog = ref(false);
const saving = ref(false);
const generating = ref(false);
const exporting = ref(false);
const converting = ref(false);

// 新增：图片预览加载状态
const imagePreviewLoading = ref(false);

// 从后端语言配置中加载支持的语言列表
const loadLanguageOptions = async () => {
    try {
        const data = await LanguageConfigService.getLanguageConfig();
        if (Array.isArray(data.config) && data.config.length > 0) {
            languageOptions.value = data.config.map((item) => ({
                label: item.name || item.code,
                value: item.code,
            }));
        }
    } catch (error) {
        console.warn('加载语言配置失败，使用默认语言列表', error);
    }
};

// 快速导航相关
const cardTypeSection = ref<HTMLElement | null>(null);
const propertiesSection = ref<HTMLElement | null>(null);
const illustrationSection = ref<HTMLElement | null>(null);
const textLayoutSection = ref<HTMLElement | null>(null);
const cardInfoSection = ref<HTMLElement | null>(null);
const ttsScriptSection = ref<HTMLElement | null>(null);
const tagsSection = ref<HTMLElement | null>(null);
const deckOptionsSection = ref<HTMLElement | null>(null);
const activeSection = ref<string>('cardType');
const isNavCollapsed = ref<boolean>(true); // 导航条收起状态（默认收起）

// CardSideEditor组件ref（用于访问暴露的section refs）
const frontCardSideEditorRef = ref<any>(null);
const backCardSideEditorRef = ref<any>(null);

// 导航项配置
const navigationItems = computed(() => {
    if (!hasAnyValidCardData.value) return [];

    const items = [
        {
            id: 'cardType',
            label: t('cardEditor.nav.cardType'),
            icon: DocumentTextOutline
        },
        {
            id: 'properties',
            label: t('cardEditor.nav.properties'),
            icon: ColorPaletteOutline
        }
    ];

    // 如果有图片，添加插画布局导航项
    if (currentCardData.picture_base64 || (currentCardData.back?.picture_base64)) {
        items.push({
            id: 'illustration',
            label: t('cardEditor.nav.illustration'),
            icon: ImagesOutline
        });
    }

    items.push(
        {
            id: 'textLayout',
            label: t('cardEditor.nav.textLayout'),
            icon: TextOutline
        },
        {
            id: 'cardInfo',
            label: t('cardEditor.nav.cardInfo'),
            icon: InformationCircleOutline
        },
        {
            id: 'ttsScript',
            label: t('cardEditor.nav.ttsScript'),
            icon: CodeSlashOutline
        },
        {
            id: 'tags',
            label: t('cardEditor.nav.tags'),
            icon: PricetagOutline
        },
        {
            id: 'deckOptions',
            label: t('cardEditor.nav.deckOptions'),
            icon: OptionsOutline
        }
    );

    return items;
});

// 辅助函数：从 ref 获取真实 DOM 元素（处理组件实例的情况）
const getElementFromRef = (refValue: any): HTMLElement | null => {
    if (!refValue) return null;
    // 如果是组件实例（有 $el 属性），返回 $el
    if (refValue.$el && refValue.$el instanceof HTMLElement) {
        return refValue.$el;
    }
    // 如果已经是 DOM 元素，直接返回
    if (refValue instanceof HTMLElement) {
        return refValue;
    }
    return null;
};

// 滚动到指定区域
const scrollToSection = async (sectionId: string) => {
    const formContent = document.querySelector('.form-content');
    if (!formContent) return;

    // 获取当前活动的CardSideEditor（根据单双面和当前面）
    const activeCardSideEditor = (!isDoubleSided.value || currentSide.value === 'front')
        ? frontCardSideEditorRef.value
        : backCardSideEditorRef.value;

    // 特殊处理：如果是插画布局导航项，先展开插画布局编辑器
    if (sectionId === 'illustration' && activeCardSideEditor?.expandIllustrationLayout) {
        activeCardSideEditor.expandIllustrationLayout();
        // 等待 DOM 更新完成
        await nextTick();
    }

    // 构建section映射，优先从CardSideEditor获取子组件refs，并转换为真实 DOM 元素
    // 注意：defineExpose 暴露的 ref 会被自动解包，所以不需要 .value
    const sectionMap: Record<string, HTMLElement | null> = {
        cardType: getElementFromRef(activeCardSideEditor?.cardTypeSection) || getElementFromRef(cardTypeSection.value),
        properties: getElementFromRef(activeCardSideEditor?.propertiesSection) || getElementFromRef(propertiesSection.value),
        illustration: getElementFromRef(activeCardSideEditor?.illustrationSection) || getElementFromRef(illustrationSection.value),
        textLayout: getElementFromRef(activeCardSideEditor?.textLayoutSection) || getElementFromRef(textLayoutSection.value),
        cardInfo: getElementFromRef(activeCardSideEditor?.cardInfoSection) || getElementFromRef(cardInfoSection.value),
        ttsScript: getElementFromRef(ttsScriptSection.value),
        tags: getElementFromRef(tagsSection.value),
        deckOptions: getElementFromRef(deckOptionsSection.value)
    };

    const targetSection = sectionMap[sectionId];
    if (targetSection) {
        // 使用 scrollIntoView 滚动到目标位置
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        activeSection.value = sectionId;

        // 滚动完成后自动收起导航栏
        isNavCollapsed.value = true;
    }
};

// 监听滚动事件，更新当前激活的导航项
const handleScroll = () => {
    const formContent = document.querySelector('.form-content');
    if (!formContent) return;

    // 获取当前活动的CardSideEditor（根据单双面和当前面）
    const activeCardSideEditor = (!isDoubleSided.value || currentSide.value === 'front')
        ? frontCardSideEditorRef.value
        : backCardSideEditorRef.value;

    // 使用 getElementFromRef 转换所有 refs 为真实 DOM 元素
    // 注意：defineExpose 暴露的 ref 会被自动解包，所以不需要 .value
    const sections = [
        { id: 'cardType', ref: getElementFromRef(activeCardSideEditor?.cardTypeSection) || getElementFromRef(cardTypeSection.value) },
        { id: 'properties', ref: getElementFromRef(activeCardSideEditor?.propertiesSection) || getElementFromRef(propertiesSection.value) },
        { id: 'illustration', ref: getElementFromRef(activeCardSideEditor?.illustrationSection) || getElementFromRef(illustrationSection.value) },
        { id: 'textLayout', ref: getElementFromRef(activeCardSideEditor?.textLayoutSection) || getElementFromRef(textLayoutSection.value) },
        { id: 'cardInfo', ref: getElementFromRef(activeCardSideEditor?.cardInfoSection) || getElementFromRef(cardInfoSection.value) },
        { id: 'ttsScript', ref: getElementFromRef(ttsScriptSection.value) },
        { id: 'tags', ref: getElementFromRef(tagsSection.value) },
        { id: 'deckOptions', ref: getElementFromRef(deckOptionsSection.value) }
    ];

    let currentActive = 'cardType';
    const containerTop = formContent.getBoundingClientRect().top;

    for (const section of sections) {
        const sectionElement = section.ref;
        if (sectionElement) {
            const rect = sectionElement.getBoundingClientRect();
            const relativeTop = rect.top - containerTop;

            // 如果元素在视口内或已经滚过
            if (relativeTop <= 100) {
                currentActive = section.id;
            }
        }
    }

    activeSection.value = currentActive;
};

// 防抖相关状态
const debounceTimer = ref<number | null>(null);
const isUserEditing = ref(false);
const lastDataSnapshot = ref<string>('');

// 【新增】处理面数据更新的函数
const updateCardSideData = (side: string, fieldKey: string, value: any) => {
    // 检查是否为带索引的字段（如 "attribute[0]"）
    const indexedFieldMatch = fieldKey.match(/^(.+)\[(\d+)\]$/);

    if (indexedFieldMatch) {
        // 处理带索引的字段
        const baseKey = indexedFieldMatch[1];
        const index = parseInt(indexedFieldMatch[2]);

        if (side === 'back') {
            if (!currentCardData.back) {
                currentCardData.back = {};
            }
            if (!Array.isArray(currentCardData.back[baseKey])) {
                currentCardData.back[baseKey] = [];
            }
            // 确保数组长度足够
            while (currentCardData.back[baseKey].length <= index) {
                currentCardData.back[baseKey].push(undefined);
            }
            currentCardData.back[baseKey][index] = value;
        } else {
            if (!Array.isArray(currentCardData[baseKey])) {
                currentCardData[baseKey] = [];
            }
            // 确保数组长度足够
            while (currentCardData[baseKey].length <= index) {
                currentCardData[baseKey].push(undefined);
            }
            currentCardData[baseKey][index] = value;
        }
    } else if (fieldKey.includes('.')) {
        // 处理多级字段（如 "scenario_card.skull"）
        const keys = fieldKey.split('.');
        const targetObj = side === 'back' ?
            (currentCardData.back || (currentCardData.back = {})) :
            currentCardData;

        // 设置深层嵌套值
        let current = targetObj;
        for (let i = 0; i < keys.length - 1; i++) {
            const key = keys[i];
            if (!current[key] || typeof current[key] !== 'object') {
                current[key] = {};
            }
            current = current[key];
        }
        current[keys[keys.length - 1]] = value;
        console.log(`🔧 设置多级字段: ${fieldKey} = ${value}`, targetObj);
    } else {
        // 处理普通字段
        if (side === 'back') {
            if (!currentCardData.back) {
                currentCardData.back = {};
            }
            currentCardData.back[fieldKey] = value;
        } else {
            currentCardData[fieldKey] = value;
            if (fieldKey === 'language' && isDoubleSided.value) {
                if (!currentCardData.back) {
                    currentCardData.back = {};
                }
                const backLang = currentCardData.back.language;
                if (!backLang || backLang.trim() === '') {
                    currentCardData.back.language = value;
                }
            }
        }
    }
    // 触发防抖预览更新
    triggerDebouncedPreviewUpdate();
};

// 【新增】处理面类型更新的函数
const updateCardSideType = (side: string, newType: string) => {
    if (side === 'back') {
        if (!currentCardData.back) {
            currentCardData.back = {};
        }
        currentCardData.back.type = newType;
        // 更新当前编辑面的类型
        if (currentSide.value === 'back') {
            currentCardType.value = newType;
        }
    } else {
        currentCardData.type = newType;
        // 更新当前编辑面的类型
        if (currentSide.value === 'front') {
            currentCardType.value = newType;
        }

        // 【新增】当正面类型变更时，如果背面为空则自动设置默认背面
        if (isDoubleSided.value && (!currentCardData.back || !currentCardData.back.type || currentCardData.back.type.trim() === '')) {
            // 确保back对象存在
            if (!currentCardData.back) {
                currentCardData.back = {};
            }

            const defaultBackConfig = getDefaultBackType(newType);
            if (defaultBackConfig) {
                currentCardData.back.type = defaultBackConfig.type;
                // 如果需要设置is_back字段
                if (defaultBackConfig.is_back !== undefined) {
                    currentCardData.back.is_back = defaultBackConfig.is_back;
                }
                // 如果需要设置is_back字段
                if (defaultBackConfig.location_type !== undefined) {
                    currentCardData.back.location_type = defaultBackConfig.location_type;
                }
                console.log(`🔄 自动设置背面类型: ${defaultBackConfig.type}, is_back: ${defaultBackConfig.is_back}`);
            }

            // 针对调查员小卡：自动设置默认参数（前：正常；背：黑白+共享正面插画）
            if (newType === '调查员小卡') {
                // 确保背面标记
                currentCardData.back.type = '调查员小卡';
                currentCardData.back.is_back = true;
                // 前面默认滤镜
                if (!currentCardData.image_filter) {
                    currentCardData.image_filter = 'normal';
                }
                // 背面默认共享插画与设置 + 黑白滤镜
                currentCardData.back.share_front_picture = 1;
                if (!currentCardData.back.image_filter) {
                    currentCardData.back.image_filter = 'grayscale';
                }
            } else if (newType === '规则小卡') {
                ensureRuleMiniBack();
            }
        }
    }
    // 触发防抖预览更新
    triggerDebouncedPreviewUpdate();
};

// 【新增】处理插画布局更新的函数
const updateIllustrationLayout = (newLayout) => {
    if (currentSide.value === 'back') {
        if (!currentCardData.back) {
            currentCardData.back = {};
        }
        currentCardData.back.picture_layout = newLayout;
    } else {
        currentCardData.picture_layout = newLayout;
    }
    // 触发防抖预览更新，以便实时看到布局变化效果
    triggerDebouncedPreviewUpdate();
};

// 【新增】处理牌库选项更新的函数
const updateDeckOptions = (options) => {
    // 避免重复更新相同数据
    const currentOptions = JSON.stringify(currentCardData.deck_options);
    const newOptions = JSON.stringify(options);

    if (currentOptions === newOptions) {
        return;
    }

    // 保存到根级deck_options字段，无论单面还是双面卡牌
    currentCardData.deck_options = options;
    // 触发防抖预览更新
    triggerDebouncedPreviewUpdate();
};

// 处理卡牌标签更新的函数
const updateCardTags = (tags: { permanent: boolean; exceptional: boolean; myriad: boolean; exile: boolean }) => {
    // 避免重复更新相同数据
    const currentSideData = currentSide.value === 'back' ? (currentCardData.back || {}) : currentCardData;
    const currentTags = {
        permanent: currentSideData.permanent || false,
        exceptional: currentSideData.exceptional || false,
        myriad: currentSideData.myriad || false,
        exile: currentSideData.exile || false
    };

    const newTagsString = JSON.stringify(tags);
    const currentTagsString = JSON.stringify(currentTags);

    if (newTagsString === currentTagsString) {
        return;
    }

    // 更新对应面的标签数据
    if (currentSide.value === 'back') {
        if (!currentCardData.back) {
            currentCardData.back = {};
        }
        currentCardData.back.permanent = tags.permanent;
        currentCardData.back.exceptional = tags.exceptional;
        currentCardData.back.myriad = tags.myriad;
        currentCardData.back.exile = tags.exile;
    } else {
        currentCardData.permanent = tags.permanent;
        currentCardData.exceptional = tags.exceptional;
        currentCardData.myriad = tags.myriad;
        currentCardData.exile = tags.exile;
    }

    // 触发防抖预览更新
    triggerDebouncedPreviewUpdate();
};

// 复制JSON到剪贴板
const copyJsonToClipboard = async () => {
    try {
        await navigator.clipboard.writeText(filteredJsonData.value);
        message.success(t('cardEditor.panel.jsonCopiedToClipboard'));
    } catch (error) {
        console.error('复制失败:', error);
        // 如果clipboard API不可用，使用备用方案
        try {
            const textArea = document.createElement('textarea');
            textArea.value = filteredJsonData.value;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            message.success(t('cardEditor.panel.jsonCopiedToClipboard'));
        } catch (fallbackError) {
            message.error(t('cardEditor.panel.copyFailed'));
        }
    }
};

// 防抖预览更新方法
const triggerDebouncedPreviewUpdate = () => {
    // 清除之前的定时器
    if (debounceTimer.value !== null) {
        clearTimeout(debounceTimer.value);
        debounceTimer.value = null;
    }

    // 检查是否有有效数据
    if (!hasValidCardData.value) {
        return;
    }

    // 标记用户正在编辑
    isUserEditing.value = true;

    // 设置新的防抖定时器 - 1秒后执行
    debounceTimer.value = window.setTimeout(async () => {
        try {
            console.log('🖼️ 防抖预览更新开始');

            // 只有数据真正发生变化才更新预览
            const currentSnapshot = JSON.stringify(currentCardData);
            if (currentSnapshot === lastDataSnapshot.value) {
                console.log('🔄 数据未变化，跳过预览更新');
                return;
            }

            lastDataSnapshot.value = currentSnapshot;

            // 检查是否正在生成中，避免重复生成
            if (generating.value) {
                console.log('⚠️ 正在生成中，跳过预览更新');
                return;
            }

            console.log('🔄 防抖预览更新，不显示特殊加载动画');

            // 调用统一的autoGeneratePreview，不结束加载动画
            await autoGeneratePreview(false);
        } catch (error) {
            console.warn('⚠️ 防抖预览更新失败:', error);
            // 不显示错误消息，避免打扰用户编辑体验
        } finally {
            console.log('✅ 防抖预览更新完成');
            isUserEditing.value = false;
            debounceTimer.value = null;
        }
    }, 500); // 0.5秒防抖延迟
};

// 清除防抖定时器
const clearDebounceTimer = () => {
    if (debounceTimer.value !== null) {
        clearTimeout(debounceTimer.value);
        debounceTimer.value = null;
    }
    isUserEditing.value = false;
};

// 初始化配置
onMounted(async () => {
    // 加载可用语言配置（失败时回退到内置默认列表）
    await loadLanguageOptions();
    // AI功能已移除
});

// 检查是否有未保存的修改
const hasUnsavedChanges = computed(() => {
    if (!props.selectedFile || props.selectedFile.type !== 'card') {
        return false;
    }

    const currentDataString = JSON.stringify(currentCardData);
    return originalCardData.value !== currentDataString;
});

// 检查是否有有效的卡牌数据
const hasValidCardData = computed(() => {
    return currentCardData.type && currentCardData.type.trim() !== '';
});

// 检查是否有未保存的卡牌数据（用于共享组件显示）
const hasAnyValidCardData = computed(() => {
    // 允许调查员小卡在未填写名称时也显示 TTS 配置，用于快速绑定调查员卡
    if ((currentCardData.type || '').trim() === '调查员小卡') {
        return true;
    }

    const hasValidFront = currentCardData.name && currentCardData.name.trim() !== '' &&
        currentCardData.type && currentCardData.type.trim() !== '';

    const hasValidBack = isDoubleSided.value &&
        currentCardData.back &&
        currentCardData.back.name && currentCardData.back.name.trim() !== '' &&
        currentCardData.back.type && currentCardData.back.type.trim() !== '';

    return hasValidFront || hasValidBack;
});

// 检查是否有未保存的文件（用于显示"全部保存"按钮）
const hasUnsavedFiles = computed(() => {
    return (props.unsavedFilesCount ?? 0) > 0;
});

// 触发保存所有未保存文件
const triggerSaveAll = () => {
    emit('trigger-save-all');
};

const currentFormConfig = computed((): CardTypeConfig | null => {
    return currentCardType.value ? cardTypeConfigs.value[currentCardType.value] : null;
});

// 更新currentCardType计算属性
watch(currentSide, () => {
    const editingData = currentSide.value === 'back' && currentCardData.back ? currentCardData.back : currentCardData;
    currentCardType.value = editingData.type || '';
    console.log(`🔄 切换到${currentSide.value}面，当前类型:`, currentCardType.value);

    // 【重要】只通知图片预览组件切换显示面，不重新生成！
    // 双面卡牌是一次性生成正反面的，切换时不需要重新生成
    emit('update-preview-side', currentSide.value);
}, { immediate: false });

// 更新TTS脚本数据
const updateTtsScript = (ttsData: { GMNotes: string; LuaScript: string; config?: any }) => {
    // 防止循环更新
    if (saving.value) return;

    // v2：仅保存统一配置到顶层 tts_config；不再写入旧版 tts_script 字段
    if (ttsData.config) {
        currentCardData.tts_config = {
            version: 'v2',
            ...(ttsData.config as any),
        };
    }
    // 清理冗余旧数据
    if ('tts_script' in currentCardData) {
        delete currentCardData.tts_script;
    }

    // 触发防抖预览更新
    triggerDebouncedPreviewUpdate();
};

// 添加防抖标志
const isProcessingKeydown = ref(false);
const handleKeydown = async (event: KeyboardEvent) => {
    // Ctrl+S 保存
    if ((event.ctrlKey || event.metaKey) && event.code === 'KeyS') {
        event.preventDefault();
        event.stopPropagation();

        // 防止重复处理
        if (isProcessingKeydown.value || saving.value) {
            console.log('阻止重复保存');
            return;
        }

        if (props.selectedFile && props.selectedFile.type === 'card') {
            isProcessingKeydown.value = true;
            try {
                await saveCard();
            } finally {
                setTimeout(() => {
                    isProcessingKeydown.value = false;
                }, 100);
            }
        }
    }
};


// 保存原始数据状态
const saveOriginalData = () => {
    originalCardData.value = JSON.stringify(currentCardData);
    lastDataSnapshot.value = originalCardData.value;
};

// 自动生成卡图（如果数据有效的话）
const autoGeneratePreview = async (endLoadingAnimation = false) => {
    // 只有当卡牌类型有值时才自动生成
    if (currentCardData.type && currentCardData.type.trim()) {
        try {
            console.log('🔄 自动生成预览开始，结束加载动画:', endLoadingAnimation);

            const result_card = await CardService.generateCard(currentCardData as CardData);
            const imageBase64 = result_card?.image;

            if (imageBase64) {
                // 检查是否为双面卡牌
                if (result_card?.back_image) {
                    const doubleSidedImage = {
                        front: imageBase64,
                        back: result_card.back_image
                    };
                    emit('update-preview-image', doubleSidedImage);
                    console.log('✅ 双面卡牌预览生成成功');
                } else {
                    emit('update-preview-image', imageBase64);
                    console.log('✅ 单面卡牌预览生成成功');
                }
            }

            // 【新增】如果需要结束加载动画，则结束
            if (endLoadingAnimation) {
                imagePreviewLoading.value = false;
                emit('update-preview-loading', false);
                console.log('✅ 自动生成完成，结束卡牌形状加载动画');
            }
        } catch (error) {
            // 自动生成失败不显示错误消息，避免打扰用户
            console.warn('自动生成卡图失败:', error);

            // 如果需要结束加载动画，失败时也要结束
            if (endLoadingAnimation) {
                imagePreviewLoading.value = false;
                emit('update-preview-loading', false);
                console.log('❌ 自动生成失败，结束卡牌形状加载动画');
            }
        }
    }
};

// 修改 loadCardData 方法，确保有默认语言
const loadCardData = async () => {
    if (!props.selectedFile || props.selectedFile.type !== 'card' || !props.selectedFile.path) {
        return;
    }

    let loadError = null; // 在try块外部定义

    try {
        // 清除防抖定时器
        clearDebounceTimer();

        // 【修改】不在这里设置加载动画，由调用方设置
        console.log('🔄 loadCardData：加载文件数据');

        // 先清空卡牌类型，触发表单卸载
        currentCardType.value = '';

        // 清空当前数据
        Object.keys(currentCardData).forEach(key => {
            delete currentCardData[key];
        });

        // 等待DOM更新，确保表单完全卸载
        await nextTick();

        // 【新增】优先从暂存加载数据
        let cardData: any = null;

        // 尝试从暂存获取数据
        const filePath = props.selectedFile.path;

        // 先尝试正常加载文件内容
        const content = await WorkspaceService.getFileContent(filePath);
        cardData = JSON.parse(content || '{}');

        // 加载新数据 - 修复：确保deck_options等关键字段正确加载
        const processedCardData = { ...cardData };

        // 处理调查员属性字段的兼容性
        if (processedCardData.type === '调查员' && processedCardData.attribute !== undefined && !Array.isArray(processedCardData.attribute)) {
            // 如果attribute是单个值，转换为数组格式（向后兼容）
            const oldValue = processedCardData.attribute;
            processedCardData.attribute = [oldValue, undefined, undefined, undefined]; // 意志、智力、战力、敏捷
            console.log('🔄 转换调查员属性为现代数组格式:', processedCardData.attribute);
        }

        Object.assign(currentCardData, {
            type: '',
            name: '',
            id: '',
            created_at: '',
            version: '1.0',
            language: 'zh', // 新增：默认语言
            ...processedCardData
        });

        // 修复：确保deck_options字段被正确处理
        if (cardData.deck_options && Array.isArray(cardData.deck_options)) {
            currentCardData.deck_options = [...cardData.deck_options];
            console.log('📚 加载deck_options数据:', currentCardData.deck_options.length, '个选项');
            // 额外确认：延迟触发再次加载，确保DeckOptionEditor能收到数据
            setTimeout(() => {
                console.log('📚 延迟确认deck_options数据已设置:', currentCardData.deck_options);
            }, 50);
        } else if (cardData.deck_options !== undefined) {
            currentCardData.deck_options = cardData.deck_options;
            console.log('📚 加载deck_options数据:', currentCardData.deck_options);
        } else {
            // 明确设置为空数组，确保DeckOptionEditor能正确处理
            currentCardData.deck_options = [];
            console.log('📚 设置deck_options为空数组');
        }

        // 等待DOM更新，确保响应式数据已设置
        await nextTick();

        // 设置新的卡牌类型 - 确保在数据加载后设置
        currentCardType.value = cardData.type || '';
        console.log('📋 加载卡牌类型设置:', currentCardType.value, '原始数据:', cardData.type);

        // 如果是双面卡牌，确保背面数据结构完整
        if (cardData.version === '2.0') {
            // 确保back对象存在
            if (!cardData.back) {
                cardData.back = {};
            }

            if (!cardData.back.language) {
                cardData.back.language = cardData.language || 'zh';
            }

            // 【新增】如果背面类型为空，则自动设置默认背面类型
            if (!cardData.back.type || cardData.back.type.trim() === '') {
                const defaultBackConfig = getDefaultBackType(cardData.type || '');
                if (defaultBackConfig) {
                    cardData.back.type = defaultBackConfig.type;
                    // 如果需要设置is_back字段
                    if (defaultBackConfig.is_back !== undefined) {
                        cardData.back.is_back = defaultBackConfig.is_back;
                    }
                    console.log(`🔄 加载时自动设置背面类型: ${defaultBackConfig.type}, is_back: ${defaultBackConfig.is_back}`);
                }
            }

            console.log('🔄 双面卡牌背面数据初始化完成:', cardData.back);
        }

        // 再次等待确保类型设置完成
        await nextTick();

        // 保存原始数据状态
        setTimeout(() => {
            saveOriginalData();
            console.log('💾 原始数据已保存，当前卡牌类型:', currentCardType.value);
            // 【关键】加载完成后自动生成预览，并结束加载动画
            autoGeneratePreview(true);
        }, 100);
    } catch (error) {
        loadError = error; // 赋值给外部变量
        console.error('加载卡牌数据失败:', loadError);
        message.error(t('cardEditor.panel.loadCardDataFailed'));
    } finally {
        // 【修改】检查是否有加载错误
        if (loadError) {
            // 文件加载失败，结束加载动画
            setTimeout(() => {
                imagePreviewLoading.value = false;
                emit('update-preview-loading', false);
                console.log('❌ 文件加载失败，隐藏卡牌形状加载动画');
            }, 300);
        } else {
            console.log('✅ 文件加载成功，等待自动生成完成');

            // 【重要】检查是否有有效数据
            const hasValidData = currentCardData.name && currentCardData.name.trim() &&
                currentCardData.type && currentCardData.type.trim();

            if (!hasValidData) {
                // 新创建的空卡牌，直接结束加载动画
                imagePreviewLoading.value = false;
                emit('update-preview-loading', false);
                console.log('⚠️ 新卡牌无有效数据，结束卡牌形状加载动画');
            } else {
                console.log('✅ 文件加载成功，有有效数据，等待自动生成完成');
            }
        }
    }
};

// 修改 saveCard 方法
const saveCard = async () => {
    const fileToSave = originalFileInfo.value || props.selectedFile;
    const frozenPath = fileToSave?.path;
    const frozenLabel = fileToSave?.label;

    if (!frozenPath) {
        message.warning(t('cardEditor.panel.noFileSelected'));
        return false;
    }

    if (saving.value) {
        console.log('已在保存中，跳过');
        return false;
    }

    // 记录保存前的状态签名，用于检测保存过程中是否有进一步修改
    const stateBeforeSave = JSON.stringify(currentCardData);
    const snapshotResult = createSaveSnapshot(frozenPath);
    if (!snapshotResult) {
        message.error(t('cardEditor.panel.saveCardFailed'));
        return false;
    }

    let snapshotData: any | null = snapshotResult.snapshot;

    try {
        saving.value = true;
        clearDebounceTimer();

        // 保存前生成 GMNotes，确保脚本 ID 持久化（仅操作快照，避免污染实时表单数据）
        await ensureScriptIdByBackend(snapshotData);

        // 在保存前计算并写入内容哈希（排除 content_hash 自身）
        try {
            const hash = await computeCardContentHash(snapshotData);
            snapshotData.content_hash = hash;
        } catch (e) {
            console.warn('计算卡牌内容哈希失败，将继续保存:', e);
        }

        // 保存JSON文件（使用冻结路径与快照数据）
        const jsonContent = JSON.stringify(snapshotData, null, 2);
        await WorkspaceService.saveFileContent(snapshotResult.filePath, jsonContent);

        // 【新增】保存成功后清除暂存（按冻结路径）
        emit('clear-cache', snapshotResult.filePath);

        // 若保存期间用户未再修改，则同步关键字段并更新“已保存”状态
        const stateAfterSave = JSON.stringify(currentCardData);
        if (stateAfterSave === stateBeforeSave) {
            if (snapshotData.tts_config !== undefined) {
                (currentCardData as any).tts_config = JSON.parse(JSON.stringify(snapshotData.tts_config));
            }
            if (snapshotData.content_hash !== undefined) {
                (currentCardData as any).content_hash = snapshotData.content_hash;
            }
            saveOriginalData();
        }

        message.success(frozenLabel ? `${frozenLabel} ${t('cardEditor.panel.cardSavedSuccessfully')}` : t('cardEditor.panel.cardSavedSuccessfully'));
        return true;
    } catch (error) {
        console.error('保存卡牌失败:', error);
        message.error(t('cardEditor.panel.saveCardFailed'));
        return false;
    } finally {
        snapshotData = null; // 显式清理快照引用，便于 GC
        saving.value = false;
    }
};

// 保存并切换文件
const saveAndSwitch = async () => {
    const success = await saveCard();
    if (success && pendingSwitchFile.value) {
        showSaveConfirmDialog.value = false;

        // 清空原始文件信息，因为已经保存了
        originalFileInfo.value = null;

        // 加载新文件
        const fileToSwitch = pendingSwitchFile.value;
        pendingSwitchFile.value = null;

        // 如果是切换到新卡牌，先重置状态
        if (fileToSwitch && fileToSwitch.type === 'card') {
            console.log('🔄 保存后切换到新卡牌，重置编辑器状态');

            // 1. 重置当前面为正面
            currentSide.value = 'front';

            // 2. 清空卡牌类型，触发表单卸载
            currentCardType.value = '';

            // 3. 通知父组件清空图片预览
            emit('update-preview-image', '');

            // 4. 清除防抖定时器
            clearDebounceTimer();

            // 5. 清空当前数据状态
            Object.keys(currentCardData).forEach(key => {
                delete currentCardData[key];
            });

            // 等待DOM更新，确保状态完全重置
            await nextTick();

            console.log('✅ 保存后编辑器状态重置完成，开始加载新卡牌数据');

            // 【新增】保存并切换文件时显示加载动画
            imagePreviewLoading.value = true;
            emit('update-preview-loading', true);
            console.log('🔄 保存并切换文件，开始显示卡牌形状加载动画');

            // 触发文件切换逻辑
            await loadCardData();
        } else {
            // 清空表单数据
            clearFormData();
        }
    }
};

// 放弃修改并切换文件
const discardChanges = () => {
    showSaveConfirmDialog.value = false;
    originalFileInfo.value = null;
    const fileToSwitch = pendingSwitchFile.value;
    pendingSwitchFile.value = null;
    clearDebounceTimer();

    // 如果是切换到新卡牌，先重置状态
    if (fileToSwitch && fileToSwitch.type === 'card') {
        console.log('🔄 放弃修改并切换到新卡牌，重置编辑器状态');

        // 1. 重置当前面为正面
        currentSide.value = 'front';

        // 2. 清空卡牌类型，触发表单卸载
        currentCardType.value = '';

        // 3. 通知父组件清空图片预览
        emit('update-preview-image', '');

        // 4. 清空当前数据状态
        Object.keys(currentCardData).forEach(key => {
            delete currentCardData[key];
        });

        // 【新增】放弃修改并切换文件时显示加载动画
        imagePreviewLoading.value = true;
        emit('update-preview-loading', true);
        console.log('🔄 放弃修改并切换文件，开始显示卡牌形状加载动画');

        // 等待DOM更新，确保状态完全重置
        nextTick(() => {
            console.log('✅ 放弃修改后编辑器状态重置完成，开始加载新卡牌数据');
            // 触发文件切换逻辑
            loadCardData();
        });
    } else {
        // 重新加载当前文件或清空数据
        if (props.selectedFile && props.selectedFile.type === 'card') {
            loadCardData();
        } else {
            clearFormData();
        }
    }
};

// 清空表单数据
const clearFormData = () => {
    clearDebounceTimer();

    Object.keys(currentCardData).forEach(key => {
        delete currentCardData[key];
    });
    Object.assign(currentCardData, {
        type: '',
        name: '',
        id: '',
        created_at: '',
        version: '1.0',
        language: 'zh', // 新增：默认语言
    });
    currentCardType.value = '';
    saveOriginalData();
};

// 过滤后的JSON数据（排除base64图片字段和tts_script字段）
const filteredJsonData = computed(() => {
    const filteredData = { ...currentCardData };

    // 删除所有base64图片字段
    const imageFields = ['picture_base64', 'avatar_base64', 'background_base64'];

    imageFields.forEach(field => {
        if (field in filteredData) {
            delete filteredData[field];
        }
    });

    // 删除tts_script字段
    if ('tts_script' in filteredData) {
        delete filteredData['tts_script'];
    }

    // 如果有嵌套对象，也要处理嵌套的base64字段和tts_script字段
    const removeBase64FromObject = (obj: any): any => {
        if (typeof obj !== 'object' || obj === null) {
            return obj;
        }

        if (Array.isArray(obj)) {
            return obj.map(item => removeBase64FromObject(item));
        }

        const result = {};
        for (const [key, value] of Object.entries(obj)) {
            // 跳过包含base64的字段和tts_script字段
            if (key === 'tts_script' || key.includes('base64') || (typeof value === 'string' && value.startsWith('data:image'))) {
                continue;
            }
            result[key] = removeBase64FromObject(value);
        }
        return result;
    };

    return JSON.stringify(removeBase64FromObject(filteredData), null, 2);
});

// 预览卡图
const previewCard = async () => {
    if (!hasValidCardData.value) {
        message.warning(t('cardEditor.panel.pleaseEnterCardNameAndType'));
        return;
    }

    try {
        generating.value = true;
        // 清除防抖定时器，避免重复生成
        clearDebounceTimer();

        // 【移除】手动预览时不显示卡牌形状加载动画
        // imagePreviewLoading.value = true;
        // emit('update-preview-loading', true);
        console.log('🔄 手动预览卡图，不显示特殊加载动画');

        // 【重要】调用统一的autoGeneratePreview，不结束加载动画
        await autoGeneratePreview(false);
        message.success(t('cardEditor.panel.cardPreviewGenerated'));
    } catch (error) {
        console.error('预览卡图失败:', error);
    } finally {
        // 【移除】手动预览时不显示卡牌形状加载动画
        // imagePreviewLoading.value = false;
        // emit('update-preview-loading', false);
        console.log('✅ 手动预览完成');
        generating.value = false;
    }
};

// 导出图片
const exportCard = async () => {
    if (!hasValidCardData.value) {
        message.warning(t('cardEditor.panel.pleaseEnterCardNameAndType'));
        return;
    }

    if (!props.selectedFile || !props.selectedFile.path) {
        message.warning(t('cardEditor.panel.noCardFileSelected'));
        return;
    }

    try {
        exporting.value = true;

        // 获取卡牌文件所在的目录
        const filePath = props.selectedFile.path;
        const parentPath = filePath.substring(0, filePath.lastIndexOf('/'));

        // 使用文件名作为导出的图片文件名，去掉.card扩展名
        const cardFileName = props.selectedFile.label?.replace('.card', '') || 'untitled';

        console.log('使用文件名作为导出文件名:', cardFileName);

        // 使用增强版保存卡牌API，支持双面卡牌和格式选择
        const savedFiles = await CardService.saveCardEnhanced(currentCardData as CardData, cardFileName, {
            parentPath,
            format: 'PNG', // 可以改为 'JPG' 如果需要
            quality: 95    // 仅对JPG格式有效
        });

        // 刷新文件树以显示新生成的图片文件
        emit('refresh-file-tree');

        // 根据保存的文件数量显示不同的成功消息
        if (savedFiles.length === 1) {
            message.success(t('cardEditor.panel.imageExported', { filename: savedFiles[0] }));
        } else if (savedFiles.length === 2) {
            message.success(`双面卡牌导出成功: ${savedFiles.join(', ')}`);
        } else {
            message.warning('未保存任何文件');
        }
    } catch (error) {
        console.error('导出图片失败:', error);
        message.error(`${t('cardEditor.panel.exportImageFailed')}: ${error.message || '未知错误'}`);
    } finally {
        exporting.value = false;
    }
};

const resetForm = () => {
    clearDebounceTimer();

    // 保留共享数据和根级字段
    const hiddenFields = ['id', 'created_at', 'version', 'language', 'deck_options', 'quantity', 'footer_copyright', 'tts_script'];
    const hiddenData = {};
    hiddenFields.forEach(field => {
        if (currentCardData[field] !== undefined) {
            hiddenData[field] = currentCardData[field];
        }
    });

    // 保留背面的基础结构
    const backData = currentCardData.back ? { language: currentCardData.back.language || 'zh' } : undefined;

    // 清空当前数据
    Object.keys(currentCardData).forEach(key => {
        delete currentCardData[key];
    });

    // 重新赋值，保留共享数据
    Object.assign(currentCardData, hiddenData, {
        type: '',
        name: '',
        language: hiddenData.language || 'zh',
        quantity: hiddenData.quantity || 1,
        back: backData
    });

    // 如果是调查员卡，重置属性数组
    if (currentCardData.type === '调查员') {
        currentCardData.attribute = [];
    }

    currentCardType.value = '';
    saveOriginalData();
    message.info(t('cardEditor.panel.formReset'));
};

// 版本转换功能
const convertToVersion2 = async () => {
    if (!currentCardData.type || !currentCardData.name) {
        message.warning(t('cardEditor.panel.needCardNameAndType'));
        return;
    }

    try {
        converting.value = true;

        // 设置版本为2.0
        currentCardData.version = '2.0';

        // 创建背面数据结构
        if (!currentCardData.back) {
            currentCardData.back = {};
        }

        // 设置背面语言与正面一致
        currentCardData.back.language = currentCardData.language || 'zh';

        // 根据正面类型设置默认背面类型
        const defaultBackConfig = getDefaultBackType(currentCardData.type);
        if (defaultBackConfig) {
            currentCardData.back.type = defaultBackConfig.type;

            // 如果需要设置is_back字段
            if (defaultBackConfig.is_back !== undefined) {
                currentCardData.back.is_back = defaultBackConfig.is_back;
            }

            // 如果需要设置location_type字段
            if (defaultBackConfig.location_type !== undefined) {
                currentCardData.back.location_type = defaultBackConfig.location_type;
            }

            console.log(`🔄 版本转换完成，设置背面类型: ${defaultBackConfig.type}, is_back: ${defaultBackConfig.is_back}`);
        } else {
            // 如果没有找到特定配置，使用默认卡背
            currentCardData.back.type = '卡背';
            console.log('🔄 版本转换完成，使用默认卡背');
        }

        // 关闭对话框
        showVersionConvertDialog.value = false;

        // 保存原始数据状态，标记为已修改
        saveOriginalData();

        // 触发防抖预览更新
        triggerDebouncedPreviewUpdate();

        message.success(t('cardEditor.panel.versionConvertSuccess'));

        // 切换到背面编辑面，让用户可以看到新生成的背面
        setTimeout(() => {
            currentSide.value = 'back';
        }, 300);

    } catch (error) {
        console.error('版本转换失败:', error);
        message.error(t('cardEditor.panel.versionConvertFailed'));
    } finally {
        converting.value = false;
    }
};

// 监听选中文件变化
watch(() => props.selectedFile, async (newFile, oldFile) => {
    // 【修复】如果切换前的文件是卡牌且有未保存修改，暂存数据
    // 注意：不能使用 hasUnsavedChanges，因为此时 props.selectedFile 已经变成新文件
    if (oldFile && oldFile.type === 'card' && oldFile.path) {
        const currentDataString = JSON.stringify(currentCardData);
        const hasChanges = originalCardData.value !== currentDataString;

        if (hasChanges) {
            console.log('💾 检测到未保存修改，暂存当前数据:', oldFile.path);
            emit('save-to-cache', oldFile.path as string, currentCardData);
        }
    }

    // 如果是切换到新文件，先重置状态
    if (newFile && newFile !== oldFile) {
        if (newFile.type === 'card') {
            console.log('🔄 切换到新卡牌，重置编辑器状态');

            // 1. 重置当前面为正面
            currentSide.value = 'front';

            // 2. 清空卡牌类型，触发表单卸载
            currentCardType.value = '';

            // 3. 通知父组件清空图片预览
            emit('update-preview-image', '');

            // 4. 清除防抖定时器
            clearDebounceTimer();

            // 5. 清空当前数据状态
            Object.keys(currentCardData).forEach(key => {
                delete currentCardData[key];
            });

            // 6. 重置导航栏状态
            activeSection.value = 'cardType';
            isNavCollapsed.value = true;

            // 等待DOM更新，确保状态完全重置
            await nextTick();

            console.log('✅ 编辑器状态重置完成，开始加载新卡牌数据');
        } else {
            // 如果不是卡牌文件，也要清空预览
            emit('update-preview-image', '');
            console.log('🔄 切换到非卡牌文件，清空预览');
        }
    }

    // 清空原始文件信息
    originalFileInfo.value = null;

    if (newFile && newFile.type === 'card') {
        // 【新增】切换文件时显示加载动画
        imagePreviewLoading.value = true;
        emit('update-preview-loading', true);
        console.log('🔄 切换文件，开始显示卡牌形状加载动画');

        // 【新增】通知父组件加载数据（父组件会检查是否有暂存并调用相应方法）
        emit('load-from-cache', newFile.path as string);

        // 等待父组件处理完暂存逻辑后，如果没有暂存则正常加载
        // 注意：这里不直接调用loadCardData，而是让WorkspaceMain决定
    } else {
        clearFormData();
    }
}, { immediate: true });

// 监听卡牌数据变化，触发防抖预览更新
watch(() => currentCardData, () => {
    // 只在用户编辑时触发防抖更新，避免初始加载时触发
    if (!saving.value && props.selectedFile) {
        triggerDebouncedPreviewUpdate();
    }
}, { deep: true });


// 组件挂载时添加键盘事件监听器
onMounted(() => {
    document.addEventListener('keydown', handleKeydown);

    // 添加滚动监听
    const formContent = document.querySelector('.form-content');
    if (formContent) {
        formContent.addEventListener('scroll', handleScroll);
    }
});

// 从外部设置当前编辑的面（用于图片预览同步）
const setSideFromExternal = (side: 'front' | 'back') => {
    currentSide.value = side;
    console.log(`🔄 从外部设置编辑器面为: ${side}`);
};

// 【新增】从暂存数据加载（外部调用）
const loadFromCacheData = async (cachedData: any) => {
    if (!cachedData) return;

    try {
        console.log('📂 从暂存数据加载卡牌');

        // 清空卡牌类型，触发表单卸载
        currentCardType.value = '';

        // 清空当前数据
        Object.keys(currentCardData).forEach(key => {
            delete currentCardData[key];
        });

        // 等待DOM更新
        await nextTick();

        // 加载暂存数据
        Object.keys(cachedData).forEach(key => {
            if (key === 'deck_options' && Array.isArray(cachedData[key])) {
                currentCardData[key] = [...cachedData[key]];
            } else {
                currentCardData[key] = cachedData[key];
            }
        });

        // 设置卡牌类型
        currentCardType.value = cachedData.type || '';

        await nextTick();

        // 保存原始数据状态
        setTimeout(() => {
            // 注意：从暂存加载时不更新originalCardData，保持未保存状态
            lastDataSnapshot.value = JSON.stringify(currentCardData);
            console.log('✅ 从暂存加载完成，保持未保存状态');

            // 【修复】自动生成预览图片，并结束加载动画
            autoGeneratePreview(true);
        }, 100);

    } catch (error) {
        console.error('从暂存加载失败:', error);
        message.error(t('cardEditor.panel.loadFromCacheFailed'));

        // 加载失败也要结束加载动画
        imagePreviewLoading.value = false;
        emit('update-preview-loading', false);
    }
};

// 【新增】保存所有未保存的文件
const saveAllUnsaved = async (unsavedPaths: string[], cacheMap: Map<string, any>) => {
    if (unsavedPaths.length === 0) {
        message.info(t('cardEditor.panel.noUnsavedFiles'));
        return;
    }

    let successCount = 0;
    let failCount = 0;

    console.log(`💾 开始批量保存 ${unsavedPaths.length} 个文件`);

    for (const filePath of unsavedPaths) {
        try {
            const cachedData = cacheMap.get(filePath);
            if (!cachedData) {
                console.warn(`⚠️ 文件 ${filePath} 没有暂存数据，跳过`);
                continue;
            }

            // 冻结路径并为本次保存创建快照，避免保存过程被后续修改污染
            const frozenPath = filePath;
            let snapshot: any | null = null;
            try {
                snapshot = JSON.parse(JSON.stringify(cachedData));
            } catch (e) {
                console.error('创建批量保存快照失败:', e);
                failCount++;
                continue;
            }

            // 保存前生成 GMNotes，确保脚本 ID 持久化
            await ensureScriptIdByBackend(snapshot);

            // 在保存前计算并写入内容哈希（排除 content_hash 自身）
            try {
                const hash = await computeCardContentHash(snapshot);
                (snapshot as any).content_hash = hash;
            } catch (e) {
                console.warn('计算卡牌内容哈希失败（批量保存）:', e);
            }

            // 直接保存JSON文件（不需要生成预览）
            const jsonContent = JSON.stringify(snapshot, null, 2);
            await WorkspaceService.saveFileContent(frozenPath, jsonContent);

            // 清除暂存
            emit('clear-cache', frozenPath);

            snapshot = null; // 显式清理，便于 GC

            successCount++;
            console.log(`✅ 保存成功: ${frozenPath}`);
        } catch (error) {
            console.error(`❌ 保存失败: ${filePath}`, error);
            failCount++;
        }
    }

    // 刷新文件树
    emit('refresh-file-tree');

    // 如果当前文件也被保存了，更新原始数据状态
    if (props.selectedFile?.path && unsavedPaths.includes(props.selectedFile.path as string)) {
        const currentState = JSON.stringify(currentCardData);
        const cachedState = JSON.stringify(cacheMap.get(props.selectedFile.path as string));
        if (currentState === cachedState) {
            saveOriginalData();
        }
    }

    // 显示保存结果
    if (successCount > 0 && failCount === 0) {
        message.success(t('cardEditor.panel.saveAllSuccess', { count: successCount }));
    } else if (successCount > 0 && failCount > 0) {
        message.warning(t('cardEditor.panel.saveAllPartial', { success: successCount, failed: failCount }));
    } else {
        message.error(t('cardEditor.panel.saveAllFailed'));
    }
};

// 导出方法供父组件调用
defineExpose({
    setSideFromExternal,
    loadFromCacheData,
    saveAllUnsaved,
    loadCardData // 暴露loadCardData方法供父组件调用
});

// 组件卸载时移除键盘事件监听器和清理定时器
onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
    clearDebounceTimer();

    // 移除滚动监听
    const formContent = document.querySelector('.form-content');
    if (formContent) {
        formContent.removeEventListener('scroll', handleScroll);
    }
});
</script>

<style scoped>
.form-pane {
    flex: 1;
    min-width: 300px;
    width: 100%;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    box-sizing: border-box;
    position: relative;
}

/* 快速导航条 */
.quick-nav {
    position: fixed;
    right: 20px;
    top: 80px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 6px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.nav-item {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #666;
    background: transparent;
}

.nav-item:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    transform: scale(1.05);
}

.nav-item.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 1px 4px rgba(102, 126, 234, 0.3);
}

/* 收起按钮样式 */
.nav-collapse {
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

/* 分隔线样式 */
.nav-divider {
    height: 1px;
    background: rgba(0, 0, 0, 0.08);
    margin: 4px 0;
}

/* 快速导航条 - 收起状态的小圆圈按钮 */
.quick-nav-toggle {
    position: fixed;
    right: 20px;
    top: 80px;
    z-index: 1000;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.quick-nav-toggle:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

/* 移动端适配 */
@media (max-width: 768px) {
    .quick-nav {
        right: 10px;
        top: 70px;
        padding: 6px 4px;
        gap: 6px;
    }

    .nav-item {
        width: 28px;
        height: 28px;
    }

    .quick-nav-toggle {
        right: 10px;
        top: 70px;
        width: 36px;
        height: 36px;
    }
}

/* 响应式设计 - 小屏幕隐藏导航条 */
@media (max-width: 480px) {
    .quick-nav {
        display: none;
    }

    .quick-nav-toggle {
        display: none;
    }
}


.pane-header {
    flex-shrink: 0;
    padding: 12px 16px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.pane-title {
    font-weight: 600;
    font-size: 14px;
    color: white;
    display: flex;
    align-items: center;
    gap: 4px;
}

.unsaved-indicator {
    color: #fbbf24;
    font-weight: bold;
    font-size: 16px;
    line-height: 1;
}

.keyboard-shortcut {
    font-size: 12px;
    opacity: 0.7;
    margin-left: 4px;
}

/* 头部按钮样式统一 */
.header-button {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    transition: all 0.2s ease;
}

.header-button:hover {
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.header-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-content {
    flex: 1;
    overflow: auto;
    background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
    /* 移动端滚动优化 */
    -webkit-overflow-scrolling: touch;
    /* 确保滚动容器在移动端有正确的高度 */
    height: 0;
}

.empty-state {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.form-wrapper {
    padding: 24px;
}

.form-card {
    margin-bottom: 20px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s ease;
}

.form-card:hover {
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}


/* JSON模态框样式 */
.json-modal-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 95vw;
    width: auto;
}

.json-display-container {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #f8f9fa;
    overflow: hidden;
}

.json-code-display {
    width: 100%;
    box-sizing: border-box;
    white-space: pre;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.4;
    padding: 16px;
    margin: 0;
    background: transparent;
}

.json-actions {
    display: flex;
    justify-content: flex-end;
    padding-top: 12px;
    border-top: 1px solid #e0e0e0;
}

.copy-button {
    background: #667eea;
    border-color: #667eea;
}

.copy-button:hover {
    background: #5a67d8;
    border-color: #5a67d8;
}

/* 双面卡牌切换器样式 */
.card-side-selector {
    display: flex;
    justify-content: center;
    padding: 16px 0;
    border-bottom: 1px solid rgba(102, 126, 234, 0.1);
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    margin-bottom: 20px;
}

/* 共享组件区域样式 */
.shared-components {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 2px solid rgba(102, 126, 234, 0.2);
    background: rgba(102, 126, 234, 0.03);
    border-radius: 12px;
    padding: 24px;
}

.card-side-selector :deep(.n-radio-group) {
    background: rgba(102, 126, 234, 0.05);
    border-radius: 8px;
    padding: 4px;
}

.card-side-selector :deep(.n-radio-button) {
    font-weight: 500;
    transition: all 0.2s ease;
}

.card-side-selector :deep(.n-radio-button--checked) {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.form-actions {
    margin-top: 32px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    border-top: 3px solid #667eea;
}

/* 欢迎指导界面样式 */
.welcome-guide {
    text-align: center;
    padding: 80px 40px 60px 40px;
    /* 增加顶部padding避免被标题栏挡住 */
    max-width: 600px;
    margin: 0 auto;
    background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.05) 0%,
            rgba(118, 75, 162, 0.05) 50%,
            rgba(255, 255, 255, 0.8) 100%);
    border-radius: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    animation: fadeInUp 0.6s ease-out;
}


.welcome-title {
    font-size: 2rem;
    font-weight: 700;
    color: #2d3748;
    margin: 0 0 16px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.welcome-subtitle {
    font-size: 1.2rem;
    color: #64748b;
    margin: 0 0 40px 0;
    font-weight: 400;
    line-height: 1.6;
}

.guide-section {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 16px;
    padding: 32px 24px;
    margin: 32px 0;
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.guide-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 24px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.guide-title::before {
    content: '💡';
    font-size: 1.2em;
}

.guide-steps {
    display: flex;
    flex-direction: column;
    gap: 20px;
    text-align: left;
}

.guide-step {
    display: flex;
    align-items: center;
    /* 修改为垂直居中对齐 */
    gap: 16px;
    padding: 16px 20px;
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.8) 0%,
            rgba(248, 250, 252, 0.9) 100%);
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.6);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.guide-step::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.guide-step:hover {
    transform: translateX(4px);
    background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.08) 0%,
            rgba(255, 255, 255, 0.9) 100%);
    border-color: rgba(102, 126, 234, 0.3);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
}

.guide-step:hover::before {
    opacity: 1;
}

.step-icon {
    font-size: 1.5rem;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
}

.guide-step:hover .step-icon {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.step-content {
    flex: 1;
    min-width: 0;
}

.step-text {
    font-size: 1rem;
    color: #374151;
    font-weight: 500;
    line-height: 1.6;
    margin: 0;
}

.welcome-footer {
    margin-top: 40px;
    padding-top: 32px;
    border-top: 1px solid rgba(226, 232, 240, 0.6);
}

.encourage-text {
    font-size: 1.1rem;
    color: #667eea;
    font-weight: 600;
    margin: 0;
    position: relative;
}

.encourage-text::before {
    content: '✨';
    margin-right: 8px;
}

.encourage-text::after {
    content: '✨';
    margin-left: 8px;
}

/* 动画效果 */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* 响应式设计 */
@media (max-width: 768px) {
    .welcome-guide {
        padding: 40px 24px;
        margin: 20px;
    }

    .welcome-title {
        font-size: 1.6rem;
    }

    .welcome-subtitle {
        font-size: 1rem;
    }

    .guide-section {
        padding: 24px 16px;
        margin: 24px 0;
    }

    .guide-title {
        font-size: 1.2rem;
    }

    .guide-step {
        padding: 12px 16px;
        gap: 12px;
    }

    .step-icon {
        width: 40px;
        height: 40px;
        font-size: 1.2rem;
    }

    .step-text {
        font-size: 0.9rem;
    }
}

@media (max-width: 480px) {
    .form-pane {
        min-width: 100%;
        width: 100%;
        height: 100vh;
        /* 确保移动端占满视口高度 */
        display: flex;
        flex-direction: column;
    }

    .pane-header {
        padding: 8px 12px;
        min-width: auto;
        width: 100%;
        box-sizing: border-box;
        flex-shrink: 0;
        /* 防止头部被压缩 */
    }

    .pane-title {
        font-size: 16px;
    }

    /* 优化移动端滚动容器 */
    .form-content {
        height: 0;
        /* 让flex子元素正确计算高度 */
        flex: 1;
        overflow-y: auto;
        /* 只允许垂直滚动 */
        -webkit-overflow-scrolling: touch;
        /* iOS平滑滚动 */
    }

    .form-wrapper {
        padding: 16px 12px;
        /* 移动端减少内边距 */
        min-height: min-content;
        /* 确保内容能完整显示 */
    }

    /* 模态框移动端适配 */
    .json-modal-content {
        max-width: 95vw;
        width: auto;
    }

    .welcome-guide {
        padding: 30px 16px;
        margin: 10px;
    }

    .welcome-icon {
        font-size: 3rem;
        margin-bottom: 16px;
    }

    .welcome-title {
        font-size: 1.4rem;
    }

    .guide-steps {
        gap: 16px;
    }

    .guide-step {
        padding: 10px 12px;
        gap: 10px;
    }

    .step-icon {
        width: 36px;
        height: 36px;
        font-size: 1.1rem;
    }

    /* 移动端操作按钮区域优化 */
    .form-actions {
        padding: 16px 12px;
        margin-top: 24px;
        flex-shrink: 0;
        /* 防止操作按钮被压缩 */
    }

    .form-actions :deep(.n-space) {
        flex-wrap: wrap;
        gap: 8px !important;
    }

    .form-actions :deep(.n-button) {
        flex: 1;
        min-width: 0;
    }
}
</style>

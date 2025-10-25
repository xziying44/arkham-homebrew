<template>
    <div class="form-pane">
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
                    <n-button size="tiny" @click="showImportJsonModal = true" class="header-button">{{
                        $t('cardEditor.panel.importJson') }}</n-button>
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
                        <TtsScriptEditor :card-data="currentCardData" :card-type="currentCardType"
                            :is-double-sided="isDoubleSided" :current-side="currentSide"
                            @update-tts-script="updateTtsScript" />

                        <!-- 牌库选项编辑器 -->
                        <DeckOptionEditor :card-data="currentCardData" :card-type="currentSideType"
                            :is-double-sided="isDoubleSided" :current-side="currentSide"
                            @update-deck-options="updateDeckOptions" />
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

        <!-- 导入JSON模态框 -->
        <n-modal v-model:show="showImportJsonModal" preset="dialog" :title="$t('cardEditor.panel.importJsonData')">
            <div class="import-json-content">
                <n-form-item :label="$t('cardEditor.panel.pasteJsonData')">
                    <n-input v-model:value="importJsonText" type="textarea"
                        :placeholder="$t('cardEditor.panel.pasteJsonPlaceholder')" :rows="10" maxlength="50000"
                        show-count class="import-textarea" />
                </n-form-item>
                <div v-if="importJsonError" class="import-error">
                    <n-alert type="error" :title="importJsonError" />
                </div>
            </div>
            <template #action>
                <n-space>
                    <n-button @click="cancelImportJson">{{ $t('cardEditor.panel.cancel') }}</n-button>
                    <n-button type="primary" @click="importJsonData" :disabled="!importJsonText.trim()">
                        {{ $t('cardEditor.panel.import') }}
                    </n-button>
                </n-space>
            </template>
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
    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { FolderOpenOutline, ImageOutline, WarningOutline, CopyOutline } from '@vicons/ionicons5';
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

import { WorkspaceService, CardService, ConfigService } from '@/api';
import type { CardData } from '@/api/types';
import TtsScriptEditor from './TtsScriptEditor.vue';
import { generateUpgradePowerWordScript } from '@/config/upgrade-script-generator';

interface Props {
    showFileTree: boolean;
    showImagePreview: boolean;
    selectedFile?: TreeOption | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'toggle-file-tree': [];
    'toggle-image-preview': [];
    'update-preview-image': [image: string | { front: string; back?: string }];
    'update-preview-side': [side: 'front' | 'back'];
    'update-preview-loading': [loading: boolean];
    'refresh-file-tree': [];
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


// 新增：语言选项
const languageOptions = computed(() => [
    {
        label: "中文",
        value: 'zh'
    },
    {
        label: "English",
        value: 'en'
    },
    {
        label: "Polski",
        value: 'pl'
    }
]);

// 获取当前语言对应的默认背面配置函数
const getDefaultBackType = (frontType: string): { type: string; is_back?: boolean } | null => {
    const getDefaultBackTypeFunc = locale.value === 'en' ? getDefaultBackTypeEn : getDefaultBackTypeZh;
    return getDefaultBackTypeFunc(frontType);
};

// 原始数据状态 - 用于检测修改
const originalCardData = ref<string>('');

// 原始文件信息 - 用于记住需要保存的文件
const originalFileInfo = ref<{ path: string; label: string } | null>(null);

// 待切换的文件
const pendingSwitchFile = ref<TreeOption | null>(null);

const currentCardType = ref('');
const showJsonModal = ref(false);
const showImportJsonModal = ref(false);
const showSaveConfirmDialog = ref(false);
const saving = ref(false);
const generating = ref(false);
const exporting = ref(false);

// 新增：图片预览加载状态
const imagePreviewLoading = ref(false);

// 导入JSON相关状态
const importJsonText = ref('');
const importJsonError = ref('');

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

// 导入JSON数据
const importJsonData = async () => {
    importJsonError.value = '';

    if (!importJsonText.value.trim()) {
        message.warning(t('cardEditor.panel.pleaseEnterJsonData'));
        return;
    }

    try {
        // 解析JSON
        const jsonData = JSON.parse(importJsonText.value.trim());

        // 验证是否是有效的卡牌数据
        if (typeof jsonData !== 'object' || jsonData === null) {
            throw new Error(t('cardEditor.panel.invalidJsonFormat'));
        }

        // 保存当前的元数据
        const metadata = {
            id: currentCardData.id || '',
            created_at: currentCardData.created_at || '',
            version: currentCardData.version || '1.0',
        };

        // 合并数据
        const newData = { ...metadata, ...jsonData };

        // 清空当前数据
        Object.keys(currentCardData).forEach(key => {
            delete currentCardData[key];
        });

        // 等待DOM更新
        await nextTick();

        // 重新赋值 - 修复：确保deck_options等数组字段正确复制
        Object.keys(newData).forEach(key => {
            if (key === 'deck_options' && Array.isArray(newData[key])) {
                // 对于数组类型，创建新的数组引用避免响应式问题
                currentCardData[key] = [...newData[key]];
                console.log('📚 导入deck_options数据:', currentCardData[key].length, '个选项');
            } else {
                currentCardData[key] = newData[key];
            }
        });

        // 更新卡牌类型
        if (jsonData.type) {
            currentCardType.value = jsonData.type;
        }

        // 关闭模态框
        showImportJsonModal.value = false;
        importJsonText.value = '';

        // 触发防抖预览更新
        triggerDebouncedPreviewUpdate();

        message.success(t('cardEditor.panel.jsonDataImportedSuccessfully'));
    } catch (error) {
        console.error('导入JSON失败:', error);
        importJsonError.value = `${t('cardEditor.panel.importFailed')}: ${error.message || t('cardEditor.panel.invalidJsonFormat')}`;
    }
};

// 取消导入JSON
const cancelImportJson = () => {
    showImportJsonModal.value = false;
    importJsonText.value = '';
    importJsonError.value = '';
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

// 检查是否有任何有效的卡牌数据（用于共享组件显示）
const hasAnyValidCardData = computed(() => {
    const hasValidFront = currentCardData.name && currentCardData.name.trim() !== '' &&
        currentCardData.type && currentCardData.type.trim() !== '';

    const hasValidBack = isDoubleSided.value &&
        currentCardData.back &&
        currentCardData.back.name && currentCardData.back.name.trim() !== '' &&
        currentCardData.back.type && currentCardData.back.type.trim() !== '';

    return hasValidFront || hasValidBack;
});

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

    // 更新currentCardData中的tts_script字段
    if (!currentCardData.tts_script) {
        currentCardData.tts_script = {};
    }

    currentCardData.tts_script.GMNotes = ttsData.GMNotes;
    currentCardData.tts_script.LuaScript = ttsData.LuaScript;

    // 新增：保存config配置
    if (ttsData.config) {
        currentCardData.tts_script.config = ttsData.config;
    }

    // 如果所有字段都为空，则删除tts_script字段
    if (!ttsData.GMNotes && !ttsData.LuaScript && !ttsData.config) {
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

        const content = await WorkspaceService.getFileContent(props.selectedFile.path);
        const cardData = JSON.parse(content || '{}');

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

        // 双面卡牌额外处理：确保图片预览立即更新
        if (cardData.version === '2.0') {
            console.log('🔄 检测到双面卡牌，立即触发预览更新');
            setTimeout(() => {
                autoGeneratePreview(true);
            }, 200);
        }
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
    // 优先使用原始文件信息，如果没有则使用当前选中文件
    const fileToSave = originalFileInfo.value || props.selectedFile;
    if (!fileToSave || !fileToSave.path) {
        message.warning(t('cardEditor.panel.noFileSelected'));
        return false;
    }
    // 如果已经在保存，直接返回
    if (saving.value) {
        console.log('已在保存中，跳过');
        return false;
    }
    try {
        saving.value = true;
        // 清除防抖定时器，避免保存时生成预览
        clearDebounceTimer();

        // 生成卡片并检查box_position
        const result_card = await CardService.generateCard(currentCardData as CardData);

        // 检查是否为定制卡且有box_position参数
        if (currentCardData.type === '定制卡' && result_card?.box_position && result_card.box_position.length > 0) {
            console.log('🎯 定制卡检测到box_position，生成Lua脚本:', result_card.box_position);

            try {
                // 生成定制卡的Lua脚本
                const luaScript = generateUpgradePowerWordScript(result_card.box_position);

                // 更新TTS脚本数据
                if (!currentCardData.tts_script) {
                    currentCardData.tts_script = {};
                }

                // 保存生成的Lua脚本
                currentCardData.tts_script.LuaScript = luaScript;

                console.log('✅ 定制卡Lua脚本生成成功');
                // message.success(t('cardEditor.panel.customCardLuaGenerated'));
            } catch (error) {
                console.error('❌ 生成定制卡Lua脚本失败:', error);
                message.warning(`生成定制卡脚本失败: ${error.message || '未知错误'}`);
            }
        }

        // 保存JSON文件
        const jsonContent = JSON.stringify(currentCardData, null, 2);
        await WorkspaceService.saveFileContent(fileToSave.path, jsonContent);
        // 更新原始数据状态
        saveOriginalData();
        // 显示卡图（使用已生成的结果）
        const imageBase64 = result_card?.image;
        if (imageBase64) {
            // 检查是否为双面卡牌，确保传递正确的数据格式
            if (result_card?.back_image) {
                const doubleSidedImage = {
                    front: imageBase64,
                    back: result_card.back_image
                };
                emit('update-preview-image', doubleSidedImage);
                console.log('✅ 保存后双面卡牌预览更新成功');
            } else {
                emit('update-preview-image', imageBase64);
                console.log('✅ 保存后单面卡牌预览更新成功');
            }
        }
        message.success(t('cardEditor.panel.cardSavedSuccessfully'));
        return true;
    } catch (error) {
        console.error('保存卡牌失败:', error);
        message.error(t('cardEditor.panel.saveCardFailed'));
        return false;
    } finally {
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

// 过滤后的JSON数据（排除base64图片字段）
const filteredJsonData = computed(() => {
    const filteredData = { ...currentCardData };

    // 删除所有base64图片字段
    const imageFields = ['picture_base64', 'avatar_base64', 'background_base64']; // 可以根据需要添加更多字段

    imageFields.forEach(field => {
        if (field in filteredData) {
            delete filteredData[field];
        }
    });

    // 如果有嵌套对象，也要处理嵌套的base64字段
    const removeBase64FromObject = (obj: any): any => {
        if (typeof obj !== 'object' || obj === null) {
            return obj;
        }

        if (Array.isArray(obj)) {
            return obj.map(item => removeBase64FromObject(item));
        }

        const result = {};
        for (const [key, value] of Object.entries(obj)) {
            // 跳过包含base64的字段
            if (key.includes('base64') || (typeof value === 'string' && value.startsWith('data:image'))) {
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

// 监听选中文件变化
watch(() => props.selectedFile, async (newFile, oldFile) => {
    // 如果当前有未保存的修改，显示确认对话框
    if (hasUnsavedChanges.value && oldFile) {
        // 记住原始文件信息（用于保存）
        originalFileInfo.value = {
            path: oldFile.path as string,
            label: oldFile.label as string
        };

        pendingSwitchFile.value = newFile;
        showSaveConfirmDialog.value = true;
        return;
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

            // 等待DOM更新，确保状态完全重置
            await nextTick();

            console.log('✅ 编辑器状态重置完成，开始加载新卡牌数据');
        } else {
            // 如果不是卡牌文件，也要清空预览
            emit('update-preview-image', '');
            console.log('🔄 切换到非卡牌文件，清空预览');
        }
    }

    // 没有未保存修改，直接切换
    originalFileInfo.value = null;
    if (newFile && newFile.type === 'card') {
        // 【新增】直接切换文件时显示加载动画
        imagePreviewLoading.value = true;
        emit('update-preview-loading', true);
        console.log('🔄 直接切换文件，开始显示卡牌形状加载动画');

        await loadCardData();
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
});

// 从外部设置当前编辑的面（用于图片预览同步）
const setSideFromExternal = (side: 'front' | 'back') => {
    currentSide.value = side;
    console.log(`🔄 从外部设置编辑器面为: ${side}`);
};

// 导出方法供父组件调用
defineExpose({
    setSideFromExternal
});

// 组件卸载时移除键盘事件监听器和清理定时器
onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
    clearDebounceTimer();
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

/* 导入JSON模态框样式 */
.import-json-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-height: 300px;
    max-width: 95vw;
    width: auto;
}

.import-textarea {
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

.import-error {
    margin-top: 12px;
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
    padding: 80px 40px 60px 40px; /* 增加顶部padding避免被标题栏挡住 */
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
    align-items: center; /* 修改为垂直居中对齐 */
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
        height: 100vh; /* 确保移动端占满视口高度 */
        display: flex;
        flex-direction: column;
    }

    .pane-header {
        padding: 8px 12px;
        min-width: auto;
        width: 100%;
        box-sizing: border-box;
        flex-shrink: 0; /* 防止头部被压缩 */
    }

    .pane-title {
        font-size: 16px;
    }

    /* 优化移动端滚动容器 */
    .form-content {
        height: 0; /* 让flex子元素正确计算高度 */
        flex: 1;
        overflow-y: auto; /* 只允许垂直滚动 */
        -webkit-overflow-scrolling: touch; /* iOS平滑滚动 */
    }

    .form-wrapper {
        padding: 16px 12px; /* 移动端减少内边距 */
        min-height: min-content; /* 确保内容能完整显示 */
    }

    /* 模态框移动端适配 */
    .json-modal-content {
        max-width: 95vw;
        width: auto;
    }

    .import-json-content {
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
        flex-shrink: 0; /* 防止操作按钮被压缩 */
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

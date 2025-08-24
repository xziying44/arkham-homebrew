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
                        {{ selectedFile?.label || '卡牌编辑器' }}
                        <span v-if="hasUnsavedChanges" class="unsaved-indicator">*</span>
                    </span>
                </n-space>
                <n-space size="small">
                    <n-button size="tiny" @click="showJsonModal = true" class="header-button"
                        v-if="selectedFile">查看JSON</n-button>
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
                <n-empty description="请在文件管理器中选择一个卡牌文件(.card)进行编辑" />
            </div>

            <!-- 卡牌编辑器内容 -->
            <n-scrollbar v-else>
                <div class="form-wrapper">
                    <!-- AI制卡区域 -->
                    <n-card v-if="aiEnabledInEditor" title="🤖 AI制卡助手" size="small" class="form-card ai-card">
                        <n-space vertical size="medium">
                            <!-- 提示词输入 -->
                            <n-form-item label="描述你想要的卡牌">
                                <n-input v-model:value="aiPrompt" type="textarea"
                                    placeholder="例如：创建一个火属性的攻击法术卡牌，名字叫火球术，造成5点伤害，消耗3点法力..." :rows="3"
                                    :disabled="aiGenerating" maxlength="500" show-count />
                            </n-form-item>

                            <!-- 控制按钮 -->
                            <n-space>
                                <n-button type="primary" :loading="aiGenerating" :disabled="!aiPrompt.trim()"
                                    @click="startAIGeneration">
                                    <template #icon>
                                        <n-icon :component="SparklesIcon" />
                                    </template>
                                    {{ aiGenerating ? '生成中...' : '生成卡牌' }}
                                </n-button>
                                <n-button v-if="aiGenerating" @click="stopAIGeneration">
                                    停止生成
                                </n-button>
                                <n-button v-if="aiResult" @click="clearAIResult">
                                    清空结果
                                </n-button>
                            </n-space>

                            <!-- AI生成结果展示 -->
                            <div v-if="aiGenerating || aiResult" class="ai-result-container">
                                <n-card size="small" class="ai-result-card">
                                    <template #header>
                                        <n-space align="center">
                                            <n-icon :component="aiGenerating ? LoadingOutline : CheckmarkCircleOutline"
                                                :class="{ 'spinning': aiGenerating }" />
                                            <span>{{ aiGenerating ? 'AI正在思考中...' : '生成完成' }}</span>
                                        </n-space>
                                    </template>

                                    <!-- 思考过程展示 -->
                                    <div v-if="aiThinking" class="ai-thinking">
                                        <n-text depth="3" style="font-size: 12px;">💭 AI思考过程：</n-text>
                                        <div class="thinking-content">{{ aiThinking }}</div>
                                    </div>

                                    <!-- JSON内容展示 -->
                                    <div v-if="aiJsonContent" class="ai-json-content">
                                        <n-text depth="3" style="font-size: 12px;">📋 生成的卡牌数据：</n-text>
                                        <n-code :code="aiJsonContent" language="json" class="ai-json-code" />
                                    </div>

                                    <!-- 验证状态 -->
                                    <div v-if="aiValidationStatus" class="validation-status">
                                        <n-alert :type="aiValidationStatus.isValid ? 'success' : 'error'"
                                            :title="aiValidationStatus.isValid ? '✅ 验证成功' : '❌ 验证失败'" size="small">
                                            <div v-if="!aiValidationStatus.isValid">
                                                <div v-for="error in aiValidationStatus.errors" :key="error"
                                                    class="error-item">
                                                    • {{ error }}
                                                </div>
                                            </div>
                                            <div v-else>
                                                卡牌数据格式正确，可以导入到编辑器中
                                            </div>
                                        </n-alert>
                                    </div>

                                    <!-- 导入按钮 -->
                                    <div v-if="aiValidationStatus?.isValid" class="import-actions">
                                        <n-space>
                                            <n-button type="success" @click="importAIResult">
                                                <template #icon>
                                                    <n-icon :component="DownloadOutline" />
                                                </template>
                                                导入到编辑器
                                            </n-button>
                                        </n-space>
                                    </div>
                                </n-card>
                            </div>
                        </n-space>
                    </n-card>

                    <!-- 卡牌类型选择 -->
                    <n-card title="卡牌类型" size="small" class="form-card">
                        <n-form-item label="选择卡牌类型">
                            <n-select v-model:value="currentCardData.type" :options="cardTypeOptions"
                                placeholder="选择卡牌类型" @update:value="onCardTypeChange" />
                        </n-form-item>
                    </n-card>

                    <!-- 动态表单 -->
                    <n-card v-if="currentCardType && currentFormConfig" title="卡牌属性" size="small" class="form-card">
                        <n-form ref="dynamicFormRef" :model="currentCardData" label-placement="top" size="small">
                            <div v-for="(row, rowIndex) in formFieldRows" :key="rowIndex" class="form-row">
                                <div v-for="field in row"
                                    :key="field.key + (field.index !== undefined ? `_${field.index}` : '')"
                                    class="form-field" :class="getFieldLayoutClass(field.layout)">
                                    <FormFieldComponent :field="field" :value="getFieldValue(field)"
                                        :new-string-value="newStringValue" @update:value="setFieldValue(field, $event)"
                                        @update:new-string-value="newStringValue = $event"
                                        @add-multi-select-item="addMultiSelectItem(field, $event)"
                                        @remove-multi-select-item="removeMultiSelectItem(field, $event)"
                                        @add-string-array-item="addStringArrayItem(field)"
                                        @remove-string-array-item="removeStringArrayItem(field, $event)"
                                        @remove-image="removeImage(field)" />
                                </div>
                            </div>
                        </n-form>
                    </n-card>

                    <!-- 卡牌信息 -->
                    <n-card v-if="currentCardType" title="卡牌信息" size="small" class="form-card">
                        <n-form :model="currentCardData" label-placement="top" size="small">
                            <div class="form-row">
                                <!-- 插画作者 -->
                                <div class="form-field layout-third">
                                    <FormFieldComponent :field="{
                                        key: 'illustrator',
                                        name: '🎨 插画作者',
                                        type: 'text'
                                    }" :value="currentCardData.illustrator || ''" :new-string-value="newStringValue"
                                        @update:value="currentCardData.illustrator = $event"
                                        @update:new-string-value="newStringValue = $event" />
                                </div>
                                <!-- 遭遇组序号 -->
                                <div class="form-field layout-third">
                                    <FormFieldComponent :field="{
                                        key: 'encounter_group_number',
                                        name: '📋 遭遇组序号',
                                        type: 'text'
                                    }" :value="currentCardData.encounter_group_number || ''"
                                        :new-string-value="newStringValue"
                                        @update:value="currentCardData.encounter_group_number = $event"
                                        @update:new-string-value="newStringValue = $event" />
                                </div>
                                <!-- 卡牌序号 -->
                                <div class="form-field layout-third">
                                    <FormFieldComponent :field="{
                                        key: 'card_number',
                                        name: '📋 卡牌序号',
                                        type: 'text'
                                    }" :value="currentCardData.card_number || ''" :new-string-value="newStringValue"
                                        @update:value="currentCardData.card_number = $event"
                                        @update:new-string-value="newStringValue = $event" />
                                </div>
                            </div>
                            <div class="form-row">
                                <!-- 卡牌备注信息 -->
                                <div class="form-field layout-full">
                                    <FormFieldComponent :field="{
                                        key: 'remark',
                                        name: '📝 卡牌备注信息',
                                        type: 'textarea',
                                        rows: 2,
                                        maxlength: 200
                                    }" :value="currentCardData.requirements || ''" :new-string-value="newStringValue"
                                        @update:value="currentCardData.requirements = $event"
                                        @update:new-string-value="newStringValue = $event" />
                                </div>
                            </div>
                        </n-form>
                    </n-card>

                    <!-- TTS脚本编辑器 -->
                    <TtsScriptEditor v-if="currentCardType" :card-data="currentCardData" :card-type="currentCardType"
                        @update-tts-script="updateTtsScript" />

                    <!-- 操作按钮 -->
                    <div class="form-actions">
                        <n-space>
                            <n-button type="primary" @click="saveCard" :loading="saving">
                                保存卡牌
                                <span class="keyboard-shortcut">(Ctrl+S)</span>
                            </n-button>
                            <n-button @click="previewCard" :loading="generating">预览卡图</n-button>
                            <n-button @click="exportCard" :loading="exporting"
                                :disabled="!hasValidCardData">导出图片</n-button>
                            <n-button @click="resetForm">重置</n-button>
                        </n-space>
                    </div>
                </div>
            </n-scrollbar>
        </div>

        <!-- JSON查看模态框 -->
        <n-modal v-model:show="showJsonModal" preset="dialog" title="当前JSON数据">
            <n-code :code="filteredJsonData" language="json" />
            <template #action>
                <n-button @click="showJsonModal = false">关闭</n-button>
            </template>
        </n-modal>

        <!-- 保存确认对话框 -->
        <n-modal v-model:show="showSaveConfirmDialog">
            <n-card style="width: 450px" title="保存确认" :bordered="false" size="huge" role="dialog" aria-modal="true">
                <n-space vertical>
                    <n-alert type="warning" title="未保存的修改">
                        <template #icon>
                            <n-icon :component="WarningOutline" />
                        </template>
                        当前文件有未保存的修改，是否保存？
                    </n-alert>
                    <n-space vertical size="small">
                        <p><strong>{{ selectedFile?.label }}</strong></p>
                        <p style="color: #666; font-size: 12px;">
                            如果不保存，您的修改将会丢失。
                        </p>
                    </n-space>
                </n-space>
                <template #footer>
                    <n-space justify="end">
                        <n-button @click="discardChanges">不保存</n-button>
                        <n-button @click="showSaveConfirmDialog = false">取消</n-button>
                        <n-button type="primary" @click="saveAndSwitch" :loading="saving">保存</n-button>
                    </n-space>
                </template>
            </n-card>
        </n-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { FolderOpenOutline, ImageOutline, WarningOutline } from '@vicons/ionicons5';
import {
    SparklesOutline as SparklesIcon,
    RefreshOutline as LoadingOutline, // 修改这里，使用 RefreshOutline 代替 LoadingOutline
    CheckmarkCircleOutline,
    DownloadOutline
} from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import type { TreeOption } from 'naive-ui';
import { cardTypeConfigs, cardTypeOptions, type FormField, type CardTypeConfig, type ShowCondition } from '@/config/cardTypeConfigs';
import FormFieldComponent from './FormField.vue';
import { WorkspaceService, CardService, ConfigService } from '@/api';
import AIService from '@/api/ai-service';
import type { CardData, GenerateCardInfoStreamRequest, ParseCardJsonRequest, StreamDataChunk } from '@/api/types';
import TtsScriptEditor from './TtsScriptEditor.vue';

interface Props {
    showFileTree: boolean;
    showImagePreview: boolean;
    selectedFile?: TreeOption | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'toggle-file-tree': [];
    'toggle-image-preview': [];
    'update-preview-image': [image: string];
    'refresh-file-tree': [];
}>();

const message = useMessage();

// 表单状态
const currentCardData = reactive({
    type: '',
    name: '',
    id: '',
    created_at: '',
    version: '1.0',
});

// 原始数据状态 - 用于检测修改
const originalCardData = ref<string>('');

// 原始文件信息 - 用于记住需要保存的文件
const originalFileInfo = ref<{ path: string; label: string } | null>(null);

// 待切换的文件
const pendingSwitchFile = ref<TreeOption | null>(null);

const currentCardType = ref('');
const newStringValue = ref('');
const showJsonModal = ref(false);
const showSaveConfirmDialog = ref(false);
const saving = ref(false);
const generating = ref(false);
const exporting = ref(false);

// AI相关状态
const aiEnabledInEditor = ref(false);
const aiPrompt = ref('');
const aiGenerating = ref(false);
const aiResult = ref('');
const aiThinking = ref('');
const aiJsonContent = ref('');
const aiValidationStatus = ref<{ isValid: boolean; errors: string[] } | null>(null);
const aiAbortController = ref<AbortController | null>(null);

// 初始化配置
onMounted(async () => {
    try {
        const config = await ConfigService.getConfig();
        aiEnabledInEditor.value = config.ai_enabled_in_editor || false;
    } catch (error) {
        console.warn('获取AI配置失败:', error);
        aiEnabledInEditor.value = false;
    }
});

// 修改 startAIGeneration 方法，添加更多日志
const startAIGeneration = async () => {
    if (!aiPrompt.value.trim()) {
        message.warning('请输入提示词');
        return;
    }
    console.log('🚀 开始AI生成');
    aiGenerating.value = true;
    aiResult.value = '';
    aiThinking.value = '';
    aiJsonContent.value = '';
    aiValidationStatus.value = null;
    aiAbortController.value = new AbortController();
    const request: GenerateCardInfoStreamRequest = {
        content: aiPrompt.value.trim()
    };
    try {
        await AIService.generateCardInfoStream(
            request,
            (chunk: StreamDataChunk) => {
                // console.log('📦 收到数据块:', chunk);
                // 处理流式数据
                if (chunk.reasoning) {
                    aiThinking.value += chunk.reasoning;
                    // console.log('💭 更新思考内容:', chunk.thinking.length);
                }
                if (chunk.content) {
                    aiJsonContent.value += chunk.content;
                    // console.log('📝 更新JSON内容，当前长度:', aiJsonContent.value.length);
                }
            },
            (error: Error) => {
                console.error('❌ AI生成失败:', error);
                message.error(`AI生成失败: ${error.message}`);
                aiGenerating.value = false;
            },
            () => {
                console.log('✅ AI生成完成');
                aiGenerating.value = false;

                // 确保有内容才验证
                if (aiJsonContent.value && aiJsonContent.value.trim()) {
                    console.log('🔍 开始验证AI结果');
                    try {
                        validateAIResult();
                    } catch (error) {
                        console.error('❌ 验证AI结果时出错:', error);
                        message.error(`验证失败: ${error.message || '未知错误'}`);
                    }
                } else {
                    console.warn('⚠️ AI生成完成但没有内容');
                    message.warning('AI生成完成但没有返回有效内容');
                }
            }
        );
    } catch (error) {
        console.error('❌ AI生成出错:', error);
        message.error(`AI生成出错: ${error.message || '未知错误'}`);
        aiGenerating.value = false;
    }
};


const stopAIGeneration = () => {
    if (aiAbortController.value) {
        aiAbortController.value.abort();
        aiAbortController.value = null;
    }
    aiGenerating.value = false;
};

// 修改 validateAIResult 方法，添加更多日志和错误处理
const validateAIResult = () => {
    console.log('🔍 开始验证AI结果');

    if (!aiJsonContent.value) {
        console.warn('⚠️ 没有AI生成的JSON内容');
        return;
    }
    // console.log('📄 AI生成的内容长度:', aiJsonContent.value.length);
    // console.log('📄 AI生成的内容预览:', aiJsonContent.value.substring(0, 200));
    try {
        // 直接在前端使用处理函数解析JSON
        console.log('🔧 开始处理JSON字符串');
        const cardJson = processJsonStr(aiJsonContent.value);
        console.log('✅ JSON解析成功:', cardJson);
        // 检查AI返回的错误信息
        if (cardJson.msg && cardJson.msg.trim()) {
            console.warn('⚠️ AI返回包含错误信息:', cardJson.msg);
            message.error('AI返回包含错误信息:' + cardJson.msg)
            aiValidationStatus.value = {
                isValid: false,
                errors: [`AI返回错误: ${cardJson.msg}`]
            };
            return;
        }
        // 验证必要字段
        console.log('🔍 验证必要字段');
        const requiredFields = ['type', 'name', 'body'];
        const missingFields = [];
        for (const field of requiredFields) {
            if (!(field in cardJson)) {
                missingFields.push(field);
                console.warn(`⚠️ 缺少字段: ${field}`);
            }
        }
        if (missingFields.length > 0) {
            console.error('❌ 验证失败，缺少必要字段:', missingFields);
            aiValidationStatus.value = {
                isValid: false,
                errors: [`缺少必要字段: ${missingFields.join(', ')}`]
            };
            return;
        }
        // 清除msg字段（如果为空）
        if (cardJson.msg && !cardJson.msg.trim()) {
            delete cardJson.msg;
            console.log('🧹 清除空的msg字段');
        }
        // 验证成功
        console.log('✅ 验证成功');
        aiValidationStatus.value = {
            isValid: true,
            errors: []
        };
        aiResult.value = aiJsonContent.value;
        // 自动导入成功的结果
        console.log('⏰ 准备自动导入结果');
        setTimeout(() => {
            console.log('🚀 开始自动导入');
            try {
                importAIResult();
            } catch (error) {
                console.error('❌ 自动导入时出错:', error);
                message.error(`自动导入失败: ${error.message || '未知错误'}`);
            }
        }, 500);
    } catch (error) {
        console.error('❌ 验证AI结果失败:', error);
        const errorMessage = error?.message || '未知错误';

        aiValidationStatus.value = {
            isValid: false,
            errors: [`验证失败: ${errorMessage}`]
        };

        message.error(`验证AI结果失败: ${errorMessage}`);
    }
};
// 修改 processJsonStr 方法，添加更多日志
const processJsonStr = (jsonStr: string): any => {
    console.log('🔧 开始处理JSON字符串，长度:', jsonStr.length);

    // 如果返回了markdown的代码块，需要去除，保留原始的json字符串
    if (jsonStr.includes('```json') && jsonStr.includes('```')) {
        console.log('🧹 清理markdown代码块（json）');
        jsonStr = jsonStr.substring(jsonStr.indexOf('```json') + 7, jsonStr.lastIndexOf('```'));
    } else if (jsonStr.includes('```')) {
        console.log('🧹 清理markdown代码块（通用）');
        const start = jsonStr.indexOf('```');
        const end = jsonStr.lastIndexOf('```');
        if (start !== end) {
            jsonStr = jsonStr.substring(start + 3, end);
        }
    }
    jsonStr = jsonStr.trim();
    console.log('🧹 清理后的JSON字符串长度:', jsonStr.length);
    try {
        console.log('🔍 尝试直接解析JSON');
        const data = JSON.parse(jsonStr);
        console.log('✅ JSON直接解析成功');
        return data;
    } catch (e) {
        console.warn('⚠️ 直接解析失败，尝试修复:', e.message);

        let fixedJson = jsonStr.trim();
        // 如果最后一个字段没有闭合引号，尝试添加
        if (!fixedJson.endsWith('"') && fixedJson.endsWith('...')) {
            console.log('🔧 修复结尾的...');
            fixedJson = fixedJson.slice(0, -3) + '"';
        } else if (!fixedJson.endsWith('"') && fixedJson.includes('"')) {
            console.log('🔧 修复未闭合的引号');
            const lines = fixedJson.split('\n');
            for (let i = lines.length - 1; i >= 0; i--) {
                const line = lines[i].trim();
                if (line.includes(':') && !line.endsWith('"') && !line.endsWith(',')) {
                    lines[i] = line + '"';
                    console.log('🔧 修复行:', line);
                    break;
                }
            }
            fixedJson = lines.join('\n');
        }
        // 如果没有闭合的大括号，尝试添加
        if (!fixedJson.endsWith('}')) {
            console.log('🔧 添加闭合大括号');
            fixedJson += '}';
        }

        try {
            console.log('🔍 尝试解析修复后的JSON');
            const data = JSON.parse(fixedJson);
            console.log('✅ 修复后的JSON解析成功');
            return data;
        } catch (err) {
            console.error('❌ 修复后仍然解析失败:', err);
            console.error('❌ 原始JSON:', jsonStr);
            console.error('❌ 修复后JSON:', fixedJson);
            throw new Error(`JSON解析错误: ${err.message || err}`);
        }
    }
};
// 修改 importAIResult 方法，添加更多日志
const importAIResult = async () => {
    console.log('🚀 开始导入AI结果');

    if (!aiValidationStatus.value?.isValid) {
        console.warn('⚠️ 没有有效的AI生成结果可以导入');
        message.warning('没有有效的AI生成结果可以导入');
        return;
    }
    try {
        console.log('🔧 解析AI生成的JSON');
        const aiData = processJsonStr(aiJsonContent.value);
        console.log('✅ AI数据解析成功:', aiData);
        // 保存当前的元数据
        const metadata = {
            id: currentCardData.id || '',
            created_at: currentCardData.created_at || '',
            version: '1.0',
        };
        console.log('📝 保存元数据:', metadata);
        const newData = { ...metadata, ...aiData };
        console.log('🔧 合并数据:', Object.keys(newData));
        // 清空当前数据并重新赋值
        console.log('🧹 清空当前数据');
        Object.keys(currentCardData).forEach(key => {
            delete currentCardData[key];
        });
        // 使用 nextTick 确保DOM更新
        console.log('⏳ 等待DOM更新');
        await nextTick();
        // 重新赋值
        console.log('📝 重新赋值数据');
        Object.keys(newData).forEach(key => {
            currentCardData[key] = newData[key];
        });
        // 更新卡牌类型
        if (aiData.type) {
            console.log('🏷️ 更新卡牌类型:', aiData.type);
            currentCardType.value = aiData.type;
        }
        // 强制触发自动预览
        console.log('🖼️ 准备生成预览');
        await nextTick();
        setTimeout(() => {
            console.log('🖼️ 开始生成预览');
            autoGeneratePreview();
        }, 100);
        console.log('✅ AI生成的卡牌数据已成功导入到编辑器');
        message.success('AI生成的卡牌数据已成功导入到编辑器');
        clearAIResult();
    } catch (error) {
        console.error('❌ 导入AI结果失败:', error);
        console.error('❌ 错误堆栈:', error.stack);
        message.error(`导入AI结果失败: ${error.message || '未知错误'}`);
    }
};


const clearAIResult = () => {
    aiResult.value = '';
    aiThinking.value = '';
    aiJsonContent.value = '';
    aiValidationStatus.value = null;
    aiPrompt.value = '';
};

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
    return currentCardData.name && currentCardData.name.trim() !== '' &&
        currentCardData.type && currentCardData.type.trim() !== '';
});

const currentFormConfig = computed((): CardTypeConfig | null => {
    return currentCardType.value ? cardTypeConfigs[currentCardType.value] : null;
});

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
};


// 添加防抖标志
const isProcessingKeydown = ref(false);
// 键盘事件处理器
const handleKeydown = async (event: KeyboardEvent) => {
    // Ctrl+S 保存
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        event.stopPropagation(); // 阻止事件冒泡

        // 防止重复处理
        if (isProcessingKeydown.value || saving.value) {
            console.log('阻止重复保存'); // 调试用
            return;
        }

        if (props.selectedFile && props.selectedFile.type === 'card') {
            isProcessingKeydown.value = true;
            try {
                await saveCard();
            } finally {
                // 确保标志被重置
                setTimeout(() => {
                    isProcessingKeydown.value = false;
                }, 100);
            }
        }
    }
};

// 检查显示条件
const checkShowCondition = (condition: ShowCondition): boolean => {
    const fieldValue = getFieldValue({ key: condition.field } as FormField);
    const targetValue = condition.value;
    const operator = condition.operator || 'equals';

    switch (operator) {
        case 'equals':
            return fieldValue === targetValue;
        case 'not-equals':
            return fieldValue !== targetValue;
        case 'includes':
            return Array.isArray(fieldValue) ? fieldValue.includes(targetValue) : false;
        case 'not-includes':
            return Array.isArray(fieldValue) ? !fieldValue.includes(targetValue) : true;
        default:
            return fieldValue === targetValue;
    }
};

// 过滤显示的字段
const visibleFields = computed(() => {
    if (!currentFormConfig.value) return [];

    return currentFormConfig.value.fields.filter(field => {
        if (!field.showCondition) return true;
        return checkShowCondition(field.showCondition);
    });
});

// 布局系统 - 基于可见字段
const formFieldRows = computed(() => {
    const fields = visibleFields.value;
    const rows = [];
    let currentRow = [];
    let currentRowWidth = 0;

    const layoutWeights = {
        'full': 1,
        'half': 0.5,
        'third': 1 / 3,
        'quarter': 0.25
    };

    for (const field of fields) {
        const layout = field.layout || 'full';
        const weight = layoutWeights[layout];

        if (layout === 'full' || currentRowWidth + weight > 1) {
            if (currentRow.length > 0) {
                rows.push(currentRow);
                currentRow = [];
                currentRowWidth = 0;
            }
        }

        currentRow.push(field);
        currentRowWidth += weight;

        if (layout === 'full' || currentRowWidth >= 1) {
            rows.push(currentRow);
            currentRow = [];
            currentRowWidth = 0;
        }
    }

    if (currentRow.length > 0) {
        rows.push(currentRow);
    }

    return rows;
});

const getFieldLayoutClass = (layout: string = 'full') => {
    const classMap = {
        'half': 'layout-half',
        'third': 'layout-third',
        'quarter': 'layout-quarter',
        'full': 'layout-full'
    };
    return classMap[layout] || 'layout-full';
};

// 获取字段路径（支持数组索引）
const getFieldPath = (field: FormField): string => {
    if (field.index !== undefined) {
        return `${field.key}[${field.index}]`;
    }
    return field.key;
};

// 表单操作方法
const getFieldValue = (field: FormField) => {
    if (field.index !== undefined) {
        const array = getDeepValue(currentCardData, field.key);
        return Array.isArray(array) ? array[field.index] : undefined;
    }
    return getDeepValue(currentCardData, field.key);
};

const getDeepValue = (obj: any, path: string) => {
    const keys = path.split('.');
    let value = obj;
    for (const key of keys) {
        if (value && typeof value === 'object' && key in value) {
            value = value[key];
        } else {
            return undefined;
        }
    }
    return value;
};

const setFieldValue = (field: FormField, value: any) => {
    if (field.index !== undefined) {
        setArrayValue(field.key, field.index, value);
    } else {
        setDeepValue(currentCardData, field.key, value);
    }
};

const setDeepValue = (obj: any, path: string, value: any) => {
    const keys = path.split('.');
    let target = obj;

    for (let i = 0; i < keys.length - 1; i++) {
        const key = keys[i];
        if (!target[key] || typeof target[key] !== 'object') {
            target[key] = {};
        }
        target = target[key];
    }

    const finalKey = keys[keys.length - 1];
    target[finalKey] = value;
};

const setArrayValue = (arrayPath: string, index: number, value: any) => {
    let array = getDeepValue(currentCardData, arrayPath);
    if (!Array.isArray(array)) {
        array = [];
        setDeepValue(currentCardData, arrayPath, array);
    }

    // 确保数组长度足够
    while (array.length <= index) {
        array.push(undefined);
    }

    array[index] = value;
};

const addMultiSelectItem = (field: FormField, value: string) => {
    if (!value) return;
    let currentArray = getFieldValue(field);
    if (!Array.isArray(currentArray)) {
        currentArray = [];
    }
    currentArray.push(value);
    setFieldValue(field, currentArray);
};

const removeMultiSelectItem = (field: FormField, index: number) => {
    const currentArray = getFieldValue(field);
    if (Array.isArray(currentArray)) {
        currentArray.splice(index, 1);
        setFieldValue(field, currentArray);
    }
};

const addStringArrayItem = (field: FormField) => {
    if (!newStringValue.value.trim()) return;
    let currentArray = getFieldValue(field);
    if (!Array.isArray(currentArray)) {
        currentArray = [];
    }
    currentArray.push(newStringValue.value.trim());
    setFieldValue(field, currentArray);
    newStringValue.value = '';
};

const removeStringArrayItem = (field: FormField, index: number) => {
    const currentArray = getFieldValue(field);
    if (Array.isArray(currentArray)) {
        currentArray.splice(index, 1);
        setFieldValue(field, currentArray);
    }
};

const onCardTypeChange = (newType: string) => {
    currentCardType.value = newType;

    const hiddenFields = ['id', 'created_at', 'version', 'type', 'name'];
    const newData = {};

    hiddenFields.forEach(field => {
        if (currentCardData[field] !== undefined) {
            newData[field] = currentCardData[field];
        }
    });

    Object.keys(currentCardData).forEach(key => {
        if (hiddenFields.includes(key)) {
            return;
        }
        delete currentCardData[key];
    });

    Object.assign(currentCardData, newData);

    // 应用默认值
    const config = cardTypeConfigs[newType];
    if (config) {
        config.fields.forEach(field => {
            if (field.defaultValue !== undefined) {
                setFieldValue(field, field.defaultValue);
            }
        });
    }
};

// 保存原始数据状态
const saveOriginalData = () => {
    originalCardData.value = JSON.stringify(currentCardData);
};

// 自动生成卡图（如果数据有效的话）
const autoGeneratePreview = async () => {
    // 只有当卡牌名称和类型都有值时才自动生成
    if (currentCardData.name && currentCardData.name.trim() &&
        currentCardData.type && currentCardData.type.trim()) {
        try {
            const imageBase64 = await CardService.generateCard(currentCardData as CardData);
            if (imageBase64) {
                emit('update-preview-image', imageBase64);
            }
        } catch (error) {
            // 自动生成失败不显示错误消息，避免打扰用户
            console.warn('自动生成卡图失败:', error);
        }
    }
};

const loadCardData = async () => {
    if (!props.selectedFile || props.selectedFile.type !== 'card' || !props.selectedFile.path) {
        return;
    }

    try {
        const content = await WorkspaceService.getFileContent(props.selectedFile.path);
        const cardData = JSON.parse(content || '{}');

        // 清空当前数据
        Object.keys(currentCardData).forEach(key => {
            delete currentCardData[key];
        });

        // 加载新数据
        Object.assign(currentCardData, {
            type: '',
            name: '',
            id: '',
            created_at: '',
            version: '1.0',
            ...cardData
        });

        currentCardType.value = cardData.type || '';

        // 等待TTS配置加载完成后再保存原始数据
        await nextTick();
        setTimeout(() => {
            saveOriginalData();
            
            // 加载完成后自动生成预览
            autoGeneratePreview();
        }, 100); // 给TTS配置更新一点时间

    } catch (error) {
        console.error('加载卡牌数据失败:', error);
        message.error('加载卡牌数据失败');
    }
};


// 生成卡图的通用方法
const generateCardImage = async (): Promise<string | null> => {
    // 验证卡牌数据
    const validation = CardService.validateCardData(currentCardData as CardData);
    if (!validation.isValid) {
        message.error('卡牌数据验证失败: ' + validation.errors.join(', '));
        return null;
    }

    try {
        const imageBase64 = await CardService.generateCard(currentCardData as CardData);
        return imageBase64;
    } catch (error) {
        console.error('生成卡图失败:', error);
        message.error(`生成卡图失败: ${error.message || '未知错误'}`);
        return null;
    }
};

// 修改 saveCard 方法，支持使用原始文件信息保存
const saveCard = async () => {
    // 优先使用原始文件信息，如果没有则使用当前选中文件
    const fileToSave = originalFileInfo.value || props.selectedFile;

    if (!fileToSave || !fileToSave.path) {
        message.warning('未选择文件');
        return false;
    }

    // 如果已经在保存，直接返回
    if (saving.value) {
        console.log('已在保存中，跳过');
        return false;
    }

    try {
        saving.value = true;
        // 保存JSON文件
        const jsonContent = JSON.stringify(currentCardData, null, 2);
        await WorkspaceService.saveFileContent(fileToSave.path, jsonContent);

        // 更新原始数据状态
        saveOriginalData();

        // 生成并显示卡图
        const imageBase64 = await generateCardImage();
        if (imageBase64) {
            emit('update-preview-image', imageBase64);
        }

        message.success('卡牌保存成功');
        return true;
    } catch (error) {
        console.error('保存卡牌失败:', error);
        message.error('保存卡牌失败');
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

        // 触发文件切换逻辑
        if (fileToSwitch && fileToSwitch.type === 'card') {
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
    pendingSwitchFile.value = null;

    // 重新加载当前文件或清空数据
    if (props.selectedFile && props.selectedFile.type === 'card') {
        loadCardData();
    } else {
        clearFormData();
    }
};

// 清空表单数据
const clearFormData = () => {
    Object.keys(currentCardData).forEach(key => {
        delete currentCardData[key];
    });
    Object.assign(currentCardData, {
        type: '',
        name: '',
        id: '',
        created_at: '',
        version: '1.0',
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
        message.warning('请先填写卡牌名称和类型');
        return;
    }

    try {
        generating.value = true;
        const imageBase64 = await generateCardImage();
        if (imageBase64) {
            emit('update-preview-image', imageBase64);
            message.success('卡图预览生成成功');
        }
    } catch (error) {
        console.error('预览卡图失败:', error);
    } finally {
        generating.value = false;
    }
};

// 导出图片
const exportCard = async () => {
    if (!hasValidCardData.value) {
        message.warning('请先填写卡牌名称和类型');
        return;
    }

    if (!props.selectedFile || !props.selectedFile.path) {
        message.warning('未选择卡牌文件');
        return;
    }

    try {
        exporting.value = true;

        // 获取卡牌文件所在的目录
        const filePath = props.selectedFile.path;
        const parentPath = filePath.substring(0, filePath.lastIndexOf('/'));

        // 使用文件名作为导出的图片文件名，去掉.card扩展名
        const cardFileName = props.selectedFile.label?.replace('.card', '') || 'untitled';
        const filename = `${cardFileName}.png`;

        console.log('使用文件名作为导出文件名:', filename);

        await CardService.saveCard(currentCardData as CardData, filename, parentPath);

        // 刷新文件树以显示新生成的图片文件
        emit('refresh-file-tree');

        message.success(`图片已导出: ${filename}`);
    } catch (error) {
        console.error('导出图片失败:', error);
        message.error(`导出图片失败: ${error.message || '未知错误'}`);
    } finally {
        exporting.value = false;
    }
};

const resetForm = () => {
    const hiddenFields = ['id', 'created_at', 'version'];
    const hiddenData = {};

    hiddenFields.forEach(field => {
        if (currentCardData[field] !== undefined) {
            hiddenData[field] = currentCardData[field];
        }
    });

    Object.keys(currentCardData).forEach(key => {
        delete currentCardData[key];
    });

    Object.assign(currentCardData, hiddenData, { type: '', name: '' });
    currentCardType.value = '';
    saveOriginalData();
    message.info('表单已重置');
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

    // 没有未保存修改，直接切换
    originalFileInfo.value = null;
    if (newFile && newFile.type === 'card') {
        await loadCardData();
    } else {
        clearFormData();
    }
}, { immediate: true });

// 在 script 中添加删除图片的方法
const removeImage = (field: FormField) => {
    setFieldValue(field, '');
};

// 组件挂载时添加键盘事件监听器
onMounted(() => {
    document.addEventListener('keydown', handleKeydown);
});

// 组件卸载时移除键盘事件监听器
onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
});
</script>


<style scoped>
.form-pane {
    flex: 1;
    min-width: 400px;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
    overflow: hidden;
    background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
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

/* AI卡片特殊样式 */
.ai-card {
    background: linear-gradient(135deg, rgba(139, 69, 19, 0.05) 0%, rgba(255, 165, 0, 0.05) 100%);
    border: 2px solid rgba(139, 69, 19, 0.2);
}

.ai-result-container {
    margin-top: 16px;
    /* 确保容器不超出父容器 */
    width: 100%;
    overflow: hidden;
}

.ai-result-card {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(139, 69, 19, 0.1);
    /* 确保卡片不超出容器 */
    width: 100%;
    overflow: hidden;
}

.ai-thinking {
    margin-bottom: 16px;
    padding: 12px;
    background: rgba(139, 69, 19, 0.05);
    border-radius: 8px;
    border-left: 4px solid rgba(139, 69, 19, 0.3);
    /* 添加宽度和溢出控制 */
    width: 100%;
    overflow: hidden;
    box-sizing: border-box;
}

.thinking-content {
    margin-top: 8px;
    font-size: 13px;
    line-height: 1.5;
    color: #666;
    white-space: pre-wrap;
    /* 添加文本换行和溢出处理 */
    word-wrap: break-word;
    word-break: break-all;
    max-width: 100%;
    overflow-wrap: break-word;
}

.ai-json-content {
    margin-bottom: 16px;
    /* 确保JSON内容容器不溢出 */
    width: 100%;
    overflow: hidden;
}

.ai-json-code {
    max-height: 200px;
    overflow-y: auto;
    overflow-x: auto;
    /* 添加水平滚动 */
    margin-top: 8px;
    /* 确保代码块不超出容器 */
    width: 100%;
    box-sizing: border-box;
    /* 添加边框来更好地显示滚动区域 */
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    background: #f8f9fa;
}

.validation-status {
    margin-bottom: 16px;
}

.error-item {
    margin: 4px 0;
    font-size: 13px;
}

.import-actions {
    margin-top: 16px;
}

.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.form-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    align-items: flex-start;
}

.form-field {
    flex: 1;
    min-width: 0;
}

.layout-full {
    flex: 1;
}

.layout-half {
    flex: 0 0 calc(50% - 8px);
}

.layout-third {
    flex: 0 0 calc(33.333% - 11px);
}

.layout-quarter {
    flex: 0 0 calc(25% - 12px);
}

@media (max-width: 768px) {
    .form-row {
        flex-direction: column;
    }

    .layout-full,
    .layout-half,
    .layout-third,
    .layout-quarter {
        flex: 1;
    }
}

.form-actions {
    margin-top: 32px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    border-top: 3px solid #667eea;
}
</style>

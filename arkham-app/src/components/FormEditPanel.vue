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
            <n-code :code="JSON.stringify(currentCardData, null, 2)" language="json" />
            <template #action>
                <n-button @click="showJsonModal = false">关闭</n-button>
            </template>
        </n-modal>

        <!-- 保存确认对话框 -->
        <n-modal v-model:show="showSaveConfirmDialog">
            <n-card
                style="width: 450px"
                title="保存确认"
                :bordered="false"
                size="huge"
                role="dialog"
                aria-modal="true"
            >
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
import { ref, computed, reactive, watch, onMounted, onUnmounted } from 'vue';
import { FolderOpenOutline, ImageOutline, WarningOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import type { TreeOption } from 'naive-ui';
import { cardTypeConfigs, cardTypeOptions, type FormField, type CardTypeConfig, type ShowCondition } from '@/config/cardTypeConfigs';
import FormFieldComponent from './FormField.vue';
import { WorkspaceService, CardService } from '@/api';
import type { CardData } from '@/api/types';

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

// 待切换的文件
const pendingSwitchFile = ref<TreeOption | null>(null);

const currentCardType = ref('');
const newStringValue = ref('');
const showJsonModal = ref(false);
const showSaveConfirmDialog = ref(false);
const saving = ref(false);
const generating = ref(false);
const exporting = ref(false);

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

// 加载卡牌数据
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
        
        // 保存原始数据状态
        saveOriginalData();

        // 加载完成后自动生成预览
        setTimeout(() => {
            autoGeneratePreview();
        }, 100); // 给一点时间让数据完全加载

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

// 修改 saveCard 方法，确保状态正确管理
const saveCard = async () => {
    if (!props.selectedFile || !props.selectedFile.path) {
        message.warning('未选择文件');
        return false; // 返回 boolean
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
        await WorkspaceService.saveFileContent(props.selectedFile.path, jsonContent);
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
        // 直接加载新文件，因为 watch 会被触发但不会再次显示确认对话框
        const fileToSwitch = pendingSwitchFile.value;
        pendingSwitchFile.value = null;
        // 由于我们已经处理了保存，可以直接切换
        if (fileToSwitch && fileToSwitch.type === 'card') {
            await loadCardData();
        } else {
            // 清空表单数据
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
        }
    }
};

// 放弃修改并切换文件
const discardChanges = () => {
    showSaveConfirmDialog.value = false;
    pendingSwitchFile.value = null;
    // 重新加载当前文件或清空数据
    if (props.selectedFile && props.selectedFile.type === 'card') {
        loadCardData();
    } else {
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
    }
};

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
        pendingSwitchFile.value = newFile;
        showSaveConfirmDialog.value = true;
        return;
    }

    // 没有未保存修改，直接切换
    if (newFile && newFile.type === 'card') {
        await loadCardData();
    } else {
        // 清空表单数据
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

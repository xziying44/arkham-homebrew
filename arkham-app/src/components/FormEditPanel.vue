<template>
    <div class="form-pane">
        <div class="pane-header">
            <n-space align="center" justify="space-between">
                <n-space align="center" size="small">
                    <n-button v-if="!showFileTree" size="tiny" quaternary @click="$emit('toggle-file-tree')" class="header-button">
                        <n-icon :component="FolderOpenOutline" />
                    </n-button>
                    <span class="pane-title">{{ selectedFile?.label || '卡牌编辑器' }}</span>
                </n-space>
                <n-space size="small">
                    <n-button size="tiny" @click="showJsonModal = true" class="header-button" v-if="selectedFile">查看JSON</n-button>
                    <n-button v-if="!showImagePreview" size="tiny" quaternary @click="$emit('toggle-image-preview')" class="header-button">
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
                                <div v-for="field in row" :key="field.key + (field.index !== undefined ? `_${field.index}` : '')" class="form-field"
                                    :class="getFieldLayoutClass(field.layout)">
                                    <FormFieldComponent :field="field" :value="getFieldValue(field)"
                                        :new-string-value="newStringValue"
                                        @update:value="setFieldValue(field, $event)"
                                        @update:new-string-value="newStringValue = $event"
                                        @add-multi-select-item="addMultiSelectItem(field, $event)"
                                        @remove-multi-select-item="removeMultiSelectItem(field, $event)"
                                        @add-string-array-item="addStringArrayItem(field)"
                                        @remove-string-array-item="removeStringArrayItem(field, $event)" />
                                </div>
                            </div>
                        </n-form>
                    </n-card>

                    <!-- 操作按钮 -->
                    <div class="form-actions">
                        <n-space>
                            <n-button type="primary" @click="saveCard" :loading="saving">保存卡牌</n-button>
                            <n-button @click="previewCard">预览卡图</n-button>
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
    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted } from 'vue';
import { FolderOpenOutline, ImageOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import type { TreeOption } from 'naive-ui';
import { cardTypeConfigs, cardTypeOptions, type FormField, type CardTypeConfig, type ShowCondition } from '@/config/cardTypeConfigs';
import FormFieldComponent from './FormField.vue';
import { WorkspaceService } from '@/api';

interface Props {
    showFileTree: boolean;
    showImagePreview: boolean;
    selectedFile?: TreeOption | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'toggle-file-tree': [];
    'toggle-image-preview': [];
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

const currentCardType = ref('');
const newStringValue = ref('');
const showJsonModal = ref(false);
const saving = ref(false);

const currentFormConfig = computed((): CardTypeConfig | null => {
    return currentCardType.value ? cardTypeConfigs[currentCardType.value] : null;
});

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
        message.success('卡牌数据加载成功');
    } catch (error) {
        console.error('加载卡牌数据失败:', error);
        message.error('加载卡牌数据失败');
    }
};

// 保存卡牌
const saveCard = async () => {
    if (!props.selectedFile || !props.selectedFile.path) {
        message.warning('未选择文件');
        return;
    }

    try {
        saving.value = true;
        const jsonContent = JSON.stringify(currentCardData, null, 2);
        await WorkspaceService.saveFileContent(props.selectedFile.path, jsonContent);
        message.success('卡牌保存成功');
    } catch (error) {
        console.error('保存卡牌失败:', error);
        message.error('保存卡牌失败');
    } finally {
        saving.value = false;
    }
};

// 预览卡图
const previewCard = () => {
    // TODO: 待开发预览卡图功能
    message.info('预览卡图功能开发中...');
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
    message.info('表单已重置');
};

// 监听选中文件变化
watch(() => props.selectedFile, (newFile) => {
    if (newFile && newFile.type === 'card') {
        loadCardData();
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
    }
}, { immediate: true });
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

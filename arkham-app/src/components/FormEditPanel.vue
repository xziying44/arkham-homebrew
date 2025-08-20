<template>
    <div class="form-pane">
        <div class="pane-header">
            <n-space align="center" justify="space-between">
                <n-space align="center" size="small">
                    <n-button v-if="!showFileTree" size="tiny" quaternary @click="$emit('toggle-file-tree')">
                        <n-icon :component="FolderOpenOutline" />
                    </n-button>
                    <span class="pane-title">{{ currentCardData?.name || '卡牌编辑器' }}</span>
                </n-space>
                <n-space size="small">
                    <n-button size="tiny" @click="loadTestData">加载测试数据</n-button>
                    <n-button size="tiny" @click="showJsonModal = true">查看JSON</n-button>
                    <n-button v-if="!showImagePreview" size="tiny" quaternary @click="$emit('toggle-image-preview')">
                        <n-icon :component="ImageOutline" />
                    </n-button>
                </n-space>
            </n-space>
        </div>

        <div class="form-content">
            <n-scrollbar>
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
                                <div v-for="field in row" :key="field.key" class="form-field"
                                    :class="getFieldLayoutClass(field.layout)">
                                    <FormFieldComponent :field="field" :value="getFieldValue(field.key)"
                                        :new-string-value="newStringValue"
                                        @update:value="setFieldValue(field.key, $event)"
                                        @update:new-string-value="newStringValue = $event"
                                        @add-multi-select-item="addMultiSelectItem(field.key, $event)"
                                        @remove-multi-select-item="removeMultiSelectItem(field.key, $event)"
                                        @add-string-array-item="addStringArrayItem(field.key)"
                                        @remove-string-array-item="removeStringArrayItem(field.key, $event)" />
                                </div>
                            </div>
                        </n-form>
                    </n-card>

                    <!-- 操作按钮 -->
                    <div class="form-actions">
                        <n-space>
                            <n-button type="primary" @click="saveCard">保存卡牌</n-button>
                            <n-button @click="resetForm">重置</n-button>
                            <n-button @click="exportJson">导出JSON</n-button>
                            <n-button @click="importJson">导入JSON</n-button>
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
import { ref, computed, reactive } from 'vue';
import { FolderOpenOutline, ImageOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import { cardTypeConfigs, cardTypeOptions, type FormField, type CardTypeConfig } from '@/config/cardTypeConfigs';
import FormFieldComponent from './FormField.vue'; // 重命名组件导入
interface Props {
    showFileTree: boolean;
    showImagePreview: boolean;
}

defineProps<Props>();

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

const currentFormConfig = computed((): CardTypeConfig | null => {
    return currentCardType.value ? cardTypeConfigs[currentCardType.value] : null;
});

// 布局系统
const formFieldRows = computed(() => {
    if (!currentFormConfig.value) return [];

    const fields = currentFormConfig.value.fields;
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

// 表单操作方法
const getFieldValue = (fieldPath: string) => {
    const keys = fieldPath.split('.');
    let value = currentCardData;
    for (const key of keys) {
        if (value && typeof value === 'object' && key in value) {
            value = value[key];
        } else {
            return undefined;
        }
    }
    return value;
};

const setFieldValue = (fieldPath: string, value: any) => {
    const keys = fieldPath.split('.');
    let target = currentCardData;

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

const addMultiSelectItem = (fieldPath: string, value: string) => {
    if (!value) return;
    let currentArray = getFieldValue(fieldPath);
    if (!Array.isArray(currentArray)) {
        currentArray = [];
    }
    currentArray.push(value);
    setFieldValue(fieldPath, currentArray);
};

const removeMultiSelectItem = (fieldPath: string, index: number) => {
    const currentArray = getFieldValue(fieldPath);
    if (Array.isArray(currentArray)) {
        currentArray.splice(index, 1);
        setFieldValue(fieldPath, currentArray);
    }
};

const addStringArrayItem = (fieldPath: string) => {
    if (!newStringValue.value.trim()) return;
    let currentArray = getFieldValue(fieldPath);
    if (!Array.isArray(currentArray)) {
        currentArray = [];
    }
    currentArray.push(newStringValue.value.trim());
    setFieldValue(fieldPath, currentArray);
    newStringValue.value = '';
};

const removeStringArrayItem = (fieldPath: string, index: number) => {
    const currentArray = getFieldValue(fieldPath);
    if (Array.isArray(currentArray)) {
        currentArray.splice(index, 1);
        setFieldValue(fieldPath, currentArray);
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

// 其他方法
const loadTestData = () => {
    Object.assign(currentCardData, {
        type: '支援卡',
        name: '医疗包',
        class: '守护者',
        submit_icon: ['意志', '战力', '战力'],
        traits: ['道具', '供给'],
        level: 0,
        cost: 2,
        id: 'med_kit_001',
        created_at: '2024-01-15T10:30:00Z',
        version: '1.0'
    });
    currentCardType.value = '支援卡';
    message.success('测试数据已加载');
};

const saveCard = () => {
    message.success('卡牌已保存');
    console.log('保存的数据:', currentCardData);
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

const exportJson = () => {
    const dataStr = JSON.stringify(currentCardData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentCardData.name || 'card'}.json`;
    link.click();
    URL.revokeObjectURL(url);
    message.success('JSON文件已导出');
};

const importJson = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const jsonData = JSON.parse(event.target?.result as string);
                    Object.assign(currentCardData, jsonData);
                    currentCardType.value = jsonData.type || '';
                    message.success('JSON文件已导入');
                } catch (error) {
                    message.error('JSON文件格式错误');
                }
            };
            reader.readAsText(file);
        }
    };
    input.click();
};
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

.form-content {
    flex: 1;
    overflow: hidden;
    background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
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
    transition: all 0.3s ease;
}

.form-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
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

<template>
    <div class="card-side-editor">
        <!-- 卡牌类型选择 -->
        <n-card :title="sideTitle" size="small" class="form-card">
            <div class="form-row">
                <!-- 语言选择 - 左列 -->
                <div class="form-field layout-half">
                    <n-form-item :label="$t('cardEditor.panel.language')">
                        <n-select v-model:value="currentLanguage" :options="languageOptions"
                            :placeholder="$t('cardEditor.panel.selectLanguage')" @update:value="updateLanguage" />
                    </n-form-item>
                </div>

                <!-- 卡牌类型选择 - 右列 -->
                <div class="form-field layout-half">
                    <n-form-item :label="$t('cardEditor.panel.selectCardType')">
                        <n-select v-model:value="currentSideType" :options="cardTypeOptions"
                            :placeholder="$t('cardEditor.panel.selectCardType')"
                            @update:value="onCardTypeChange" />
                    </n-form-item>
                </div>
            </div>
        </n-card>

        <!-- 动态表单 -->
        <n-card v-if="currentSideType && currentFormConfig" :title="$t('cardEditor.panel.cardProperties')"
            size="small" class="form-card">
            <n-form ref="dynamicFormRef" :model="sideCardData" label-placement="top" size="small">
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
                            @move-string-array-item-up="moveStringArrayItemUp(field, $event)"
                            @move-string-array-item-down="moveStringArrayItemDown(field, $event)"
                            @edit-string-array-item="(index, newValue) => editStringArrayItem(field, index, newValue)"
                            @remove-image="removeImage(field)" />
                    </div>
                </div>
            </n-form>
        </n-card>

        <!-- 插画布局编辑器 -->
        <IllustrationLayoutEditor v-if="sideCardData.picture_base64"
            :image-src="sideCardData.picture_base64" :layout="sideCardData.picture_layout"
            :card_type="sideCardData.type"
            @update:layout="updateIllustrationLayout" />

        <!-- 卡牌信息 -->
        <n-card v-if="currentSideType" :title="$t('cardEditor.panel.cardInfo')" size="small"
            class="form-card">
            <n-form :model="sideCardData" label-placement="top" size="small">
                <div class="form-row">
                    <!-- 插画作者 -->
                    <div class="form-field layout-third">
                        <FormFieldComponent :field="{
                            key: 'illustrator',
                            name: $t('cardEditor.panel.illustrator'),
                            type: 'text'
                        }" :value="sideCardData.illustrator || ''" :new-string-value="newStringValue"
                            @update:value="updateSideData('illustrator', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                    <!-- 遭遇组序号 -->
                    <div class="form-field layout-third">
                        <FormFieldComponent :field="{
                            key: 'encounter_group_number',
                            name: $t('cardEditor.panel.encounterGroupNumber'),
                            type: 'text'
                        }" :value="sideCardData.encounter_group_number || ''"
                            :new-string-value="newStringValue"
                            @update:value="updateSideData('encounter_group_number', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                    <!-- 卡牌序号 -->
                    <div class="form-field layout-third">
                        <FormFieldComponent :field="{
                            key: 'card_number',
                            name: $t('cardEditor.panel.cardNumber'),
                            type: 'text'
                        }" :value="sideCardData.card_number || ''" :new-string-value="newStringValue"
                            @update:value="updateSideData('card_number', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                </div>
                <div class="form-row">
                    <!-- 卡牌数量 -->
                    <div class="form-field layout-half">
                        <FormFieldComponent :field="{
                            key: 'quantity',
                            name: '卡牌数量',
                            type: 'number',
                            min: 1,
                            max: 999,
                            defaultValue: 1
                        }" :value="sideCardData.quantity || 1" :new-string-value="newStringValue"
                            @update:value="updateSideData('quantity', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                    <!-- 卡牌版权信息 -->
                    <div class="form-field layout-half">
                        <FormFieldComponent :field="{
                            key: 'footer_copyright',
                            name: '版权信息',
                            type: 'text',
                            placeholder: '例如：© 2024 Fantasy Flight Games'
                        }" :value="sideCardData.footer_copyright || ''" :new-string-value="newStringValue"
                            @update:value="updateSideData('footer_copyright', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                </div>
                <div class="form-row">
                    <!-- 卡牌备注信息 -->
                    <div class="form-field layout-full">
                        <FormFieldComponent :field="{
                            key: 'remark',
                            name: $t('cardEditor.panel.cardRemarks'),
                            type: 'textarea',
                            rows: 2,
                            maxlength: 200
                        }" :value="sideCardData.requirements || ''" :new-string-value="newStringValue"
                            @update:value="updateSideData('requirements', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                </div>
            </n-form>
        </n-card>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import type { FormField, CardTypeConfig, ShowCondition } from '@/config/cardTypeConfigs';
import FormFieldComponent from './FormField.vue';
import IllustrationLayoutEditor from './IllustrationLayoutEditor.vue';

interface Props {
    side: 'front' | 'back';
    cardData: any;
    cardTypeConfigs: Record<string, CardTypeConfig>;
    cardTypeOptions: any[];
    languageOptions: any[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'update-card-data': [side: string, fieldKey: string, value: any];
    'update-card-type': [side: string, type: string];
    'trigger-preview': [];
}>();

const { t } = useI18n();

// 当前面的数据（使用响应式引用确保数据独立）
const sideCardData = reactive({ ...props.cardData });

// 计算属性
const sideTitle = computed(() => {
    return props.side === 'back' ? t('cardEditor.panel.backSide') : t('cardEditor.panel.frontSide');
});

const currentLanguage = computed({
    get: () => sideCardData.language || 'zh',
    set: (value) => {
        sideCardData.language = value;
        updateSideData('language', value);
    }
});

// 当前面的类型 - 必须在watch之前声明
const currentSideType = ref(sideCardData.type || '');

// 监听props变化，更新本地数据
watch(() => props.cardData, (newData) => {
    Object.keys(sideCardData).forEach(key => {
        delete sideCardData[key];
    });
    Object.assign(sideCardData, newData);

    // 确保类型同步更新
    if (newData.type !== currentSideType.value) {
        currentSideType.value = newData.type || '';
        console.log(`🔄 ${props.side}面从props更新卡牌类型:`, currentSideType.value);
    }
}, { deep: true, immediate: true });

// 监听sideCardData的类型变化，同步更新currentSideType
watch(() => sideCardData.type, (newType) => {
    if (newType !== currentSideType.value) {
        currentSideType.value = newType || '';
        console.log(`🔄 ${props.side}面卡牌类型已更新:`, currentSideType.value);
    }
});

const currentFormConfig = computed((): CardTypeConfig | null => {
    return currentSideType.value ? props.cardTypeConfigs[currentSideType.value] : null;
});

// 表单操作状态
const newStringValue = ref('');

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

// 表单操作方法
const getFieldValue = (field: FormField) => {
    if (field.index !== undefined) {
        const array = getDeepValue(sideCardData, field.key);
        return Array.isArray(array) ? array[field.index] : undefined;
    }
    return getDeepValue(sideCardData, field.key);
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
        setDeepValue(sideCardData, field.key, value);
    }

    // 通知父组件数据变化
    updateSideData(field.key, value);
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
    let array = getDeepValue(sideCardData, arrayPath);
    if (!Array.isArray(array)) {
        array = [];
        setDeepValue(sideCardData, arrayPath, array);
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

const moveStringArrayItemUp = (field: FormField, index: number) => {
    if (index <= 0) return;
    const currentArray = getFieldValue(field);
    if (Array.isArray(currentArray)) {
        const item = currentArray[index];
        currentArray.splice(index, 1);
        currentArray.splice(index - 1, 0, item);
        setFieldValue(field, currentArray);
    }
};

const moveStringArrayItemDown = (field: FormField, index: number) => {
    const currentArray = getFieldValue(field);
    if (!Array.isArray(currentArray) || index >= currentArray.length - 1) return;
    const item = currentArray[index];
    currentArray.splice(index, 1);
    currentArray.splice(index + 1, 0, item);
    setFieldValue(field, currentArray);
};

const editStringArrayItem = (field: FormField, index: number, newValue: string) => {
    const currentArray = getFieldValue(field);
    if (Array.isArray(currentArray) && index >= 0 && index < currentArray.length) {
        currentArray[index] = newValue;
        setFieldValue(field, currentArray);
    }
};

// 更新语言
const updateLanguage = (value: string) => {
    sideCardData.language = value;
    updateSideData('language', value);
};

// 卡牌类型变更处理
const onCardTypeChange = (newType: string) => {
    // 保留需要保留的字段
    const hiddenFields = ['id', 'created_at', 'version', 'type', 'name', 'language', 'quantity', 'footer_copyright'];
    const newData = {};

    hiddenFields.forEach(field => {
        if (sideCardData[field] !== undefined) {
            newData[field] = sideCardData[field];
        }
    });

    // 清空其他字段
    Object.keys(sideCardData).forEach(key => {
        if (!hiddenFields.includes(key)) {
            delete sideCardData[key];
        }
    });

    Object.assign(sideCardData, newData);

    // 更新类型
    currentSideType.value = newType;
    sideCardData.type = newType;

    // 应用默认值
    const config = props.cardTypeConfigs[newType];
    if (config) {
        config.fields.forEach(field => {
            if (field.defaultValue !== undefined) {
                setDeepValue(sideCardData, field.key, field.defaultValue);
            }
        });
    }

    // 通知父组件类型变化
    emit('update-card-type', props.side, newType);
    emit('trigger-preview');
};

// 更新插画布局
const updateIllustrationLayout = (newLayout: string) => {
    sideCardData.picture_layout = newLayout;
    updateSideData('picture_layout', newLayout);
};

// 更新面数据
const updateSideData = (fieldKey: string, value: any) => {
    emit('update-card-data', props.side, fieldKey, value);
    emit('trigger-preview');
};

// 删除图片
const removeImage = (field: FormField) => {
    setFieldValue(field, '');
};
</script>

<style scoped>
.card-side-editor {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.form-card {
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

/* 响应式设计 */
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
</style>
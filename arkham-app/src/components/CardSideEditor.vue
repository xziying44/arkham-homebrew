<template>
    <div class="card-side-editor">
        <!-- 卡牌类型选择 -->
        <n-card :ref="setCardTypeSection" :title="sideTitle" size="small" class="form-card">
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
        <n-card :ref="setPropertiesSection" v-if="currentSideType && currentFormConfig" :title="$t('cardEditor.panel.cardProperties')"
            size="small" class="form-card">
            <n-form ref="dynamicFormRef" :model="sideCardData" label-placement="top" size="small">
                <n-tabs v-if="fieldGroupTabs.length" v-model:value="activeFieldGroup" type="line" :animated="false">
                    <n-tab-pane v-for="tab in fieldGroupTabs" :key="tab.key" :name="tab.key"
                        :tab="$t(`cardEditor.groups.${tab.key}`)" display-directive="if">
                        <transition name="card-props-fade" mode="out-in">
                            <div :key="tab.key">
                                <div v-for="(row, rowIndex) in fieldGroupRows[tab.key] || []" :key="rowIndex" class="form-row">
                                    <div v-for="field in row"
                                        :key="field.key + (field.index !== undefined ? `_${field.index}` : '')"
                                        class="form-field" :class="getFieldLayoutClass(field.layout)">
                                        <FormFieldComponent :field="field" :value="getFieldValue(field)"
                                            :subclasses="sideCardData.subclass || []"
                                            :card-language="sideCardData.language || 'zh'"
                                            :new-string-value="newStringValue" @update:value="setFieldValue(field, $event)"
                                            @update:subclasses="updateSubclasses"
                                            @update:new-string-value="newStringValue = $event"
                                            @add-multi-select-item="addMultiSelectItem(field, $event)"
                                            @remove-multi-select-item="removeMultiSelectItem(field, $event)"
                                            @add-string-array-item="addStringArrayItem(field)"
                                            @remove-string-array-item="removeStringArrayItem(field, $event)"
                                            @move-string-array-item-up="moveStringArrayItemUp(field, $event)"
                                            @move-string-array-item-down="moveStringArrayItemDown(field, $event)"
                                            @edit-string-array-item="(index, newValue) => editStringArrayItem(field, index, newValue)"
                                            @remove-image="removeImage(field)" />

                                        <!-- 地点卡快捷操作按钮放在“连接地点图标”字段下方 -->
                                        <div v-if="isLocationType && field.key === 'location_link'" style="margin-top: 6px; display: flex; justify-content: flex-end;">
                                            <n-button tertiary size="small" @click="applyLocationToOtherSide">
                                                {{ $t('cardEditor.locationActions.applyToOtherSide') }}
                                            </n-button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </transition>
                    </n-tab-pane>
                </n-tabs>

                <!-- 冒险参考卡：组合标记效果 -->
                <div v-if="showScenarioTokenGroups" class="scenario-groups-section">
                    <div class="scenario-groups-header">
                        <div class="scenario-groups-title">
                            {{ $t('cardEditor.scenarioGroups.title') }}
                        </div>
                        <div class="scenario-groups-hint">
                            {{ $t('cardEditor.scenarioGroups.tokensHint') }}
                        </div>
                    </div>

                    <div v-for="(group, index) in scenarioGroups" :key="index" class="scenario-group-card">
                        <div class="scenario-group-card__header">
                            <div class="scenario-group-card__title">
                                {{ $t('cardEditor.scenarioGroups.groupLabel', { index: index + 1 }) }}
                            </div>
                            <n-button quaternary type="error" size="tiny" @click="removeScenarioGroup(index)">
                                {{ $t('cardEditor.scenarioGroups.remove') }}
                            </n-button>
                        </div>

                        <div class="form-row">
                            <div class="form-field layout-half">
                                <n-form-item :label="$t('cardEditor.scenarioGroups.tokensLabel')">
                                    <n-select
                                        :value="group.tokens || []"
                                        multiple
                                        :options="getScenarioTokenOptions(index)"
                                        :placeholder="$t('cardEditor.scenarioGroups.tokensPlaceholder')"
                                        @update:value="updateScenarioGroupTokens(index, $event)" />
                                </n-form-item>
                            </div>
                            <div class="form-field layout-half">
                                <n-form-item :label="$t('cardEditor.scenarioGroups.textLabel')">
                                    <n-input
                                        type="textarea"
                                        :rows="2"
                                        :value="group.text || ''"
                                        :placeholder="$t('cardEditor.scenarioGroups.textPlaceholder')"
                                        @update:value="updateScenarioGroupText(index, $event)" />
                                </n-form-item>
                            </div>
                        </div>
                    </div>

                    <n-button dashed block class="scenario-groups-add" :disabled="!hasAvailableScenarioTokens" @click="addScenarioGroup">
                        {{ $t('cardEditor.scenarioGroups.add') }}
                    </n-button>
                    <div v-if="!hasAvailableScenarioTokens" class="scenario-groups-exhausted">
                        {{ $t('cardEditor.scenarioGroups.allUsedHint') }}
                    </div>
                </div>
            </n-form>

            <!-- 插画布局设置展开按钮 -->
            <n-divider v-if="sideCardData.picture_base64" style="margin: 16px 0 12px 0;" />
            <div v-if="sideCardData.picture_base64" style="display: flex; justify-content: center;">
                <n-button
                    type="primary"
                    secondary
                    size="medium"
                    @click="toggleIllustrationLayout"
                    style="width: 100%; font-weight: 500;">
                    <template #icon>
                        <n-icon>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                                <path v-if="illustrationLayoutCollapsed.includes('illustration')"
                                    d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"
                                    fill="currentColor"/>
                                <path v-else
                                    d="M233.4 105.4c12.5-12.5 32.8-12.5 45.3 0l192 192c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L256 173.3 86.6 342.6c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3l192-192z"
                                    fill="currentColor"/>
                            </svg>
                        </n-icon>
                    </template>
                    {{ illustrationLayoutCollapsed.includes('illustration') ?
                       $t('cardEditor.illustrationLayout.hideSettings') :
                       $t('cardEditor.illustrationLayout.showSettings') }}
                </n-button>
            </div>
        </n-card>

        <!-- 插画布局编辑器 -->
        <div ref="illustrationSection" v-if="sideCardData.picture_base64 && illustrationLayoutCollapsed.includes('illustration')"
             style="margin-top: 12px;">
            <IllustrationLayoutEditor
                :image-src="sideCardData.picture_base64"
                :layout="sideCardData.picture_layout"
                :card_type="sideCardData.type"
                @update:layout="updateIllustrationLayout" />
        </div>

        <!-- 高级文本布局编辑器 -->
        <n-card :ref="setTextLayoutSection" v-if="currentSideType" :title="$t('cardEditor.panel.advancedTextLayout')" size="small"
            class="form-card">
            <n-button @click="showTextBoundaryModal = true" size="small" type="primary">
                {{ $t('cardEditor.panel.advancedTextLayout') }}
            </n-button>
        </n-card>

        <!-- 卡牌信息 -->
        <n-card :ref="setCardInfoSection" v-if="currentSideType" :title="$t('cardEditor.panel.cardInfo')" size="small"
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
                    <!-- 卡牌数量 - 正面可编辑，背面只读（共享数据）-->
                    <div class="form-field layout-half" v-if="props.side === 'front'">
                        <FormFieldComponent :field="{
                            key: 'quantity',
                            name: $t('cardEditor.panel.cardQuantity'),
                            type: 'number',
                            min: 1,
                            max: 999,
                            defaultValue: 1
                        }" :value="quantity" :new-string-value="newStringValue"
                            @update:value="quantity = $event"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                    <div class="form-field layout-half" v-else>
                        <n-form-item :label="$t('cardEditor.panel.cardQuantity')">
                            <n-input-number :value="quantity" readonly :precision="0" :min="1" :max="999"
                                style="width: 100%" />
                        </n-form-item>
                    </div>
                    <!-- 卡牌版权信息 - 正反面都可编辑（独立数据）-->
                    <div class="form-field layout-half">
                        <FormFieldComponent :field="{
                            key: 'footer_copyright',
                            name: $t('cardEditor.panel.copyright'),
                            type: 'text',
                            placeholder: '例如：© FFG'
                        }" :value="sideCardData.footer_copyright || ''" :new-string-value="newStringValue"
                            @update:value="updateSideData('footer_copyright', $event)"
                            @update:new-string-value="newStringValue = $event" />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-field layout-half">
                        <n-form-item :label="$t('cardEditor.panel.footerIcon')">
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <n-select
                                    v-model:value="footerIconPath"
                                    :options="footerIconOptions"
                                    :loading="footerIconLoading"
                                    :placeholder="$t('cardEditor.panel.footerIconPlaceholder')"
                                    clearable
                                    filterable />
                                <n-button tertiary size="small" :loading="footerIconLoading" @click="loadFooterIconOptions">
                                    {{ $t('common.buttons.refresh') }}
                                </n-button>
                            </div>
                            <template #feedback v-if="footerIconPath">
                                <span style="color: #888;">{{ footerIconPath }}</span>
                            </template>
                        </n-form-item>
                    </div>
                    <div class="form-field layout-half" v-if="isInvestigatorType">
                        <n-form-item :label="$t('cardEditor.panel.investigatorFooterType')">
                            <n-radio-group v-model:value="investigatorFooterType" size="small">
                                <n-space>
                                    <n-radio value="normal">{{ $t('cardEditor.panel.investigatorFooterTypeNormal') }}</n-radio>
                                    <n-radio value="big-art">{{ $t('cardEditor.panel.investigatorFooterTypeBigArt') }}</n-radio>
                                </n-space>
                            </n-radio-group>
                        </n-form-item>
                    </div>
                </div>
                <!-- 卡牌备注信息 - 正反面都可编辑（独立数据）-->
                <div class="form-row">
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

        <!-- 文本边界编辑器抽屉 -->
        <n-drawer v-model:show="showTextBoundaryModal" :width="600" placement="left" :show-mask="false">
            <n-drawer-content :title="$t('cardEditor.panel.advancedTextLayout')" closable>
                <TextBoundaryEditor
                    :card-type="sideCardData.type"
                    :text-boundary="sideCardData.text_boundary"
                    @update:text-boundary="updateTextBoundary" />
            </n-drawer-content>
        </n-drawer>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, nextTick, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import type { FormField, CardTypeConfig, ShowCondition } from '@/config/cardTypeConfigs';
import { cardFieldGroups } from '@/config/cardFieldGroups';
import type { TreeOption } from '@/api/types';
import { WorkspaceService } from '@/api';
import FormFieldComponent from './FormField.vue';
import IllustrationLayoutEditor from './IllustrationLayoutEditor.vue';
import TextBoundaryEditor from './TextBoundaryEditor.vue';

interface Props {
    side: 'front' | 'back';
    cardData: any;
    cardTypeConfigs: Record<string, CardTypeConfig>;
    cardTypeOptions: any[];
    languageOptions: any[];
    activeFieldGroupKey?: string;
}

interface FieldGroupTab {
    key: string;
    fields: FormField[];
}

interface ExtendedTreeOption extends TreeOption {
    relativePath?: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'update-card-data': [side: string, fieldKey: string, value: any];
    'update-card-type': [side: string, type: string];
    'trigger-preview': [];
    'update:active-field-group': [value: string];
}>();

const { t } = useI18n();
const message = useMessage();

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

// 获取共享的卡牌数量（正面和背面都使用同一个数量）
const quantity = computed({
    get: () => {
        // 对于背面，从props中获取正面数据
        if (props.side === 'back') {
            return props.cardData.quantity || 1;
        }
        // 对于正面，从sideCardData获取
        return sideCardData.quantity || 1;
    },
    set: (value) => {
        // 只允许正面修改数量
        if (props.side === 'front') {
            updateSideData('quantity', value);
        }
    }
});

// 当前面的类型 - 必须在watch之前声明
const currentSideType = ref(sideCardData.type || '');
const isLocationType = computed(() => currentSideType.value === '地点卡');
const isInvestigatorType = computed(() => currentSideType.value === '调查员');
const isScenarioReferenceType = computed(() => currentSideType.value === '冒险参考卡');
const showScenarioTokenGroups = computed(() => isScenarioReferenceType.value && sideCardData.scenario_type !== 2);

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

// 【新增】监听正面数量变化（仅背面需要）
watch(() => props.cardData.quantity, (newQuantity) => {
    if (props.side === 'back' && newQuantity !== undefined) {
        console.log(`🔄 ${props.side}面数量同步更新:`, newQuantity);
        // 触发组件重新渲染，确保显示最新的数量
        // 不需要直接修改sideCardData.quantity，因为quantity计算属性会直接从props获取
    }
});

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
const footerIconLoading = ref(false);
const rootImages = ref<ExtendedTreeOption[]>([]);
const workspaceRootPath = ref('');
const footerIconOptions = computed(() => rootImages.value
    .filter(img => img.relativePath)
    .map(img => ({
        label: img.label,
        value: img.relativePath as string
    }))
);
const footerIconPath = computed({
    get: () => sideCardData.footer_icon_path || '',
    set: (value: string | null) => {
        const nextValue = value || '';
        sideCardData.footer_icon_path = nextValue;
        updateSideData('footer_icon_path', nextValue);
    }
});
const investigatorFooterType = computed({
    get: () => sideCardData.investigator_footer_type || 'normal',
    set: (value: string) => {
        sideCardData.investigator_footer_type = value;
        updateSideData('investigator_footer_type', value);
    }
});

// 冒险参考卡：组合标记配置
const scenarioTokenOptions = computed(() => ([
    { label: `💀 ${t('cardEditor.scenarioGroups.tokenSkull')}`, value: 'skull' },
    { label: `👥 ${t('cardEditor.scenarioGroups.tokenCultist')}`, value: 'cultist' },
    { label: `📜 ${t('cardEditor.scenarioGroups.tokenTablet')}`, value: 'tablet' },
    { label: `👁️ ${t('cardEditor.scenarioGroups.tokenElderThing')}`, value: 'elder_thing' }
]));

const getScenarioCard = (ensure = true) => {
    const current = sideCardData.scenario_card;
    if (!isScenarioReferenceType.value) {
        return ensure ? {} : current;
    }
    if (!current || typeof current !== 'object') {
        if (!ensure) return current;
        sideCardData.scenario_card = {};
    }
    return sideCardData.scenario_card;
};

const scenarioGroups = computed(() => {
    if (!showScenarioTokenGroups.value) return [];
    const scenarioCard = getScenarioCard();
    if (!Array.isArray(scenarioCard.groups)) {
        scenarioCard.groups = [];
    }
    return scenarioCard.groups;
});

const isTokenUsed = (token: string, excludeIndex?: number) => {
    return scenarioGroups.value.some((group, index) => {
        if (excludeIndex !== undefined && index === excludeIndex) return false;
        return Array.isArray(group.tokens) && group.tokens.includes(token);
    });
};

const getScenarioTokenOptions = (currentIndex: number) => {
    return scenarioTokenOptions.value.map(option => ({
        ...option,
        disabled: isTokenUsed(option.value, currentIndex)
    }));
};

const getAvailableScenarioTokens = (excludeIndex?: number) => {
    return scenarioTokenOptions.value
        .map(option => option.value as string)
        .filter(token => !isTokenUsed(token, excludeIndex));
};

const hasAvailableScenarioTokens = computed(() => getAvailableScenarioTokens().length > 0);

const commitScenarioGroups = (groups: Array<{ tokens?: string[]; text?: string }>) => {
    if (!showScenarioTokenGroups.value) return;
    const scenarioCard = getScenarioCard();
    scenarioCard.groups = groups.map(group => ({
        tokens: Array.isArray(group.tokens) ? group.tokens.filter(Boolean) : [],
        text: group.text || ''
    }));
    updateSideData('scenario_card.groups', scenarioCard.groups);
};

const addScenarioGroup = () => {
    if (!showScenarioTokenGroups.value || !hasAvailableScenarioTokens.value) return;
    const nextGroups = [...scenarioGroups.value.map(group => ({
        tokens: Array.isArray(group.tokens) ? [...group.tokens] : [],
        text: group.text || ''
    }))];
    nextGroups.push({ tokens: [], text: '' });
    commitScenarioGroups(nextGroups);
};

const updateScenarioGroupTokens = (index: number, tokens: string[]) => {
    if (!showScenarioTokenGroups.value) return;
    const sanitizedTokens = Array.from(new Set(tokens || []))
        .filter(token => !isTokenUsed(token, index));
    const nextGroups = scenarioGroups.value.map((group, idx) => {
        if (idx !== index) {
            return {
                tokens: Array.isArray(group.tokens) ? [...group.tokens] : [],
                text: group.text || ''
            };
        }
        return {
            tokens: sanitizedTokens,
            text: group.text || ''
        };
    });
    commitScenarioGroups(nextGroups);
};

const updateScenarioGroupText = (index: number, text: string) => {
    if (!showScenarioTokenGroups.value) return;
    const nextGroups = scenarioGroups.value.map((group, idx) => ({
        tokens: Array.isArray(group.tokens) ? [...group.tokens] : [],
        text: idx === index ? text : (group.text || '')
    }));
    commitScenarioGroups(nextGroups);
};

const removeScenarioGroup = (index: number) => {
    if (!showScenarioTokenGroups.value) return;
    const nextGroups = scenarioGroups.value.filter((_, idx) => idx !== index)
        .map(group => ({
            tokens: Array.isArray(group.tokens) ? [...group.tokens] : [],
            text: group.text || ''
        }));
    commitScenarioGroups(nextGroups);
};

// 文本边界编辑器模态状态
const showTextBoundaryModal = ref(false);

// 插画布局编辑器折叠状态（默认收起）
const illustrationLayoutCollapsed = ref<string[]>([]);

// 工具函数：获取深层嵌套值
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

// 工具函数：获取字段值
const getFieldValue = (field: FormField) => {
    if (field.index !== undefined) {
        const array = getDeepValue(sideCardData, field.key);
        if (Array.isArray(array)) {
            return array[field.index] !== undefined ? array[field.index] : '';
        }
        // 如果不是数组，尝试从旧的单值格式读取
        const oldValue = getDeepValue(sideCardData, field.key);
        return oldValue !== undefined ? oldValue : '';
    }
    return getDeepValue(sideCardData, field.key);
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

const getRelativePath = (absolutePath: string, rootPath: string): string => {
    if (!absolutePath || !rootPath) return '';
    const normalizedAbsolute = absolutePath.replace(/\\/g, '/');
    const normalizedRoot = rootPath.replace(/\\/g, '/');
    if (normalizedAbsolute.startsWith(normalizedRoot)) {
        const relative = normalizedAbsolute.slice(normalizedRoot.length);
        return relative.startsWith('/') ? relative.slice(1) : relative;
    }
    return absolutePath;
};

const extractRootImages = (rootNode: TreeOption, rootPath: string): ExtendedTreeOption[] => {
    const images: ExtendedTreeOption[] = [];
    if (rootNode.children) {
        for (const child of rootNode.children) {
            if (child.type === 'image' && child.path && child.label.toLowerCase().endsWith('.png')) {
                const relativePath = getRelativePath(child.path, rootPath);
                images.push({
                    label: child.label,
                    key: child.key,
                    type: child.type,
                    path: child.path,
                    relativePath
                });
            }
        }
    }
    return images.sort((a, b) => a.label.localeCompare(b.label));
};

const loadFooterIconOptions = async () => {
    footerIconLoading.value = true;
    try {
        const fileTree = await WorkspaceService.getFileTree();
        workspaceRootPath.value = fileTree.fileTree?.path || '';
        rootImages.value = extractRootImages(fileTree.fileTree, workspaceRootPath.value);
    } catch (error: any) {
        console.warn('加载页脚图标失败', error);
        message.warning(t('common.messages.operationFailed'));
    } finally {
        footerIconLoading.value = false;
    }
};

watch(currentSideType, (newType) => {
    if (newType === '调查员' && !sideCardData.investigator_footer_type) {
        investigatorFooterType.value = 'normal';
    }
});

onMounted(() => {
    loadFooterIconOptions();
});

const buildFieldRows = (fields: FormField[]) => {
    const rows: FormField[][] = [];
    let currentRow: FormField[] = [];
    let currentRowWidth = 0;

    const layoutWeights: Record<string, number> = {
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
};

const fieldGroupTabs = computed<FieldGroupTab[]>(() => {
    if (!currentFormConfig.value) return [];

    const groups = cardFieldGroups.default;
    const usedKeys = new Set<string>();

    const tabs = groups
        .map(group => {
            const matchedFields = visibleFields.value.filter(field => group.fields.includes(field.key));
            matchedFields.forEach(field => usedKeys.add(field.key));
            return { key: group.key, fields: matchedFields } as FieldGroupTab;
        })
        .filter(group => group.fields.length > 0);

    const otherFields = visibleFields.value.filter(field => !usedKeys.has(field.key));
    if (otherFields.length > 0) {
        tabs.push({ key: 'other', fields: otherFields });
    }

    return tabs;
});

const activeFieldGroup = ref<string>('');

const resolveActiveFieldGroup = (candidate?: string) => {
    const tabs = fieldGroupTabs.value;
    if (!tabs.length) return '';
    if (candidate && tabs.some(tab => tab.key === candidate)) {
        return candidate;
    }
    return tabs[0].key;
};

watch(
    [fieldGroupTabs, () => props.activeFieldGroupKey],
    ([, activeKey]) => {
        const next = resolveActiveFieldGroup(activeKey || activeFieldGroup.value);
        if (activeFieldGroup.value !== next) {
            activeFieldGroup.value = next;
        }

        // 如果父级传入的值无效，回退时通知父级同步
        if (activeKey && activeKey !== next) {
            emit('update:active-field-group', next);
        }
    },
    { immediate: true }
);

watch(activeFieldGroup, (val, oldVal) => {
    if (val !== oldVal) {
        emit('update:active-field-group', val);
    }
});

const fieldGroupRows = computed<Record<string, FormField[][]>>(() => {
    const rowsMap: Record<string, FormField[][]> = {};
    fieldGroupTabs.value.forEach(tab => {
        rowsMap[tab.key] = buildFieldRows(tab.fields);
    });
    return rowsMap;
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
const setFieldValue = (field: FormField, value: any) => {
    if (field.index !== undefined) {
        setArrayValue(field.key, field.index, value);
        // 对于带索引的字段，传递完整的字段标识符
        updateSideData(`${field.key}[${field.index}]`, value);
    } else {
        setDeepValue(sideCardData, field.key, value);
        // 通知父组件数据变化
        updateSideData(field.key, value);
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

const updateSubclasses = (value: string[]) => {
    setDeepValue(sideCardData, 'subclass', value);
    updateSideData('subclass', value);
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
    // 保留需要保留的字段（移除quantity，因为现在是共享的）
    const hiddenFields = ['id', 'created_at', 'version', 'type', 'name', 'language', 'footer_copyright', 'footer_icon_path', 'investigator_footer_type'];
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

// 切换插画布局编辑器显示状态
const toggleIllustrationLayout = () => {
    if (illustrationLayoutCollapsed.value.includes('illustration')) {
        illustrationLayoutCollapsed.value = [];
    } else {
        illustrationLayoutCollapsed.value = ['illustration'];
    }
};

// 展开插画布局编辑器（用于导航跳转）
const expandIllustrationLayout = () => {
    if (!illustrationLayoutCollapsed.value.includes('illustration')) {
        illustrationLayoutCollapsed.value = ['illustration'];
    }
};

// 更新文本边界
const updateTextBoundary = (newBoundary: any) => {
    sideCardData.text_boundary = newBoundary;
    emit('update-card-data', props.side, 'text_boundary', newBoundary);
    emit('trigger-preview');
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

// 快捷操作：将当前侧的地点图标配置应用到另一侧（卡面字段）
const applyLocationToOtherSide = () => {
    if (!isLocationType.value) return;
    const target = props.side === 'front' ? 'back' : 'front';
    const icon = sideCardData.location_icon ? String(sideCardData.location_icon) : '';
    const links = Array.isArray(sideCardData.location_link) ? sideCardData.location_link as any[] : [];
    if (icon) emit('update-card-data', target, 'location_icon', icon);
    if (Array.isArray(links)) emit('update-card-data', target, 'location_link', [...links]);
    emit('trigger-preview');
    message.success(t('cardEditor.locationActions.applySuccess'));
};

// Section refs (用于父组件导航定位)
const cardTypeSection = ref<HTMLElement | null>(null);
const propertiesSection = ref<HTMLElement | null>(null);
const illustrationSection = ref<HTMLElement | null>(null);
const textLayoutSection = ref<HTMLElement | null>(null);
const cardInfoSection = ref<HTMLElement | null>(null);

// 函数 refs：捕获组件的 $el (DOM 元素) 而不是组件实例
const setCardTypeSection = (el: any) => {
    cardTypeSection.value = el?.$el ?? el;
};

const setPropertiesSection = (el: any) => {
    propertiesSection.value = el?.$el ?? el;
};

const setTextLayoutSection = (el: any) => {
    textLayoutSection.value = el?.$el ?? el;
};

const setCardInfoSection = (el: any) => {
    cardInfoSection.value = el?.$el ?? el;
};

// 暴露section refs给父组件用于导航
defineExpose({
    cardTypeSection,
    propertiesSection,
    illustrationSection,
    textLayoutSection,
    cardInfoSection,
    expandIllustrationLayout  // 暴露展开方法
});
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

.card-props-fade-enter-active,
.card-props-fade-leave-active {
    transition: opacity 0.16s ease, transform 0.16s ease;
}

.card-props-fade-enter-from,
.card-props-fade-leave-to {
    opacity: 0;
    transform: translateY(6px);
}

.form-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    align-items: flex-start;
    /* 移动端优化 */
    flex-wrap: wrap;
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
    .card-side-editor {
        /* 确保移动端有足够的空间进行滚动 */
        min-height: 100%;
        padding-bottom: 40px; /* 为底部操作按钮留出空间 */
    }

    .form-row {
        flex-direction: column;
        gap: 12px; /* 移动端减少间距 */
        margin-bottom: 12px;
    }

    .layout-full,
    .layout-half,
    .layout-third,
    .layout-quarter {
        flex: 1;
        width: 100%; /* 确保移动端占满宽度 */
    }

    .form-card {
        margin-bottom: 16px; /* 移动端减少卡片间距 */
    }

    /* 移动端表单字段优化 */
    .form-field {
        min-width: 0;
        width: 100%;
    }
}

.scenario-groups-section {
    margin-top: 16px;
    padding: 12px;
    border: 1px dashed rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.65);
}

.scenario-groups-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    gap: 8px;
    flex-wrap: wrap;
}

.scenario-groups-title {
    font-weight: 600;
    color: #333;
}

.scenario-groups-hint {
    color: #888;
    font-size: 12px;
}

.scenario-group-card {
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.75);
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.scenario-group-card__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.scenario-group-card__title {
    font-weight: 600;
}

.scenario-groups-add {
    margin-top: 4px;
}

.scenario-groups-exhausted {
    margin-top: 6px;
    color: #a0a0a0;
    font-size: 12px;
    text-align: center;
}
</style>

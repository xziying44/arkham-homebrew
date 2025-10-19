<template>
    <n-card v-if="shouldShowEditor" :title="$t('deckOptionEditor.title')" size="small" class="form-card deck-option-card">
        <n-space vertical size="large">
            <!-- 牌库选项列表 -->
            <div class="deck-options-list">
                <div class="section-header">
                    <n-text depth="3" style="font-size: 12px;">{{ $t('deckOptionEditor.currentOptions') }}</n-text>
                    <n-button size="tiny" type="primary" @click="addDeckOption">
                        <template #icon>
                            <n-icon><span style="font-size: 14px;">➕</span></n-icon>
                        </template>
                        {{ $t('deckOptionEditor.addOption') }}
                    </n-button>
                </div>

                <div v-if="deckOptions.length === 0" class="empty-options">
                    <n-empty :description="$t('deckOptionEditor.noOptions')" size="small" />
                </div>

                <div v-else class="options-container">
                    <div v-for="(option, index) in deckOptions" :key="index" class="deck-option-item">
                        <div class="option-header">
                            <div class="option-title">
                                <n-text strong>{{ $t('deckOptionEditor.option') }} {{ index + 1 }}</n-text>
                                <n-tag v-if="option.id" size="tiny" type="info">{{ option.id }}</n-tag>
                            </div>
                            <div class="option-actions">
                                <n-button size="tiny" @click="editOption(index)" :type="editingIndex === index ? 'primary' : 'default'">
                                    {{ editingIndex === index ? $t('deckOptionEditor.editing') : $t('deckOptionEditor.edit') }}
                                </n-button>
                                <n-button size="tiny" type="error" @click="removeOption(index)" quaternary>
                                    {{ $t('deckOptionEditor.delete') }}
                                </n-button>
                            </div>
                        </div>

                        <!-- 选项预览 -->
                        <div v-if="editingIndex !== index" class="option-preview">
                            <n-space size="small" wrap>
                                <n-tag v-if="option.faction && option.faction.length > 0" size="tiny" type="primary">
                                    {{ $t('deckOptionEditor.faction') }}: {{ formatFactionDisplay(option.faction) }}
                                </n-tag>
                                <n-tag v-if="option.type && option.type.length > 0" size="tiny" type="success">
                                    {{ $t('deckOptionEditor.cardType') }}: {{ formatTypeDisplay(option.type) }}
                                </n-tag>
                                <n-tag v-if="option.level" size="tiny" type="warning">
                                    {{ $t('deckOptionEditor.levelRange') }}: {{ option.level.min }}-{{ option.level.max }}
                                </n-tag>
                                <n-tag v-if="option.limit" size="tiny" type="error">
                                    {{ $t('deckOptionEditor.limit') }}: {{ option.limit }}
                                </n-tag>
                                <n-tag v-if="option.not" size="tiny" type="default">
                                    {{ $t('deckOptionEditor.not') }}
                                </n-tag>
                                <n-tag v-if="option.text && option.text.length > 0" size="tiny" type="info">
                                    {{ $t('deckOptionEditor.textContains') }}: {{ option.text.join(', ') }}
                                </n-tag>
                                <n-tag v-if="option.text_exact && option.text_exact.length > 0" size="tiny" type="info">
                                    {{ $t('deckOptionEditor.textExact') }}: {{ option.text_exact.join(', ') }}
                                </n-tag>
                                <n-tag v-if="option.trait && option.trait.length > 0" size="tiny" type="info">
                                    {{ $t('deckOptionEditor.traits') }}: {{ option.trait.join(', ') }}
                                </n-tag>
                            </n-space>
                        </div>

                        <!-- 折叠式选项编辑器 -->
                        <div v-else class="option-editor">
                            <n-form :model="option" label-placement="left" label-width="80" size="small">
                                <!-- ID设置 -->
                                <n-form-item :label="$t('deckOptionEditor.optionId')">
                                    <n-input v-model:value="option.id" :placeholder="$t('deckOptionEditor.optionIdPlaceholder')" />
                                </n-form-item>

                                <!-- 可折叠的配置模块 -->
                                <n-collapse v-model:value="expandedSections" accordion>
                                    <!-- 基础过滤条件 -->
                                    <n-collapse-item :title="$t('deckOptionEditor.basicFilters')" name="basicFilters">
                                        <div class="collapse-content">
                                            <!-- 卡牌类型 -->
                                            <n-form-item :label="$t('deckOptionEditor.cardType')">
                                                <n-select
                                                    v-model:value="option.type"
                                                    :options="cardTypeOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectCardTypes')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>

                                            <!-- 职阶 -->
                                            <n-form-item :label="$t('deckOptionEditor.faction')">
                                                <n-select
                                                    v-model:value="option.faction"
                                                    :options="factionOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectFactions')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>

                                            <!-- 特性 -->
                                            <n-form-item :label="$t('deckOptionEditor.traits')">
                                                <n-dynamic-tags v-model:value="option.trait" :placeholder="$t('deckOptionEditor.addTrait')" />
                                            </n-form-item>

                                            <!-- 槽位 -->
                                            <n-form-item :label="$t('deckOptionEditor.slots')">
                                                <n-select
                                                    v-model:value="option.slot"
                                                    :options="slotOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectSlots')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>

                                            <!-- 使用标记 -->
                                            <n-form-item :label="$t('deckOptionEditor.uses')">
                                                <n-select
                                                    v-model:value="option.uses"
                                                    :options="usesOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectUses')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>
                                        </div>
                                    </n-collapse-item>

                                    <!-- 文本匹配 -->
                                    <n-collapse-item :title="$t('deckOptionEditor.textMatch')" name="textMatch">
                                        <div class="collapse-content">
                                            <n-form-item :label="$t('deckOptionEditor.textContains')">
                                                <n-dynamic-tags v-model:value="option.text" :placeholder="$t('deckOptionEditor.addText')" />
                                            </n-form-item>

                                            <n-form-item :label="$t('deckOptionEditor.textExact')">
                                                <n-dynamic-tags v-model:value="option.text_exact" :placeholder="$t('deckOptionEditor.addExactText')" />
                                            </n-form-item>
                                        </div>
                                    </n-collapse-item>

                                    <!-- 等级系统 -->
                                    <n-collapse-item :title="$t('deckOptionEditor.levelSystem')" name="levelSystem">
                                        <div class="collapse-content">
                                            <n-form-item :label="$t('deckOptionEditor.levelRange')">
                                                <n-space>
                                                    <n-input-number
                                                        v-model:value="option.level.min"
                                                        :min="0"
                                                        :max="10"
                                                        :placeholder="$t('deckOptionEditor.minLevel')"
                                                        style="width: 100px"
                                                    />
                                                    <n-text>-</n-text>
                                                    <n-input-number
                                                        v-model:value="option.level.max"
                                                        :min="0"
                                                        :max="10"
                                                        :placeholder="$t('deckOptionEditor.maxLevel')"
                                                        style="width: 100px"
                                                    />
                                                </n-space>
                                            </n-form-item>
                                        </div>
                                    </n-collapse-item>

                                    <!-- 数量限制 -->
                                    <n-collapse-item :title="$t('deckOptionEditor.quantityLimit')" name="quantityLimit">
                                        <div class="collapse-content">
                                            <n-form-item :label="$t('deckOptionEditor.limit')">
                                                <n-input-number
                                                    v-model:value="option.limit"
                                                    :min="0"
                                                    :max="50"
                                                    :placeholder="$t('deckOptionEditor.limitPlaceholder')"
                                                    style="width: 150px"
                                                />
                                            </n-form-item>
                                        </div>
                                    </n-collapse-item>

                                    <!-- 选择机制 -->
                                    <n-collapse-item :title="$t('deckOptionEditor.selectionMechanism')" name="selectionMechanism">
                                        <div class="collapse-content">
                                            <n-form-item :label="$t('deckOptionEditor.factionSelect')">
                                                <n-select
                                                    v-model:value="option.faction_select"
                                                    :options="factionOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectFactionForSelection')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>

                                            <n-form-item :label="$t('deckOptionEditor.deckSizeSelect')">
                                                <n-select
                                                    v-model:value="option.deck_size_select"
                                                    :options="deckSizeOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectDeckSizes')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>
                                        </div>
                                    </n-collapse-item>

                                    <!-- 高级规则 -->
                                    <n-collapse-item :title="$t('deckOptionEditor.advancedRules')" name="advancedRules">
                                        <div class="collapse-content">
                                            <!-- 否定条件 -->
                                            <n-form-item>
                                                <n-switch v-model:value="option.not">
                                                    <template #checked>{{ $t('deckOptionEditor.notEnabled') }}</template>
                                                    <template #unchecked>{{ $t('deckOptionEditor.notDisabled') }}</template>
                                                </n-switch>
                                            </n-form-item>

                                            <!-- 至少条件 -->
                                            <n-form-item :label="$t('deckOptionEditor.atLeast')">
                                                <n-space vertical size="small">
                                                    <n-switch v-model:value="atLeastEnabled">
                                                        <template #checked>{{ $t('deckOptionEditor.atLeastEnabled') }}</template>
                                                        <template #unchecked>{{ $t('deckOptionEditor.atLeastDisabled') }}</template>
                                                    </n-switch>

                                                    <div v-if="atLeastEnabled">
                                                        <n-space>
                                                            <n-input-number
                                                                v-model:value="option.atleast.min"
                                                                :min="0"
                                                                :max="50"
                                                                :placeholder="$t('deckOptionEditor.minCount')"
                                                                style="width: 120px"
                                                            />
                                                            <n-select
                                                                v-model:value="option.atleast.types"
                                                                :options="cardTypeOptions"
                                                                multiple
                                                                :placeholder="$t('deckOptionEditor.selectAtLeastTypes')"
                                                                style="width: 200px"
                                                            />
                                                        </n-space>
                                                    </div>
                                                </n-space>
                                            </n-form-item>
                                        </div>
                                    </n-collapse-item>
                                </n-collapse>
                            </n-form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 最终JSON预览 -->
            <div class="json-preview-section">
                <div class="section-header">
                    <n-text depth="3" style="font-size: 12px;">{{ $t('deckOptionEditor.finalPreview') }}</n-text>
                    <n-space size="small">
                        <n-button size="tiny" @click="copyJsonToClipboard">
                            <template #icon>
                                <n-icon><span style="font-size: 12px;">📋</span></n-icon>
                            </template>
                            {{ $t('deckOptionEditor.copyJson') }}
                        </n-button>
                        <n-button size="tiny" @click="refreshJsonPreview">
                            <template #icon>
                                <n-icon><span style="font-size: 12px;">🔄</span></n-icon>
                            </template>
                            {{ $t('deckOptionEditor.refresh') }}
                        </n-button>
                    </n-space>
                </div>

                <div class="json-preview-container">
                    <n-scrollbar style="max-height: 300px;">
                        <n-code :code="finalJsonPreview" language="json" word-wrap class="preview-code" />
                    </n-scrollbar>
                </div>
            </div>

          </n-space>
    </n-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, h } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';

interface Props {
    cardData: Record<string, any>;
    cardType: string;
    isDoubleSided?: boolean;
    currentSide?: 'front' | 'back';
}

interface DeckOption {
    id?: string;
    type?: string[];
    faction?: string[];
    trait?: string[];
    slot?: string[];
    uses?: string[];
    text?: string[];
    text_exact?: string[];
    level?: {
        min: number;
        max: number;
    };
    limit?: number;
    faction_select?: string[];
    deck_size_select?: string[];
    not?: boolean;
    atleast?: {
        min: number;
        types: string[];
    };
}

const props = withDefaults(defineProps<Props>(), {
    isDoubleSided: false,
    currentSide: 'front'
});

const emit = defineEmits<{
    'update-deck-options': [options: DeckOption[]];
}>();

const { t } = useI18n();
const message = useMessage();

// 是否应该显示编辑器
const shouldShowEditor = computed(() => {
    return props.cardType === '调查员' || props.cardType === '调查员背面';
});

// 牌库选项数据
const deckOptions = ref<DeckOption[]>([]);
const editingIndex = ref<number>(-1);
const atLeastEnabled = ref(false);

// 折叠面板状态
const expandedSections = ref<string[]>([]);

// JSON预览相关
const finalJsonPreview = ref('');

// 选项配置
const cardTypeOptions = [
    { label: '支援卡 (asset)', value: 'asset' },
    { label: '事件卡 (event)', value: 'event' },
    { label: '技能卡 (skill)', value: 'skill' }
];

const factionOptions = [
    { label: '守护者 (guardian)', value: 'guardian' },
    { label: '探求者 (seeker)', value: 'seeker' },
    { label: '流浪者 (rogue)', value: 'rogue' },
    { label: '潜修者 (mystic)', value: 'mystic' },
    { label: '生存者 (survivor)', value: 'survivor' },
    { label: '中立 (neutral)', value: 'neutral' }
];

const slotOptions = [
    { label: '手部 (hand)', value: 'hand' },
    { label: '奥术 (arcane)', value: 'arcane' },
    { label: '饰品 (accessory)', value: 'accessory' },
    { label: '身体 (body)', value: 'body' },
    { label: '盟友 (ally)', value: 'ally' },
    { label: '塔罗 (tarot)', value: 'tarot' },
    { label: '理智 (sanity)', value: 'sanity' },
    { label: '生命 (health)', value: 'health' }
];

const usesOptions = [
    { label: '充能 (charge)', value: 'charge' },
    { label: '弹药 (ammo)', value: 'ammo' },
    { label: '补给 (supply)', value: 'supply' },
    { label: '秘密 (secret)', value: 'secret' },
    { label: '资源 (resource)', value: 'resource' },
    { label: '证据 (evidence)', value: 'evidence' },
    { label: '供品 (offering)', value: 'offering' }
];

const deckSizeOptions = [
    { label: '20张', value: '20' },
    { label: '25张', value: '25' },
    { label: '30张', value: '30' },
    { label: '35张', value: '35' },
    { label: '40张', value: '40' }
];

// 自定义标签渲染
const renderTag = ({ option }: { option: any }) => {
    return h('span', { style: 'font-size: 12px;' }, option.label);
};

// 添加新的牌库选项
const addDeckOption = () => {
    const newOption: DeckOption = {
        id: `option_${deckOptions.value.length + 1}`,
        type: [],
        faction: [],
        trait: [],
        slot: [],
        uses: [],
        text: [],
        text_exact: [],
        level: { min: 0, max: 5 },
        limit: null,
        faction_select: [],
        deck_size_select: [],
        not: false,
        atleast: null
    };

    deckOptions.value.push(newOption);
    editingIndex.value = deckOptions.value.length - 1;
    message.success(t('deckOptionEditor.messages.optionAdded'));
};

// 编辑选项
const editOption = (index: number) => {
    editingIndex.value = editingIndex.value === index ? -1 : index;

    if (editingIndex.value === index) {
        const option = deckOptions.value[index];
        atLeastEnabled.value = !!option.atleast;
    }
};

// 删除选项
const removeOption = (index: number) => {
    deckOptions.value.splice(index, 1);
    if (editingIndex.value === index) {
        editingIndex.value = -1;
    } else if (editingIndex.value > index) {
        editingIndex.value--;
    }
    // 自动保存
    autoSaveOptions();
};

// 自动保存选项（当数据变化时）
const autoSaveOptions = () => {
    // 避免在数据为空时触发保存
    if (deckOptions.value.length === 0) {
        return;
    }

    // 清理空数据
    const cleanedOptions = deckOptions.value.map(option => {
        const cleaned: DeckOption = { ...option };

        // 移除空数组
        Object.keys(cleaned).forEach(key => {
            if (Array.isArray(cleaned[key]) && cleaned[key].length === 0) {
                delete cleaned[key];
            }
        });

        // 处理至少条件
        if (!atLeastEnabled.value || !cleaned.atleast?.min) {
            delete cleaned.atleast;
        }

        return cleaned;
    });

    emit('update-deck-options', cleanedOptions);
    // 自动保存时不显示消息，避免干扰用户
};

// 生成最终的JSON预览
const generateJsonPreview = () => {
    const cleanedOptions = deckOptions.value.map(option => {
        const cleaned: DeckOption = { ...option };

        // 移除空数组
        Object.keys(cleaned).forEach(key => {
            if (Array.isArray(cleaned[key]) && cleaned[key].length === 0) {
                delete cleaned[key];
            }
        });

        // 处理至少条件
        if (!atLeastEnabled.value || !cleaned.atleast?.min) {
            delete cleaned.atleast;
        }

        // 移除空字符串
        Object.keys(cleaned).forEach(key => {
            if (cleaned[key] === '') {
                delete cleaned[key];
            }
        });

        return cleaned;
    });

    try {
        finalJsonPreview.value = JSON.stringify(cleanedOptions, null, 2);
    } catch (error) {
        finalJsonPreview.value = '// JSON generation failed';
        console.error('JSON预览生成失败:', error);
    }
};

// 格式化职阶显示
const formatFactionDisplay = (factions: string[]) => {
    return factions.map(faction => {
        const factionOption = factionOptions.find(opt => opt.value === faction);
        return factionOption ? factionOption.label : faction;
    }).join(', ');
};

// 格式化类型显示
const formatTypeDisplay = (types: string[]) => {
    return types.map(type => {
        const typeOption = cardTypeOptions.find(opt => opt.value === type);
        return typeOption ? typeOption.label : type;
    }).join(', ');
};

// 复制JSON到剪贴板
const copyJsonToClipboard = async () => {
    try {
        await navigator.clipboard.writeText(finalJsonPreview.value);
        message.success(t('deckOptionEditor.messages.copySuccess'));
    } catch (error) {
        console.error('复制失败:', error);
        message.error(t('deckOptionEditor.messages.copyError'));
    }
};

// 刷新JSON预览
const refreshJsonPreview = () => {
    generateJsonPreview();
    message.success(t('deckOptionEditor.messages.refreshSuccess'));
};

// 从卡牌数据加载选项
const loadFromCardData = () => {
    // deck_options 存储在根级别的 cardData 中
    const options = props.cardData.deck_options || [];

    if (options.length > 0) {
        deckOptions.value = options.map((option: DeckOption, index: number) => ({
            id: option.id || `option_${index + 1}`,
            type: option.type || [],
            faction: option.faction || [],
            trait: option.trait || [],
            slot: option.slot || [],
            uses: option.uses || [],
            text: option.text || [],
            text_exact: option.text_exact || [],
            level: option.level || { min: 0, max: 5 },
            limit: option.limit || null,
            faction_select: option.faction_select || [],
            deck_size_select: option.deck_size_select || [],
            not: option.not || false,
            atleast: option.atleast || null
        }));
        console.log('📚 成功加载deck_options，共', deckOptions.value.length, '个选项');
    } else {
        deckOptions.value = [];
        console.log('📚 没有找到deck_options数据或数据为空');
    }

    editingIndex.value = -1;
    // 生成初始JSON预览
    generateJsonPreview();
};

// 监听卡牌数据变化 - 修复：改进防重复更新机制和添加文件切换检测
let lastKnownDeckOptions = '';
let lastUpdateTime = 0;
let lastCardDataId = '';
watch(() => props.cardData?.deck_options, (newOptions) => {
    if (!shouldShowEditor.value) {
        deckOptions.value = [];
        return;
    }

    // 检测是否切换了不同的卡牌文件
    const currentCardDataId = props.cardData?.id || props.cardData?.name || '';
    const isDifferentCard = currentCardDataId !== lastCardDataId;
    if (isDifferentCard) {
        console.log('📚 检测到切换到不同卡牌，强制重新加载数据');
        lastCardDataId = currentCardDataId;
        lastKnownDeckOptions = ''; // 重置缓存
    }

    const newOptionsString = JSON.stringify(newOptions);
    const currentTime = Date.now();

    // 修复：改进重复检测逻辑，如果是不同卡牌或数据真的变化了，则重新加载
    if (!isDifferentCard && newOptionsString === lastKnownDeckOptions && (currentTime - lastUpdateTime) < 1000) {
        console.log('📚 deck_options数据未变化，跳过更新');
        return; // 数据没有变化且时间间隔很短，跳过
    }

    console.log('📚 检测到deck_options变化，更新数据:', {
        isDifferentCard,
        optionsCount: Array.isArray(newOptions) ? newOptions.length : 0,
        newOptions
    });
    lastKnownDeckOptions = newOptionsString;
    lastUpdateTime = currentTime;
    loadFromCardData();
}, { immediate: true, deep: true });

// 添加额外的监听器来检测整个卡牌数据对象的变化（用于文件切换）
let lastCardDataSnapshot = '';
watch(() => props.cardData, (newCardData) => {
    if (!shouldShowEditor.value) {
        return;
    }

    const currentSnapshot = JSON.stringify({
        id: newCardData?.id,
        name: newCardData?.name,
        deck_options: newCardData?.deck_options
    });

    if (currentSnapshot !== lastCardDataSnapshot) {
        console.log('📚 检测到卡牌数据对象发生变化，强制刷新deck_options');
        lastCardDataSnapshot = currentSnapshot;
        lastKnownDeckOptions = ''; // 重置缓存，强制重新加载
        loadFromCardData();
    }
}, { immediate: false, deep: true });

// 监听至少条件启用状态
watch(atLeastEnabled, (enabled) => {
    if (enabled && editingIndex.value >= 0) {
        const option = deckOptions.value[editingIndex.value];
        if (!option.atleast) {
            option.atleast = {
                min: 1,
                types: []
            };
        }
    } else if (!enabled && editingIndex.value >= 0) {
        delete deckOptions.value[editingIndex.value].atleast;
    }
    // 更新JSON预览和自动保存
    generateJsonPreview();
    autoSaveOptions();
});

// 监听选项数据变化，自动更新JSON预览和保存 - 添加防抖
let updateTimer: number | null = null;
watch(deckOptions, () => {
    // 清除之前的定时器
    if (updateTimer !== null) {
        clearTimeout(updateTimer);
    }

    // 延迟执行，避免频繁触发
    updateTimer = window.setTimeout(() => {
        generateJsonPreview();
        autoSaveOptions();
        updateTimer = null;
    }, 100);
}, { deep: true });

// 初始化
if (shouldShowEditor.value) {
    loadFromCardData();
}
</script>

<style scoped>
.deck-option-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border: 2px solid rgba(102, 126, 234, 0.2);
}

.deck-options-list {
    width: 100%;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.empty-options {
    padding: 20px;
    text-align: center;
}

.options-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.deck-option-item {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.8);
    transition: all 0.2s ease;
}

.deck-option-item:hover {
    border-color: rgba(102, 126, 234, 0.3);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.option-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.option-title {
    display: flex;
    align-items: center;
    gap: 8px;
}

.option-actions {
    display: flex;
    gap: 8px;
}

.option-preview {
    padding: 8px 0;
}

.option-editor {
    margin-top: 16px;
}

.editor-section {
    margin-bottom: 24px;
    padding: 16px;
    background: rgba(248, 250, 252, 0.8);
    border-radius: 6px;
    border: 1px solid rgba(226, 232, 240, 0.6);
}

.section-title {
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(203, 213, 224, 0.5);
}


/* 响应式设计 */
@media (max-width: 768px) {
    .option-header {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
    }

    .section-header {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
    }

    .editor-section {
        padding: 12px;
    }
}

/* 折叠面板内容样式 */
.collapse-content {
    padding: 12px 0;
}

.collapse-content :deep(.n-form-item) {
    margin-bottom: 12px;
}

.collapse-content :deep(.n-form-item:last-child) {
    margin-bottom: 0;
}

/* JSON预览区域 */
.json-preview-section {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    background: rgba(248, 250, 252, 0.8);
    overflow: hidden;
}

.json-preview-container {
    position: relative;
    border: 1px solid rgba(203, 213, 224, 0.5);
    border-radius: 6px;
    background: #f8f9fa;
    margin-top: 8px;
}

.preview-code {
    max-height: 280px;
    overflow-y: auto;
    padding: 16px;
    margin: 0;
    background: transparent;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* 折叠面板样式优化 */
.option-editor :deep(.n-collapse) {
    border: none;
}

.option-editor :deep(.n-collapse-item) {
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 6px;
    margin-bottom: 8px;
    background: rgba(255, 255, 255, 0.9);
    overflow: hidden;
}

.option-editor :deep(.n-collapse-item:last-child) {
    margin-bottom: 0;
}

.option-editor :deep(.n-collapse-item__header) {
    padding: 12px 16px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.option-editor :deep(.n-collapse-item__content) {
    padding: 0 16px 16px;
}

.option-editor :deep(.n-collapse-item__content-wrapper) {
    padding: 0;
}

/* 动画效果 */
.deck-option-item {
    animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式设计优化 */
@media (max-width: 768px) {
    .json-preview-section {
        margin-top: 16px;
    }

    .preview-code {
        font-size: 11px;
        padding: 12px;
    }

    .option-editor :deep(.n-collapse-item__header) {
        padding: 10px 12px;
    }

    .option-editor :deep(.n-collapse-item__content) {
        padding: 0 12px 12px;
    }
}
</style>
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
                                <n-text strong>{{ getOptionDisplayName(option) }}</n-text>
                                <n-tag v-if="option.id && option.id !== option.name" size="tiny" type="info">{{ option.id }}</n-tag>
                            </div>
                            <div class="option-actions">
                                <n-button v-if="editingIndex === index" size="tiny" type="success" @click="saveOption(index)">
                                    {{ $t('deckOptionEditor.save') }}
                                </n-button>
                                <n-button v-else size="tiny" @click="editOption(index)" type="default">
                                    {{ $t('deckOptionEditor.edit') }}
                                </n-button>
                                <n-button v-if="editingIndex === index" size="tiny" @click="cancelEdit(index)">
                                    {{ $t('deckOptionEditor.cancel') }}
                                </n-button>
                                <n-button size="tiny" type="error" @click="removeOption(index)" quaternary>
                                    {{ $t('deckOptionEditor.delete') }}
                                </n-button>
                            </div>
                        </div>

                        <!-- 选项预览 -->
                        <div v-if="editingIndex !== index" class="option-preview">
                            <n-space size="small" wrap>
                                <n-tag v-if="option.name && option.name !== option.id" size="tiny" type="primary">
                                    名称: {{ option.name }}
                                </n-tag>
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
                                <n-tag v-if="option.trait && option.trait.length > 0" size="tiny" type="info">
                                    {{ $t('deckOptionEditor.traits') }}: {{ option.trait.join(', ') }}
                                </n-tag>
                                <n-tag v-if="option.slot && option.slot.length > 0" size="tiny" type="info">
                                    槽位: {{ formatSlotDisplay(option.slot) }}
                                </n-tag>
                                <n-tag v-if="option.uses && option.uses.length > 0" size="tiny" type="info">
                                    使用: {{ formatUsesDisplay(option.uses) }}
                                </n-tag>
                                <n-tag v-if="option.faction_select && option.faction_select.length > 0" size="tiny" type="warning">
                                    职阶选择: {{ formatFactionDisplay(option.faction_select) }}
                                </n-tag>
                                <n-tag v-if="option.deck_size_select && option.deck_size_select.length > 0" size="tiny" type="warning">
                                    牌库大小: {{ option.deck_size_select.join(', ') }}张
                                </n-tag>
                                <n-tag v-if="option.option_select && option.option_select.length > 0" size="tiny" type="warning">
                                    高级属性选择 ({{ option.option_select.length }}项)
                                </n-tag>
                            </n-space>
                        </div>

                        <!-- 选项编辑器 -->
                        <div v-else class="option-editor" :key="`editing-${index}`">
                            <n-form :model="option" label-placement="left" label-width="100" size="small">
                                <!-- ID和名称设置 -->
                                <n-form-item label="选项ID">
                                    <n-input v-model:value="option.id" placeholder="自动生成或手动输入ID" @blur="syncNameFromId(option)" />
                                </n-form-item>
                                <n-form-item label="选项名称">
                                    <n-input v-model:value="option.name" placeholder="名称通常与ID一致，可手动修改" />
                                </n-form-item>

                                <!-- 选择机制 -->
                                <n-form-item label="选择机制">
                                    <n-select
                                        v-model:value="option.selectionType"
                                        :options="selectionTypeOptions"
                                        placeholder="请选择选择机制（只能选择一种）"
                                        @update:value="onSelectionTypeChange(option)"
                                    />
                                </n-form-item>

                                <!-- 根据选择机制显示不同配置 -->
                                <div v-if="option.selectionType && option.selectionType !== 'none'" class="selection-config">
                                    <!-- 职阶选择配置 -->
                                    <div v-if="option.selectionType === 'faction'" class="config-section">
                                        <n-form-item label="可选职阶">
                                            <n-select
                                                v-model:value="option.faction_select"
                                                :options="factionOptions"
                                                multiple
                                                placeholder="选择允许的职阶"
                                                :render-tag="renderTag"
                                            />
                                        </n-form-item>
                                        <n-form-item label="等级范围">
                                            <n-space>
                                                <n-input-number
                                                    v-model:value="option.level.min"
                                                    :min="0"
                                                    :max="10"
                                                    placeholder="最低等级"
                                                    style="width: 100px"
                                                />
                                                <n-text>-</n-text>
                                                <n-input-number
                                                    v-model:value="option.level.max"
                                                    :min="0"
                                                    :max="10"
                                                    placeholder="最高等级"
                                                    style="width: 100px"
                                                />
                                            </n-space>
                                        </n-form-item>
                                    </div>

                                    <!-- 牌库大小选择配置 -->
                                    <div v-if="option.selectionType === 'deckSize'" class="config-section">
                                        <n-form-item label="可选牌库大小">
                                            <n-select
                                                v-model:value="option.deck_size_select"
                                                :options="deckSizeOptions"
                                                multiple
                                                placeholder="选择允许的牌库大小"
                                                :render-tag="renderTag"
                                            />
                                        </n-form-item>
                                    </div>

                                    <!-- 高级属性选择配置 -->
                                    <div v-if="option.selectionType === 'advanced'" class="config-section">
                                        <div class="option-select-list">
                                            <div class="list-header">
                                                <n-text strong>可选属性列表</n-text>
                                                <n-button size="tiny" type="primary" @click="addOptionSelectItem(option)">
                                                    <template #icon><span>➕</span></template>
                                                    添加选项
                                                </n-button>
                                            </div>
                                            <div v-if="!option.option_select || option.option_select.length === 0" class="empty-list">
                                                <n-empty description="暂无可选属性" size="small" />
                                            </div>
                                            <div v-else class="option-items">
                                                <div v-for="(item, itemIndex) in option.option_select" :key="itemIndex" class="option-item">
                                                    <n-card size="small" class="item-card">
                                                        <template #header>
                                                            <div class="item-header">
                                                                <n-input v-model:value="item.id" placeholder="ID" size="tiny" style="width: 120px" @blur="syncItemNameFromId(item)" />
                                                                <n-input v-model:value="item.name" placeholder="名称" size="tiny" style="width: 120px" />
                                                                <n-button size="tiny" type="error" @click="removeOptionSelectItem(option, itemIndex)">删除</n-button>
                                                            </div>
                                                        </template>
                                                        <div class="item-content">
                                                            <!-- 基础过滤条件 -->
                                                            <n-form-item label="卡牌类型">
                                                                <n-select
                                                                    v-model:value="item.type"
                                                                    :options="cardTypeOptions"
                                                                    multiple
                                                                    placeholder="选择卡牌类型"
                                                                    size="tiny"
                                                                    :render-tag="renderTag"
                                                                />
                                                            </n-form-item>
                                                            <n-form-item label="职阶">
                                                                <n-select
                                                                    v-model:value="item.faction"
                                                                    :options="factionOptions"
                                                                    multiple
                                                                    placeholder="选择职阶"
                                                                    size="tiny"
                                                                    :render-tag="renderTag"
                                                                />
                                                            </n-form-item>
                                                            <n-form-item label="特性">
                                                                <n-dynamic-tags v-model:value="item.trait" placeholder="添加特性" size="tiny" />
                                                            </n-form-item>
                                                            <n-form-item label="槽位">
                                                                <n-select
                                                                    v-model:value="item.slot"
                                                                    :options="slotOptions"
                                                                    multiple
                                                                    placeholder="选择槽位"
                                                                    size="tiny"
                                                                    :render-tag="renderTag"
                                                                />
                                                            </n-form-item>
                                                            <n-form-item label="使用标记">
                                                                <n-select
                                                                    v-model:value="item.uses"
                                                                    :options="usesOptions"
                                                                    multiple
                                                                    placeholder="选择使用标记"
                                                                    size="tiny"
                                                                    :render-tag="renderTag"
                                                                />
                                                            </n-form-item>
                                                            <n-form-item label="等级范围">
                                                                <n-space>
                                                                    <n-input-number
                                                                        v-model:value="item.level.min"
                                                                        :min="0"
                                                                        :max="10"
                                                                        placeholder="最低"
                                                                        size="tiny"
                                                                        style="width: 80px"
                                                                    />
                                                                    <n-text>-</n-text>
                                                                    <n-input-number
                                                                        v-model:value="item.level.max"
                                                                        :min="0"
                                                                        :max="10"
                                                                        placeholder="最高"
                                                                        size="tiny"
                                                                        style="width: 80px"
                                                                    />
                                                                </n-space>
                                                            </n-form-item>
                                                        </div>
                                                    </n-card>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 基础条件（仅在无选择机制时显示） -->
                                <div v-show="!option.selectionType || option.selectionType === 'none'" class="basic-conditions">
                                    <n-divider class="section-divider">
                                        <n-text strong>基础条件</n-text>
                                    </n-divider>

                                    <!-- 适合窄布局的单列显示 -->
                                    <div style="display: flex; flex-direction: column; gap: 16px;">
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

                                        <!-- 文本匹配 -->
                                        <n-form-item :label="$t('deckOptionEditor.textContains')">
                                            <n-dynamic-tags v-model:value="option.text" :placeholder="$t('deckOptionEditor.addText')" />
                                        </n-form-item>

                                        <!-- 等级范围 -->
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

                                        <!-- 数量限制 -->
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
                                </div>

                                <!-- 其他条件 -->
                                <n-divider class="section-divider">
                                    <n-text strong>其他条件</n-text>
                                </n-divider>

                                <n-space vertical size="medium">
                                    <!-- 否定条件 -->
                                    <n-form-item>
                                        <n-switch v-model:value="option.not" size="medium">
                                            <template #checked>启用否定条件</template>
                                            <template #unchecked>禁用否定条件</template>
                                        </n-switch>
                                    </n-form-item>

                                    <!-- 至少条件 -->
                                    <n-form-item :label="$t('deckOptionEditor.atLeast')">
                                        <n-space vertical size="small" style="width: 100%">
                                            <n-switch v-model:value="atLeastEnabled" size="medium">
                                                <template #checked>启用至少条件</template>
                                                <template #unchecked>禁用至少条件</template>
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
                                                        :render-tag="renderTag"
                                                    />
                                                </n-space>
                                            </div>
                                        </n-space>
                                    </n-form-item>
                                </n-space>
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
    name?: string;
    type?: string[];
    faction?: string[];
    trait?: string[];
    slot?: string[];
    uses?: string[];
    text?: string[];
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
    selectionType?: 'none' | 'faction' | 'deckSize' | 'advanced';
    option_select?: OptionSelectItem[];
}

interface OptionSelectItem {
    id: string;
    name?: string;
    type?: string[];
    faction?: string[];
    trait?: string[];
    slot?: string[];
    uses?: string[];
    level?: {
        min: number;
        max: number;
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
const editingBackup = ref<DeckOption | null>(null);
const isSavingFromEditor = ref(false); // 添加标志防止保存时触发重新加载

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
    { label: '40张', value: '40' },
    { label: '50张', value: '50' }
];

const selectionTypeOptions = [
    { label: '无选择机制 (正常筛选条件)', value: 'none' },
    { label: '职阶选择 (Class Choice)', value: 'faction' },
    { label: '牌库大小选择 (Deck Size)', value: 'deckSize' },
    { label: '高级属性选择 (Advanced Attributes)', value: 'advanced' }
];

// 自定义标签渲染
const renderTag = ({ option }: { option: any }) => {
    return h('span', { style: 'font-size: 12px;' }, option.label);
};

// 获取选项显示名称
const getOptionDisplayName = (option: DeckOption) => {
    if (option.name) {
        return option.name;
    }
    if (option.id) {
        return option.id;
    }
    const index = deckOptions.value.indexOf(option) + 1;
    return `${t('deckOptionEditor.option')} ${index}`;
};

// ID变化时同步名称
const syncNameFromId = (option: DeckOption) => {
    if (option.id && !option.name) {
        option.name = option.id;
    }
};

// 子项ID变化时同步名称
const syncItemNameFromId = (item: OptionSelectItem) => {
    if (item.id && !item.name) {
        item.name = item.id;
    }
};

// 选择机制变化处理
const onSelectionTypeChange = (option: DeckOption) => {
    // 清除其他选择机制的数据
    if (option.selectionType !== 'faction') {
        option.faction_select = [];
    }
    if (option.selectionType !== 'deckSize') {
        option.deck_size_select = [];
    }
    if (option.selectionType !== 'advanced') {
        option.option_select = [];
    }

    // 设置特殊名称
    if (option.selectionType === 'faction') {
        option.name = 'Class Choice';
    } else if (option.selectionType === 'deckSize') {
        option.name = 'Deck Size';
    } else if (option.selectionType === 'none' || !option.selectionType) {
        // 无选择机制时，如果名称是特殊名称，则清空
        if (option.name === 'Class Choice' || option.name === 'Deck Size') {
            option.name = option.id || '';
        }
    }
};

// 添加高级属性选择项
const addOptionSelectItem = (option: DeckOption) => {
    if (!option.option_select) {
        option.option_select = [];
    }

    const newItem: OptionSelectItem = {
        id: `option_${option.option_select.length + 1}`,
        name: '',
        type: [],
        faction: [],
        trait: [],
        slot: [],
        uses: [],
        level: { min: 0, max: 5 }
    };

    option.option_select.push(newItem);
};

// 删除高级属性选择项
const removeOptionSelectItem = (option: DeckOption, index: number) => {
    if (option.option_select && option.option_select.length > index) {
        option.option_select.splice(index, 1);
    }
};

// 格式化槽位显示
const formatSlotDisplay = (slots: string[]) => {
    return slots.map(slot => {
        const slotOption = slotOptions.find(opt => opt.value === slot);
        return slotOption ? slotOption.label.split(' ')[0] : slot;
    }).join(', ');
};

// 格式化使用标记显示
const formatUsesDisplay = (uses: string[]) => {
    return uses.map(use => {
        const useOption = usesOptions.find(opt => opt.value === use);
        return useOption ? useOption.label.split(' ')[0] : use;
    }).join(', ');
};

// 添加新的牌库选项
const addDeckOption = () => {
    const newOption: DeckOption = {
        id: `option_${deckOptions.value.length + 1}`,
        name: `option_${deckOptions.value.length + 1}`,
        type: [],
        faction: [],
        trait: [],
        slot: [],
        uses: [],
        text: [],
        level: { min: 0, max: 5 },
        limit: null,
        faction_select: [],
        deck_size_select: [],
        not: false,
        atleast: null,
        selectionType: 'none',
        option_select: []
    };

    deckOptions.value.push(newOption);
    editingIndex.value = deckOptions.value.length - 1;
    message.success(t('deckOptionEditor.messages.optionAdded'));
};

// 编辑选项
const editOption = (index: number) => {
    if (editingIndex.value === index) {
        // 如果点击的是正在编辑的选项，不做任何操作
        return;
    }

    // 如果之前有其他选项在编辑状态，先保存它
    if (editingIndex.value >= 0 && editingIndex.value !== index) {
        saveOption(editingIndex.value);
    }

    // 开始编辑新选项
    editingIndex.value = index;
    const option = deckOptions.value[index];

    // 创建当前选项的深拷贝作为备份
    editingBackup.value = JSON.parse(JSON.stringify(option));
    atLeastEnabled.value = !!option.atleast;
};

// 保存选项
const saveOption = (index: number) => {
    if (index >= 0 && index < deckOptions.value.length) {
        editingIndex.value = -1;
        editingBackup.value = null;

        // 设置保存标志，防止保存时触发重新加载
        isSavingFromEditor.value = true;

        // 保存时触发自动保存和预览更新
        generateJsonPreview();
        autoSaveOptions();

        // 重置保存标志
        setTimeout(() => {
            isSavingFromEditor.value = false;
        }, 200);

        message.success(t('deckOptionEditor.messages.optionSaved'));
    }
};

// 取消编辑
const cancelEdit = (index: number) => {
    if (index >= 0 && index < deckOptions.value.length && editingBackup.value) {
        // 恢复备份数据
        deckOptions.value[index] = JSON.parse(JSON.stringify(editingBackup.value));
        editingIndex.value = -1;
        editingBackup.value = null;
        message.info(t('deckOptionEditor.messages.editCancelled'));
    }
};

// 删除选项
const removeOption = (index: number) => {
    // 如果删除的是正在编辑的选项，先清除编辑状态
    if (editingIndex.value === index) {
        editingIndex.value = -1;
        editingBackup.value = null;
    } else if (editingIndex.value > index) {
        editingIndex.value--;
    }

    deckOptions.value.splice(index, 1);

    // 自动保存
    autoSaveOptions();
};

// 自动保存选项（当数据变化时）
const autoSaveOptions = () => {
    // 避免在数据为空时触发保存
    if (deckOptions.value.length === 0) {
        return;
    }

    // 清理空数据并转换为最终格式
    const cleanedOptions = deckOptions.value.map(option => {
        const cleaned: any = {};

        // 基础字段
        if (option.id) cleaned.id = option.id;
        if (option.name && option.name !== option.id) cleaned.name = option.name;

        // 根据选择机制处理数据
        if (option.selectionType === 'faction') {
            cleaned.name = 'Class Choice';
            if (option.faction_select && option.faction_select.length > 0) {
                cleaned.faction_select = option.faction_select;
            }
            if (option.level && (option.level.min !== 0 || option.level.max !== 5)) {
                cleaned.level = { ...option.level };
            }
        } else if (option.selectionType === 'deckSize') {
            cleaned.name = 'Deck Size';
            if (option.deck_size_select && option.deck_size_select.length > 0) {
                cleaned.deck_size_select = option.deck_size_select;
            }
            if (option.faction && option.faction.length > 0) {
                cleaned.faction = option.faction;
            }
        } else if (option.selectionType === 'advanced') {
            if (option.option_select && option.option_select.length > 0) {
                cleaned.option_select = option.option_select.map(item => {
                    const cleanedItem: any = { id: item.id };
                    if (item.name && item.name !== item.id) cleanedItem.name = item.name;
                    if (item.type && item.type.length > 0) cleanedItem.type = item.type;
                    if (item.faction && item.faction.length > 0) cleanedItem.faction = item.faction;
                    if (item.trait && item.trait.length > 0) cleanedItem.trait = item.trait;
                    if (item.slot && item.slot.length > 0) cleanedItem.slot = item.slot;
                    if (item.uses && item.uses.length > 0) cleanedItem.uses = item.uses;
                    if (item.level && (item.level.min !== 0 || item.level.max !== 5)) {
                        cleanedItem.level = { ...item.level };
                    }
                    return cleanedItem;
                });
            }
        } else {
            // 基础条件
            if (option.type && option.type.length > 0) cleaned.type = option.type;
            if (option.faction && option.faction.length > 0) cleaned.faction = option.faction;
            if (option.trait && option.trait.length > 0) cleaned.trait = option.trait;
            if (option.slot && option.slot.length > 0) cleaned.slot = option.slot;
            if (option.uses && option.uses.length > 0) cleaned.uses = option.uses;
            if (option.text && option.text.length > 0) cleaned.text = option.text;
            if (option.level && (option.level.min !== 0 || option.level.max !== 5)) {
                cleaned.level = { ...option.level };
            }
            if (option.limit) cleaned.limit = option.limit;
        }

        // 其他条件
        if (option.not) cleaned.not = option.not;
        if (atLeastEnabled.value && option.atleast && option.atleast.min) {
            cleaned.atleast = { ...option.atleast };
        }

        return cleaned;
    }).filter(option => Object.keys(option).length > 1); // 过滤掉空的选项

    emit('update-deck-options', cleanedOptions);
    // 自动保存时不显示消息，避免干扰用户
};

// 生成最终的JSON预览
const generateJsonPreview = () => {
    // 使用与自动保存相同的清理逻辑
    const cleanedOptions = deckOptions.value.map(option => {
        const cleaned: any = {};

        // 基础字段
        if (option.id) cleaned.id = option.id;
        if (option.name && option.name !== option.id) cleaned.name = option.name;

        // 根据选择机制处理数据
        if (option.selectionType === 'faction') {
            cleaned.name = 'Class Choice';
            if (option.faction_select && option.faction_select.length > 0) {
                cleaned.faction_select = option.faction_select;
            }
            if (option.level && (option.level.min !== 0 || option.level.max !== 5)) {
                cleaned.level = { ...option.level };
            }
        } else if (option.selectionType === 'deckSize') {
            cleaned.name = 'Deck Size';
            if (option.deck_size_select && option.deck_size_select.length > 0) {
                cleaned.deck_size_select = option.deck_size_select;
            }
            if (option.faction && option.faction.length > 0) {
                cleaned.faction = option.faction;
            }
        } else if (option.selectionType === 'advanced') {
            if (option.option_select && option.option_select.length > 0) {
                cleaned.option_select = option.option_select.map(item => {
                    const cleanedItem: any = { id: item.id };
                    if (item.name && item.name !== item.id) cleanedItem.name = item.name;
                    if (item.type && item.type.length > 0) cleanedItem.type = item.type;
                    if (item.faction && item.faction.length > 0) cleanedItem.faction = item.faction;
                    if (item.trait && item.trait.length > 0) cleanedItem.trait = item.trait;
                    if (item.slot && item.slot.length > 0) cleanedItem.slot = item.slot;
                    if (item.uses && item.uses.length > 0) cleanedItem.uses = item.uses;
                    if (item.level && (item.level.min !== 0 || item.level.max !== 5)) {
                        cleanedItem.level = { ...item.level };
                    }
                    return cleanedItem;
                });
            }
        } else {
            // 基础条件
            if (option.type && option.type.length > 0) cleaned.type = option.type;
            if (option.faction && option.faction.length > 0) cleaned.faction = option.faction;
            if (option.trait && option.trait.length > 0) cleaned.trait = option.trait;
            if (option.slot && option.slot.length > 0) cleaned.slot = option.slot;
            if (option.uses && option.uses.length > 0) cleaned.uses = option.uses;
            if (option.text && option.text.length > 0) cleaned.text = option.text;
            if (option.level && (option.level.min !== 0 || option.level.max !== 5)) {
                cleaned.level = { ...option.level };
            }
            if (option.limit) cleaned.limit = option.limit;
        }

        // 其他条件
        if (option.not) cleaned.not = option.not;
        if (atLeastEnabled.value && option.atleast && option.atleast.min) {
            cleaned.atleast = { ...option.atleast };
        }

        return cleaned;
    }).filter(option => Object.keys(option).length > 1); // 过滤掉空的选项

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
        deckOptions.value = options.map((option: any, index: number) => {
            const loadedOption: DeckOption = {
                id: option.id || `option_${index + 1}`,
                name: option.name || option.id || `option_${index + 1}`,
                type: option.type || [],
                faction: option.faction || [],
                trait: option.trait || [],
                slot: option.slot || [],
                uses: option.uses || [],
                text: option.text || [],
                level: option.level || { min: 0, max: 5 },
                limit: option.limit || null,
                faction_select: option.faction_select || [],
                deck_size_select: option.deck_size_select || [],
                not: option.not || false,
                atleast: option.atleast || null,
                selectionType: 'none',
                option_select: []
            };

            // 检测选择机制类型
            if (option.faction_select && option.faction_select.length > 0) {
                loadedOption.selectionType = 'faction';
            } else if (option.deck_size_select && option.deck_size_select.length > 0) {
                loadedOption.selectionType = 'deckSize';
            } else if (option.option_select && option.option_select.length > 0) {
                loadedOption.selectionType = 'advanced';
                loadedOption.option_select = option.option_select.map((item: any) => ({
                    id: item.id || `item_${index + 1}`,
                    name: item.name || item.id || '',
                    type: item.type || [],
                    faction: item.faction || [],
                    trait: item.trait || [],
                    slot: item.slot || [],
                    uses: item.uses || [],
                    level: item.level || { min: 0, max: 5 }
                }));
            }

            return loadedOption;
        });
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
        // 切换卡牌时强制重新加载，即使正在编辑也要退出编辑模式
        loadFromCardData();
        return;
    }

    const newOptionsString = JSON.stringify(newOptions);
    const currentTime = Date.now();

    // 修复：如果正在编辑状态或正在保存，且数据是当前编辑的数据（由自己触发的更新），则跳过重新加载
    if (editingIndex.value >= 0 || isSavingFromEditor.value) {
        // 正在编辑时或正在保存时，跳过所有外部数据更新，避免干扰编辑
        console.log('📚 正在编辑中或正在保存，跳过外部数据更新');
        lastKnownDeckOptions = newOptionsString;
        lastUpdateTime = currentTime;
        return;
    }

    // 修复：改进重复检测逻辑，如果是不同卡牌或数据真的变化了，则重新加载
    if (!isDifferentCard && newOptionsString === lastKnownDeckOptions && (currentTime - lastUpdateTime) < 1000) {
        console.log('📚 deck_options数据未变化，跳过更新');
        return; // 数据没有变化且时间间隔很短，跳过
    }

    console.log('📚 检测到外部deck_options变化，更新数据:', {
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

    // 如果正在编辑或正在保存，跳过数据变化监听（除非是卡牌切换）
    if (editingIndex.value >= 0 || isSavingFromEditor.value) {
        const currentCardDataId = newCardData?.id || newCardData?.name || '';
        if (currentCardDataId === lastCardDataId) {
            console.log('📚 正在编辑中或正在保存，跳过卡牌数据变化监听');
            return;
        }
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
        // 更新卡牌ID记录
        lastCardDataId = newCardData?.id || newCardData?.name || '';
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
    // 更新JSON预览和自动保存 - 仅在非编辑状态下执行
    if (editingIndex.value === -1) {
        generateJsonPreview();
        autoSaveOptions();
    }
});

// 监听选项数据变化，自动更新JSON预览和保存 - 添加防抖和编辑状态检测
let updateTimer: number | null = null;
watch(deckOptions, () => {
    // 清除之前的定时器
    if (updateTimer !== null) {
        clearTimeout(updateTimer);
    }

    // 延迟执行，避免频繁触发
    updateTimer = window.setTimeout(() => {
        // 仅在非编辑状态下执行自动保存和预览更新
        if (editingIndex.value === -1) {
            generateJsonPreview();
            autoSaveOptions();
        } else {
            // 编辑状态下只更新JSON预览，不触发自动保存
            generateJsonPreview();
        }
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
    border-radius: 12px;
}

.deck-options-list {
    width: 100%;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.empty-options {
    padding: 40px 20px;
    text-align: center;
    background: rgba(248, 250, 252, 0.5);
    border-radius: 8px;
    border: 1px dashed rgba(102, 126, 234, 0.3);
}

.options-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.deck-option-item {
    border: 2px solid rgba(226, 232, 240, 0.8);
    border-radius: 12px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.95);
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.deck-option-item:hover {
    border-color: rgba(102, 126, 234, 0.4);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
    transform: translateY(-2px);
}

.option-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(226, 232, 240, 0.6);
}

.option-title {
    display: flex;
    align-items: center;
    gap: 12px;
}

.option-actions {
    display: flex;
    gap: 8px;
}

.option-preview {
    padding: 12px 0;
}

.option-editor {
    margin-top: 20px;
}

/* 选择机制配置样式 */
.selection-config {
    margin: 16px 0;
    padding: 20px;
    background: rgba(248, 250, 252, 0.8);
    border-radius: 8px;
    border: 1px solid rgba(102, 126, 234, 0.2);
}

.config-section {
    margin-bottom: 16px;
}

.config-section:last-child {
    margin-bottom: 0;
}

/* 高级属性选择列表样式 */
.option-select-list {
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.9);
    overflow: hidden;
}

.list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(102, 126, 234, 0.05);
    border-bottom: 1px solid rgba(226, 232, 240, 0.8);
}

.empty-list {
    padding: 20px;
    text-align: center;
}

.option-items {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 400px;
    overflow-y: auto;
}

.option-item {
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.95);
}

.item-card {
    border: none;
    box-shadow: none;
}

.item-card :deep(.n-card__header) {
    padding: 12px 16px 8px;
    border-bottom: 1px solid rgba(226, 232, 240, 0.4);
}

.item-header {
    display: flex;
    gap: 8px;
    align-items: center;
}

.item-content {
    padding: 8px 16px 12px;
}

.item-content :deep(.n-form-item) {
    margin-bottom: 8px;
}

.item-content :deep(.n-form-item:last-child) {
    margin-bottom: 0;
}

/* 基础条件样式 */
.basic-conditions {
    margin: 20px 0;
}

.section-divider {
    margin: 24px 0 16px;
}

.section-divider :deep(.n-divider__title) {
    font-weight: 600;
    color: #667eea;
}

/* 开关样式优化 */
.option-editor :deep(.n-switch) {
    border-radius: 16px;
}

.option-editor :deep(.n-switch__rail) {
    background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
}

.option-editor :deep(.n-switch--checked .n-switch__rail) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    .item-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    .options-container {
        gap: 16px;
    }

    .deck-option-item {
        padding: 16px;
    }
}

/* JSON预览区域 */
.json-preview-section {
    border: 2px solid rgba(226, 232, 240, 0.8);
    border-radius: 12px;
    background: rgba(248, 250, 252, 0.8);
    overflow: hidden;
    margin-top: 24px;
}

.json-preview-container {
    position: relative;
    border: 1px solid rgba(203, 213, 224, 0.5);
    border-radius: 8px;
    background: #f8f9fa;
    margin-top: 12px;
}

.preview-code {
    max-height: 320px;
    overflow-y: auto;
    padding: 20px;
    margin: 0;
    background: transparent;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: #2d3748;
}

/* 动画效果 */
.deck-option-item {
    animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 滚动条样式 */
.option-items::-webkit-scrollbar {
    width: 6px;
}

.option-items::-webkit-scrollbar-track {
    background: rgba(226, 232, 240, 0.3);
    border-radius: 3px;
}

.option-items::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.4);
    border-radius: 3px;
}

.option-items::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.6);
}

.preview-code::-webkit-scrollbar {
    width: 8px;
}

.preview-code::-webkit-scrollbar-track {
    background: rgba(226, 232, 240, 0.3);
    border-radius: 4px;
}

.preview-code::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.4);
    border-radius: 4px;
}

.preview-code::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.6);
}

/* 响应式设计优化 */
@media (max-width: 768px) {
    .json-preview-section {
        margin-top: 20px;
    }

    .preview-code {
        font-size: 12px;
        padding: 16px;
    }

    .selection-config {
        padding: 16px;
        margin: 12px 0;
    }

    .option-items {
        padding: 12px;
        max-height: 300px;
    }
}
</style>
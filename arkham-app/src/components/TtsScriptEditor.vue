<template>
    <n-card v-if="shouldShowTtsScript" :title="$t('ttsScriptEditor.title')" size="small" class="form-card tts-card">
        <n-space vertical size="medium">
            <!-- ID配置 - 所有卡牌类型都支持 -->
            <n-form-item :label="$t('ttsScriptEditor.scriptId.label')">
                <n-space align="center">
                    <n-input v-model:value="scriptConfig.id" :placeholder="$t('ttsScriptEditor.scriptId.placeholder')"
                        :allow-input="allowOnlyAlphaNumeric" style="flex: 1" @update:value="onScriptConfigChange" />
                    <n-button @click="generateRandomId" size="small" type="primary">
                        {{ $t('ttsScriptEditor.scriptId.button') }}
                    </n-button>
                </n-space>
            </n-form-item>

            <!-- 高级配置 - 仅支持的卡牌类型显示 -->
            <template v-if="hasAdvancedConfig">
                <!-- 调查员专用配置 -->
                <template v-if="props.cardType === '调查员'">
                <!-- 额外标记类型 -->
                <n-form-item :label="$t('ttsScriptEditor.investigator.extraTokenLabel')">
                    <n-select v-model:value="investigatorConfig.extraToken" :options="computedExtraTokenOptions"
                        :placeholder="$t('ttsScriptEditor.investigator.extraTokenPlaceholder')"
                        @update:value="onScriptConfigChange" />
                </n-form-item>

                <!-- 四维属性 -->
                <n-form-item :label="$t('ttsScriptEditor.investigator.attributesLabel')">
                    <n-space>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">{{
                                $t('ttsScriptEditor.investigator.willpower') }}</n-text>
                            <n-input-number v-model:value="investigatorConfig.willpowerIcons" :min="0" :max="9"
                                :step="1" size="small" @update:value="onScriptConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.investigator.intellect')
                                }}</n-text>
                            <n-input-number v-model:value="investigatorConfig.intellectIcons" :min="0" :max="9"
                                :step="1" size="small" @update:value="onScriptConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.investigator.combat')
                                }}</n-text>
                            <n-input-number v-model:value="investigatorConfig.combatIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onScriptConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.investigator.agility')
                                }}</n-text>
                            <n-input-number v-model:value="investigatorConfig.agilityIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onScriptConfigChange" />
                        </div>
                    </n-space>
                </n-form-item>

                <!-- 每阶段脚本配置开关 -->
                <n-form-item :label="$t('ttsScriptEditor.investigator.phaseButtons.label')">
                    <n-space vertical size="small">
                        <n-switch v-model:value="enablePhaseButtons" @update:value="onPhaseButtonToggle">
                            <template #checked>{{ $t('ttsScriptEditor.investigator.phaseButtons.enable') }}</template>
                            <template #unchecked>{{ $t('ttsScriptEditor.investigator.phaseButtons.disable')
                                }}</template>
                        </n-switch>

                        <!-- 每阶段脚本配置 -->
                        <div v-show="enablePhaseButtons" class="phase-buttons-config">
                            <n-space vertical size="small">
                                <!-- 按钮列表 -->
                                <div v-for="(button, index) in phaseButtonConfig.buttons" :key="index"
                                    class="button-config-row">
                                    <n-space align="center">
                                        <n-input v-model:value="button.id"
                                            :placeholder="$t('ttsScriptEditor.investigator.phaseButtons.idPlaceholder')"
                                            style="width: 120px" @update:value="onPhaseButtonConfigChange" />
                                        <n-select v-model:value="button.label" :options="buttonLabelOptions"
                                            :placeholder="$t('ttsScriptEditor.investigator.phaseButtons.labelPlaceholder')"
                                            style="width: 140px" @update:value="onPhaseButtonConfigChange" />
                                        <n-select v-model:value="button.color" :options="colorOptions"
                                            :placeholder="$t('ttsScriptEditor.investigator.phaseButtons.colorPlaceholder')"
                                            style="width: 120px" @update:value="onPhaseButtonConfigChange">
                                            <template #label="{ option }">
                                                <div class="color-option-display">
                                                    <div
                                                        :style="{ backgroundColor: option.value, width: '16px', height: '16px', borderRadius: '2px', marginRight: '8px' }">
                                                    </div>
                                                    <span>{{ option.label }}</span>
                                                </div>
                                            </template>
                                            <template #option="{ node, option }">
                                                <div class="color-option-display">
                                                    <div
                                                        :style="{ backgroundColor: option.value, width: '16px', height: '16px', borderRadius: '2px', marginRight: '8px' }">
                                                    </div>
                                                    <span>{{ option.label }}</span>
                                                </div>
                                            </template>
                                        </n-select>
                                        <n-button @click="removePhaseButton(index)" size="small" type="error"
                                            quaternary>
                                            {{ $t('ttsScriptEditor.common.deleteBtn') }}
                                        </n-button>
                                    </n-space>
                                </div>

                                <!-- 添加按钮 -->
                                <n-button @click="addPhaseButton" size="small" type="primary" dashed>
                                    {{ $t('ttsScriptEditor.investigator.phaseButtons.addBtn') }}
                                </n-button>
                            </n-space>
                        </div>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 支援卡/事件卡专用配置 -->
            <template v-if="props.cardType === '支援卡' || props.cardType === '事件卡'">
                <!-- Uses配置 -->
                <n-form-item :label="$t('ttsScriptEditor.asset.usesLabel')">
                    <n-space vertical size="medium">
                        <!-- Uses列表 -->
                        <div v-for="(use, index) in assetConfig.uses" :key="index" class="uses-config-row">
                            <n-space align="center">
                                <div class="uses-input-group">
                                    <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.asset.count')
                                        }}</n-text>
                                    <n-input-number v-model:value="use.count" :min="0" :max="20" :step="1" size="small"
                                        @update:value="onScriptConfigChange" />
                                </div>
                                <div class="uses-input-group">
                                    <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.asset.token')
                                        }}</n-text>
                                    <n-select v-model:value="use.token" :options="computedTokenOptions"
                                        :placeholder="$t('ttsScriptEditor.asset.tokenPlaceholder')" style="width: 120px"
                                        @update:value="(value) => onTokenChange(index, value)" />
                                </div>
                                <div class="uses-input-group">
                                    <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.asset.type')
                                        }}</n-text>
                                    <n-select v-model:value="use.type" :options="getUsesTypeOptions(use.token)"
                                        :placeholder="$t('ttsScriptEditor.asset.typePlaceholder')" style="width: 120px"
                                        @update:value="onScriptConfigChange" />
                                </div>
                                <n-button @click="removeUse(index)" size="small" type="error" quaternary>
                                    {{ $t('ttsScriptEditor.common.deleteBtn') }}
                                </n-button>
                            </n-space>
                        </div>

                        <!-- 添加Uses -->
                        <n-button @click="addUse" size="small" type="primary" dashed>
                            {{ $t('ttsScriptEditor.asset.addBtn') }}
                        </n-button>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 地点卡专用配置 -->
            <template v-if="props.cardType === '地点卡'">
                <!-- 双面卡牌提示 -->
                <div v-if="props.isDoubleSided" style="margin-bottom: 16px;">
                    <n-alert type="info" :title="`${props.currentSide === 'front' ? $t('ttsScriptEditor.location.frontSide') : $t('ttsScriptEditor.location.backSide')} ${$t('ttsScriptEditor.location.locationCard')}`">
                        <template #icon>
                            <n-icon><span style="font-size: 16px;">📍</span></n-icon>
                        </template>
                        {{ props.currentSide === 'front' ?
                            (props.cardData.back?.type === '地点卡' ? $t('ttsScriptEditor.location.bothSidesLocation') : $t('ttsScriptEditor.location.frontIsLocation')) :
                            (props.cardData.type === '地点卡' ? $t('ttsScriptEditor.location.backIsLocation') : $t('ttsScriptEditor.location.onlyBackIsLocation'))
                        }}
                    </n-alert>
                </div>

                <!-- 地点信息显示 -->
                <n-form-item :label="$t('ttsScriptEditor.location.locationIconLabel')">
                    <n-input :value="getEditingCardData().location_icon || $t('ttsScriptEditor.location.notSet')" readonly />
                </n-form-item>

                <n-form-item :label="$t('ttsScriptEditor.location.connectionIconLabel')">
                    <n-input :value="(getEditingCardData().location_link || []).join(', ') || $t('ttsScriptEditor.location.notSet')" readonly />
                </n-form-item>

                <!-- 线索值配置 - 只有已揭示地点才显示 -->
                <n-form-item v-if="getEditingCardData().location_type === '已揭示'" :label="$t('ttsScriptEditor.location.clueValueLabel')">
                    <n-space vertical size="small">
                        <n-text depth="3" style="font-size: 12px;">
                            {{ $t('ttsScriptEditor.location.originalValueLabel') }} {{ getEditingCardData().clues || $t('ttsScriptEditor.location.notSet') }}
                        </n-text>
                        <n-space align="end" style="align-items: flex-end;">
                            <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                                <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.location.countLabel') }}</n-text>
                                <n-input-number v-model:value="clueCount" :min="0" :max="20" :step="1" size="small"
                                    @update:value="onClueCountChange" />
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                                <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.location.typeLabel') }}</n-text>
                                <n-switch v-model:value="isPerInvestigator" @update:value="onClueTypeChange">
                                    <template #checked>{{ $t('ttsScriptEditor.location.perInvestigator') }}</template>
                                    <template #unchecked>{{ $t('ttsScriptEditor.location.fixedCount') }}</template>
                                </n-switch>
                            </div>
                        </n-space>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 签名卡配置 -->
            <template v-if="props.cardType === '调查员'">
                <n-form-item :label="$t('ttsScriptEditor.investigator.signatureCardsLabel')">
                    <n-space vertical size="medium">
                        <!-- 已选择的签名卡列表 -->
                        <div v-if="signatureConfig.length > 0" class="signature-list">
                            <div v-for="(signature, index) in signatureConfig" :key="`${signature.id}-${index}`"
                                class="signature-item">
                                <n-space align="center">
                                    <n-text>{{ signature.name }}</n-text>
                                    <n-input-number v-model:value="signature.count" :min="1" :max="9" size="small"
                                        style="width: 80px" @update:value="onSignatureCountChange" />
                                    <n-button @click="removeSignature(index)" size="small" type="error" quaternary>
                                        {{ $t('ttsScriptEditor.common.deleteBtn') }}
                                    </n-button>
                                </n-space>
                            </div>
                        </div>

                        <!-- 添加签名卡按钮 -->
                        <n-button @click="showSignatureSelector = true" size="small" type="primary" dashed>
                            {{ $t('ttsScriptEditor.investigator.addSignatureCard') }}
                        </n-button>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 预览GMNotes -->
            <n-form-item :label="$t('ttsScriptEditor.preview.label')">
                <div class="gmnotes-preview">
                    <n-code :code="generatedGMNotes" language="json" :word-wrap="true" class="preview-code" />
                    <div class="preview-actions">
                        <n-space size="small">
                            <n-button size="tiny" @click="copyGMNotes" :title="$t('ttsScriptEditor.preview.copyBtn')">
                                {{ $t('ttsScriptEditor.preview.copyBtn') }}
                            </n-button>
                            <n-button size="tiny" @click="regenerateGMNotes"
                                :title="$t('ttsScriptEditor.preview.refreshBtn')">
                                {{ $t('ttsScriptEditor.preview.refreshBtn') }}
                            </n-button>
                        </n-space>
                    </div>
                </div>
            </n-form-item>
            </template>

            <!-- 不支持高级配置的卡牌类型显示提示 -->
            <template v-else>
                <n-alert type="info" :title="$t('ttsScriptEditor.basicConfig.title')">
                    {{ $t('ttsScriptEditor.basicConfig.description') }}
                </n-alert>
            </template>
        </n-space>
    </n-card>

    <!-- 签名卡选择器模态框 -->
    <n-modal v-model:show="showSignatureSelector" style="width: 80%; max-width: 800px;" preset="card">
        <template #header>
            <div class="signature-selector-header">
                <n-text>{{ $t('ttsScriptEditor.investigator.selectSignatureCards') }}</n-text>
            </div>
        </template>

        <div class="signature-selector-content">
            <CardFileBrowser
                :visible="showSignatureSelector"
                @update:visible="showSignatureSelector = $event"
                @confirm="onSignatureCardsSelected"
            />
        </div>

        <template #action>
            <n-space>
                <n-button @click="showSignatureSelector = false">
                    {{ $t('ttsScriptEditor.common.cancel') }}
                </n-button>
            </n-space>
        </template>
    </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n'; // <-- 新增: 引入 useI18n
import { v4 as uuidv4 } from 'uuid';
import {
    generatePhaseButtonScript,
    parsePhaseButtonConfig,
    defaultPhaseButtons,
    buttonLabelOptions,
    colorOptions,
    type PhaseButtonConfig,
    type PhaseButton
} from '@/config/ttsScriptGenerator';
import { WorkspaceService } from '@/api';
import CardFileBrowser from './CardFileBrowser.vue';

// --- 新增: i18n设置 ---
const { t } = useI18n();
// -----------------------

interface Props {
    cardData: Record<string, any>;
    cardType: string;
    isDoubleSided?: boolean;
    currentSide?: 'front' | 'back';
}

interface TtsScriptData {
    GMNotes: string;
    LuaScript: string;
    config?: {
        enablePhaseButtons: boolean;
        phaseButtonConfig: PhaseButtonConfig;
        investigatorConfig: InvestigatorConfig;
        assetConfig: AssetConfig;
        locationConfig: LocationConfig;
        scriptConfig: ScriptConfig;
        signatureConfig: Array<{ id: string; name: string; count: number }>;
    };
}

interface ScriptConfig {
    id: string;
}

interface InvestigatorConfig {
    extraToken: string;
    willpowerIcons: number;
    intellectIcons: number;
    combatIcons: number;
    agilityIcons: number;
}

interface UseConfig {
    count: number;
    type: string;
    token: string;
}

interface AssetConfig {
    uses: UseConfig[];
}

interface LocationConfig {
    location: {
        icons: string;
        connections: string[];
        uses: UseConfig[];
    };
}

const props = withDefaults(defineProps<Props>(), {
    isDoubleSided: false,
    currentSide: 'front'
});
const emit = defineEmits<{
    'update-tts-script': [data: TtsScriptData];
}>();

const message = useMessage();

// 通用脚本配置
const scriptConfig = ref<ScriptConfig>({
    id: ''
});

// 调查员TTS配置
const investigatorConfig = ref<InvestigatorConfig>({
    extraToken: 'None',
    willpowerIcons: 3,
    intellectIcons: 3,
    combatIcons: 2,
    agilityIcons: 2
});

// 支援卡/事件卡TTS配置
const assetConfig = ref<AssetConfig>({
    uses: []
});

// 地点卡TTS配置
const locationConfig = ref<LocationConfig>({
    location: {
        icons: 'Diamond',
        connections: [],
        uses: []
    }
});

// 地点卡线索值相关数据
const clueCount = ref(1);
const isPerInvestigator = ref(false);

// 每阶段按钮配置开关
const enablePhaseButtons = ref(false);

// 每阶段按钮配置
const phaseButtonConfig = ref<PhaseButtonConfig>({
    buttons: [...defaultPhaseButtons]
});

// 签名卡配置
const signatureConfig = ref<Array<{ id: string; name: string; count: number }>>([]);
const showSignatureSelector = ref(false);

// 职阶映射 (通常为内部数据，无需翻译)
const classMapping: Record<string, string> = {
    '守护者': 'Guardian',
    '探求者': 'Seeker',
    '流浪者': 'Rogue',
    '潜修者': 'Mystic',
    '生存者': 'Survivor',
    '中立': 'Neutral'
};

// 卡牌类型映射 (通常为内部数据，无需翻译)
const typeMapping: Record<string, string> = {
    '调查员': 'Investigator',
    '支援卡': 'Asset',
    '事件卡': 'Event',
    '地点卡': 'Location'
};

// 扩展的卡牌类型映射 - 支持所有卡牌类型
const getCardTypeMapping = (cardType: string): string => {
    // 先检查标准映射
    if (typeMapping[cardType]) {
        return typeMapping[cardType];
    }

    // 扩展映射
    const extendedMapping: Record<string, string> = {
        '技能卡': 'Skill',
        '调查员背面': 'InvestigatorBack',
        '定制卡': 'Custom',
        '故事卡': 'Story',
        '诡计卡': 'Treachery',
        '敌人卡': 'Enemy',
        '密谋卡': 'Agenda',
        '密谋卡-大画': 'Agenda',
        '场景卡': 'Act',
        '场景卡-大画': 'Act',
        '冒险参考卡': 'AgendaReference',
        '玩家卡背': 'PlayerCardBack',
        '遭遇卡背': 'EncounterCardBack'
    };

    return extendedMapping[cardType] || 'Asset'; // 默认为Asset
};

// 地点图标中英文映射
const locationIconMapping: Record<string, string> = {
    '绿菱': 'GreenDiamond',
    '暗红漏斗': 'DarkRedCrescent',
    '橙心': 'OrangeHeart',
    '浅褐水滴': 'LightBrownDroplet',
    '深紫星': 'DeepPurpleStar',
    '深绿斜二': 'DeepGreenSquare',
    '深蓝T': 'DeepBlueHourglass',
    '紫月': 'PurpleMoon',
    '红十': 'RedCross',
    '红方': 'RedSquare',
    '蓝三角': 'BlueTriangle',
    '褐扭': 'BrownSpiral',
    '青花': 'BlueFlower',
    '黄圆': 'YellowCircle'
};

// ID验证函数 - 只允许字母数字
const allowOnlyAlphaNumeric = (value: string) => /^[A-Za-z0-9]*$/.test(value);

// --- 修改: 扩展extraToken选项 ---
const computedExtraTokenOptions = computed(() => [
    { label: t('ttsScriptEditor.options.extraToken.none'), value: 'None' },
    { label: t('ttsScriptEditor.options.extraToken.activate'), value: 'Activate' },
    { label: t('ttsScriptEditor.options.extraToken.engage'), value: 'Engage' },
    { label: t('ttsScriptEditor.options.extraToken.evade'), value: 'Evade' },
    { label: t('ttsScriptEditor.options.extraToken.explore'), value: 'Explore' },
    { label: t('ttsScriptEditor.options.extraToken.fight'), value: 'Fight' },
    { label: t('ttsScriptEditor.options.extraToken.freeTrigger'), value: 'FreeTrigger' },
    { label: t('ttsScriptEditor.options.extraToken.investigate'), value: 'Investigate' },
    { label: t('ttsScriptEditor.options.extraToken.move'), value: 'Move' },
    { label: t('ttsScriptEditor.options.extraToken.parley'), value: 'Parley' },
    { label: t('ttsScriptEditor.options.extraToken.playItem'), value: 'PlayItem' },
    { label: t('ttsScriptEditor.options.extraToken.reaction'), value: 'Reaction' },
    { label: t('ttsScriptEditor.options.extraToken.resource'), value: 'Resource' },
    { label: t('ttsScriptEditor.options.extraToken.scan'), value: 'Scan' },
    { label: t('ttsScriptEditor.options.extraToken.spell'), value: 'Spell' },
    { label: t('ttsScriptEditor.options.extraToken.tome'), value: 'Tome' },
    { label: t('ttsScriptEditor.options.extraToken.guardian'), value: 'Guardian' },
    { label: t('ttsScriptEditor.options.extraToken.mystic'), value: 'Mystic' },
    { label: t('ttsScriptEditor.options.extraToken.neutral'), value: 'Neutral' },
    { label: t('ttsScriptEditor.options.extraToken.rogue'), value: 'Rogue' },
    { label: t('ttsScriptEditor.options.extraToken.seeker'), value: 'Seeker' },
    { label: t('ttsScriptEditor.options.extraToken.survivor'), value: 'Survivor' }
]);

const computedTokenOptions = computed(() => [
    { label: t('ttsScriptEditor.options.tokenTypes.resource'), value: 'resource' },
    { label: t('ttsScriptEditor.options.tokenTypes.damage'), value: 'damage' },
    { label: t('ttsScriptEditor.options.tokenTypes.horror'), value: 'horror' },
    { label: t('ttsScriptEditor.options.tokenTypes.doom'), value: 'doom' },
    { label: t('ttsScriptEditor.options.tokenTypes.clue'), value: 'clue' }
]);

const computedResourceTypeOptions = computed(() => [
    { label: t('ttsScriptEditor.options.resourceTypes.ammo'), value: 'Ammo' },
    { label: t('ttsScriptEditor.options.resourceTypes.resource'), value: 'Resource' },
    { label: t('ttsScriptEditor.options.resourceTypes.bounty'), value: 'Bounty' },
    { label: t('ttsScriptEditor.options.resourceTypes.charge'), value: 'Charge' },
    { label: t('ttsScriptEditor.options.resourceTypes.evidence'), value: 'Evidence' },
    { label: t('ttsScriptEditor.options.resourceTypes.secret'), value: 'Secret' },
    { label: t('ttsScriptEditor.options.resourceTypes.supply'), value: 'Supply' },
    { label: t('ttsScriptEditor.options.resourceTypes.offering'), value: 'Offering' }
]);

const computedFixedTokenTypeMap = computed<Record<string, { label: string; value: string }[]>>(() => ({
    damage: [{ label: t('ttsScriptEditor.options.fixedTokenTypes.damage'), value: 'Damage' }],
    horror: [{ label: t('ttsScriptEditor.options.fixedTokenTypes.horror'), value: 'Horror' }],
    doom: [{ label: t('ttsScriptEditor.options.fixedTokenTypes.doom'), value: 'Doom' }],
    clue: [{ label: t('ttsScriptEditor.options.fixedTokenTypes.clue'), value: 'Clue' }]
}));

// 地点图标选项
const locationIconOptions = computed(() => [
    { label: '🔶 绿菱', value: '绿菱' },
    { label: '🔴 暗红漏斗', value: '暗红漏斗' },
    { label: '🧡 橙心', value: '橙心' },
    { label: '🟤 浅褐水滴', value: '浅褐水滴' },
    { label: '🟣 深紫星', value: '深紫星' },
    { label: '🟢 深绿斜二', value: '深绿斜二' },
    { label: '🔷 深蓝T', value: '深蓝T' },
    { label: '🌙 紫月', value: '紫月' },
    { label: '➕ 红十', value: '红十' },
    { label: '🟥 红方', value: '红方' },
    { label: '🔺 蓝三角', value: '蓝三角' },
    { label: '🌀 褐扭', value: '褐扭' },
    { label: '🌸 青花', value: '青花' },
    { label: '🟡 黄圆', value: '黄圆' }
]);
// ----------------------------------------------------

// 根据选择的token类型获取可用的type选项
const getUsesTypeOptions = (token: string) => {
    if (token === 'resource') {
        return computedResourceTypeOptions.value;
    }
    return computedFixedTokenTypeMap.value[token] || [];
};

// 判断是否应该显示TTS脚本组件 - 现在支持所有卡牌类型
const shouldShowTtsScript = computed(() => {
    // 支持所有卡牌类型，包括系统预设的卡背类型
    return true;
});

// 判断是否有高级配置（调查员、支援卡、事件卡、地点卡）
const hasAdvancedConfig = computed(() => {
    const advancedTypes = ['调查员', '支援卡', '事件卡', '地点卡'];
    return advancedTypes.includes(props.cardType);
});

// 获取当前编辑的数据对象（支持双面卡牌）
const getEditingCardData = () => {
    if (props.isDoubleSided && props.currentSide === 'back') {
        return props.cardData.back || props.cardData;
    }
    return props.cardData;
};

// 生成GMNotes
const generatedGMNotes = computed(() => {
    const cardType = props.cardType;
    if (!shouldShowTtsScript.value) return '';

    // 对于双面卡牌，需要判断当前面的类型
    const currentEditingData = getEditingCardData();
    const currentCardType = currentEditingData.type || cardType;

    // 基础数据 - 所有卡牌类型都包含这些字段
    const baseData = {
        id: scriptConfig.value.id || generateUUID(),
        type: typeMapping[currentCardType] || getCardTypeMapping(currentCardType),
        // 添加其他可能的字段
        ...(currentEditingData.name && { name: currentEditingData.name }),
        ...(currentEditingData.traits && Array.isArray(currentEditingData.traits) && currentEditingData.traits.length > 0 && {
            traits: currentEditingData.traits.join('.') + '.'
        }),
        ...(currentEditingData.class && { class: classMapping[currentEditingData.class] || currentEditingData.class }),
        ...(currentEditingData.level != null && { level: currentEditingData.level }),
        ...(currentEditingData.cost != null && { cost: currentEditingData.cost }),
        ...(currentEditingData.victory != null && { victory: currentEditingData.victory })
    };

    let gmNotesData: any;

    // 对于有高级配置的卡牌类型，使用原来的逻辑
    if (hasAdvancedConfig.value) {
        switch (cardType) {
            case '调查员':
                gmNotesData = {
                    ...baseData,
                    type: 'Investigator',
                    willpowerIcons: investigatorConfig.value.willpowerIcons,
                    intellectIcons: investigatorConfig.value.intellectIcons,
                    combatIcons: investigatorConfig.value.combatIcons,
                    agilityIcons: investigatorConfig.value.agilityIcons,
                    extraToken: investigatorConfig.value.extraToken
                };

                // 添加签名卡配置
                if (signatureConfig.value.length > 0) {
                    const signatures: Record<string, number>[] = [{}];
                    for (const signature of signatureConfig.value) {
                        // 如果同一张卡牌出现多次，累加数量
                        if (signatures[0][signature.id]) {
                            signatures[0][signature.id] += signature.count;
                        } else {
                            signatures[0][signature.id] = signature.count;
                        }
                    }
                    gmNotesData.signatures = signatures;
                }
                break;

            case '支援卡':
            case '事件卡':
                gmNotesData = {
                    ...baseData,
                    ...(props.cardData.slot && { slot: props.cardData.slot }),
                    ...(props.cardData.willpowerIcons && { willpowerIcons: props.cardData.willpowerIcons }),
                    ...(props.cardData.intellectIcons && { intellectIcons: props.cardData.intellectIcons }),
                    ...(props.cardData.combatIcons && { combatIcons: props.cardData.combatIcons }),
                    ...(props.cardData.agilityIcons && { agilityIcons: props.cardData.agilityIcons }),
                    ...(assetConfig.value.uses.length > 0 && { uses: assetConfig.value.uses })
                };
                break;

            case '地点卡':
                const locationData: any = {
                    icons: locationIconMapping[currentEditingData.location_icon] || currentEditingData.location_icon || 'Diamond',
                    connections: (currentEditingData.location_link || []).map(conn => locationIconMapping[conn] || conn).join('|'),
                    ...(currentEditingData.victory != null && { victory: currentEditingData.victory })
                };

                // 只有当地点类型为"已揭示"时才添加uses字段
                if (currentEditingData.location_type === '已揭示') {
                    locationData.uses = [{
                        ...(isPerInvestigator.value ? { countPerInvestigator: clueCount.value } : { count: clueCount.value }),
                        type: 'Clue',
                        token: 'clue'
                    }];
                }

                // 双面卡牌特殊处理：根据正背面存储到不同字段
                if (props.isDoubleSided) {
                    gmNotesData = {
                        id: scriptConfig.value.id || generateUUID(),
                        type: 'Location',
                        traits: (currentEditingData.traits || []).join('.') + (currentEditingData.traits?.length ? '.' : ''),
                    };

                    // 根据当前编辑的面决定存储字段
                    if (props.currentSide === 'back') {
                        // 背面是地点卡，直接存储到locationBack
                        gmNotesData.locationBack = locationData;

                        // 如果正面也是地点卡，需要从原始数据中获取locationFront
                        if (props.cardData.type === '地点卡') {
                            const frontLocationData: any = {
                                icons: locationIconMapping[props.cardData.location_icon] || props.cardData.location_icon || 'Diamond',
                                connections: (props.cardData.location_link || []).map(conn => locationIconMapping[conn] || conn).join('|'),
                                ...(props.cardData.victory != null && { victory: props.cardData.victory })
                            };

                            if (props.cardData.location_type === '已揭示') {
                                frontLocationData.uses = [{
                                    ...(isPerInvestigator.value ? { countPerInvestigator: clueCount.value } : { count: clueCount.value }),
                                    type: 'Clue',
                                    token: 'clue'
                                }];
                            }

                            gmNotesData.locationFront = frontLocationData;
                        }
                    } else {
                        // 正面是地点卡，存储到locationFront
                        gmNotesData.locationFront = locationData;

                        // 如果背面也是地点卡，需要从back数据中获取locationBack
                        if (props.cardData.back && props.cardData.back.type === '地点卡') {
                            const backLocationData: any = {
                                icons: locationIconMapping[props.cardData.back.location_icon] || props.cardData.back.location_icon || 'Diamond',
                                connections: (props.cardData.back.location_link || []).map(conn => locationIconMapping[conn] || conn).join('|'),
                                ...(props.cardData.back.victory != null && { victory: props.cardData.back.victory })
                            };

                            if (props.cardData.back.location_type === '已揭示') {
                                backLocationData.uses = [{
                                    ...(isPerInvestigator.value ? { countPerInvestigator: clueCount.value } : { count: clueCount.value }),
                                    type: 'Clue',
                                    token: 'clue'
                                }];
                            }

                            gmNotesData.locationBack = backLocationData;
                        }
                    }
                } else {
                    // 单面卡牌，使用原来的location字段
                    gmNotesData = {
                        id: scriptConfig.value.id || generateUUID(),
                        type: 'Location',
                        traits: (currentEditingData.traits || []).join('.') + (currentEditingData.traits?.length ? '.' : ''),
                        location: locationData
                    };
                }
                break;

            default:
                // 对于不支持高级配置的卡牌类型，使用基础数据
                gmNotesData = baseData;
                break;
        }
    } else {
        // 不支持高级配置的卡牌类型，直接使用基础数据
        gmNotesData = baseData;
    }

    try {
        return JSON.stringify(gmNotesData, null, 2);
    } catch (error) {
        return '// JSON generation failed';
    }
});


// 生成完整的Lua脚本
const generatedLuaScript = computed(() => {
    if (props.cardType !== '调查员' || !enablePhaseButtons.value) return '';
    return generatePhaseButtonScript(phaseButtonConfig.value);
});

// TTS脚本数据（包含配置）
const ttsScriptData = computed((): TtsScriptData => ({
    GMNotes: generatedGMNotes.value,
    LuaScript: generatedLuaScript.value,
    config: {
        enablePhaseButtons: enablePhaseButtons.value,
        phaseButtonConfig: phaseButtonConfig.value,
        investigatorConfig: investigatorConfig.value,
        assetConfig: assetConfig.value,
        locationConfig: locationConfig.value,
        scriptConfig: scriptConfig.value,
        signatureConfig: signatureConfig.value
    }
}));

// 生成UUID
const generateUUID = (): string => {
    return uuidv4().replace(/-/g, '').substring(0, 8).toUpperCase();
};

// 生成随机ID
const generateRandomId = () => {
    scriptConfig.value.id = generateUUID();
    onScriptConfigChange();
};

// 添加Uses配置
const addUse = () => {
    assetConfig.value.uses.push({
        count: 2,
        type: 'Resource',
        token: 'resource'
    });
    onScriptConfigChange();
};

// 删除Uses配置
const removeUse = (index: number) => {
    assetConfig.value.uses.splice(index, 1);
    onScriptConfigChange();
};

// 令牌类型变化时自动更新type
const onTokenChange = (index: number, token: string) => {
    const use = assetConfig.value.uses[index];
    if (use) {
        use.token = token;
        const typeOptions = getUsesTypeOptions(token);
        if (typeOptions.length > 0) {
            use.type = typeOptions[0].value;
        }
        onScriptConfigChange();
    }
};

// 添加阶段按钮
const addPhaseButton = () => {
    phaseButtonConfig.value.buttons.push({
        id: `Button${phaseButtonConfig.value.buttons.length + 1}`,
        label: 'w',
        color: '#ffffff'
    });
    onPhaseButtonConfigChange();
};

// 删除阶段按钮
const removePhaseButton = (index: number) => {
    phaseButtonConfig.value.buttons.splice(index, 1);
    onPhaseButtonConfigChange();
};

// 添加线索值配置
const addClueUse = () => {
    locationConfig.value.locationBack.uses.push({
        count: 1,
        type: 'Clue',
        token: 'clue',
        isPerInvestigator: false
    });
    onScriptConfigChange();
};

// 删除线索值配置
const removeClueUse = (index: number) => {
    locationConfig.value.locationBack.uses.splice(index, 1);
    onScriptConfigChange();
};

// 解析clues字段
const parseCluesField = (clues: string) => {
    if (!clues) {
        clueCount.value = 1;
        isPerInvestigator.value = false;
        return;
    }
    
    // 匹配格式如 "1<调查员>" 或 "4"
    const match = clues.match(/^(\d+)(<调查员>)?$/);
    if (match) {
        const count = parseInt(match[1], 10);
        const hasInvestigatorTag = match[2] === '<调查员>';
        
        clueCount.value = count;
        isPerInvestigator.value = hasInvestigatorTag;
    } else {
        // 默认值
        clueCount.value = 1;
        isPerInvestigator.value = false;
    }
};

// 线索值数量变化处理
const onClueCountChange = () => {
    onScriptConfigChange();
};

// 线索值类型变化处理
const onClueTypeChange = () => {
    onScriptConfigChange();
};

// 脚本配置变化处理
const onScriptConfigChange = () => {
    nextTick(() => {
        emit('update-tts-script', ttsScriptData.value);
    });
};

// 阶段按钮配置变化处理
const onPhaseButtonConfigChange = () => {
    nextTick(() => {
        emit('update-tts-script', ttsScriptData.value);
    });
};

// 阶段按钮开关变化处理
const onPhaseButtonToggle = () => {
    nextTick(() => {
        emit('update-tts-script', ttsScriptData.value);
    });
};

// 复制GMNotes
const copyGMNotes = async () => {
    try {
        await navigator.clipboard.writeText(generatedGMNotes.value);
        // --- 修改: 使用本地化消息 ---
        message.success(t('ttsScriptEditor.messages.copySuccess'));
    } catch (error) {
        message.error(t('ttsScriptEditor.messages.copyError'));
    }
};

// 重新生成GMNotes
const regenerateGMNotes = () => {
    onScriptConfigChange();
    // --- 修改: 使用本地化消息 ---
    message.success(t('ttsScriptEditor.messages.regenerateSuccess'));
};

// 签名卡相关方法
// 签名卡选择回调
const onSignatureCardsSelected = async (selectedItems: any[]) => {
    console.log('📝 选中的签名卡:', selectedItems);

    try {
        // 处理选中的卡牌文件 - 每张卡牌都单独添加
        for (const item of selectedItems) {
            // 只有卡牌类型才处理
            if (item.type === 'card') {
                // 尝试从卡牌文件中读取ID，如果失败则使用文件名
                let cardId = item.name; // 默认使用文件名
                let cardName = item.name; // 默认使用文件名作为显示名称

                try {
                    // 读取卡牌文件内容以获取真实的ID
                    const fileContent = await WorkspaceService.getFileContent(item.fullPath);
                    const cardData = JSON.parse(fileContent);

                    // 优先使用卡牌名称
                    if (cardData.name) {
                        cardName = cardData.name;
                    }

                    // 从TTS脚本的GMNotes中解析ID
                    if (cardData.tts_script?.GMNotes) {
                        try {
                            const gmNotesData = JSON.parse(cardData.tts_script.GMNotes);
                            if (gmNotesData.id) {
                                cardId = gmNotesData.id;
                                console.log('📖 从GMNotes解析卡牌ID成功:', { path: item.fullPath, id: cardId, name: cardName });
                            }
                        } catch (gmNotesError) {
                            console.warn('解析GMNotes失败，尝试使用根级ID:', gmNotesError);
                            // 如果GMNotes解析失败，尝试使用根级ID
                            if (cardData.id) {
                                cardId = cardData.id;
                            }
                        }
                    } else if (cardData.id) {
                        // 如果没有GMNotes，使用根级ID
                        cardId = cardData.id;
                    }

                    console.log('📖 读取卡牌文件成功:', { path: item.fullPath, id: cardId, name: cardName });
                } catch (error) {
                    console.warn('无法读取卡牌文件内容，使用文件名:', error);
                }

                // 为每张选中的卡牌创建独立的条目
                signatureConfig.value.push({
                    id: cardId,
                    name: cardName,
                    count: 1
                });
            }
        }

        console.log('✅ 签名卡配置已更新:', signatureConfig.value);
        showSignatureSelector.value = false;
        onScriptConfigChange();
        message.success(`已添加 ${selectedItems.filter(item => item.type === 'card').length} 张签名卡`);
    } catch (error) {
        console.error('❌ 处理签名卡时出错:', error);
        message.error('处理签名卡时出错，请重试');
    }
};

// 签名卡数量变化处理
const onSignatureCountChange = () => {
    onScriptConfigChange();
};

// 删除签名卡
const removeSignature = (index: number) => {
    signatureConfig.value.splice(index, 1);
    onScriptConfigChange();
};


// --- 以下部分逻辑不变 ---

// 从卡牌数据同步属性
const syncAttributesFromCardData = () => {
    const currentEditingData = getEditingCardData();

    if (props.cardType === '调查员' && currentEditingData.attribute) {
        const attributes = currentEditingData.attribute;
        if (Array.isArray(attributes) && attributes.length >= 4) {
            investigatorConfig.value.willpowerIcons = attributes[0] || 3;
            investigatorConfig.value.intellectIcons = attributes[1] || 3;
            investigatorConfig.value.combatIcons = attributes[2] || 2;
            investigatorConfig.value.agilityIcons = attributes[3] || 2;
        }
    }
    if ((props.cardType === '支援卡' || props.cardType === '事件卡') && currentEditingData.uses) {
        assetConfig.value.uses = [...currentEditingData.uses];
    }
    if (props.cardType === '地点卡') {
        // 解析clues字段
        parseCluesField(currentEditingData.clues);
    }
};

// 从保存的配置中加载数据
const loadFromSavedConfig = (savedConfig: any) => {
    console.log('🔧 加载保存的TTS配置:', savedConfig);
    if (savedConfig?.scriptConfig) {
        scriptConfig.value = { ...savedConfig.scriptConfig };
        console.log('✅ 脚本配置已加载');
    }
    if (savedConfig?.investigatorConfig) {
        investigatorConfig.value = { ...savedConfig.investigatorConfig };
        console.log('✅ 调查员配置已加载');
    }
    if (savedConfig?.assetConfig) {
        assetConfig.value = { ...savedConfig.assetConfig };
        console.log('✅ 支援卡/事件卡配置已加载');
    }
    if (savedConfig?.locationConfig) {
        locationConfig.value = { ...savedConfig.locationConfig };
        console.log('✅ 地点卡配置已加载');
    }
    if (savedConfig?.enablePhaseButtons !== undefined) {
        enablePhaseButtons.value = savedConfig.enablePhaseButtons;
        console.log('✅ 阶段按钮开关状态已加载:', enablePhaseButtons.value);
    }
    if (savedConfig?.phaseButtonConfig) {
        phaseButtonConfig.value = savedConfig.phaseButtonConfig;
        console.log('✅ 阶段按钮配置已加载:', phaseButtonConfig.value.buttons.length, '个按钮');
    }
    if (savedConfig?.signatureConfig) {
        signatureConfig.value = [...savedConfig.signatureConfig];
        console.log('✅ 签名卡配置已加载:', signatureConfig.value.length, '张签名卡');
    }
};

// 从旧数据格式兼容加载
const loadFromLegacyFormat = (ttsScript: any) => {
    console.log('🔄 使用兼容模式加载TTS数据');
    if (ttsScript?.GMNotes) {
        try {
            const parsed = JSON.parse(ttsScript.GMNotes);
            if (parsed.id) {
                scriptConfig.value.id = parsed.id;
            }
            if (props.cardType === '调查员') {
                investigatorConfig.value = {
                    extraToken: parsed.extraToken || 'None',
                    willpowerIcons: parsed.willpowerIcons || 3,
                    intellectIcons: parsed.intellectIcons || 3,
                    combatIcons: parsed.combatIcons || 2,
                    agilityIcons: parsed.agilityIcons || 2
                };
            }
            if ((props.cardType === '支援卡' || props.cardType === '事件卡') && parsed.uses) {
                assetConfig.value.uses = parsed.uses;
            }
            if (props.cardType === '地点卡') {
                // 加载地点卡配置
                if (parsed.locationFront) {
                    locationConfig.value.locationFront = {
                        icons: parsed.locationFront.icons || 'Diamond',
                        connections: parsed.locationFront.connections ? parsed.locationFront.connections.split('|') : []
                    };
                }
                if (parsed.locationBack) {
                    locationConfig.value.locationBack = {
                        icons: parsed.locationBack.icons || 'Diamond',
                        connections: parsed.locationBack.connections ? parsed.locationBack.connections.split('|') : [],
                        uses: parsed.locationBack.uses ? parsed.locationBack.uses.map((use: any) => ({
                            count: use.count || use.countPerInvestigator || 1,
                            type: use.type || 'Clue',
                            token: use.token || 'clue',
                            isPerInvestigator: !!use.countPerInvestigator
                        })) : []
                    };
                }
            }
            console.log('✅ 从GMNotes解析配置成功');
        } catch (error) {
            console.warn('⚠️ 解析GMNotes失败:', error);
        }
    }
    if (ttsScript?.LuaScript && props.cardType === '调查员') {
        enablePhaseButtons.value = true;
        const parsedConfig = parsePhaseButtonConfig(ttsScript.LuaScript);
        if (parsedConfig) {
            phaseButtonConfig.value = parsedConfig;
            console.log('✅ 从LuaScript解析阶段按钮配置成功');
        } else {
            console.log('⚠️ 无法解析LuaScript，使用默认配置');
        }
    } else {
        enablePhaseButtons.value = false;
        console.log('🔧 没有LuaScript，禁用阶段按钮');
    }
};

// 监听卡牌数据变化
watch(
    () => props.cardData,
    () => {
        if (shouldShowTtsScript.value) {
            syncAttributesFromCardData();
        }
    },
    { deep: true }
);

// 监听TTS脚本数据变化，加载配置
watch(
    () => props.cardData.tts_script,
    (newTtsScript) => {
        console.log('📥 TTS脚本数据变化:', newTtsScript);
        if (!newTtsScript) {
            console.log('🧹 没有TTS脚本数据，初始化默认配置');
            // 当没有TTS脚本数据时，初始化脚本ID
            if (!scriptConfig.value.id) {
                scriptConfig.value.id = generateUUID();
                console.log('✅ 生成默认脚本ID:', scriptConfig.value.id);
            }
            return;
        }
        if (newTtsScript.config) {
            loadFromSavedConfig(newTtsScript.config);
        } else {
            loadFromLegacyFormat(newTtsScript);
        }
        nextTick(() => {
            onScriptConfigChange();
        });
    },
    { immediate: true }
);

// 初始化
if (shouldShowTtsScript.value) {
    nextTick(() => {
        syncAttributesFromCardData();
        // 确保脚本ID有默认值
        if (!scriptConfig.value.id) {
            scriptConfig.value.id = generateUUID();
            console.log('✅ 初始化时生成默认脚本ID:', scriptConfig.value.id);
        }
        onScriptConfigChange();
    });
}
</script>

<style scoped>
/* 样式部分 */
.tts-card {
    background: linear-gradient(135deg, rgba(74, 144, 226, 0.05) 0%, rgba(80, 200, 120, 0.05) 100%);
    border: 2px solid rgba(74, 144, 226, 0.2);
}

.attribute-input {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.attribute-input :deep(.n-input-number) {
    width: 80px;
}

.uses-input-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.uses-input-group :deep(.n-input-number) {
    width: 80px;
}

.uses-config-row {
    background: rgba(255, 255, 255, 0.7);
    padding: 12px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.gmnotes-preview {
    position: relative;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    overflow: hidden;
}

.preview-code {
    max-height: 200px;
    overflow-y: auto;
    padding-right: 140px;
    padding-top: 50px;
    padding-bottom: 16px;
    padding-left: 16px;
}

.preview-actions {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 6px;
    padding: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 10;
    backdrop-filter: blur(4px);
    min-width: 120px;
}

.phase-buttons-config {
    padding: 16px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    margin-top: 8px;
}

.button-config-row {
    background: rgba(255, 255, 255, 0.7);
    padding: 12px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.color-option-display {
    display: flex;
    align-items: center;
}

/* 签名卡相关样式 */
.signature-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 200px;
    overflow-y: auto;
}

.signature-item {
    background: rgba(255, 255, 255, 0.7);
    padding: 12px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.signature-item:hover {
    background: rgba(255, 255, 255, 0.9);
}

.signature-selector-header {
    font-size: 16px;
    font-weight: 500;
}

.signature-selector-content {
    min-height: 400px;
}

@media (max-width: 768px) {
    .preview-code {
        padding-right: 16px;
        padding-top: 16px;
        padding-bottom: 60px;
    }

    .preview-actions {
        position: absolute;
        bottom: 8px;
        right: 8px;
        top: auto;
        background: rgba(245, 245, 245, 0.95);
        box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(4px);
        min-width: auto;
    }

    .attribute-input :deep(.n-input-number) {
        width: 60px;
    }

    .uses-input-group :deep(.n-input-number) {
        width: 60px;
    }

    .button-config-row :deep(.n-space),
    .uses-config-row :deep(.n-space) {
        flex-wrap: wrap;
    }
}
</style>

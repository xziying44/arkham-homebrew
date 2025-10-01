<template>
    <n-card v-if="shouldShowTtsScript" :title="$t('ttsScriptEditor.title')" size="small" class="form-card tts-card">
        <n-space vertical size="medium">
            <!-- ID配置 -->
            <n-form-item :label="$t('ttsScriptEditor.scriptId.label')">
                <n-space align="center">
                    <n-input v-model:value="scriptConfig.id" :placeholder="$t('ttsScriptEditor.scriptId.placeholder')"
                        :allow-input="allowOnlyAlphaNumeric" style="flex: 1" @update:value="onScriptConfigChange" />
                    <n-button @click="generateRandomId" size="small" type="primary">
                        {{ $t('ttsScriptEditor.scriptId.button') }}
                    </n-button>
                </n-space>
            </n-form-item>


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
        </n-space>
    </n-card>
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

// --- 新增: i18n设置 ---
const { t } = useI18n();
// -----------------------

interface Props {
    cardData: Record<string, any>;
    cardType: string;
}

interface TtsScriptData {
    GMNotes: string;
    LuaScript: string;
    config?: {
        enablePhaseButtons: boolean;
        phaseButtonConfig: PhaseButtonConfig;
        investigatorConfig: InvestigatorConfig;
        assetConfig: AssetConfig;
        scriptConfig: ScriptConfig;
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

const props = defineProps<Props>();
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

// 每阶段按钮配置开关
const enablePhaseButtons = ref(false);

// 每阶段按钮配置
const phaseButtonConfig = ref<PhaseButtonConfig>({
    buttons: [...defaultPhaseButtons]
});

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
    '事件卡': 'Event'
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
// ----------------------------------------------------

// 根据选择的token类型获取可用的type选项
const getUsesTypeOptions = (token: string) => {
    if (token === 'resource') {
        return computedResourceTypeOptions.value;
    }
    return computedFixedTokenTypeMap.value[token] || [];
};

// 判断是否应该显示TTS脚本组件
const shouldShowTtsScript = computed(() => {
    const supportedTypes = ['调查员', '支援卡', '事件卡'];
    return supportedTypes.includes(props.cardType);
});

// 生成GMNotes
const generatedGMNotes = computed(() => {
    const cardType = props.cardType;
    if (!shouldShowTtsScript.value) return '';

    const baseData = {
        id: scriptConfig.value.id || generateUUID(),
        type: typeMapping[cardType] || 'Asset',
        class: classMapping[props.cardData.class || '中立'] || 'Neutral',
        level: props.cardData.level || 0,
        traits: (props.cardData.traits || []).join('.') + (props.cardData.traits?.length ? '.' : ''),
        cost: props.cardData.cost || 0,
        // 添加victory字段检测
        ...(props.cardData.victory != null && { victory: props.cardData.victory })
    };

    let gmNotesData: any;

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

        default:
            return '';
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
        scriptConfig: scriptConfig.value
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


// --- 以下部分逻辑不变 ---

// 从卡牌数据同步属性
const syncAttributesFromCardData = () => {
    if (props.cardType === '调查员' && props.cardData.attribute) {
        const attributes = props.cardData.attribute;
        if (Array.isArray(attributes) && attributes.length >= 4) {
            investigatorConfig.value.willpowerIcons = attributes[0] || 3;
            investigatorConfig.value.intellectIcons = attributes[1] || 3;
            investigatorConfig.value.combatIcons = attributes[2] || 2;
            investigatorConfig.value.agilityIcons = attributes[3] || 2;
        }
    }
    if ((props.cardType === '支援卡' || props.cardType === '事件卡') && props.cardData.uses) {
        assetConfig.value.uses = [...props.cardData.uses];
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
    if (savedConfig?.enablePhaseButtons !== undefined) {
        enablePhaseButtons.value = savedConfig.enablePhaseButtons;
        console.log('✅ 阶段按钮开关状态已加载:', enablePhaseButtons.value);
    }
    if (savedConfig?.phaseButtonConfig) {
        phaseButtonConfig.value = savedConfig.phaseButtonConfig;
        console.log('✅ 阶段按钮配置已加载:', phaseButtonConfig.value.buttons.length, '个按钮');
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
/* 样式部分保持不变 */
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

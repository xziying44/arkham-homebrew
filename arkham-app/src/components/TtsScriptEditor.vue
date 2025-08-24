<template>
    <n-card v-if="shouldShowTtsScript" title="📢 TTS脚本" size="small" class="form-card tts-card">
        <n-space vertical size="medium">
            <!-- ID配置 -->
            <n-form-item label="🔖 脚本ID">
                <n-space align="center">
                    <n-input v-model:value="scriptConfig.id" placeholder="输入自定义ID或使用随机生成" style="flex: 1"
                        @update:value="onScriptConfigChange" />
                    <n-button @click="generateRandomId" size="small" type="primary">
                        🎲 随机
                    </n-button>
                </n-space>
            </n-form-item>

            <!-- 调查员专用配置 -->
            <template v-if="props.cardType === '调查员'">
                <!-- 额外标记类型 -->
                <n-form-item label="🏷️ 额外标记（每轮一次）">
                    <n-select v-model:value="investigatorConfig.extraToken" :options="extraTokenOptions"
                        placeholder="选择额外标记类型" @update:value="onScriptConfigChange" />
                </n-form-item>

                <!-- 四维属性 -->
                <n-form-item label="🎯 能力值">
                    <n-space>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">🧠 意志</n-text>
                            <n-input-number v-model:value="investigatorConfig.willpowerIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onScriptConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">📚 智力</n-text>
                            <n-input-number v-model:value="investigatorConfig.intellectIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onScriptConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">⚔️ 战力</n-text>
                            <n-input-number v-model:value="investigatorConfig.combatIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onScriptConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">⚡ 敏捷</n-text>
                            <n-input-number v-model:value="investigatorConfig.agilityIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onScriptConfigChange" />
                        </div>
                    </n-space>
                </n-form-item>

                <!-- 每阶段脚本配置开关 -->
                <n-form-item label="🎮 每阶段按钮配置">
                    <n-space vertical size="small">
                        <n-switch v-model:value="enablePhaseButtons" @update:value="onPhaseButtonToggle">
                            <template #checked>启用</template>
                            <template #unchecked>禁用</template>
                        </n-switch>

                        <!-- 每阶段脚本配置 -->
                        <div v-show="enablePhaseButtons" class="phase-buttons-config">
                            <n-space vertical size="small">
                                <!-- 按钮列表 -->
                                <div v-for="(button, index) in phaseButtonConfig.buttons" :key="index"
                                    class="button-config-row">
                                    <n-space align="center">
                                        <n-input v-model:value="button.id" placeholder="按钮ID" style="width: 120px"
                                            @update:value="onPhaseButtonConfigChange" />
                                        <n-select v-model:value="button.label" :options="buttonLabelOptions"
                                            placeholder="选择标签" style="width: 140px"
                                            @update:value="onPhaseButtonConfigChange" />
                                        <n-select v-model:value="button.color" :options="colorOptions" placeholder="选择颜色"
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
                                        <n-button @click="removePhaseButton(index)" size="small" type="error" quaternary>
                                            🗑️ 删除
                                        </n-button>
                                    </n-space>
                                </div>

                                <!-- 添加按钮 -->
                                <n-button @click="addPhaseButton" size="small" type="primary" dashed>
                                    ➕ 添加按钮
                                </n-button>
                            </n-space>
                        </div>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 支援卡/事件卡专用配置 -->
            <template v-if="props.cardType === '支援卡' || props.cardType === '事件卡'">
                <!-- Uses配置 -->
                <n-form-item label="🎯 入场标记配置">
                    <n-space vertical size="medium">
                        <!-- Uses列表 -->
                        <div v-for="(use, index) in assetConfig.uses" :key="index" class="uses-config-row">
                            <n-space align="center">
                                <div class="uses-input-group">
                                    <n-text depth="3" style="font-size: 12px;">数量</n-text>
                                    <n-input-number v-model:value="use.count" :min="0" :max="20" :step="1"
                                        size="small" @update:value="onScriptConfigChange" />
                                </div>
                                <div class="uses-input-group">
                                    <n-text depth="3" style="font-size: 12px;">令牌</n-text>
                                    <n-select v-model:value="use.token" :options="tokenOptions"
                                        placeholder="选择令牌类型" style="width: 120px"
                                        @update:value="(value) => onTokenChange(index, value)" />
                                </div>
                                <div class="uses-input-group">
                                    <n-text depth="3" style="font-size: 12px;">类型</n-text>
                                    <n-select v-model:value="use.type" :options="getUsesTypeOptions(use.token)"
                                        placeholder="选择标记类型" style="width: 120px"
                                        @update:value="onScriptConfigChange" />
                                </div>
                                <n-button @click="removeUse(index)" size="small" type="error" quaternary>
                                    🗑️ 删除
                                </n-button>
                            </n-space>
                        </div>

                        <!-- 添加Uses -->
                        <n-button @click="addUse" size="small" type="primary" dashed>
                            ➕ 添加标记配置
                        </n-button>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 预览GMNotes -->
            <n-form-item label="📋 GMNotes预览">
                <div class="gmnotes-preview">
                    <n-code :code="generatedGMNotes" language="json" :word-wrap="true" class="preview-code" />
                    <div class="preview-actions">
                        <n-space size="small">
                            <n-button size="tiny" @click="copyGMNotes" title="复制到剪贴板">
                                📋 复制
                            </n-button>
                            <n-button size="tiny" @click="regenerateGMNotes" title="重新生成">
                                🔄 刷新
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

interface Props {
    cardData: Record<string, any>;
    cardType: string;
}

interface TtsScriptData {
    GMNotes: string;
    LuaScript: string;
    // 新增：保存配置项
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

// 职阶映射
const classMapping: Record<string, string> = {
    '守护者': 'Guardian',
    '探求者': 'Seeker',
    '流浪者': 'Rogue',
    '潜修者': 'Mystic',
    '生存者': 'Survivor',
    '中立': 'Neutral'
};

// 卡牌类型映射
const typeMapping: Record<string, string> = {
    '调查员': 'Investigator',
    '支援卡': 'Asset',
    '事件卡': 'Event'
};

// 额外标记选项
const extraTokenOptions = [
    { label: '🚫 无标记', value: 'None' },
    { label: '⭕ 反应', value: 'Reaction' },
    { label: '⚡ 免费', value: 'FreeTrigger' }
];

// 令牌类型选项
const tokenOptions = [
    { label: '📋 资源', value: 'resource' },
    { label: '🔥 伤害', value: 'damage' },
    { label: '👻 恐惧', value: 'horror' },
    { label: '💀 毁灭', value: 'doom' },
    { label: '🔍 线索', value: 'clue' }
];

// Resource令牌的type选项
const resourceTypeOptions = [
    { label: '🔫 弹药', value: 'Ammo' },
    { label: '💰 资源', value: 'Resource' },
    { label: '🎯 赏金', value: 'Bounty' },
    { label: '⚡ 充能', value: 'Charge' },
    { label: '🔍 证据', value: 'Evidence' },
    { label: '🤫 秘密', value: 'Secret' },
    { label: '📦 补给', value: 'Supply' },
    { label: '🕯️ 贡品', value: 'Offering' }
];

// 固定令牌的type选项
const fixedTokenTypeMap: Record<string, { label: string; value: string }[]> = {
    damage: [{ label: '🔥 伤害', value: 'Damage' }],
    horror: [{ label: '👻 恐怖', value: 'Horror' }],
    doom: [{ label: '💀 厄运', value: 'Doom' }],
    clue: [{ label: '🔍 线索', value: 'Clue' }]
};

// 根据选择的token类型获取可用的type选项
const getUsesTypeOptions = (token: string) => {
    if (token === 'resource') {
        return resourceTypeOptions;
    }
    return fixedTokenTypeMap[token] || [];
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
        cost: props.cardData.cost || 0
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
        return '// JSON生成失败';
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
        
        // 根据token类型自动设置对应的type
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
        message.success('GMNotes已复制到剪贴板');
    } catch (error) {
        message.error('复制失败，请手动复制');
    }
};

// 重新生成GMNotes
const regenerateGMNotes = () => {
    // 触发重新计算
    onScriptConfigChange();
    message.success('GMNotes已重新生成');
};

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
    
    // 同步Uses数据（支援卡/事件卡）
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
    
    // 尝试从GMNotes解析配置
    if (ttsScript?.GMNotes) {
        try {
            const parsed = JSON.parse(ttsScript.GMNotes);
            
            // 加载通用ID
            if (parsed.id) {
                scriptConfig.value.id = parsed.id;
            }
            
            // 加载调查员配置
            if (props.cardType === '调查员') {
                investigatorConfig.value = {
                    extraToken: parsed.extraToken || 'None',
                    willpowerIcons: parsed.willpowerIcons || 3,
                    intellectIcons: parsed.intellectIcons || 3,
                    combatIcons: parsed.combatIcons || 2,
                    agilityIcons: parsed.agilityIcons || 2
                };
            }
            
            // 加载支援卡/事件卡配置
            if ((props.cardType === '支援卡' || props.cardType === '事件卡') && parsed.uses) {
                assetConfig.value.uses = parsed.uses;
            }
            
            console.log('✅ 从GMNotes解析配置成功');
        } catch (error) {
            console.warn('⚠️ 解析GMNotes失败:', error);
        }
    }

    // 如果存在LuaScript，启用阶段按钮并尝试解析配置
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
            console.log('🧹 没有TTS脚本数据，使用默认配置');
            return;
        }

        // 优先使用新格式的配置数据
        if (newTtsScript.config) {
            loadFromSavedConfig(newTtsScript.config);
        } else {
            // 兼容旧格式
            loadFromLegacyFormat(newTtsScript);
        }
        
        // 触发一次配置更新以确保数据同步
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
        onScriptConfigChange();
    });
}
</script>

<style scoped>
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
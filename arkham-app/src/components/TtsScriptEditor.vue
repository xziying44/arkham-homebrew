<template>
    <n-card v-if="shouldShowTtsScript" title="📢 TTS脚本" size="small" class="form-card tts-card">
        <n-space vertical size="medium">
            <!-- ID配置 -->
            <n-form-item label="🔖 脚本ID">
                <n-space align="center">
                    <n-input v-model:value="cardConfig.id" placeholder="输入自定义ID或使用随机生成" style="flex: 1"
                        @update:value="onCardConfigChange" />
                    <n-button @click="generateRandomId" size="small" type="primary">
                        🎲 随机
                    </n-button>
                </n-space>
            </n-form-item>

            <!-- 调查员专用配置 -->
            <template v-if="cardType === '调查员'">
                <!-- 额外标记类型 -->
                <n-form-item label="🏷️ 额外标记（每轮一次）">
                    <n-select v-model:value="investigatorConfig.extraToken" :options="extraTokenOptions"
                        placeholder="选择额外标记类型" @update:value="onCardConfigChange" />
                </n-form-item>

                <!-- 四维属性 -->
                <n-form-item label="🎯 能力值">
                    <n-space>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">🧠 意志</n-text>
                            <n-input-number v-model:value="investigatorConfig.willpowerIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onCardConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">📚 智力</n-text>
                            <n-input-number v-model:value="investigatorConfig.intellectIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onCardConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">⚔️ 战力</n-text>
                            <n-input-number v-model:value="investigatorConfig.combatIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onCardConfigChange" />
                        </div>
                        <div class="attribute-input">
                            <n-text depth="3" style="font-size: 12px;">⚡ 敏捷</n-text>
                            <n-input-number v-model:value="investigatorConfig.agilityIcons" :min="0" :max="9" :step="1"
                                size="small" @update:value="onCardConfigChange" />
                        </div>
                    </n-space>
                </n-form-item>
            </template>

            <!-- 支援卡/事件卡专用配置 -->
            <template v-if="cardType === '支援' || cardType === '事件'">
                <!-- 基本属性 -->
                <n-form-item label="📊 卡片属性">
                    <n-space vertical size="small">
                        <n-space align="center">
                            <n-text depth="3">💰 费用:</n-text>
                            <n-input-number v-model:value="assetConfig.cost" :min="0" :max="99" :step="1"
                                size="small" style="width: 80px" @update:value="onCardConfigChange" />
                            
                            <n-text depth="3">📶 等级:</n-text>
                            <n-input-number v-model:value="assetConfig.level" :min="0" :max="5" :step="1"
                                size="small" style="width: 80px" @update:value="onCardConfigChange" />
                        </n-space>
                        
                        <!-- 技能图标 -->
                        <n-space>
                            <div class="attribute-input">
                                <n-text depth="3" style="font-size: 12px;">🧠</n-text>
                                <n-input-number v-model:value="assetConfig.willpowerIcons" :min="0" :max="3" :step="1"
                                    size="small" @update:value="onCardConfigChange" />
                            </div>
                            <div class="attribute-input">
                                <n-text depth="3" style="font-size: 12px;">📚</n-text>
                                <n-input-number v-model:value="assetConfig.intellectIcons" :min="0" :max="3" :step="1"
                                    size="small" @update:value="onCardConfigChange" />
                            </div>
                            <div class="attribute-input">
                                <n-text depth="3" style="font-size: 12px;">⚔️</n-text>
                                <n-input-number v-model:value="assetConfig.combatIcons" :min="0" :max="3" :step="1"
                                    size="small" @update:value="onCardConfigChange" />
                            </div>
                            <div class="attribute-input">
                                <n-text depth="3" style="font-size: 12px;">⚡</n-text>
                                <n-input-number v-model:value="assetConfig.agilityIcons" :min="0" :max="3" :step="1"
                                    size="small" @update:value="onCardConfigChange" />
                            </div>
                            <div class="attribute-input">
                                <n-text depth="3" style="font-size: 12px;">🌟</n-text>
                                <n-input-number v-model:value="assetConfig.wildIcons" :min="0" :max="3" :step="1"
                                    size="small" @update:value="onCardConfigChange" />
                            </div>
                        </n-space>
                    </n-space>
                </n-form-item>

                <!-- Uses 配置 -->
                <n-form-item label="🎯 Uses 配置">
                    <n-space vertical size="small">
                        <n-switch v-model:value="enableUses" @update:value="onUsesToggle">
                            <template #checked>启用 Uses</template>
                            <template #unchecked>禁用 Uses</template>
                        </n-switch>

                        <div v-show="enableUses" class="uses-config">
                            <n-space vertical size="small">
                                <!-- Uses 列表 -->
                                <div v-for="(use, index) in assetConfig.uses" :key="index" class="use-config-row">
                                    <n-space align="center">
                                        <n-text depth="3">数量:</n-text>
                                        <n-input-number v-model:value="use.count" :min="1" :max="99" :step="1"
                                            size="small" style="width: 80px" @update:value="onCardConfigChange" />
                                        
                                        <n-text depth="3">类型:</n-text>
                                        <n-input v-model:value="use.type" placeholder="如: Ammo" 
                                            style="width: 100px" @update:value="onCardConfigChange" />
                                        
                                        <n-text depth="3">Token:</n-text>
                                        <n-select v-model:value="use.token" :options="tokenTypeOptions"
                                            placeholder="选择Token类型" style="width: 120px"
                                            @update:value="onCardConfigChange" />
                                        
                                        <n-button @click="removeUse(index)" size="small" type="error" quaternary>
                                            🗑️
                                        </n-button>
                                    </n-space>
                                </div>

                                <!-- 添加 Use -->
                                <n-button @click="addUse" size="small" type="primary" dashed>
                                    ➕ 添加 Use
                                </n-button>
                            </n-space>
                        </div>
                    </n-space>
                </n-form-item>
            </template>

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
    config?: {
        enablePhaseButtons: boolean;
        enableUses: boolean;
        phaseButtonConfig: PhaseButtonConfig;
        investigatorConfig: InvestigatorConfig;
        assetConfig: AssetConfig;
    };
}

interface InvestigatorConfig {
    id: string;
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
    id: string;
    cost: number;
    level: number;
    willpowerIcons: number;
    intellectIcons: number;
    combatIcons: number;
    agilityIcons: number;
    wildIcons: number;
    uses: UseConfig[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
    'update-tts-script': [data: TtsScriptData];
}>();

const message = useMessage();

// 通用卡片配置
const cardConfig = ref({
    id: ''
});

// 调查员TTS配置
const investigatorConfig = ref<InvestigatorConfig>({
    id: '',
    extraToken: 'None',
    willpowerIcons: 3,
    intellectIcons: 3,
    combatIcons: 2,
    agilityIcons: 2
});

// 支援卡/事件卡配置
const assetConfig = ref<AssetConfig>({
    id: '',
    cost: 1,
    level: 0,
    willpowerIcons: 0,
    intellectIcons: 0,
    combatIcons: 0,
    agilityIcons: 0,
    wildIcons: 0,
    uses: []
});

// Uses 配置开关
const enableUses = ref(false);

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

// 卡片类型映射
const typeMapping: Record<string, string> = {
    '调查员': 'Investigator',
    '支援': 'Asset',
    '事件': 'Event'
};

// 额外标记选项
const extraTokenOptions = [
    { label: '🚫 无标记', value: 'None' },
    { label: '⭕ 反应', value: 'Reaction' },
    { label: '⚡ 免费', value: 'FreeTrigger' }
];

// Token类型选项
const tokenTypeOptions = [
    { label: '💧 Resource', value: 'resource' },
    { label: '🔫 Ammo', value: 'resource' },
    { label: '💰 Bounty', value: 'resource' },
    { label: '⚡ Charge', value: 'resource' },
    { label: '🔍 Evidence', value: 'resource' },
    { label: '🤫 Secret', value: 'resource' },
    { label: '📦 Supply', value: 'resource' },
    { label: '🎁 Offering', value: 'resource' }
];

// 判断是否应该显示TTS脚本组件
const shouldShowTtsScript = computed(() => {
    const supportedTypes = ['调查员', '支援', '事件'];
    return supportedTypes.includes(props.cardType);
});

// 生成GMNotes
const generatedGMNotes = computed(() => {
    if (props.cardType === '调查员') {
        return generateInvestigatorGMNotes();
    } else if (props.cardType === '支援' || props.cardType === '事件') {
        return generateAssetGMNotes();
    }
    return '';
});

// 生成调查员GMNotes
const generateInvestigatorGMNotes = () => {
    const gmNotesData = {
        id: cardConfig.value.id || generateUUID(),
        type: 'Investigator',
        class: classMapping[props.cardData.class || '探求者'] || 'Seeker',
        traits: (props.cardData.traits || []).join('.') + (props.cardData.traits?.length ? '.' : ''),
        willpowerIcons: investigatorConfig.value.willpowerIcons,
        intellectIcons: investigatorConfig.value.intellectIcons,
        combatIcons: investigatorConfig.value.combatIcons,
        agilityIcons: investigatorConfig.value.agilityIcons,
        extraToken: investigatorConfig.value.extraToken
    };

    try {
        return JSON.stringify(gmNotesData, null, 2);
    } catch (error) {
        return '// JSON生成失败';
    }
};

// 生成支援卡/事件卡GMNotes
const generateAssetGMNotes = () => {
    const gmNotesData: any = {
        id: cardConfig.value.id || generateUUID(),
        class: classMapping[props.cardData.class || '中立'] || 'Neutral',
        type: typeMapping[props.cardType] || 'Asset',
        level: assetConfig.value.level,
        traits: (props.cardData.traits || []).join('.') + (props.cardData.traits?.length ? '.' : ''),
        cost: assetConfig.value.cost
    };

    // 添加技能图标
    if (assetConfig.value.willpowerIcons > 0) gmNotesData.willpowerIcons = assetConfig.value.willpowerIcons;
    if (assetConfig.value.intellectIcons > 0) gmNotesData.intellectIcons = assetConfig.value.intellectIcons;
    if (assetConfig.value.combatIcons > 0) gmNotesData.combatIcons = assetConfig.value.combatIcons;
    if (assetConfig.value.agilityIcons > 0) gmNotesData.agilityIcons = assetConfig.value.agilityIcons;
    if (assetConfig.value.wildIcons > 0) gmNotesData.wildIcons = assetConfig.value.wildIcons;

    // 添加Uses配置
    if (enableUses.value && assetConfig.value.uses.length > 0) {
        gmNotesData.uses = assetConfig.value.uses;
    }

    try {
        return JSON.stringify(gmNotesData, null, 2);
    } catch (error) {
        return '// JSON生成失败';
    }
};

// 生成完整的Lua脚本
const generatedLuaScript = computed(() => {
    if (!enablePhaseButtons.value) return '';
    return generatePhaseButtonScript(phaseButtonConfig.value);
});

// TTS脚本数据（包含配置）
const ttsScriptData = computed((): TtsScriptData => ({
    GMNotes: generatedGMNotes.value,
    LuaScript: generatedLuaScript.value,
    config: {
        enablePhaseButtons: enablePhaseButtons.value,
        enableUses: enableUses.value,
        phaseButtonConfig: phaseButtonConfig.value,
        investigatorConfig: investigatorConfig.value,
        assetConfig: assetConfig.value
    }
}));

// 生成UUID
const generateUUID = (): string => {
    return uuidv4().replace(/-/g, '').substring(0, 8).toUpperCase();
};

// 生成随机ID
const generateRandomId = () => {
    cardConfig.value.id = generateUUID();
    if (props.cardType === '调查员') {
        investigatorConfig.value.id = cardConfig.value.id;
    } else {
        assetConfig.value.id = cardConfig.value.id;
    }
    onCardConfigChange();
};

// 添加Use
const addUse = () => {
    assetConfig.value.uses.push({
        count: 2,
        type: 'Ammo',
        token: 'resource'
    });
    onCardConfigChange();
};

// 删除Use
const removeUse = (index: number) => {
    assetConfig.value.uses.splice(index, 1);
    onCardConfigChange();
};

// Uses开关变化处理
const onUsesToggle = () => {
    nextTick(() => {
        emit('update-tts-script', ttsScriptData.value);
    });
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

// 卡片配置变化处理
const onCardConfigChange = () => {
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
    onCardConfigChange();
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
    } else if ((props.cardType === '支援' || props.cardType === '事件') && props.cardData) {
        // 同步费用
        if (props.cardData.cost !== undefined) {
            assetConfig.value.cost = props.cardData.cost;
        }
        // 同步等级
        if (props.cardData.level !== undefined) {
            assetConfig.value.level = props.cardData.level;
        }
        // 同步uses配置
        if (props.cardData.uses && Array.isArray(props.cardData.uses)) {
            enableUses.value = true;
            assetConfig.value.uses = [...props.cardData.uses];
        }
    }
};

// 从保存的配置中加载数据
const loadFromSavedConfig = (savedConfig: any) => {
    console.log('🔧 加载保存的TTS配置:', savedConfig);
    
    if (savedConfig?.investigatorConfig) {
        const config = savedConfig.investigatorConfig;
        investigatorConfig.value = {
            id: config.id || '',
            extraToken: config.extraToken || 'None',
            willpowerIcons: config.willpowerIcons || 3,
            intellectIcons: config.intellectIcons || 3,
            combatIcons: config.combatIcons || 2,
            agilityIcons: config.agilityIcons || 2
        };
        cardConfig.value.id = config.id;
        console.log('✅ 调查员配置已加载');
    }

    if (savedConfig?.assetConfig) {
        const config = savedConfig.assetConfig;
        assetConfig.value = {
            id: config.id || '',
            cost: config.cost || 1,
            level: config.level || 0,
            willpowerIcons: config.willpowerIcons || 0,
            intellectIcons: config.intellectIcons || 0,
            combatIcons: config.combatIcons || 0,
            agilityIcons: config.agilityIcons || 0,
            wildIcons: config.wildIcons || 0,
            uses: config.uses || []
        };
        cardConfig.value.id = config.id;
        console.log('✅ 支援卡/事件卡配置已加载');
    }

    if (savedConfig?.enableUses !== undefined) {
        enableUses.value = savedConfig.enableUses;
        console.log('✅ Uses配置开关状态已加载:', enableUses.value);
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
            cardConfig.value.id = parsed.id || '';
            
            if (props.cardType === '调查员') {
                investigatorConfig.value = {
                    id: parsed.id || '',
                    extraToken: parsed.extraToken || 'None',
                    willpowerIcons: parsed.willpowerIcons || 3,
                    intellectIcons: parsed.intellectIcons || 3,
                    combatIcons: parsed.combatIcons || 2,
                    agilityIcons: parsed.agilityIcons || 2
                };
            } else {
                assetConfig.value = {
                    id: parsed.id || '',
                    cost: parsed.cost || 1,
                    level: parsed.level || 0,
                    willpowerIcons: parsed.willpowerIcons || 0,
                    intellectIcons: parsed.intellectIcons || 0,
                    combatIcons: parsed.combatIcons || 0,
                    agilityIcons: parsed.agilityIcons || 0,
                    wildIcons: parsed.wildIcons || 0,
                    uses: parsed.uses || []
                };
                
                if (parsed.uses && parsed.uses.length > 0) {
                    enableUses.value = true;
                }
            }
            console.log('✅ 从GMNotes解析配置成功');
        } catch (error) {
            console.warn('⚠️ 解析GMNotes失败:', error);
        }
    }

    // 如果存在LuaScript，启用阶段按钮并尝试解析配置
    if (ttsScript?.LuaScript) {
        enablePhaseButtons.value = true;
        const parsedConfig = parsePhaseButtonConfig(ttsScript.LuaScript);
        if (parsedConfig) {
            phaseButtonConfig.value = parsedConfig;
            console.log('✅ 从LuaScript解析阶段按钮配置成功');
        }
    } else {
        enablePhaseButtons.value = false;
    }
};

// 监听卡牌数据变化
watch(
    () => props.cardData,
    () => {
        syncAttributesFromCardData();
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
            onCardConfigChange();
        });
    },
    { immediate: true }
);

// 初始化
if (shouldShowTtsScript.value) {
    nextTick(() => {
        syncAttributesFromCardData();
        onCardConfigChange();
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
    width: 60px;
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

.uses-config {
    padding: 16px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    margin-top: 8px;
}

.use-config-row {
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
        width: 50px;
    }

    .button-config-row :deep(.n-space),
    .use-config-row :deep(.n-space) {
        flex-wrap: wrap;
    }
}
</style>

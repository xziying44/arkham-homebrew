<template>
    <n-card v-if="shouldShowTtsScript" :title="$t('ttsScriptEditor.title')" size="small" class="form-card tts-card">
        <n-space vertical size="medium">
            <!-- ID配置 - 所有卡牌类型都支持 -->
            <n-form-item :label="$t('ttsScriptEditor.scriptId.label')">
                <n-space align="center">
                    <n-input v-model:value="scriptConfig.id" :placeholder="$t('ttsScriptEditor.scriptId.placeholder')"
                        :allow-input="allowOnlyAlphaNumeric" :disabled="isScriptIdLocked" style="flex: 1" @update:value="onScriptConfigChange" />
                    <n-button @click="generateRandomId" size="small" type="primary" :disabled="isScriptIdLocked">
                        {{ $t('ttsScriptEditor.scriptId.button') }}
                    </n-button>
                </n-space>
            </n-form-item>

            <!-- 调查员小卡：绑定调查员卡牌（用于脚本ID软链接） -->
            <template v-if="props.cardType === '调查员小卡'">
                <BindCardField
                    v-model:path="miniBindPath"
                    :label="$t('ttsScriptEditor.mini.bind.label')"
                    :none-text="$t('ttsScriptEditor.mini.bind.noneSelected')"
                    :choose-text="$t('ttsScriptEditor.mini.bind.choose')"
                    :clear-text="$t('ttsScriptEditor.mini.bind.clear')"
                    :modal-title="$t('ttsScriptEditor.mini.bind.modalTitle')"
                    :cancel-text="$t('ttsScriptEditor.common.cancel')"
                    :info="$t('ttsScriptEditor.mini.bind.infoBound')"
                    :single-select="true"
                />
            </template>

            <!-- 定制卡：绑定任意卡牌（用于脚本ID软链接，后端生成 <base>-c） -->
            <template v-if="props.cardType === '定制卡'">
                <BindCardField
                    v-model:path="customBindPath"
                    :label="$t('ttsScriptEditor.custom.bind.label')"
                    :none-text="$t('ttsScriptEditor.custom.bind.noneSelected')"
                    :choose-text="$t('ttsScriptEditor.custom.bind.choose')"
                    :clear-text="$t('ttsScriptEditor.custom.bind.clear')"
                    :modal-title="$t('ttsScriptEditor.custom.bind.modalTitle')"
                    :cancel-text="$t('ttsScriptEditor.common.cancel')"
                    :info="$t('ttsScriptEditor.custom.bind.infoBound')"
                    :single-select="true"
                />
            </template>

            <!-- 通用入场标记配置 - 所有卡牌类型都支持 -->
            <n-form-item v-if="!isLightScriptOnly" :label="$t('ttsScriptEditor.entryTokens.label')">
                <n-space vertical size="medium">
                    <!-- 入场标记列表 -->
                    <div v-for="(use, index) in entryTokensConfig" :key="index" class="uses-config-row">
                        <n-space align="center">
                            <div class="uses-input-group">
                                <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.entryTokens.count')
                                    }}</n-text>
                                <n-input-number v-model:value="use.count" :min="0" :max="20" :step="1" size="small"
                                    @update:value="onScriptConfigChange" />
                            </div>
                            <div class="uses-input-group">
                                <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.entryTokens.token')
                                    }}</n-text>
                                <n-select v-model:value="use.token" :options="computedTokenOptions"
                                    :placeholder="$t('ttsScriptEditor.entryTokens.tokenPlaceholder')" style="width: 120px"
                                    @update:value="(value) => onEntryTokenChange(index, value)" />
                            </div>
                            <div class="uses-input-group">
                                <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.entryTokens.type')
                                    }}</n-text>
                                <n-select v-model:value="use.type" :options="getUsesTypeOptions(use.token)"
                                    :placeholder="$t('ttsScriptEditor.entryTokens.typePlaceholder')" style="width: 120px"
                                    @update:value="onScriptConfigChange" />
                            </div>
                            <n-button @click="removeEntryToken(index)" size="small" type="error" quaternary>
                                {{ $t('ttsScriptEditor.common.deleteBtn') }}
                            </n-button>
                        </n-space>
                    </div>

                    <!-- 添加入场标记 -->
                    <n-button @click="addEntryToken" size="small" type="primary" dashed>
                        {{ $t('ttsScriptEditor.entryTokens.addBtn') }}
                    </n-button>
                </n-space>
            </n-form-item>

            <!-- 游戏开始位置配置 - 所有卡牌类型都支持 -->
            <n-form-item v-if="!isLightScriptOnly" :label="$t('ttsScriptEditor.gameStart.label')">
                <n-space>
                    <n-switch v-model:value="gameStartConfig.startsInPlay" @update:value="onScriptConfigChange">
                        <template #checked>{{ $t('ttsScriptEditor.gameStart.startsInPlay') }}</template>
                        <template #unchecked>{{ $t('ttsScriptEditor.gameStart.startsInPlay') }}</template>
                    </n-switch>
                    <n-switch v-model:value="gameStartConfig.startsInHand" @update:value="onScriptConfigChange">
                        <template #checked>{{ $t('ttsScriptEditor.gameStart.startsInHand') }}</template>
                        <template #unchecked>{{ $t('ttsScriptEditor.gameStart.startsInHand') }}</template>
                    </n-switch>
                </n-space>
            </n-form-item>

            <!-- 封印脚本配置 - 除调查员与定制卡外均可用 -->
            <template v-if="supportsSealConfig">
                <n-form-item :label="$t('ttsScriptEditor.seal.label')">
                    <div class="seal-config">
                        <n-space align="center" justify="space-between">
                            <n-switch v-model:value="sealEnabled" @update:value="onSealConfigChange">
                                <template #checked>{{ $t('ttsScriptEditor.seal.enable') }}</template>
                                <template #unchecked>{{ $t('ttsScriptEditor.seal.enable') }}</template>
                            </n-switch>
                        </n-space>
                        <div v-if="sealEnabled" class="seal-fields">
                            <n-grid :cols="24" :x-gap="12" :y-gap="8" responsive="screen">
                                <n-gi :span="24" :lg="16">
                                    <div class="seal-field">
                                        <n-checkbox class="seal-checkbox" size="large" v-model:checked="sealAllTokens" @update:checked="onSealAllToggle">
                                            {{ $t('ttsScriptEditor.seal.all') }}
                                        </n-checkbox>
                                        <div v-if="!sealAllTokens" class="seal-select-wrap">
                                            <n-select
                                                v-model:value="sealTokens"
                                                :options="sealTokenOptions"
                                                multiple
                                                filterable
                                                :clearable="false"
                                                :max-tag-count="5"
                                                @update:value="onSealConfigChange"
                                                class="seal-select"
                                                :placeholder="$t('ttsScriptEditor.seal.tokensPlaceholder')"
                                            />
                                            <n-button v-if="sealTokens.length" size="tiny" tertiary class="seal-clear-btn" @click="() => { sealTokens = []; onSealConfigChange(); }">
                                                {{ $t('ttsScriptEditor.seal.clear') }}
                                            </n-button>
                                        </div>
                                    </div>
                                </n-gi>
                                <n-gi :span="24" :lg="8">
                                    <div class="seal-field">
                                        <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.seal.max') }}</n-text>
                                        <n-input-number
                                            v-model:value="sealMaxDisplay"
                                            :min="0"
                                            :max="99"
                                            :step="1"
                                            size="small"
                                            style="width: 180px"
                                            @update:value="onSealConfigChange"
                                        />
                                        <n-text depth="3" style="font-size: 12px;">{{ $t('ttsScriptEditor.seal.maxHint') }}</n-text>
                                    </div>
                                </n-gi>
                            </n-grid>
                        </div>
                    </div>
                </n-form-item>
            </template>

            <!-- 高级配置 - 仅支持的卡牌类型显示 -->
            <template v-if="hasAdvancedConfig">
                <!-- 调查员专用配置 -->
                <template v-if="props.cardType === '调查员'">
                <!-- 额外标记类型 -->
                <n-form-item :label="$t('ttsScriptEditor.investigator.extraTokenLabel')">
                    <n-select v-model:value="investigatorConfig.extraToken" :options="computedExtraTokenOptions"
                        :placeholder="$t('ttsScriptEditor.investigator.extraTokenPlaceholder')"
                        multiple :max-tag-count="3" @update:value="onScriptConfigChange" />
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

                <!-- 地点图标模式切换：默认模式（自动从卡面）/ 高级模式（可编辑数组） -->
                <n-form-item :label="t('ttsScriptEditor.location.modeLabel', '图标模式')">
                    <n-space align="center">
                        <n-switch v-model:value="locationAdvancedEnabled" @update:value="onLocationModeToggle">
                            <template #unchecked>{{ t('ttsScriptEditor.location.mode.default', '默认模式') }}</template>
                            <template #checked>{{ t('ttsScriptEditor.location.mode.advanced', '高级配置') }}</template>
                        </n-switch>
                        <n-text depth="3" style="font-size: 12px;">{{ t('ttsScriptEditor.location.modeHelp', '默认模式自动使用卡面上的地点图标；高级模式可自定义并可从卡面同步一次。') }}</n-text>
                    </n-space>
                </n-form-item>

                <!-- 默认模式：只读展示（自动同步卡面） -->
                <template v-if="!locationAdvancedEnabled">
                    <n-form-item :label="$t('ttsScriptEditor.location.locationIconLabel')">
                        <div class="loc-readonly">
                            <template v-if="getEditingCardData().location_icon">
                                <img v-if="getIconUrlByChinese(getEditingCardData().location_icon)" :src="getIconUrlByChinese(getEditingCardData().location_icon) as string" class="loc-icon" style="width:14px;height:14px;display:inline-block;vertical-align:middle;object-fit:contain;" />
                                <span>{{ defaultLocationIconDisplay }}</span>
                            </template>
                            <template v-else>
                                <span>{{ $t('ttsScriptEditor.location.notSet') }}</span>
                            </template>
                        </div>
                    </n-form-item>
                    <n-form-item :label="$t('ttsScriptEditor.location.connectionIconLabel')">
                        <div class="loc-readonly">
                            <template v-if="Array.isArray(getEditingCardData().location_link) && getEditingCardData().location_link.length">
                                <span v-for="(x, idx) in getEditingCardData().location_link" :key="idx" class="loc-chip">
                                    <img v-if="getIconUrlByChinese(x)" :src="getIconUrlByChinese(x) as string" class="loc-icon" style="width:14px;height:14px;display:inline-block;vertical-align:middle;object-fit:contain;" />
                                    <span>{{ toDisplayLabel(String(x)) }}</span>
                                </span>
                            </template>
                            <template v-else>
                                <span>{{ $t('ttsScriptEditor.location.notSet') }}</span>
                            </template>
                        </div>
                    </n-form-item>
                    <n-space v-if="props.isDoubleSided">
                        <n-button size="small" @click="applyToOtherSide" tertiary>
                            {{ t('ttsScriptEditor.location.applyToOtherSide', '应用到另一侧') }}
                        </n-button>
                    </n-space>
                </template>

                <!-- 高级模式：可编辑的数组（可添加自定义项） -->
                <template v-else>
                    <n-form-item :label="$t('ttsScriptEditor.location.locationIconLabel')">
                        <n-select
                            :options="locationIconSelectOptions"
                            :value="locationIconAdvanced"
                            filterable
                            tag
                            clearable
                            :render-label="renderLocationOptionLabel"
                            :placeholder="t('ttsScriptEditor.location.addPlaceholder', '输入或选择图标，例如 arkham_world')"
                            @update:value="onLocationIconChange"
                        />
                    </n-form-item>
                    <n-form-item :label="$t('ttsScriptEditor.location.connectionIconLabel')">
                        <n-select
                            multiple
                            tag
                            clearable
                            filterable
                            :options="locationIconSelectOptions"
                            :value="locationConnectionsAdvanced"
                            :render-label="renderLocationOptionLabel"
                            :render-tag="renderLocationTag"
                            :placeholder="t('ttsScriptEditor.location.addPlaceholder', '输入或选择连接图标')"
                            @update:value="onLocationConnectionsChange"
                        />
                    </n-form-item>
                    <n-space>
                        <n-button size="small" type="primary" tertiary @click="syncLocationFromCard">
                            {{ t('ttsScriptEditor.location.syncFromCardOnce', '从卡面同步一次') }}
                        </n-button>
                        <n-button v-if="props.isDoubleSided" size="small" @click="applyToOtherSide" tertiary>
                            {{ t('ttsScriptEditor.location.applyToOtherSide', '应用到另一侧') }}
                        </n-button>
                    </n-space>
                </template>

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
            <div v-for="(signature, index) in signatureConfig" :key="`${signature.path}-${index}`"
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
            </template>

            <!-- 预览GMNotes - 所有卡牌类型都显示 -->
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

            <!-- 不支持高级配置的卡牌类型显示提示 -->
            <template v-if="!hasAdvancedConfig">
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

    <!-- 调查员小卡绑定选择器 -->
    

    
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
import { WorkspaceService, TtsScriptService } from '@/api';
import { cardTypeConfigs } from '@/config/cardTypeConfigsEn';
import { getIconUrlByChinese } from '@/config/locationIcons';
import { h } from 'vue';
import { NTag } from 'naive-ui';
import CardFileBrowser from './CardFileBrowser.vue';
import BindCardField from './BindCardField.vue';

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
        signatureConfig: Array<{ path: string; name: string; count: number }>;
        entryTokensConfig: UseConfig[]; // 通用入场标记配置
        gameStartConfig: GameStartConfig; // 游戏开始位置配置
        seal?: SealConfig; // 封印脚本配置
    };
}

interface ScriptConfig {
    id: string;
}

interface InvestigatorConfig {
    extraToken: string[];
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

interface GameStartConfig {
    startsInPlay: boolean;
    startsInHand: boolean;
}

interface SealConfig {
    enabled: boolean;
    allTokens: boolean;
    tokens: string[];
    max?: number | null;
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
    extraToken: [],
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
const signatureConfig = ref<Array<{ path: string; name: string; count: number }>>([]);
const showSignatureSelector = ref(false);

// 通用入场标记配置 - 所有卡牌类型都支持
const entryTokensConfig = ref<UseConfig[]>([]);

// 游戏开始位置配置 - 所有卡牌类型都支持
const gameStartConfig = ref<GameStartConfig>({
    startsInPlay: false,
    startsInHand: false
});

// 地点图标 - 高级模式开关与数据（按正/背面独立配置）
const sideKey = computed<'front' | 'back'>(() => (props.isDoubleSided && props.currentSide === 'back') ? 'back' : 'front');
const locationAdvancedEnabledBySide = ref<{ front: boolean; back: boolean }>({ front: false, back: false });
const locationIconAdvancedBySide = ref<{ front: string; back: string }>({ front: '', back: '' });
const locationConnectionsAdvancedBySide = ref<{ front: string[]; back: string[] }>({ front: [], back: [] });

const locationAdvancedEnabled = computed<boolean>({
    get() { return locationAdvancedEnabledBySide.value[sideKey.value]; },
    set(v: boolean) { locationAdvancedEnabledBySide.value[sideKey.value] = v; }
});
const locationIconAdvanced = computed<string>({
    get() { return locationIconAdvancedBySide.value[sideKey.value]; },
    set(v: string) { locationIconAdvancedBySide.value[sideKey.value] = v; }
});
const locationConnectionsAdvanced = computed<string[]>({
    get() { return locationConnectionsAdvancedBySide.value[sideKey.value]; },
    set(v: string[]) { locationConnectionsAdvancedBySide.value[sideKey.value] = v; }
});

// 从英文配置获取地点图标选项（英文 label + 中文 value），构建映射
const locationIconOptionList = (() => {
    const cfg = cardTypeConfigs['地点卡'];
    const fields = Array.isArray(cfg?.fields) ? cfg.fields : [];
    const iconField = fields.find(f => f.key === 'location_icon');
    const linkField = fields.find(f => f.key === 'location_link');
    const options = Array.isArray(iconField?.options) ? iconField!.options : [];
    const linkOptions = Array.isArray(linkField?.options) ? linkField!.options : [];
    // 保持去重（两处来源应一致）
    const map = new Map<string, string>(); // value(中文) -> label(英文)
    [...options, ...linkOptions].forEach(opt => {
        if (opt && typeof opt.value === 'string' && typeof opt.label === 'string') {
            map.set(opt.value as string, opt.label);
        }
    });
    return map; // 中文 -> 英文
})();

const englishLabelToChineseValueMap = (() => {
    const m = new Map<string, string>(); // 规范化英文 -> 中文
    const normalize = (s: string) => (s || '')
        // 去掉前缀的非字母字符（如 emoji 与图标）
        .replace(/^[^A-Za-z]+/, '')
        .replace(/\s+/g, ' ')
        .trim()
        .toLowerCase();
    locationIconOptionList.forEach((label, value) => {
        m.set(normalize(label), value);
        // 也尝试去掉前缀符号（含 emoji 后已去除），保留纯英文关键词匹配
    });
    return { normalize, map: m };
})();

// 显示用：根据语言选择中文或英文
const { locale } = useI18n();
const toDisplayLabel = (value: string): string => {
    if (!value) return '';
    const isZh = String(locale.value || '').toLowerCase().startsWith('zh');
    if (isZh) return value; // 中文环境直接显示中文
    const label = locationIconOptionList.get(value);
    return label || value; // 英文环境显示英文，不存在则回退原值
};

// 默认模式下展示：从卡面读取并本地化
const defaultLocationIconDisplay = computed<string>(() => {
    const raw = getEditingCardData().location_icon as string | undefined;
    if (!raw) return t('ttsScriptEditor.location.notSet');
    return toDisplayLabel(String(raw));
});
const defaultLocationConnectionsDisplay = computed<string>(() => {
    const arr = Array.isArray(getEditingCardData().location_link) ? getEditingCardData().location_link as any[] : [];
    if (!arr.length) return t('ttsScriptEditor.location.notSet');
    return arr.map(x => toDisplayLabel(String(x))).join(', ');
});

// 显示直接由 NSelect 的 render-label 控制，无需额外 display 计算

// 规范化输入：英文→中文，保留未知值（自定义）
const normalizeIconInput = (input: string): string => {
    if (!input) return input;
    // 如果恰好等于中文值，直接返回
    if (locationIconOptionList.has(input)) return input;
    const key = englishLabelToChineseValueMap.normalize(input);
    const mapped = englishLabelToChineseValueMap.map.get(key);
    return mapped || input; // 未知项直接返回作为自定义
};

const uniqueNormalized = (arr: string[]): string[] => {
    const result: string[] = [];
    const seen = new Set<string>();
    for (const raw of arr) {
        const norm = normalizeIconInput(String(raw || '').trim());
        if (!norm) continue;
        if (!seen.has(norm)) {
            seen.add(norm);
            result.push(norm);
        }
    }
    return result;
};

// 高级模式：事件处理
const locationIconSelectOptions = computed(() => {
    const arr: Array<{ label: string; value: string }> = [];
    locationIconOptionList.forEach((_, value) => {
        arr.push({ label: toDisplayLabel(value), value });
    });
    return arr;
});

const renderLocationOptionLabel = (option: any) => {
    const src = getIconUrlByChinese(option.value as string);
    const text = toDisplayLabel(option.value as string);
    const imgStyle = 'width:14px;height:14px;display:inline-block;vertical-align:middle;object-fit:contain;';
    return h('div', { class: 'loc-opt', style: 'display:inline-flex;align-items:center;gap:6px;' }, [
        src ? h('img', { src, class: 'loc-icon', style: imgStyle }) : null,
        h('span', { style: 'line-height:1;display:inline-block;vertical-align:middle;' }, text)
    ]);
};
const renderLocationTag = ({ option, handleClose }: any) => {
    const value = option?.value as string;
    const src = getIconUrlByChinese(value || '');
    const text = toDisplayLabel(value || '');
    const imgStyle = 'width:14px;height:14px;display:inline-block;vertical-align:middle;object-fit:contain;';
    const content = [src ? h('img', { src, class: 'loc-icon', style: imgStyle }) : null, h('span', { style: 'line-height:1;display:inline-block;vertical-align:middle;' }, text)];
    return h(
        NTag,
        { closable: true, onClose: handleClose, size: 'small' },
        { default: () => h('span', { class: 'loc-opt', style: 'display:inline-flex;align-items:center;gap:6px;' }, content) }
    );
};

const onLocationIconChange = (val: string | null) => {
    const normalized = normalizeIconInput(val || '');
    locationIconAdvanced.value = normalized;
    onScriptConfigChange();
};
const onLocationConnectionsChange = (displayList: string[]) => {
    locationConnectionsAdvanced.value = uniqueNormalized(displayList);
    onScriptConfigChange();
};
const onLocationModeToggle = (enabled: boolean) => {
    if (isSyncingFromParent.value) return;
    if (enabled && !locationIconAdvanced.value && locationConnectionsAdvanced.value.length === 0) {
        syncLocationFromCard();
    } else {
        // 切换任一模式都应刷新预览
        onScriptConfigChange();
    }
};
const syncLocationFromCard = () => {
    const side = getEditingCardData();
    const iconVal = side.location_icon ? String(side.location_icon) : '';
    const links = Array.isArray(side.location_link) ? side.location_link.map((x: any) => String(x)) : [];
    locationIconAdvanced.value = normalizeIconInput(iconVal);
    locationConnectionsAdvanced.value = uniqueNormalized(links);
    onScriptConfigChange();
};

// 应用到另一侧：将当前侧的图标配置复制到另一侧（目标侧启用高级模式）
const applyToOtherSide = () => {
    const target: 'front' | 'back' = sideKey.value === 'front' ? 'back' : 'front';
    // 源数据：优先取高级配置，否则取卡面字段
    const sourceIcon = locationAdvancedEnabled.value
        ? (locationIconAdvanced.value || '')
        : (getEditingCardData().location_icon ? String(getEditingCardData().location_icon) : '');
    const sourceLinks = locationAdvancedEnabled.value
        ? [...locationConnectionsAdvanced.value]
        : (Array.isArray(getEditingCardData().location_link) ? (getEditingCardData().location_link as any[]).map(x => String(x)) : []);

    locationAdvancedEnabledBySide.value[target] = true;
    locationIconAdvancedBySide.value[target] = normalizeIconInput(sourceIcon);
    locationConnectionsAdvancedBySide.value[target] = uniqueNormalized(sourceLinks);
    onScriptConfigChange();
    message.success(t('ttsScriptEditor.messages.applyOtherSideSuccess', '已应用到另一侧'));
};

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
        '冒险参考卡': 'ScenarioReference',
        '玩家卡背': 'PlayerCardBack',
        '遭遇卡背': 'EncounterCardBack'
    };

    return extendedMapping[cardType] || 'Asset'; // 默认为Asset
};

// Chaos Token 可选项（保持与后端Lua模板名称一致）
const CHAOS_TOKENS = [
    'Elder Sign', '+1', '0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8',
    'Skull', 'Cultist', 'Tablet', 'Elder Thing', 'Auto-fail', 'Bless', 'Curse', 'Frost'
] as const;
const TOKEN_EMOJI_MAP: Record<string, string> = {
    'Elder Sign': '⭐',
    '+1': '🔹', '0': '🔹', '-1': '🔹', '-2': '🔹', '-3': '🔹', '-4': '🔹', '-5': '🔹', '-6': '🔹', '-7': '🔹', '-8': '🔹',
    'Skull': '💀', 'Cultist': '👤', 'Tablet': '📜', 'Elder Thing': '👹', 'Auto-fail': '🐙', 'Bless': '✨', 'Curse': '🌑', 'Frost': '❄️'
};
const sealTokenOptions = computed(() => CHAOS_TOKENS.map(name => ({
    label: `${TOKEN_EMOJI_MAP[name] || '🔹'} ${t(`ttsScriptEditor.seal.tokenNames.${name}` as any) || name}`,
    value: name
})));

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

// 是否允许封印脚本配置（排除调查员与定制卡）
const supportsSealConfig = computed(() => {
    return !(props.cardType === '调查员' || props.cardType === '定制卡');
});

// 轻量脚本：调查员小卡/定制卡仅显示 GMNotes 预览
const isLightScriptOnly = computed(() => props.cardType === '调查员小卡' || props.cardType === '定制卡');

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

// 后端预览结果
const backendGMNotes = ref('');
const backendLuaScript = ref('');

// 统一的GMNotes（来自后端）
const generatedGMNotes = computed(() => {
    if (!shouldShowTtsScript.value) return '';
    return backendGMNotes.value;
});


// 生成完整的Lua脚本（来自后端）
const generatedLuaScript = computed(() => {
    return backendLuaScript.value || '';
});

// Mini card binding
// removed: handled by BindCardField internally
// const showMiniBindSelector = ref(false);
const miniBindPath = ref<string>('');
const isMiniCardBound = computed(() => props.cardType === '调查员小卡' && !!miniBindPath.value);

// Custom card binding
const customBindPath = ref<string>('');
const isCustomBound = computed(() => props.cardType === '定制卡' && !!customBindPath.value);
const isScriptIdLocked = computed(() => isMiniCardBound.value || isCustomBound.value);

// 绑定变化触发预览
watch([miniBindPath, customBindPath], () => {
    if (isSyncingFromParent.value) return;
    onScriptConfigChange();
});

// TTS脚本数据（包含配置）
// 统一 v2 配置对象（将作为 tts_config 存储与传输）
const tts_config = computed(() => ({
    version: 'v2',
    script_id: scriptConfig.value.id,
    enablePhaseButtons: enablePhaseButtons.value,
    phaseButtonConfig: phaseButtonConfig.value,
    mini: {
        bind: { path: miniBindPath.value || '' }
    },
    custom: {
        bind: { path: customBindPath.value || '' }
    },
    investigator: {
        extraToken: investigatorConfig.value.extraToken,
        willpowerIcons: investigatorConfig.value.willpowerIcons,
        intellectIcons: investigatorConfig.value.intellectIcons,
        combatIcons: investigatorConfig.value.combatIcons,
        agilityIcons: investigatorConfig.value.agilityIcons,
    },
    signatures: signatureConfig.value.map(s => ({ path: s.path, count: s.count })),
    entryTokens: entryTokensConfig.value,
    gameStart: {
        startsInPlay: gameStartConfig.value.startsInPlay,
        startsInHand: gameStartConfig.value.startsInHand,
    },
    seal: {
        enabled: sealEnabled.value,
        allTokens: sealAllTokens.value,
        tokens: [...sealTokens.value],
        max: sealMax.value ?? null,
    } as SealConfig,
    ...(locationAdvancedEnabledBySide.value.front && (locationIconAdvancedBySide.value.front || locationConnectionsAdvancedBySide.value.front.length > 0) ? {
        locationFront: {
            ...(locationIconAdvancedBySide.value.front ? { icons: locationIconAdvancedBySide.value.front } : {}),
            ...(locationConnectionsAdvancedBySide.value.front.length > 0 ? { connections: [...locationConnectionsAdvancedBySide.value.front] } : {}),
        }
    } : {}),
    ...(locationAdvancedEnabledBySide.value.back && (locationIconAdvancedBySide.value.back || locationConnectionsAdvancedBySide.value.back.length > 0) ? {
        locationBack: {
            ...(locationIconAdvancedBySide.value.back ? { icons: locationIconAdvancedBySide.value.back } : {}),
            ...(locationConnectionsAdvancedBySide.value.back.length > 0 ? { connections: [...locationConnectionsAdvancedBySide.value.back] } : {}),
        }
    } : {}),
}));

const ttsScriptData = computed((): TtsScriptData => ({
    GMNotes: generatedGMNotes.value,
    LuaScript: generatedLuaScript.value,
    // 复用原字段名 config 以兼容父组件处理，但内部已是 v2 的 tts_config 结构
    config: tts_config.value as any,
}));

// 避免父子间同步引发的循环请求
const isSyncingFromParent = ref(false);
const hasInitPreview = ref(false);

// 预览调用防抖
let previewTimer: any = null;

// 实际请求函数
const updateBackendPreview = async () => {
    try {
        const cardPayload = JSON.parse(JSON.stringify(props.cardData || {}));
        // 注入/覆盖 v2 tts_config，不修改原 props 对象
        cardPayload.tts_config = tts_config.value;
        const result = await TtsScriptService.generateFromCard(cardPayload);
        backendGMNotes.value = result.GMNotes || '';
        backendLuaScript.value = result.LuaScript || '';
    } catch (err) {
        console.warn('TTS 后端预览失败，使用空结果:', err);
        backendGMNotes.value = '';
        backendLuaScript.value = '';
    }
};

// 防抖调度函数
const scheduleBackendPreview = () => {
    if (previewTimer) clearTimeout(previewTimer);
    previewTimer = setTimeout(() => {
        updateBackendPreview();
    }, 250);
};

// 生成UUID
const generateUUID = (): string => {
    return uuidv4().replace(/-/g, '').substring(0, 8).toUpperCase();
};

// 生成随机ID
const generateRandomId = () => {
    scriptConfig.value.id = generateUUID();
    onScriptConfigChange();
};

// 通用入场标记配置方法
// 添加入场标记
const addEntryToken = () => {
    entryTokensConfig.value.push({
        count: 2,
        type: 'Resource',
        token: 'resource'
    });
    onScriptConfigChange();
};

// 删除入场标记
const removeEntryToken = (index: number) => {
    entryTokensConfig.value.splice(index, 1);
    onScriptConfigChange();
};

// 入场标记令牌类型变化时自动更新type
const onEntryTokenChange = (index: number, token: string) => {
    const use = entryTokensConfig.value[index];
    if (use) {
        use.token = token;
        const typeOptions = getUsesTypeOptions(token);
        if (typeOptions.length > 0) {
            use.type = typeOptions[0].value;
        }
        onScriptConfigChange();
    }
};

// 为了向后兼容，保留原来的asset uses方法（用于支援卡/事件卡的现有配置加载）
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
const onScriptConfigChange = async () => {
    // 如果当前是父组件写回引发的同步，不再触发预览与上行事件，避免循环
    if (isSyncingFromParent.value) return;
    scheduleBackendPreview();
    nextTick(() => {
        emit('update-tts-script', ttsScriptData.value);
    });
};

// 封印脚本配置
const sealEnabled = ref(false);
const sealAllTokens = ref(true);
const sealTokens = ref<string[]>([]);
const sealMax = ref<number | null>(null);
const sealMaxDisplay = computed<number>({
    get() { return typeof sealMax.value === 'number' ? sealMax.value : 0 },
    set(v: number) { sealMax.value = (!v || v === 0) ? null : v }
});

const onSealConfigChange = async () => {
    if (isSyncingFromParent.value) return;
    scheduleBackendPreview();
    nextTick(() => emit('update-tts-script', ttsScriptData.value));
};

const onSealAllToggle = (checked: boolean) => {
    sealAllTokens.value = checked;
    if (checked) {
        sealTokens.value = [];
    }
    onSealConfigChange();
};

// 阶段按钮配置变化处理
const onPhaseButtonConfigChange = async () => {
    if (isSyncingFromParent.value) return;
    scheduleBackendPreview();
    nextTick(() => {
        emit('update-tts-script', ttsScriptData.value);
    });
};

// 阶段按钮开关变化处理
const onPhaseButtonToggle = async () => {
    if (isSyncingFromParent.value) return;
    scheduleBackendPreview();
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
        // 处理选中的卡牌文件 - 每张卡牌都单独添加（按相对路径保存）
        for (const item of selectedItems) {
            if (item.type === 'card') {
                const cardPath: string = item.fullPath; // 相对工作目录路径
                // 名称：优先文件树中的 name（文件名），不再强依赖读取文件
                const displayName: string = item.name || cardPath.split('/').pop() || cardPath;
                signatureConfig.value.push({ path: cardPath, name: displayName, count: 1 });
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
            investigatorConfig.value.willpowerIcons = attributes[0] ?? 3;
            investigatorConfig.value.intellectIcons = attributes[1] ?? 3;
            investigatorConfig.value.combatIcons = attributes[2] ?? 2;
            investigatorConfig.value.agilityIcons = attributes[3] ?? 2;
        }
    }
    if ((props.cardType === '支援卡' || props.cardType === '事件卡') && currentEditingData.uses) {
        assetConfig.value.uses = [...currentEditingData.uses];
        // 同时同步到通用入场标记配置
        entryTokensConfig.value = [...currentEditingData.uses];
    } else if (currentEditingData.uses) {
        // 其他卡牌类型如果有uses字段，也同步到通用入场标记配置
        entryTokensConfig.value = [...currentEditingData.uses];
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
        investigatorConfig.value = {
            ...savedConfig.investigatorConfig,
            extraToken: Array.isArray(savedConfig.investigatorConfig.extraToken)
                ? savedConfig.investigatorConfig.extraToken
                : (savedConfig.investigatorConfig.extraToken || 'None').split('|').filter(token => token && token !== 'None')
        };
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
    // 加载新的通用配置
    if (savedConfig?.entryTokensConfig) {
        entryTokensConfig.value = [...savedConfig.entryTokensConfig];
        console.log('✅ 入场标记配置已加载:', entryTokensConfig.value.length, '个标记');
    }
    if (savedConfig?.gameStartConfig) {
        gameStartConfig.value = { ...savedConfig.gameStartConfig };
        console.log('✅ 游戏开始位置配置已加载:', gameStartConfig.value);
    }
    if (savedConfig?.seal) {
        const s = savedConfig.seal;
        sealEnabled.value = !!s.enabled;
        sealAllTokens.value = !!s.allTokens;
        sealTokens.value = Array.isArray(s.tokens) ? [...s.tokens] : [];
        sealMax.value = (typeof s.max === 'number' && s.max > 0) ? s.max : null;
        console.log('✅ 封印脚本配置已加载:', {
            enabled: sealEnabled.value,
            all: sealAllTokens.value,
            tokens: sealTokens.value.length,
            max: sealMax.value
        });
    }
};

// 从 v2 tts_config 加载
const loadFromTtsConfigV2 = (cfg: any) => {
    if (!cfg) return;
    // 基本
    scriptConfig.value.id = cfg.script_id || scriptConfig.value.id || generateUUID();
    // 调查员
    if (cfg.investigator) {
        investigatorConfig.value = {
            extraToken: Array.isArray(cfg.investigator.extraToken) ? cfg.investigator.extraToken : [],
            willpowerIcons: Number(cfg.investigator.willpowerIcons ?? 3),
            intellectIcons: Number(cfg.investigator.intellectIcons ?? 3),
            combatIcons: Number(cfg.investigator.combatIcons ?? 2),
            agilityIcons: Number(cfg.investigator.agilityIcons ?? 2),
        };
    }
    // 阶段按钮
    enablePhaseButtons.value = !!cfg.enablePhaseButtons;
    if (cfg.phaseButtonConfig && Array.isArray(cfg.phaseButtonConfig.buttons)) {
        phaseButtonConfig.value = { buttons: [...cfg.phaseButtonConfig.buttons] };
    }
    // 入场标记
    if (Array.isArray(cfg.entryTokens)) {
        entryTokensConfig.value = [...cfg.entryTokens];
    }
    // 游戏开始位置
    if (cfg.gameStart) {
        gameStartConfig.value = {
            startsInPlay: !!cfg.gameStart.startsInPlay,
            startsInHand: !!cfg.gameStart.startsInHand,
        };
    }
    // 签名卡
    if (Array.isArray(cfg.signatures)) {
        signatureConfig.value = cfg.signatures.map((s: any) => ({
            path: s.path,
            name: s.name || (typeof s.path === 'string' ? (s.path.split('/').pop() || s.path) : ''),
            count: Number(s.count || 1)
        }));
    }
    // 封印脚本
    if (cfg.seal) {
        const s = cfg.seal;
        sealEnabled.value = !!s.enabled;
        sealAllTokens.value = !!s.allTokens;
        sealTokens.value = Array.isArray(s.tokens) ? [...s.tokens] : [];
        sealMax.value = (typeof s.max === 'number' && s.max > 0) ? s.max : null;
    }
    // 地点（高级模式）
    // 兼容旧字段（location）：将其视为正面高级配置
    if (cfg.location && (typeof cfg.location.icons === 'string' || Array.isArray(cfg.location.connections))) {
        locationAdvancedEnabledBySide.value.front = true;
        locationIconAdvancedBySide.value.front = normalizeIconInput(typeof cfg.location.icons === 'string' ? cfg.location.icons : '');
        locationConnectionsAdvancedBySide.value.front = uniqueNormalized(Array.isArray(cfg.location.connections) ? cfg.location.connections : []);
    }
    // 新字段：locationFront / locationBack（分别配置）
    if (cfg.locationFront && (typeof cfg.locationFront.icons === 'string' || Array.isArray(cfg.locationFront.connections))) {
        locationAdvancedEnabledBySide.value.front = true;
        locationIconAdvancedBySide.value.front = normalizeIconInput(typeof cfg.locationFront.icons === 'string' ? cfg.locationFront.icons : '');
        locationConnectionsAdvancedBySide.value.front = uniqueNormalized(Array.isArray(cfg.locationFront.connections) ? cfg.locationFront.connections : []);
    }
    if (cfg.locationBack && (typeof cfg.locationBack.icons === 'string' || Array.isArray(cfg.locationBack.connections))) {
        locationAdvancedEnabledBySide.value.back = true;
        locationIconAdvancedBySide.value.back = normalizeIconInput(typeof cfg.locationBack.icons === 'string' ? cfg.locationBack.icons : '');
        locationConnectionsAdvancedBySide.value.back = uniqueNormalized(Array.isArray(cfg.locationBack.connections) ? cfg.locationBack.connections : []);
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
                    extraToken: (parsed.extraToken || 'None').split('|').filter(token => token && token !== 'None'),
                    willpowerIcons: parsed.willpowerIcons ?? 3,
                    intellectIcons: parsed.intellectIcons ?? 3,
                    combatIcons: parsed.combatIcons ?? 2,
                    agilityIcons: parsed.agilityIcons ?? 2
                };
            }
            if ((props.cardType === '支援卡' || props.cardType === '事件卡') && parsed.uses) {
                assetConfig.value.uses = parsed.uses;
                // 同时加载到通用入场标记配置中
                entryTokensConfig.value = [...parsed.uses];
            } else if (parsed.uses) {
                // 其他卡牌类型如果有uses字段，也加载到通用入场标记配置中
                entryTokensConfig.value = [...parsed.uses];
            }

            // 加载游戏开始位置配置（如果存在）
            if (parsed.startsInPlay !== undefined) {
                gameStartConfig.value.startsInPlay = parsed.startsInPlay;
            }
            if (parsed.startsInHand !== undefined) {
                gameStartConfig.value.startsInHand = parsed.startsInHand;
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
                            count: use.count ?? use.countPerInvestigator ?? 1,
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
            // 默认模式下（未启用高级地点配置），地点图标从卡面自动生效，需触发预览
            if (!locationAdvancedEnabled.value) {
                scheduleBackendPreview();
            }
        }
    },
    { deep: true }
);

// 监听TTS脚本数据变化，加载配置
watch(
() => props.cardData.tts_script,
(newTtsScript) => {
    // 仅用于旧数据向后兼容；若已存在 v2 配置，则忽略
    if ((props.cardData as any)?.tts_config?.version === 'v2') return;
    console.log('📥 旧版 TTS 脚本数据变化:', newTtsScript);
    if (!newTtsScript) {
        if (!scriptConfig.value.id) {
            scriptConfig.value.id = generateUUID();
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

// 监听 v2 tts_config
watch(
    () => (props.cardData as any)?.tts_config,
    (cfg) => {
        if (cfg?.version === 'v2') {
            console.log('📥 加载 v2 tts_config');
            isSyncingFromParent.value = true;
            loadFromTtsConfigV2(cfg);
            // 加载 mini 绑定
            const m = (cfg as any)?.mini?.bind?.path;
            if (typeof m === 'string') miniBindPath.value = m;
            // 加载 custom 绑定
            const c = (cfg as any)?.custom?.bind?.path;
            if (typeof c === 'string') customBindPath.value = c;
            // 避免触发再次 emit 导致循环，仅在首次加载时进行一次预览
            nextTick(async () => {
                isSyncingFromParent.value = false;
                if (!hasInitPreview.value) {
                    hasInitPreview.value = true;
                    await updateBackendPreview();
                }
            });
        }
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
        // 不在此处主动触发 onScriptConfigChange，首帧预览交由 tts_config / tts_script 的 watcher 负责
    });
}
</script>

<style scoped>
/* 样式部分 */
.tts-card {
    background: linear-gradient(135deg, rgba(74, 144, 226, 0.05) 0%, rgba(80, 200, 120, 0.05) 100%);
    border: 2px solid rgba(74, 144, 226, 0.2);
}

.loc-readonly {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
}
.loc-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-right: 8px;
}
.loc-icon {
    width: 14px;
    height: 14px;
    vertical-align: middle;
    display: inline-block;
}
.loc-opt {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
:deep(.loc-opt) {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
:deep(.loc-icon) {
    width: 14px;
    height: 14px;
    vertical-align: middle;
    display: inline-block;
}
/* Reduce option height in dropdown */
:deep(.n-base-select-menu .n-base-select-option) {
    padding: 4px 8px;
}
:deep(.n-base-select-menu .n-base-select-option__content) {
    display: inline-flex;
    align-items: center;
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

.seal-config {
    width: 100%;
    box-sizing: border-box;
    padding: 14px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.seal-fields {
    margin-top: 10px;
}

.seal-field {
    min-width: 240px;
}

.seal-select { width: 100%; }
.seal-select-wrap { margin-top: 6px; }
.seal-clear-btn { margin-top: 6px; }

.seal-checkbox :deep(.n-checkbox) {
    display: inline-flex;
    align-items: center;
}
.seal-checkbox :deep(.n-checkbox__label) {
    display: inline-flex;
    align-items: center;
}
.seal-checkbox {
    padding: 6px 8px;
}

.seal-select :deep(.n-base-selection) {
    width: 100%;
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

<template>
    <n-card v-if="shouldShowEditor" :title="$t('deckOptionEditor.title')" size="small" class="form-card deck-option-card">
        <n-space vertical size="large">
            <!-- 牌库选项列表 -->
            <div class="deck-options-list">
                <!-- 牌组构建顺序说明 -->
                <div class="deck-building-order-notice">
                    <n-button
                        text
                        type="warning"
                        @click="toggleOrderNotice"
                        style="margin-bottom: 12px; padding: 8px 12px;"
                    >
                        <template #icon>
                            <n-icon style="margin-right: 6px;">
                                <span v-if="showOrderNotice">📖</span>
                                <span v-else>📘</span>
                            </n-icon>
                        </template>
                        {{ $t('deckOptionEditor.deckBuildingOrder.title') }}
                        <n-icon style="margin-left: 6px; transition: transform 0.2s;" :style="{ transform: showOrderNotice ? 'rotate(180deg)' : 'rotate(0deg)' }">
                            <span>▼</span>
                        </n-icon>
                    </n-button>

                    <n-collapse-transition :show="showOrderNotice">
                        <n-alert type="warning" style="margin-bottom: 16px;">
                            <div class="notice-content">
                                <p>{{ $t('deckOptionEditor.deckBuildingOrder.description') }}</p>

                                <div class="example-section" style="margin-top: 12px;">
                                    <n-text strong>{{ $t('deckOptionEditor.deckBuildingOrder.exampleTitle') }}:</n-text>
                                    <p style="margin-top: 8px; margin-bottom: 4px;">{{ $t('deckOptionEditor.deckBuildingOrder.exampleDescription') }}</p>
                                    <ol style="margin: 8px 0 8px 20px; padding: 0; font-size: 12px; line-height: 1.4;">
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order1') }}</li>
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order2') }}</li>
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order3') }}</li>
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order4') }}</li>
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order5') }}</li>
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order6') }}</li>
                                        <li>{{ $t('deckOptionEditor.deckBuildingOrder.order7') }}</li>
                                    </ol>
                                    <n-text depth="3" style="font-size: 11px; font-style: italic;">
                                        {{ $t('deckOptionEditor.deckBuildingOrder.note') }}
                                    </n-text>
                                </div>
                            </div>
                        </n-alert>
                    </n-collapse-transition>
                </div>

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
                                    {{ $t('deckOptionEditor.slots') }}: {{ formatSlotDisplay(option.slot) }}
                                </n-tag>
                                <n-tag v-if="option.uses && option.uses.length > 0" size="tiny" type="info">
                                    {{ $t('deckOptionEditor.uses') }}: {{ formatUsesDisplay(option.uses) }}
                                </n-tag>
                                <n-tag v-if="option.faction_select && option.faction_select.length > 0" size="tiny" type="warning">
                                    {{ $t('deckOptionEditor.factionSelect') }}: {{ formatFactionDisplay(option.faction_select) }}
                                </n-tag>
                                <n-tag v-if="option.deck_size_select && option.deck_size_select.length > 0" size="tiny" type="warning">
                                    {{ $t('deckOptionEditor.deckSizeSelect') }}: {{ option.deck_size_select.join(', ') }}{{ $t('deckOptionEditor.deckSizes.unit') }}
                                </n-tag>
                                <n-tag v-if="option.option_select && option.option_select.length > 0" size="tiny" type="warning">
                                    {{ $t('deckOptionEditor.advancedSelect') }} ({{ option.option_select.length }}{{ $t('deckOptionEditor.items') }})
                                </n-tag>
                            </n-space>
                        </div>

                        <!-- 选项编辑器 -->
                        <div v-else class="option-editor" :key="`editing-${index}`">
                            <n-form :model="option" label-placement="left" size="small">
                                <!-- ID和名称设置 -->
                                <n-form-item :label="$t('deckOptionEditor.optionId')">
                                    <n-input v-model:value="option.id" :placeholder="$t('deckOptionEditor.optionIdPlaceholder')" @blur="syncNameFromId(option)" />
                                </n-form-item>
                                <n-form-item :label="$t('deckOptionEditor.optionName')">
                                    <n-input v-model:value="option.name" :placeholder="$t('deckOptionEditor.optionNamePlaceholder')" />
                                </n-form-item>

                                <!-- 选择机制 -->
                                <n-form-item :label="$t('deckOptionEditor.selectionMechanismLabel')">
                                    <n-select
                                        v-model:value="option.selectionType"
                                        :options="selectionTypeOptions"
                                        :placeholder="$t('deckOptionEditor.selectSelectionType')"
                                        @update:value="onSelectionTypeChange(option)"
                                    />
                                </n-form-item>

                                <!-- 根据选择机制显示不同配置 -->
                                <div v-if="option.selectionType && option.selectionType !== 'none'" class="selection-config">
                                    <!-- 职阶选择配置 -->
                                    <div v-if="option.selectionType === 'faction'" class="config-section">
                                        <n-form-item :label="$t('deckOptionEditor.selectFactionForSelection')">
                                            <n-select
                                                v-model:value="option.faction_select"
                                                :options="factionOptions"
                                                multiple
                                                :placeholder="$t('deckOptionEditor.selectFactions')"
                                                :render-tag="renderTag"
                                            />
                                        </n-form-item>
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

                                    <!-- 牌库大小选择配置 -->
                                    <div v-if="option.selectionType === 'deckSize'" class="config-section">
                                        <n-form-item :label="$t('deckOptionEditor.selectDeckSizes')">
                                            <n-select
                                                v-model:value="option.deck_size_select"
                                                :options="deckSizeOptions"
                                                multiple
                                                :placeholder="$t('deckOptionEditor.selectDeckSizes')"
                                                :render-tag="renderTag"
                                            />
                                        </n-form-item>
                                    </div>

                                    <!-- 高级属性选择配置 -->
                                    <div v-if="option.selectionType === 'advanced'" class="config-section">
                                        <div class="option-select-list">
                                            <div class="list-header">
                                                <n-text strong>{{ $t('deckOptionEditor.optionalAttributes') }}</n-text>
                                                <n-button size="tiny" type="primary" @click="addOptionSelectItem(option)">
                                                    <template #icon><span>➕</span></template>
                                                    {{ $t('deckOptionEditor.addItemOption') }}
                                                </n-button>
                                            </div>
                                            <div v-if="!option.option_select || option.option_select.length === 0" class="empty-list">
                                                <n-empty :description="$t('deckOptionEditor.noOptionalAttributes')" size="small" />
                                            </div>
                                            <div v-else class="option-items">
                                                <div v-for="(item, itemIndex) in option.option_select" :key="itemIndex" class="option-item">
                                                    <n-card size="small" class="item-card">
                                                        <template #header>
                                                            <div class="item-header">
                                                                <n-input v-model:value="item.id" :placeholder="$t('deckOptionEditor.itemId')" size="tiny" style="width: 100px" @blur="syncItemNameFromId(item)" />
                                                                <n-input v-model:value="item.name" :placeholder="$t('deckOptionEditor.itemNameRequired')" size="tiny" style="width: 140px" />
                                                                <n-button size="tiny" type="error" @click="removeOptionSelectItem(option, itemIndex)">{{ $t('deckOptionEditor.removeItem') }}</n-button>
                                                            </div>
                                                        </template>
                                                        <div class="item-content">
                                                            <!-- 高级属性选项标签 -->
                                                            <div class="advanced-option-tags">
                                                                <n-space size="small" wrap>
                                                                    <!-- 卡牌类型标签 -->
                                                                    <n-tag
                                                                        :type="hasAdvancedOptionValue(item, 'type') ? 'primary' : 'default'"
                                                                        :closable="false"
                                                                        checkable
                                                                        :checked="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.type || hasAdvancedOptionValue(item, 'type')"
                                                                        @update:checked="() => toggleAdvancedOptionTag(item, itemIndex, option, 'type')"
                                                                        style="cursor: pointer;"
                                                                    >
                                                                        {{ $t('deckOptionEditor.cardType') }}
                                                                        <n-text v-if="hasAdvancedOptionValue(item, 'type')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                                            ({{ item.type?.length || 0 }})
                                                                        </n-text>
                                                                    </n-tag>

                                                                    <!-- 职阶标签 -->
                                                                    <n-tag
                                                                        :type="hasAdvancedOptionValue(item, 'faction') ? 'success' : 'default'"
                                                                        :closable="false"
                                                                        checkable
                                                                        :checked="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.faction || hasAdvancedOptionValue(item, 'faction')"
                                                                        @update:checked="() => toggleAdvancedOptionTag(item, itemIndex, option, 'faction')"
                                                                        style="cursor: pointer;"
                                                                    >
                                                                        {{ $t('deckOptionEditor.faction') }}
                                                                        <n-text v-if="hasAdvancedOptionValue(item, 'faction')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                                            ({{ item.faction?.length || 0 }})
                                                                        </n-text>
                                                                    </n-tag>

                                                                    <!-- 特性标签 -->
                                                                    <n-tag
                                                                        :type="hasAdvancedOptionValue(item, 'trait') ? 'info' : 'default'"
                                                                        :closable="false"
                                                                        checkable
                                                                        :checked="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.trait || hasAdvancedOptionValue(item, 'trait')"
                                                                        @update:checked="() => toggleAdvancedOptionTag(item, itemIndex, option, 'trait')"
                                                                        style="cursor: pointer;"
                                                                    >
                                                                        {{ $t('deckOptionEditor.traits') }}
                                                                        <n-text v-if="hasAdvancedOptionValue(item, 'trait')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                                            ({{ item.trait?.length || 0 }})
                                                                        </n-text>
                                                                    </n-tag>

                                                                    <!-- 槽位标签 -->
                                                                    <n-tag
                                                                        :type="hasAdvancedOptionValue(item, 'slot') ? 'warning' : 'default'"
                                                                        :closable="false"
                                                                        checkable
                                                                        :checked="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.slot || hasAdvancedOptionValue(item, 'slot')"
                                                                        @update:checked="() => toggleAdvancedOptionTag(item, itemIndex, option, 'slot')"
                                                                        style="cursor: pointer;"
                                                                    >
                                                                        {{ $t('deckOptionEditor.slots') }}
                                                                        <n-text v-if="hasAdvancedOptionValue(item, 'slot')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                                            ({{ item.slot?.length || 0 }})
                                                                        </n-text>
                                                                    </n-tag>

                                                                    <!-- 使用标记标签 -->
                                                                    <n-tag
                                                                        :type="hasAdvancedOptionValue(item, 'uses') ? 'error' : 'default'"
                                                                        :closable="false"
                                                                        checkable
                                                                        :checked="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.uses || hasAdvancedOptionValue(item, 'uses')"
                                                                        @update:checked="() => toggleAdvancedOptionTag(item, itemIndex, option, 'uses')"
                                                                        style="cursor: pointer;"
                                                                    >
                                                                        {{ $t('deckOptionEditor.uses') }}
                                                                        <n-text v-if="hasAdvancedOptionValue(item, 'uses')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                                            ({{ item.uses?.length || 0 }})
                                                                        </n-text>
                                                                    </n-tag>

                                                                    <!-- 等级范围标签 -->
                                                                    <n-tag
                                                                        :type="hasAdvancedOptionValue(item, 'level') ? 'warning' : 'default'"
                                                                        :closable="false"
                                                                        checkable
                                                                        :checked="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.level || hasAdvancedOptionValue(item, 'level')"
                                                                        @update:checked="() => toggleAdvancedOptionTag(item, itemIndex, option, 'level')"
                                                                        style="cursor: pointer;"
                                                                    >
                                                                        {{ $t('deckOptionEditor.level') }}
                                                                        <n-text v-if="hasAdvancedOptionValue(item, 'level')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                                            ({{ item.level?.min || 0 }}-{{ item.level?.max || 5 }})
                                                                        </n-text>
                                                                    </n-tag>
                                                                </n-space>
                                                            </div>

                                                            <!-- 展开的高级选项配置 -->
                                                            <div v-if="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]" class="expanded-advanced-options">
                                                                <!-- 卡牌类型 -->
                                                                <div v-show="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.type" class="advanced-option-config">
                                                                    <n-form-item :label="$t('deckOptionEditor.cardType')">
                                                                        <n-select
                                                                            v-model:value="item.type"
                                                                            :options="cardTypeOptions"
                                                                            multiple
                                                                            :placeholder="$t('deckOptionEditor.selectCardTypes')"
                                                                            size="tiny"
                                                                            :render-tag="renderTag"
                                                                        />
                                                                    </n-form-item>
                                                                </div>

                                                                <!-- 职阶 -->
                                                                <div v-show="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.faction" class="advanced-option-config">
                                                                    <n-form-item :label="$t('deckOptionEditor.faction')">
                                                                        <n-select
                                                                            v-model:value="item.faction"
                                                                            :options="factionOptions"
                                                                            multiple
                                                                            :placeholder="$t('deckOptionEditor.selectFactions')"
                                                                            size="tiny"
                                                                            :render-tag="renderTag"
                                                                        />
                                                                    </n-form-item>
                                                                </div>

                                                                <!-- 特性 -->
                                                                <div v-show="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.trait" class="advanced-option-config">
                                                                    <n-form-item :label="$t('deckOptionEditor.traits')">
                                                                        <n-dynamic-tags v-model:value="item.trait" :placeholder="$t('deckOptionEditor.addTrait')" size="tiny" />
                                                                    </n-form-item>
                                                                </div>

                                                                <!-- 槽位 -->
                                                                <div v-show="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.slot" class="advanced-option-config">
                                                                    <n-form-item :label="$t('deckOptionEditor.slots')">
                                                                        <n-select
                                                                            v-model:value="item.slot"
                                                                            :options="slotOptions"
                                                                            multiple
                                                                            :placeholder="$t('deckOptionEditor.selectSlots')"
                                                                            size="tiny"
                                                                            :render-tag="renderTag"
                                                                        />
                                                                    </n-form-item>
                                                                </div>

                                                                <!-- 使用标记 -->
                                                                <div v-show="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.uses" class="advanced-option-config">
                                                                    <n-form-item :label="$t('deckOptionEditor.uses')">
                                                                        <n-select
                                                                            v-model:value="item.uses"
                                                                            :options="usesOptions"
                                                                            multiple
                                                                            :placeholder="$t('deckOptionEditor.selectUses')"
                                                                            size="tiny"
                                                                            :render-tag="renderTag"
                                                                        />
                                                                    </n-form-item>
                                                                </div>

                                                                <!-- 等级范围 -->
                                                                <div v-show="advancedOptionTags[`${option.id || 'new'}_advanced_${itemIndex}`]?.level" class="advanced-option-config">
                                                                    <n-form-item :label="$t('deckOptionEditor.level')">
                                                                        <n-space>
                                                                            <n-input-number
                                                                                v-model:value="item.level.min"
                                                                                :min="0"
                                                                                :max="10"
                                                                                :placeholder="$t('deckOptionEditor.minLevel')"
                                                                                size="tiny"
                                                                                style="width: 80px"
                                                                            />
                                                                            <n-text>-</n-text>
                                                                            <n-input-number
                                                                                v-model:value="item.level.max"
                                                                                :min="0"
                                                                                :max="10"
                                                                                :placeholder="$t('deckOptionEditor.maxLevel')"
                                                                                size="tiny"
                                                                                style="width: 80px"
                                                                            />
                                                                        </n-space>
                                                                    </n-form-item>
                                                                </div>
                                                            </div>
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
                                        <n-text strong>{{ $t('deckOptionEditor.basicFilters') }}</n-text>
                                    </n-divider>

                                    <!-- 基础条件标签 -->
                                    <div class="basic-condition-tags">
                                        <n-space size="small" wrap>
                                            <!-- 卡牌类型标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'type') ? 'primary' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.type || hasBasicConditionValue(option, 'type')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'type')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.cardType') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'type')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.type?.length || 0 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 职阶标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'faction') ? 'success' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.faction || hasBasicConditionValue(option, 'faction')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'faction')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.faction') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'faction')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.faction?.length || 0 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 特性标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'trait') ? 'info' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.trait || hasBasicConditionValue(option, 'trait')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'trait')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.traits') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'trait')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.trait?.length || 0 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 槽位标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'slot') ? 'warning' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.slot || hasBasicConditionValue(option, 'slot')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'slot')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.slots') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'slot')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.slot?.length || 0 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 使用标记标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'uses') ? 'error' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.uses || hasBasicConditionValue(option, 'uses')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'uses')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.uses') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'uses')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.uses?.length || 0 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 文本匹配标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'text') ? 'info' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.text || hasBasicConditionValue(option, 'text')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'text')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.textContains') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'text')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.text?.length || 0 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 等级范围标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'level') ? 'warning' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.level || hasBasicConditionValue(option, 'level')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'level')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.levelRange') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'level')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.level?.min || 0 }}-{{ option.level?.max || 5 }})
                                                </n-text>
                                            </n-tag>

                                            <!-- 数量限制标签 -->
                                            <n-tag
                                                :type="hasBasicConditionValue(option, 'limit') ? 'error' : 'default'"
                                                :closable="false"
                                                checkable
                                                :checked="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.limit || hasBasicConditionValue(option, 'limit')"
                                                @update:checked="() => toggleBasicConditionTag(option, 'limit')"
                                                style="cursor: pointer;"
                                            >
                                                {{ $t('deckOptionEditor.limit') }}
                                                <n-text v-if="hasBasicConditionValue(option, 'limit')" depth="1" style="font-size: 10px; margin-left: 4px; font-weight: 500;">
                                                    ({{ option.limit }})
                                                </n-text>
                                            </n-tag>
                                        </n-space>
                                    </div>

                                    <!-- 展开的条件配置 -->
                                    <div v-if="basicConditionTags[`${option.id || 'new'}_basic_tags`]" class="expanded-conditions">
                                        <!-- 卡牌类型 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.type" class="condition-config">
                                            <n-form-item :label="$t('deckOptionEditor.cardType')">
                                                <n-select
                                                    v-model:value="option.type"
                                                    :options="cardTypeOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectCardTypes')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>
                                        </div>

                                        <!-- 职阶 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.faction" class="condition-config">
                                            <n-form-item :label="$t('deckOptionEditor.faction')">
                                                <n-select
                                                    v-model:value="option.faction"
                                                    :options="factionOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectFactions')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>
                                        </div>

                                        <!-- 特性 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.trait" class="condition-config">
                                            <n-form-item :label="$t('deckOptionEditor.traits')">
                                                <n-dynamic-tags v-model:value="option.trait" :placeholder="$t('deckOptionEditor.addTrait')" />
                                            </n-form-item>
                                        </div>

                                        <!-- 槽位 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.slot" class="condition-config">
                                            <n-form-item :label="$t('deckOptionEditor.slots')">
                                                <n-select
                                                    v-model:value="option.slot"
                                                    :options="slotOptions"
                                                    multiple
                                                    :placeholder="$t('deckOptionEditor.selectSlots')"
                                                    :render-tag="renderTag"
                                                />
                                            </n-form-item>
                                        </div>

                                        <!-- 使用标记 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.uses" class="condition-config">
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

                                        <!-- 文本匹配 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.text" class="condition-config">
                                            <n-form-item :label="$t('deckOptionEditor.textContains')">
                                                <n-dynamic-tags v-model:value="option.text" :placeholder="$t('deckOptionEditor.addText')" />
                                            </n-form-item>
                                        </div>

                                        <!-- 等级范围 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.level" class="condition-config">
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

                                        <!-- 数量限制 -->
                                        <div v-show="basicConditionTags[`${option.id || 'new'}_basic_tags`]?.limit" class="condition-config">
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
                                </div>

                                <!-- 其他条件 -->
                                <n-divider class="section-divider">
                                    <n-text strong>{{ $t('deckOptionEditor.otherConditions') }}</n-text>
                                </n-divider>

                                <!-- 其他条件 -->
                                <div class="other-conditions">
                                    <!-- 条件开关组 -->
                                    <div class="condition-switches">
                                        <div class="switch-item">
                                            <n-switch v-model:value="option.not" size="small" :class="option.not ? 'switch-on' : 'switch-off'">
                                                <template #checked>{{ $t('deckOptionEditor.negativeCondition') }}</template>
                                                <template #unchecked>{{ $t('deckOptionEditor.negativeCondition') }}</template>
                                            </n-switch>
                                        </div>
                                        <div class="switch-item">
                                            <n-switch v-model:value="atLeastEnabled" size="small" :class="atLeastEnabled ? 'switch-on' : 'switch-off'">
                                                <template #checked>{{ $t('deckOptionEditor.atLeastCondition') }}</template>
                                                <template #unchecked>{{ $t('deckOptionEditor.atLeastCondition') }}</template>
                                            </n-switch>
                                        </div>
                                    </div>

                                    <!-- 至少条件配置 -->
                                    <div v-if="atLeastEnabled" class="atleast-config">
                                        <!-- 最少数量 -->
                                        <div class="atleast-row">
                                            <label class="atleast-label">{{ $t('deckOptionEditor.minimumCount') }}</label>
                                            <n-input-number
                                                v-model:value="option.atleast.min"
                                                :min="0"
                                                :max="50"
                                                :placeholder="$t('deckOptionEditor.minimumCount')"
                                                size="small"
                                                style="width: 70px"
                                            />
                                        </div>

                                        <!-- 条件类型 -->
                                        <div class="atleast-row">
                                            <label class="atleast-label">{{ $t('deckOptionEditor.conditionType') }}</label>
                                            <n-radio-group v-model:value="atleastType" size="small" class="atleast-radio-group">
                                                <n-radio value="factions" class="compact-radio">{{ $t('deckOptionEditor.factionCount') }}</n-radio>
                                                <n-radio value="types" class="compact-radio">{{ $t('deckOptionEditor.typeCount') }}</n-radio>
                                            </n-radio-group>
                                        </div>

                                        <!-- 满足数量 -->
                                        <div class="atleast-row">
                                            <label class="atleast-label">{{ $t('deckOptionEditor.satisfiedCount') }}</label>
                                            <n-input-number
                                                :value="getAtleastConditionValue()"
                                                :min="0"
                                                :max="atleastType === 'factions' ? 6 : 3"
                                                :placeholder="$t('deckOptionEditor.satisfiedCount')"
                                                size="small"
                                                style="width: 70px"
                                                @update:value="setAtleastConditionValue"
                                            />
                                        </div>
                                    </div>
                                </div>
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
        factions?: number;
        types?: number;
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
const atleastType = ref<'factions' | 'types'>('factions');
const editingBackup = ref<DeckOption | null>(null);
const isSavingFromEditor = ref(false); // 添加标志防止保存时触发重新加载

// 折叠面板状态
const expandedSections = ref<string[]>([]);

// 牌组构建顺序提示显示状态
const showOrderNotice = ref(false);

// 基础条件标签状态
const basicConditionTags = ref<Record<string, boolean>>({});

// 高级属性选项标签状态
const advancedOptionTags = ref<Record<string, boolean>>({});

// JSON预览相关
const finalJsonPreview = ref('');

// 选项配置 - 使用多语言
const cardTypeOptions = computed(() => [
    { label: t('deckOptionEditor.cardTypes.asset'), value: 'asset' },
    { label: t('deckOptionEditor.cardTypes.event'), value: 'event' },
    { label: t('deckOptionEditor.cardTypes.skill'), value: 'skill' }
]);

const factionOptions = computed(() => [
    { label: t('deckOptionEditor.factions.guardian'), value: 'guardian' },
    { label: t('deckOptionEditor.factions.seeker'), value: 'seeker' },
    { label: t('deckOptionEditor.factions.rogue'), value: 'rogue' },
    { label: t('deckOptionEditor.factions.mystic'), value: 'mystic' },
    { label: t('deckOptionEditor.factions.survivor'), value: 'survivor' },
    { label: t('deckOptionEditor.factions.neutral'), value: 'neutral' }
]);

const slotOptions = computed(() => [
    { label: t('deckOptionEditor.slotOptions.hand'), value: 'hand' },
    { label: t('deckOptionEditor.slotOptions.arcane'), value: 'arcane' },
    { label: t('deckOptionEditor.slotOptions.accessory'), value: 'accessory' },
    { label: t('deckOptionEditor.slotOptions.body'), value: 'body' },
    { label: t('deckOptionEditor.slotOptions.ally'), value: 'ally' },
    { label: t('deckOptionEditor.slotOptions.tarot'), value: 'tarot' },
    { label: t('deckOptionEditor.slotOptions.sanity'), value: 'sanity' },
    { label: t('deckOptionEditor.slotOptions.health'), value: 'health' }
]);

const usesOptions = computed(() => [
    { label: t('deckOptionEditor.usesOptions.charge'), value: 'charge' },
    { label: t('deckOptionEditor.usesOptions.ammo'), value: 'ammo' },
    { label: t('deckOptionEditor.usesOptions.supply'), value: 'supply' },
    { label: t('deckOptionEditor.usesOptions.secret'), value: 'secret' },
    { label: t('deckOptionEditor.usesOptions.resource'), value: 'resource' },
    { label: t('deckOptionEditor.usesOptions.evidence'), value: 'evidence' },
    { label: t('deckOptionEditor.usesOptions.offering'), value: 'offering' }
]);

const deckSizeOptions = computed(() => [
    { label: t('deckOptionEditor.deckSizes.20'), value: '20' },
    { label: t('deckOptionEditor.deckSizes.25'), value: '25' },
    { label: t('deckOptionEditor.deckSizes.30'), value: '30' },
    { label: t('deckOptionEditor.deckSizes.35'), value: '35' },
    { label: t('deckOptionEditor.deckSizes.40'), value: '40' },
    { label: t('deckOptionEditor.deckSizes.50'), value: '50' }
]);

const selectionTypeOptions = computed(() => [
    { label: t('deckOptionEditor.noneSelection'), value: 'none' },
    { label: t('deckOptionEditor.selectionTypeNames.faction'), value: 'faction' },
    { label: t('deckOptionEditor.selectionTypeNames.deckSize'), value: 'deckSize' },
    { label: t('deckOptionEditor.selectionTypeNames.advanced'), value: 'advanced' }
]);

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

    // 根据当前语言自动设置name字段的值
    if (option.selectionType === 'faction') {
        option.name = t('deckOptionEditor.selectionTypeNames.faction');
    } else if (option.selectionType === 'deckSize') {
        option.name = t('deckOptionEditor.selectionTypeNames.deckSize');
    } else if (option.selectionType === 'advanced') {
        // 高级属性选择保持用户自定义名称，如果没有则设置默认值
        if (!option.name || option.name === '') {
            option.name = t('deckOptionEditor.defaultAdvancedName');
        }
    } else if (option.selectionType === 'none' || !option.selectionType) {
        // 无选择机制时，如果名称是自动设置的名称，则清空
        const factionName = t('deckOptionEditor.selectionTypeNames.faction');
        const deckSizeName = t('deckOptionEditor.selectionTypeNames.deckSize');
        const defaultAdvancedName = t('deckOptionEditor.defaultAdvancedName');
        if (option.name === factionName || option.name === deckSizeName || option.name === defaultAdvancedName) {
            option.name = option.id || '';
        }
    }
};

// 添加高级属性选择项
const addOptionSelectItem = (option: DeckOption) => {
    if (!option.option_select) {
        option.option_select = [];
    }

    const newIndex = option.option_select.length + 1;
    const newItem: OptionSelectItem = {
        id: `option_${newIndex}`,
        name: t('deckOptionEditor.newOptionItem', { index: newIndex }),
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
        const slotOption = slotOptions.value.find(opt => opt.value === slot);
        return slotOption ? slotOption.label.split(' ')[0] : slot;
    }).join(', ');
};

// 格式化使用标记显示
const formatUsesDisplay = (uses: string[]) => {
    return uses.map(use => {
        const useOption = usesOptions.value.find(opt => opt.value === use);
        return useOption ? useOption.label.split(' ')[0] : use;
    }).join(', ');
};

// 检查基础条件是否有值
const hasBasicConditionValue = (option: DeckOption, conditionType: string): boolean => {
    switch (conditionType) {
        case 'type':
            return option.type && option.type.length > 0;
        case 'faction':
            return option.faction && option.faction.length > 0;
        case 'trait':
            return option.trait && option.trait.length > 0;
        case 'slot':
            return option.slot && option.slot.length > 0;
        case 'uses':
            return option.uses && option.uses.length > 0;
        case 'text':
            return option.text && option.text.length > 0;
        case 'level':
            return option.level && (option.level.min !== 0 || option.level.max !== 5);
        case 'limit':
            return option.limit !== null && option.limit !== undefined;
        default:
            return false;
    }
};

// 初始化基础条件标签状态
const initializeBasicConditionTags = (option: DeckOption) => {
    const optionKey = `${option.id || 'new'}_basic_tags`;
    if (!basicConditionTags.value[optionKey]) {
        basicConditionTags.value[optionKey] = {
            type: hasBasicConditionValue(option, 'type'),
            faction: hasBasicConditionValue(option, 'faction'),
            trait: hasBasicConditionValue(option, 'trait'),
            slot: hasBasicConditionValue(option, 'slot'),
            uses: hasBasicConditionValue(option, 'uses'),
            text: hasBasicConditionValue(option, 'text'),
            level: hasBasicConditionValue(option, 'level'),
            limit: hasBasicConditionValue(option, 'limit')
        };
    }
};

// 切换基础条件标签
const toggleBasicConditionTag = (option: DeckOption, conditionType: string) => {
    const optionKey = `${option.id || 'new'}_basic_tags`;
    if (!basicConditionTags.value[optionKey]) {
        initializeBasicConditionTags(option);
    }
    basicConditionTags.value[optionKey][conditionType] = !basicConditionTags.value[optionKey][conditionType];
};

// 检查高级属性选项是否有值
const hasAdvancedOptionValue = (item: OptionSelectItem, valueType: string): boolean => {
    switch (valueType) {
        case 'type':
            return item.type && item.type.length > 0;
        case 'faction':
            return item.faction && item.faction.length > 0;
        case 'trait':
            return item.trait && item.trait.length > 0;
        case 'slot':
            return item.slot && item.slot.length > 0;
        case 'uses':
            return item.uses && item.uses.length > 0;
        case 'level':
            return item.level && (item.level.min !== 0 || item.level.max !== 5);
        default:
            return false;
    }
};

// 初始化高级属性选项标签状态
const initializeAdvancedOptionTags = (item: OptionSelectItem, itemIndex: number, option: DeckOption) => {
    const optionKey = `${option.id || 'new'}_advanced_${itemIndex}`;
    if (!advancedOptionTags.value[optionKey]) {
        advancedOptionTags.value[optionKey] = {
            type: hasAdvancedOptionValue(item, 'type'),
            faction: hasAdvancedOptionValue(item, 'faction'),
            trait: hasAdvancedOptionValue(item, 'trait'),
            slot: hasAdvancedOptionValue(item, 'slot'),
            uses: hasAdvancedOptionValue(item, 'uses'),
            level: hasAdvancedOptionValue(item, 'level')
        };
    }
};

// 切换高级属性选项标签
const toggleAdvancedOptionTag = (item: OptionSelectItem, itemIndex: number, option: DeckOption, valueType: string) => {
    const optionKey = `${option.id || 'new'}_advanced_${itemIndex}`;
    if (!advancedOptionTags.value[optionKey]) {
        initializeAdvancedOptionTags(item, itemIndex, option);
    }
    advancedOptionTags.value[optionKey][valueType] = !advancedOptionTags.value[optionKey][valueType];
};

// 获取至少条件的值
const getAtleastConditionValue = (): number => {
    if (editingIndex.value >= 0) {
        const option = deckOptions.value[editingIndex.value];
        if (option.atleast) {
            return atleastType.value === 'factions' ? (option.atleast.factions || 0) : (option.atleast.types || 0);
        }
    }
    return 0;
};

// 设置至少条件的值
const setAtleastConditionValue = (value: number) => {
    if (editingIndex.value >= 0) {
        const option = deckOptions.value[editingIndex.value];
        if (!option.atleast) {
            option.atleast = { min: 1 };
        }

        if (atleastType.value === 'factions') {
            option.atleast.factions = value;
            delete option.atleast.types; // 清除另一个字段
        } else {
            option.atleast.types = value;
            delete option.atleast.factions; // 清除另一个字段
        }
    }
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

    // 初始化至少条件类型
    if (option.atleast) {
        if (option.atleast.factions !== undefined) {
            atleastType.value = 'factions';
        } else if (option.atleast.types !== undefined) {
            atleastType.value = 'types';
        }
    }
};

// 验证选项数据
const validateOption = (option: DeckOption): { isValid: boolean; message?: string } => {
    // 验证基础名称
    if (!option.name || option.name.trim() === '') {
        return { isValid: false, message: t('deckOptionEditor.validation.nameRequired') };
    }

    // 验证高级属性选择
    if (option.selectionType === 'advanced' && option.option_select) {
        for (const item of option.option_select) {
            if (!item.name || item.name.trim() === '') {
                return {
                    isValid: false,
                    message: t('deckOptionEditor.validation.itemNameRequired', { itemId: item.id })
                };
            }
        }
    }

    return { isValid: true };
};

// 保存选项
const saveOption = (index: number) => {
    if (index >= 0 && index < deckOptions.value.length) {
        const option = deckOptions.value[index];

        // 验证选项数据
        const validation = validateOption(option);
        if (!validation.isValid) {
            message.error(validation.message);
            return;
        }

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
            cleaned.name = t('deckOptionEditor.selectionTypeNames.faction');
            if (option.faction_select && option.faction_select.length > 0) {
                cleaned.faction_select = option.faction_select;
            }
            if (option.level && (option.level.min !== 0 || option.level.max !== 5)) {
                cleaned.level = { ...option.level };
            }
        } else if (option.selectionType === 'deckSize') {
            cleaned.name = t('deckOptionEditor.selectionTypeNames.deckSize');
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
            cleaned.name = t('deckOptionEditor.selectionTypeNames.faction');
            if (option.faction_select && option.faction_select.length > 0) {
                cleaned.faction_select = option.faction_select;
            }
            if (option.level && (option.level.min !== 0 || option.level.max !== 5)) {
                cleaned.level = { ...option.level };
            }
        } else if (option.selectionType === 'deckSize') {
            cleaned.name = t('deckOptionEditor.selectionTypeNames.deckSize');
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
        const factionOption = factionOptions.value.find(opt => opt.value === faction);
        return factionOption ? factionOption.label : faction;
    }).join(', ');
};

// 格式化类型显示
const formatTypeDisplay = (types: string[]) => {
    return types.map(type => {
        const typeOption = cardTypeOptions.value.find(opt => opt.value === type);
        return typeOption ? typeOption.label : type;
    }).join(', ');
};

// 切换牌组构建顺序提示显示状态
const toggleOrderNotice = () => {
    showOrderNotice.value = !showOrderNotice.value;
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

            // 检测选择机制类型并设置正确的名称
            if (option.faction_select && option.faction_select.length > 0) {
                loadedOption.selectionType = 'faction';
                // 强制使用当前语言的名称，覆盖原来的name
                loadedOption.name = t('deckOptionEditor.selectionTypeNames.faction');
            } else if (option.deck_size_select && option.deck_size_select.length > 0) {
                loadedOption.selectionType = 'deckSize';
                // 强制使用当前语言的名称，覆盖原来的name
                loadedOption.name = t('deckOptionEditor.selectionTypeNames.deckSize');
            } else if (option.option_select && option.option_select.length > 0) {
                loadedOption.selectionType = 'advanced';
                // 高级属性选择：如果原来有自定义名称则保留，否则使用默认名称
                if (!option.name || option.name.trim() === '') {
                    loadedOption.name = t('deckOptionEditor.defaultAdvancedName');
                } else {
                    // 保持原来的自定义名称
                    loadedOption.name = option.name;
                }
                loadedOption.option_select = option.option_select.map((item: any) => ({
                    id: item.id || `item_${index + 1}`,
                    name: item.name || item.id || t('deckOptionEditor.newOptionItem', { index: index + 1 }),
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

    // 初始化所有选项的标签状态
    deckOptions.value.forEach(option => {
        initializeBasicConditionTags(option);

        // 初始化高级属性选项的标签状态
        if (option.option_select) {
            option.option_select.forEach((item, itemIndex) => {
                initializeAdvancedOptionTags(item, itemIndex, option);
            });
        }
    });

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
                [atleastType.value]: 0
            };
        } else if (!option.atleast[atleastType.value]) {
            // 如果当前类型没有值，初始化为0
            option.atleast[atleastType.value] = 0;
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
    width: 100%;
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
    max-height: 500px;
    overflow-y: auto;
    width: 100%;
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
    gap: 6px;
    align-items: center;
    flex-wrap: wrap;
    width: 100%;
}

.item-header :deep(.n-input) {
    flex: 1;
}

.item-content {
    padding: 8px 16px 12px;
}

.item-content :deep(.n-form-item) {
    margin-bottom: 8px;
}

.item-content :deep(.n-form-item .n-form-item-label) {
    text-align: left;
    padding-right: 8px;
}

.item-content :deep(.n-form-item .n-form-item-blank) {
    flex: 1;
}

.item-content :deep(.n-form-item:last-child) {
    margin-bottom: 0;
}



/* 基础条件样式 */
.basic-conditions {
    margin: 20px 0;
}

/* 基础条件标签样式 */
.basic-condition-tags {
    margin-bottom: 16px;
}

.basic-condition-tags :deep(.n-tag) {
    transition: all 0.2s ease;
}

.basic-condition-tags :deep(.n-tag:hover) {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 展开条件配置样式 */
.expanded-conditions {
    margin-top: 16px;
    padding: 16px;
    background: rgba(248, 250, 252, 0.5);
    border-radius: 8px;
    border: 1px solid rgba(226, 232, 240, 0.6);
}

.condition-config {
    margin-bottom: 16px;
}

.condition-config:last-child {
    margin-bottom: 0;
}

/* 高级属性选项标签样式 */
.advanced-option-tags {
    margin-bottom: 12px;
}

.advanced-option-tags :deep(.n-tag) {
    transition: all 0.2s ease;
    font-size: 11px;
    padding: 1px 6px;
    margin: 2px;
}

.advanced-option-tags :deep(.n-tag:hover) {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.advanced-option-tags :deep(.n-text) {
    font-size: 10px;
}

/* 展开高级选项配置样式 */
.expanded-advanced-options {
    margin-top: 16px;
    padding: 16px;
    background: rgba(248, 250, 252, 0.5);
    border-radius: 8px;
    border: 1px solid rgba(226, 232, 240, 0.6);
}

.advanced-option-config {
    margin-bottom: 16px;
}

.advanced-option-config:last-child {
    margin-bottom: 0;
}

.section-divider {
    margin: 24px 0 16px;
}

.section-divider :deep(.n-divider__title) {
    font-weight: 600;
    color: #667eea;
}

/* 其他条件样式 */
.other-conditions {
    margin: 20px 0;
    padding: 12px;
    background: rgba(248, 250, 252, 0.6);
    border-radius: 6px;
    border: 1px solid rgba(226, 232, 240, 0.6);
    width: 100%;
    box-sizing: border-box;
}

/* 条件开关组样式 */
.condition-switches {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(226, 232, 240, 0.4);
    width: 100%;
}

.switch-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.switch-item :deep(.n-switch) {
    flex-shrink: 0;
}

.switch-item :deep(.n-switch__unchecked-text),
.switch-item :deep(.n-switch__checked-text) {
    font-size: 11px;
    padding: 0 4px;
}

/* 至少条件配置样式 */
.atleast-config {
    margin-top: 12px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 4px;
    border: 1px solid rgba(102, 126, 234, 0.2);
    width: 100%;
    box-sizing: border-box;
}

.atleast-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    width: 100%;
    gap: 8px;
}

.atleast-row:last-child {
    margin-bottom: 0;
}

.atleast-label {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
    margin: 0;
    flex-shrink: 0;
    min-width: 50px;
}

.atleast-radio-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
    width: 70px;
    flex-shrink: 0;
}

.compact-radio {
    display: flex;
    align-items: center;
    min-height: 16px;
}

.compact-radio :deep(.n-radio__dot) {
    width: 12px;
    height: 12px;
    margin: 0;
}

.compact-radio :deep(.n-radio__label) {
    font-size: 10px;
    margin-left: 4px;
    line-height: 1;
}

/* 开关样式 - 使用动态class控制 */
.option-editor :deep(.switch-off .n-switch__rail) {
    background-color: #cbd5e0 !important;
    border: 1px solid #a0aec0;
}

.option-editor :deep(.switch-on .n-switch__rail) {
    background-color: #3182ce !important;
    border: 1px solid #2c5282;
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

/* 牌组构建顺序提示样式 */
.deck-building-order-notice {
    margin-bottom: 16px;
}

.deck-building-order-notice :deep(.n-button) {
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.deck-building-order-notice :deep(.n-button:hover) {
    background: rgba(245, 158, 11, 0.1);
}

.deck-building-order-notice :deep(.n-alert) {
    border-radius: 8px;
    border-left: 4px solid #f59e0b;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(217, 119, 6, 0.05) 100%);
    margin-top: 0;
}

.deck-building-order-notice :deep(.n-alert__header) {
    font-weight: 600;
    font-size: 13px;
}

.notice-content p {
    margin: 8px 0;
    line-height: 1.4;
}

.example-section {
    background: rgba(255, 255, 255, 0.6);
    padding: 12px;
    border-radius: 6px;
    border: 1px solid rgba(245, 158, 11, 0.2);
}

.example-section ol {
    color: #4b5563;
}

.example-section li {
    margin-bottom: 2px;
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

    /* 在窄屏下保持垂直布局 */
    .condition-switches {
        flex-direction: column;
        gap: 6px;
        padding: 6px 0;
    }

    .atleast-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
        margin-bottom: 6px;
    }

    .atleast-label {
        font-size: 10px;
        min-width: auto;
    }

    .atleast-radio-group {
        width: 100%;
        flex-direction: row;
        justify-content: space-between;
        gap: 8px;
    }

    .other-conditions {
        padding: 8px;
    }

    .atleast-config {
        padding: 6px;
    }
}
</style>
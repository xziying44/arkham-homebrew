export interface FieldOption {
  label: string;
  value: string | number | null;
}

export interface ShowCondition {
  field: string;  // Field name dependency
  value: any;     // Show when field value equals this value
  operator?: 'equals' | 'not-equals' | 'includes' | 'not-includes';  // Comparison operator, defaults to equals
}

// Add new field types in FormField interface
export interface FormField {
  key: string;
  name: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'multi-select' | 'string-array' | 'image' | 'encounter-group-select' | 'class-selector' | 'slot-selector' | 'stat-badge' | 'cost-coin' | 'level-ring'; // Add new type
  layout?: 'full' | 'half' | 'third' | 'quarter';
  min?: number;
  max?: number;
  rows?: number;
  maxlength?: number;
  options?: FieldOption[];
  showCondition?: ShowCondition;
  index?: number;
  maxSize?: number;
  defaultValue?: any;
  helpText?: string;
  statType?: 'health' | 'horror'; // For stat-badge type
}

export interface CardTypeConfig {
  fields: FormField[];
  field_type_en?: string; // English display name
  field_type_display?: string; // Display name with emoji
  card_category?: 'player' | 'encounter'; // Card category
}

// Help text
const compoundNumbersTip = `Input format:
• Number: e.g. 8
• Variable number: e.g. 2<调查员>
• Special values: - / X / ?

Support: numbers, number<调查员>, special symbols (-/X/?).
`;

const bodyTip = `Input format:
● 【】 or {{}} for bold text, e.g.: 【Investigation】, {{Investigation}}
● {} for traits, e.g.: {Ally}
● [] for flavor text, e.g.: [This is flavor text...]
You can use more advanced flavor tags to customize functionality:
 <flavor align="left" flex="false" padding="0" quote="false">xxx</flavor>
●The <upg> tag will automatically generate a TTS checkbox script when used in custom cards.

<fullname> represents the name of this card.

Available icon tags:
🏅 <*> unique
⭕ <rea> reaction
➡️ <act> action
⚡ <fre> free
💀 <sku> skull
👤 <cul> cultist
📜 <tab> tablet
👹 <mon> elder
🐙 <ten> tentacle
⭐ <eld> seal
👊 <com> fist
📚 <int> book
🦶 <agi> foot
🧠 <wil> brain
❓ <\?> ?
🔵 <bul> dot
🌑 <cur> curse
🌟 <ble> blessing
❄️ <frost> frost
🕵️ <per> investigator
🚶 <rog> rogue
🏕️ <sur> survivor
🛡️ <gua> guardian
🧘 <mys> mystic
🔍 <see> seeker

Special tags:
<br> line break
<hr> horizontal line
<p></p> paragraph
<center>Centered text</center>
<size "2"> means the font size increases by 2 relative levels.

Support direct use of emoji or corresponding tag format
`;

const nameTip = `Support unique marker: 🏅 or <独特>`;

const victoryTip = `Only one of Victory Points or Victory Text can be filled in. Victory Text takes precedence over Victory Points.`

const externalImageFields: FormField[] = [
  {
    key: 'use_external_image',
    name: '🔄 Replace with External Image',
    type: 'select',
    layout: 'half',
    defaultValue: false,
    options: [
      { label: '❌ Do Not Use', value: 0 },
      { label: '✅ Use External Image', value: 1 }
    ]
  },
  {
    key: 'external_image',
    name: '🖼️ External Card Image',
    type: 'image',
    layout: 'half',
    maxSize: 50 * 1024 * 1024,
    showCondition: {
      field: 'use_external_image',
      value: 1
    }
  }
];

export const cardTypeConfigs: Record<string, CardTypeConfig> = {
  '支援卡': {
    field_type_en: 'Asset Card',
    field_type_display: '📦 Asset Card',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 Subtitle',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '⚔️ Class',
        type: 'class-selector',
        layout: 'full'
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ Weakness Type',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 Weakness', value: '弱点' },
          { label: '📋 Basic Weakness', value: '基础弱点' }
        ]
      },
      {
        key: 'health',
        name: '❤️ Health',
        type: 'stat-badge',
        statType: 'health',
        layout: 'half'
      },
      {
        key: 'horror',
        name: '🧠 Sanity',
        type: 'stat-badge',
        statType: 'horror',
        layout: 'half'
      },
      {
        key: 'level',
        name: '⭐ Card Level',
        type: 'level-ring',
        layout: 'half',
        defaultValue: -1
      },
      {
        key: 'cost',
        name: '💰 Cost',
        type: 'cost-coin',
        layout: 'half',
        defaultValue: -1
      },
      {
        key: 'slots',
        name: '🎒 Slot',
        type: 'slot-selector',
        layout: 'half'
      },
      {
        key: 'slots2',
        name: '🎒 Second Slot',
        type: 'slot-selector',
        layout: 'half'
      },
      {
        key: 'submit_icon',
        name: '🎯 Skill Icons',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🧠 Willpower', value: '意志' },
          { label: '👊 Combat', value: '战力' },
          { label: '🦶 Agility', value: '敏捷' },
          { label: '📚 Intellect', value: '智力' },
          { label: '❓ Wild', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        showCondition: {
          field: 'class',
          value: '中立'
        },
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '调查员小卡': {
    field_type_en: 'Investigator Mini',
    field_type_display: '🧩 Investigator Mini',
    card_category: 'player',
    fields: [
      {
        key: 'is_back',
        name: '📃 Front/Back',
        type: 'select',
        layout: 'half',
        defaultValue: false,
        options: [
          { label: '🔼 Front', value: false },
          { label: '🔽 Back', value: true },
        ]
      },
      {
        key: 'image_filter',
        name: '🎨 Filter Style',
        type: 'select',
        layout: 'half',
        defaultValue: 'normal',
        options: [
          { label: '🌈 Normal', value: 'normal' },
          { label: '⚫ Grayscale', value: 'grayscale' }
        ]
      },
      {
        key: 'share_front_picture',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🔗 Share Front Image & Settings',
        type: 'select',
        layout: 'half',
        defaultValue: 1,
        options: [
          { label: '✅ Share', value: 1 },
          { label: "❌ Don't Share", value: 0 }
        ]
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'share_front_picture',
          value: 1,
          operator: 'not-equals'
        },
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024,
      },
      // Investigator mini is pure image, no external image replacement
    ]
  },
  '事件卡': {
    field_type_en: 'Event Card',
    field_type_display: '⚡ Event Card',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'full',
        helpText: nameTip
      },
      {
        key: 'class',
        name: '⚔️ Class',
        type: 'class-selector',
        layout: 'full'
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ Weakness Type',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 Weakness', value: '弱点' },
          { label: '📋 Basic Weakness', value: '基础弱点' }
        ]
      },
      {
        key: 'level',
        name: '⭐ Card Level',
        type: 'level-ring',
        layout: 'half',
        defaultValue: -1
      },
      {
        key: 'cost',
        name: '💰 Cost',
        type: 'cost-coin',
        layout: 'half',
        defaultValue: -1
      },
      {
        key: 'submit_icon',
        name: '🎯 Skill Icons',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🧠 Willpower', value: '意志' },
          { label: '👊 Combat', value: '战力' },
          { label: '🦶 Agility', value: '敏捷' },
          { label: '📚 Intellect', value: '智力' },
          { label: '❓ Wild', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '技能卡': {
    field_type_en: 'Skill Card',
    field_type_display: '🎯 Skill Card',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'full',
        helpText: nameTip
      },
      {
        key: 'class',
        name: '⚔️ Class',
        type: 'class-selector',
        layout: 'full'
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ Weakness Type',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 Weakness', value: '弱点' },
          { label: '📋 Basic Weakness', value: '基础弱点' }
        ]
      },
      {
        key: 'level',
        name: '⭐ Card Level',
        type: 'level-ring',
        layout: 'full',
        defaultValue: -1
      },
      {
        key: 'submit_icon',
        name: '🎯 Skill Icons',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🧠 Willpower', value: '意志' },
          { label: '👊 Combat', value: '战力' },
          { label: '🦶 Agility', value: '敏捷' },
          { label: '📚 Intellect', value: '智力' },
          { label: '❓ Wild', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '调查员': {
    field_type_en: 'Investigator',
    field_type_display: '👤 Investigator',
    card_category: 'player',
    fields: [
      {
        key: 'subtype',
        name: '⚙️ Subtype',
        type: 'select',
        layout: 'full',
        defaultValue: '默认',
        options: [
          { label: '📛 Default', value: '默认' },
          { label: '🔀 Parallel', value: '平行' }
        ]
      },
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 Subtitle',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '⚔️ Class',
        type: 'class-selector',
        layout: 'full'
      },
      {
        key: 'attribute',
        index: 0,
        name: '🧠 Willpower',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 19
      },
      {
        key: 'attribute',
        index: 1,
        name: '📚 Intellect',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 19
      },
      {
        key: 'attribute',
        index: 2,
        name: '⚔️ Combat',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 19
      },
      {
        key: 'attribute',
        index: 3,
        name: '⚡ Agility',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 19
      },
      {
        key: 'health',
        name: '❤️ Health',
        type: 'stat-badge',
        statType: 'health',
        layout: 'half'
      },
      {
        key: 'horror',
        name: '🧠 Sanity',
        type: 'stat-badge',
        statType: 'horror',
        layout: 'half'
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '调查员背面': {
    field_type_en: 'Investigator Back',
    field_type_display: '🔄 Investigator Back',
    card_category: 'player',
    fields: [
      {
        key: 'subtype',
        name: '⚙️ Subtype',
        type: 'select',
        layout: 'full',
        defaultValue: '默认',
        options: [
          { label: '📛 Default', value: '默认' },
          { label: '🔀 Parallel', value: '平行' }
        ]
      },
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 Subtitle',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '⚔️ Class',
        type: 'class-selector',
        layout: 'full'
      },
      {
        key: 'card_back.size',
        name: '🔢 Deck Size',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 99
      },
      {
        key: 'card_back.option',
        name: '🎯 Deck Building Options',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'card_back.requirement',
        name: '📋 Deck Building Requirements',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'card_back.other',
        name: '⚙️ Other Requirements',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'card_back.story',
        name: '📖 Story Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '定制卡': {
    field_type_en: 'Custom Card',
    field_type_display: '🎨 Custom Card',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      ...externalImageFields
    ]
  },
  '故事卡': {
    field_type_en: 'Story Card',
    field_type_display: '📖 Story Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      ...externalImageFields
    ]
  },
  '诡计卡': {
    field_type_en: 'Treachery Card',
    field_type_display: '🎭 Treachery Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'class',
        name: '🃏 Type',
        type: 'select',
        layout: 'half',
        defaultValue: '',
        options: [
          { label: '🔮 Encounter', value: "" },
          { label: '💀 Weakness', value: '弱点' },
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ Weakness Type',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 Weakness', value: '弱点' },
          { label: '📋 Basic Weakness', value: '基础弱点' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '敌人卡': {
    field_type_en: 'Enemy Card',
    field_type_display: '👹 Enemy Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 Subtitle',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '🃏 Type',
        type: 'select',
        layout: 'full',
        defaultValue: '',
        options: [
          { label: '🔮 Encounter', value: "" },
          { label: '💀 Weakness', value: '弱点' },
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ Weakness Type',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 Weakness', value: '弱点' },
          { label: '📋 Basic Weakness', value: '基础弱点' }
        ]
      },
      {
        key: 'attack',
        name: '⚔️ Fight',
        type: 'text',
        layout: 'third',
        helpText: compoundNumbersTip
      },
      {
        key: 'enemy_health',
        name: '❤️ Health',
        type: 'text',
        layout: 'third',
        helpText: compoundNumbersTip
      },
      {
        key: 'evade',
        name: '🏃 Evade',
        type: 'text',
        layout: 'third',
        helpText: compoundNumbersTip
      },
      {
        key: 'enemy_damage',
        name: '💔 Damage',
        type: 'select',
        layout: 'half',
        options: [
          { label: '💔 Damage-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `💔 Damage-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'enemy_damage_horror',
        name: '😱 Horror',
        type: 'select',
        layout: 'half',
        options: [
          { label: '😱 Horror-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `😱 Horror-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '地点卡': {
    field_type_en: 'Location Card',
    field_type_display: '📍 Location Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 Subtitle',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'location_type',
        name: '🗺️ Location Type',
        type: 'select',
        layout: 'half',
        options: [
          { label: '👁️ Revealed', value: '已揭示' },
          { label: '❓ Unrevealed', value: '未揭示' },
        ]
      },
      {
        key: 'location_icon',
        name: '📍 Location Icon',
        type: 'select',
        layout: 'half',
        options: [
          { label: 'Diamond', value: '绿菱' },
          { label: 'Hourglass', value: '暗红漏斗' },
          { label: 'Heart', value: '橙心' },
          { label: 'Blob', value: '浅褐水滴' },
          { label: 'Star', value: '深紫星' },
          { label: 'Equals', value: '深绿斜二' },
          { label: 'T', value: '深蓝T' },
          { label: 'Crescent', value: '紫月' },
          { label: 'Plus', value: '红十' },
          { label: 'Square', value: '红方' },
          { label: 'Triangle', value: '蓝三角' },
          { label: 'Wave', value: '褐扭' },
          { label: '3circles', value: '青花' },
          { label: 'Circle', value: '黄圆' },
          { label: 'Spades', value: '粉桃' },
        ]
      },
      {
        key: 'location_link',
        name: '🔗 Connected Location Icons',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: 'Diamond', value: '绿菱' },
          { label: 'Hourglass', value: '暗红漏斗' },
          { label: 'Heart', value: '橙心' },
          { label: 'Blob', value: '浅褐水滴' },
          { label: 'Star', value: '深紫星' },
          { label: 'Equals', value: '深绿斜二' },
          { label: 'T', value: '深蓝T' },
          { label: 'Crescent', value: '紫月' },
          { label: 'Plus', value: '红十' },
          { label: 'Square', value: '红方' },
          { label: 'Triangle', value: '蓝三角' },
          { label: 'Wave', value: '褐扭' },
          { label: '3circles', value: '青花' },
          { label: 'Circle', value: '黄圆' },
          { label: 'Spades', value: '粉桃' },
        ]
      },
      {
        key: 'shroud',
        name: '🌫️ Shroud',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'clues',
        name: '🔍 Clues',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'traits',
        name: '🏷️ Traits',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '密谋卡': {
    field_type_en: 'Agenda Card',
    field_type_display: '🌙 Agenda Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'is_back',
        name: '📃 Side',
        type: 'select',
        layout: 'half',
        defaultValue: false,
        options: [
          { label: '🔼 Front', value: false },
          { label: '🔽 Back', value: true },
        ]
      },
      {
        key: 'serial_number',
        name: '🔢 Agenda Number',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'threshold',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '💥 Doom Threshold',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'victory',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '密谋卡-大画': {
    field_type_en: 'Agenda Card - Large Art',
    field_type_display: '🌕 Agenda Card - Large Art',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'threshold',
        name: '💥 Doom Threshold',
        type: 'text',
        layout: 'full'
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '场景卡': {
    field_type_en: 'Act Card',
    field_type_display: '🎬 Act Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'is_back',
        name: '📃 Side',
        type: 'select',
        layout: 'half',
        defaultValue: false,
        options: [
          { label: '🔼 Front', value: false },
          { label: '🔽 Back', value: true },
        ]
      },
      {
        key: 'serial_number',
        name: '🔢 Act Number',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'threshold',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🎯 Clue Threshold',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'victory',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '场景卡-大画': {
    field_type_en: 'Act Card - Large Art',
    field_type_display: '🎞️ Act Card - Large Art',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'flavor',
        name: '🎭 Flavor Text',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '冒险参考卡': {
    field_type_en: 'Scenario Reference Card',
    field_type_display: '📋 Scenario Reference Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Card Name',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        showCondition: {
          field: 'scenario_type',
          value: 2,
          operator: 'not-equals'
        },
        name: '📋 Subtitle',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'scenario_type',
        name: '🃏 Card Type',
        type: 'select',
        layout: 'full',
        defaultValue: 0,
        options: [
          { label: '📊 Default Type', value: 0 },
          { label: '💎 Resource Type', value: 1 },
          { label: '📄 Text Type', value: 2 }
        ]
      },
      {
        key: 'body',
        showCondition: {
          field: 'scenario_type',
          value: 2
        },
        name: '📄 Card Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'scenario_card.resource_name',
        showCondition: {
          field: 'scenario_type',
          value: 1
        },
        name: '💎 Resource Name',
        type: 'text',
        layout: 'full'
      },
      {
        key: 'scenario_card.skull',
        showCondition: {
          field: 'scenario_type',
          value: 2,
          operator: 'not-equals'
        },
        name: '💀 Skull Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.cultist',
        showCondition: {
          field: 'scenario_type',
          value: 2,
          operator: 'not-equals'
        },
        name: '👥 Cultist Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.tablet',
        showCondition: {
          field: 'scenario_type',
          value: 2,
          operator: 'not-equals'
        },
        name: '📜 Tablet Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.elder_thing',
        showCondition: {
          field: 'scenario_type',
          value: 2,
          operator: 'not-equals'
        },
        name: '👁️ Elder Thing Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'victory',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 Victory Points',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 Victory Text',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 Encounter Set',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🖼️ Artwork',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
      ...externalImageFields
    ]
  },
  '规则小卡': {
    field_type_en: 'Rules Mini Card',
    field_type_display: '📘 Rules Mini Card',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 Title',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'body',
        name: '📄 Body Text',
        type: 'body-editor',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'page_number',
        name: '🔢 Page Number (1-999)',
        type: 'number',
        layout: 'half',
        helpText: 'Display numbers 1-999 only'
      }
    ]
  },
};

// Unofficial template mappings
const unofficialTemplates: Record<string, { source: string; displayName: string; englishName: string }> = {
  '大画-支援卡': {
    source: '支援卡',
    displayName: '📦 Large Art - Asset',
    englishName: 'Large Art Asset Card'
  },
  '大画-事件卡': {
    source: '事件卡',
    displayName: '⚡ Large Art - Event',
    englishName: 'Large Art Event Card'
  },
  '大画-技能卡': {
    source: '技能卡',
    displayName: '🎯 Large Art - Skill',
    englishName: 'Large Art Skill Card'
  }
};
// Generate unofficial template configs (deep clone)
Object.entries(unofficialTemplates).forEach(([key, { source, displayName }]) => {
  cardTypeConfigs[key] = JSON.parse(JSON.stringify(cardTypeConfigs[source]));
  cardTypeConfigs[key].field_type_display = displayName;
});

// System preset card back type configurations
export const cardBackConfigs: Record<string, CardTypeConfig> = {
  '玩家卡背': {
    field_type_en: 'Player Card Back',
    field_type_display: '🎴 Player Card Back',
    card_category: 'player',
    fields: []
  },
  '遭遇卡背': {
    field_type_en: 'Encounter Card Back',
    field_type_display: '🎯 Encounter Card Back',
    card_category: 'encounter',
    fields: []
  },
  '定制卡背': {
    field_type_en: 'Custom Card Back',
    field_type_display: '🃏 Custom Card Back',
    card_category: 'custom',
    fields: []
  },
  '敌库卡背': {
    field_type_en: 'Enemy Deck Card Back',
    field_type_display: '👹 Enemy Deck Card Back',
    card_category: 'encounter',
    fields: []
  }
};

export const cardTypeOptions = [
  { label: '--- Player Cards ---', value: '__divider_player__', disabled: true },
  // Player card types
  ...Object.keys(cardTypeConfigs)
    .filter(key => {
      const isPlayerCard = cardTypeConfigs[key].card_category === 'player';
      const isUnofficial = key in unofficialTemplates;
      return isPlayerCard && !isUnofficial;
    })
    .map(key => ({
      label: cardTypeConfigs[key].field_type_display || cardTypeConfigs[key].field_type_en || key,
      value: key
    })),
  { label: '--- Encounter Cards ---', value: '__divider_encounter__', disabled: true },
  // Encounter card types
  ...Object.keys(cardTypeConfigs)
    .filter(key => cardTypeConfigs[key].card_category === 'encounter')
    .map(key => ({
      label: cardTypeConfigs[key].field_type_display || cardTypeConfigs[key].field_type_en || key,
      value: key
    })),
  { label: '--- Unofficial Templates ---', value: '__divider_unofficial__', disabled: true },
  ...Object.keys(unofficialTemplates).map(key => ({
    label: cardTypeConfigs[key].field_type_display || key,
    value: key
  })),
  // System preset card back options
  { label: '--- System Presets ---', value: '__divider__', disabled: true },
  { label: cardBackConfigs['玩家卡背'].field_type_display, value: '玩家卡背' },
  { label: cardBackConfigs['遭遇卡背'].field_type_display, value: '遭遇卡背' },
  { label: cardBackConfigs['定制卡背'].field_type_display, value: '定制卡背' },
  { label: cardBackConfigs['敌库卡背'].field_type_display, value: '敌库卡背' },
];

// Get default back type configuration for card types
export const getDefaultBackType = (frontType: string): { type: string; is_back?: boolean } | null => {
  const playerCardTypes = ['支援卡', '事件卡', '技能卡'];
  const encounterCardTypes = ['故事卡', '诡计卡', '敌人卡'];

  if (playerCardTypes.includes(frontType)) {
    return { type: '玩家卡背' };
  }

  if (encounterCardTypes.includes(frontType)) {
    return { type: '遭遇卡背' };
  }

  if (frontType === '定制卡') {
    return { type: '定制卡背' };
  }

  if (frontType === '调查员') {
    return { type: '调查员背面' };
  }

  if (frontType === '调查员小卡') {
    return { type: '调查员小卡', is_back: true };
  }

  if (frontType === '地点卡') {
    return { type: '地点卡', location_type: '未揭示' };
  }

  if (frontType === '密谋卡') {
    return { type: '密谋卡', is_back: true };
  }

  if (frontType === '场景卡') {
    return { type: '场景卡', is_back: true };
  }

  if (frontType === '冒险参考卡') {
    return { type: '冒险参考卡' };
  }

  return null;
};

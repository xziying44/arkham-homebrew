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
  type: 'text' | 'textarea' | 'number' | 'select' | 'multi-select' | 'string-array' | 'image' | 'encounter-group-select'; // Add new type
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

Support direct use of emoji or corresponding tag format
`;

const nameTip = `Support unique marker: 🏅 or <独特>`;

const victoryTip = `Only one of Victory Points or Victory Text can be filled in. Victory Text takes precedence over Victory Points.`

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
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' },
          { label: '🌟 Multi-class', value: '多职阶' },
          { label: '💀 Weakness', value: '弱点' },
          { label: '⚪ Neutral', value: '中立' }
        ]
      },
      {
        key: 'subclass',
        index: 0,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '1️⃣ First Class',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 1,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '2️⃣ Second Class',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 No Class', value: null },
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 2,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '3️⃣ Third Class',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 No Class', value: null },
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' }
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
        key: 'health',
        name: '❤️ Health',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 No Health', value: -1 },
          { label: '⭐ Infinite Health', value: -2 },
          { label: '💀 Health-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `❤️ Health-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'horror',
        name: '🧠 Sanity',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 No Sanity', value: -1 },
          { label: '⭐ Infinite Sanity', value: -2 },
          { label: '😵 Sanity-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `🧠 Sanity-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'slots',
        name: '🎒 Slot',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 No Slot', value: null },
          { label: '👥 Ally', value: '盟友' },
          { label: '👕 Body', value: '身体' },
          { label: '💍 Accessory', value: '饰品' },
          { label: '🤲 Hand', value: '手部' },
          { label: '🙌 Two-Handed', value: '双手' },
          { label: '🔮 Spell', value: '法术' },
          { label: '✨ Two-Spell', value: '双法术' },
          { label: '🃏 Tarot', value: '塔罗' }
        ]
      },
      {
        key: 'slots2',
        name: '🎒 Second Slot',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 No Slot', value: null },
          { label: '👥 Ally', value: '盟友' },
          { label: '👕 Body', value: '身体' },
          { label: '💍 Accessory', value: '饰品' },
          { label: '🤲 Hand', value: '手部' },
          { label: '🙌 Two-Handed', value: '双手' },
          { label: '🔮 Spell', value: '法术' },
          { label: '✨ Two-Spell', value: '双法术' },
          { label: '🃏 Tarot', value: '塔罗' }
        ]
      },
      {
        key: 'level',
        name: '⭐ Card Level',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🧩 Custom Level', value: -2 },
          { label: '🚫 No Level', value: -1 },
          { label: '0️⃣ Level-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} Level-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '💰 Cost',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🆓 No Cost', value: -1 },
          { label: '✖️ X Cost', value: -2 },
          { label: '0️⃣ Cost-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `💰 Cost-${i + 1}`, value: i + 1 }))
        ]
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
        type: 'textarea',
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
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' },
          { label: '🌟 Multi-class', value: '多职阶' },
          { label: '💀 Weakness', value: '弱点' },
          { label: '⚪ Neutral', value: '中立' }
        ]
      },
      {
        key: 'subclass',
        index: 0,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '1️⃣ First Class',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 1,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '2️⃣ Second Class',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 No Class', value: null },
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 2,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '3️⃣ Third Class',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 No Class', value: null },
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' }
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
        key: 'level',
        name: '⭐ Card Level',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🧩 Custom Level', value: -2 },
          { label: '🚫 No Level', value: -1 },
          { label: '0️⃣ Level-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} Level-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '💰 Cost',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🆓 No Cost', value: -1 },
          { label: '✖️ X Cost', value: -2 },
          { label: '0️⃣ Cost-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `💰 Cost-${i + 1}`, value: i + 1 }))
        ]
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
        type: 'textarea',
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
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' },
          { label: '💀 Weakness', value: '弱点' },
          { label: '⚪ Neutral', value: '中立' }
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
        key: 'level',
        name: '⭐ Card Level',
        type: 'select',
        layout: 'full',
        defaultValue: -1,
        options: [
          { label: '🧩 Custom Level', value: -2 },
          { label: '🚫 No Level', value: -1 },
          { label: '0️⃣ Level-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} Level-${i + 1}`, value: i + 1 }))
        ]
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
        type: 'textarea',
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
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' },
          { label: '⚪ Neutral', value: '中立' }
        ]
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
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 No Health', value: -1 },
          { label: '💀 Health-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `❤️ Health-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'horror',
        name: '🧠 Sanity',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 No Sanity', value: -1 },
          { label: '😵 Sanity-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `🧠 Sanity-${i + 1}`, value: i + 1 }))
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
        type: 'textarea',
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
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ Guardian', value: '守护者' },
          { label: '🔍 Seeker', value: '探求者' },
          { label: '🏃 Rogue', value: '流浪者' },
          { label: '🔮 Mystic', value: '潜修者' },
          { label: '💪 Survivor', value: '生存者' },
          { label: '⚪ Neutral', value: '中立' }
        ]
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
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
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
        type: 'textarea',
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
        type: 'textarea',
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
        type: 'textarea',
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
          { label: '🔶 Green Diamond', value: '绿菱' },
          { label: '🔴 Dark Red Funnel', value: '暗红漏斗' },
          { label: '🧡 Orange Heart', value: '橙心' },
          { label: '🟤 Light Brown Drop', value: '浅褐水滴' },
          { label: '🟣 Deep Purple Star', value: '深紫星' },
          { label: '🟢 Dark Green Slash', value: '深绿斜二' },
          { label: '🔷 Dark Blue T', value: '深蓝T' },
          { label: '🌙 Purple Moon', value: '紫月' },
          { label: '➕ Red Cross', value: '红十' },
          { label: '🟥 Red Square', value: '红方' },
          { label: '🔺 Blue Triangle', value: '蓝三角' },
          { label: '🌀 Brown Spiral', value: '褐扭' },
          { label: '🌸 Cyan Flower', value: '青花' },
          { label: '🟡 Yellow Circle', value: '黄圆' },
        ]
      },
      {
        key: 'location_link',
        name: '🔗 Connected Location Icons',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🔶 Green Diamond', value: '绿菱' },
          { label: '🔴 Dark Red Funnel', value: '暗红漏斗' },
          { label: '🧡 Orange Heart', value: '橙心' },
          { label: '🟤 Light Brown Drop', value: '浅褐水滴' },
          { label: '🟣 Deep Purple Star', value: '深紫星' },
          { label: '🟢 Dark Green Slash', value: '深绿斜二' },
          { label: '🔷 Dark Blue T', value: '深蓝T' },
          { label: '🌙 Purple Moon', value: '紫月' },
          { label: '➕ Red Cross', value: '红十' },
          { label: '🟥 Red Square', value: '红方' },
          { label: '🔺 Blue Triangle', value: '蓝三角' },
          { label: '🌀 Brown Spiral', value: '褐扭' },
          { label: '🌸 Cyan Flower', value: '青花' },
          { label: '🟡 Yellow Circle', value: '黄圆' },
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
        type: 'textarea',
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
        type: 'textarea',
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
        type: 'textarea',
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
        type: 'textarea',
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
        type: 'textarea',
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
          { label: '💎 Resource Type', value: 1 }
        ]
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
        name: '💀 Skull Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.cultist',
        name: '👥 Cultist Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.tablet',
        name: '📜 Tablet Effect',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.elder_thing',
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
    ]
  },
};

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
    .filter(key => cardTypeConfigs[key].card_category === 'player')
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

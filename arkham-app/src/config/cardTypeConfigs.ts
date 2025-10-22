export interface FieldOption {
  label: string;
  value: string | number | null;
}

export interface ShowCondition {
  field: string;  // 依赖的字段名
  value: any;     // 当字段值等于此值时显示
  operator?: 'equals' | 'not-equals' | 'includes' | 'not-includes';  // 比较操作符，默认为 equals
}

// 在 FormField 接口中添加新的字段类型
export interface FormField {
  key: string;
  name: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'multi-select' | 'string-array' | 'image' | 'encounter-group-select'; // 添加新类型
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
  field_type_display?: string; // 用于显示的名称（带emoji）
  card_category?: 'player' | 'encounter'; // 卡牌分类
}

// 提示文本
const compoundNumbersTip = `输入格式：
• 数字：如 8
• 可变数字：如 2<调查员>
• 特殊值：- / X / ?

支持：数字、数字<调查员>、特殊符号(-/X/?)。
`

const bodyTip = `输入格式：
● 【】或{{}}表示粗体，如：【调查】、{{调查}}
● {}表示特性，如：{盟友}
● []表示风味文本，如：[这里是风味文本...]
● 你可以使用更高级的风味标签来定制你所需要的功能：
 <flavor align="left" flex="false" padding="0" quote="false">xxx</flavor>
● <upg>或<升级>在定制卡中使用会自动生成TTS的复选框脚本。

可用图标标签：
🏅 <独特>
⭕ <反应>
➡️ <启动>
⚡ <免费>
💀 <骷髅>
👤 <异教徒>
📜 <石板>
👹 <古神>
🐙 <触手>
⭐ <旧印>
👊 <拳>
📚 <书>
🦶 <脚>
🧠 <脑>
❓ <?>
🔵 <点>
🌑 <诅咒>
🌟 <祝福>
❄️ <雪花>
🕵️ <调查员>
🚶 <流浪者>
🏕️ <生存者>
🛡️ <守护者>
🧘 <潜修者>
🔍 <探求者>

特殊标签：
<br> 换行
<hr> 横线

支持直接使用emoji或对应的标签格式
`

const nameTip = `支持添加独特标记：🏅 或 <独特>`

const victoryTip = `胜利点和胜利点文本只能填写一个，胜利点文本优先级大于胜利点。`

export const cardTypeConfigs: Record<string, CardTypeConfig> = {
  '支援卡': {
    field_type_display: '📦 支援卡',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '⚔️ 职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' },
          { label: '🌟 多职阶', value: '多职阶' },
          { label: '💀 弱点', value: '弱点' },
          { label: '⚪ 中立', value: '中立' }
        ]
      },
      {
        key: 'subclass',
        index: 0,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '1️⃣ 第一职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 1,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '2️⃣ 第二职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 无职介', value: null },
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 2,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '3️⃣ 第三职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 无职介', value: null },
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' }
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ 弱点类型',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 弱点', value: '弱点' },
          { label: '📋 基础弱点', value: '基础弱点' }
        ]
      },
      {
        key: 'health',
        name: '❤️ 生命值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无生命值', value: -1 },
          { label: '⭐ 无限生命值', value: -2 },
          { label: '💀 生命值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `❤️ 生命值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'horror',
        name: '🧠 理智值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无理智值', value: -1 },
          { label: '⭐ 无限理智值', value: -2 },
          { label: '😵 理智值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `🧠 理智值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'slots',
        name: '🎒 槽位',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 空槽位', value: null },
          { label: '👥 盟友', value: '盟友' },
          { label: '👕 身体', value: '身体' },
          { label: '💍 饰品', value: '饰品' },
          { label: '🤲 手部', value: '手部' },
          { label: '🙌 双手', value: '双手' },
          { label: '🔮 法术', value: '法术' },
          { label: '✨ 双法术', value: '双法术' },
          { label: '🃏 塔罗', value: '塔罗' }
        ]
      },
      {
        key: 'slots2',
        name: '🎒 第二槽位',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 空槽位', value: null },
          { label: '👥 盟友', value: '盟友' },
          { label: '👕 身体', value: '身体' },
          { label: '💍 饰品', value: '饰品' },
          { label: '🤲 手部', value: '手部' },
          { label: '🙌 双手', value: '双手' },
          { label: '🔮 法术', value: '法术' },
          { label: '✨ 双法术', value: '双法术' },
          { label: '🃏 塔罗', value: '塔罗' }
        ]
      },
      {
        key: 'level',
        name: '⭐ 卡牌等级',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🧩 定制标', value: -2 },
          { label: '🚫 无等级', value: -1 },
          { label: '0️⃣ 等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} 等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '💰 卡牌费用',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🆓 无费用', value: -1 },
          { label: '✖️ X费用', value: -2 },
          { label: '0️⃣ 费用-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `💰 费用-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'submit_icon',
        name: '🎯 投入图标',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🧠 意志', value: '意志' },
          { label: '⚔️ 战力', value: '战力' },
          { label: '⚡ 敏捷', value: '敏捷' },
          { label: '📚 智力', value: '智力' },
          { label: '🌟 狂野', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
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
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '事件卡': {
    field_type_display: '⚡ 事件卡',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'full',
        helpText: nameTip
      },
      {
        key: 'class',
        name: '⚔️ 职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' },
          { label: '🌟 多职阶', value: '多职阶' },
          { label: '💀 弱点', value: '弱点' },
          { label: '⚪ 中立', value: '中立' }
        ]
      },
      {
        key: 'subclass',
        index: 0,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '1️⃣ 第一职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 1,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '2️⃣ 第二职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 无职介', value: null },
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 2,
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '3️⃣ 第三职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '🚫 无职介', value: null },
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' }
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ 弱点类型',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 弱点', value: '弱点' },
          { label: '📋 基础弱点', value: '基础弱点' }
        ]
      },
      {
        key: 'level',
        name: '⭐ 卡牌等级',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🧩 定制标', value: -2 },
          { label: '🚫 无等级', value: -1 },
          { label: '0️⃣ 等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} 等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '💰 卡牌费用',
        type: 'select',
        layout: 'half',
        defaultValue: -1,
        options: [
          { label: '🆓 无费用', value: -1 },
          { label: '✖️ X费用', value: -2 },
          { label: '0️⃣ 费用-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `💰 费用-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'submit_icon',
        name: '🎯 投入图标',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🧠 意志', value: '意志' },
          { label: '⚔️ 战力', value: '战力' },
          { label: '⚡ 敏捷', value: '敏捷' },
          { label: '📚 智力', value: '智力' },
          { label: '🌟 狂野', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '技能卡': {
    field_type_display: '🎯 技能卡',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'full',
        helpText: nameTip
      },
      {
        key: 'class',
        name: '⚔️ 职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' },
          { label: '💀 弱点', value: '弱点' },
          { label: '⚪ 中立', value: '中立' }
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ 弱点类型',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 弱点', value: '弱点' },
          { label: '📋 基础弱点', value: '基础弱点' }
        ]
      },
      {
        key: 'level',
        name: '⭐ 卡牌等级',
        type: 'select',
        layout: 'full',
        defaultValue: -1,
        options: [
          { label: '🧩 定制标', value: -2 },
          { label: '🚫 无等级', value: -1 },
          { label: '0️⃣ 等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} 等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'submit_icon',
        name: '🎯 投入图标',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '🧠 意志', value: '意志' },
          { label: '⚔️ 战力', value: '战力' },
          { label: '⚡ 敏捷', value: '敏捷' },
          { label: '📚 智力', value: '智力' },
          { label: '🌟 狂野', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '调查员': {
    field_type_display: '👤 调查员',
    card_category: 'player',
    fields: [
      {
        key: 'subtype',
        name: '⚙️ 副类型',
        type: 'select',
        layout: 'full',
        defaultValue: '默认',
        options: [
          { label: '📛 默认', value: '默认' },
          { label: '🔀 平行', value: '平行' }
        ]
      },
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '⚔️ 职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' },
          { label: '⚪ 中立', value: '中立' }
        ]
      },
      {
        key: 'attribute',
        index: 0,
        name: '🧠 意志',
        type: 'number',
        layout: 'quarter',
        min: 0,
        max: 19
      },
      {
        key: 'attribute',
        index: 1,
        name: '📚 智力',
        type: 'number',
        layout: 'quarter',
        min: 0,
        max: 19
      },
      {
        key: 'attribute',
        index: 2,
        name: '⚔️ 战力',
        type: 'number',
        layout: 'quarter',
        min: 0,
        max: 19
      },
      {
        key: 'attribute',
        index: 3,
        name: '⚡ 敏捷',
        type: 'number',
        layout: 'quarter',
        min: 0,
        max: 19
      },
      {
        key: 'health',
        name: '❤️ 生命值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无生命值', value: -1 },
          { label: '💀 生命值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `❤️ 生命值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'horror',
        name: '🧠 理智值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无理智值', value: -1 },
          { label: '😵 理智值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `🧠 理智值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '调查员背面': {
    field_type_display: '🔄 调查员背面',
    card_category: 'player',
    fields: [
      {
        key: 'subtype',
        name: '⚙️ 副类型',
        type: 'select',
        layout: 'full',
        defaultValue: '默认',
        options: [
          { label: '📛 默认', value: '默认' },
          { label: '🔀 平行', value: '平行' }
        ]
      },
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '⚔️ 职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '🛡️ 守护者', value: '守护者' },
          { label: '🔍 探求者', value: '探求者' },
          { label: '🏃 流浪者', value: '流浪者' },
          { label: '🔮 潜修者', value: '潜修者' },
          { label: '💪 生存者', value: '生存者' },
          { label: '⚪ 中立', value: '中立' }
        ]
      },
      {
        key: 'card_back.size',
        name: '🔢 卡牌张数',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 99
      },
      {
        key: 'card_back.option',
        name: '🎯 牌库构建选项',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'card_back.requirement',
        name: '📋 牌库构建需求',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'card_back.other',
        name: '⚙️ 其他构筑需求',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'card_back.story',
        name: '📖 故事文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '定制卡': {
    field_type_display: '🎨 定制卡',
    card_category: 'player',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
    ]
  },
  '故事卡': {
    field_type_display: '📖 故事卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
    ]
  },
  '诡计卡': {
    field_type_display: '🎭 诡计卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'class',
        name: '🃏 类型',
        type: 'select',
        layout: 'half',
        defaultValue: '',
        options: [
          { label: '🔮 遭遇', value: "" },
          { label: '💀 弱点', value: '弱点' },
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ 弱点类型',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 弱点', value: '弱点' },
          { label: '📋 基础弱点', value: '基础弱点' }
        ]
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '敌人卡': {
    field_type_display: '👹 敌人卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '🃏 类型',
        type: 'select',
        layout: 'full',
        defaultValue: '',
        options: [
          { label: '🔮 遭遇', value: "" },
          { label: '💀 弱点', value: '弱点' },
        ]
      },
      {
        key: 'weakness_type',
        showCondition: {
          field: 'class',
          value: '弱点'
        },
        name: '🏷️ 弱点类型',
        type: 'select',
        layout: 'full',
        defaultValue: '弱点',
        options: [
          { label: '💀 弱点', value: '弱点' },
          { label: '📋 基础弱点', value: '基础弱点' }
        ]
      },
      {
        key: 'attack',
        name: '⚔️ 攻击值',
        type: 'text',
        layout: 'third',
        helpText: compoundNumbersTip
      },
      {
        key: 'enemy_health',
        name: '❤️ 生命值',
        type: 'text',
        layout: 'third',
        helpText: compoundNumbersTip
      },
      {
        key: 'evade',
        name: '🏃 躲避值',
        type: 'text',
        layout: 'third',
        helpText: compoundNumbersTip
      },
      {
        key: 'enemy_damage',
        name: '💔 伤害',
        type: 'select',
        layout: 'half',
        options: [
          { label: '💔 伤害-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `💔 伤害-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'enemy_damage_horror',
        name: '😱 恐惧',
        type: 'select',
        layout: 'half',
        options: [
          { label: '😱 恐惧-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `😱 恐惧-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '地点卡': {
    field_type_display: '📍 地点卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'location_type',
        name: '🗺️ 地点类型',
        type: 'select',
        layout: 'half',
        options: [
          { label: '👁️ 已揭示', value: '已揭示' },
          { label: '❓ 未揭示', value: '未揭示' },
        ]
      },
      {
        key: 'location_icon',
        name: '📍 地点图标',
        type: 'select',
        layout: 'half',
        options: [
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
          { label: '🟡 黄圆', value: '黄圆' },
        ]
      },
      {
        key: 'location_link',
        name: '🔗 连接地点图标',
        type: 'multi-select',
        layout: 'full',
        options: [
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
          { label: '🟡 黄圆', value: '黄圆' },
        ]
      },
      {
        key: 'shroud',
        name: '🌫️ 隐藏值',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'clues',
        name: '🔍 线索值',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'traits',
        name: '🏷️ 特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '密谋卡': {
    field_type_display: '🌙 密谋卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'is_back',
        name: '📃 正面背面',
        type: 'select',
        layout: 'half',
        defaultValue: false,
        options: [
          { label: '🔼 正面', value: false },
          { label: '🔽 背面', value: true },
        ]
      },
      {
        key: 'serial_number',
        name: '🔢 密谋编号',
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
        name: '💥 毁灭阈值',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
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
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '密谋卡-大画': {
    field_type_display: '🌕 密谋卡-大画',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'threshold',
        name: '💥 毁灭阈值',
        type: 'text',
        layout: 'full'
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '场景卡': {
    field_type_display: '🎬 场景卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'is_back',
        name: '📃 正面背面',
        type: 'select',
        layout: 'half',
        defaultValue: false,
        options: [
          { label: '🔼 正面', value: false },
          { label: '🔽 背面', value: true },
        ]
      },
      {
        key: 'serial_number',
        name: '🔢 场景编号',
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
        name: '🎯 场景目标',
        type: 'text',
        layout: 'half',
        helpText: compoundNumbersTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
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
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '场景卡-大画': {
    field_type_display: '🎞️ 场景卡-大画',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'flavor',
        name: '🎭 风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full',
        helpText: bodyTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
  '冒险参考卡': {
    field_type_display: '📋 冒险参考卡',
    card_category: 'encounter',
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half',
        helpText: nameTip
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'scenario_type',
        name: '🃏 卡牌类型',
        type: 'select',
        layout: 'full',
        defaultValue: 0,
        options: [
          { label: '📊 默认类型', value: 0 },
          { label: '💎 资源类型', value: 1 }
        ]
      },
      {
        key: 'scenario_card.resource_name',
        showCondition: {
          field: 'scenario_type',
          value: 1
        },
        name: '💎 资源名称',
        type: 'text',
        layout: 'full'
      },
      {
        key: 'scenario_card.skull',
        name: '💀 骷髅效果',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.cultist',
        name: '👥 异教徒效果',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.tablet',
        name: '📜 石板效果',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'scenario_card.elder_thing',
        name: '👁️ 古神效果',
        type: 'textarea',
        layout: 'half'
      },
      {
        key: 'victory',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 胜利点',
        type: 'number',
        layout: 'half'
      },
      {
        key: 'victory_text',
        showCondition: {
          field: 'is_back',
          value: true
        },
        name: '🏆 胜利点文本',
        type: 'text',
        layout: 'half',
        helpText: victoryTip
      },
      {
        key: 'encounter_group',
        name: '🎲 遭遇组',
        type: 'encounter-group-select',
        layout: 'full'
      },
      {
        key: 'picture_base64',
        showCondition: {
          field: 'is_back',
          value: false
        },
        name: '🖼️ 插画',
        type: 'image',
        layout: 'half',
        maxSize: 50 * 1024 * 1024, // 50MB
      },
    ]
  },
};

// 系统预设卡背类型配置
export const cardBackConfigs: Record<string, CardTypeConfig> = {
  '玩家卡背': {
    field_type_display: '🎴 玩家卡背',
    card_category: 'player',
    fields: []
  },
  '遭遇卡背': {
    field_type_display: '🎯 遭遇卡背',
    card_category: 'encounter',
    fields: []
  },
  '调查员背面': {
    field_type_display: '🔄 调查员背面',
    card_category: 'player',
    fields: []
  },
  '密谋卡': {
    field_type_display: '🌙 密谋卡',
    card_category: 'encounter',
    fields: []
  },
  '场景卡': {
    field_type_display: '🎬 场景卡',
    card_category: 'encounter',
    fields: []
  },
  '冒险参考卡': {
    field_type_display: '📋 冒险参考卡',
    card_category: 'encounter',
    fields: []
  }
};

export const cardTypeOptions = [
  { label: '--- 玩家卡 ---', value: '__divider_player__', disabled: true },
  // 玩家卡类型
  ...Object.keys(cardTypeConfigs)
    .filter(key => cardTypeConfigs[key].card_category === 'player')
    .map(key => ({
      label: cardTypeConfigs[key].field_type_display || key,
      value: key
    })),
  { label: '--- 遭遇卡 ---', value: '__divider_encounter__', disabled: true },
  // 遭遇卡类型
  ...Object.keys(cardTypeConfigs)
    .filter(key => cardTypeConfigs[key].card_category === 'encounter')
    .map(key => ({
      label: cardTypeConfigs[key].field_type_display || key,
      value: key
    })),
  // 系统预设卡背选项
  { label: '--- 系统预设 ---', value: '__divider__', disabled: true },
  { label: cardBackConfigs['玩家卡背'].field_type_display, value: '玩家卡背' },
  { label: cardBackConfigs['遭遇卡背'].field_type_display, value: '遭遇卡背' },
];

// 获取卡牌类型对应的默认背面配置
export const getDefaultBackType = (frontType: string): { type: string; is_back?: boolean } | null => {
  const playerCardTypes = ['支援卡', '事件卡', '技能卡', '定制卡'];
  const encounterCardTypes = ['故事卡', '诡计卡', '敌人卡'];

  if (playerCardTypes.includes(frontType)) {
    return { type: '玩家卡背' };
  }

  if (encounterCardTypes.includes(frontType)) {
    return { type: '遭遇卡背' };
  }

  if (frontType === '地点卡') {
    return { type: '地点卡', location_type: '未揭示' };
  }

  if (frontType === '调查员') {
    return { type: '调查员背面' };
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

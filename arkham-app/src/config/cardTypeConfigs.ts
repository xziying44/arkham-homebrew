export interface FieldOption {
  label: string;
  value: string | number | null;
}

export interface ShowCondition {
  field: string;  // 依赖的字段名
  value: any;     // 当字段值等于此值时显示
  operator?: 'equals' | 'not-equals' | 'includes' | 'not-includes';  // 比较操作符，默认为 equals
}

export interface FormField {
  key: string;
  name: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'multi-select' | 'string-array' | 'image';
  layout?: 'full' | 'half' | 'third' | 'quarter';
  min?: number;
  max?: number;
  rows?: number;
  maxlength?: number;
  options?: FieldOption[];
  showCondition?: ShowCondition;  // 新增：显示条件
  index?: number;  // 新增：数组索引，表示绑定到 key[index]
  maxSize?: number; // 图片最大文件大小（字节）
}

export interface CardTypeConfig {
  fields: FormField[];
}

export const cardTypeConfigs: Record<string, CardTypeConfig> = {
  '支援卡': {
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half'
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
        key: 'health',
        name: '❤️ 生命值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无生命值', value: null },
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
          { label: '🚫 无理智值', value: null },
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
        options: [
          { label: '🚫 无等级', value: null },
          { label: '0️⃣ 等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} 等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '💰 卡牌费用',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🆓 无费用', value: null },
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
        layout: 'full'
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
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'full'
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
        key: 'level',
        name: '⭐ 卡牌等级',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无等级', value: null },
          { label: '0️⃣ 等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `${['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][i]} 等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '💰 卡牌费用',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🆓 无费用', value: null },
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
        layout: 'full'
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
  '技能卡': {
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'full'
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
        key: 'level',
        name: '⭐ 卡牌等级',
        type: 'select',
        layout: 'full',
        options: [
          { label: '🚫 无等级', value: null },
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
        layout: 'full'
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
  '调查员': {
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'attribute',
        index: 0,
        name: '🧠 意志',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'attribute',
        index: 1,
        name: '📚 智力',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'attribute',
        index: 2,
        name: '⚔️ 战力',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'attribute',
        index: 3,
        name: '⚡ 敏捷',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'health',
        name: '❤️ 生命值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '🚫 无生命值', value: null },
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
          { label: '🚫 无理智值', value: null },
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
        layout: 'full'
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
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
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
        type: 'string-array',
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
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'body',
        name: '📄 卡牌效果',
        type: 'textarea',
        layout: 'full'
      },
    ]
  },
  '诡计卡': {
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'full'
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
        layout: 'full'
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
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'subtitle',
        name: '📋 副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'attack',
        name: '⚔️ 攻击值',
        type: 'text',
        layout: 'third'
      },
      {
        key: 'enemy_health',
        name: '❤️ 生命值',
        type: 'text',
        layout: 'third'
      },
      {
        key: 'evade',
        name: '🏃 躲避值',
        type: 'text',
        layout: 'third'
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
        layout: 'full'
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
    fields: [
      {
        key: 'name',
        name: '📝 卡名',
        type: 'text',
        layout: 'half'
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
        layout: 'half'
      },
      {
        key: 'clues',
        name: '🔍 线索值',
        type: 'text',
        layout: 'half'
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
        layout: 'full'
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
};

export const cardTypeOptions = Object.keys(cardTypeConfigs).map(key => ({
  label: key,
  value: key
}));

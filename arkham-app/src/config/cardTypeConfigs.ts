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
  type: 'text' | 'textarea' | 'number' | 'select' | 'multi-select' | 'string-array';
  layout?: 'full' | 'half' | 'third' | 'quarter';
  min?: number;
  max?: number;
  rows?: number;
  maxlength?: number;
  options?: FieldOption[];
  showCondition?: ShowCondition;  // 新增：显示条件
  index?: number;  // 新增：数组索引，表示绑定到 key[index]
}
export interface CardTypeConfig {
  fields: FormField[];
}

export const cardTypeConfigs: Record<string, CardTypeConfig> = {
  '支援卡': {
    fields: [
      {
        key: 'name',
        name: '卡名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'subtitle',
        name: '副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'class',
        name: '职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' },
          { label: '多职阶', value: '多职阶' },
          { label: '弱点', value: '弱点' },
          { label: '中立', value: '中立' }
        ]
      },
      {
        key: 'subclass',
        index: 0,  // 绑定到 subclass[1]
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '第一职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 1,  // 绑定到 subclass[1]
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '第二职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '无职介', value: null },
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 2,  // 绑定到 subclass[1]
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '第三职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '无职介', value: null },
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' }
        ]
      },
      {
        key: 'health',
        name: '生命值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无生命值', value: null },
          { label: '生命值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `生命值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'horror',
        name: '理智值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无理智值', value: null },
          { label: '理智值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `理智值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'slots',
        name: '槽位',
        type: 'select',
        layout: 'half',
        options: [
          { label: '空槽位', value: null },
          { label: '盟友', value: '盟友' },
          { label: '身体', value: '身体' },
          { label: '饰品', value: '饰品' },
          { label: '手部', value: '手部' },
          { label: '双手', value: '双手' },
          { label: '法术', value: '法术' },
          { label: '双法术', value: '双法术' },
          { label: '塔罗', value: '塔罗' }
        ]
      },
      {
        key: 'slots2',
        name: '第二槽位',
        type: 'select',
        layout: 'half',
        options: [
          { label: '空槽位', value: null },
          { label: '盟友', value: '盟友' },
          { label: '身体', value: '身体' },
          { label: '饰品', value: '饰品' },
          { label: '手部', value: '手部' },
          { label: '双手', value: '双手' },
          { label: '法术', value: '法术' },
          { label: '双法术', value: '双法术' },
          { label: '塔罗', value: '塔罗' }
        ]
      },
      {
        key: 'level',
        name: '卡牌等级',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无等级', value: null },
          { label: '等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '卡牌费用',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无费用', value: null },
          { label: '费用-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `费用-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'submit_icon',
        name: '投入图标',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '意志', value: '意志' },
          { label: '战力', value: '战力' },
          { label: '敏捷', value: '敏捷' },
          { label: '智力', value: '智力' },
          { label: '狂野', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '卡牌效果',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'flavor',
        name: '风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '胜利点',
        type: 'number',
        layout: 'full'
      },
    ]
  },
  '事件卡': {
    fields: [
      {
        key: 'name',
        name: '卡名',
        type: 'text',
        layout: 'full'
      },
      {
        key: 'class',
        name: '职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' },
          { label: '多职阶', value: '多职阶' },
          { label: '弱点', value: '弱点' },
          { label: '中立', value: '中立' }
        ]
      },
      {
        key: 'subclass',
        index: 0,  // 绑定到 subclass[1]
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '第一职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 1,  // 绑定到 subclass[1]
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '第二职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '无职介', value: null },
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' }
        ]
      },
      {
        key: 'subclass',
        index: 2,  // 绑定到 subclass[1]
        showCondition: {
          field: 'class',
          value: '多职阶'
        },
        name: '第三职阶',
        type: 'select',
        layout: 'third',
        options: [
          { label: '无职介', value: null },
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' }
        ]
      },
      {
        key: 'level',
        name: '卡牌等级',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无等级', value: null },
          { label: '等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '卡牌费用',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无费用', value: null },
          { label: '费用-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `费用-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'submit_icon',
        name: '投入图标',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '意志', value: '意志' },
          { label: '战力', value: '战力' },
          { label: '敏捷', value: '敏捷' },
          { label: '智力', value: '智力' },
          { label: '狂野', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '卡牌效果',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'flavor',
        name: '风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '胜利点',
        type: 'number',
        layout: 'full'
      },
    ]
  },
  '技能卡': {
    fields: [
      {
        key: 'name',
        name: '卡名',
        type: 'text',
        layout: 'full'
      },
      {
        key: 'class',
        name: '职阶',
        type: 'select',
        layout: 'full',
        options: [
          { label: '守护者', value: '守护者' },
          { label: '探求者', value: '探求者' },
          { label: '流浪者', value: '流浪者' },
          { label: '潜修者', value: '潜修者' },
          { label: '生存者', value: '生存者' },
          { label: '弱点', value: '弱点' },
          { label: '中立', value: '中立' }
        ]
      },
      {
        key: 'level',
        name: '卡牌等级',
        type: 'select',
        layout: 'full',
        options: [
          { label: '无等级', value: null },
          { label: '等级-0', value: 0 },
          ...Array.from({ length: 5 }, (_, i) => ({ label: `等级-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'submit_icon',
        name: '投入图标',
        type: 'multi-select',
        layout: 'full',
        options: [
          { label: '意志', value: '意志' },
          { label: '战力', value: '战力' },
          { label: '敏捷', value: '敏捷' },
          { label: '智力', value: '智力' },
          { label: '狂野', value: '狂野' }
        ]
      },
      {
        key: 'traits',
        name: '特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '卡牌效果',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'flavor',
        name: '风味文本',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'victory',
        name: '胜利点',
        type: 'number',
        layout: 'full'
      },
    ]
  },
  '调查员': {
    fields: [
      {
        key: 'name',
        name: '卡名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'subtitle',
        name: '副标题',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'attribute',
        index: 0,
        name: '意志',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'attribute',
        index: 1,
        name: '智力',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'attribute',
        index: 2,
        name: '战力',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'attribute',
        index: 3,
        name: '敏捷',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 9
      },
      {
        key: 'health',
        name: '生命值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无生命值', value: null },
          { label: '生命值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `生命值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'horror',
        name: '理智值',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无理智值', value: null },
          { label: '理智值-0', value: 0 },
          ...Array.from({ length: 99 }, (_, i) => ({ label: `理智值-${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'traits',
        name: '特性',
        type: 'string-array',
        layout: 'full'
      },
      {
        key: 'body',
        name: '卡牌效果',
        type: 'textarea',
        layout: 'full'
      },
      {
        key: 'flavor',
        name: '风味文本',
        type: 'textarea',
        layout: 'full'
      }
    ]
  },
};

export const cardTypeOptions = Object.keys(cardTypeConfigs).map(key => ({
  label: key,
  value: key
}));

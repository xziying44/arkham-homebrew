export interface FieldOption {
  label: string;
  value: string | number | null;
}

export interface FormField {
  key: string;
  name: string;
  type: 'text' | 'number' | 'select' | 'multi-select' | 'string-array';
  layout?: 'full' | 'half' | 'third' | 'quarter';
  min?: number;
  max?: number;
  options?: FieldOption[];
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
        key: 'class',
        name: '职阶',
        type: 'select',
        layout: 'half',
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
        layout: 'half',
        options: [
          { label: '无等级', value: null },
          { label: '0', value: 0 },
          ...Array.from({ length: 15 }, (_, i) => ({ label: `${i + 1}`, value: i + 1 }))
        ]
      },
      {
        key: 'cost',
        name: '卡牌费用',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无费用', value: null },
          { label: '0', value: 0 },
          ...Array.from({ length: 15 }, (_, i) => ({ label: `${i + 1}`, value: i + 1 }))
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
      }
    ]
  },
  '调查员': {
    fields: [
      {
        key: 'name',
        name: '姓名',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'title',
        name: '称号',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'willpower',
        name: '意志',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 6
      },
      {
        key: 'intellect',
        name: '智力',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 6
      },
      {
        key: 'combat',
        name: '战力',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 6
      },
      {
        key: 'agility',
        name: '敏捷',
        type: 'number',
        layout: 'quarter',
        min: 1,
        max: 6
      },
      {
        key: 'health',
        name: '生命值',
        type: 'number',
        layout: 'half',
        min: 1,
        max: 12
      },
      {
        key: 'sanity',
        name: '理智值',
        type: 'number',
        layout: 'half',
        min: 1,
        max: 12
      }
    ]
  },
  '资产': {
    fields: [
      {
        key: 'name',
        name: '名称',
        type: 'text',
        layout: 'half'
      },
      {
        key: 'cost',
        name: '消耗',
        type: 'number',
        layout: 'quarter',
        min: 0,
        max: 10
      },
      {
        key: 'uses',
        name: '使用次数',
        type: 'number',
        layout: 'quarter',
        min: 0
      },
      {
        key: 'slot',
        name: '槽位',
        type: 'select',
        layout: 'half',
        options: [
          { label: '无', value: null },
          { label: '手部', value: 'hand' },
          { label: '身体', value: 'body' },
          { label: '配件', value: 'accessory' },
          { label: '奥秘', value: 'arcane' },
          { label: '盟友', value: 'ally' }
        ]
      },
      {
        key: 'traits',
        name: '特性',
        type: 'string-array',
        layout: 'full'
      }
    ]
  }
};

export const cardTypeOptions = Object.keys(cardTypeConfigs).map(key => ({
  label: key,
  value: key
}));

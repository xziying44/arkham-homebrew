export default {
  // 卡片标题
  title: '📢 TTS脚本',

  // 脚本ID部分
  scriptId: {
    label: '🔖 脚本ID',
    placeholder: '输入自定义ID或使用随机生成',
    button: '🎲 随机',
  },

  // 调查员专用配置
  investigator: {
    extraTokenLabel: '🏷️ 额外标记（每轮一次）',
    extraTokenPlaceholder: '选择额外标记类型',
    attributesLabel: '🎯 能力值',
    willpower: '🧠 意志',
    intellect: '📚 智力',
    combat: '⚔️ 战力',
    agility: '⚡ 敏捷',
    phaseButtons: {
      label: '🎮 每阶段按钮配置',
      enable: '启用',
      disable: '禁用',
      idPlaceholder: '按钮ID',
      labelPlaceholder: '选择标签',
      colorPlaceholder: '选择颜色',
      addBtn: '➕ 添加按钮',
    },
  },

  // 支援卡/事件卡专用配置
  asset: {
    usesLabel: '🎯 入场标记配置',
    count: '数量',
    token: '令牌',
    tokenPlaceholder: '选择令牌类型',
    type: '类型',
    typePlaceholder: '选择标记类型',
    addBtn: '➕ 添加标记配置',
  },

  // GMNotes 预览部分
  preview: {
    label: '📋 GMNotes预览',
    copyBtn: '📋 复制',
    refreshBtn: '🔄 刷新',
  },

  // 通用按钮
  common: {
    deleteBtn: '🗑️ 删除',
  },

  // 下拉选项
  options: {
    extraToken: {
      none: '🚫 无标记',
      activate: '➡️ 启动',
      engage: '⚔️ 交战',
      evade: '💨 躲避',
      explore: '🔍 探索',
      fight: '👊 攻击',
      freeTrigger: '⚡ 免费',
      investigate: '🔎 调查',
      move: '👣 移动',
      parley: '🤝 谈判',
      playItem: '🎯 打出道具',
      reaction: '⭕ 反应',
      resource: '💰 资源',
      scan: '📡 扫描',
      spell: '✨ 法术',
      tome: '📚 书籍',
      guardian: '🛡️ 守护者',
      mystic: '🔮 潜修者',
      neutral: '⚖️ 中立',
      rogue: '🗡️ 流浪者',
      seeker: '📖 探求者',
      survivor: '🔧 生存者',
    },
    tokenTypes: {
      resource: '📋 资源',
      damage: '🔥 伤害',
      horror: '👻 恐怖',
      doom: '💀 厄运',
      clue: '🔍 线索',
    },
    resourceTypes: {
      ammo: '🔫 弹药',
      resource: '💰 资源',
      bounty: '🎯 赏金',
      charge: '⚡ 充能',
      evidence: '🔍 证据',
      secret: '🤫 秘密',
      supply: '📦 补给',
      offering: '🕯️ 贡品',
    },
    // 固定用途的令牌类型
    fixedTokenTypes: {
      damage: '🔥 伤害',
      horror: '👻 恐怖',
      doom: '💀 厄运',
      clue: '🔍 线索',
    },
  },

  // 消息提示
  messages: {
    copySuccess: 'GMNotes已复制到剪贴板',
    copyError: '复制失败，请手动复制',
    regenerateSuccess: 'GMNotes已重新生成',
  },
}

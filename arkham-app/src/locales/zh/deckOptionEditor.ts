export default {
  // 组件标题
  title: '🎯 牌库选项编辑器',
  currentOptions: '当前牌库选项',
  addOption: '添加选项',
  noOptions: '暂无牌库选项',
  option: '选项',
  editing: '编辑中',
  edit: '编辑',
  save: '保存',
  cancel: '取消',
  delete: '删除',

  // 选项配置
  optionId: '选项ID',
  optionIdPlaceholder: '输入选项ID（可选）',

  // 基础过滤条件
  basicFilters: '📊 基础过滤条件',
  cardType: '卡牌类型',
  selectCardTypes: '选择卡牌类型',
  faction: '职阶',
  selectFactions: '选择职阶',
  traits: '特性',
  addTrait: '添加特性',
  slots: '槽位',
  selectSlots: '选择槽位',
  uses: '使用标记',
  selectUses: '选择使用标记',

  // 文本匹配
  textMatch: '📝 文本匹配',
  textContains: '文本包含',
  addText: '添加文本',
  textExact: '精确匹配',
  addExactText: '添加精确文本',

  // 等级系统
  levelSystem: '🎚️ 等级系统',
  levelRange: '等级范围',
  level: '等级',
  minLevel: '最低等级',
  maxLevel: '最高等级',

  // 数量限制
  quantityLimit: '🔢 数量限制',
  limit: '数量限制',
  limitPlaceholder: '最大选择数量',

  // 选择机制
  selectionMechanism: '🎲 选择机制',
  selectSelectionType: '请选择选择机制（只能选择一种）',
  noneSelection: '无选择机制',
  factionSelect: '职阶选择',
  selectFactionForSelection: '选择可供选择的职阶',
  deckSizeSelect: '牌库大小选择',
  selectDeckSizes: '选择可选的牌库大小',
  advancedSelect: '高级属性选择',
  selectionTypeNames: {
    faction: '职阶选择',
    deckSize: '牌库大小',
    advanced: '高级属性选择'
  },
  defaultAdvancedName: '高级属性选择',
  newOptionItem: '选项 {index}',

  // 高级规则
  advancedRules: '⚙️ 高级规则',
  not: '否定条件',
  notEnabled: '启用否定条件',
  notDisabled: '禁用否定条件',
  atLeast: '至少条件',
  atLeastEnabled: '启用至少条件',
  atLeastDisabled: '禁用至少条件',
  minCount: '最小数量',
  selectAtLeastTypes: '选择至少包含的卡牌类型',

  // JSON预览
  finalPreview: '📋 最终配置预览',
  copyJson: '复制JSON',
  refresh: '刷新',

  // 验证消息
  validation: {
    nameRequired: '选项名称不能为空',
    itemNameRequired: '选项项 "{itemId}" 的名称不能为空'
  },

  // 消息提示
  messages: {
    optionAdded: '牌库选项已添加',
    optionSaved: '牌库选项已保存',
    optionDeleted: '牌库选项已删除',
    editCancelled: '编辑已取消',
    copySuccess: 'JSON已复制到剪贴板',
    copyError: '复制失败，请手动复制',
    refreshSuccess: '预览已刷新'
  }
}
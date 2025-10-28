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
  optionName: '选项名称',
  optionNamePlaceholder: '名称通常与ID一致，可手动修改',

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
  selectionMechanismLabel: '选择机制',
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

  // 其他条件
  otherConditions: '其他条件',
  negativeCondition: '否定条件',
  atLeastCondition: '至少条件',
  minimumCount: '最少数量',
  conditionType: '条件类型',
  factionCount: '职阶',
  typeCount: '类型',
  satisfiedCount: '满足数量',

  // 可选属性列表
  optionalAttributes: '可选属性列表',
  addItemOption: '添加选项',
  noOptionalAttributes: '暂无可选属性',

  // 牌组构建顺序说明
  deckBuildingOrder: {
    title: '⚠️ 牌组构建选项顺序说明',
    description: '调查员牌组构建选项中，顺序会影响卡池。请按照正确的顺序设置选项以确保卡池计算准确。',
    exampleTitle: '示例：平行记者',
    exampleDescription: '正确的构建顺序应该是：',
    order1: '1. 诅咒萦绕中立卡牌等级 0-5',
    order2: '2. 诅咒萦绕卡牌等级 0-4',
    order3: '3. 否定条件，幸运、祝福卡牌等级 0-5',
    order4: '4. 探求者(🌐)等级 0-3',
    order5: '5. 中立卡牌等级 0-5',
    order6: '6. 局势卡牌等级 0-4',
    order7: '7. 流浪者(💵)等级0，限制5张',
    note: '注意：错误的顺序可能导致某些卡牌无法正确加入卡池。'
  },
  removeItem: '删除',
  itemId: 'ID',
  itemName: '名称',
  itemNameRequired: '名称（必填）',
  items: '项',

  // 卡牌类型选项
  cardTypes: {
    asset: '支援卡',
    event: '事件卡',
    skill: '技能卡'
  },

  // 职阶选项
  factions: {
    guardian: '守护者',
    seeker: '探求者',
    rogue: '流浪者',
    mystic: '潜修者',
    survivor: '生存者',
    neutral: '中立'
  },

  // 槽位选项
  slotOptions: {
    hand: '手部',
    arcane: '奥术',
    accessory: '饰品',
    body: '身体',
    ally: '盟友',
    tarot: '塔罗',
    sanity: '理智',
    health: '生命'
  },

  // 使用标记选项
  usesOptions: {
    charge: '充能',
    ammo: '弹药',
    supply: '补给',
    secret: '秘密',
    resource: '资源',
    evidence: '证据',
    offering: '供品'
  },

  // 牌库大小选项
  deckSizes: {
    20: '20张',
    25: '25张',
    30: '30张',
    35: '35张',
    40: '40张',
    50: '50张',
    unit: '张'
  },

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
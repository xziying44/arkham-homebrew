export default {
  title: '多语言卡牌支持',
  description: '管理卡牌支持的多语言字体与文本配置。',
  languageList: {
    title: '语言列表',
    empty: '暂未配置任何语言，请先新增语言。',
  },
  sections: {
    basic: '基础信息',
    fonts: '字体配置',
    texts: '文本映射',
    fontFolder: '字体目录',
  },
  fields: {
    name: '语言名称',
    code: '语言代码',
  },
  fonts: {
    hint: '每种语言需要配置标题、副标题、卡牌类型、特性、粗体、正文、风味文本和收藏信息的字体。',
    headers: {
      category: '类别',
      name: '字体名称',
      size: '尺寸百分比',
      offset: '垂直偏移',
    },
    categories: {
      title: '标题',
      subtitle: '副标题',
      card_type: '卡牌类型',
      trait: '特性',
      bold: '加粗',
      body: '正文',
      flavor: '风味文本',
      collection_info: '收藏信息',
    },
  },
  texts: {
    hint: '文本映射用于多语言卡牌模板中的各种标签，如卡牌类型、胜利、显现等。键集合由系统内置，前端仅允许编辑各语言的显示文本。',
  },
  fontFolder: {
    hint: '你可以在应用目录下创建 fonts 文件夹来添加自定义字体。Windows 用户在程序运行目录下创建，macOS 用户在 ~/Documents/ArkhamCardMaker 目录下创建。将字体文件放入该文件夹后，点击刷新按钮即可更新字体列表。',
  },
  actions: {
    addLanguage: '新增语言',
    delete: '删除',
    cancel: '取消',
    refreshFonts: '刷新字体列表',
    save: '保存语言配置',
  },
  forms: {
    newLanguage: {
      title: '新增语言',
      templateLabel: '选择模板语言',
      templateHint: '选择一个现有语言作为字体配置模板',
      templateNone: '空模板（默认配置）',
    },
  },
  deleteDialog: {
    title: '删除语言',
    warning: '警告',
    message: '删除语言「{name}」可能会导致使用该语言的卡牌显示异常，是否确认删除？',
  },
  defaults: {
    newLanguageName: '新语言',
  },
  messages: {
    loadFailed: '加载语言配置失败',
    saveSuccess: '语言配置保存成功',
    saveFailed: '语言配置保存失败',
    deleteSuccess: '语言删除成功',
    deleteFailed: '语言删除失败',
    refreshFontsSuccess: '字体列表已刷新',
    refreshFontsFailed: '刷新字体列表失败',
  },
};

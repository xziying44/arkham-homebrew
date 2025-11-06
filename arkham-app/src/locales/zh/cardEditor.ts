export default {
  // FormField 组件
  field: {
    pleaseEnter: '请输入{name}',
    pleaseSelect: '请选择{name}',
    add: '添加{name}',
    input: '输入{name}',
    addItem: '添加',
    viewFieldDescription: '查看字段说明',
    fieldDescription: '字段说明',
    help: '帮助',
    close: '关闭',
    delete: '删除',
    clickOrDragToUpload: '点击或者拖拽图片到该区域来上传',
    supportedFormats: '支持 JPG、PNG、GIF、WebP 等格式，大小不超过 {size}',
    noAvailableEncounterGroups: '无可用遭遇组 (请检查配置)',
    loadEncounterGroupsFailed: '加载遭遇组列表失败，请检查遭遇组目录配置',
    unsupportedImageFormat: '不支持的图片格式，请选择 JPG、PNG、GIF、WebP 或 SVG 文件',
    fileSizeExceeded: '文件大小超过限制，最大支持 {size}',
    fileReadFailed: '文件读取失败',
    imageProcessFailed: '图片处理失败，请重试',
    editItem: '编辑项目',
    moveUp: '上移',
    moveDown: '下移',
    edit: '编辑'
  },

  // FormEditPanel 组件
  panel: {
    close: '关闭',
    cardEditor: '卡牌编辑器',
    importJson: '导入JSON',
    viewJson: '查看JSON',
    selectCardFileToEdit: '请在文件管理器中选择一个卡牌文件(.card)进行编辑',
    noCardSelected: '尚未选择卡牌',
    createOrSelectCard: '创建或选择卡牌进行编辑',
    howToCreateCard: '如何创建卡牌？',
    clickPlusButton: '点击顶部的 "+" 按钮创建新卡牌',
    rightClickFileTree: '右键点击文件树节点创建新卡牌',
    selectExistingCard: '或者选择一个现有的 .card 文件进行编辑',
    getStarted: '开始制作您的卡牌吧！',

    // AI 助手
    aiAssistant: '🤖 AI制卡助手',
    describeYourCard: '描述你想要的卡牌',
    cardDescriptionPlaceholder: '例如：创建一个火属性的攻击法术卡牌，名字叫火球术，造成5点伤害，消耗3点法力...',
    generateCard: '生成卡牌',
    generating: '生成中...',
    stopGeneration: '停止生成',
    clearResult: '清空结果',
    aiThinking: 'AI正在思考中...',
    generationComplete: '生成完成',
    aiThoughtProcess: '💭 AI思考过程：',
    generatedCardData: '📋 生成的卡牌数据：',
    validationSuccess: '✅ 验证成功',
    validationFailed: '❌ 验证失败',
    cardDataValid: '卡牌数据格式正确，可以导入到编辑器中',
    importToEditor: '导入到编辑器',

    // 卡牌类型
    cardType: '卡牌类型',
    selectCardType: '选择卡牌类型',
    frontSide: '正面',
    backSide: '反面',

    language: "语言",
    selectLanguage: "选择语言",
    chinese: "中文",
    english: "英语",
    polski: "波兰语",

    // 卡牌属性
    cardProperties: '卡牌属性',

    // 卡牌信息
    cardInfo: '卡牌信息',
    advancedTextLayout: '高级文本布局',
    illustrator: '🎨 插画作者',
    encounterGroupNumber: '📋 遭遇组序号',
    cardNumber: '📋 卡牌序号',
    cardRemarks: '📝 卡牌备注信息',
    cardQuantity: '卡牌数量',
    copyright: '版权信息',

    // 操作按钮
    saveCard: '保存卡牌',
    saveAll: '全部保存',
    previewCard: '预览卡图',
    exportImage: '导出图片',
    reset: '重置',
    convertToV2: '转换为2.0版本',

    // JSON 模态框
    currentJsonData: '当前JSON数据',
    copyJson: '复制JSON',

    // 导入 JSON 模态框
    importJsonData: '导入JSON数据',
    pasteJsonData: '请粘贴JSON数据',
    pasteJsonPlaceholder: '请粘贴要导入的JSON数据...',
    cancel: '取消',
    import: '导入',

    // 保存确认对话框
    saveConfirmation: '保存确认',
    unsavedChanges: '未保存的修改',
    hasUnsavedChangesMessage: '当前文件有未保存的修改，是否保存？',
    changesWillBeLost: '如果不保存，您的修改将会丢失。',
    dontSave: '不保存',
    save: '保存',

    // 快捷键
    ctrlS: '(Ctrl+S)',

    // 消息提示
    noFileSelected: '未选择文件',
    cardSavedSuccessfully: '卡牌保存成功',
    saveCardFailed: '保存卡牌失败',
    loadCardDataFailed: '加载卡牌数据失败',
    loadFromCacheFailed: '从暂存加载失败',
    cardDataValidationFailed: '卡牌数据验证失败',
    generateCardImageFailed: '生成卡图失败',
    pleaseEnterCardNameAndType: '请先填写卡牌名称和类型',
    cardPreviewGenerated: '卡图预览生成成功',
    previewCardImageFailed: '预览卡图失败',
    noCardFileSelected: '未选择卡牌文件',
    imageExported: '图片已导出: {filename}',
    exportImageFailed: '导出图片失败',
    formReset: '表单已重置',
    jsonCopiedToClipboard: 'JSON已复制到剪贴板',
    copyFailed: '复制失败，请手动选择文本复制',
    pleaseEnterJsonData: '请输入JSON数据',
    jsonDataImportedSuccessfully: 'JSON数据导入成功',
    importFailed: '导入失败',
    invalidJsonFormat: '无效的JSON格式',
    noUnsavedFiles: '没有未保存的文件',
    saveAllSuccess: '成功保存 {count} 个文件',
    saveAllPartial: '保存了 {success} 个文件，{failed} 个失败',
    saveAllFailed: '保存失败',

    // AI 相关消息
    pleaseEnterPrompt: '请输入提示词',
    aiGenerationFailed: 'AI生成失败',
    validationError: '验证失败',
    noValidAiResult: '没有有效的AI生成结果可以导入',
    aiDataImportedSuccessfully: 'AI生成的卡牌数据已成功导入到编辑器',
    importAiResultFailed: '导入AI结果失败',
    aiGenerationCompleted: 'AI生成完成但没有返回有效内容',
    aiReturnedError: 'AI返回错误',
    missingRequiredFields: '缺少必要字段',
    jsonParseError: 'JSON解析错误',

    // 版本转换
    convertToV2Confirm: '转换为2.0版本',
    versionConvertInfo: '版本转换信息',
    versionConvertDescription: '将当前卡牌转换为2.0版本（双面卡牌），这将为卡牌创建一个背面。',
    convertWillCreateBack: '系统将根据卡牌类型自动设置合适的背面类型。',
    currentCard: '当前卡牌',
    currentType: '当前类型',
    autoSetBackType: '将自动设置背面类型',
    confirmConvert: '确认转换',
    needCardNameAndType: '请先填写卡牌名称和类型',
    versionConvertSuccess: '成功转换为2.0版本！',
    versionConvertFailed: '版本转换失败'
  },

  // IllustrationLayoutEditor component
  illustrationLayout: {
    title: '插画布局设置',
    showSettings: '🎨 展开插画布局设置',
    hideSettings: '🎨 收起插画布局设置',
    layoutMode: '布局模式',
    autoCenter: '自动居中',
    custom: '自定义',
    zoomHint: '按住 Alt + 滚动以缩放',
    offset: '偏移 (Offset)',
    xAxis: 'X 轴',
    yAxis: 'Y 轴',
    crop: '裁剪 (px) - 原图 {width}x{height}',
    top: '上',
    bottom: '下',
    left: '左',
    right: '右',
    scale: '缩放 (Scale)',
    ratio: '比例',
    rotation: '旋转 (Rotation)',
    angle: '角度',
    flip: '镜像翻转 (Flip)',
    horizontal: '水平',
    vertical: '垂直'
  },

  // TextBoundaryEditor component
  textBoundary: {
    title: '文本边界调整',
    body: {
      title: '正文边界',
      top: '上边界',
      bottom: '下边界',
      left: '左边界',
      right: '右边界'
    },
    flavor: {
      title: '风味文本边距',
      padding: '内边距'
    },
    helpTitle: '使用提示',
    helpText: '正文边界：正数向外扩展，负数向内收缩（范围: -50px ~ +50px）。风味内边距：控制风味文本的padding值（范围: 0px ~ 100px）'
  }
}

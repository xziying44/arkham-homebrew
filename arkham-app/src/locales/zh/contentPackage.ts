export default {
  title: '内容包管理',
  languages: {
    zh: '中文',
    en: '英文'
  },
  packageTypes: {
    investigators: '调查员卡',
    player_cards: '玩家卡',
    campaign: '剧本卡'
  },
  editor: {
    tabs: {
      info: '基础信息',
      cards: '卡牌管理',
      export: '导出设置'
    },
    sections: {
      banner: '封面预览',
      basicInfo: '基础信息',
      cards: '卡牌管理',
      export: '导出设置'
    },
    fields: {
      code: '标识ID',
      name: '名称',
      description: '描述',
      author: '作者',
      language: '语言',
      types: '内容包类型',
      status: '状态',
      dateUpdated: '更新时间',
      generator: '生成器',
      externalLink: '外部地址',
      banner: '封面'
    },
    editMeta: {
      title: '编辑内容包信息',
      namePlaceholder: '请输入内容包名称',
      descriptionPlaceholder: '请输入内容包描述',
      authorPlaceholder: '请输入作者名称',
      externalLinkPlaceholder: '可选，请输入外部链接地址',
      bannerUrl: '封面URL',
      bannerUrlPlaceholder: '请输入封面图片的网络地址',
      bannerFile: '封面文件',
      dragToUpload: '点击或拖拽图片到此处上传',
      uploadHint: '支持 JPG、PNG、GIF 等格式',
      saveSuccess: '保存成功'
    },
    noBanner: '暂无封面'
  },
  actions: {
    newPackage: '新建内容包',
    refresh: '刷新',
    delete: '删除',
    cancel: '取消',
    create: '创建',
    save: '保存'
  },
  panels: {
    myPackages: '我的内容包'
  },
  packageList: {
    empty: '暂无内容包',
    emptyDesc: '点击右上角按钮创建第一个内容包'
  },
  noSelection: {
    title: '请选择内容包',
    description: '从左侧列表选择一个内容包进行编辑，或创建新的内容包'
  },
  forms: {
    newPackage: {
      title: '新建内容包',
      name: '名称',
      namePlaceholder: '请输入内容包名称',
      description: '描述',
      descriptionPlaceholder: '请输入内容包描述',
      author: '作者',
      authorPlaceholder: '请输入作者名称',
      language: '语言',
      types: '内容包类型',
      externalLink: '外部地址',
      externalLinkPlaceholder: '可选，请输入外部链接地址',
      banner: '封面',
      bannerUrl: '封面URL',
      bannerUrlPlaceholder: '请输入封面图片的网络地址',
      bannerFile: '封面文件',
      dragToUpload: '点击或拖拽图片到此处上传',
      uploadHint: '支持 JPG、PNG、GIF 等格式'
    },
    validation: {
      nameRequired: '请输入名称',
      nameLength: '名称长度应在1-100字符之间',
      namePattern: '名称不能包含特殊字符',
      descriptionRequired: '请输入描述',
      descriptionLength: '描述长度应在1-1000字符之间',
      authorRequired: '请输入作者',
      authorLength: '作者长度应在1-100字符之间',
      languageRequired: '请选择语言',
      typesRequired: '请至少选择一种内容包类型'
    }
  },
  deleteDialog: {
    title: '删除确认',
    warning: '警告',
    message: '确定要删除内容包 "{name}" 吗？此操作不可撤销。'
  },
  messages: {
    refreshSuccess: '刷新成功',
    loadFailed: '加载失败',
    createSuccess: '创建成功',
    createFailed: '创建失败',
    saveSuccess: '保存成功',
    saveFailed: '保存失败',
    deleteSuccess: '删除成功',
    deleteFailed: '删除失败',
    readBannerFailed: '读取封面文件失败',
    addCardSuccess: '成功添加 {count} 张卡牌',
    addCardFailed: '添加卡牌失败',
    cardDeleted: '卡牌已删除',
    bannerUploadSuccess: '封面上传成功',
    cardUploadSuccess: '卡牌上传成功',
    batchUploadSuccess: '批量上传成功！共上传 {count} 张卡牌',
    batchUploadCompleted: '批量上传完成，成功 {success} 张，失败 {failure} 张',
    noCardsToUpload: '没有需要上传的卡牌',
    imageHostConfigIncomplete: '图床配置不完整，请先配置图床信息',
    batchUploadFailed: '批量上传失败',
    batchPreparing: '准备批量上传...',
    batchStarting: '开始批量上传...',
    batchUploading: '正在上传: {filename} ({index}/{total})'
  },
  upload: {
    button: {
      uploadToCloud: '上传云端',
      reuploadToCloud: '重新上传云端',
      uploadCard: '上传此卡',
      reupload: '重新上传'
    },
    title: {
      uploadBannerToCloud: '上传封面到云端',
      uploadCardToCloud: '上传卡牌到云端',
      batchUploadToCloud: '批量上传卡牌到云端',
      configureBatchUpload: '配置批量上传'
    },
    status: {
      uploadedToCloud: '已上传到云端',
      savedToLocal: '已保存到本地'
    },
    info: {
      willUploadAllV2Cards: '将为所有v2.0卡牌批量配置图床并上传。已上传过的卡牌将被覆盖更新。',
      v2CardCount: 'v2.0卡牌总数',
      cloudUploaded: '已上传云端',
      v2CardList: 'v2.0卡牌列表',
      uploadProgress: '上传进度',
      batchUploadCompleted: '批量上传完成: 成功 {success} 张，失败 {failure} 张'
    },
    action: {
      startConfiguration: '开始配置 ({count} 张)',
      startUpload: '开始上传'
    }
  },
  cards: {
    empty: {
      title: '还没有添加任何卡牌',
      description: '点击上方"添加卡牌"按钮开始添加'
    },
    status: {
      unsupported: '不支持 (v{version})',
      supported: 'v{version}',
      generating: '生成失败',
      generationStopped: '已中止',
      versionCheckFailed: '版本检查失败'
    },
    actions: {
      addCard: '添加卡牌'
    },
    dialog: {
      title: '添加卡牌'
    }
  },
  export: {
    notImplemented: {
      title: '导出功能开发中',
      description: '该功能将在后续版本中实现'
    }
  }
}
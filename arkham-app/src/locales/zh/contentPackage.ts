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
  statusOptions: {
    draft: '草稿',
    alpha: 'Alpha版',
    beta: 'Beta版',
    complete: '完成版',
    final: '最终版'
  },
  editor: {
    tabs: {
      info: '基础信息',
      cards: '卡牌管理',
      encounters: '遭遇组',
      export: '导出设置'
    },
    sections: {
      banner: '封面预览',
      basicInfo: '基础信息',
      cards: '卡牌管理',
      encounters: '遭遇组管理',
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
      languagePlaceholder: '请选择内容包语言',
      typesPlaceholder: '请选择内容包类型（可多选）',
      statusPlaceholder: '请选择内容包状态',
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
      typesRequired: '请至少选择一种内容包类型',
      atLeastOneType: '请至少选择一种内容包类型',
      statusRequired: '请选择内容包状态'
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
    },
    tts: {
      title: '导出到TTS物品',
      description: '将内容包导出为TTS可用的JSON文件，包含所有已生成图片的卡牌（支持云端图片和本地图片）',
      packageName: '内容包名称',
      cardCount: '卡牌数量',
      cardsWithImages: '有图片的卡牌',
      exportStatus: '导出状态',
      canExport: '可导出',
      needImages: '需要生成图片',
      cardExportStatus: '卡牌导出状态',
      exportTTSItems: '导出TTS物品',
      exportLogs: '导出日志',
      close: '关闭',
      openFolder: '打开文件夹'
    },
    arkhamdb: {
      title: '导出到ArkhamDB格式',
      description: '将内容包导出为ArkhamDB格式的JSON文件，适用于arkham.build扩展包制作',
      packageName: '内容包名称',
      cardCount: '卡牌数量',
      packageCode: '内容包代码',
      alwaysExportable: '可导出',
      exportStatus: '导出状态',
      exportDescription: '导出说明',
      exportDetails: [
        '• 导出的JSON文件包含所有卡牌的ArkhamDB格式数据',
        '• 可直接用于arkham.build网站的扩展包上传',
        '• 包含完整的卡牌属性、标签和元数据信息'
      ],
      exportArkhamDB: '导出ArkhamDB格式',
      exportLogs: 'ArkhamDB导出日志',
      close: '关闭',
      openFolder: '打开文件夹',
      success: {
        ttsExportSuccess: 'TTS物品导出成功！',
        arkhamdbExportSuccess: 'ArkhamDB格式导出成功！'
      }
    }
  },
  tags: {
    edit: {
      title: '编辑卡牌标签 - {filename}',
      description: '为卡牌设置特殊属性标签，这些标签将在导出时保留',
      permanent: {
        label: '永久卡牌',
        description: '永久卡牌不占用卡组张数，不会从游戏中移除，且开场设置于场上'
      },
      exceptional: {
        label: '卓越卡牌',
        description: '卓越卡牌花费两倍经验值，且只能购买一份'
      },
      myriad: {
        label: '无数卡牌',
        description: '无数卡牌可以在卡组中放入3张，且购买多张时只需花费一份经验'
      },
      exile: {
        label: '可放逐',
        description: '可放逐卡牌可以在特定条件下从游戏中移除'
      },
      preview: '当前标签预览',
      save: '保存',
      cancel: '取消'
    }
  },
  encounters: {
    empty: {
      title: '还没有遭遇组',
      description: '点击刷新按钮加载遭遇组'
    },
    error: {
      noPackagePath: '内容包路径无效',
      refreshFailed: '刷新遭遇组失败: {message}',
      noEncountersToUpload: '没有需要上传的遭遇组',
      noIconData: '没有找到遭遇组图标数据',
      batchUploadFailed: '批量上传失败: {message}'
    },
    success: {
      refreshSuccess: '成功刷新 {count} 个遭遇组',
      uploadSuccess: '遭遇组上传成功',
      batchUploadSuccess: '批量上传成功！共上传 {count} 个遭遇组'
    },
    messages: {
      batchPreparing: '准备批量上传...',
      batchStarting: '开始批量上传...',
      batchUploading: '正在上传: {name} ({index}/{total})',
      batchUploadCompleted: '批量上传完成，成功 {success} 个，失败 {failure} 个'
    }
  },
  upload: {
    button: {
      uploadToCloud: '上传云端',
      reuploadToCloud: '重新上传云端',
      uploadCard: '上传此卡',
      reupload: '重新上传'
    },
    dialog: {
      selectImageHost: '选择图床服务',
      localMode: '本地测试',
      localModeDescription: '本地测试模式：只导出图片到本地，不上传到云端，使用 file:/// 格式URL',
      cloudinaryConfig: 'Cloudinary 配置',
      cloudName: 'Cloud Name',
      apiKey: 'API Key',
      apiSecret: 'API Secret',
      folder: '文件夹',
      folderPlaceholder: '文件夹名称（可选）',
      imgbbConfig: 'ImgBB 配置',
      expirationHours: '过期时间（小时）',
      expirationPlaceholder: '0（永不过期）',
      exportFormat: '导出格式',
      imageQuality: '图片质量',
      uploadProgress: '上传进度',
      uploadLogs: '上传日志',
      preparingUpload: '准备上传...',
      configSaved: '配置已保存',
      preparingImages: '准备导出图片...',
      preparingCloudUpload: '准备上传到云端...',
      updatingData: '更新内容包数据...',
      uploadComplete: '上传成功',
      preparingBatchConfig: '准备批量上传配置...',
      preparingBatchUpload: '准备批量上传...',
      batchUploadComplete: '批量上传完成',
      bannerInfo: '封面信息',
      cardInfo: '卡牌信息',
      encounterInfo: '遭遇组信息',
      encounterName: '遭遇组名称',
      encounterCode: '遭遇组代码',
      currentStatus: '当前状态',
      noIcon: '无图标',
      uploadInfo: '上传信息',
      imageUploadSuccess: '图片上传成功: {filename}',
      imageUploadFailed: '图片上传失败: {filename} - {error}',
      bannerUploadComplete: '封面上传完成',
      cardUploadComplete: '卡牌上传完成',
      batchUploadCompleteLog: '批量上传完成',
      cardUploadSuccessLog: '卡牌 {filename} 上传成功',
      cardUploadFailedLog: '卡牌 {filename} 上传失败: {error}',
      imageExportStart: '开始导出图片: {filename}',
      imageExportSuccess: '图片导出成功: {filename}',
      imageExportFailed: '图片导出失败: {filename}',
      imageUploadStart: '开始上传图片: {filename}',
      imageUploadSuccessUrl: '图片上传成功: {url}',
      localModeUrl: '本地模式，使用本地URL: {url}',
      completeConfigInfo: '将为所有v2.0卡牌批量配置图床并上传。已上传过的卡牌将被覆盖更新。',
      playerCardbackDetected: '检测到玩家卡背，使用预定义URL',
      encounterCardbackDetected: '检测到遭遇卡背，使用预定义URL',
      uploadingImage: '上传图片 {index}/{total}...'
    },
    error: {
      configIncomplete: '请完善图床配置信息',
      noBannerData: '没有找到封面图片数据',
      uploadFailed: '上传失败: {message}',
      packagePathInvalid: '内容包路径无效',
      noCardsToUpload: '没有需要上传的卡牌',
      batchUploadFailed: '批量上传失败: {message}',
      cannotGetWorkspacePath: '无法获取工作空间路径',
      configLoadFailed: '加载配置失败: {message}',
      configSaveFailed: '保存配置失败: {message}',
      exportFailed: '导出失败: {message}'
    },
    success: {
      configSaveSuccess: '配置保存成功',
      localModeNoSave: '本地测试模式，无需保存配置'
    },
    status: {
      cloud: '云端',
      local: '本地',
      noImage: '无图片',
      uploaded: '已上传',
      pending: '待上传'
    },
    title: {
      uploadBannerToCloud: '上传封面到云端',
      uploadCardToCloud: '上传卡牌到云端',
      uploadEncounterToCloud: '上传遭遇组到云端',
      batchUploadToCloud: '批量上传卡牌到云端',
      batchUploadEncountersToCloud: '批量上传遭遇组到云端',
      configureBatchUpload: '配置批量上传'
    },
    info: {
      v2CardCount: 'v2.0卡牌总数',
      cloudUploaded: '已上传云端',
      v2CardList: 'v2.0卡牌列表',
      uploadProgress: '上传进度',
      batchUploadCompleted: '批量上传完成: 成功 {success} 张，失败 {failure} 张',
      totalEncounters: '遭遇组总数',
      totalItems: '项目总数'
    },
    action: {
      startConfiguration: '开始配置 ({count} 张)',
      startUpload: '开始上传',
      uploadToCloud: '上传云端'
    }
  },
  common: {
    editInfo: '编辑信息',
    save: '保存',
    unnamedPackage: '未命名内容包',
    unknown: '未知',
    unknownAuthor: '未知作者',
    noDescription: '暂无描述',
    batchUpload: '批量上传',
    addCard: '添加卡牌',
    generationFailed: '生成失败',
    unsupported: '不支持',
    editTags: '编辑标签',
    permanent: '永久',
    exceptional: '卓越',
    myriad: '无数',
    exile: '可放逐',
    cancel: '取消',
    uploadToCloud: '上传云端',
    close: '关闭',
    openFolder: '打开文件夹',
    cardTagsSaved: '卡牌标签保存成功',
    refresh: '刷新'
  }
}
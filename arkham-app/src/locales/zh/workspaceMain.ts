export default {
  layout: {
    fileTree: '文件树',
    imagePreview: '图片预览',
    adjustWidth: '拖拽调整宽度'
  },
  sidebar: {
    title: '工作区',
    backToHome: '返回首页',
    navItems: {
      workspace: '工作区',
      deckBuilder: '牌库制作',
      ttsItems: 'TTS物品',
      settings: '其他设置',
      about: '关于'
    }
  },
  fileTree: {
    title: '文件资源管理器',
    adjustWidth: '拖拽调整文件树宽度',
    emptyText: '暂无文件',
    actions: {
      goBack: '返回',
      refresh: '刷新',
      create: '新建',
      close: '关闭'
    },
    contextMenu: {
      newFolder: '新建文件夹',
      newCard: '新建卡牌',
      batchExport: '批量导出',
      rename: '重命名',
      delete: '删除'
    },
    createFolder: {
      title: '新建文件夹',
      label: '文件夹名称',
      placeholder: '请输入文件夹名称',
      cancel: '取消',
      confirm: '确定'
    },
    createCard: {
      title: '新建卡牌',
      label: '卡牌文件名',
      placeholder: '请输入卡牌文件名（自动添加.card扩展名）',
      cancel: '取消',
      confirm: '确定'
    },
    rename: {
      title: '重命名',
      filenameLabel: '文件名',
      filenamePlaceholder: '请输入文件名',
      extensionLabel: '扩展名',
      extensionPlaceholder: '请输入扩展名（不含点号）',
      preview: '预览:',
      cancel: '取消',
      confirm: '确定'
    },
    delete: {
      title: '删除确认',
      warning: '警告',
      confirmText: '此操作不可恢复，请确认是否删除？',
      pathLabel: '路径:',
      folderPrefix: '文件夹:',
      filePrefix: '文件:',
      cancel: '取消',
      confirm: '删除'
    },
    batchExport: {
      title: '批量导出卡牌',
      directory: '目标目录',
      foundCards: '发现卡牌',
      cpuCores: 'CPU核心数',
      threadsUsing: '使用线程数',
      processing: '正在处理',
      completed: '批量导出完成',
      currentTasks: '当前处理任务',
      logs: '导出日志',
      cancel: '取消',
      stop: '停止',
      start: '开始导出',
      close: '关闭',
      scanning: '正在扫描目录...',
      noCardsFound: '目录中没有找到卡牌文件',
      scanFailed: '扫描目录失败',
      foundCardsLog: '发现卡牌文件',
      usingThreads: '使用线程数',
      startLog: '开始批量导出',
      abortedLog: '批量导出已中止',
      processingLog: '正在处理',
      validationFailed: '卡牌数据验证失败',
      exportSuccess: '导出成功',
      exportFailed: '导出失败',
      failedExports: '导出失败数量',
      completedLog: '批量导出完成',
      allCompleted: '成功导出 {successCount} 张卡牌，共 {totalCount} 张！',
      partialSuccess: '导出完成：成功 {successCount} 张，失败 {errorCount} 张',
      stopping: '正在停止批量导出...',
      progressDetail: '进度详情',
      total: '总计',
      remaining: '剩余',
      userStopped: '用户停止了批量导出'
    },
    validation: {
      folderNameRequired: '请输入文件夹名称',
      folderNameLength: '文件夹名称长度在1-50个字符',
      folderNameInvalid: '文件夹名称不能包含特殊字符 \\/:*?"<>',
      cardNameRequired: '请输入卡牌文件名',
      cardNameLength: '卡牌文件名长度在1-50个字符',
      cardNameInvalid: '卡牌文件名不能包含特殊字符 \\/:*?"<>',
      filenameRequired: '请输入文件名',
      filenameLength: '文件名长度在1-50个字符',
      filenameInvalid: '文件名不能包含特殊字符 \\/:*?"<>.',
      extensionInvalid: '扩展名不能包含特殊字符 \\/:*?"<>.'
    },
    messages: {
      loadFailed: '加载文件树失败',
      loadFailedNetwork: '加载文件树失败，请检查服务连接',
      createFolderSuccess: '文件夹创建成功',
      createFolderFailed: '创建文件夹失败',
      createFolderFailedRetry: '创建文件夹失败，请重试',
      createCardSuccess: '卡牌创建成功',
      createCardFailed: '创建卡牌失败',
      createCardFailedRetry: '创建卡牌失败，请重试',
      renameSuccess: '重命名成功',
      renameFailed: '重命名失败',
      renameFailedRetry: '重命名失败，请重试',
      deleteSuccess: '删除成功',
      deleteFailed: '删除失败',
      deleteFailedRetry: '删除失败，请重试'
    }
  },
  imagePreview: {
    title: '图片预览',
    adjustWidth: '拖拽调整预览区宽度',
    emptyText: '选择图片进行预览',
    controls: {
      zoomIn: '放大',
      zoomOut: '缩小',
      fitToWindow: '适应窗口',
      copyImage: '复制图片'
    },
    messages: {
      copySuccess: '图片已复制到剪贴板',
      copyNotSupported: '当前浏览器不支持复制功能',
      copyFailed: '复制失败：请检查网络连接或重试',
      copyPermissionDenied: '复制失败：浏览器阻止了剪贴板访问权限',
      copyImageFetchFailed: '复制失败：无法获取图片数据',
      copyInvalidFormat: '复制失败：不是有效的图片格式',
      imageLoadFailed: '加载图片失败',
      notImageFormat: '选中的文件不是图片格式'
    }
  },
  modals: {
    close: '✕'
  }
}

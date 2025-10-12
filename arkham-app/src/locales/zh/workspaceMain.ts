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
      quickExport: '快速导出',      // 新增
      advancedExport: '高级导出',   // 新增
      copy: '复制',
      paste: '粘贴',
      rename: '重命名',
      delete: '删除'
    },
    // 新增 quickExport 部分：
    quickExport: {
      title: '快速批量导出',
      directory: '目录',
      foundCards: '发现卡牌',
      cpuCores: 'CPU核心数',
      activeThreads: '使用线程',
      processing: '正在处理中...',
      completed: '导出完成',
      currentTasks: '当前任务:',
      logs: '导出日志:',
      cancel: '取消',
      stop: '停止',
      start: '开始导出',
      close: '关闭',
      scanning: '正在扫描卡牌文件...',
      noCardsFound: '未找到可导出的卡牌文件',
      scanFailed: '扫描目录失败',
      foundCardsLog: '发现卡牌文件',
      threadsLog: '使用线程数',
      startLog: '开始快速批量导出...',
      usingThreads: '使用 {count} 个线程并发处理',
      exportSuccess: '✓ {name}: 导出成功',
      exportFailed: '✗ {name}: 导出失败 - {error}',
      completedLog: '导出完成: {success}/{total}',
      failedCount: '失败数量: {count}',
      userStopped: '用户停止了导出',
      quickExportCompleted: '快速导出完成: {success}/{total} 张卡牌',
      partialSuccess: '部分导出成功: {success} 成功, {failed} 失败',
      stopping: '正在停止导出...'
    },
    // 新增 advancedExport 部分：
    advancedExport: {
      title: '高级导出设置',
      exportInfo: '导出信息',
      directory: '目录',
      card: '卡牌',
      foundCards: '发现卡牌',
      sheets: '张',
      exportParams: '导出参数设置',
      format: {
        label: '导出格式',
        png: 'PNG',
        jpg: 'JPG'
      },
      quality: {
        label: '图片质量',
        recommended: '95%（推荐）',
        highest: '100%（最高质量）'
      },
      size: {
        label: '导出尺寸',
        standard: '63.5mm × 88.9mm (2.5″ × 3.5″)'
      },
      dpi: {
        label: 'DPI设置'
      },
      bleed: {
        label: '出血规格',
        none: '0mm（无出血）',
        standard: '2mm（标准出血）',
        enhanced: '3mm（加强出血）'
      },
      bleedMode: {
        label: '出血模式',
        crop: '裁剪（保持比例）',
        stretch: '拉伸（填满尺寸）'
      },
      bleedModel: {
        label: '出血模型',
        mirror: '镜像出血（速度快）',
        lama: 'LaMa模型出血（质量高）'
      },
      lamaGuide: {
        text: 'Lama Cleaner 安装指南:',
        link: '点击查看'
      },
      saturation: {
        label: '饱和度'
      },
      brightness: {
        label: '亮度'
      },
      gamma: {
        label: '伽马值'
      },
      progress: {
        exporting: '正在导出: {current} / {total}',
        completed: '导出完成！'
      },
      logs: '导出日志:',
      cancel: '取消',
      stop: '停止',
      start: '开始导出',
      close: '关闭',
      scanning: '正在扫描卡牌文件...',
      noCardsFound: '未找到可导出的卡牌文件',
      prepareFailed: '准备高级导出失败',
      startLog: '开始高级导出...',
      paramsLog: '导出参数: 格式={format}, DPI={dpi}, 出血={bleed}mm',
      exportSuccess: '✓ {name}: 导出成功',
      exportFailed: '✗ {name}: 导出失败 - {error}',
      completedLog: '高级导出完成: {success}/{total}',
      failedCount: '失败数量: {count}',
      userStopped: '用户停止了高级导出',
      advancedExportCompleted: '高级导出完成: {success}/{total} 张卡牌',
      partialSuccess: '部分导出成功: {success} 成功, {failed} 失败',
      stopping: '正在停止高级导出...',
      validationFailed: '验证失败: {errors}',
      exportError: '导出失败'
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
      deleteFailedRetry: '删除失败，请重试',
      copySuccess: '文件复制成功',
      copyFailed: '复制失败，只能复制卡牌文件',
      pasteSuccess: '文件粘贴成功',
      pasteFailed: '粘贴失败',
      pasteNoContent: '剪贴板中没有可粘贴的内容',
      pasteInvalidTarget: '只能在目录中粘贴文件',
      pasteFileExists: '文件已存在，无法粘贴'
    }
  },
  imagePreview: {
    title: '图片预览',
    adjustWidth: '拖拽调整预览区宽度',
    emptyText: '选择图片进行预览',
    frontSide: '正面',
    backSide: '反面',
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

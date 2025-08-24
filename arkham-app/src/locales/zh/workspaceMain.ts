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
    validation: {
      folderNameRequired: '请输入文件夹名称',
      folderNameLength: '文件夹名称长度在1-50个字符',
      folderNameInvalid: '文件夹名称不能包含特殊字符 \\/:*?"<>|',
      cardNameRequired: '请输入卡牌文件名',
      cardNameLength: '卡牌文件名长度在1-50个字符',
      cardNameInvalid: '卡牌文件名不能包含特殊字符 \\/:*?"<>|',
      filenameRequired: '请输入文件名',
      filenameLength: '文件名长度在1-50个字符',
      filenameInvalid: '文件名不能包含特殊字符 \\/:*?"<>|.',
      extensionInvalid: '扩展名不能包含特殊字符 \\/:*?"<>|.'
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

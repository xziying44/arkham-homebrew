export default {
  title: '阿卡姆印牌姬',
  subtitle: '专业的卡牌设计工具',
  
  actions: {
    openProject: '打开项目文件夹',
    openProjectDesc: '选择包含卡牌文件的文件夹开始工作',
    selecting: '正在选择文件夹...'
  },
  
  serviceStatus: {
    connected: '后端服务已连接',
    disconnected: '后端服务离线',
    workspace: '工作空间: {name}'
  },
  
  features: {
    lightweight: '轻量化的json卡牌格式',
    workspace: '同一个工作空间快捷D卡',
    autoTTS: '自动装配TTS物品'
  },
  
  recentProjects: {
    title: '最近项目',
    subtitle: '选择一个最近使用的项目继续编辑',
    clearRecords: '清空记录',
    emptyState: '还没有最近项目',
    emptyStateTitle: '开始你的第一个项目',
    emptyStateDescription: '看起来你还没有创建过任何项目。点击下面的按钮选择一个包含卡牌文件的文件夹，或者选择一个空文件夹来开始你的第一个阿卡姆卡牌设计项目。',
    emptyStateGuide: '你可以选择：',
    emptyStateOption1: '包含现有JSON卡牌文件的文件夹',
    emptyStateOption2: '一个空文件夹来开始新项目',
    loading: '正在加载最近项目...',
    removeSuccess: '已移除: {name}',
    clearSuccess: '已清空最近项目记录'
  },
  
  messages: {
    folderOpened: '文件夹 "{name}" 已成功打开！',
    folderNotSelected: '未选择文件夹',
    selectingInProgress: '目录选择正在进行中，请稍候...',
    serviceOffline: '后端服务未连接，请确保服务正在运行',
    openingFolder: '正在打开目录选择对话框...',
    openingRecent: '正在打开: {name}...',
    opened: '已打开: {name}'
  },
  
  errors: {
    selectInProgress: '目录选择正在进行中，请稍后再试',
    timeout: '操作超时，请重试',
    userCancelled: '用户取消了选择',
    selectError: '选择目录时出错，请重试',
    serverError: '服务器错误，请检查后端服务',
    unknownError: '选择目录时发生未知错误',
    workspaceNotExists: '工作目录不存在，请重新选择',
    accessDenied: '无法访问该目录，请检查权限'
  }
}

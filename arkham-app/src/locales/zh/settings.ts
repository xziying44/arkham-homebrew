export default {
  title: '工作区设置',
  loading: '正在加载配置...',
  
  sections: {
    ai: {
      title: '🤖 AI设置',
      endpoint: 'AI端点',
      model: 'AI模型',
      apiKey: 'API密钥',
      enableInEditor: '在编辑区启用AI',
      enableInEditorDesc: '在编辑器中启用AI辅助功能'
    },
    
    github: {
      title: '📷 GitHub图床设置',
      token: 'GitHub Token',
      tokenDesc: '需要repo权限的GitHub Personal Access Token',
      getToken: '获取Token',
      tokenPlaceholder: '输入GitHub Personal Access Token',
      verifyLogin: '验证登录',
      verifying: '验证中...',
      verified: '已验证',
      loginSuccess: '登录成功，用户名: {username}',
      
      repo: 'GitHub仓库',
      repoDesc: '选择用作图床的GitHub仓库',
      selectRepo: '请选择仓库',
      private: '私有',
      public: '公开',
      
      branch: '分支名称',
      branchDesc: '图片存储的分支（默认：main）',
      
      folder: '存储文件夹',
      folderDesc: '图片存储的文件夹名称（默认：images）'
    },
    
    workspace: {
      title: '🏗️ 工作区配置',
      encounterGroups: '遭遇组图标目录',
      selectDirectory: '请选择目录',
      footerIcon: '底标图标',
      selectImage: '请选择图片',
      footerIconDesc: '选择根目录下的PNG图片作为底标图标',
      copyright: '底标版权信息',
      relativePath: '相对路径: {path}'
    },
    
    language: {
      title: '🌐 语言设置',
      interface: '界面语言',
      chinese: '中文',
      english: 'English (待开发)'
    }
  },
  
  actions: {
    save: '保存设置',
    reset: '重置为默认',
    resetConfirm: '确定要重置所有设置为默认值吗？此操作不可撤销。'
  },
  
  messages: {
    saveSuccess: '设置保存成功！',
    loadError: '无法加载工作区目录，请确保已打开工作空间',
    githubLoginFailed: 'GitHub登录失败',
    tokenRequired: '请输入GitHub Token',
    loadRepoFailed: '加载仓库列表失败: {error}',
    aiConfigRequired: '启用AI功能时，端点和API密钥为必填项'
  }
}

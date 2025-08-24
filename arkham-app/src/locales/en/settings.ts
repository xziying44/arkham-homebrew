export default {
  title: 'Workspace Settings',
  loading: 'Loading configuration...',
  
  sections: {
    ai: {
      title: '🤖 AI Settings',
      endpoint: 'AI Endpoint',
      model: 'AI Model',
      apiKey: 'API Key',
      enableInEditor: 'Enable AI in Editor',
      enableInEditorDesc: 'Enable AI assistance in the editor'
    },
    
    github: {
      title: '📷 GitHub Image Hosting',
      token: 'GitHub Token',
      tokenDesc: 'GitHub Personal Access Token with repo permissions required',
      getToken: 'Get Token',
      tokenPlaceholder: 'Enter GitHub Personal Access Token',
      verifyLogin: 'Verify Login',
      verifying: 'Verifying...',
      verified: 'Verified',
      loginSuccess: 'Login successful, username: {username}',
      
      repo: 'GitHub Repository',
      repoDesc: 'Select a GitHub repository for image hosting',
      selectRepo: 'Please select repository',
      private: 'Private',
      public: 'Public',
      
      branch: 'Branch Name',
      branchDesc: 'Branch for storing images (default: main)',
      
      folder: 'Storage Folder',
      folderDesc: 'Folder name for storing images (default: images)'
    },
    
    workspace: {
      title: '🏗️ Workspace Configuration',
      encounterGroups: 'Encounter Groups Icon Directory',
      selectDirectory: 'Please select directory',
      footerIcon: 'Footer Icon',
      selectImage: 'Please select image',
      footerIconDesc: 'Select a PNG image from root directory as footer icon',
      copyright: 'Footer Copyright',
      relativePath: 'Relative path: {path}'
    },
    
    language: {
      title: '🌐 Language Settings',
      interface: 'Interface Language',
      chinese: '中文',
      english: 'English'
    }
  },
  
  actions: {
    save: 'Save Settings',
    reset: 'Reset to Default',
    resetConfirm: 'Are you sure you want to reset all settings to default values? This action cannot be undone.'
  },
  
  messages: {
    saveSuccess: 'Settings saved successfully!',
    loadError: 'Cannot load workspace directories, please ensure workspace is opened',
    githubLoginFailed: 'GitHub login failed',
    tokenRequired: 'Please enter GitHub Token',
    loadRepoFailed: 'Failed to load repository list: {error}',
    aiConfigRequired: 'Endpoint and API key are required when AI functionality is enabled'
  }
}

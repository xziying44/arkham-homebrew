export default {
  title: 'Arkham Card Maker',
  subtitle: 'Professional Card Design Tool',
  
  actions: {
    openProject: 'Open Project Folder',
    openProjectDesc: 'Select a folder containing card files to start working',
    selecting: 'Selecting folder...'
  },
  
  serviceStatus: {
    connected: 'Backend service connected',
    disconnected: 'Backend service offline',
    workspace: 'Workspace: {name}'
  },
  
  features: {
    lightweight: 'Lightweight JSON card format',
    workspace: 'Quick deck building in same workspace',
    autoTTS: 'Auto-generate TTS items'
  },
  
  recentProjects: {
    title: 'Recent Projects',
    subtitle: 'Select a recently used project to continue editing',
    clearRecords: 'Clear Records',
    emptyState: 'No recent projects yet',
    loading: 'Loading recent projects...',
    removeSuccess: 'Removed: {name}',
    clearSuccess: 'Cleared recent project records'
  },
  
  messages: {
    folderOpened: 'Folder "{name}" opened successfully!',
    folderNotSelected: 'No folder selected',
    selectingInProgress: 'Directory selection in progress, please wait...',
    serviceOffline: 'Backend service not connected, please ensure service is running',
    openingFolder: 'Opening directory selection dialog...',
    openingRecent: 'Opening: {name}...',
    opened: 'Opened: {name}'
  },
  
  errors: {
    selectInProgress: 'Directory selection in progress, please try again later',
    timeout: 'Operation timeout, please retry',
    userCancelled: 'User cancelled selection',
    selectError: 'Error selecting directory, please retry',
    serverError: 'Server error, please check backend service',
    unknownError: 'Unknown error occurred while selecting directory',
    workspaceNotExists: 'Workspace directory does not exist, please reselect',
    accessDenied: 'Cannot access directory, please check permissions'
  }
}

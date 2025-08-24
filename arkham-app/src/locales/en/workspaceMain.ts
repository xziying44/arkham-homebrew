export default {
  layout: {
    fileTree: 'File Tree',
    imagePreview: 'Image Preview',
    adjustWidth: 'Drag to adjust width'
  },
  sidebar: {
    title: 'Workspace',
    backToHome: 'Back to Home',
    navItems: {
      workspace: 'Workspace',
      deckBuilder: 'Deck Builder',
      ttsItems: 'TTS Items',
      settings: 'Settings',
      about: 'About'
    }
  },
  fileTree: {
    title: 'File Explorer',
    adjustWidth: 'Drag to adjust file tree width',
    emptyText: 'No files',
    actions: {
      goBack: 'Back',
      refresh: 'Refresh',
      create: 'Create',
      close: 'Close'
    },
    contextMenu: {
      newFolder: 'New Folder',
      newCard: 'New Card',
      rename: 'Rename',
      delete: 'Delete'
    },
    createFolder: {
      title: 'New Folder',
      label: 'Folder Name',
      placeholder: 'Please enter folder name',
      cancel: 'Cancel',
      confirm: 'OK'
    },
    createCard: {
      title: 'New Card',
      label: 'Card Filename',
      placeholder: 'Please enter card filename (automatically add .card extension)',
      cancel: 'Cancel',
      confirm: 'OK'
    },
    rename: {
      title: 'Rename',
      filenameLabel: 'Filename',
      filenamePlaceholder: 'Please enter filename',
      extensionLabel: 'Extension',
      extensionPlaceholder: 'Please enter extension (without dot)',
      preview: 'Preview:',
      cancel: 'Cancel',
      confirm: 'OK'
    },
    delete: {
      title: 'Delete Confirmation',
      warning: 'Warning',
      confirmText: 'This operation cannot be undone. Are you sure you want to delete?',
      pathLabel: 'Path:',
      folderPrefix: 'Folder:',
      filePrefix: 'File:',
      cancel: 'Cancel',
      confirm: 'Delete'
    },
    validation: {
      folderNameRequired: 'Please enter folder name',
      folderNameLength: 'Folder name length should be 1-50 characters',
      folderNameInvalid: 'Folder name cannot contain special characters \\/:*?"<>|',
      cardNameRequired: 'Please enter card filename',
      cardNameLength: 'Card filename length should be 1-50 characters',
      cardNameInvalid: 'Card filename cannot contain special characters \\/:*?"<>|',
      filenameRequired: 'Please enter filename',
      filenameLength: 'Filename length should be 1-50 characters',
      filenameInvalid: 'Filename cannot contain special characters \\/:*?"<>|.',
      extensionInvalid: 'Extension cannot contain special characters \\/:*?"<>|.'
    },
    messages: {
      loadFailed: 'Failed to load file tree',
      loadFailedNetwork: 'Failed to load file tree, please check service connection',
      createFolderSuccess: 'Folder created successfully',
      createFolderFailed: 'Failed to create folder',
      createFolderFailedRetry: 'Failed to create folder, please try again',
      createCardSuccess: 'Card created successfully',
      createCardFailed: 'Failed to create card',
      createCardFailedRetry: 'Failed to create card, please try again',
      renameSuccess: 'Renamed successfully',
      renameFailed: 'Failed to rename',
      renameFailedRetry: 'Failed to rename, please try again',
      deleteSuccess: 'Deleted successfully',
      deleteFailed: 'Failed to delete',
      deleteFailedRetry: 'Failed to delete, please try again'
    }
  },
  imagePreview: {
    title: 'Image Preview',
    adjustWidth: 'Drag to adjust preview area width',
    emptyText: 'Select an image to preview',
    controls: {
      zoomIn: 'Zoom In',
      zoomOut: 'Zoom Out',
      fitToWindow: 'Fit to Window',
      copyImage: 'Copy Image'
    },
    messages: {
      copySuccess: 'Image copied to clipboard',
      copyNotSupported: 'Current browser does not support copy functionality',
      copyFailed: 'Copy failed: Please check network connection or try again',
      copyPermissionDenied: 'Copy failed: Browser blocked clipboard access permission',
      copyImageFetchFailed: 'Copy failed: Unable to fetch image data',
      copyInvalidFormat: 'Copy failed: Not a valid image format',
      imageLoadFailed: 'Failed to load image',
      notImageFormat: 'Selected file is not an image format'
    }
  },
  modals: {
    close: '✕'
  }
}

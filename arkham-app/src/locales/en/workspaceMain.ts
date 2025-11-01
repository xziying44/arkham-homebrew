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
    // 在 contextMenu 部分添加：
    contextMenu: {
      newFolder: 'New Folder',
      newCard: 'New Card',
      quickExport: 'Quick Export',        // 新增
      advancedExport: 'Advanced Export',  // 新增
      copy: 'Copy',
      copyRelativePath: 'Copy Relative Path',
      copyImageTag: 'Copy Image Tag',
      paste: 'Paste',
      rename: 'Rename',
      delete: 'Delete'
    },
    copyImageTag: {
    title: 'Copy Image Tag',
    widthLabel: 'Width',
    widthPlaceholder: 'e.g.: 100',
    heightLabel: 'Height',
    heightPlaceholder: 'e.g.: 100',
    offsetLabel: 'Y-Offset',
    offsetPlaceholder: 'e.g.: -2',
    centerLabel: 'Center',
    preview: 'Preview:',
    cancel: 'Cancel',
    confirm: 'Confirm'
    },
    // 新增 quickExport 部分：
    quickExport: {
      title: 'Quick Batch Export',
      directory: 'Directory',
      foundCards: 'Found Cards',
      cpuCores: 'CPU Cores',
      activeThreads: 'Active Threads',
      processing: 'Processing...',
      completed: 'Export Completed',
      currentTasks: 'Current Tasks:',
      logs: 'Export Logs:',
      cancel: 'Cancel',
      stop: 'Stop',
      start: 'Start Export',
      close: 'Close',
      scanning: 'Scanning card files...',
      noCardsFound: 'No exportable card files found',
      scanFailed: 'Failed to scan directory',
      foundCardsLog: 'Found card files',
      threadsLog: 'Using threads',
      startLog: 'Starting quick batch export...',
      usingThreads: 'Using {count} concurrent threads',
      exportSuccess: '✓ {name}: Export successful',
      exportFailed: '✗ {name}: Export failed - {error}',
      completedLog: 'Export completed: {success}/{total}',
      failedCount: 'Failed count: {count}',
      userStopped: 'User stopped export',
      quickExportCompleted: 'Quick export completed: {success}/{total} cards',
      partialSuccess: 'Partial success: {success} succeeded, {failed} failed',
      stopping: 'Stopping export...'
    },

    // 新增 advancedExport 部分：
    advancedExport: {
      title: 'Advanced Export Settings',
      exportInfo: 'Export Information',
      directory: 'Directory',
      card: 'Card',
      foundCards: 'Found Cards',
      sheets: 'sheets',
      exportParams: 'Export Parameters',
      format: {
        label: 'Export Format',
        png: 'PNG',
        jpg: 'JPG'
      },
      quality: {
        label: 'Image Quality',
        recommended: '95% (Recommended)',
        highest: '100% (Highest Quality)'
      },
      size: {
        label: 'Export Size',
        standard: '63.5mm × 88.9mm (2.5″ × 3.5″)'
      },
      dpi: {
        label: 'DPI Setting'
      },
      bleed: {
        label: 'Bleed Specification',
        none: '0mm (No Bleed)',
        standard: '2mm (Standard Bleed)',
        enhanced: '3mm (Enhanced Bleed)'
      },
      bleedMode: {
        label: 'Bleed Mode',
        crop: 'Crop (Keep Ratio)',
        stretch: 'Stretch (Fill Size)'
      },
      bleedModel: {
        label: 'Bleed Model',
        mirror: 'Mirror Bleed (Fast)',
        lama: 'LaMa Model Bleed (High Quality)'
      },
      lamaGuide: {
        text: 'Lama Cleaner Installation Guide:',
        link: 'Click to view'
      },
      saturation: {
        label: 'Saturation'
      },
      brightness: {
        label: 'Brightness'
      },
      gamma: {
        label: 'Gamma'
      },
      progress: {
        exporting: 'Exporting: {current} / {total}',
        completed: 'Export completed!'
      },
      logs: 'Export Logs:',
      cancel: 'Cancel',
      stop: 'Stop',
      start: 'Start Export',
      close: 'Close',
      scanning: 'Scanning card files...',
      noCardsFound: 'No exportable card files found',
      prepareFailed: 'Failed to prepare advanced export',
      startLog: 'Starting advanced export...',
      paramsLog: 'Export parameters: Format={format}, DPI={dpi}, Bleed={bleed}mm',
      exportSuccess: '✓ {name}: Export successful',
      exportFailed: '✗ {name}: Export failed - {error}',
      completedLog: 'Advanced export completed: {success}/{total}',
      failedCount: 'Failed count: {count}',
      userStopped: 'User stopped advanced export',
      advancedExportCompleted: 'Advanced export completed: {success}/{total} cards',
      partialSuccess: 'Partial success: {success} succeeded, {failed} failed',
      stopping: 'Stopping advanced export...',
      validationFailed: 'Validation failed: {errors}',
      exportError: 'Export failed'
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
    batchExport: {
      title: 'Batch Export Cards',
      directory: 'Target Directory',
      foundCards: 'Found Cards',
      cpuCores: 'CPU Cores',
      threadsUsing: 'Threads Using',
      processing: 'Processing',
      completed: 'Batch Export Completed',
      currentTasks: 'Current Tasks',
      logs: 'Export Logs',
      cancel: 'Cancel',
      stop: 'Stop',
      start: 'Start Export',
      close: 'Close',
      scanning: 'Scanning directory...',
      noCardsFound: 'No card files found in directory',
      scanFailed: 'Failed to scan directory',
      foundCardsLog: 'Found card files',
      usingThreads: 'Using threads',
      startLog: 'Starting batch export',
      abortedLog: 'Batch export aborted',
      processingLog: 'Processing',
      validationFailed: 'Card data validation failed',
      exportSuccess: 'Export successful',
      exportFailed: 'Export failed',
      failedExports: 'Failed exports',
      completedLog: 'Batch export completed',
      allCompleted: 'Successfully exported {successCount} cards out of {totalCount}!',
      partialSuccess: 'Export completed: {successCount} successful, {errorCount} failed',
      stopping: 'Stopping batch export...',
      progressDetail: 'Progress Detail',
      total: 'Total',
      remaining: 'Remaining',
      userStopped: 'User stopped batch export'
    },
    validation: {
      folderNameRequired: 'Please enter folder name',
      folderNameLength: 'Folder name length should be 1-50 characters',
      folderNameInvalid: 'Folder name cannot contain special characters \\/:*?"<>',
      cardNameRequired: 'Please enter card filename',
      cardNameLength: 'Card filename length should be 1-50 characters',
      cardNameInvalid: 'Card filename cannot contain special characters \\/:*?"<>',
      filenameRequired: 'Please enter filename',
      filenameLength: 'Filename length should be 1-50 characters',
      filenameInvalid: 'Filename cannot contain special characters \\/:*?"<>.',
      extensionInvalid: 'Extension cannot contain special characters \\/:*?"<>.'
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
      deleteFailedRetry: 'Failed to delete, please try again',
      copySuccess: 'File copied successfully',
      copyFailed: 'Copy failed, only card files can be copied',
      copyRelativePathSuccess: 'Relative path copied: {path}',
      copyRelativePathFailed: 'Failed to copy relative path',
      copyImageTagSuccess: 'Image tag copied to clipboard',  // 新增
      copyImageTagFailed: 'Failed to copy image tag',  // 新增
      pasteSuccess: 'File pasted successfully',
      pasteFailed: 'Paste failed',
      pasteNoContent: 'No content to paste in clipboard',
      pasteInvalidTarget: 'Files can only be pasted in directories',
      pasteFileExists: 'File already exists, cannot paste'
    }
  },
  imagePreview: {
    title: 'Image Preview',
    adjustWidth: 'Drag to adjust preview area width',
    emptyText: 'Select an image to preview',
    frontSide: 'Front',
    backSide: 'Back',
    loadingText: 'Generating card...',
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

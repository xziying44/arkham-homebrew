export default {
  title: 'Content Package Management',
  languages: {
    zh: 'Chinese',
    en: 'English'
  },
  packageTypes: {
    investigators: 'Investigators',
    player_cards: 'Player Cards',
    campaign: 'Campaign'
  },
  editor: {
    tabs: {
      info: 'Basic Info',
      cards: 'Card Management',
      export: 'Export Settings'
    },
    sections: {
      banner: 'Banner Preview',
      basicInfo: 'Basic Info',
      cards: 'Card Management',
      export: 'Export Settings'
    },
    fields: {
      code: 'ID',
      name: 'Name',
      description: 'Description',
      author: 'Author',
      language: 'Language',
      types: 'Package Types',
      status: 'Status',
      dateUpdated: 'Updated Date',
      generator: 'Generator',
      externalLink: 'External Link',
      banner: 'Banner'
    },
    editMeta: {
      title: 'Edit Package Info',
      namePlaceholder: 'Enter package name',
      descriptionPlaceholder: 'Enter package description',
      authorPlaceholder: 'Enter author name',
      externalLinkPlaceholder: 'Optional: Enter external link URL',
      bannerUrl: 'Banner URL',
      bannerUrlPlaceholder: 'Enter banner image URL',
      bannerFile: 'Banner File',
      dragToUpload: 'Click or drag image here to upload',
      uploadHint: 'Supports JPG, PNG, GIF and other formats',
      saveSuccess: 'Saved successfully'
    },
    noBanner: 'No banner'
  },
  actions: {
    newPackage: 'New Package',
    refresh: 'Refresh',
    delete: 'Delete',
    cancel: 'Cancel',
    create: 'Create',
    save: 'Save'
  },
  panels: {
    myPackages: 'My Packages'
  },
  packageList: {
    empty: 'No packages yet',
    emptyDesc: 'Click the top-right button to create your first package'
  },
  noSelection: {
    title: 'Please select a package',
    description: 'Select a package from the left list to edit, or create a new package'
  },
  forms: {
    newPackage: {
      title: 'Create New Package',
      name: 'Name',
      namePlaceholder: 'Enter package name',
      description: 'Description',
      descriptionPlaceholder: 'Enter package description',
      author: 'Author',
      authorPlaceholder: 'Enter author name',
      language: 'Language',
      types: 'Package Types',
      externalLink: 'External Link',
      externalLinkPlaceholder: 'Optional: Enter external link URL',
      banner: 'Banner',
      bannerUrl: 'Banner URL',
      bannerUrlPlaceholder: 'Enter banner image URL',
      bannerFile: 'Banner File',
      dragToUpload: 'Click or drag image here to upload',
      uploadHint: 'Supports JPG, PNG, GIF and other formats'
    },
    validation: {
      nameRequired: 'Please enter a name',
      nameLength: 'Name length should be between 1-100 characters',
      namePattern: 'Name cannot contain special characters',
      descriptionRequired: 'Please enter a description',
      descriptionLength: 'Description length should be between 1-1000 characters',
      authorRequired: 'Please enter an author',
      authorLength: 'Author length should be between 1-100 characters',
      languageRequired: 'Please select a language',
      typesRequired: 'Please select at least one package type'
    }
  },
  deleteDialog: {
    title: 'Delete Confirmation',
    warning: 'Warning',
    message: 'Are you sure you want to delete package "{name}"? This action cannot be undone.'
  },
  messages: {
    refreshSuccess: 'Refreshed successfully',
    loadFailed: 'Load failed',
    createSuccess: 'Created successfully',
    createFailed: 'Create failed',
    saveSuccess: 'Saved successfully',
    saveFailed: 'Save failed',
    deleteSuccess: 'Deleted successfully',
    deleteFailed: 'Delete failed',
    readBannerFailed: 'Failed to read banner file',
    addCardSuccess: 'Successfully added {count} cards',
    addCardFailed: 'Failed to add cards',
    cardDeleted: 'Card deleted',
    bannerUploadSuccess: 'Banner uploaded successfully',
    cardUploadSuccess: 'Card uploaded successfully',
    batchUploadSuccess: 'Batch upload successful! Total {count} cards uploaded',
    batchUploadCompleted: 'Batch upload completed: {success} successful, {failure} failed',
    noCardsToUpload: 'No cards to upload',
    imageHostConfigIncomplete: 'Image hosting configuration incomplete, please configure first',
    batchUploadFailed: 'Batch upload failed',
    batchPreparing: 'Preparing batch upload...',
    batchStarting: 'Starting batch upload...',
    batchUploading: 'Uploading: {filename} ({index}/{total})'
  },
  cards: {
    empty: {
      title: 'No cards added yet',
      description: 'Click the "Add Card" button above to start adding'
    },
    status: {
      unsupported: 'Unsupported (v{version})',
      supported: 'v{version}',
      generating: 'Generation failed',
      generationStopped: 'Stopped',
      versionCheckFailed: 'Version check failed'
    },
    actions: {
      addCard: 'Add Card'
    },
    dialog: {
      title: 'Add Card'
    }
  },
  export: {
    notImplemented: {
      title: 'Export feature in development',
      description: 'This feature will be implemented in future versions'
    },
    tts: {
      title: 'Export to TTS Items',
      description: 'Export the content package as a JSON file usable by TTS, containing all cards with generated images (supports both cloud and local images)',
      packageName: 'Package Name',
      cardCount: 'Card Count',
      cardsWithImages: 'Cards with Images',
      exportStatus: 'Export Status',
      canExport: 'Can Export',
      needImages: 'Need to Generate Images',
      cardExportStatus: 'Card Export Status',
      exportTTSItems: 'Export TTS Items',
      exportLogs: 'Export Logs',
      close: 'Close',
      openFolder: 'Open Folder'
    },
    arkhamdb: {
      title: 'Export to ArkhamDB Format',
      description: 'Export the content package as an ArkhamDB format JSON file, suitable for arkham.build expansion pack creation',
      packageName: 'Package Name',
      cardCount: 'Card Count',
      packageCode: 'Package Code',
      alwaysExportable: 'Can Export',
      exportStatus: 'Export Status',
      exportDescription: 'Export Description',
      exportDetails: [
        '• Exported JSON file contains ArkhamDB format data for all cards',
        '• Can be directly used for expansion pack upload on arkham.build website',
        '• Contains complete card attributes, tags and metadata information'
      ],
      exportArkhamDB: 'Export ArkhamDB Format',
      exportLogs: 'ArkhamDB Export Logs',
      close: 'Close',
      openFolder: 'Open Folder',
      success: {
        ttsExportSuccess: 'TTS items exported successfully!',
        arkhamdbExportSuccess: 'ArkhamDB format exported successfully!'
      }
    }
  },
  tags: {
    edit: {
      title: 'Edit Card Tags - {filename}',
      description: 'Set special attribute tags for cards, these tags will be retained during export',
      permanent: {
        label: 'Permanent Card',
        description: 'Permanent cards do not count towards deck size, are not removed from the game, and are set up on the field at the start of the game'
      },
      exceptional: {
        label: 'Exceptional Card',
        description: 'Exceptional cards cost double the experience points, and only one copy can be purchased'
      },
      myriad: {
        label: 'Myriad Card',
        description: 'Myriad cards can have 3 copies in a deck, and purchasing multiple copies only costs experience once'
      },
      exile: {
        label: 'Exile',
        description: 'Exile cards can be removed from the game under specific conditions'
      },
      preview: 'Current Tags Preview',
      save: 'Save',
      cancel: 'Cancel'
    }
  },
  upload: {
    button: {
      uploadToCloud: 'Upload to Cloud',
      reuploadToCloud: 'Re-upload to Cloud',
      uploadCard: 'Upload This Card',
      reupload: 'Re-upload'
    },
    dialog: {
      selectImageHost: 'Select Image Host Service',
      localMode: 'Local Test',
      localModeDescription: 'Local test mode: only export images to local, not upload to cloud, using file:/// format URLs',
      cloudinaryConfig: 'Cloudinary Configuration',
      cloudName: 'Cloud Name',
      apiKey: 'API Key',
      apiSecret: 'API Secret',
      folder: 'Folder',
      folderPlaceholder: 'Folder name (optional)',
      imgbbConfig: 'ImgBB Configuration',
      expirationHours: 'Expiration Time (hours)',
      expirationPlaceholder: '0 (never expires)',
      exportFormat: 'Export Format',
      imageQuality: 'Image Quality',
      uploadProgress: 'Upload Progress',
      uploadLogs: 'Upload Logs',
      preparingUpload: 'Preparing upload...',
      configSaved: 'Configuration saved',
      preparingImages: 'Preparing to export images...',
      preparingCloudUpload: 'Preparing to upload to cloud...',
      updatingData: 'Updating content package data...',
      uploadComplete: 'Upload complete',
      preparingBatchConfig: 'Preparing batch upload configuration...',
      preparingBatchUpload: 'Preparing batch upload...',
      batchUploadComplete: 'Batch upload complete',
      imageUploadSuccess: 'Image uploaded successfully: {filename}',
      imageUploadFailed: 'Image upload failed: {filename} - {error}',
      bannerUploadComplete: 'Banner upload complete',
      cardUploadComplete: 'Card upload complete',
      batchUploadCompleteLog: 'Batch upload complete',
      cardUploadSuccessLog: 'Card {filename} upload successful',
      cardUploadFailedLog: 'Card {filename} upload failed: {error}',
      imageExportStart: 'Starting to export image: {filename}',
      imageExportSuccess: 'Image export successful: {filename}',
      imageExportFailed: 'Image export failed: {filename}',
      imageUploadStart: 'Starting to upload image: {filename}',
      imageUploadSuccessUrl: 'Image upload successful: {url}',
      localModeUrl: 'Local mode, using local URL: {url}',
      completeConfigInfo: 'Complete image hosting configuration and upload all v2.0 cards. Previously uploaded cards will be overwritten.',
      playerCardbackDetected: 'Detected player card back, using predefined URL',
      encounterCardbackDetected: 'Detected encounter card back, using predefined URL',
      uploadingImage: 'Uploading image {index}/{total}...'
    },
    error: {
      configIncomplete: 'Please complete the image hosting configuration information',
      noBannerData: 'No banner image data found',
      uploadFailed: 'Upload failed: {message}',
      packagePathInvalid: 'Content package path invalid',
      noCardsToUpload: 'No cards to upload',
      batchUploadFailed: 'Batch upload failed: {message}',
      cannotGetWorkspacePath: 'Cannot get workspace path',
      configLoadFailed: 'Configuration loading failed: {message}',
      configSaveFailed: 'Configuration saving failed: {message}',
      exportFailed: 'Export failed: {message}'
    },
    success: {
      configSaveSuccess: 'Configuration saved successfully',
      localModeNoSave: 'Local test mode, no need to save configuration'
    },
    status: {
      cloud: 'Cloud',
      local: 'Local',
      noImage: 'No Image',
      uploaded: 'Uploaded',
      pending: 'Pending'
    },
    title: {
      uploadBannerToCloud: 'Upload Banner to Cloud',
      uploadCardToCloud: 'Upload Card to Cloud',
      batchUploadToCloud: 'Batch Upload Cards to Cloud',
      configureBatchUpload: 'Configure Batch Upload'
    },
    info: {
      v2CardCount: 'Total v2.0 Cards',
      cloudUploaded: 'Cloud Uploaded',
      v2CardList: 'v2.0 Card List',
      uploadProgress: 'Upload Progress',
      batchUploadCompleted: 'Batch upload completed: {success} successful, {failure} failed'
    },
    action: {
      startConfiguration: 'Start Configuration ({count} cards)',
      startUpload: 'Start Upload'
    }
  },
  common: {
    editInfo: 'Edit Info',
    save: 'Save',
    unnamedPackage: 'Unnamed Package',
    unknown: 'Unknown',
    unknownAuthor: 'Unknown Author',
    noDescription: 'No Description',
    batchUpload: 'Batch Upload',
    addCard: 'Add Card',
    generationFailed: 'Generation Failed',
    unsupported: 'Unsupported',
    editTags: 'Edit Tags',
    permanent: 'Permanent',
    exceptional: 'Exceptional',
    myriad: 'Myriad',
    exile: 'Exile',
    cancel: 'Cancel',
    uploadToCloud: 'Upload to Cloud',
    close: 'Close',
    openFolder: 'Open Folder',
    cardTagsSaved: 'Card tags saved successfully'
  }
}
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
  upload: {
    button: {
      uploadToCloud: 'Upload to Cloud',
      reuploadToCloud: 'Reupload to Cloud',
      uploadCard: 'Upload Card',
      reupload: 'Reupload'
    },
    title: {
      uploadBannerToCloud: 'Upload Banner to Cloud',
      uploadCardToCloud: 'Upload Card to Cloud',
      batchUploadToCloud: 'Batch Upload Cards to Cloud',
      configureBatchUpload: 'Configure Batch Upload'
    },
    status: {
      uploadedToCloud: 'Uploaded to Cloud',
      savedToLocal: 'Saved to Local'
    },
    info: {
      willUploadAllV2Cards: 'Will configure image hosting and upload all v2.0 cards. Previously uploaded cards will be overwritten.',
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
    }
  }
}
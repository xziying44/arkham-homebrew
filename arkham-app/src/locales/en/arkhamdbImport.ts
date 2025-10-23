export default {
  title: 'ArkhamDB Import',
  description: 'Import cards from ArkhamDB JSON content pack to current workspace',
  upload: {
    title: 'Select or drag ArkhamDB content pack file',
    subtitle: 'Support .json and .pack format files, max 50MB',
    hint: 'Click to select file or drag file here'
  },
  fileInfo: {
    title: 'File Information',
    name: 'File Name',
    size: 'File Size',
    type: 'File Type'
  },
  targetDirectory: {
    title: 'Target Directory',
    placeholder: 'Select import directory (optional)',
    hint: 'Leave empty to import to workspace root directory',
    root: 'Workspace Root'
  },
  validation: {
    title: 'Validation Result',
    valid: '✅ Content pack format validation passed',
    invalid: '❌ Content pack format validation failed',
    warning: '⚠️ Content pack has some issues',
    success: 'Content pack validation completed',
    packName: 'Pack Name',
    language: 'Language',
    totalCards: 'Total Cards',
    validCards: 'Valid Cards',
    errors: 'Validation Errors'
  },
  errors: {
    invalidFile: 'Invalid file format, please select .json or .pack file',
    validationFailed: 'Content pack validation failed',
    validationError: 'Error occurred during validation',
    importFailed: 'Import failed',
    importError: 'Error occurred during import'
  },
  actions: {
    validate: 'Validate File',
    import: 'Start Import',
    cancel: 'Cancel',
    refresh: 'Refresh'
  },
  importResult: {
    title: 'Import Result',
    success: 'Successfully imported {count} cards',
    totalCards: 'Total Processed Cards',
    language: 'Pack Language',
    targetDirectory: 'Target Directory',
    logs: 'Import Logs'
  },
  language: {
    unknown: 'Unknown'
  },
  // New fields
  importWarning: '⚠️ Please be careful! This import operation may overwrite certain configurations and card files in the workspace. It is recommended to perform the import in an empty directory or backup important data first.',
  importConfirm: {
    title: 'Important Notice',
    warning1: '• Please ensure you have selected the correct ArkhamDB content pack file',
    warning2: '• It is recommended to perform the import operation in an empty directory',
    warning3: '• Imported cards will overwrite existing files with the same name'
  },
  sampleCards: 'Sample Cards',
  importing: 'Importing content pack...',
  importCompleted: 'Content pack import completed',
  noLogs: 'No log information available',
  stopImport: 'Stop Import',
  close: 'Close'
};
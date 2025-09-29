export default {
  // FormField component
  field: {
    pleaseEnter: 'Please enter {name}',
    pleaseSelect: 'Please select {name}',
    add: 'Add {name}',
    input: 'Enter {name}',
    addItem: 'Add',
    viewFieldDescription: 'View field description',
    fieldDescription: 'Field Description',
    close: 'Close',
    delete: 'Delete',
    clickOrDragToUpload: 'Click or drag image to this area to upload',
    supportedFormats: 'Support JPG, PNG, GIF, WebP formats, max size {size}',
    noAvailableEncounterGroups: 'No available encounter groups (please check configuration)',
    loadEncounterGroupsFailed: 'Failed to load encounter groups, please check encounter group directory configuration',
    unsupportedImageFormat: 'Unsupported image format, please select JPG, PNG, GIF, WebP or SVG file',
    fileSizeExceeded: 'File size exceeds limit, maximum supported {size}',
    fileReadFailed: 'File read failed',
    imageProcessFailed: 'Image processing failed, please try again'
  },

  // FormEditPanel component
  panel: {
    close:'close',
    cardEditor: 'Card Editor',
    importJson: 'Import JSON',
    viewJson: 'View JSON',
    selectCardFileToEdit: 'Please select a card file (.card) in the file manager to edit',
    noCardSelected: 'No Card Selected',
    createOrSelectCard: 'Create or Select a Card to Edit',
    howToCreateCard: 'How to Create a Card?',
    clickPlusButton: 'Click the "+" button at the top to create a new card',
    rightClickFileTree: 'Right-click on a file tree node to create a new card',
    selectExistingCard: 'Or select an existing .card file to edit',
    getStarted: 'Let\'s start creating your card!',

    // AI assistant
    aiAssistant: '🤖 AI Card Assistant',
    describeYourCard: 'Describe the card you want',
    cardDescriptionPlaceholder: 'e.g.: Create a fire attribute attack spell card named Fireball, dealing 5 damage, costing 3 mana...',
    generateCard: 'Generate Card',
    generating: 'Generating...',
    stopGeneration: 'Stop Generation',
    clearResult: 'Clear Result',
    aiThinking: 'AI is thinking...',
    generationComplete: 'Generation Complete',
    aiThoughtProcess: '💭 AI Thought Process:',
    generatedCardData: '📋 Generated Card Data:',
    validationSuccess: '✅ Validation Success',
    validationFailed: '❌ Validation Failed',
    cardDataValid: 'Card data format is correct and can be imported into the editor',
    importToEditor: 'Import to Editor',

    // Card type
    cardType: 'Card Type',
    selectCardType: 'Select Card Type',

    // Card properties
    cardProperties: 'Card Properties',

    language: "Language",
    selectLanguage: "Select Language",
    chinese: "中文",
    english: "English",

    // Card info
    cardInfo: 'Card Information',
    illustrator: '🎨 Illustrator',
    encounterGroupNumber: '📋 Encounter Group Number',
    cardNumber: '📋 Card Number',
    cardRemarks: '📝 Card Remarks',

    // Action buttons
    saveCard: 'Save Card',
    previewCard: 'Preview Card',
    exportImage: 'Export Image',
    reset: 'Reset',

    // JSON modal
    currentJsonData: 'Current JSON Data',
    copyJson: 'Copy JSON',

    // Import JSON modal
    importJsonData: 'Import JSON Data',
    pasteJsonData: 'Please paste JSON data',
    pasteJsonPlaceholder: 'Please paste the JSON data to import...',
    cancel: 'Cancel',
    import: 'Import',

    // Save confirmation dialog
    saveConfirmation: 'Save Confirmation',
    unsavedChanges: 'Unsaved Changes',
    hasUnsavedChangesMessage: 'The current file has unsaved changes, do you want to save?',
    changesWillBeLost: 'If you don\'t save, your changes will be lost.',
    dontSave: 'Don\'t Save',
    save: 'Save',

    // Shortcuts
    ctrlS: '(Ctrl+S)',

    // Message prompts
    noFileSelected: 'No file selected',
    cardSavedSuccessfully: 'Card saved successfully',
    saveCardFailed: 'Failed to save card',
    loadCardDataFailed: 'Failed to load card data',
    cardDataValidationFailed: 'Card data validation failed',
    generateCardImageFailed: 'Failed to generate card image',
    pleaseEnterCardNameAndType: 'Please enter card name and type first',
    cardPreviewGenerated: 'Card preview generated successfully',
    previewCardImageFailed: 'Failed to preview card image',
    noCardFileSelected: 'No card file selected',
    imageExported: 'Image exported: {filename}',
    exportImageFailed: 'Failed to export image',
    formReset: 'Form reset',
    jsonCopiedToClipboard: 'JSON copied to clipboard',
    copyFailed: 'Copy failed, please manually select text to copy',
    pleaseEnterJsonData: 'Please enter JSON data',
    jsonDataImportedSuccessfully: 'JSON data imported successfully',
    importFailed: 'Import failed',
    invalidJsonFormat: 'Invalid JSON format',

    // AI related messages
    pleaseEnterPrompt: 'Please enter prompt',
    aiGenerationFailed: 'AI generation failed',
    validationError: 'Validation failed',
    noValidAiResult: 'No valid AI generation result to import',
    aiDataImportedSuccessfully: 'AI generated card data successfully imported to editor',
    importAiResultFailed: 'Failed to import AI result',
    aiGenerationCompleted: 'AI generation completed but no valid content returned',
    aiReturnedError: 'AI returned error',
    missingRequiredFields: 'Missing required fields',
    jsonParseError: 'JSON parse error'
  }
}

export default {
  title: 'Card Languages',
  description: 'Manage fonts and text mappings for supported card languages.',
  languageList: {
    title: 'Languages',
    empty: 'No languages configured yet. Please add one.',
  },
  sections: {
    basic: 'Basic Info',
    fonts: 'Font Settings',
    texts: 'Text Mappings',
    fontFolder: 'Fonts Directory',
  },
  fields: {
    name: 'Language Name',
    code: 'Language Code',
  },
  fonts: {
    hint: 'Each language needs fonts for title, subtitle, card type, trait, bold, body, flavor and collection info.',
    headers: {
      category: 'Category',
      name: 'Font Name',
      size: 'Size %',
      offset: 'Vertical Offset',
    },
    categories: {
      title: 'Title',
      subtitle: 'Subtitle',
      card_type: 'Card Type',
      trait: 'Trait',
      bold: 'Bold',
      body: 'Body',
      flavor: 'Flavor',
      collection_info: 'Collection Info',
    },
  },
  texts: {
    hint: 'Text mappings are used for various labels in card templates, such as card types, Victory, Revelation, etc. Keys are defined by the system; the UI only allows editing the display texts.',
  },
  fontFolder: {
    hint: 'You can create a fonts folder in the application directory to add custom fonts. Windows users should create it in the program running directory, macOS users in ~/Documents/ArkhamCardMaker. After placing font files in the folder, click the refresh button to update the font list.',
  },
  actions: {
    addLanguage: 'Add Language',
    delete: 'Delete',
    cancel: 'Cancel',
    refreshFonts: 'Refresh Fonts',
    save: 'Save Language Config',
  },
  forms: {
    newLanguage: {
      title: 'Add New Language',
      templateLabel: 'Select Template Language',
      templateHint: 'Select an existing language as a template for font configuration',
      templateNone: 'Empty Template (Default)',
    },
  },
  deleteDialog: {
    title: 'Delete Language',
    warning: 'Warning',
    message: 'Deleting language "{name}" may cause display issues for cards using this language. Are you sure you want to delete it?',
  },
  defaults: {
    newLanguageName: 'New Language',
  },
  messages: {
    loadFailed: 'Failed to load language config',
    saveSuccess: 'Language config saved successfully',
    saveFailed: 'Failed to save language config',
    deleteSuccess: 'Language deleted successfully',
    deleteFailed: 'Failed to delete language',
    refreshFontsSuccess: 'Font list refreshed',
    refreshFontsFailed: 'Failed to refresh font list',
  },
};

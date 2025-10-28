export default {
  // Component title
  title: '🎯 Deck Options Editor',
  currentOptions: 'Current Deck Options',
  addOption: 'Add Option',
  noOptions: 'No deck options available',
  option: 'Option',
  editing: 'Editing',
  edit: 'Edit',
  save: 'Save',
  cancel: 'Cancel',
  delete: 'Delete',

  // Option configuration
  optionId: 'Option ID',
  optionIdPlaceholder: 'Enter option ID (optional)',

  // Basic filters
  basicFilters: '📊 Basic Filters',
  cardType: 'Card Type',
  selectCardTypes: 'Select card types',
  faction: 'Faction',
  selectFactions: 'Select factions',
  traits: 'Traits',
  addTrait: 'Add trait',
  slots: 'Slots',
  selectSlots: 'Select slots',
  uses: 'Uses',
  selectUses: 'Select uses',

  // Text match
  textMatch: '📝 Text Match',
  textContains: 'Text contains',
  addText: 'Add text',
  textExact: 'Exact match',
  addExactText: 'Add exact text',

  // Level system
  levelSystem: '🎚️ Level System',
  levelRange: 'Level range',
  level: 'Level',
  minLevel: 'Min level',
  maxLevel: 'Max level',

  // Quantity limit
  quantityLimit: '🔢 Quantity Limit',
  limit: 'Limit',
  limitPlaceholder: 'Maximum selection count',

  // Selection mechanism
  selectionMechanism: '🎲 Selection Mechanism',
  selectSelectionType: 'Please select selection mechanism (only one type allowed)',
  noneSelection: 'No Selection Mechanism',
  factionSelect: 'Faction Select',
  selectFactionForSelection: 'Select selectable factions',
  deckSizeSelect: 'Deck Size Select',
  selectDeckSizes: 'Select selectable deck sizes',
  advancedSelect: 'Advanced Attribute Select',
  selectionTypeNames: {
    faction: 'Class Choice',
    deckSize: 'Deck Size',
    advanced: 'Advanced Attributes'
  },
  defaultAdvancedName: 'Advanced Attributes',
  newOptionItem: 'Option {index}',

  // Advanced rules
  advancedRules: '⚙️ Advanced Rules',
  not: 'Negative condition',
  notEnabled: 'Enable negative condition',
  notDisabled: 'Disable negative condition',
  atLeast: 'At Least',
  atLeastEnabled: 'Enable at least condition',
  atLeastDisabled: 'Disable at least condition',
  minCount: 'Min count',
  selectAtLeastTypes: 'Select at least card types',

  // JSON preview
  finalPreview: '📋 Final Configuration Preview',
  copyJson: 'Copy JSON',
  refresh: 'Refresh',

  // Validation messages
  validation: {
    nameRequired: 'Option name cannot be empty',
    itemNameRequired: 'Item "{itemId}" name cannot be empty'
  },

  // Messages
  messages: {
    optionAdded: 'Deck option added',
    optionSaved: 'Deck option saved',
    optionDeleted: 'Deck option deleted',
    editCancelled: 'Edit cancelled',
    copySuccess: 'JSON copied to clipboard',
    copyError: 'Copy failed, please copy manually',
    refreshSuccess: 'Preview refreshed'
  }
}
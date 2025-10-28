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
  optionName: 'Option Name',
  optionNamePlaceholder: 'Name usually matches ID, can be modified manually',

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
  selectionMechanismLabel: 'Selection Mechanism',
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

  // Other conditions
  otherConditions: 'Other Conditions',
  negativeCondition: 'Negative Condition',
  atLeastCondition: 'At Least Condition',
  minimumCount: 'Minimum Count',
  conditionType: 'Condition Type',
  factionCount: 'Faction',
  typeCount: 'Type',
  satisfiedCount: 'Satisfied Count',

  // Optional attributes list
  optionalAttributes: 'Optional Attributes List',
  addItemOption: 'Add Option',
  noOptionalAttributes: 'No optional attributes available',
  removeItem: 'Delete',
  itemId: 'ID',
  itemName: 'Name',
  itemNameRequired: 'Name (required)',
  items: ' items',

  // Card type options
  cardTypes: {
    asset: 'Asset',
    event: 'Event',
    skill: 'Skill'
  },

  // Faction options
  factions: {
    guardian: 'Guardian',
    seeker: 'Seeker',
    rogue: 'Rogue',
    mystic: 'Mystic',
    survivor: 'Survivor',
    neutral: 'Neutral'
  },

  // Slot options
  slotOptions: {
    hand: 'Hand',
    arcane: 'Arcane',
    accessory: 'Accessory',
    body: 'Body',
    ally: 'Ally',
    tarot: 'Tarot',
    sanity: 'Sanity',
    health: 'Health'
  },

  // Uses options
  usesOptions: {
    charge: 'Charge',
    ammo: 'Ammo',
    supply: 'Supply',
    secret: 'Secret',
    resource: 'Resource',
    evidence: 'Evidence',
    offering: 'Offering'
  },

  // Deck size options
  deckSizes: {
    20: '20 cards',
    25: '25 cards',
    30: '30 cards',
    35: '35 cards',
    40: '40 cards',
    50: '50 cards',
    unit: ' cards'
  },

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
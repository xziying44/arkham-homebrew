export default {
  // Card Title
  title: '📢 TTS Script',

  // Script ID Section
  scriptId: {
    label: '🔖 Script ID',
    placeholder: 'Enter custom ID or use random',
    button: '🎲 Random',
  },

  // Basic Config Section
  basicConfig: {
    title: 'ℹ️ Basic Configuration',
    description: 'This card type only supports basic TTS script configuration. The script ID is used to uniquely identify this card in Tabletop Simulator.',
  },

  // Investigator Specific Config
  investigator: {
    extraTokenLabel: '🏷️ Extra Token (Once per round)',
    extraTokenPlaceholder: 'Select extra token type',
    attributesLabel: '🎯 Attributes',
    willpower: '🧠 Willpower',
    intellect: '📚 Intellect',
    combat: '⚔️ Combat',
    agility: '⚡ Agility',
    phaseButtons: {
      label: '🎮 Phase Button Config',
      enable: 'Enable',
      disable: 'Disable',
      idPlaceholder: 'Button ID',
      labelPlaceholder: 'Select Label',
      colorPlaceholder: 'Select Color',
      addBtn: '➕ Add Button',
    },
    signatureCardsLabel: '🃏 Signature Cards',
    addSignatureCard: '➕ Add Signature Card',
    selectSignatureCards: 'Select Signature Cards',
  },

  // Asset/Event Specific Config
  asset: {
    usesLabel: '🎯 On-Play Token Config',
    count: 'Count',
    token: 'Token',
    tokenPlaceholder: 'Select token type',
    type: 'Type',
    typePlaceholder: 'Select marker type',
    addBtn: '➕ Add Token Config',
  },

  // Location Specific Config
  location: {
    locationIconLabel: '📍 Location Icon',
    connectionIconLabel: '🔗 Connection Icons',
    clueValueLabel: '🔍 Clue Value',
    originalValueLabel: 'Original Value:',
    countLabel: 'Count',
    typeLabel: 'Type',
    perInvestigator: 'Per Investigator',
    fixedCount: 'Fixed Count',
    notSet: 'Not Set',
    frontSide: 'Front Side',
    backSide: 'Back Side',
    locationCard: 'Location Card',
    bothSidesLocation: 'Both sides are location cards, data stored separately in locationFront and locationBack fields',
    frontIsLocation: 'Front side is location card, data stored in locationFront field',
    backIsLocation: 'Back side is location card, data stored in locationBack field',
    onlyBackIsLocation: 'Only back side is location card, data stored in locationBack field',
  },

  // GMNotes Preview Section
  preview: {
    label: '📋 GMNotes Preview',
    copyBtn: '📋 Copy',
    refreshBtn: '🔄 Refresh',
  },

  // Common Buttons
  common: {
    deleteBtn: '🗑️ Delete',
    cancel: 'Cancel',
  },

  // Dropdown Options
  options: {
    extraToken: {
      none: '🚫 None',
      activate: '➡️ Activate',
      engage: '⚔️ Engage',
      evade: '💨 Evade',
      explore: '🔍 Explore',
      fight: '👊 Fight',
      freeTrigger: '⚡ Free Trigger',
      investigate: '🔎 Investigate',
      move: '👣 Move',
      parley: '🤝 Parley',
      playItem: '🎯 Play Item',
      reaction: '⭕ Reaction',
      resource: '💰 Resource',
      scan: '📡 Scan',
      spell: '✨ Spell',
      tome: '📚 Tome',
      guardian: '🛡️ Guardian',
      mystic: '🔮 Mystic',
      neutral: '⚖️ Neutral',
      rogue: '🗡️ Rogue',
      seeker: '📖 Seeker',
      survivor: '🔧 Survivor',
    },

    tokenTypes: {
      resource: '📋 Resource',
      damage: '🔥 Damage',
      horror: '👻 Horror',
      doom: '💀 Doom',
      clue: '🔍 Clue',
    },
    resourceTypes: {
      ammo: '🔫 Ammo',
      resource: '💰 Resource',
      bounty: '🎯 Bounty',
      charge: '⚡ Charge',
      evidence: '🔍 Evidence',
      secret: '🤫 Secret',
      supply: '📦 Supply',
      offering: '🕯️ Offering',
    },
    // Fixed purpose token types
    fixedTokenTypes: {
      damage: '🔥 Damage',
      horror: '👻 Horror',
      doom: '💀 Doom',
      clue: '🔍 Clue',
    },
  },

  // Messages
  messages: {
    copySuccess: 'GMNotes copied to clipboard',
    copyError: 'Copy failed. Please copy manually.',
    regenerateSuccess: 'GMNotes regenerated successfully',
  },
}

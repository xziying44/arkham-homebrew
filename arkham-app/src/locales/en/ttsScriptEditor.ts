export default {
  // Card Title
  title: '📢 TTS Script',

  // Script ID Section
  scriptId: {
    label: '🔖 Script ID',
    placeholder: 'Enter custom ID or use random',
    button: '🎲 Random',
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

  // GMNotes Preview Section
  preview: {
    label: '📋 GMNotes Preview',
    copyBtn: '📋 Copy',
    refreshBtn: '🔄 Refresh',
  },

  // Common Buttons
  common: {
    deleteBtn: '🗑️ Delete',
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

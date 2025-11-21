export interface FieldGroup {
  // group id used for i18n key: cardEditor.groups.<key>
  key: string;
  // field keys from cardTypeConfigs
  fields: string[];
}

export interface CardFieldGroupConfig {
  // default groups for all card types
  default: FieldGroup[];
}

export const cardFieldGroups: CardFieldGroupConfig = {
  default: [
    {
      key: 'basic',
      fields: [
        'name',
        'subtitle',
        'class',
        'weakness_type',
        'subtype',
        'scenario_type',
        'location_type',
        'serial_number',
        'page_number',
        'is_back',
        'traits',
        'submit_icon',
        'shroud',
        'clues',
        'attribute',
        'threshold'
      ]
    },
    {
      key: 'stats',
      fields: [
        'cost',
        'level',
        'slots',
        'slots2',
        'health',
        'horror',
        'enemy_health',
        'enemy_damage',
        'enemy_damage_horror',
        'attack',
        'evade'
      ]
    },
    {
      key: 'text',
      fields: [
        'body',
        'flavor',
        'victory',
        'victory_text',
        'scenario_card.skull',
        'scenario_card.cultist',
        'scenario_card.tablet',
        'scenario_card.elder_thing',
        'scenario_card.resource_name',
        'card_back.option',
        'card_back.other',
        'card_back.requirement',
        'card_back.story',
        'card_back.size'
      ]
    },
    {
      key: 'location',
      fields: ['location_icon', 'location_link']
    },
    {
      key: 'art',
      fields: [
        'encounter_group',
        'picture_base64',
        'use_external_image',
        'external_image',
        'image_filter',
        'share_front_picture'
      ]
    }
  ]
};

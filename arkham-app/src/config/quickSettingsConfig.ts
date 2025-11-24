/**
 * Quick settings configuration for numeric field components
 * Defines quick-select values and max limits for health, horror, cost, and level fields
 */

export interface QuickSettingsFieldConfig {
  quickValues: number[];
  maxValue: number;
  specialValues?: { value: number; label: string; icon?: string }[];
}

export interface QuickSettingsConfig {
  health: QuickSettingsFieldConfig;
  horror: QuickSettingsFieldConfig;
  cost: QuickSettingsFieldConfig;
  level: QuickSettingsFieldConfig;
}

export const defaultQuickSettingsConfig: QuickSettingsConfig = {
  health: {
    quickValues: [1, 2, 3, 4, 5, 6, 7, 8, 9],
    maxValue: 99,
    specialValues: [
      { value: -2, label: 'infinite', icon: '∞' },
      { value: -1, label: 'none', icon: '—' }
    ]
  },
  horror: {
    quickValues: [1, 2, 3, 4, 5, 6, 7, 8, 9],
    maxValue: 99,
    specialValues: [
      { value: -2, label: 'infinite', icon: '∞' },
      { value: -1, label: 'none', icon: '—' }
    ]
  },
  cost: {
    quickValues: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    maxValue: 99,
    specialValues: [
      { value: -2, label: 'variable', icon: 'X' },
      { value: -1, label: 'none', icon: '—' }
    ]
  },
  level: {
    quickValues: [0, 1, 2, 3, 4, 5],
    maxValue: 5,
    specialValues: [
      { value: -2, label: 'customizable', icon: '🧩' },
      { value: -1, label: 'none', icon: '—' }
    ]
  }
};

export type QuickSettingsFieldType = keyof QuickSettingsConfig;

<template>
  <div class="class-selector">
    <!-- Main class buttons -->
    <div class="main-classes">
      <button
        v-for="cls in mainClasses"
        :key="cls.value"
        class="class-button"
        :class="{ selected: isSelected(cls.value) }"
        :style="getButtonStyle(cls.value, isSelected(cls.value))"
        @click="selectClass(cls.value)"
      >
        <span class="class-emoji">{{ cls.emoji }}</span>
        <span class="class-label">{{ cls.label }}</span>
      </button>
    </div>

    <!-- Subclass selector (shown when multi-class is selected) -->
    <div v-if="showSubclasses" class="subclass-section">
      <!-- Subclass slots display -->
      <div class="subclass-slots">
        <div class="subclass-slots-label">{{ $t('cardEditor.classSelector.selectedSubclasses') }}</div>
        <div class="slots-container">
          <div
            v-for="i in maxSubclassCount"
            :key="i"
            class="subclass-slot"
            :class="{ filled: selectedSubclassAt(i - 1) }"
            :style="getSlotStyle(i - 1)"
            @click="removeSubclassAt(i - 1)"
          >
            <span v-if="selectedSubclassAt(i - 1)" class="slot-content">
              <span class="slot-position">{{ i }}</span>
              <span class="slot-label">{{ getSubclassLabel(i - 1) }}</span>
            </span>
            <span v-else class="slot-empty">{{ i }}</span>
          </div>
        </div>
      </div>

      <!-- Available subclasses to select -->
      <div class="subclass-label">{{ $t('cardEditor.classSelector.selectSubclasses') }}</div>
      <div class="subclass-buttons">
        <button
          v-for="cls in availableSubclasses"
          :key="cls.value"
          class="subclass-button"
          :class="{
            selected: isSubclassSelected(cls.value),
            disabled: !isSubclassSelected(cls.value) && currentSubclasses.length >= maxSubclassCount
          }"
          :style="getSubclassStyle(cls.value)"
          @click="toggleSubclass(cls.value)"
          :disabled="!isSubclassSelected(cls.value) && currentSubclasses.length >= maxSubclassCount"
        >
          <span class="subclass-label">{{ cls.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface ClassOption {
  value: string;
  label: string;
  emoji: string;
  color: string;
}

const props = defineProps<{
  value: string;
  subclasses?: string[];
  maxSubclasses?: number;
}>();

const emit = defineEmits<{
  'update:value': [value: string];
  'update:subclasses': [value: string[]];
}>();

// Arkham Horror class colors
const classColors: Record<string, string> = {
  '守护者': '#316BCF',
  '探求者': '#D4A635',
  '流浪者': '#378E31',
  '潜修者': '#6B2D75',
  '生存者': '#C73E3A',
  '中立': '#A0A0A0',
  '弱点': '#1A1A1A',
  '多职阶': '#E5A53A'
};

const surfaceColor = '#FDFDFE';
const neutralTextColor = '#1F2A44';
const neutralBorder = '#D7DEE9';

const mainClasses: ClassOption[] = [
  { value: '守护者', label: t('cardEditor.classSelector.guardian'), emoji: '🛡️', color: classColors['守护者'] },
  { value: '探求者', label: t('cardEditor.classSelector.seeker'), emoji: '🔍', color: classColors['探求者'] },
  { value: '流浪者', label: t('cardEditor.classSelector.rogue'), emoji: '🚶', color: classColors['流浪者'] },
  { value: '潜修者', label: t('cardEditor.classSelector.mystic'), emoji: '🧘', color: classColors['潜修者'] },
  { value: '生存者', label: t('cardEditor.classSelector.survivor'), emoji: '🏕️', color: classColors['生存者'] },
  { value: '中立', label: t('cardEditor.classSelector.neutral'), emoji: '⚪', color: classColors['中立'] },
  { value: '弱点', label: t('cardEditor.classSelector.weakness'), emoji: '⚫', color: classColors['弱点'] },
  { value: '多职阶', label: t('cardEditor.classSelector.multiclass'), emoji: '🌈', color: classColors['多职阶'] }
];

const availableSubclasses = computed(() => {
  return mainClasses.filter(c =>
    !['中立', '弱点', '多职阶'].includes(c.value)
  );
});

const showSubclasses = computed(() => props.value === '多职阶');

const maxSubclassCount = computed(() => props.maxSubclasses || 3);

const currentSubclasses = computed(() => props.subclasses || []);

function isSelected(value: string): boolean {
  return props.value === value;
}

function isSubclassSelected(value: string): boolean {
  return currentSubclasses.value.includes(value);
}

function selectedSubclassAt(index: number): string | null {
  return currentSubclasses.value[index] || null;
}

function getSubclassLabel(index: number): string {
  const value = currentSubclasses.value[index];
  if (!value) return '';
  const cls = mainClasses.find(c => c.value === value);
  return cls ? cls.label : value;
}

function removeSubclassAt(index: number): void {
  const value = currentSubclasses.value[index];
  if (value) {
    const newSubclasses = [...currentSubclasses.value];
    newSubclasses.splice(index, 1);
    emit('update:subclasses', newSubclasses);
  }
}

function getSlotStyle(index: number) {
  const value = currentSubclasses.value[index];
  if (!value) {
    return {
      backgroundColor: 'transparent',
      borderColor: neutralBorder,
      color: '#999'
    };
  }
  const color = classColors[value] || '#666';
  const blend = mixColor(surfaceColor, color, 0.32);
  return {
    background: `linear-gradient(135deg, ${blend} 0%, ${withAlpha(color, 0.24)} 35%, ${withAlpha(color, 0.8)} 100%)`,
    borderColor: withAlpha(color, 0.5),
    color: readableTextColor(color),
    cursor: 'pointer',
    boxShadow: `0 4px 12px ${withAlpha(color, 0.22)}, inset 0 1px 0 ${withAlpha('#FFFFFF', 0.6)}`
  };
}

function selectClass(value: string) {
  emit('update:value', value);
  if (value !== '多职阶') {
    emit('update:subclasses', []);
  }
}

function toggleSubclass(value: string) {
  const current = [...(props.subclasses || [])];
  const index = current.indexOf(value);

  if (index >= 0) {
    // Remove the subclass
    current.splice(index, 1);
  } else if (current.length < maxSubclassCount.value) {
    // Add the subclass
    current.push(value);
  }

  // Emit the updated array to trigger reactive update
  emit('update:subclasses', current);
}

function getButtonStyle(value: string, selected: boolean) {
  const color = classColors[value] || '#64748B';
  const softAccent = mixColor(surfaceColor, color, 0.3);
  const neutralTint = mixColor(surfaceColor, '#A8B3C8', 0.12);
  if (selected) {
    return {
      background: `linear-gradient(135deg, ${softAccent} 0%, ${withAlpha(color, 0.18)} 40%, ${withAlpha(color, 0.85)} 100%)`,
      borderColor: withAlpha(color, 0.45),
      color: readableTextColor(color),
      boxShadow: `0 6px 16px ${withAlpha(color, 0.24)}, inset 0 1px 0 ${withAlpha('#FFFFFF', 0.65)}`
    };
  }
  return {
    background: `linear-gradient(135deg, ${neutralTint} 0%, ${mixColor(surfaceColor, color, 0.12)} 100%)`,
    borderColor: neutralBorder,
    color: neutralTextColor,
    boxShadow: `0 2px 6px rgba(31, 42, 68, 0.08)`
  };
}

function getSubclassStyle(value: string) {
  const color = classColors[value] || '#64748B';
  const selected = isSubclassSelected(value);
  const softAccent = mixColor(surfaceColor, color, 0.28);
  if (selected) {
    return {
      background: `linear-gradient(135deg, ${softAccent} 0%, ${withAlpha(color, 0.18)} 40%, ${withAlpha(color, 0.8)} 100%)`,
      borderColor: withAlpha(color, 0.45),
      color: readableTextColor(color),
      boxShadow: `0 6px 14px ${withAlpha(color, 0.22)}, inset 0 1px 0 ${withAlpha('#FFFFFF', 0.6)}`
    };
  }
  return {
    background: `linear-gradient(135deg, ${mixColor(surfaceColor, '#A8B3C8', 0.08)} 0%, ${mixColor(surfaceColor, color, 0.1)} 100%)`,
    borderColor: neutralBorder,
    color: neutralTextColor
  };
}

function hexToRgb(hex: string) {
  const clean = hex.replace('#', '');
  const full = clean.length === 3 ? clean.split('').map(c => c + c).join('') : clean;
  const r = parseInt(full.substring(0, 2), 16);
  const g = parseInt(full.substring(2, 4), 16);
  const b = parseInt(full.substring(4, 6), 16);
  return { r, g, b };
}

function mixColor(base: string, color: string, ratio: number) {
  const baseRgb = hexToRgb(base);
  const accent = hexToRgb(color);
  const clamp = (v: number) => Math.max(0, Math.min(255, v));
  const r = clamp(Math.round(baseRgb.r * (1 - ratio) + accent.r * ratio));
  const g = clamp(Math.round(baseRgb.g * (1 - ratio) + accent.g * ratio));
  const b = clamp(Math.round(baseRgb.b * (1 - ratio) + accent.b * ratio));
  return `rgb(${r}, ${g}, ${b})`;
}

function withAlpha(color: string, alpha: number) {
  const { r, g, b } = hexToRgb(color);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function readableTextColor(baseColor: string, fallback: string = neutralTextColor) {
  const { r, g, b } = hexToRgb(baseColor);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness > 80 ? fallback : '#FFFFFF';
}
</script>

<style scoped>
.class-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.main-classes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.class-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 12px;
  border: 2px solid;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  /* Fixed width for consistent layout */
  width: 120px;
  flex-shrink: 0;
}

.class-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(31, 42, 68, 0.12);
}

.class-button.selected {
  box-shadow: 0 3px 12px rgba(31, 42, 68, 0.18);
}

.class-emoji {
  font-size: 14px;
}

.class-label {
  font-size: 12px;
}

.subclass-section {
  padding: 12px;
  background: linear-gradient(135deg, #fdfdfe 0%, #f3f5fb 100%);
  border-radius: 10px;
  border: 1px solid #d7dee9;
  box-shadow: 0 2px 8px rgba(31, 42, 68, 0.08);
}

/* Subclass slots */
.subclass-slots {
  margin-bottom: 12px;
}

.subclass-slots-label {
  font-size: 12px;
  color: #1f2a44;
  margin-bottom: 8px;
}

.slots-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.subclass-slot {
  flex: 1;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d7dee9;
  border-radius: 8px;
  background: linear-gradient(135deg, #f9fbff 0%, #eef1f8 100%);
  font-size: 12px;
  transition: all 0.2s ease;
}

.subclass-slot.filled {
  border-style: solid;
  cursor: pointer;
}

.subclass-slot.filled:hover {
  opacity: 0.8;
  transform: scale(0.98);
}

.slot-content {
  display: flex;
  align-items: center;
  gap: 4px;
}

.slot-position {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  font-size: 10px;
  font-weight: bold;
}

.slot-empty {
  color: #ccc;
  font-weight: bold;
}

.subclass-label {
  font-size: 12px;
  color: #1f2a44;
  margin-bottom: 8px;
}

.subclass-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.subclass-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 12px;
  border: 2px solid;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  /* Fixed width for consistent layout */
  width: 120px;
  flex-shrink: 0;
}

.subclass-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.subclass-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.subclass-button .subclass-label {
  margin: 0;
}

/* Dark mode support */
:global(.dark) .subclass-section {
  background: #2a2a2a;
  border-color: #444;
  box-shadow: none;
}

:global(.dark) .class-button:not(.selected),
:global(.dark) .subclass-button:not(.selected) {
  border-color: #444;
  color: #aaa;
}

:global(.dark) .subclass-slot {
  border-color: #444;
  background: #2f2f2f;
}

:global(.dark) .slot-empty {
  color: #555;
}

:global(.dark) .subclass-slots-label,
:global(.dark) .subclass-label {
  color: #aaa;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .class-button {
    padding: 5px 8px;
    font-size: 12px;
  }

  .class-emoji {
    font-size: 12px;
  }

  .class-label {
    font-size: 11px;
  }

  .slots-container {
    flex-direction: column;
    gap: 6px;
  }

  .subclass-slot {
    min-height: 32px;
  }
}
</style>

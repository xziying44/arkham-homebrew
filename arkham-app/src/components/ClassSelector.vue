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
      borderColor: '#d0d0d0',
      color: '#999'
    };
  }
  const color = classColors[value] || '#666';
  return {
    backgroundColor: color,
    borderColor: color,
    color: isLightColor(color) ? '#000' : '#fff',
    cursor: 'pointer'
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
  const color = classColors[value] || '#666';
  if (selected) {
    return {
      backgroundColor: color,
      borderColor: color,
      color: value === '弱点' ? '#fff' : (isLightColor(color) ? '#000' : '#fff')
    };
  }
  return {
    backgroundColor: 'transparent',
    borderColor: '#d0d0d0',
    color: '#666'
  };
}

function getSubclassStyle(value: string) {
  const color = classColors[value] || '#666';
  const selected = isSubclassSelected(value);
  if (selected) {
    return {
      backgroundColor: color,
      borderColor: color,
      color: isLightColor(color) ? '#000' : '#fff'
    };
  }
  return {
    backgroundColor: 'transparent',
    borderColor: '#d0d0d0',
    color: '#666'
  };
}

function isLightColor(color: string): boolean {
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness > 155;
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.class-button.selected {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.class-emoji {
  font-size: 14px;
}

.class-label {
  font-size: 12px;
}

.subclass-section {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
}

/* Subclass slots */
.subclass-slots {
  margin-bottom: 12px;
}

.subclass-slots-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.slots-container {
  display: flex;
  gap: 8px;
}

.subclass-slot {
  flex: 1;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d0d0d0;
  border-radius: 6px;
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
  background: rgba(255, 255, 255, 0.3);
  font-size: 10px;
  font-weight: bold;
}

.slot-empty {
  color: #ccc;
  font-weight: bold;
}

.subclass-label {
  font-size: 12px;
  color: #666;
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
}

:global(.dark) .class-button:not(.selected),
:global(.dark) .subclass-button:not(.selected) {
  border-color: #444;
  color: #aaa;
}

:global(.dark) .subclass-slot {
  border-color: #444;
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

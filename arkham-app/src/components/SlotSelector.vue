<template>
  <div class="slot-selector">
    <button
      v-for="slot in slots"
      :key="slot.value"
      class="slot-button"
      :class="{ selected: value === slot.value }"
      @click="selectSlot(slot.value)"
    >
      <span class="slot-emoji">{{ slot.emoji }}</span>
      <span class="slot-label">{{ slot.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface SlotOption {
  value: string;
  label: string;
  emoji: string;
}

const props = defineProps<{
  value: string;
}>();

const emit = defineEmits<{
  'update:value': [value: string];
}>();

const slots: SlotOption[] = [
  { value: '盟友', label: t('cardEditor.slotSelector.ally'), emoji: '👤' },
  { value: '身体', label: t('cardEditor.slotSelector.body'), emoji: '👕' },
  { value: '饰品', label: t('cardEditor.slotSelector.accessory'), emoji: '💍' },
  { value: '手部', label: t('cardEditor.slotSelector.hand'), emoji: '✋' },
  { value: '双手', label: t('cardEditor.slotSelector.twoHands'), emoji: '🙌' },
  { value: '法术', label: t('cardEditor.slotSelector.arcane'), emoji: '✨' },
  { value: '双法术', label: t('cardEditor.slotSelector.twoArcane'), emoji: '🌟' },
  { value: '塔罗', label: t('cardEditor.slotSelector.tarot'), emoji: '🃏' }
];

function selectSlot(value: string) {
  emit('update:value', value);
}
</script>

<style scoped>
.slot-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.slot-button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 2px solid #d0d0d0;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  color: #666;
}

.slot-button:hover {
  border-color: #999;
  background: #f5f5f5;
  transform: translateY(-1px);
}

.slot-button.selected {
  border-color: #333;
  background: #333;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.slot-emoji {
  font-size: 14px;
}

.slot-label {
  font-size: 12px;
}

/* Dark mode support */
:global(.dark) .slot-button {
  border-color: #444;
  color: #aaa;
}

:global(.dark) .slot-button:hover {
  border-color: #666;
  background: #3a3a3a;
}

:global(.dark) .slot-button.selected {
  border-color: #f5f5f5;
  background: #f5f5f5;
  color: #333;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .slot-button {
    padding: 5px 8px;
    font-size: 12px;
  }

  .slot-emoji {
    font-size: 12px;
  }

  .slot-label {
    font-size: 11px;
  }
}
</style>

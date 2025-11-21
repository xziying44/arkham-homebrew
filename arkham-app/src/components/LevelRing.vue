<template>
  <div class="level-ring-container">
    <!-- Star ring display -->
    <div class="level-ring">
      <span
        v-for="i in 5"
        :key="i"
        class="star"
        :class="{ filled: i <= value && value >= 0 }"
        @click="setLevel(i)"
      >
        ★
      </span>
      <!-- Special value indicator -->
      <span v-if="value === -2" class="special-indicator">🧩</span>
      <span v-else-if="value === -1" class="special-indicator empty">○</span>
    </div>

    <!-- Quick select buttons -->
    <div class="quick-buttons">
      <!-- Row 1: Special values (铺满宽度) -->
      <div class="special-row">
        <button
          v-for="special in specialValues"
          :key="special.value"
          class="quick-button special"
          :class="{ selected: value === special.value }"
          @click="selectValue(special.value)"
          :title="$t(`cardEditor.levelRing.${special.label}`)"
        >
          <span v-if="special.value === -1" class="no-level-icon">○</span>
          <span v-else>{{ special.icon }}</span>
        </button>
      </div>

      <!-- Row 2+: Level buttons 0-5 (响应式布局) -->
      <div class="number-rows">
        <button
          v-for="num in quickValues"
          :key="num"
          class="quick-button"
          :class="{ selected: value === num }"
          @click="selectValue(num)"
        >
          {{ num }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { defaultQuickSettingsConfig } from '@/config/quickSettingsConfig';

const { t } = useI18n();

const props = defineProps<{
  value: number;
}>();

const emit = defineEmits<{
  'update:value': [value: number];
}>();

const config = computed(() => defaultQuickSettingsConfig.level);
const quickValues = computed(() => config.value.quickValues);
const specialValues = computed(() => config.value.specialValues || []);

function selectValue(val: number) {
  emit('update:value', val);
}

function setLevel(level: number) {
  // If clicking the same level, toggle to 0
  if (level === props.value) {
    emit('update:value', 0);
  } else {
    emit('update:value', level);
  }
}
</script>

<style scoped>
.level-ring-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.level-ring {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f9fbff 0%, #f1f4fb 100%);
  border-radius: 20px;
  position: relative;
  border: 1px solid #d7dee9;
  box-shadow: 0 2px 8px rgba(31, 42, 68, 0.08);
}

.star {
  font-size: 20px;
  color: #c3cddd;
  cursor: pointer;
  transition: all 0.2s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.star:hover {
  transform: scale(1.2);
}

.star.filled {
  color: #ffc870;
  text-shadow: 0 0 8px rgba(255, 200, 112, 0.55);
}

.special-indicator {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  pointer-events: none;
}

.special-indicator.empty {
  color: #999;
  font-size: 28px;
}

.quick-buttons {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: stretch;
  width: 100%;
  max-width: 280px;
}

.special-row {
  display: flex;
  gap: 4px;
  justify-content: space-between;
  width: 100%;
}

/* Special value buttons auto-fill width */
.special-row .quick-button {
  flex: 1;
  width: auto;
  min-width: 42px;
}

.number-rows {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: flex-start;
  width: 100%;
}

.quick-button {
  width: 42px;
  height: 42px;
  border: 1px solid #d7dee9;
  border-radius: 8px;
  background: linear-gradient(135deg, #f9fafc 0%, #eef1f8 100%);
  color: #1f2a44;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(31, 42, 68, 0.08);
}

.quick-button:hover {
  border-color: rgba(210, 173, 116, 0.55);
  background: linear-gradient(135deg, #fdfdfe 0%, #f1f4fb 100%);
}

.quick-button.selected {
  border-color: rgba(210, 173, 116, 0.55);
  background: linear-gradient(135deg, #fff5dc 0%, #ffe7bb 100%);
  color: #2f2415;
  box-shadow: 0 3px 10px rgba(234, 194, 135, 0.28);
}

.quick-button.special {
  font-size: 18px;
}

.no-level-icon {
  font-size: 20px;
  color: #999;
}

/* Dark mode */
:global(.dark) .level-ring {
  background: #2a2a2a;
}

:global(.dark) .star {
  color: #555;
}

:global(.dark) .star.filled {
  color: #ffc107;
}

:global(.dark) .quick-button {
  border-color: #444;
  background: #2a2a2a;
  color: #ddd;
}

:global(.dark) .quick-button:hover {
  border-color: #666;
  background: #3a3a3a;
}

:global(.dark) .quick-button.selected {
  border-color: #ffc107;
  background: #3d3000;
  color: #ffc107;
}

/* Mobile */
@media (max-width: 768px) {
  .star {
    font-size: 16px;
  }

  .special-indicator {
    font-size: 20px;
  }

  .quick-button {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }
}
</style>

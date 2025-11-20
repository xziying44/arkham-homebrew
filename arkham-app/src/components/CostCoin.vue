<template>
  <div class="cost-coin-container">
    <!-- Coin display -->
    <div
      class="cost-coin"
      @click="showInput = true"
    >
      <span class="coin-value">{{ displayValue }}</span>
    </div>

    <!-- Quick select buttons -->
    <div class="quick-buttons">
      <!-- Special values -->
      <button
        v-for="special in specialValues"
        :key="special.value"
        class="quick-button special"
        :class="{ selected: value === special.value }"
        @click="selectValue(special.value)"
        :title="$t(`cardEditor.costCoin.${special.label}`)"
      >
        {{ special.icon }}
      </button>

      <!-- Quick numeric values -->
      <button
        v-for="num in quickValues"
        :key="num"
        class="quick-button"
        :class="{ selected: value === num }"
        @click="selectValue(num)"
      >
        {{ num }}
      </button>

      <!-- Custom input trigger -->
      <button
        class="quick-button custom"
        :class="{ selected: isCustomValue }"
        @click="showInput = true"
        :title="$t('cardEditor.costCoin.custom')"
      >
        ...
      </button>
    </div>

    <!-- Custom input modal -->
    <n-modal v-model:show="showInput" preset="dialog" :title="$t('cardEditor.costCoin.enterValue')">
      <n-input-number
        v-model:value="customValue"
        :min="0"
        :max="maxValue"
        :placeholder="$t('cardEditor.costCoin.valuePlaceholder')"
        @keyup.enter="confirmCustomValue"
      />
      <template #action>
        <n-button @click="showInput = false">{{ $t('common.cancel') }}</n-button>
        <n-button type="primary" @click="confirmCustomValue">{{ $t('common.confirm') }}</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { NModal, NInputNumber, NButton } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { defaultQuickSettingsConfig } from '@/config/quickSettingsConfig';

const { t } = useI18n();

const props = defineProps<{
  value: number;
}>();

const emit = defineEmits<{
  'update:value': [value: number];
}>();

const showInput = ref(false);
const customValue = ref<number | null>(null);

const config = computed(() => defaultQuickSettingsConfig.cost);
const quickValues = computed(() => config.value.quickValues);
const maxValue = computed(() => config.value.maxValue);
const specialValues = computed(() => config.value.specialValues || []);

const displayValue = computed(() => {
  const special = specialValues.value.find(s => s.value === props.value);
  if (special) return special.icon;
  return props.value.toString();
});

const isCustomValue = computed(() => {
  return props.value >= 0 &&
    !quickValues.value.includes(props.value) &&
    !specialValues.value.some(s => s.value === props.value);
});

function selectValue(val: number) {
  emit('update:value', val);
}

function confirmCustomValue() {
  if (customValue.value !== null && customValue.value >= 0 && customValue.value <= maxValue.value) {
    emit('update:value', customValue.value);
  }
  showInput.value = false;
  customValue.value = null;
}
</script>

<style scoped>
.cost-coin-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.cost-coin {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: bold;
  font-size: 18px;
  color: #5d4037;
  background: linear-gradient(135deg, #ffd54f, #ffb300);
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.3),
    inset 0 2px 4px rgba(255, 255, 255, 0.4),
    inset 0 -2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
  border: 2px solid #ff8f00;
}

.cost-coin:hover {
  transform: scale(1.05);
}

.coin-value {
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  max-width: 200px;
}

.quick-button {
  width: 28px;
  height: 28px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-button:hover {
  border-color: #999;
  background: #f0f0f0;
}

.quick-button.selected {
  border-color: #ff8f00;
  background: #fff3e0;
  color: #e65100;
}

.quick-button.special {
  font-size: 14px;
}

.quick-button.custom {
  font-size: 10px;
  letter-spacing: 1px;
}

/* Dark mode */
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
  border-color: #ff8f00;
  background: #3d2c00;
  color: #ffd54f;
}

/* Mobile */
@media (max-width: 768px) {
  .cost-coin {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .quick-button {
    width: 24px;
    height: 24px;
    font-size: 11px;
  }
}
</style>

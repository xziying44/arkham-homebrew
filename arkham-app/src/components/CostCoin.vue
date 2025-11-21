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
      <!-- Row 1: Special values (铺满宽度) -->
      <div class="special-row">
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
      </div>

      <!-- Row 2+: Numbers 0-9 + Custom (响应式布局) -->
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
        <!-- Custom input trigger -->
        <button
          class="quick-button custom"
          :class="{ selected: isCustomValue }"
          @click="showInput = true"
          :title="$t('cardEditor.costCoin.custom')"
        >
          <n-icon :size="14">
            <SettingsOutline />
          </n-icon>
        </button>
      </div>
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
import { NModal, NInputNumber, NButton, NIcon } from 'naive-ui';
import { SettingsOutline } from '@vicons/ionicons5';
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
  background: linear-gradient(135deg, #ffd54f 0%, #ffb300 50%, #ff8f00 100%);
  box-shadow:
    0 4px 12px rgba(255, 143, 0, 0.4),
    0 0 20px rgba(255, 179, 0, 0.2),
    inset 0 2px 4px rgba(255, 255, 255, 0.5),
    inset 0 -2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
  border: 2px solid #ff8f00;
  position: relative;
  overflow: hidden;
}

.cost-coin::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.4) 50%, transparent 70%);
  animation: shine 3s ease-in-out infinite;
}

@keyframes shine {
  0% {
    transform: translateX(-100%) rotate(0deg);
  }
  100% {
    transform: translateX(100%) rotate(0deg);
  }
}

.cost-coin:hover {
  transform: scale(1.05) rotate(5deg);
}

.coin-value {
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  position: relative;
  z-index: 1;
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
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  background: #fff;
  color: #333;
  font-size: 16px;
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
  font-size: 18px;
}

.quick-button.custom {
  display: flex;
  align-items: center;
  justify-content: center;
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
    width: 36px;
    height: 36px;
    font-size: 14px;
  }
}
</style>

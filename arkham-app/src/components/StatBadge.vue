<template>
  <div class="stat-badge-container">
    <!-- Badge display -->
    <div
      class="stat-badge"
      :class="[type, { pulse: enablePulse }]"
      @click="showInput = true"
    >
      <span class="stat-value">{{ displayValue }}</span>
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
        :title="$t(`cardEditor.statBadge.${special.label}`)"
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
        :title="$t('cardEditor.statBadge.custom')"
      >
        ...
      </button>
    </div>

    <!-- Custom input modal -->
    <n-modal v-model:show="showInput" preset="dialog" :title="$t('cardEditor.statBadge.enterValue')">
      <n-input-number
        v-model:value="customValue"
        :min="0"
        :max="maxValue"
        :placeholder="$t('cardEditor.statBadge.valuePlaceholder')"
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
import { defaultQuickSettingsConfig, type QuickSettingsFieldType } from '@/config/quickSettingsConfig';

const { t } = useI18n();

const props = withDefaults(defineProps<{
  type: 'health' | 'horror';
  value: number;
  enablePulse?: boolean;
}>(), {
  enablePulse: true
});

const emit = defineEmits<{
  'update:value': [value: number];
}>();

const showInput = ref(false);
const customValue = ref<number | null>(null);

const config = computed(() => defaultQuickSettingsConfig[props.type as QuickSettingsFieldType]);
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
.stat-badge-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-badge {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: bold;
  font-size: 18px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease;
}

.stat-badge:hover {
  transform: scale(1.05);
}

.stat-badge.health {
  background: linear-gradient(135deg, #e53935, #c62828);
}

.stat-badge.horror {
  background: linear-gradient(135deg, #1e88e5, #1565c0);
}

.stat-badge.pulse {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  50% {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  }
}

.stat-value {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
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
  border-color: #333;
  background: #333;
  color: #fff;
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
  border-color: #f5f5f5;
  background: #f5f5f5;
  color: #333;
}

/* Mobile */
@media (max-width: 768px) {
  .stat-badge {
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

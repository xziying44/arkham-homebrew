<template>
  <n-card :title="t('cardEditor.textBoundary.title')" size="small" class="form-card text-boundary-editor-card">
    <n-form label-placement="top" size="small">
      <!-- Body 边界组 -->
      <n-divider title-placement="left">{{ t('cardEditor.textBoundary.body.title') }}</n-divider>
      <n-grid cols="2" x-gap="12" y-gap="16">
        <!-- Top 边界 -->
        <n-grid-item>
          <n-form-item :label="t('cardEditor.textBoundary.body.top')">
            <div class="slider-container">
              <n-slider
                v-model:value="boundaryData.body.top"
                :min="-50"
                :max="50"
                :step="1"
                class="slider"
                @update:value="handleUpdate"
              />
              <n-input-number
                v-model:value="boundaryData.body.top"
                :min="-50"
                :max="50"
                :step="1"
                size="small"
                class="input-number"
                @update:value="handleUpdate"
              />
            </div>
          </n-form-item>
        </n-grid-item>

        <!-- Bottom 边界 -->
        <n-grid-item>
          <n-form-item :label="t('cardEditor.textBoundary.body.bottom')">
            <div class="slider-container">
              <n-slider
                v-model:value="boundaryData.body.bottom"
                :min="-50"
                :max="50"
                :step="1"
                class="slider"
                @update:value="handleUpdate"
              />
              <n-input-number
                v-model:value="boundaryData.body.bottom"
                :min="-50"
                :max="50"
                :step="1"
                size="small"
                class="input-number"
                @update:value="handleUpdate"
              />
            </div>
          </n-form-item>
        </n-grid-item>

        <!-- Left 边界 -->
        <n-grid-item>
          <n-form-item :label="t('cardEditor.textBoundary.body.left')">
            <div class="slider-container">
              <n-slider
                v-model:value="boundaryData.body.left"
                :min="-50"
                :max="50"
                :step="1"
                class="slider"
                @update:value="handleUpdate"
              />
              <n-input-number
                v-model:value="boundaryData.body.left"
                :min="-50"
                :max="50"
                :step="1"
                size="small"
                class="input-number"
                @update:value="handleUpdate"
              />
            </div>
          </n-form-item>
        </n-grid-item>

        <!-- Right 边界 -->
        <n-grid-item>
          <n-form-item :label="t('cardEditor.textBoundary.body.right')">
            <div class="slider-container">
              <n-slider
                v-model:value="boundaryData.body.right"
                :min="-50"
                :max="50"
                :step="1"
                class="slider"
                @update:value="handleUpdate"
              />
              <n-input-number
                v-model:value="boundaryData.body.right"
                :min="-50"
                :max="50"
                :step="1"
                size="small"
                class="input-number"
                @update:value="handleUpdate"
              />
            </div>
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <!-- Flavor Padding 组 -->
      <n-divider title-placement="left">{{ t('cardEditor.textBoundary.flavor.title') }}</n-divider>
      <n-grid cols="1" x-gap="12" y-gap="16">
        <!-- Padding -->
        <n-grid-item>
          <n-form-item :label="t('cardEditor.textBoundary.flavor.padding')">
            <div class="slider-container">
              <n-slider
                v-model:value="boundaryData.flavor.padding"
                :min="0"
                :max="100"
                :step="1"
                class="slider"
                @update:value="handleUpdate"
              />
              <n-input-number
                v-model:value="boundaryData.flavor.padding"
                :min="0"
                :max="100"
                :step="1"
                size="small"
                class="input-number"
                @update:value="handleUpdate"
              />
            </div>
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <!-- 帮助提示 -->
      <n-alert type="info" :title="t('cardEditor.textBoundary.helpTitle')" style="margin-top: 16px;">
        {{ t('cardEditor.textBoundary.helpText') }}
      </n-alert>
    </n-form>
  </n-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

// Props 接口定义
interface TextBoundary {
  body: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  flavor: {
    padding: number;
  };
}

interface Props {
  cardType: string;
  textBoundary?: TextBoundary;
}

// Emits 接口定义
interface Emits {
  (event: 'update:text-boundary', value: TextBoundary): void;
}

const { t } = useI18n();
const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// 默认值
const defaultBoundary: TextBoundary = {
  body: {
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
  },
  flavor: {
    padding: 20
  }
};

// 本地响应式数据
const boundaryData = ref<TextBoundary>({ ...defaultBoundary });

// 监听 props 变化，同步到本地数据
watch(
  () => props.textBoundary,
  (newBoundary) => {
    if (newBoundary) {
      boundaryData.value = {
        body: { ...defaultBoundary.body, ...newBoundary.body },
        flavor: { ...defaultBoundary.flavor, ...newBoundary.flavor }
      };
    } else {
      boundaryData.value = { ...defaultBoundary };
    }
  },
  { immediate: true, deep: true }
);

// 更新处理函数
const handleUpdate = () => {
  emit('update:text-boundary', JSON.parse(JSON.stringify(boundaryData.value)));
};
</script>

<style scoped>
.text-boundary-editor-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 40px;
}

.slider {
  flex: 1 1 auto;
  min-width: 120px;
  max-width: 100%;
}

.input-number {
  width: 80px;
  flex-shrink: 0;
}
</style>

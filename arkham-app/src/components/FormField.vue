<template>
  <!-- 文本输入 -->
  <n-form-item v-if="field.type === 'text'" :label="field.name" :path="field.key">
    <n-input 
      :value="value" 
      @update:value="$emit('update:value', $event)"
      :placeholder="`请输入${getCleanFieldName(field.name)}`" 
    />
  </n-form-item>

  <!-- 长文本输入 -->
  <n-form-item v-else-if="field.type === 'textarea'" :label="field.name" :path="field.key">
    <n-input 
      :value="value" 
      @update:value="$emit('update:value', $event)"
      type="textarea"
      :rows="field.rows || 3"
      :maxlength="field.maxlength"
      :placeholder="`请输入${getCleanFieldName(field.name)}`"
      show-count
      :autosize="{ minRows: field.rows || 3, maxRows: (field.rows || 3) + 2 }"
    />
  </n-form-item>

  <!-- 数字输入 -->
  <n-form-item v-else-if="field.type === 'number'" :label="field.name" :path="field.key">
    <n-input-number 
      :value="value" 
      @update:value="$emit('update:value', $event)"
      :min="field.min" 
      :max="field.max" 
      :placeholder="`请输入${getCleanFieldName(field.name)}`" 
    />
  </n-form-item>

  <!-- 下拉单选 -->
  <n-form-item v-else-if="field.type === 'select'" :label="field.name" :path="field.key">
    <n-select 
      :value="value" 
      @update:value="$emit('update:value', $event)"
      :options="field.options" 
      :placeholder="`请选择${getCleanFieldName(field.name)}`" 
    />
  </n-form-item>

  <!-- 多选数组 -->
  <n-form-item v-else-if="field.type === 'multi-select'" :label="field.name" :path="field.key">
    <div class="multi-select-container">
      <n-select 
        :value="null" 
        :options="field.options" 
        :placeholder="`添加${getCleanFieldName(field.name)}`"
        @update:value="$emit('add-multi-select-item', $event)" 
        clearable 
      />
      <div v-if="value && value.length > 0" class="selected-items">
        <n-tag 
          v-for="(item, index) in value" 
          :key="index" 
          closable
          @close="$emit('remove-multi-select-item', index)" 
          class="item-tag"
        >
          {{ item }}
        </n-tag>
      </div>
    </div>
  </n-form-item>

  <!-- 字符串数组 -->
  <n-form-item v-else-if="field.type === 'string-array'" :label="field.name" :path="field.key">
    <div class="string-array-container">
      <n-space align="center">
        <n-input 
          :value="newStringValue" 
          @update:value="$emit('update:new-string-value', $event)"
          :placeholder="`输入${getCleanFieldName(field.name)}`"
          @keyup.enter="$emit('add-string-array-item')" 
        />
        <n-button @click="$emit('add-string-array-item')" size="small">添加</n-button>
      </n-space>
      <div v-if="value && value.length > 0" class="selected-items">
        <n-tag 
          v-for="(item, index) in value" 
          :key="index" 
          closable
          @close="$emit('remove-string-array-item', index)" 
          class="item-tag"
        >
          {{ item }}
        </n-tag>
      </div>
    </div>
  </n-form-item>
</template>

<script setup lang="ts">
import type { FormField } from '@/config/cardTypeConfigs';

interface Props {
  field: FormField;
  value: any;
  newStringValue: string;
}

defineProps<Props>();

defineEmits<{
  'update:value': [value: any];
  'update:new-string-value': [value: string];
  'add-multi-select-item': [value: string];
  'remove-multi-select-item': [index: number];
  'add-string-array-item': [];
  'remove-string-array-item': [index: number];
}>();

// 去掉emoji和空格，获取纯净的字段名
// 只保留中文、英文字母和数字，移除其他所有字符
const getCleanFieldName = (fieldName: string): string => {
  return fieldName.replace(/[^\u4e00-\u9fffa-zA-Z0-9]/g, '').trim();
};

</script>

<style scoped>
.multi-select-container,
.string-array-container {
  width: 100%;
}

.selected-items {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.item-tag {
  margin: 0;
}

/* 长文本框样式优化 */
:deep(.n-input--textarea) {
  min-height: auto;
}

:deep(.n-input--textarea .n-input__input-el) {
  line-height: 1.5;
  font-family: inherit;
}
</style>

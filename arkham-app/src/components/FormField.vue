<template>
  <!-- 文本输入 -->
  <n-form-item v-if="field.type === 'text'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-input :value="value" @update:value="$emit('update:value', $event)"
      :placeholder="`请输入${getCleanFieldName(field.name)}`" />
  </n-form-item>

  <!-- 长文本输入 -->
  <n-form-item v-else-if="field.type === 'textarea'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-input :value="value" @update:value="$emit('update:value', $event)" type="textarea" :rows="field.rows || 3"
      :maxlength="field.maxlength" :placeholder="`请输入${getCleanFieldName(field.name)}`" show-count
      :autosize="{ minRows: field.rows || 3, maxRows: (field.rows || 3) + 2 }" />
  </n-form-item>

  <!-- 数字输入 -->
  <n-form-item v-else-if="field.type === 'number'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-input-number :value="value" @update:value="$emit('update:value', $event)" :min="field.min" :max="field.max"
      :placeholder="`请输入${getCleanFieldName(field.name)}`" />
  </n-form-item>

  <!-- 下拉单选 -->
  <n-form-item v-else-if="field.type === 'select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-select :value="value" @update:value="$emit('update:value', $event)" :options="field.options"
      :placeholder="`请选择${getCleanFieldName(field.name)}`" />
  </n-form-item>

  <!-- 多选数组 -->
  <n-form-item v-else-if="field.type === 'multi-select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <div class="multi-select-container">
      <n-select :value="null" :options="field.options" :placeholder="`添加${getCleanFieldName(field.name)}`"
        @update:value="$emit('add-multi-select-item', $event)" clearable />
      <div v-if="value && value.length > 0" class="selected-items">
        <n-tag v-for="(item, index) in value" :key="index" closable @close="$emit('remove-multi-select-item', index)"
          class="item-tag">
          {{ item }}
        </n-tag>
      </div>
    </div>
  </n-form-item>

  <!-- 字符串数组 -->
  <n-form-item v-else-if="field.type === 'string-array'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <div class="string-array-container">
      <n-space align="center">
        <n-input :value="newStringValue" @update:value="$emit('update:new-string-value', $event)"
          :placeholder="`输入${getCleanFieldName(field.name)}`" @keyup.enter="$emit('add-string-array-item')" />
        <n-button @click="$emit('add-string-array-item')" size="small">添加</n-button>
      </n-space>
      <div v-if="value && value.length > 0" class="selected-items">
        <n-tag v-for="(item, index) in value" :key="index" closable @close="$emit('remove-string-array-item', index)"
          class="item-tag">
          {{ item }}
        </n-tag>
      </div>
    </div>
  </n-form-item>

  <!-- 图片上传 -->
  <n-form-item v-else-if="field.type === 'image'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          title="查看字段说明">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <div class="image-upload-container">
      <!-- 图片预览 -->
      <div v-if="value && value.startsWith('data:image')" class="image-preview">
        <img :src="value" :alt="getCleanFieldName(field.name)" class="preview-image" />
        <div class="image-actions">
          <n-button size="small" @click="$emit('remove-image')" quaternary type="error">
            <template #icon>
              <n-icon :component="TrashOutline" />
            </template>
            删除
          </n-button>
        </div>
      </div>

      <!-- 上传按钮 -->
      <div v-else class="upload-area">
        <n-upload :file-list="[]" :show-file-list="false" accept="image/*" @change="handleFileChange" :max="1">
          <n-upload-dragger>
            <div class="upload-content">
              <n-icon size="48" :depth="3">
                <ImageOutline />
              </n-icon>
              <n-text style="font-size: 16px">
                点击或者拖拽图片到该区域来上传
              </n-text>
              <n-p depth="3" style="margin: 8px 0 0 0">
                支持 JPG、PNG、GIF、WebP 等格式，大小不超过 {{ formatFileSize(field.maxSize || 5 * 1024 * 1024) }}
              </n-p>
            </div>
          </n-upload-dragger>
        </n-upload>
      </div>

      <!-- 错误信息 -->
      <div v-if="imageError" class="error-message">
        <n-alert type="error" :show-icon="false">
          {{ imageError }}
        </n-alert>
      </div>
    </div>
  </n-form-item>

  <!-- 帮助文本模态框 -->
  <n-modal v-model:show="showHelpModal" preset="dialog" title="字段说明" style="width: 600px;">
    <div class="help-content">
      <pre class="help-text">{{ field.helpText }}</pre>
    </div>
    <template #action>
      <n-space>

        <n-button @click="showHelpModal = false" type="primary">关闭</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { UploadFileInfo } from 'naive-ui';
import { TrashOutline, ImageOutline, HelpCircleOutline, CopyOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import type { FormField } from '@/config/cardTypeConfigs';

interface Props {
  field: FormField;
  value: any;
  newStringValue: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:value': [value: any];
  'update:new-string-value': [value: string];
  'add-multi-select-item': [value: string];
  'remove-multi-select-item': [index: number];
  'add-string-array-item': [];
  'remove-string-array-item': [index: number];
  'remove-image': [];
}>();

const message = useMessage();
const imageError = ref('');
const showHelpModal = ref(false);



// 去掉emoji和空格，获取纯净的字段名
const getCleanFieldName = (fieldName: string): string => {
  return fieldName.replace(/[^\u4e00-\u9fffa-zA-Z0-9]/g, '').trim();
};

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 验证图片文件
const validateImageFile = (file: File, field: FormField): string | null => {
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
  if (!validTypes.includes(file.type)) {
    return '不支持的图片格式，请选择 JPG、PNG、GIF、WebP 或 SVG 文件';
  }

  const maxSize = field.maxSize || 5 * 1024 * 1024;
  if (file.size > maxSize) {
    return `文件大小超过限制，最大支持 ${formatFileSize(maxSize)}`;
  }

  return null;
};

// 将文件转换为 base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      resolve(result);
    };
    reader.onerror = () => {
      reject(new Error('文件读取失败'));
    };
    reader.readAsDataURL(file);
  });
};

// 处理文件选择
const handleFileChange = async (data: { file: UploadFileInfo; fileList: UploadFileInfo[] }) => {
  const { file } = data;

  if (!file.file) {
    return;
  }

  try {
    imageError.value = '';

    const error = validateImageFile(file.file, props.field);
    if (error) {
      imageError.value = error;
      return;
    }

    const base64 = await fileToBase64(file.file);
    emit('update:value', base64);

  } catch (error) {
    console.error('处理图片文件失败:', error);
    imageError.value = '图片处理失败，请重试';
  }
};
</script>

<style scoped>
.multi-select-container,
.string-array-container,
.image-upload-container {
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

/* 字段标签样式 */
.field-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.help-button {
  color: #909399;
  transition: color 0.2s ease;
}

.help-button:hover {
  color: #409eff;
}

/* 帮助文本模态框样式 */
.help-content {
  max-height: 400px;
  overflow-y: auto;
}

.help-text {
  white-space: pre-wrap;
  line-height: 1.6;
  font-family: inherit;
  margin: 0;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  word-wrap: break-word;
  font-size: 14px;
  color: #333;
}

/* 图片上传相关样式 */
.image-preview {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  object-fit: contain;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  padding: 4px;
}

.upload-area {
  width: 100%;
}

.upload-content {
  text-align: center;
  padding: 20px;
}

.error-message {
  margin-top: 12px;
}

/* 长文本框样式优化 */
:deep(.n-input--textarea) {
  min-height: auto;
}

:deep(.n-input--textarea .n-input__input-el) {
  line-height: 1.5;
  font-family: inherit;
}

/* 上传组件样式优化 */
:deep(.n-upload-dragger) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  transition: border-color 0.3s ease;
}

:deep(.n-upload-dragger:hover) {
  border-color: #40a9ff;
}

:deep(.n-upload-dragger.n-upload-dragger--drag-over) {
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.02);
}
</style>

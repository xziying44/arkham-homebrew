<template>
  <!-- 文本输入 -->
  <n-form-item v-if="field.type === 'text'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-input :value="value" @update:value="$emit('update:value', $event)"
      :placeholder="$t('cardEditor.field.pleaseEnter', { name: getCleanFieldName(field.name) })" />
  </n-form-item>

  <!-- 长文本输入 -->
  <n-form-item v-else-if="field.type === 'textarea'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-input :value="value" @update:value="$emit('update:value', $event)" type="textarea" :rows="field.rows || 3"
      :maxlength="field.maxlength" :placeholder="$t('cardEditor.field.pleaseEnter', { name: getCleanFieldName(field.name) })" show-count
      :autosize="{ minRows: field.rows || 3, maxRows: (field.rows || 3) + 2 }" />
  </n-form-item>

  <!-- 数字输入 -->
  <n-form-item v-else-if="field.type === 'number'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-input-number :value="value" @update:value="$emit('update:value', $event)" :min="field.min" :max="field.max"
      :placeholder="$t('cardEditor.field.pleaseEnter', { name: getCleanFieldName(field.name) })" />
  </n-form-item>

  <!-- 下拉单选 -->
  <n-form-item v-else-if="field.type === 'select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-select :value="value" @update:value="$emit('update:value', $event)" :options="field.options"
      :placeholder="$t('cardEditor.field.pleaseSelect', { name: getCleanFieldName(field.name) })" />
  </n-form-item>

  <!-- 多选数组 -->
  <n-form-item v-else-if="field.type === 'multi-select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <div class="multi-select-container">
      <n-select :value="null" :options="field.options" :placeholder="$t('cardEditor.field.add', { name: getCleanFieldName(field.name) })"
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
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <div class="string-array-container">
      <n-space align="center">
        <n-input :value="newStringValue" @update:value="$emit('update:new-string-value', $event)"
          :placeholder="$t('cardEditor.field.input', { name: getCleanFieldName(field.name) })" @keyup.enter="$emit('add-string-array-item')" />
        <n-button @click="$emit('add-string-array-item')" size="small">{{ $t('cardEditor.field.addItem') }}</n-button>
      </n-space>
      <div v-if="value && value.length > 0" class="selected-items">
        <n-tag v-for="(item, index) in value" :key="index" closable @close="$emit('remove-string-array-item', index)"
          class="item-tag">
          {{ item }}
        </n-tag>
      </div>
    </div>
  </n-form-item>

  <!-- 遭遇组选择 -->
  <n-form-item v-else-if="field.type === 'encounter-group-select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
        </n-button>
      </div>
    </template>
    <n-select :value="value" @update:value="$emit('update:value', $event)" :options="encounterGroupOptions"
      :placeholder="$t('cardEditor.field.pleaseSelect', { name: getCleanFieldName(field.name) })" :loading="loadingEncounterGroups" clearable filterable
      @focus="loadEncounterGroups" />
  </n-form-item>

  <!-- 图片上传 -->
  <n-form-item v-else-if="field.type === 'image'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" quaternary circle @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
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
            {{ $t('cardEditor.field.delete') }}
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
                {{ $t('cardEditor.field.clickOrDragToUpload') }}
              </n-text>
              <n-p depth="3" style="margin: 8px 0 0 0">
                {{ $t('cardEditor.field.supportedFormats', { size: formatFileSize(field.maxSize || 5 * 1024 * 1024) }) }}
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
  <n-modal v-model:show="showHelpModal" preset="dialog" :title="$t('cardEditor.field.fieldDescription')" style="width: 600px;">
    <div class="help-content">
      <pre class="help-text">{{ field.helpText }}</pre>
    </div>
    <template #action>
      <n-space>
        <n-button @click="showHelpModal = false" type="primary">{{ $t('cardEditor.field.close') }}</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { UploadFileInfo } from 'naive-ui';
import { TrashOutline, ImageOutline, HelpCircleOutline, CopyOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n'; // 新增
import type { FormField } from '@/config/cardTypeConfigs';
import { ConfigService } from '@/api';

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

const { t } = useI18n(); // 新增
const message = useMessage();
const imageError = ref('');
const showHelpModal = ref(false);
// 遭遇组相关状态
const encounterGroupOptions = ref<Array<{label: string, value: string}>>([]);
const loadingEncounterGroups = ref(false);
const encounterGroupsLoaded = ref(false);

// 加载遭遇组列表
const loadEncounterGroups = async () => {
  // 如果已经加载过或正在加载中，则跳过
  if (encounterGroupsLoaded.value || loadingEncounterGroups.value) {
    return;
  }
  try {
    loadingEncounterGroups.value = true;
    const encounterGroups = await ConfigService.getEncounterGroups();
    
    // 转换为select组件需要的格式
    encounterGroupOptions.value = encounterGroups.map(group => ({
      label: group,
      value: group
    }));
    
    encounterGroupsLoaded.value = true;
  } catch (error) {
    console.error('加载遭遇组列表失败:', error);
    message.error(t('cardEditor.field.loadEncounterGroupsFailed'));
    
    // 提供一个空选项，避免用户无法操作
    encounterGroupOptions.value = [
      { label: t('cardEditor.field.noAvailableEncounterGroups'), value: '' }
    ];
  } finally {
    loadingEncounterGroups.value = false;
  }
};

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
    return t('cardEditor.field.unsupportedImageFormat');
  }

  const maxSize = field.maxSize || 5 * 1024 * 1024;
  if (file.size > maxSize) {
    return t('cardEditor.field.fileSizeExceeded', { size: formatFileSize(maxSize) });
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
      reject(new Error(t('cardEditor.field.fileReadFailed')));
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
    imageError.value = t('cardEditor.field.imageProcessFailed');
  }
};
</script>

<style scoped>
/* 样式保持不变 */
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

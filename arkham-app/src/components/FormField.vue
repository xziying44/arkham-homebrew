<template>
  <!-- 文本输入 -->
  <n-form-item v-if="field.type === 'text'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
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
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <n-input :value="value" @update:value="$emit('update:value', $event)" type="textarea" :rows="field.rows || 3"
      :maxlength="field.maxlength" :placeholder="$t('cardEditor.field.pleaseEnter', { name: getCleanFieldName(field.name) })" show-count
      :autosize="{ minRows: field.rows || 5, maxRows: (field.rows || 5) + 3 }" />
  </n-form-item>

  <!-- 数字输入 -->
  <n-form-item v-else-if="field.type === 'number'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <n-input-number :value="value" @update:value="$emit('update:value', $event)" :min="field.min" :max="field.max"
      :placeholder="$t('cardEditor.field.pleaseEnter', { name: getCleanFieldName(field.name) })" />
  </n-form-item>

  <!-- 地点图标：下拉单选（带SVG图标） -->
  <n-form-item v-else-if="field.type === 'select' && field.key === 'location_icon'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <n-select :value="value" @update:value="$emit('update:value', $event)" :options="field.options"
      :render-label="renderLocationOptionLabel"
      :consistent-menu-width="false"
      :placeholder="$t('cardEditor.field.pleaseSelect', { name: getCleanFieldName(field.name) })" />
  </n-form-item>

  <!-- 其他下拉单选 -->
  <n-form-item v-else-if="field.type === 'select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
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
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <div class="multi-select-container">
      <n-select :value="null" :options="field.options"
        :render-label="field.key === 'location_link' ? renderLocationOptionLabel : undefined"
        :consistent-menu-width="false"
        :placeholder="$t('cardEditor.field.add', { name: getCleanFieldName(field.name) })"
        @update:value="$emit('add-multi-select-item', $event)" clearable />
      <div v-if="value && value.length > 0" class="selected-items">
        <n-tag v-for="(item, index) in value" :key="index" closable @close="$emit('remove-multi-select-item', index)"
          class="item-tag">
          <span class="loc-tag" v-if="field.key === 'location_link'">
            <img v-if="getLocationIconUrl(item)" :src="getLocationIconUrl(item) as string" class="loc-icon" />
            <span>{{ getMultiSelectLabelNoEmoji(item, field) }}</span>
          </span>
          <template v-else>{{ getMultiSelectLabel(item, field) }}</template>
        </n-tag>
      </div>
    </div>
  </n-form-item>

  <!-- 字符串数组 -->
  <n-form-item v-else-if="field.type === 'string-array'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
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
        <div v-for="(item, index) in value" :key="index" class="string-array-item">
          <!-- 编辑模式 -->
          <div v-if="editingIndex === index" class="editing-item">
            <n-input 
              v-model:value="editingValue" 
              size="small" 
              :placeholder="$t('cardEditor.field.editItem')"
              @keyup.enter="confirmEdit"
              @keyup.escape="cancelEdit"
            />
            <n-space size="small">
              <n-button size="small" type="primary" @click="confirmEdit">
                <template #icon>
                  <n-icon :component="CheckmarkOutline" />
                </template>
              </n-button>
              <n-button size="small" @click="cancelEdit">
                <template #icon>
                  <n-icon :component="CloseOutline" />
                </template>
              </n-button>
            </n-space>
          </div>
          <!-- 显示模式 -->
          <div v-else class="display-item">
            <n-tag class="item-content">{{ item }}</n-tag>
            <n-space size="small" class="item-controls">
              <!-- 向上移动 -->
              <n-button 
                size="tiny" 
                quaternary 
                @click="$emit('move-string-array-item-up', index)"
                :disabled="index === 0"
                :title="$t('cardEditor.field.moveUp')"
              >
                <template #icon>
                  <n-icon :component="ArrowUpOutline" size="12" />
                </template>
              </n-button>
              <!-- 向下移动 -->
              <n-button 
                size="tiny" 
                quaternary 
                @click="$emit('move-string-array-item-down', index)"
                :disabled="index === value.length - 1"
                :title="$t('cardEditor.field.moveDown')"
              >
                <template #icon>
                  <n-icon :component="ArrowDownOutline" size="12" />
                </template>
              </n-button>
              <!-- 编辑 -->
              <n-button 
                size="tiny" 
                quaternary 
                @click="startEditing(index)"
                :title="$t('cardEditor.field.edit')"
              >
                <template #icon>
                  <n-icon :component="CreateOutline" size="12" />
                </template>
              </n-button>
              <!-- 删除 -->
              <n-button 
                size="tiny" 
                quaternary 
                type="error"
                @click="$emit('remove-string-array-item', index)"
                :title="$t('cardEditor.field.delete')"
              >
                <template #icon>
                  <n-icon :component="TrashOutline" size="12" />
                </template>
              </n-button>
            </n-space>
          </div>
        </div>
      </div>
    </div>
  </n-form-item>

  <!-- 遭遇组选择 -->
  <n-form-item v-else-if="field.type === 'encounter-group-select'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <n-select :value="value" @update:value="$emit('update:value', $event)" :options="encounterGroupOptions"
      :placeholder="$t('cardEditor.field.pleaseSelect', { name: getCleanFieldName(field.name) })" :loading="loadingEncounterGroups" clearable filterable
      @focus="loadEncounterGroups" />
  </n-form-item>

  <!-- 职阶选择器 -->
  <n-form-item v-else-if="field.type === 'class-selector'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <ClassSelector
      :value="value"
      :subclasses="props.subclasses || []"
      @update:value="$emit('update:value', $event)"
      @update:subclasses="$emit('update:subclasses', $event)"
    />
  </n-form-item>

  <!-- 槽位选择器 -->
  <n-form-item v-else-if="field.type === 'slot-selector'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <SlotSelector :value="value || ''" @update:value="$emit('update:value', $event)" />
  </n-form-item>

  <!-- 生命/理智徽章 -->
  <n-form-item v-else-if="field.type === 'stat-badge'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <StatBadge :type="field.statType || 'health'" :value="value ?? -1" @update:value="$emit('update:value', $event)" />
  </n-form-item>

  <!-- 费用金币 -->
  <n-form-item v-else-if="field.type === 'cost-coin'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <CostCoin :value="value ?? -1" @update:value="$emit('update:value', $event)" />
  </n-form-item>

  <!-- 等级星环 -->
  <n-form-item v-else-if="field.type === 'level-ring'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
        </n-button>
      </div>
    </template>
    <LevelRing :value="value ?? -1" @update:value="$emit('update:value', $event)" />
  </n-form-item>

  <!-- 图片上传 -->
  <n-form-item v-else-if="field.type === 'image'" :path="field.key">
    <template #label>
      <div class="field-label">
        <span>{{ field.name }}</span>
        <n-button v-if="field.helpText" size="tiny" @click="showHelpModal = true" class="help-button"
          :title="$t('cardEditor.field.viewFieldDescription')">
          <template #icon>
            <n-icon :component="HelpCircleOutline" size="14" />
          </template>
          {{ $t('cardEditor.field.help') }}
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
import { ref, onMounted, h } from 'vue';
import type { UploadFileInfo } from 'naive-ui';
import { TrashOutline, ImageOutline, HelpCircleOutline, CopyOutline, ArrowUpOutline, ArrowDownOutline, CreateOutline, CheckmarkOutline, CloseOutline } from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n'; // 新增
import type { FormField } from '@/config/cardTypeConfigs';
import { ConfigService } from '@/api';
import { getIconUrlByChinese } from '@/config/locationIcons';
// 导入新的特殊组件
import ClassSelector from './ClassSelector.vue';
import SlotSelector from './SlotSelector.vue';
import StatBadge from './StatBadge.vue';
import CostCoin from './CostCoin.vue';
import LevelRing from './LevelRing.vue';

interface Props {
  field: FormField;
  value: any;
  newStringValue: string;
  subclasses?: string[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:value': [value: any];
  'update:subclasses': [value: string[]];
  'update:new-string-value': [value: string];
  'add-multi-select-item': [value: string];
  'remove-multi-select-item': [index: number];
  'add-string-array-item': [];
  'remove-string-array-item': [index: number];
  'move-string-array-item-up': [index: number];
  'move-string-array-item-down': [index: number];
  'edit-string-array-item': [index: number, newValue: string];
  'remove-image': [];
}>();

const { t } = useI18n(); // 新增
const message = useMessage();
const imageError = ref('');
const showHelpModal = ref(false);
// 字符串数组编辑状态
const editingIndex = ref<number | null>(null);
const editingValue = ref('');
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

// 字符串数组编辑相关函数
const startEditing = (index: number) => {
  editingIndex.value = index;
  editingValue.value = props.value[index];
};

const confirmEdit = () => {
  if (editingIndex.value !== null && editingValue.value.trim()) {
    emit('edit-string-array-item', editingIndex.value, editingValue.value.trim());
  }
  cancelEdit();
};

const cancelEdit = () => {
  editingIndex.value = null;
  editingValue.value = '';
};

// 获取多选组件中项目的翻译标签
const getMultiSelectLabel = (itemValue: string, field: FormField): string => {
  if (!field.options || !Array.isArray(field.options)) {
    return itemValue; // 如果没有选项数组，返回原始值
  }

  const option = field.options.find(opt => opt.value === itemValue);
  return option ? option.label : itemValue; // 找到对应选项则返回标签，否则返回原始值
};

// 去掉emoji用于纯文本展示
const stripEmoji = (s: string): string => s.replace(/[^\u4e00-\u9fffa-zA-Z0-9\s]/g, '').trim();

const getMultiSelectLabelNoEmoji = (itemValue: string, field: FormField): string => {
  const label = getMultiSelectLabel(itemValue, field);
  return stripEmoji(label);
};

// 选项渲染：地点图标（带SVG）
const renderLocationOptionLabel = (option: any) => {
  const src = getIconUrlByChinese(option.value as string);
  const text = stripEmoji(String(option.label ?? option.value ?? ''));
  const imgStyle = 'width:14px;height:14px;display:inline-block;vertical-align:middle;object-fit:contain;';
  return h('div', { class: 'loc-opt', style: 'display:inline-flex;align-items:center;gap:6px;' }, [
    src ? h('img', { src, class: 'loc-icon', style: imgStyle }) : null,
    h('span', { style: 'line-height:1;display:inline-block;vertical-align:middle;' }, text)
  ]);
};

const getLocationIconUrl = (value: string): string | null => getIconUrlByChinese(value);

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

/* 字符串数组项目样式 */
.string-array-item {
  width: 100%;
  margin-bottom: 8px;
}

.string-array-item:last-child {
  margin-bottom: 0;
}

.editing-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #f9f9f9;
}

.editing-item .n-input {
  flex: 1;
}

.display-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid transparent;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.display-item:hover {
  background: #f5f5f5;
  border-color: #e0e0e0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-controls {
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.display-item:hover .item-controls {
  opacity: 1;
}

.item-controls .n-button {
  min-width: 24px;
  height: 24px;
}

/* 字符串数组容器特殊样式覆盖 */
.string-array-container .selected-items {
  flex-direction: column;
  align-items: stretch;
}

/* 字段标签样式 */
.field-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.help-button {
  color: #606266;
  background: #f4f4f5;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  min-height: 20px;
}

.help-button:hover {
  color: #409eff;
  background: #ecf5ff;
  border-color: #b3d8ff;
}

.help-button:active {
  transform: scale(0.95);
}

.loc-opt {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.loc-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
:deep(.n-base-select-menu .n-base-select-option) {
  padding: 4px 8px;
}
:deep(.n-base-select-menu .n-base-select-option__content) {
  display: inline-flex;
  align-items: center;
}
:deep(.loc-opt) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
:deep(.loc-icon) {
  width: 14px;
  height: 14px;
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
  
  /* --- 新增的核心代码 --- */
  -webkit-user-select: text; /* 兼容 WebKit (pywebview 在 macOS/Linux 上常用) */
  -moz-user-select: text;    /* 兼容 Firefox */
  -ms-user-select: text;     /* 兼容 IE/旧版 Edge */
  user-select: text;         /* 标准属性 */
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

<template>
  <div class="language-config-container">
    <!-- 顶部标题栏 -->
    <div class="language-config-header">
      <h2>{{ $t('languageConfig.title') }}</h2>
      <div class="header-actions">
        <n-button type="primary" @click="showAddDialog = true" size="large">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          {{ $t('languageConfig.actions.addLanguage') }}
        </n-button>
      </div>
    </div>

    <div class="language-config-content">
      <!-- 左侧语言列表 -->
      <div class="language-list-panel">
        <div class="panel-header">
          <h3>{{ $t('languageConfig.languageList.title') }}</h3>
          <div class="panel-header-actions">
            <n-button text @click="refreshFonts" :loading="loading" :title="$t('languageConfig.actions.refreshFonts')">
              <n-icon :component="RefreshOutline" />
            </n-button>
          </div>
        </div>
        <n-scrollbar class="language-list">
          <div
            v-for="(lang, index) in languages"
            :key="lang.code + '_' + index"
            class="language-item"
            :class="{ 'active': index === activeIndex }"
            @click="activeIndex = index"
          >
            <div class="language-icon">🌐</div>
            <div class="language-info">
              <div class="language-name">{{ lang.name || lang.code }}</div>
              <div class="language-code-badge">{{ lang.code }}</div>
            </div>
            <div class="language-item-actions">
              <n-button
                text
                type="error"
                @click.stop="confirmDelete(index)"
                :title="$t('languageConfig.actions.delete')"
                size="small"
                class="delete-button"
              >
                <n-icon :component="TrashOutline" />
              </n-button>
            </div>
          </div>
          <n-empty v-if="!languages.length && !loading" :description="$t('languageConfig.languageList.empty')">
            <template #icon>
              <n-icon :component="LanguageOutline" />
            </template>
            <template #extra>
              <n-text depth="3">{{ $t('languageConfig.languageList.empty') }}</n-text>
            </template>
          </n-empty>
        </n-scrollbar>
      </div>

      <!-- 右侧详情编辑器 -->
      <div v-if="currentLanguage" class="language-detail-panel">
        <n-scrollbar class="detail-content">
          <!-- 基本信息卡片 -->
          <n-card class="section-card" :title="$t('languageConfig.sections.basic')">
            <n-form label-placement="top" size="medium">
              <n-form-item :label="$t('languageConfig.fields.name')">
                <n-input v-model:value="currentLanguage.name" :placeholder="$t('languageConfig.fields.name')" />
              </n-form-item>
              <n-form-item :label="$t('languageConfig.fields.code')">
                <n-input v-model:value="currentLanguage.code" :placeholder="$t('languageConfig.fields.code')" />
              </n-form-item>
            </n-form>
          </n-card>

          <!-- 字体配置卡片 -->
          <n-card class="section-card" :title="$t('languageConfig.sections.fonts')">
            <template #header-extra>
              <n-text depth="3" style="font-size: 12px;">
                {{ $t('languageConfig.fonts.hint') }}
              </n-text>
            </template>
            <div class="font-items-grid">
              <div v-for="item in fontItems" :key="item.key" class="font-item-card">
                <div class="font-item-header">
                  <n-icon :component="TextOutline" class="font-item-icon" />
                  <span class="font-item-label">{{ item.label }}</span>
                </div>
                <n-form label-placement="left" size="small" label-width="100px">
                  <n-form-item :label="$t('languageConfig.fonts.headers.name')">
                    <n-select
                      v-model:value="currentLanguage.fonts[item.key].name"
                      :options="fonts.map(font => ({ label: font, value: font }))"
                      size="small"
                      :consistent-menu-width="false"
                    />
                  </n-form-item>
                  <n-form-item :label="$t('languageConfig.fonts.headers.size')">
                    <n-input-number
                      v-model:value="currentLanguage.fonts[item.key].size_percent"
                      size="small"
                      :step="0.01"
                      :min="0.1"
                      :max="3"
                      :show-button="true"
                    />
                  </n-form-item>
                  <n-form-item :label="$t('languageConfig.fonts.headers.offset')">
                    <n-input-number
                      v-model:value="currentLanguage.fonts[item.key].vertical_offset"
                      size="small"
                      :step="1"
                      :min="-50"
                      :max="50"
                      :show-button="true"
                    />
                  </n-form-item>
                </n-form>
              </div>
            </div>
          </n-card>

          <!-- 文本配置卡片 -->
          <n-card class="section-card" :title="$t('languageConfig.sections.texts')">
            <template #header-extra>
              <n-text depth="3" style="font-size: 12px;">
                {{ $t('languageConfig.texts.hint') }}
              </n-text>
            </template>
            <div class="texts-grid">
              <div
                v-for="(value, key) in currentLanguage.texts"
                :key="key"
                class="text-item-card"
              >
                <div class="text-item-label">{{ key }}</div>
                <n-input
                  v-model:value="currentLanguage.texts[key]"
                  size="small"
                  :placeholder="key"
                />
              </div>
            </div>
          </n-card>

          <!-- 字体目录卡片 -->
          <n-card class="section-card" :title="$t('languageConfig.sections.fontFolder')">
            <template #header-extra>
              <n-button text @click="refreshFonts">
                <template #icon>
                  <n-icon :component="RefreshOutline" />
                </template>
                {{ $t('languageConfig.actions.refreshFonts') }}
              </n-button>
            </template>
            <div class="font-folder-hint">
              <n-icon :component="InformationCircleOutline" class="hint-icon" />
              <div class="hint-text">
                {{ $t('languageConfig.fontFolder.hint') }}
              </div>
            </div>
          </n-card>

          <!-- 保存按钮 -->
          <div class="save-actions">
            <n-button type="primary" size="large" @click="save" :loading="saving" block>
              <template #icon>
                <n-icon :component="SaveOutline" />
              </template>
              {{ saving ? $t('common.buttons.loading') : $t('languageConfig.actions.save') }}
            </n-button>
          </div>
        </n-scrollbar>
      </div>

      <!-- 未选择语言时的提示 -->
      <div v-else class="no-language-selected">
        <n-empty :description="$t('languageConfig.languageList.empty')">
          <template #icon>
            <n-icon :component="LanguageOutline" size="64" />
          </template>
          <template #extra>
            <n-text depth="3">{{ $t('languageConfig.languageList.empty') }}</n-text>
          </template>
        </n-empty>
      </div>
    </div>

    <!-- 新增语言对话框 -->
    <n-modal v-model:show="showAddDialog" preset="dialog" :title="$t('languageConfig.forms.newLanguage.title')" style="width: 500px;">
      <n-form label-placement="top" size="medium">
        <n-form-item :label="$t('languageConfig.forms.newLanguage.templateLabel')">
          <n-select
            v-model:value="selectedTemplateIndex"
            :options="templateOptions"
            size="medium"
            :placeholder="$t('languageConfig.forms.newLanguage.templateHint')"
          />
          <template #feedback>
            <n-text depth="3" style="font-size: 12px;">
              {{ $t('languageConfig.forms.newLanguage.templateHint') }}
            </n-text>
          </template>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showAddDialog = false">{{ $t('languageConfig.actions.cancel') }}</n-button>
          <n-button type="primary" @click="addLanguage">
            {{ $t('languageConfig.actions.addLanguage') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal v-model:show="showDeleteDialog" preset="dialog" :title="$t('languageConfig.deleteDialog.title')">
      <n-alert type="warning" :title="$t('languageConfig.deleteDialog.warning')">
        <template #icon>
          <n-icon :component="WarningOutline" />
        </template>
        {{ $t('languageConfig.deleteDialog.message', { name: languageToDelete?.name || languageToDelete?.code }) }}
      </n-alert>
      <template #action>
        <n-space>
          <n-button @click="showDeleteDialog = false">{{ $t('languageConfig.actions.cancel') }}</n-button>
          <n-button type="error" @click="deleteLanguage">
            {{ $t('languageConfig.actions.delete') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <n-spin size="large" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
  AddOutline,
  RefreshOutline,
  TrashOutline,
  LanguageOutline,
  TextOutline,
  SaveOutline,
  WarningOutline,
  InformationCircleOutline
} from '@vicons/ionicons5';
import { LanguageConfigService } from '@/api';
import type { LanguageConfigItem, LanguageFontsConfig } from '@/api/types';

const { t } = useI18n();
const message = useMessage();

const languages = ref<LanguageConfigItem[]>([]);
const fonts = ref<string[]>([]);

const loading = ref<boolean>(false);
const saving = ref<boolean>(false);
const activeIndex = ref<number>(0);

// 新增语言对话框
const showAddDialog = ref<boolean>(false);
const selectedTemplateIndex = ref<number | null>(null);

// 删除确认对话框
const showDeleteDialog = ref<boolean>(false);
const languageToDelete = ref<LanguageConfigItem | null>(null);
const deleteIndex = ref<number>(-1);

const fontItems = [
  { key: 'title', label: t('languageConfig.fonts.categories.title') },
  { key: 'subtitle', label: t('languageConfig.fonts.categories.subtitle') },
  { key: 'card_type', label: t('languageConfig.fonts.categories.card_type') },
  { key: 'trait', label: t('languageConfig.fonts.categories.trait') },
  { key: 'bold', label: t('languageConfig.fonts.categories.bold') },
  { key: 'body', label: t('languageConfig.fonts.categories.body') },
  { key: 'flavor', label: t('languageConfig.fonts.categories.flavor') },
  { key: 'collection_info', label: t('languageConfig.fonts.categories.collection_info') },
] as const;

const currentLanguage = computed(() => {
  if (!languages.value.length) return null;
  if (activeIndex.value < 0 || activeIndex.value >= languages.value.length) {
    activeIndex.value = 0;
  }
  const lang = languages.value[activeIndex.value];

  if (!lang.texts) {
    lang.texts = {};
  }
  return lang;
});

// 模板选项（用于新增语言时选择）
const templateOptions = computed(() => {
  const options = [
    {
      label: t('languageConfig.forms.newLanguage.templateNone'),
      value: null
    }
  ];

  languages.value.forEach((lang, index) => {
    options.push({
      label: `${lang.name || lang.code} (${lang.code})`,
      value: index
    });
  });

  return options;
});

const ensureFontsConfig = (fontsConfig: Partial<LanguageFontsConfig>): LanguageFontsConfig => {
  const makeFont = (cfg: any): { name: string; size_percent: number; vertical_offset: number } => ({
    name: cfg?.name ?? '',
    size_percent: typeof cfg?.size_percent === 'number' ? cfg.size_percent : 1.0,
    vertical_offset: typeof cfg?.vertical_offset === 'number' ? cfg.vertical_offset : 0,
  });

  return {
    title: makeFont(fontsConfig.title),
    subtitle: makeFont(fontsConfig.subtitle),
    card_type: makeFont(fontsConfig.card_type),
    trait: makeFont(fontsConfig.trait),
    bold: makeFont(fontsConfig.bold),
    body: makeFont(fontsConfig.body),
    flavor: makeFont(fontsConfig.flavor),
    collection_info: makeFont(fontsConfig.collection_info),
  };
};

const loadLanguageConfig = async () => {
  loading.value = true;
  try {
    const data = await LanguageConfigService.getLanguageConfig();
    fonts.value = data.fonts || [];

    const cfg = Array.isArray(data.config) ? data.config : [];
    languages.value = cfg.map((item) => ({
      name: item.name,
      code: item.code,
      fonts: ensureFontsConfig(item.fonts || {}),
      texts: { ...(item.texts || {}) },
    }));

    if (!languages.value.length) {
      activeIndex.value = -1;
    } else if (activeIndex.value < 0 || activeIndex.value >= languages.value.length) {
      activeIndex.value = 0;
    }
  } catch (error) {
    console.error(error);
    message.error(t('languageConfig.messages.loadFailed'));
  } finally {
    loading.value = false;
  }
};

const addLanguage = () => {
  let baseFonts: LanguageFontsConfig;
  let baseTexts: Record<string, string> = {};

  // 如果选择了模板语言，使用模板的字体配置和文本映射
  if (selectedTemplateIndex.value !== null && selectedTemplateIndex.value >= 0 && selectedTemplateIndex.value < languages.value.length) {
    const templateLang = languages.value[selectedTemplateIndex.value];
    baseFonts = ensureFontsConfig(templateLang.fonts);
    baseTexts = { ...(templateLang.texts || {}) };
  } else {
    // 否则使用默认配置，但如果有现有语言，也复制第一个语言的文本映射作为基础
    baseFonts = ensureFontsConfig({});
    if (languages.value.length > 0 && languages.value[0].texts) {
      baseTexts = { ...languages.value[0].texts };
    }
  }

  languages.value.push({
    name: t('languageConfig.defaults.newLanguageName'),
    code: 'new-lang',
    fonts: reactive(baseFonts),
    texts: baseTexts,
  });

  activeIndex.value = languages.value.length - 1;
  showAddDialog.value = false;
  selectedTemplateIndex.value = null;
};

const confirmDelete = (index: number) => {
  if (index < 0 || index >= languages.value.length) return;
  languageToDelete.value = languages.value[index];
  deleteIndex.value = index;
  showDeleteDialog.value = true;
};

const deleteLanguage = async () => {
  const index = deleteIndex.value;
  if (index < 0 || index >= languages.value.length) return;

  languages.value.splice(index, 1);

  if (!languages.value.length) {
    activeIndex.value = -1;
  } else if (activeIndex.value >= languages.value.length) {
    activeIndex.value = languages.value.length - 1;
  }

  showDeleteDialog.value = false;
  languageToDelete.value = null;
  deleteIndex.value = -1;

  // 删除后立即保存到后端
  try {
    const payload = languages.value.map((item) => ({
      name: item.name,
      code: item.code,
      fonts: ensureFontsConfig(item.fonts || {}),
      texts: item.texts || {},
    }));

    await LanguageConfigService.saveLanguageConfig(payload);
    message.success(t('languageConfig.messages.deleteSuccess'));
  } catch (error) {
    console.error(error);
    message.error(t('languageConfig.messages.deleteFailed'));
  }
};

const save = async () => {
  saving.value = true;
  try {
    const payload = languages.value.map((item) => ({
      name: item.name,
      code: item.code,
      fonts: ensureFontsConfig(item.fonts || {}),
      texts: item.texts || {},
    }));

    await LanguageConfigService.saveLanguageConfig(payload);
    message.success(t('languageConfig.messages.saveSuccess'));
  } catch (error) {
    console.error(error);
    message.error(t('languageConfig.messages.saveFailed'));
  } finally {
    saving.value = false;
  }
};

const refreshFonts = async () => {
  try {
    // 只刷新字体列表，不重新加载整个配置
    const data = await LanguageConfigService.getLanguageConfig();
    fonts.value = data.fonts || [];
    message.success(t('languageConfig.messages.refreshFontsSuccess'));
  } catch (error) {
    console.error(error);
    message.error(t('languageConfig.messages.refreshFontsFailed'));
  }
};

// 键盘快捷键处理
const handleKeydown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.code === 'KeyS') {
    event.preventDefault();
    if (!saving.value && languages.value.length > 0) {
      save();
    }
  }
};

onMounted(() => {
  loadLanguageConfig();
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.language-config-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  position: relative;
}

.language-config-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  height: 48px;
}

.language-config-header h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.1;
}

.header-actions .n-button {
  height: 32px;
}

.language-config-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.language-list-panel {
  width: 320px;
  background: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.panel-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.panel-header-actions {
  display: flex;
  gap: 0.5rem;
}

.language-list {
  flex: 1;
  min-height: 0;
  padding: 0.5rem;
}

.language-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.5rem;
  position: relative;
  border: 1px solid transparent;
}

.language-item:hover {
  background: #f8f9fa;
  border-color: #e9ecef;
}

.language-item.active {
  background: linear-gradient(135deg, #e3f2fd 0%, #e8f5e8 100%);
  border-left: 3px solid #667eea;
  border-color: #667eea;
}

.language-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.language-info {
  flex: 1;
  min-width: 0;
}

.language-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.language-code-badge {
  display: inline-block;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.7rem;
}

.language-item-actions {
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.language-item:hover .language-item-actions {
  opacity: 1;
}

.delete-button {
  transition: all 0.2s ease;
}

.language-detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: white;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.detail-content {
  flex: 1;
  min-height: 0;
  padding: 1.5rem;
}

.section-card {
  margin-bottom: 1.5rem;
}

.section-card:last-child {
  margin-bottom: 0;
}

.font-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.font-item-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e9ecef;
  transition: all 0.2s ease;
}

.font-item-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.font-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.font-item-icon {
  color: #667eea;
  font-size: 1.2rem;
}

.font-item-label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.texts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.text-item-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.text-item-label {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 500;
}

.font-folder-hint {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0f8ff;
  border-left: 3px solid #667eea;
  border-radius: 4px;
}

.hint-icon {
  color: #667eea;
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.hint-text {
  flex: 1;
  font-size: 0.875rem;
  color: #4a5568;
  line-height: 1.6;
}

.save-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.no-language-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

/* 动画效果 */
.language-item {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .language-list-panel {
    width: 280px;
  }

  .font-items-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .language-config-content {
    flex-direction: column;
  }

  .language-list-panel {
    width: 100%;
    max-height: 300px;
  }

  .language-list {
    padding: 0.25rem;
  }

  .language-item {
    padding: 0.75rem;
    margin-bottom: 0.25rem;
  }

  .language-icon {
    font-size: 1.25rem;
    margin-right: 0.75rem;
  }

  .font-items-grid,
  .texts-grid {
    grid-template-columns: 1fr;
  }
}

/* 滚动条样式 */
.n-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.n-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.n-scrollbar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.n-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

<template>
  <n-modal
    v-model:show="showLanguageModal"
    :mask-closable="false"
    :closable="false"
    :auto-focus="false"
    :block-scroll="true"
    transform-origin="center"
    preset="card"
    class="language-welcome-modal"
    :style="{ 
      maxWidth: '600px',
      width: '90vw',
      margin: '0 auto'
    }"
  >
    <template #default>
      <div class="language-welcome-content">
        <!-- 欢迎图标和标题 - 固定在顶部 -->
        <div class="welcome-header">
          <div class="welcome-icon">
            <n-icon size="64" :component="LanguageOutline" color="#667eea" />
          </div>
          <h2 class="welcome-title">{{ $t('languageWelcome.title') }}</h2>
          <p class="welcome-subtitle">{{ $t('languageWelcome.subtitle') }}</p>
        </div>

        <!-- 语言选择区域 - 可滚动 -->
        <div class="language-selection-area">
          <div class="language-grid">
            <div
              v-for="language in languageOptions"
              :key="language.key"
              class="language-option"
              :class="{ 'selected': selectedLanguage === language.key }"
              @click="selectLanguage(language.key)"
            >
              <div class="language-card">
                <div class="language-flag">
                  <n-icon size="32" :component="language.icon" />
                </div>
                <div class="language-info">
                  <h3 class="language-name">{{ language.label }}</h3>
                  <p class="language-native">{{ language.nativeName }}</p>
                </div>
                <div class="language-check" v-if="selectedLanguage === language.key">
                  <n-icon size="20" :component="CheckmarkCircle" color="#10b981" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 确认按钮 - 固定在底部 -->
        <div class="welcome-actions">
          <n-button
            type="primary"
            size="large"
            :disabled="!selectedLanguage"
            :loading="isConfirming"
            @click="confirmLanguage"
            class="confirm-btn"
          >
            <template #icon>
              <n-icon :component="CheckmarkCircle" />
            </template>
            {{ $t('languageWelcome.confirm') }}
          </n-button>
        </div>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  NModal,
  NCard,
  NButton,
  NIcon,
  useMessage
} from 'naive-ui';
import {
  LanguageOutline,
  CheckmarkCircle,
  GlobeOutline,
  LanguageSharp
} from '@vicons/ionicons5';
import { setLanguage } from '@/locales';

// Props 和 Emits
const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  'update:show': [value: boolean];
  'language-selected': [language: string];
}>();

// 国际化
const { t, locale } = useI18n();
const message = useMessage();

// 组件状态
const showLanguageModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
});

const selectedLanguage = ref<string>('');
const isConfirming = ref(false);

// 语言选项配置
const languageOptions = [
  {
    key: 'zh',
    label: '中文',
    nativeName: '简体中文',
    icon: LanguageSharp
  },
  {
    key: 'en',
    label: 'English',
    nativeName: 'English',
    icon: GlobeOutline
  }
];

// 选择语言
const selectLanguage = (languageKey: string) => {
  selectedLanguage.value = languageKey;
};

// 确认语言选择
const confirmLanguage = async () => {
  if (!selectedLanguage.value) return;

  isConfirming.value = true;

  try {
    // 应用语言选择
    setLanguage(selectedLanguage.value);

    // 发送语言选择事件
    emit('language-selected', selectedLanguage.value);

    // 关闭弹窗
    showLanguageModal.value = false;

    // 显示成功提示
    message.success(t('languageWelcome.success'));

  } catch (error) {
    console.error('语言切换失败:', error);
    message.error(t('languageWelcome.error'));
  } finally {
    isConfirming.value = false;
  }
};

// 监听弹窗显示状态，重置选择
watch(() => props.show, (newShow) => {
  if (newShow) {
    // 获取当前语言作为默认选择
    selectedLanguage.value = locale.value;
  }
});
</script>

<style scoped>
/* 移除 n-card 默认的 padding */
.language-welcome-modal :deep(.n-card) {
  padding: 0 !important;
  max-height: 85vh;
  overflow: hidden;
}

.language-welcome-modal :deep(.n-card__content) {
  padding: 0 !important;
  height: 100%;
  overflow: hidden;
}

.language-welcome-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 85vh;
  overflow: hidden;
}

/* 欢迎头部 - 固定在顶部 */
.welcome-header {
  text-align: center;
  padding: 24px 24px 16px 24px;
  flex-shrink: 0;
  background: white;
  border-bottom: 1px solid #f1f5f9;
}

.welcome-icon {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.welcome-subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* 语言选择区域 - 可滚动 */
.language-selection-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  min-height: 0;
  -webkit-overflow-scrolling: touch;
}

.language-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.language-option {
  cursor: pointer;
  transition: all 0.2s ease;
}

.language-option:hover .language-card {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.language-option.selected .language-card {
  border-color: #667eea;
  background: #f8fafc;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
}

.language-card {
  position: relative;
  padding: 24px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
}

.language-flag {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.language-info {
  flex: 1;
}

.language-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.language-native {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.language-check {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 50%;
  border: 2px solid #10b981;
}

/* 操作按钮区域 - 固定在底部 */
.welcome-actions {
  display: flex;
  justify-content: center;
  padding: 16px 24px 24px 24px;
  flex-shrink: 0;
  background: white;
  border-top: 1px solid #f1f5f9;
}

.confirm-btn {
  min-width: 200px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
}

/* 美化滚动条 */
.language-selection-area::-webkit-scrollbar {
  width: 6px;
}

.language-selection-area::-webkit-scrollbar-track {
  background: #f8fafc;
  border-radius: 3px;
}

.language-selection-area::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.language-selection-area::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* 响应式设计 - 手机端优化 */
@media (max-width: 640px) {
  .language-welcome-modal :deep(.n-card) {
    max-height: 90vh;
    border-radius: 16px 16px 0 0;
  }

  .language-welcome-content {
    max-height: 90vh;
  }

  .welcome-header {
    padding: 20px 16px 12px 16px;
  }

  .welcome-icon {
    margin-bottom: 12px;
  }

  .welcome-icon :deep(.n-icon) {
    font-size: 48px !important;
  }

  .welcome-title {
    font-size: 22px;
    margin-bottom: 8px;
  }

  .welcome-subtitle {
    font-size: 14px;
    padding: 0 8px;
  }

  .language-selection-area {
    padding: 16px;
  }

  .language-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .language-card {
    padding: 18px;
    gap: 10px;
  }

  .language-flag {
    width: 56px;
    height: 56px;
  }

  .language-flag :deep(.n-icon) {
    font-size: 28px !important;
  }

  .language-name {
    font-size: 17px;
  }

  .language-native {
    font-size: 13px;
  }

  .language-check {
    top: 10px;
    right: 10px;
    width: 28px;
    height: 28px;
  }

  .language-check :deep(.n-icon) {
    font-size: 16px !important;
  }

  .welcome-actions {
    padding: 12px 16px 20px 16px;
  }

  .confirm-btn {
    width: 100%;
    min-width: auto;
    height: 46px;
    font-size: 15px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 375px) {
  .welcome-header {
    padding: 16px 12px 10px 12px;
  }

  .welcome-title {
    font-size: 20px;
  }

  .welcome-subtitle {
    font-size: 13px;
  }

  .language-selection-area {
    padding: 12px;
  }

  .language-card {
    padding: 16px;
  }

  .language-flag {
    width: 48px;
    height: 48px;
  }

  .language-name {
    font-size: 16px;
  }

  .welcome-actions {
    padding: 12px 12px 16px 12px;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .language-welcome-modal :deep(.n-card) {
    max-height: 95vh;
  }

  .language-welcome-content {
    max-height: 95vh;
  }

  .welcome-header {
    padding: 12px 20px 8px 20px;
  }

  .welcome-icon {
    margin-bottom: 8px;
  }

  .welcome-icon :deep(.n-icon) {
    font-size: 40px !important;
  }

  .welcome-title {
    font-size: 20px;
    margin-bottom: 6px;
  }

  .welcome-subtitle {
    font-size: 13px;
  }

  .language-selection-area {
    padding: 12px 20px;
  }

  .language-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .language-card {
    padding: 12px;
    flex-direction: row;
    text-align: left;
  }

  .language-flag {
    width: 48px;
    height: 48px;
  }

  .welcome-actions {
    padding: 10px 20px 12px 20px;
  }

  .confirm-btn {
    height: 40px;
  }
}
</style>

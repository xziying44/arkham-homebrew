<template>
  <n-modal
    v-model:show="showLanguageModal"
    :mask-closable="false"
    :closable="false"
    :auto-focus="false"
    :block-scroll="true"
    :style="{ maxHeight: '90vh', overflow: 'hidden' }"
    transform-origin="center"
    class="language-welcome-modal"
  >
    <n-card
      class="language-welcome-card"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
    >
      <div class="language-welcome-content">
        <!-- 欢迎图标和标题 -->
        <div class="welcome-header">
          <div class="welcome-icon">
            <n-icon size="64" :component="LanguageOutline" color="#667eea" />
          </div>
          <h2 class="welcome-title">{{ $t('languageWelcome.title') }}</h2>
          <p class="welcome-subtitle">{{ $t('languageWelcome.subtitle') }}</p>
        </div>

        <!-- 语言选择网格 -->
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

        <!-- 确认按钮 -->
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
    </n-card>
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

  // 立即预览语言切换（可选）
  // setLanguage(languageKey);
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

    // 标记首次访问已完成
    localStorage.setItem('language-welcome-completed', 'true');

  } catch (error) {
    console.error('语言切换失败:', error);
    message.error(t('languageWelcome.error'));
  } finally {
    isConfirming.value = false;
  }
};

// 跳过语言选择
const skipLanguage = () => {
  showLanguageModal.value = false;
  localStorage.setItem('language-welcome-completed', 'true');
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
.language-welcome-modal {
  --n-border-radius: 16px;
}

.language-welcome-card {
  max-width: 600px;
  width: 90vw;
  max-height: 85vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.language-welcome-content {
  padding: 20px;
  overflow: visible;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 0;
}

/* 欢迎头部 */
.welcome-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 10px 0;
  flex-shrink: 0;
}

.welcome-icon {
  margin-bottom: 20px;
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

/* 语言选择网格 */
.language-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
  flex: 1;
  min-height: 0;
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

/* 操作按钮区域 */
.welcome-actions {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
  flex-shrink: 0;
}

.confirm-btn {
  min-width: 200px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
}

.welcome-skip {
  text-align: center;
  flex-shrink: 0;
}

.skip-btn {
  font-size: 14px;
  color: #64748b;
  text-decoration: underline;
  text-decoration-style: dotted;
}

.skip-btn:hover {
  color: #475569;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .language-welcome-card {
    width: 95vw;
    margin: 10px;
  }

  .language-welcome-content {
    padding: 16px;
  }

  .welcome-title {
    font-size: 24px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .language-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .language-card {
    padding: 20px;
  }

  .confirm-btn {
    width: 100%;
  }
}

/* 美化滚动条 */
.language-welcome-content::-webkit-scrollbar {
  width: 6px;
}

.language-welcome-content::-webkit-scrollbar-track {
  background: transparent;
}

.language-welcome-content::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.language-welcome-content::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
<template>
  <n-card :title="$t('cardEditor.tags.title')" size="small" class="form-card">
    <div class="tags-editor-container">
      <div class="tags-info">
        <n-alert type="info" style="margin-bottom: 1rem;">
          <template #icon>
            <n-icon :component="InformationCircleOutline" />
          </template>
          {{ $t('cardEditor.tags.description') }}
        </n-alert>
      </div>

      <n-form ref="tagsFormRef" :model="tagsForm" label-placement="left" label-width="100px">
        <n-form-item :label="$t('cardEditor.tags.permanent.label')">
          <n-switch v-model:value="tagsForm.permanent" @update:value="updateTags" />
          <template #feedback>
            <n-text depth="3" style="font-size: 0.875rem;">
              {{ $t('cardEditor.tags.permanent.description') }}
            </n-text>
          </template>
        </n-form-item>

        <n-form-item :label="$t('cardEditor.tags.exceptional.label')">
          <n-switch v-model:value="tagsForm.exceptional" @update:value="updateTags" />
          <template #feedback>
            <n-text depth="3" style="font-size: 0.875rem;">
              {{ $t('cardEditor.tags.exceptional.description') }}
            </n-text>
          </template>
        </n-form-item>

        <n-form-item :label="$t('cardEditor.tags.myriad.label')">
          <n-switch v-model:value="tagsForm.myriad" @update:value="updateTags" />
          <template #feedback>
            <n-text depth="3" style="font-size: 0.875rem;">
              {{ $t('cardEditor.tags.myriad.description') }}
            </n-text>
          </template>
        </n-form-item>

        <n-form-item :label="$t('cardEditor.tags.exile.label')">
          <n-switch v-model:value="tagsForm.exile" @update:value="updateTags" />
          <template #feedback>
            <n-text depth="3" style="font-size: 0.875rem;">
              {{ $t('cardEditor.tags.exile.description') }}
            </n-text>
          </template>
        </n-form-item>
      </n-form>

      <!-- 当前标签预览 -->
      <div class="current-tags-preview" v-if="hasAnyTags()">
        <h5>{{ $t('cardEditor.tags.preview') }}</h5>
        <n-space size="small">
          <n-tag v-if="tagsForm.permanent" type="info" size="small">
            {{ $t('cardEditor.tags.permanent.name') }}
          </n-tag>
          <n-tag v-if="tagsForm.exceptional" type="warning" size="small">
            {{ $t('cardEditor.tags.exceptional.name') }}
          </n-tag>
          <n-tag v-if="tagsForm.myriad" type="success" size="small">
            {{ $t('cardEditor.tags.myriad.name') }}
          </n-tag>
          <n-tag v-if="tagsForm.exile" type="error" size="small">
            {{ $t('cardEditor.tags.exile.name') }}
          </n-tag>
        </n-space>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { NCard, NForm, NFormItem, NSwitch, NAlert, NIcon, NText, NSpace, NTag } from 'naive-ui';
import { InformationCircleOutline } from '@vicons/ionicons5';
import { useI18n } from 'vue-i18n';

// Props定义
interface Props {
  cardData: any; // 当前卡牌数据
  side?: 'front' | 'back'; // 当前编辑的面
}

const props = withDefaults(defineProps<Props>(), {
  side: 'front'
});

// Emits定义
const emit = defineEmits<{
  'update-tags': (tags: CardTags) => void;
}>();

// 卡牌标签接口
interface CardTags {
  permanent: boolean;
  exceptional: boolean;
  myriad: boolean;
  exile: boolean;
}

const { t } = useI18n();

// 组件状态
const tagsFormRef = ref<any>(null);
const tagsForm = reactive<CardTags>({
  permanent: false,
  exceptional: false,
  myriad: false,
  exile: false
});

// 计算属性：获取当前卡牌面数据
const currentSideData = computed(() => {
  if (props.side === 'back' && props.cardData.back) {
    return props.cardData.back;
  }
  return props.cardData;
});

// 计算属性：检查是否有任何标签
const hasAnyTags = (): boolean => {
  return !!(tagsForm.permanent || tagsForm.exceptional ||
           tagsForm.myriad || tagsForm.exile);
};

// 初始化标签表单
const initializeTags = () => {
  const sideData = currentSideData.value;
  tagsForm.permanent = sideData.permanent || false;
  tagsForm.exceptional = sideData.exceptional || false;
  tagsForm.myriad = sideData.myriad || false;
  tagsForm.exile = sideData.exile || false;
};

// 更新标签
const updateTags = () => {
  const updatedTags: CardTags = {
    permanent: tagsForm.permanent,
    exceptional: tagsForm.exceptional,
    myriad: tagsForm.myriad,
    exile: tagsForm.exile
  };
  emit('update-tags', updatedTags);
};

// 监听卡牌数据变化
watch(() => props.cardData, () => {
  initializeTags();
}, { deep: true, immediate: true });

// 监听面切换
watch(() => props.side, () => {
  initializeTags();
}, { immediate: true });
</script>

<style scoped>
.tags-editor-container {
  padding: 8px 0;
}

.tags-info {
  margin-bottom: 16px;
}

.current-tags-preview {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--n-border-color);
}

.current-tags-preview h5 {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--n-text-color);
}

.form-card {
  margin-bottom: 16px;
}
</style>
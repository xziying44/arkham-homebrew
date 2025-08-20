<template>
  <div class="file-tree-pane" :style="{ width: width + 'px' }">
    <div class="pane-header">
      <n-space align="center" justify="space-between">
        <n-space align="center" size="small">
          <n-button size="tiny" quaternary @click="$emit('go-back')">
            <n-icon :component="ArrowBackOutline" />
          </n-button>
          <span class="pane-title">文件资源管理器</span>
        </n-space>
        <n-button size="tiny" quaternary @click="$emit('toggle')">
          <n-icon :component="Close" />
        </n-button>
      </n-space>
    </div>

    <div class="file-tree-content">
      <n-tree 
        :data="fileTreeData" 
        :render-label="renderTreeLabel" 
        :render-prefix="renderTreePrefix" 
        selectable
        expand-on-click 
        @update:selected-keys="handleFileSelect" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue';
import { NIcon } from 'naive-ui';
import type { TreeOption } from 'naive-ui';
import {
  FolderOpenOutline,
  DocumentOutline,
  ImageOutline,
  Close,
  ArrowBackOutline,
  LayersOutline,
  GridOutline,
  SettingsOutline,
  FolderOutline
} from '@vicons/ionicons5';

interface Props {
  width: number;
}

defineProps<Props>();

const emit = defineEmits<{
  'toggle': [];
  'go-back': [];
  'file-select': [keys: Array<string | number>];
}>();

// 文件树数据
const fileTreeData = ref<TreeOption[]>([
  {
    label: '目录',
    key: 'directories',
    type: 'directory',
    children: [
      {
        label: '调查员卡牌',
        key: 'investigators',
        type: 'folder',
        children: [
          { label: 'Roland-Banks.card', key: 'roland', type: 'card' },
          { label: 'Wendy-Adams.card', key: 'wendy', type: 'card' },
        ]
      },
      {
        label: '资产卡牌',
        key: 'assets',
        type: 'folder',
        children: [
          { label: 'Magnifying-Glass.card', key: 'magnifying', type: 'card' },
          { label: 'Flashlight.card', key: 'flashlight', type: 'card' },
        ]
      },
    ]
  },
  {
    label: '卡牌',
    key: 'cards',
    type: 'card-category',
    children: [
      { label: 'Roland-Banks.card', key: 'roland-card', type: 'card' },
      { label: 'Wendy-Adams.card', key: 'wendy-card', type: 'card' },
      { label: 'Duke.card', key: 'duke-card', type: 'card' },
      { label: 'Magnifying-Glass.card', key: 'magnifying-card', type: 'card' },
      { label: 'Flashlight.card', key: 'flashlight-card', type: 'card' },
    ]
  },
  {
    label: '图片',
    key: 'images',
    type: 'image-category',
    children: [
      { label: 'card-background.png', key: 'bg1', type: 'image' },
      { label: 'character-portrait.jpg', key: 'portrait1', type: 'image' },
      { label: 'icon-set.svg', key: 'icons', type: 'image' },
      { label: 'logo.png', key: 'logo', type: 'image' },
      { label: 'texture-pattern.jpg', key: 'texture', type: 'image' },
    ]
  },
  {
    label: '其他',
    key: 'others',
    type: 'other-category',
    children: [
      { label: 'config.json', key: 'config', type: 'config' },
      { label: 'styles.css', key: 'styles', type: 'style' },
      { label: 'data.xml', key: 'data', type: 'data' },
      { label: 'readme.txt', key: 'readme', type: 'text' },
    ]
  }
]);

const renderTreeLabel = ({ option }: { option: TreeOption }) => {
  return option.label as string;
};

const renderTreePrefix = ({ option }: { option: TreeOption }) => {
  const iconStyle = { marginRight: '6px' };

  const iconMap = {
    'directory': { component: FolderOutline, color: '#ffa726' },
    'card-category': { component: LayersOutline, color: '#42a5f5' },
    'image-category': { component: ImageOutline, color: '#66bb6a' },
    'other-category': { component: SettingsOutline, color: '#ab47bc' },
    'folder': { component: FolderOpenOutline, color: '#ffa726' },
    'card': { component: DocumentOutline, color: '#42a5f5' },
    'image': { component: ImageOutline, color: '#66bb6a' },
    'config': { component: GridOutline, color: '#ff7043' },
    'data': { component: GridOutline, color: '#ff7043' },
    'style': { component: SettingsOutline, color: '#ec407a' },
    'text': { component: DocumentOutline, color: '#8d6e63' },
    'default': { component: DocumentOutline, color: '#90a4ae' }
  };

  const iconConfig = iconMap[option.type as keyof typeof iconMap] || iconMap.default;
  
  return h(NIcon, {
    component: iconConfig.component,
    color: iconConfig.color,
    size: option.type?.includes('category') || option.type === 'directory' ? 16 : 14,
    style: iconStyle
  });
};

const handleFileSelect = (keys: Array<string | number>) => {
  emit('file-select', keys);
};
</script>

<style scoped>
.file-tree-pane {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: width var(--resize-transition);
  will-change: width;
}

.pane-header {
  flex-shrink: 0;
  padding: 12px 16px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.pane-title {
  font-weight: 600;
  font-size: 14px;
  color: white;
}

.file-tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
}

.file-tree-content::-webkit-scrollbar {
  width: 8px;
}

.file-tree-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.file-tree-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.file-tree-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #5a67d8 0%, #6b46c1 100%);
}
</style>

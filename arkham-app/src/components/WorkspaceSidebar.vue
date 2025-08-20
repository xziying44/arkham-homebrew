<template>
  <div class="workspace-sidebar" :class="{ 'collapsed': collapsed }">
    <div class="sidebar-header">
      <div class="logo" v-if="!collapsed">工作区</div>
      <button class="collapse-btn" @click="toggleCollapse">
        <svg :style="{ transform: collapsed ? 'rotate(0deg)' : 'rotate(180deg)' }" 
             width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
      </button>
    </div>

    <nav class="sidebar-nav">
      <div 
        v-for="item in navItems" 
        :key="item.key"
        class="nav-item" 
        :class="{ 'active': activeItem === item.key }"
        @click="selectItem(item.key)"
      >
        <div class="nav-icon" v-html="item.icon"></div>
        <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
      </div>
    </nav>

    <div class="sidebar-footer" v-if="!collapsed">
      <button class="back-btn" @click="goBack">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
        返回首页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  activeItem: string;
}>();

const emit = defineEmits<{
  'item-select': [key: string];
  'go-back': [];
}>();

const collapsed = ref(true);

const navItems = [
  {
    key: 'workspace',
    label: '工作区',
    icon: '🏠'
  },
  {
    key: 'deck-builder',
    label: '牌库制作',
    icon: '🃏'
  },
  {
    key: 'tts-items',
    label: 'TTS物品',
    icon: '📦'
  },
  {
    key: 'settings',
    label: '其他设置',
    icon: '⚙️'
  }
];

const toggleCollapse = () => {
  collapsed.value = !collapsed.value;
};

const selectItem = (key: string) => {
  emit('item-select', key);
};

const goBack = () => {
  emit('go-back');
};
</script>

<style scoped>
/* 样式保持不变 */
.workspace-sidebar {
  width: 220px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.workspace-sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 1.1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
}

.collapse-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.collapse-btn svg {
  transition: transform 0.3s ease;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: inset 3px 0 0 #ffffff;
}

.nav-icon {
  font-size: 1.25rem;
  width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
}

.collapsed .nav-icon {
  margin-right: 0;
}

.nav-label {
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.collapsed .nav-label {
  opacity: 0;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.back-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .workspace-sidebar {
    width: 60px;
  }
  
  .workspace-sidebar .nav-label,
  .workspace-sidebar .logo,
  .workspace-sidebar .sidebar-footer {
    display: none;
  }
}
</style>

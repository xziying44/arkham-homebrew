<template>
  <!-- 桌面端侧边栏 -->
  <div v-if="!isMobile" class="workspace-sidebar" :class="{ 'collapsed': collapsed }">
    <div class="sidebar-header">
      <div class="logo" v-if="!collapsed">{{ t('workspace.sidebar.title') }}</div>
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
        {{ t('workspace.sidebar.backToHome') }}
      </button>
    </div>
  </div>

  <!-- 手机端底部导航 -->
  <div v-else class="mobile-bottom-nav">
    <button
      class="mobile-nav-btn"
      :class="{ 'active': activeItem === 'workspace' }"
      @click="selectItem('workspace')"
    >
      <div class="mobile-nav-icon">🏠</div>
      <span class="mobile-nav-label">{{ t('workspace.sidebar.navItems.workspace') }}</span>
    </button>
    <button
      class="mobile-nav-btn"
      :class="{ 'active': activeItem === 'settings' }"
      @click="selectItem('settings')"
    >
      <div class="mobile-nav-icon">⚙️</div>
      <span class="mobile-nav-label">{{ t('workspace.sidebar.navItems.settings') }}</span>
    </button>
    <button
      class="mobile-nav-btn"
      :class="{ 'active': activeItem === 'about' }"
      @click="selectItem('about')"
    >
      <div class="mobile-nav-icon">ℹ️</div>
      <span class="mobile-nav-label">{{ t('workspace.sidebar.navItems.about') }}</span>
    </button>
    <button
      class="mobile-nav-btn mobile-back-btn"
      @click="goBack"
    >
      <div class="mobile-nav-icon">🏠</div>
      <span class="mobile-nav-label">{{ t('workspace.sidebar.backToHome') }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  activeItem: string;
}>();

const emit = defineEmits<{
  'item-select': [key: string];
  'go-back': [];
}>();

const { t } = useI18n();
const collapsed = ref(true);

// 手机端检测
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value <= 768);

// 窗口大小监听
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

const navItems = computed(() => [
  {
    key: 'workspace',
    label: t('workspace.sidebar.navItems.workspace'),
    icon: '🏠'
  },
  {
    key: 'deck-builder',
    label: t('workspace.sidebar.navItems.deckBuilder'),
    icon: '🃏'
  },
  {
    key: 'content-package',
    label: t('workspace.sidebar.navItems.contentPackage'),
    icon: '📦'
  },
  {
    key: 'settings',
    label: t('workspace.sidebar.navItems.settings'),
    icon: '⚙️'
  },
  {
    key: 'about',
    label: t('workspace.sidebar.navItems.about'),
    icon: 'ℹ️'
  }
]);

const toggleCollapse = () => {
  collapsed.value = !collapsed.value;
};

const selectItem = (key: string) => {
  emit('item-select', key);
};

const goBack = () => {
  emit('go-back');
};

// 生命周期钩子
onMounted(() => {
  window.addEventListener('resize', handleResize, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* 样式保持不变，这里省略... */
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

/* ============================================= */
/* 手机端底部导航 */
/* ============================================= */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 10px;
  z-index: 1000;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.mobile-nav-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  flex: 1;
  min-width: 0;
}

.mobile-nav-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.mobile-nav-btn.active {
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
}

.mobile-nav-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-nav-label {
  font-size: 11px;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.mobile-back-btn {
  color: #ef4444;
}

.mobile-back-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.mobile-back-btn.active {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}
</style>

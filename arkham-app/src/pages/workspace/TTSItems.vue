<template>
  <div class="tts-items-container">
    <div class="tts-content">
      <h2>{{ $t('ttsItems.title') }}</h2>
      
      <!-- 开发中提示 -->
      <div class="dev-notice">
        <div class="dev-icon">🚧</div>
        <div class="dev-text">
          <strong>{{ $t('ttsItems.devNotice.title') }}</strong>
          <span>{{ $t('ttsItems.devNotice.description') }}</span>
        </div>
      </div>

      <div class="items-grid">
        <div class="item-card" v-for="item in items" :key="item.id">
          <div class="item-icon">📦</div>
          <div class="item-info">
            <h3>{{ $t(`ttsItems.items.${item.type}.name`) }}</h3>
            <p>{{ $t(`ttsItems.items.${item.type}.description`) }}</p>
          </div>
        </div>
        <div class="item-card add-new" @click="addNewItem">
          <div class="add-icon">➕</div>
          <div class="add-text">{{ $t('ttsItems.actions.addNewItem') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface TTSItem {
  id: string;
  name: string;
  description: string;
  type: string;
}

const items = ref<TTSItem[]>([
  { id: '1', name: 'dice', description: 'dice_desc', type: 'dice' },
  { id: '2', name: 'board', description: 'board_desc', type: 'board' },
  { id: '3', name: 'counter', description: 'counter_desc', type: 'counter' }
]);

const addNewItem = () => {
  console.log('添加新物品');
  // 这里可以打开添加物品的对话框或导航到详细页面
};
</script>

<style scoped>
.tts-items-container {
  padding: 2rem;
  height: 100%;
  overflow-y: auto;
}

.tts-content h2 {
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

/* 开发中提示样式 */
.dev-notice {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.15);
}

.dev-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.dev-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dev-text strong {
  color: #856404;
  font-size: 0.95rem;
}

.dev-text span {
  color: #856404;
  font-size: 0.85rem;
  opacity: 0.8;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.item-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
}

.item-card.add-new {
  border: 2px dashed #bdc3c7;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 120px;
}

.item-card.add-new:hover {
  border-color: #3498db;
  background-color: #f8f9fa;
}

.item-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.add-icon {
  font-size: 3rem;
  color: #3498db;
  margin-bottom: 0.5rem;
}

.add-text {
  color: #7f8c8d;
  font-weight: 500;
}

.item-info h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.item-info p {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}
</style>

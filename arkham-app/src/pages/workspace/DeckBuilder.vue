<template>
  <div class="deck-builder-container">
    <div class="deck-builder-header">
      <h2>🃏 牌库制作</h2>
      <div class="header-actions">
        <button class="btn-secondary" @click="importDeck">导入牌库</button>
        <button class="btn-primary" @click="createNewDeck">新建牌库</button>
      </div>
    </div>

    <div class="deck-builder-content">
      <!-- 左侧牌库列表 -->
      <div class="deck-list-panel">
        <div class="panel-header">
          <h3>我的牌库</h3>
          <button class="icon-btn" @click="refreshDecks">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
          </button>
        </div>
        <div class="deck-list">
          <div 
            v-for="deck in decks" 
            :key="deck.id"
            class="deck-item"
            :class="{ 'active': selectedDeck?.id === deck.id }"
            @click="selectDeck(deck)"
          >
            <div class="deck-icon">🎴</div>
            <div class="deck-info">
              <div class="deck-name">{{ deck.name }}</div>
              <div class="deck-meta">{{ deck.cardCount }} 张卡牌</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间卡牌编辑区 -->
      <div class="card-editor-panel" v-if="selectedDeck">
        <div class="panel-header">
          <h3>{{ selectedDeck.name }}</h3>
          <div class="editor-actions">
            <button class="icon-btn" @click="addCard">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
            </button>
            <button class="icon-btn" @click="saveDeck">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="cards-grid">
          <div 
            v-for="card in selectedDeck.cards" 
            :key="card.id"
            class="card-item"
            @click="editCard(card)"
          >
            <div class="card-preview">
              <img v-if="card.image" :src="card.image" :alt="card.name" />
              <div v-else class="card-placeholder">🖼️</div>
            </div>
            <div class="card-details">
              <div class="card-name">{{ card.name }}</div>
              <div class="card-type">{{ card.type }}</div>
            </div>
          </div>
          <div class="card-item add-card" @click="addCard">
            <div class="add-card-content">
              <div class="add-icon">➕</div>
              <div class="add-text">添加卡牌</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧卡牌属性面板 -->
      <div class="card-properties-panel" v-if="editingCard">
        <div class="panel-header">
          <h3>卡牌属性</h3>
          <button class="icon-btn" @click="closeCardEditor">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        
        <div class="properties-form">
          <div class="form-group">
            <label>卡牌名称</label>
            <input v-model="editingCard.name" type="text" />
          </div>
          <div class="form-group">
            <label>卡牌类型</label>
            <select v-model="editingCard.type">
              <option value="creature">生物</option>
              <option value="spell">法术</option>
              <option value="artifact">神器</option>
              <option value="land">地牌</option>
            </select>
          </div>
          <div class="form-group">
            <label>费用</label>
            <input v-model.number="editingCard.cost" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>攻击力</label>
            <input v-model.number="editingCard.attack" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>生命值</label>
            <input v-model.number="editingCard.health" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="editingCard.description" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>卡牌图片</label>
            <input type="file" @change="handleImageUpload" accept="image/*" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Card {
  id: string;
  name: string;
  type: string;
  cost: number;
  attack: number;
  health: number;
  description: string;
  image?: string;
}

interface Deck {
  id: string;
  name: string;
  cardCount: number;
  cards: Card[];
}

const decks = ref<Deck[]>([
  {
    id: '1',
    name: '火焰牌库',
    cardCount: 12,
    cards: [
      { id: '1', name: '火球术', type: 'spell', cost: 3, attack: 0, health: 0, description: '对目标造成6点伤害' },
      { id: '2', name: '烈焰元素', type: 'creature', cost: 4, attack: 5, health: 3, description: '一个强大的火焰生物' }
    ]
  },
  {
    id: '2',
    name: '水系牌库',
    cardCount: 8,
    cards: [
      { id: '3', name: '冰冻术', type: 'spell', cost: 2, attack: 0, health: 0, description: '冻结目标一回合' }
    ]
  }
]);

const selectedDeck = ref<Deck | null>(decks.value[0]);
const editingCard = ref<Card | null>(null);

const selectDeck = (deck: Deck) => {
  selectedDeck.value = deck;
  editingCard.value = null;
};

const editCard = (card: Card) => {
  editingCard.value = { ...card };
};

const closeCardEditor = () => {
  editingCard.value = null;
};

const addCard = () => {
  if (!selectedDeck.value) return;
  
  const newCard: Card = {
    id: Date.now().toString(),
    name: '新卡牌',
    type: 'creature',
    cost: 1,
    attack: 1,
    health: 1,
    description: ''
  };
  
  selectedDeck.value.cards.push(newCard);
  selectedDeck.value.cardCount = selectedDeck.value.cards.length;
  editingCard.value = newCard;
};

const createNewDeck = () => {
  const newDeck: Deck = {
    id: Date.now().toString(),
    name: '新牌库',
    cardCount: 0,
    cards: []
  };
  decks.value.push(newDeck);
  selectedDeck.value = newDeck;
};

const importDeck = () => {
  console.log('导入牌库');
};

const refreshDecks = () => {
  console.log('刷新牌库列表');
};

const saveDeck = () => {
  console.log('保存牌库', selectedDeck.value);
};

const handleImageUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file && editingCard.value) {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (editingCard.value) {
        editingCard.value.image = e.target?.result as string;
      }
    };
    reader.readAsDataURL(file);
  }
};
</script>

<style scoped>
.deck-builder-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.deck-builder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.deck-builder-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.deck-builder-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.deck-list-panel {
  width: 280px;
  background: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
}

.card-editor-panel {
  flex: 1;
  background: white;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-properties-panel {
  width: 320px;
  background: white;
  border-left: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
}

.panel-header {
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

.editor-actions {
  display: flex;
  gap: 0.5rem;
}

.deck-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.deck-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.25rem;
}

.deck-item:hover {
  background: #f8f9fa;
}

.deck-item.active {
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.deck-icon {
  font-size: 1.25rem;
  margin-right: 0.75rem;
}

.deck-info {
  flex: 1;
}

.deck-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.deck-meta {
  font-size: 0.8rem;
  color: #6c757d;
}

.cards-grid {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.card-item {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 280px;
}

.card-item:hover {
  border-color: #2196f3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-item.add-card {
  border: 2px dashed #bdc3c7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-item.add-card:hover {
  border-color: #2196f3;
  background: #f8f9fa;
}

.add-card-content {
  text-align: center;
}

.add-icon {
  font-size: 2rem;
  color: #2196f3;
  margin-bottom: 0.5rem;
}

.add-text {
  color: #6c757d;
  font-weight: 500;
}

.card-preview {
  height: 180px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-placeholder {
  font-size: 3rem;
  color: #bdc3c7;
}

.card-details {
  padding: 1rem;
}

.card-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.card-type {
  font-size: 0.85rem;
  color: #6c757d;
  text-transform: capitalize;
}

.properties-form {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #2196f3;
  outline: none;
}

.btn-primary {
  background: #2196f3;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover {
  background: #5a6268;
}

.icon-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #f8f9fa;
  color: #2196f3;
}
</style>

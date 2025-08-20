<template>
  <div class="settings-container">
    <div class="settings-content">
      <h2>工作区设置</h2>
      
      <div class="settings-sections">
        <div class="settings-section">
          <h3>📁 项目设置</h3>
          <div class="setting-item">
            <label>项目名称</label>
            <input v-model="projectSettings.name" type="text" />
          </div>
          <div class="setting-item">
            <label>项目路径</label>
            <input v-model="projectSettings.path" type="text" readonly />
            <button @click="selectProjectPath">选择路径</button>
          </div>
        </div>

        <div class="settings-section">
          <h3>🎨 界面设置</h3>
          <div class="setting-item">
            <label>主题</label>
            <select v-model="uiSettings.theme">
              <option value="light">浅色主题</option>
              <option value="dark">深色主题</option>
              <option value="auto">自动</option>
            </select>
          </div>
          <div class="setting-item">
            <label>语言</label>
            <select v-model="uiSettings.language">
              <option value="zh">中文</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div class="settings-section">
          <h3>⚙️ 编辑器设置</h3>
          <div class="setting-item">
            <label>自动保存</label>
            <input v-model="editorSettings.autoSave" type="checkbox" />
          </div>
          <div class="setting-item">
            <label>保存间隔 (秒)</label>
            <input v-model.number="editorSettings.saveInterval" type="number" min="1" max="300" />
          </div>
          <div class="setting-item">
            <label>代码格式化</label>
            <input v-model="editorSettings.autoFormat" type="checkbox" />
          </div>
        </div>

        <div class="settings-section">
          <h3>🔧 高级设置</h3>
          <div class="setting-item">
            <label>调试模式</label>
            <input v-model="advancedSettings.debugMode" type="checkbox" />
          </div>
          <div class="setting-item">
            <label>最大历史记录数</label>
            <input v-model.number="advancedSettings.maxHistory" type="number" min="10" max="1000" />
          </div>
        </div>
      </div>

      <div class="settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置为默认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const projectSettings = reactive({
  name: '我的工作区',
  path: '/path/to/workspace'
});

const uiSettings = reactive({
  theme: 'light',
  language: 'zh'
});

const editorSettings = reactive({
  autoSave: true,
  saveInterval: 30,
  autoFormat: true
});

const advancedSettings = reactive({
  debugMode: false,
  maxHistory: 100
});

const selectProjectPath = () => {
  // 这里可以调用文件选择对话框
  console.log('选择项目路径');
};

const saveSettings = () => {
  // 保存设置到本地存储或发送到服务器
  console.log('保存设置', {
    project: projectSettings,
    ui: uiSettings,
    editor: editorSettings,
    advanced: advancedSettings
  });
};

const resetSettings = () => {
  // 重置所有设置为默认值
  Object.assign(projectSettings, {
    name: '我的工作区',
    path: '/path/to/workspace'
  });
  Object.assign(uiSettings, {
    theme: 'light',
    language: 'zh'
  });
  Object.assign(editorSettings, {
    autoSave: true,
    saveInterval: 30,
    autoFormat: true
  });
  Object.assign(advancedSettings, {
    debugMode: false,
    maxHistory: 100
  });
};
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  height: 100%;
  overflow-y: auto;
}

.settings-content h2 {
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.settings-sections {
  display: grid;
  gap: 2rem;
}

.settings-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.settings-section h3 {
  color: #34495e;
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  min-width: 120px;
  color: #2c3e50;
  font-weight: 500;
}

.setting-item input[type="text"],
.setting-item input[type="number"],
.setting-item select {
  flex: 1;
  padding: 0.5rem;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  font-size: 0.9rem;
}

.setting-item input[type="text"]:focus,
.setting-item input[type="number"]:focus,
.setting-item select:focus {
  border-color: #3498db;
  outline: none;
}

.setting-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

.setting-item button {
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.setting-item button:hover {
  background: #2980b9;
}

.settings-actions {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary:hover {
  background: #219a52;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover {
  background: #7f8c8d;
}
</style>

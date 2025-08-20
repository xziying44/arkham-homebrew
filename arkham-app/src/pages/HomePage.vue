<template>
  <div class="welcome-container">
    <!-- 隐藏的文件选择元素 -->
    <input
      ref="fileInput"
      type="file"
      accept=".card,.json"
      style="display: none"
      @change="handleFileSelected"
    >
    <input
      ref="folderInput"
      type="file"
      webkitdirectory
      style="display: none"
      @change="handleFolderSelected"
    >

    <!-- ============================================= -->
    <!-- 左侧操作窗格 (Left Pane) -->
    <!-- ============================================= -->
    <div class="left-pane">
      <div class="left-content">
        <!-- Logo 和标题 -->
        <div class="logo-area">
          <n-icon size="40" :component="ColorWand" />
          <n-gradient-text type="primary" :size="28">
            阿卡姆印牌姬
          </n-gradient-text>
        </div>

        <!-- 操作按钮列表 -->
        <div class="actions-list">
          <div
            v-for="action in actions"
            :key="action.key"
            class="action-item"
            @click="action.handler"
          >
            <n-icon size="22" :component="action.icon" />
            <span>{{ action.label }}</span>
          </div>
        </div>
      </div>

      <!-- 左侧底部的设置区域 -->
      <div class="left-footer">
        <n-space align="center" justify="space-between">
          <span>{{ isDark ? '暗色模式' : '亮色模式' }}</span>
          <n-switch :value="isDark" @update:value="toggleTheme">
            <template #checked-icon>
              <n-icon :component="Moon" />
            </template>
            <template #unchecked-icon>
              <n-icon :component="Sunny" />
            </template>
          </n-switch>
        </n-space>
      </div>
    </div>

    <!-- ============================================= -->
    <!-- 右侧内容窗格 (Right Pane) -->
    <!-- ============================================= -->
    <div class="right-pane">
      <div class="content-wrapper">
        <header class="content-header">
          <h2>最近项目</h2>
          <p class="subtitle">选择一个项目继续，或从左侧开始新的创作</p>
        </header>

        <!-- 最近项目列表容器 -->
        <div class="recent-list-container">
          <n-list v-if="recentItems.length > 0" hoverable clickable>
            <n-list-item v-for="item in recentItems" :key="item.id" @click="handleOpenRecent(item)">
              <n-thing>
                <template #header>{{ item.name }}</template>
                <template #description>
                  <span class="recent-item-path">{{ item.path }}</span>
                </template>
                <template #header-extra>
                  <n-icon class="hover-arrow" :component="ArrowForwardOutline" />
                </template>
              </n-thing>
            </n-list-item>
          </n-list>

          <!-- 空状态 -->
          <n-empty
            v-else
            description="还没有最近项目"
            size="huge"
            class="empty-state"
          >
            <template #icon>
              <n-icon :component="CubeOutline" />
            </template>
          </n-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  AddCircleOutline,
  FileTrayFullOutline,
  FolderOpenOutline,
  ArrowForwardOutline,
  ColorWand,
  Moon,
  Sunny,
  CubeOutline
} from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';

// ----------- Props 和 Emits -----------
defineProps<{
  isDark: boolean;
}>();

const emit = defineEmits<{
  'toggle-theme': [];
  'navigate-to-workspace': [params: {
    mode: 'file' | 'folder';
    projectPath: string;
    projectName: string;
  }];
}>();

const toggleTheme = () => {
  emit('toggle-theme');
};

// ----------- 文件选择相关 -----------
const fileInput = ref<HTMLInputElement>();
const folderInput = ref<HTMLInputElement>();
const message = useMessage();

// ----------- 数据和状态 -----------
interface RecentItem {
  id: number;
  name: string;
  path: string;
}

// 阿卡姆印牌姬相关的最近项目
const recentItems = ref<RecentItem[]>([
  { id: 1, name: '调查员卡牌组-罗兰', path: 'D:/ArkhamCards/Investigators/Roland.card' },
  { id: 2, name: '恐怖遭遇卡组-古神', path: 'C:/Projects/ArkhamHorror/Ancient-Ones.card' },
  { id: 3, name: '资产卡牌设计稿', path: '~/Documents/Asset-Cards-Draft.card' },
  { id: 4, name: '技能卡牌模板', path: 'D:/Templates/Skill-Cards.card' },
  { id: 5, name: '场景卡组-敦威治', path: 'D:/Scenarios/Dunwich-Horror.card' },
  { id: 6, name: '自制调查员-艾米丽', path: 'C:/Custom/Investigators/Emily.card' },
  { id: 7, name: '事件卡牌合集', path: '~/Documents/Event-Cards-Collection.card' },
  { id: 8, name: '神话卡组-印斯茅斯', path: 'D:/Mythos/Innsmouth.card' },
  { id: 9, name: '弱点卡牌库', path: 'D:/Cards/Weaknesses/Library.card' },
]);

// ----------- 模拟后端API调用 -----------

/**
 * 模拟发送文件路径到后端
 */
const sendFilePathToBackend = async (filePath: string) => {
  console.log('🚀 [前端->后端] 发送文件路径:', filePath);
  
  // 模拟API调用
  try {
    // 这里在真实的桌面应用中会调用 Electron 的 ipcRenderer 或 Tauri 的 invoke
    // 例如：await window.electronAPI.openFile(filePath)
    // 或者：await invoke('open_file', { path: filePath })
    
    const response = await mockBackendCall('open_file', { path: filePath });
    console.log('✅ [后端->前端] 响应:', response);
    return response;
  } catch (error) {
    console.error('❌ [后端->前端] 错误:', error);
    throw error;
  }
};

/**
 * 模拟发送文件夹路径到后端
 */
const sendFolderPathToBackend = async (folderPath: string) => {
  console.log('🚀 [前端->后端] 发送文件夹路径:', folderPath);
  
  try {
    // 同样，这里在真实应用中会调用桌面应用的API
    // 例如：await window.electronAPI.openFolder(folderPath)
    // 或者：await invoke('open_folder', { path: folderPath })
    
    const response = await mockBackendCall('open_folder', { path: folderPath });
    console.log('✅ [后端->前端] 响应:', response);
    return response;
  } catch (error) {
    console.error('❌ [后端->前端] 错误:', error);
    throw error;
  }
};

/**
 * 模拟后端API调用
 */
const mockBackendCall = (action: string, params: any): Promise<any> => {
  return new Promise((resolve) => {
    // 模拟网络延迟
    setTimeout(() => {
      resolve({
        success: true,
        action,
        params,
        timestamp: new Date().toISOString(),
        message: `${action} executed successfully`
      });
    }, 500);
  });
};

// ----------- 事件处理函数 -----------

/**
 * 新建卡牌
 */
const handleNewCard = async () => {
  console.log('🎴 [阿卡姆印牌姬] 用户点击：新建卡牌');
  message.success('正在创建新的卡牌...');
  
  try {
    // 模拟调用后端创建新卡牌
    const response = await mockBackendCall('create_new_card', {});
    console.log('✅ 新建卡牌成功:', response);
    message.destroyAll();
    message.success('新卡牌已创建！');
    
    // 跳转到工作区页面
    emit('navigate-to-workspace', {
      mode: 'file',
      projectPath: 'new-card.card',
      projectName: '新建卡牌'
    });
    
  } catch (error) {
    message.destroyAll();
    message.error('创建失败！');
  }
};

/**
 * 打开卡牌文件
 */
const handleOpenFile = () => {
  console.log('📂 [阿卡姆印牌姬] 用户点击：打开文件');
  message.info('请选择一个卡牌文件...');
  
  // 触发隐藏的文件选择框
  if (fileInput.value) {
    fileInput.value.click();
  }
};

/**
 * 打开文件夹
 */
const handleOpenFolder = () => {
  console.log('📁 [阿卡姆印牌姬] 用户点击：打开文件夹');
  message.info('请选择一个文件夹...');
  
  // 触发隐藏的文件夹选择框
  if (folderInput.value) {
    folderInput.value.click();
  }
};

/**
 * 处理文件选择
 */
const handleFileSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  
  if (files && files.length > 0) {
    const file = files[0];
    const fileName = file.name;
    
    // 在浏览器环境中，我们只能获取文件名
    // 在真实的桌面应用中，可以获取完整的文件路径
    console.log('📄 [文件选择] 已选择文件:', fileName);
    
    message.loading(`正在打开文件: ${fileName}...`);
    
    try {
      // 发送文件路径到后端处理
      // 注意：在真实应用中，这里应该是完整路径，如 'C:/Users/User/Desktop/file.card'
      await sendFilePathToBackend(fileName);
      
      message.destroyAll();
      message.success(`文件 "${fileName}" 已成功打开！`);
      
      // 跳转到工作区页面 - 文件模式
      emit('navigate-to-workspace', {
        mode: 'file',
        projectPath: fileName,
        projectName: fileName.replace(/\.[^/.]+$/, '') // 去掉扩展名
      });
      
    } catch (error) {
      message.destroyAll();
      message.error(`打开文件失败: ${fileName}`);
    }
  }
  
  // 重置 input，允许重复选择同一文件
  target.value = '';
};

/**
 * 处理文件夹选择
 */
const handleFolderSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  
  if (files && files.length > 0) {
    // 从第一个文件的路径中提取文件夹路径
    const firstFile = files[0];
    const relativePath = firstFile.webkitRelativePath;
    const folderName = relativePath.split('/')[0]; // 获取根文件夹名
    
    console.log('📁 [文件夹选择] 已选择文件夹:', folderName);
    console.log('📁 [文件夹选择] 文件夹内包含文件数量:', files.length);
    
    message.loading(`正在打开文件夹: ${folderName}...`);
    
    try {
      // 发送文件夹路径到后端处理
      // 注意：在真实应用中，这里应该是完整路径，如 'C:/Users/User/Desktop/ProjectFolder'
      await sendFolderPathToBackend(folderName);
      
      message.destroyAll();
      message.success(`文件夹 "${folderName}" 已成功打开！包含 ${files.length} 个文件`);
      
      // 跳转到工作区页面 - 文件夹模式
      emit('navigate-to-workspace', {
        mode: 'folder',
        projectPath: folderName,
        projectName: folderName
      });
      
    } catch (error) {
      message.destroyAll();
      message.error(`打开文件夹失败: ${folderName}`);
    }
  }
  
  // 重置 input
  target.value = '';
};

/**
 * 打开最近项目
 */
const handleOpenRecent = async (item: RecentItem) => {
  console.log('🔄 [阿卡姆印牌姬] 用户点击最近项目:', item.name);
  console.log('🔄 [最近项目] 文件路径:', item.path);
  
  message.loading(`正在打开: ${item.name}...`);
  
  try {
    // 发送最近项目的完整路径到后端
    await sendFilePathToBackend(item.path);
    
    message.destroyAll();
    message.success(`已打开: ${item.name}`);
    
    // 跳转到工作区页面 - 根据文件扩展名判断模式
    const isFolder = !item.path.includes('.');
    emit('navigate-to-workspace', {
      mode: isFolder ? 'folder' : 'file',
      projectPath: item.path,
      projectName: item.name
    });
    
  } catch (error) {
    message.destroyAll();
    message.error(`打开失败: ${item.name}`);
  }
};

// 操作按钮配置
const actions = ref([
  { key: 'new', label: '新建卡牌', icon: AddCircleOutline, handler: handleNewCard },
  { key: 'open', label: '打开文件', icon: FileTrayFullOutline, handler: handleOpenFile },
  { key: 'folder', label: '打开文件夹', icon: FolderOpenOutline, handler: handleOpenFolder },
]);

</script>

<style scoped>
/* =========== 顶级容器 =========== */
.welcome-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--n-color);
}

/* =========== 左侧窗格 =========== */
.left-pane {
  width: 340px;
  flex-shrink: 0;
  background-color: var(--n-card-color);
  padding: 40px 20px 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-right: 1px solid var(--n-border-color);
  transition: background-color 0.3s var(--n-cubic-bezier-ease-in-out);
}

.left-content {
  /* 主要内容区域 */
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 10px;
  margin-bottom: 50px;
}

.logo-area .n-gradient-text {
  font-weight: bold;
  font-size: 24px;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease, color 0.2s ease;
  color: var(--n-text-color-2);
}

.action-item:hover {
  background-color: var(--n-hover-color);
  color: var(--n-text-color-1);
}

.left-footer {
  padding: 10px;
}

/* =========== 右侧窗格 =========== */
.right-pane {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; 
  min-height: 0;
  padding: 40px 60px;
  background-image: radial-gradient(var(--n-border-color) 1px, transparent 0);
  background-size: 20px 20px;
}

.content-wrapper {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.content-header {
  flex-shrink: 0;
}

.right-pane h2 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
}

.right-pane .subtitle {
  font-size: 16px;
  color: var(--n-text-color-2);
  margin-bottom: 30px;
}

.recent-list-container {
  flex-grow: 1;
  overflow-y: auto;
  min-height: 0;
  padding-right: 10px;
  margin-right: -10px;
}

/* 美化滚动条 */
.recent-list-container::-webkit-scrollbar {
  width: 6px;
}
.recent-list-container::-webkit-scrollbar-track {
  background: transparent;
}
.recent-list-container::-webkit-scrollbar-thumb {
  background-color: var(--n-border-color);
  border-radius: 3px;
}
.recent-list-container::-webkit-scrollbar-thumb:hover {
  background-color: var(--n-text-color-3);
}

.n-list-item {
  padding: 16px !important;
  border-radius: 8px;
}

.n-thing .n-thing-header {
  font-weight: 500;
  font-size: 16px;
}

.recent-item-path {
  font-size: 13px;
  color: var(--n-text-color-3);
  opacity: 0.8;
}

.hover-arrow {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.n-list-item:hover .hover-arrow {
  opacity: 1;
}

.empty-state {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>

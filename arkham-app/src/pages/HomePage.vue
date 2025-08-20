<template>
  <div class="welcome-container">
    <!-- 隐藏的文件夹选择元素 -->
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
          <div class="logo-icon">
            <n-icon size="48" :component="ColorWand" color="white" />
          </div>
          <div class="logo-text">
            <h1>阿卡姆印牌姬</h1>
            <p>专业的卡牌设计工具</p>
          </div>
        </div>

        <!-- 主要操作按钮 -->
        <div class="primary-action">
          <button class="open-folder-btn" @click="handleOpenFolder">
            <div class="btn-icon">
              <n-icon size="28" :component="FolderOpenOutline" />
            </div>
            <div class="btn-content">
              <span class="btn-title">打开项目文件夹</span>
              <span class="btn-desc">选择包含卡牌文件的文件夹开始工作</span>
            </div>
            <div class="btn-arrow">
              <n-icon size="20" :component="ArrowForwardOutline" />
            </div>
          </button>
        </div>

        <!-- 快捷说明 -->
        <div class="quick-info">
          <div class="info-item">
            <n-icon :component="FileTrayFullOutline" color="#a855f7" />
            <span>轻量化的json卡牌格式</span>
          </div>
          <div class="info-item">
            <n-icon :component="LayersOutline" color="#a855f7" />
            <span>同一个工作空间快捷D卡</span>
          </div>
          <div class="info-item">
            <n-icon :component="ImageOutline" color="#a855f7" />
            <span>自动装配TTS物品</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================= -->
    <!-- 右侧内容窗格 (Right Pane) -->
    <!-- ============================================= -->
    <div class="right-pane">
      <div class="content-wrapper">
        <header class="content-header">
          <h2>最近项目</h2>
          <p class="subtitle">选择一个最近使用的项目继续编辑</p>
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
  FolderOpenOutline,
  ArrowForwardOutline,
  ColorWand,
  CubeOutline,
  FileTrayFullOutline,
  LayersOutline,
  ImageOutline
} from '@vicons/ionicons5';
import { useMessage } from 'naive-ui';

// ----------- Props 和 Emits -----------
const emit = defineEmits<{
  'navigate-to-workspace': [params: {
    mode: 'file' | 'folder';
    projectPath: string;
    projectName: string;
  }];
}>();

// ----------- 文件选择相关 -----------
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
 * 模拟发送文件夹路径到后端
 */
const sendFolderPathToBackend = async (folderPath: string) => {
  console.log('🚀 [前端->后端] 发送文件夹路径:', folderPath);
  
  try {
    const response = await mockBackendCall('open_folder', { path: folderPath });
    console.log('✅ [后端->前端] 响应:', response);
    return response;
  } catch (error) {
    console.error('❌ [后端->前端] 错误:', error);
    throw error;
  }
};

/**
 * 模拟发送文件路径到后端
 */
const sendFilePathToBackend = async (filePath: string) => {
  console.log('🚀 [前端->后端] 发送文件路径:', filePath);
  
  try {
    const response = await mockBackendCall('open_file', { path: filePath });
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
 * 打开文件夹
 */
const handleOpenFolder = () => {
  console.log('📁 [阿卡姆印牌姬] 用户点击：打开文件夹');
  message.info('请选择一个项目文件夹...');
  
  if (folderInput.value) {
    folderInput.value.click();
  }
};

/**
 * 处理文件夹选择
 */
const handleFolderSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  
  if (files && files.length > 0) {
    const firstFile = files[0];
    const relativePath = firstFile.webkitRelativePath;
    const folderName = relativePath.split('/')[0];
    
    console.log('📁 [文件夹选择] 已选择文件夹:', folderName);
    console.log('📁 [文件夹选择] 文件夹内包含文件数量:', files.length);
    
    message.loading(`正在打开文件夹: ${folderName}...`);
    
    try {
      await sendFolderPathToBackend(folderName);
      
      message.destroyAll();
      message.success(`文件夹 "${folderName}" 已成功打开！包含 ${files.length} 个文件`);
      
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
    await sendFilePathToBackend(item.path);
    
    message.destroyAll();
    message.success(`已打开: ${item.name}`);
    
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
</script>

<style scoped>
/* =========== 顶级容器 =========== */
.welcome-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #f8fafc;
}

/* =========== 左侧窗格 =========== */
.left-pane {
  width: 420px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.left-pane::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.left-content {
  position: relative;
  z-index: 1;
}

.logo-area {
  text-align: center;
  margin-bottom: 60px;
}

.logo-icon {
  margin-bottom: 20px;
}

.logo-text h1 {
  color: white;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.logo-text p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  margin: 0;
}

.primary-action {
  margin-bottom: 50px;
}

.open-folder-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 20px;
  text-align: left;
  position: relative;
  overflow: hidden;
}

.open-folder-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.6s ease;
}

.open-folder-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.open-folder-btn:hover::before {
  left: 100%;
}

.btn-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-content {
  flex-grow: 1;
}

.btn-title {
  display: block;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
}

.btn-desc {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.btn-arrow {
  flex-shrink: 0;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.open-folder-btn:hover .btn-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.quick-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

/* =========== 右侧窗格 =========== */
.right-pane {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; 
  min-height: 0;
  padding: 40px 60px;
  background: #f8fafc;
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
  color: #1e293b;
}

.right-pane .subtitle {
  font-size: 16px;
  color: #64748b;
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
  background-color: #cbd5e1;
  border-radius: 3px;
}
.recent-list-container::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

.n-list-item {
  padding: 16px !important;
  border-radius: 8px;
  background: white;
  border: 1px solid #e2e8f0;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.n-list-item:hover {
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.n-thing .n-thing-header {
  font-weight: 500;
  font-size: 16px;
  color: #1e293b;
}

.recent-item-path {
  font-size: 13px;
  color: #64748b;
  opacity: 0.8;
}

.hover-arrow {
  opacity: 0;
  transition: all 0.2s ease;
  color: #667eea;
}

.n-list-item:hover .hover-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.empty-state {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* =========== 响应式设计 =========== */
@media (max-width: 1024px) {
  .left-pane {
    width: 380px;
    padding: 30px 25px;
  }
  
  .right-pane {
    padding: 30px 40px;
  }
}

@media (max-width: 768px) {
  .welcome-container {
    flex-direction: column;
  }
  
  .left-pane {
    width: 100%;
    padding: 30px 20px;
  }
  
  .right-pane {
    padding: 30px 20px;
  }
  
  .logo-text h1 {
    font-size: 28px;
  }
  
  .btn-title {
    font-size: 16px;
  }
  
  .btn-desc {
    font-size: 13px;
  }
}
</style>

<template>
  <div class="file-tree-pane" :style="{ width: width + 'px' }">
    <div class="pane-header">
      <n-space align="center" justify="space-between">
        <n-space align="center" size="small">
          <n-button size="tiny" quaternary @click="$emit('go-back')" class="header-button">
            <n-icon :component="ArrowBackOutline" />
          </n-button>
          <span class="pane-title">文件资源管理器</span>
        </n-space>
        <n-space align="center" size="small">
          <n-button size="tiny" @click="refreshFileTree" class="header-button">
            <n-icon :component="RefreshOutline" />
          </n-button>
          <n-dropdown :options="createOptions" @select="handleCreateSelect">
            <n-button size="tiny" class="header-button">
              <n-icon :component="AddOutline" />
            </n-button>
          </n-dropdown>
          <n-button size="tiny" @click="$emit('toggle')" class="header-button">
            <n-icon :component="Close" />
          </n-button>
        </n-space>
      </n-space>
    </div>

    <div class="file-tree-content">
      <n-spin :show="loading">
        <n-tree 
          v-if="fileTreeData && fileTreeData.length > 0"
          :data="fileTreeData" 
          :render-label="renderTreeLabel" 
          :render-prefix="renderTreePrefix" 
          selectable
          expand-on-click 
          @update:selected-keys="handleFileSelect"
        />
        <n-empty v-else description="暂无文件" />
      </n-spin>
    </div>

    <!-- 右键菜单 -->
    <n-dropdown
      placement="bottom-start"
      trigger="manual"
      :x="contextMenuX"
      :y="contextMenuY"
      :options="contextMenuOptions"
      :show="showContextMenu"
      @clickoutside="showContextMenu = false"
      @select="handleContextMenuSelect"
    />

    <!-- 新建文件夹对话框 -->
    <n-modal v-model:show="showCreateFolderDialog">
      <n-card
        style="width: 400px"
        title="新建文件夹"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-form ref="createFolderFormRef" :model="createFolderForm" :rules="createFolderRules">
          <n-form-item path="name" label="文件夹名称">
            <n-input
              v-model:value="createFolderForm.name"
              placeholder="请输入文件夹名称"
              @keydown.enter="handleCreateFolder"
              clearable
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCreateFolderDialog = false">取消</n-button>
            <n-button type="primary" @click="handleCreateFolder" :loading="creating">确定</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 新建卡牌对话框 -->
    <n-modal v-model:show="showCreateCardDialog">
      <n-card
        style="width: 400px"
        title="新建卡牌"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-form ref="createCardFormRef" :model="createCardForm" :rules="createCardRules">
          <n-form-item path="name" label="卡牌文件名">
            <n-input
              v-model:value="createCardForm.name"
              placeholder="请输入卡牌文件名（自动添加.card扩展名）"
              @keydown.enter="handleCreateCard"
              clearable
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCreateCardDialog = false">取消</n-button>
            <n-button type="primary" @click="handleCreateCard" :loading="creating">确定</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 重命名对话框 -->
    <n-modal v-model:show="showRenameDialog">
      <n-card
        style="width: 450px"
        title="重命名"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-form ref="renameFormRef" :model="renameForm" :rules="renameRules">
          <n-form-item path="filename" label="文件名">
            <n-input
              v-model:value="renameForm.filename"
              placeholder="请输入文件名"
              clearable
            />
          </n-form-item>
          <n-form-item path="extension" label="扩展名" v-if="showExtensionField">
            <n-input
              v-model:value="renameForm.extension"
              placeholder="请输入扩展名（不含点号）"
              clearable
            >
              <template #prefix>.</template>
            </n-input>
          </n-form-item>
          <n-space vertical size="small">
            <n-text depth="3" style="font-size: 12px;">
              预览: {{ renamePreview }}
            </n-text>
          </n-space>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showRenameDialog = false">取消</n-button>
            <n-button type="primary" @click="handleRename" :loading="renaming">确定</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal v-model:show="showDeleteDialog">
      <n-card
        style="width: 450px"
        title="删除确认"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-space vertical>
          <n-alert type="warning" title="警告">
            <template #icon>
              <n-icon :component="WarningOutline" />
            </template>
            此操作不可恢复，请确认是否删除？
          </n-alert>
          <n-space vertical size="small">
            <p><strong>{{ deleteConfirmText }}</strong></p>
            <p style="color: #666; font-size: 12px;">
              路径: {{ contextMenuTarget?.path }}
            </p>
          </n-space>
        </n-space>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showDeleteDialog = false">取消</n-button>
            <n-button type="error" @click="handleDelete" :loading="deleting">删除</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted, computed } from 'vue';
import { NIcon, useMessage, NText } from 'naive-ui';
import type { TreeOption, FormInst, FormRules } from 'naive-ui';
import {
  FolderOpenOutline,
  DocumentOutline,
  ImageOutline,
  Close,
  ArrowBackOutline,
  LayersOutline,
  GridOutline,
  SettingsOutline,
  FolderOutline,
  AddOutline,
  RefreshOutline,
  CreateOutline,
  TrashOutline,
  WarningOutline
} from '@vicons/ionicons5';

// 导入API服务
import { WorkspaceService, ApiError } from '@/api';

interface Props {
  width: number;
}

defineProps<Props>();

const emit = defineEmits<{
  'toggle': [];
  'go-back': [];
  'file-select': [keys: Array<string | number>, option?: TreeOption];
}>();

const message = useMessage();

// 状态管理
const loading = ref(false);
const creating = ref(false);
const renaming = ref(false);
const deleting = ref(false);

// 文件树数据
const fileTreeData = ref<TreeOption[]>([]);

// 右键菜单
const showContextMenu = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuTarget = ref<TreeOption | null>(null);

// 对话框状态
const showCreateFolderDialog = ref(false);
const showCreateCardDialog = ref(false);
const showRenameDialog = ref(false);
const showDeleteDialog = ref(false);

// 表单数据
const createFolderForm = ref({ name: '' });
const createCardForm = ref({ name: '' });
const renameForm = ref({ 
  filename: '', 
  extension: '' 
});

// 表单引用
const createFolderFormRef = ref<FormInst | null>(null);
const createCardFormRef = ref<FormInst | null>(null);
const renameFormRef = ref<FormInst | null>(null);

// 是否显示扩展名字段（文件夹不显示）
const showExtensionField = computed(() => {
  return contextMenuTarget.value?.type !== 'directory' && 
         contextMenuTarget.value?.type !== 'workspace';
});

// 重命名预览
const renamePreview = computed(() => {
  if (!renameForm.value.filename) return '';
  
  if (showExtensionField.value && renameForm.value.extension) {
    return `${renameForm.value.filename}.${renameForm.value.extension}`;
  } else {
    return renameForm.value.filename;
  }
});

// 表单验证规则
const createFolderRules: FormRules = {
  name: [
    { required: true, message: '请输入文件夹名称', trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: '文件夹名称长度在1-50个字符', trigger: ['input', 'blur'] },
    { 
      pattern: /^[^\\/:*?"<>|]+$/, 
      message: '文件夹名称不能包含特殊字符 \\/:*?"<>|', 
      trigger: ['input', 'blur'] 
    }
  ]
};

const createCardRules: FormRules = {
  name: [
    { required: true, message: '请输入卡牌文件名', trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: '卡牌文件名长度在1-50个字符', trigger: ['input', 'blur'] },
    { 
      pattern: /^[^\\/:*?"<>|]+$/, 
      message: '卡牌文件名不能包含特殊字符 \\/:*?"<>|', 
      trigger: ['input', 'blur'] 
    }
  ]
};

const renameRules: FormRules = {
  filename: [
    { required: true, message: '请输入文件名', trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: '文件名长度在1-50个字符', trigger: ['input', 'blur'] },
    { 
      pattern: /^[^\\/:*?"<>|.]+$/, 
      message: '文件名不能包含特殊字符 \\/:*?"<>|.', 
      trigger: ['input', 'blur'] 
    }
  ],
  extension: [
    { 
      pattern: /^[^\\/:*?"<>|.]*$/, 
      message: '扩展名不能包含特殊字符 \\/:*?"<>|.', 
      trigger: ['input', 'blur'] 
    }
  ]
};

// 删除确认文本
const deleteConfirmText = computed(() => {
  if (!contextMenuTarget.value) return '';
  const isDirectory = contextMenuTarget.value.type === 'directory';
  const name = contextMenuTarget.value.label as string;
  return `${isDirectory ? '文件夹' : '文件'}: ${name}`;
});

// 创建选项
const createOptions = [
  {
    label: '新建文件夹',
    key: 'folder',
    icon: () => h(NIcon, { component: FolderOutline })
  },
  {
    label: '新建卡牌',
    key: 'card',
    icon: () => h(NIcon, { component: DocumentOutline })
  }
];

// 右键菜单选项
const contextMenuOptions = computed(() => {
  if (!contextMenuTarget.value) return [];

  const isWorkspace = contextMenuTarget.value.type === 'workspace';
  const isDirectory = contextMenuTarget.value.type === 'directory';
  const isFile = !isWorkspace && !isDirectory;

  const options = [];

  // 工作空间和目录可以创建子项
  if (isWorkspace || isDirectory) {
    options.push(
      {
        label: '新建文件夹',
        key: 'create-folder',
        icon: () => h(NIcon, { component: FolderOutline })
      },
      {
        label: '新建卡牌',
        key: 'create-card',
        icon: () => h(NIcon, { component: DocumentOutline })
      }
    );
  }

  // 非工作空间节点可以重命名和删除
  if (!isWorkspace) {
    if (options.length > 0) {
      options.push({ type: 'divider', key: 'divider1' });
    }
    options.push(
      {
        label: '重命名',
        key: 'rename',
        icon: () => h(NIcon, { component: CreateOutline })
      },
      {
        label: '删除',
        key: 'delete',
        icon: () => h(NIcon, { component: TrashOutline })
      }
    );
  }

  return options;
});

// 解析文件名和扩展名
const parseFileName = (fileName: string) => {
  const lastDotIndex = fileName.lastIndexOf('.');
  if (lastDotIndex === -1 || lastDotIndex === 0) {
    // 没有扩展名或者以点开头的文件
    return {
      filename: fileName,
      extension: ''
    };
  }
  
  return {
    filename: fileName.substring(0, lastDotIndex),
    extension: fileName.substring(lastDotIndex + 1)
  };
};

// 根据文件扩展名获取文件类型
const getFileType = (fileName: string): string => {
  if (!fileName.includes('.')) return 'file';
  
  const extension = fileName.split('.').pop()?.toLowerCase() || '';
  
  if (extension === 'card') return 'card';
  if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(extension)) return 'image';
  if (['json', 'yml', 'yaml', 'toml'].includes(extension)) return 'config';
  if (['csv', 'tsv', 'dat'].includes(extension)) return 'data';
  if (['css', 'scss', 'sass', 'less'].includes(extension)) return 'style';
  if (['txt', 'md', 'markdown'].includes(extension)) return 'text';
  
  return 'file';
};

// 转换API返回的文件树结构为组件所需格式
const convertFileTreeData = (node: any): TreeOption => {
  const treeNode: TreeOption = {
    label: node.label,
    key: node.key,
    type: node.type,
    path: node.path
  };

  if (node.children && node.children.length > 0) {
    treeNode.children = node.children.map(convertFileTreeData);
  }

  return treeNode;
};

// 文件树操作辅助函数
const findNodeByPath = (nodes: TreeOption[], path: string): TreeOption | null => {
  for (const node of nodes) {
    if (node.path === path) {
      return node;
    }
    if (node.children) {
      const found = findNodeByPath(node.children, path);
      if (found) return found;
    }
  }
  return null;
};

// 在指定父路径下添加新节点
const addNodeToTree = (nodes: TreeOption[], parentPath: string | undefined, newNode: TreeOption): boolean => {
  // 如果没有指定父路径，添加到根目录
  if (!parentPath) {
    if (nodes.length > 0 && nodes[0].type === 'workspace') {
      if (!nodes[0].children) {
        nodes[0].children = [];
      }
      nodes[0].children.push(newNode);
      // 按名称排序，目录在前
      nodes[0].children.sort((a, b) => {
        if (a.type === 'directory' && b.type !== 'directory') return -1;
        if (a.type !== 'directory' && b.type === 'directory') return 1;
        return (a.label as string).localeCompare(b.label as string);
      });
      return true;
    }
    return false;
  }

  // 递归查找父节点并添加
  for (const node of nodes) {
    if (node.path === parentPath) {
      if (!node.children) {
        node.children = [];
      }
      node.children.push(newNode);
      // 按名称排序，目录在前
      node.children.sort((a, b) => {
        if (a.type === 'directory' && b.type !== 'directory') return -1;
        if (a.type !== 'directory' && b.type === 'directory') return 1;
        return (a.label as string).localeCompare(b.label as string);
      });
      return true;
    }
    if (node.children) {
      if (addNodeToTree(node.children, parentPath, newNode)) {
        return true;
      }
    }
  }
  return false;
};

// 从树中删除节点
const removeNodeFromTree = (nodes: TreeOption[], path: string): boolean => {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].path === path) {
      nodes.splice(i, 1);
      return true;
    }
    if (nodes[i].children) {
      if (removeNodeFromTree(nodes[i].children!, path)) {
        return true;
      }
    }
  }
  return false;
};

// 更新树中节点的信息
const updateNodeInTree = (nodes: TreeOption[], oldPath: string, newLabel: string, newPath: string): boolean => {
  for (const node of nodes) {
    if (node.path === oldPath) {
      node.label = newLabel;
      node.path = newPath;
      return true;
    }
    if (node.children) {
      if (updateNodeInTree(node.children, oldPath, newLabel, newPath)) {
        return true;
      }
    }
  }
  return false;
};

// 加载文件树
const loadFileTree = async () => {
  loading.value = true;
  try {
    const data = await WorkspaceService.getFileTree(false);
    // API返回的是单个根节点对象，需要转换为数组
    if (data.fileTree) {
      fileTreeData.value = [convertFileTreeData(data.fileTree)];
    } else {
      fileTreeData.value = [];
    }
  } catch (error) {
    console.error('加载文件树失败:', error);
    if (error instanceof ApiError) {
      message.error(`加载文件树失败: ${error.message}`);
    } else {
      message.error('加载文件树失败，请检查服务连接');
    }
    fileTreeData.value = [];
  } finally {
    loading.value = false;
  }
};

// 刷新文件树
const refreshFileTree = () => {
  loadFileTree();
};

// 渲染树节点标签
const renderTreeLabel = ({ option }: { option: TreeOption }) => {
  return h('span', {
    onContextmenu: (e: MouseEvent) => handleRightClick(e, option)
  }, option.label as string);
};

// 渲染树节点前缀图标
const renderTreePrefix = ({ option }: { option: TreeOption }) => {
  const iconStyle = { marginRight: '6px' };

  const iconMap = {
    'workspace': { component: LayersOutline, color: '#667eea' },
    'directory': { component: FolderOpenOutline, color: '#ffa726' },
    'card': { component: DocumentOutline, color: '#42a5f5' },
    'image': { component: ImageOutline, color: '#66bb6a' },
    'config': { component: GridOutline, color: '#ff7043' },
    'data': { component: GridOutline, color: '#ff7043' },
    'style': { component: SettingsOutline, color: '#ec407a' },
    'text': { component: DocumentOutline, color: '#8d6e63' },
    'file': { component: DocumentOutline, color: '#90a4ae' },
    'default': { component: DocumentOutline, color: '#90a4ae' }
  };

  const iconConfig = iconMap[option.type as keyof typeof iconMap] || iconMap.default;

  return h(NIcon, {
    component: iconConfig.component,
    color: iconConfig.color,
    size: option.type === 'workspace' ? 18 : option.type === 'directory' ? 16 : 14,
    style: iconStyle
  });
};

// 处理文件选择
const handleFileSelect = (keys: Array<string | number>, options: TreeOption[]) => {
  emit('file-select', keys, options[0]);
};

// 处理右键点击
const handleRightClick = (e: MouseEvent, option: TreeOption) => {
  e.preventDefault();
  e.stopPropagation();
  contextMenuTarget.value = option;
  contextMenuX.value = e.clientX;
  contextMenuY.value = e.clientY;
  showContextMenu.value = true;
};

// 处理创建选择
const handleCreateSelect = (key: string) => {
  if (key === 'folder') {
    createFolderForm.value.name = '';
    contextMenuTarget.value = fileTreeData.value[0]; // 默认在根目录创建
    showCreateFolderDialog.value = true;
  } else if (key === 'card') {
    createCardForm.value.name = '';
    contextMenuTarget.value = fileTreeData.value[0]; // 默认在根目录创建
    showCreateCardDialog.value = true;
  }
};

// 处理右键菜单选择
const handleContextMenuSelect = (key: string) => {
  showContextMenu.value = false;

  switch (key) {
    case 'create-folder':
      createFolderForm.value.name = '';
      showCreateFolderDialog.value = true;
      break;
    case 'create-card':
      createCardForm.value.name = '';
      showCreateCardDialog.value = true;
      break;
    case 'rename':
      const currentName = contextMenuTarget.value?.label as string || '';
      const parsed = parseFileName(currentName);
      renameForm.value.filename = parsed.filename;
      renameForm.value.extension = parsed.extension;
      showRenameDialog.value = true;
      break;
    case 'delete':
      showDeleteDialog.value = true;
      break;
  }
};

// 处理创建文件夹
const handleCreateFolder = async () => {
  if (!createFolderFormRef.value) return;

  try {
    await createFolderFormRef.value.validate();
    creating.value = true;
  
    const parentPath = contextMenuTarget.value?.path;
    await WorkspaceService.createDirectory(createFolderForm.value.name, parentPath);
    
    // 构建新节点路径
    const newPath = parentPath 
      ? `${parentPath}/${createFolderForm.value.name}`
      : createFolderForm.value.name;
    
    // 直接在文件树中添加新节点
    const newNode: TreeOption = {
      label: createFolderForm.value.name,
      key: newPath,
      type: 'directory',
      path: newPath,
      children: []
    };
    
    addNodeToTree(fileTreeData.value, parentPath, newNode);
  
    message.success('文件夹创建成功');
    showCreateFolderDialog.value = false;
    createFolderForm.value.name = '';
  } catch (error) {
    console.error('创建文件夹失败:', error);
    if (error instanceof ApiError) {
      message.error(`创建文件夹失败: ${error.message}`);
    } else if (error.errors) {
      // 表单验证错误，不显示消息
    } else {
      message.error('创建文件夹失败，请重试');
    }
  } finally {
    creating.value = false;
  }
};

// 处理创建卡牌
const handleCreateCard = async () => {
  if (!createCardFormRef.value) return;

  try {
    await createCardFormRef.value.validate();
    creating.value = true;
  
    const fileName = createCardForm.value.name.endsWith('.card') 
      ? createCardForm.value.name 
      : `${createCardForm.value.name}.card`;
  
    const parentPath = contextMenuTarget.value?.path;
  
    // 创建空的JSON对象
    const defaultContent = '{}';
  
    await WorkspaceService.createFile(fileName, defaultContent, parentPath);
    
    // 构建新节点路径
    const newPath = parentPath 
      ? `${parentPath}/${fileName}`
      : fileName;
    
    // 直接在文件树中添加新节点
    const newNode: TreeOption = {
      label: fileName,
      key: newPath,
      type: 'card',
      path: newPath
    };
    
    addNodeToTree(fileTreeData.value, parentPath, newNode);
  
    message.success('卡牌创建成功');
    showCreateCardDialog.value = false;
    createCardForm.value.name = '';
  } catch (error) {
    console.error('创建卡牌失败:', error);
    if (error instanceof ApiError) {
      message.error(`创建卡牌失败: ${error.message}`);
    } else if (error.errors) {
      // 表单验证错误，不显示消息
    } else {
      message.error('创建卡牌失败，请重试');
    }
  } finally {
    creating.value = false;
  }
};

// 处理重命名
const handleRename = async () => {
  if (!renameFormRef.value || !contextMenuTarget.value?.path) return;

  try {
    await renameFormRef.value.validate();
    renaming.value = true;
  
    // 构建新文件名
    const newName = showExtensionField.value && renameForm.value.extension
      ? `${renameForm.value.filename}.${renameForm.value.extension}`
      : renameForm.value.filename;
  
    const oldPath = contextMenuTarget.value.path;
    await WorkspaceService.renameItem(oldPath, newName);
    
    // 构建新路径
    const pathParts = oldPath.split('/');
    pathParts[pathParts.length - 1] = newName;
    const newPath = pathParts.join('/');
    
    // 直接在文件树中更新节点
    updateNodeInTree(fileTreeData.value, oldPath, newName, newPath);
    
    // 如果是文件，更新类型
    const targetNode = findNodeByPath(fileTreeData.value, newPath);
    if (targetNode && targetNode.type !== 'directory' && targetNode.type !== 'workspace') {
      targetNode.type = getFileType(newName);
    }
  
    message.success('重命名成功');
    showRenameDialog.value = false;
    renameForm.value.filename = '';
    renameForm.value.extension = '';
  } catch (error) {
    console.error('重命名失败:', error);
    if (error instanceof ApiError) {
      message.error(`重命名失败: ${error.message}`);
    } else if (error.errors) {
      // 表单验证错误，不显示消息
    } else {
      message.error('重命名失败，请重试');
    }
  } finally {
    renaming.value = false;
  }
};

// 处理删除
const handleDelete = async () => {
  if (!contextMenuTarget.value?.path) return;

  try {
    deleting.value = true;
    const pathToDelete = contextMenuTarget.value.path;
    
    await WorkspaceService.deleteItem(pathToDelete);
    
    // 直接从文件树中删除节点
    removeNodeFromTree(fileTreeData.value, pathToDelete);
  
    message.success('删除成功');
    showDeleteDialog.value = false;
  } catch (error) {
    console.error('删除失败:', error);
    if (error instanceof ApiError) {
      message.error(`删除失败: ${error.message}`);
    } else {
      message.error('删除失败，请重试');
    }
  } finally {
    deleting.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadFileTree();
});

// 导出方法供父组件调用
defineExpose({
  refreshFileTree
});
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

/* 头部按钮样式优化 */
.header-button {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  transition: all 0.2s ease;
}

.header-button:hover {
  background: rgba(255, 255, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.header-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

/* 树组件样式优化 */
:deep(.n-tree-node-content) {
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

:deep(.n-tree-node-content:hover) {
  background-color: rgba(102, 126, 234, 0.1);
}

:deep(.n-tree-node-content--selected) {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
}

/* 模态对话框优化 */
:deep(.n-modal) {
  backdrop-filter: blur(8px);
}

:deep(.n-card) {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
}

:deep(.n-form-item-label__text) {
  font-weight: 500;
}

:deep(.n-input__input-el) {
  border-radius: 6px;
}

:deep(.n-select .n-base-selection) {
  border-radius: 6px;
}

/* 按钮样式优化 */
:deep(.n-button) {
  border-radius: 6px;
  transition: all 0.2s ease;
}

:deep(.n-button--primary) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
}

:deep(.n-button--primary:hover) {
  background: linear-gradient(90deg, #5a67d8 0%, #6b46c1 100%);
  transform: translateY(-1px);
}

:deep(.n-button--error) {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
  border: none;
}

:deep(.n-button--error:hover) {
  background: linear-gradient(90deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-1px);
}
</style>

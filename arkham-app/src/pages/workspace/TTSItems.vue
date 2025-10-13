<template>
  <div class="content-package-manager-container">
    <div class="package-manager-header">
      <h2>{{ $t('contentPackage.title') }}</h2>
      <div class="header-actions">
        <n-button type="primary" @click="showCreatePackageDialog = true" size="large">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          {{ $t('contentPackage.actions.newPackage') }}
        </n-button>
      </div>
    </div>

    <div class="package-manager-content">
      <!-- 左侧内容包列表 -->
      <div class="package-list-panel">
        <div class="panel-header">
          <h3>{{ $t('contentPackage.panels.myPackages') }}</h3>
          <n-button text @click="loadPackages" :loading="loading" :title="$t('contentPackage.actions.refresh')">
            <n-icon :component="RefreshOutline" />
          </n-button>
        </div>
        <n-scrollbar class="package-list">
          <div v-for="pkg in packageList" :key="pkg.path" class="package-item"
            :class="{ 'active': selectedPackage?.path === pkg.path }" @click="selectPackage(pkg)">
            <div class="package-icon">📦</div>
            <div class="package-info">
              <div class="package-name">{{ pkg.meta.name }}</div>
              <div class="package-meta">
                {{ pkg.meta.language === 'zh' ? '中文' : '英文' }} · {{ formatPackageTypes(pkg.meta.types) }}
                <span class="author">{{ pkg.meta.author }}</span>
              </div>
            </div>
            <n-button text type="error" @click.stop="showDeleteConfirm(pkg)" :title="$t('contentPackage.actions.delete')" size="small">
              <n-icon :component="TrashOutline" />
            </n-button>
          </div>
          <n-empty v-if="packageList.length === 0 && !loading" :description="$t('contentPackage.packageList.empty')">
            <template #icon>
              <n-icon :component="FolderOpenOutline" />
            </template>
            <template #extra>
              <n-text depth="3">{{ $t('contentPackage.packageList.emptyDesc') }}</n-text>
            </template>
          </n-empty>
        </n-scrollbar>
      </div>

      <!-- 右侧内容包编辑器 -->
      <PackageEditor v-if="selectedPackage" :package="selectedPackage" :saving="saving"
        @save="savePackage" @update:package="updateSelectedPackage" />

      <!-- 当没有选择内容包时显示的提示 -->
      <div v-else class="no-package-selected">
        <n-empty :description="$t('contentPackage.noSelection.title')">
          <template #icon>
            <n-icon :component="FolderOpenOutline" size="64" />
          </template>
          <template #extra>
            <n-text depth="3">{{ $t('contentPackage.noSelection.description') }}</n-text>
          </template>
        </n-empty>
      </div>
    </div>

    <!-- 新建内容包对话框 -->
    <n-modal v-model:show="showCreatePackageDialog" preset="dialog" :title="$t('contentPackage.forms.newPackage.title')" style="width: 600px;">
      <n-form ref="createFormRef" :model="newPackageForm" :rules="createRules" label-placement="left" label-width="100px">
        <n-form-item path="name" :label="$t('contentPackage.forms.newPackage.name')">
          <n-input v-model:value="newPackageForm.name" :placeholder="$t('contentPackage.forms.newPackage.namePlaceholder')" clearable />
        </n-form-item>
        <n-form-item path="description" :label="$t('contentPackage.forms.newPackage.description')">
          <n-input v-model:value="newPackageForm.description" type="textarea" :placeholder="$t('contentPackage.forms.newPackage.descriptionPlaceholder')"
            :rows="3" clearable />
        </n-form-item>
        <n-form-item path="author" :label="$t('contentPackage.forms.newPackage.author')">
          <n-input v-model:value="newPackageForm.author" :placeholder="$t('contentPackage.forms.newPackage.authorPlaceholder')" clearable />
        </n-form-item>
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item path="language" :label="$t('contentPackage.forms.newPackage.language')">
              <n-select v-model:value="newPackageForm.language" :options="LANGUAGE_OPTIONS" clearable />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item path="types" :label="$t('contentPackage.forms.newPackage.types')">
              <n-select v-model:value="newPackageForm.types" :options="PACKAGE_TYPE_OPTIONS" multiple clearable />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item path="external_link" :label="$t('contentPackage.forms.newPackage.externalLink')">
          <n-input v-model:value="newPackageForm.external_link" :placeholder="$t('contentPackage.forms.newPackage.externalLinkPlaceholder')" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.forms.newPackage.banner')">
          <n-tabs type="line" default-value="url">
            <n-tab-pane name="url" :tab="$t('contentPackage.forms.newPackage.bannerUrl')">
              <n-input v-model:value="newPackageForm.banner_url" :placeholder="$t('contentPackage.forms.newPackage.bannerUrlPlaceholder')" clearable />
            </n-tab-pane>
            <n-tab-pane name="file" :tab="$t('contentPackage.forms.newPackage.bannerFile')">
              <div class="banner-upload-container">
                <div v-if="!newPackageForm.banner_base64" class="upload-area">
                  <n-upload
                    :max="1"
                    accept="image/*"
                    @change="handleBannerUpload"
                    :show-download-button="false"
                    :default-upload="false"
                    :show-file-list="false"
                  >
                    <n-upload-dragger>
                      <div style="margin-bottom: 12px">
                        <n-icon size="48" :depth="3">
                          <CloudUploadOutline />
                        </n-icon>
                      </div>
                      <n-text style="font-size: 16px">
                        {{ $t('contentPackage.forms.newPackage.dragToUpload') }}
                      </n-text>
                      <n-p depth="3" style="margin: 8px 0 0 0">
                        {{ $t('contentPackage.forms.newPackage.uploadHint') }}
                      </n-p>
                    </n-upload-dragger>
                  </n-upload>
                </div>
                <div v-else class="banner-preview" @click="triggerFileInput">
                  <img :src="newPackageForm.banner_base64" alt="封面预览" />
                  <div class="banner-preview-overlay">
                    <n-button circle type="error" @click.stop="handleBannerRemove">
                      <template #icon>
                        <n-icon :component="TrashOutline" />
                      </template>
                    </n-button>
                    <n-button circle type="primary" @click.stop="triggerFileInput">
                      <template #icon>
                        <n-icon :component="CreateOutline" />
                      </template>
                    </n-button>
                  </div>
                </div>
                <!-- 隐藏的文件输入框，用于重新上传 -->
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleFileInputChange"
                />
              </div>
            </n-tab-pane>
          </n-tabs>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="closeCreateDialog">{{ $t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="createPackage" :loading="creating">
            {{ $t('contentPackage.actions.create') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal v-model:show="showDeleteDialog" preset="dialog" :title="$t('contentPackage.deleteDialog.title')">
      <n-alert type="warning" :title="$t('contentPackage.deleteDialog.warning')">
        <template #icon>
          <n-icon :component="WarningOutline" />
        </template>
        {{ $t('contentPackage.deleteDialog.message', { name: packageToDelete?.meta.name }) }}
      </n-alert>
      <template #action>
        <n-space>
          <n-button @click="showDeleteDialog = false">{{ $t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="error" @click="confirmDeletePackage" :loading="deleting">
            {{ $t('contentPackage.actions.delete') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import {
  useMessage,
  type FormInst,
  type FormRules,
  type UploadFileInfo
} from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
  AddOutline,
  RefreshOutline,
  TrashOutline,
  FolderOpenOutline,
  WarningOutline,
  CloudUploadOutline,
  CreateOutline
} from '@vicons/ionicons5';
import { v4 as uuidv4 } from 'uuid';
import { WorkspaceService } from '@/api';
import PackageEditor from '@/components/PackageEditor.vue';
import type {
  ContentPackage,
  ContentPackageFile,
  CreatePackageForm,
  ContentPackageMeta,
  PackageType
} from '@/types/content-package';
import {
  createDefaultMeta,
  createDefaultPackage,
  PACKAGE_TYPE_OPTIONS,
  LANGUAGE_OPTIONS
} from '@/types/content-package';

const message = useMessage();
const { t } = useI18n();

// 状态管理
const loading = ref(false);
const saving = ref(false);
const creating = ref(false);
const deleting = ref(false);

// 内容包相关
const packageList = ref<ContentPackageFile[]>([]);
const selectedPackage = ref<ContentPackageFile | null>(null);

// 新建内容包表单
const showCreatePackageDialog = ref(false);
const createFormRef = ref<FormInst | null>(null);
const newPackageForm = ref<CreatePackageForm>({
  name: '',
  description: '',
  author: '',
  language: 'zh',
  types: [],
  external_link: '',
  banner_url: '',
  banner_base64: ''
});

// 删除确认对话框
const showDeleteDialog = ref(false);
const packageToDelete = ref<ContentPackageFile | null>(null);

// 文件输入框引用
const fileInputRef = ref<HTMLInputElement | null>(null);

// 表单验证规则
const createRules = computed((): FormRules => ({
  name: [
    { required: true, message: t('contentPackage.forms.validation.nameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 100, message: t('contentPackage.forms.validation.nameLength'), trigger: ['input', 'blur'] },
    {
      pattern: /^[^\\/:*?"<>|]+$/,
      message: t('contentPackage.forms.validation.namePattern'),
      trigger: ['input', 'blur']
    }
  ],
  description: [
    { required: true, message: t('contentPackage.forms.validation.descriptionRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 1000, message: t('contentPackage.forms.validation.descriptionLength'), trigger: ['input', 'blur'] }
  ],
  author: [
    { required: true, message: t('contentPackage.forms.validation.authorRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 100, message: t('contentPackage.forms.validation.authorLength'), trigger: ['input', 'blur'] }
  ],
  language: [
    { required: true, message: t('contentPackage.forms.validation.languageRequired'), trigger: ['change', 'blur'] }
  ],
  types: [
    {
      required: true,
      validator: (rule: any, value: any) => {
        if (!value || !Array.isArray(value) || value.length === 0) {
          return new Error(t('contentPackage.forms.validation.typesRequired'));
        }
        return true;
      },
      trigger: ['change', 'blur']
    }
  ]
}));

// 格式化内容包类型显示
const formatPackageTypes = (types: PackageType[]): string => {
  return types.map(type => {
    const option = PACKAGE_TYPE_OPTIONS.find(opt => opt.value === type);
    return option ? option.label : type;
  }).join('、');
};

// 确保ContentPackage目录存在
const ensureContentPackageDirectory = async () => {
  try {
    await WorkspaceService.createDirectory('ContentPackage');
  } catch (error) {
    console.log('ContentPackage目录已存在或创建失败:', error);
  }
};

// 加载所有内容包
const loadPackages = async () => {
  loading.value = true;
  try {
    await ensureContentPackageDirectory();

    const response = await WorkspaceService.getFileTree();
    const contentPackageNode = findContentPackageNode(response.fileTree);

    if (contentPackageNode && contentPackageNode.children) {
      const packageFiles = contentPackageNode.children.filter(
        (file: any) => file.label.endsWith('.pack')
      );

      const packages: ContentPackageFile[] = [];
      for (const file of packageFiles) {
        try {
          const content = await WorkspaceService.getFileContent(file.path);
          const packageData: ContentPackage = JSON.parse(content);

          packages.push({
            name: packageData.meta.name,
            path: file.path,
            meta: packageData.meta,
            banner_base64: packageData.banner_base64
          });
        } catch (error) {
          console.error(`加载内容包文件失败: ${file.path}`, error);
        }
      }

      packageList.value = packages;
    } else {
      packageList.value = [];
    }

    message.success(t('contentPackage.messages.refreshSuccess'));
  } catch (error) {
    console.error('加载内容包列表失败:', error);
    message.error(t('contentPackage.messages.loadFailed'));
  } finally {
    loading.value = false;
  }
};

// 查找ContentPackage节点
const findContentPackageNode = (node: any): any => {
  if (node.label === 'ContentPackage') return node;
  if (node.children) {
    for (const child of node.children) {
      const found = findContentPackageNode(child);
      if (found) return found;
    }
  }
  return null;
};

// 选择内容包
const selectPackage = async (pkg: ContentPackageFile) => {
  selectedPackage.value = pkg;
};

// 更新选中的内容包
const updateSelectedPackage = (updatedPackage: ContentPackageFile) => {
  if (selectedPackage.value && selectedPackage.value.path === updatedPackage.path) {
    Object.assign(selectedPackage.value, updatedPackage);
    const index = packageList.value.findIndex(pkg => pkg.path === updatedPackage.path);
    if (index > -1) {
      Object.assign(packageList.value[index], updatedPackage);
    }
  } else {
    selectedPackage.value = updatedPackage;
  }
};

// 处理封面上传
const handleBannerUpload = async (data: { file: UploadFileInfo, fileList: UploadFileInfo[] }) => {
  if (data.file.file) {
    handleFileUpload(data.file.file);
  }
};

// 处理封面移除
const handleBannerRemove = () => {
  newPackageForm.value.banner_base64 = '';
};

// 触发文件输入框
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

// 处理文件输入框变化
const handleFileInputChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    handleFileUpload(file);
  }
  // 清空输入框，允许重复选择同一个文件
  target.value = '';
};

// 处理文件上传
const handleFileUpload = (file: File) => {
  try {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        newPackageForm.value.banner_base64 = e.target.result as string;
      }
    };
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('读取封面文件失败:', error);
    message.error(t('contentPackage.messages.readBannerFailed'));
  }
};

// 创建新内容包
const createPackage = async () => {
  if (!createFormRef.value) return;

  try {
    await createFormRef.value.validate();
    creating.value = true;

    await ensureContentPackageDirectory();

    const meta: ContentPackageMeta = {
      ...createDefaultMeta(),
      code: uuidv4(),
      name: newPackageForm.value.name,
      description: newPackageForm.value.description,
      author: newPackageForm.value.author,
      language: newPackageForm.value.language,
      types: newPackageForm.value.types,
      external_link: newPackageForm.value.external_link || '',
      banner_url: newPackageForm.value.banner_url || ''
    };

    const packageData: ContentPackage = {
      meta,
      banner_base64: newPackageForm.value.banner_base64
    };

    const fileName = `${newPackageForm.value.name}.pack`;
    const filePath = `ContentPackage/${fileName}`;

    await WorkspaceService.createFile(fileName, JSON.stringify(packageData, null, 2), 'ContentPackage');

    const newPackage: ContentPackageFile = {
      name: packageData.meta.name,
      path: filePath,
      meta: packageData.meta,
      banner_base64: packageData.banner_base64
    };

    packageList.value.push(newPackage);
    closeCreateDialog();
    message.success(t('contentPackage.messages.createSuccess'));
    selectPackage(newPackage);
  } catch (error) {
    if (error && typeof error === 'object' && 'errors' in error) {
      return;
    }
    console.error('创建内容包失败:', error);
    message.error(t('contentPackage.messages.createFailed'));
  } finally {
    creating.value = false;
  }
};

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreatePackageDialog.value = false;
  newPackageForm.value = {
    name: '',
    description: '',
    author: '',
    language: 'zh',
    types: [],
    external_link: '',
    banner_url: '',
    banner_base64: ''
  };
  createFormRef.value?.restoreValidation();
};

// 保存内容包
const savePackage = async () => {
  if (!selectedPackage.value) return;

  saving.value = true;
  try {
    const packageData: ContentPackage = {
      meta: selectedPackage.value.meta,
      banner_base64: selectedPackage.value.banner_base64
    };

    await WorkspaceService.saveFileContent(
      selectedPackage.value.path,
      JSON.stringify(packageData, null, 2)
    );

    message.success(t('contentPackage.messages.saveSuccess'));
  } catch (error) {
    console.error('保存内容包失败:', error);
    message.error(t('contentPackage.messages.saveFailed'));
  } finally {
    saving.value = false;
  }
};

// 显示删除确认对话框
const showDeleteConfirm = (pkg: ContentPackageFile) => {
  packageToDelete.value = pkg;
  showDeleteDialog.value = true;
};

// 确认删除内容包
const confirmDeletePackage = async () => {
  if (!packageToDelete.value) return;

  deleting.value = true;
  try {
    await WorkspaceService.deleteItem(packageToDelete.value.path);

    const index = packageList.value.findIndex(p => p.path === packageToDelete.value!.path);
    if (index > -1) {
      packageList.value.splice(index, 1);
    }

    if (selectedPackage.value?.path === packageToDelete.value.path) {
      selectedPackage.value = null;
    }

    showDeleteDialog.value = false;
    packageToDelete.value = null;
    message.success(t('contentPackage.messages.deleteSuccess'));
  } catch (error) {
    console.error('删除内容包失败:', error);
    message.error(t('contentPackage.messages.deleteFailed'));
  } finally {
    deleting.value = false;
  }
};

// 键盘快捷键处理
const handleKeydown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.code === 'KeyS') {
    event.preventDefault();
    if (selectedPackage.value && !saving.value) {
      savePackage();
    }
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadPackages();
  document.addEventListener('keydown', handleKeydown);
});

// 组件卸载时清理
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.content-package-manager-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.package-manager-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  height: 48px;
}

.package-manager-header h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.1;
}

.header-actions .n-button {
  height: 32px;
}

.package-manager-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.package-list-panel {
  width: 320px;
  background: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  flex-shrink: 0;
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

.package-list {
  flex: 1;
  min-height: 0;
  padding: 0.5rem;
}

.package-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.5rem;
  position: relative;
  border: 1px solid transparent;
}

.package-item:hover {
  background: #f8f9fa;
  border-color: #e9ecef;
}

.package-item.active {
  background: linear-gradient(135deg, #e3f2fd 0%, #e8f5e8 100%);
  border-left: 3px solid #667eea;
  border-color: #667eea;
}

.package-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.package-info {
  flex: 1;
  min-width: 0;
}

.package-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.package-meta {
  font-size: 0.75rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.author {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.7rem;
}

.no-package-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  margin: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* 表单对话框样式 */
.n-modal .n-form {
  max-height: 70vh;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

/* 隐藏滚动条 - Webkit浏览器 */
.n-modal .n-form::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

/* 上传区域样式 */
.n-upload-dragger {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  background: #fafafa;
  transition: all 0.3s;
}

.n-upload-dragger:hover {
  border-color: #667eea;
  background: #f0f8ff;
}

/* 封面上传容器 */
.banner-upload-container {
  width: 100%;
}

.banner-upload-container .n-upload {
  width: 100%;
}

.upload-area {
  width: 100%;
}

.upload-area .n-upload {
  width: 100%;
}

/* 封面预览 */
.banner-preview {
  position: relative;
  width: 100%;
  max-width: 400px;
  height: 225px; /* 16:9 比例 */
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e9ecef;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.banner-preview:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-preview-overlay {
  position: absolute;
  top: 0;
  right: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.5);
  border-bottom-left-radius: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  gap: 8px;
}

.banner-preview:hover .banner-preview-overlay {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .package-list-panel {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .package-manager-content {
    flex-direction: column;
  }

  .package-list-panel {
    width: 100%;
    max-height: 300px;
  }

  .package-list {
    padding: 0.25rem;
  }

  .package-item {
    padding: 0.75rem;
    margin-bottom: 0.25rem;
  }

  .package-icon {
    font-size: 1.25rem;
    margin-right: 0.75rem;
  }
}

/* 动画效果 */
.package-item {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 滚动条样式 */
.n-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.n-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.n-scrollbar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.n-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

<template>
  <div class="file-tree-pane" :style="{ width: width + 'px' }">
    <div class="pane-header">
      <n-space align="center" justify="space-between">
        <n-space align="center" size="small">
          <n-button size="tiny" quaternary @click="$emit('go-back')" class="header-button">
            <n-icon :component="ArrowBackOutline" />
          </n-button>
          <span class="pane-title">{{ $t('workspaceMain.fileTree.title') }}</span>
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
        <n-tree v-if="fileTreeData && fileTreeData.length > 0" :data="fileTreeData" :render-label="renderTreeLabel"
          :render-prefix="renderTreePrefix" selectable expand-on-click @update:selected-keys="handleFileSelect" />
        <n-empty v-else :description="$t('workspaceMain.fileTree.emptyText')" />
      </n-spin>
    </div>

    <!-- 右键菜单 -->
    <n-dropdown placement="bottom-start" trigger="manual" :x="contextMenuX" :y="contextMenuY"
      :options="contextMenuOptions" :show="showContextMenu" @clickoutside="showContextMenu = false"
      @select="handleContextMenuSelect" />

    <!-- 新建文件夹对话框 -->
    <n-modal v-model:show="showCreateFolderDialog">
      <n-card style="width: 90vw; max-width: 400px" :title="$t('workspaceMain.fileTree.createFolder.title')" :bordered="false"
        size="huge" role="dialog" aria-modal="true">
        <n-form ref="createFolderFormRef" :model="createFolderForm" :rules="createFolderRules">
          <n-form-item path="name" :label="$t('workspaceMain.fileTree.createFolder.label')">
            <n-input v-model:value="createFolderForm.name"
              :placeholder="$t('workspaceMain.fileTree.createFolder.placeholder')" @keydown.enter="handleCreateFolder"
              clearable />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCreateFolderDialog = false">{{ $t('workspaceMain.fileTree.createFolder.cancel')
            }}</n-button>
            <n-button type="primary" @click="handleCreateFolder" :loading="creating">{{
              $t('workspaceMain.fileTree.createFolder.confirm') }}</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 新建卡牌对话框 -->
    <n-modal v-model:show="showCreateCardDialog">
      <n-card style="width: 90vw; max-width: 400px" :title="$t('workspaceMain.fileTree.createCard.title')" :bordered="false" size="huge"
        role="dialog" aria-modal="true">
        <n-form ref="createCardFormRef" :model="createCardForm" :rules="createCardRules">
          <n-form-item path="name" :label="$t('workspaceMain.fileTree.createCard.label')">
            <n-input v-model:value="createCardForm.name"
              :placeholder="$t('workspaceMain.fileTree.createCard.placeholder')" @keydown.enter="handleCreateCard"
              clearable />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCreateCardDialog = false">{{ $t('workspaceMain.fileTree.createCard.cancel')
            }}</n-button>
            <n-button type="primary" @click="handleCreateCard" :loading="creating">{{
              $t('workspaceMain.fileTree.createCard.confirm') }}</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 重命名对话框 -->
    <n-modal v-model:show="showRenameDialog">
      <n-card style="width: 90vw; max-width: 450px" :title="$t('workspaceMain.fileTree.rename.title')" :bordered="false" size="huge"
        role="dialog" aria-modal="true">
        <n-form ref="renameFormRef" :model="renameForm" :rules="renameRules">
          <n-form-item path="filename" :label="$t('workspaceMain.fileTree.rename.filenameLabel')">
            <n-input v-model:value="renameForm.filename"
              :placeholder="$t('workspaceMain.fileTree.rename.filenamePlaceholder')" clearable />
          </n-form-item>
          <n-form-item path="extension" :label="$t('workspaceMain.fileTree.rename.extensionLabel')"
            v-if="showExtensionField">
            <n-input v-model:value="renameForm.extension"
              :placeholder="$t('workspaceMain.fileTree.rename.extensionPlaceholder')" clearable>
              <template #prefix>.</template>
            </n-input>
          </n-form-item>
          <n-space vertical size="small">
            <n-text depth="3" style="font-size: 12px;">
              {{ $t('workspaceMain.fileTree.rename.preview') }} {{ renamePreview }}
            </n-text>
          </n-space>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showRenameDialog = false">{{ $t('workspaceMain.fileTree.rename.cancel') }}</n-button>
            <n-button type="primary" @click="handleRename" :loading="renaming">{{
              $t('workspaceMain.fileTree.rename.confirm') }}</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal v-model:show="showDeleteDialog">
      <n-card style="width: 90vw; max-width: 450px" :title="$t('workspaceMain.fileTree.delete.title')" :bordered="false" size="huge"
        role="dialog" aria-modal="true">
        <n-space vertical>
          <n-alert type="warning" :title="$t('workspaceMain.fileTree.delete.warning')">
            <template #icon>
              <n-icon :component="WarningOutline" />
            </template>
            {{ $t('workspaceMain.fileTree.delete.confirmText') }}
          </n-alert>
          <n-space vertical size="small">
            <p><strong>{{ deleteConfirmText }}</strong></p>
            <p style="color: #666; font-size: 12px;">
              {{ $t('workspaceMain.fileTree.delete.pathLabel') }} {{ contextMenuTarget?.path }}
            </p>
          </n-space>
        </n-space>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showDeleteDialog = false">{{ $t('workspaceMain.fileTree.delete.cancel') }}</n-button>
            <n-button type="error" @click="handleDelete" :loading="deleting">{{
              $t('workspaceMain.fileTree.delete.confirm') }}</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 快速批量导出进度对话框 -->
    <n-modal v-model:show="showBatchExportDialog">
      <n-card style="width: 95vw; max-width: 600px" :title="$t('workspaceMain.fileTree.quickExport.title')" :bordered="false" size="huge"
        role="dialog" aria-modal="true">
        <n-space vertical size="large">
          <n-space vertical size="small">
            <n-text depth="3">{{ $t('workspaceMain.fileTree.quickExport.directory') }}: {{ batchExportTarget?.path
            }}</n-text>
            <n-text depth="3">{{ $t('workspaceMain.fileTree.quickExport.foundCards') }}: {{ batchExportCards.length
            }}</n-text>
            <n-text depth="3">{{ $t('workspaceMain.fileTree.quickExport.cpuCores') }}: {{ cpuCores }}</n-text>
            <n-text depth="3">{{ $t('workspaceMain.fileTree.quickExport.activeThreads') }}: {{ activeThreads }}</n-text>
          </n-space>

          <n-progress v-if="batchExporting" type="line" :percentage="batchExportProgress" :show-indicator="true"
            status="active" :stroke-width="8" :color="'#667eea'" />

          <div class="batch-export-status">
            <n-text v-if="batchExporting" style="font-weight: 600;">
              {{ $t('workspaceMain.fileTree.quickExport.processing') }}
            </n-text>
            <n-text v-if="batchExporting" depth="3" style="font-size: 12px; margin-top: 4px;">
              {{ $t('workspaceMain.fileTree.quickExport.progress.detail') }}: {{ batchExportedCount }} / {{
                batchExportCards.length }} ({{ batchExportProgress }}%)
            </n-text>
            <n-text v-else-if="batchExportCompleted">
              {{ $t('workspaceMain.fileTree.quickExport.completed') }}
            </n-text>

            <!-- 并发处理状态显示 -->
            <div v-if="batchExporting && activeExportTasks.length > 0" class="concurrent-status">
              <n-text depth="3" style="font-size: 12px; margin-top: 8px;">
                {{ $t('workspaceMain.fileTree.quickExport.currentTasks') }}
              </n-text>
              <div class="active-tasks">
                <n-tag v-for="task in activeExportTasks" :key="task.cardPath" size="small" type="info"
                  style="margin: 2px;">
                  {{ task.cardName }}
                </n-tag>
              </div>
            </div>
          </div>

          <!-- 导出日志 -->
          <div v-if="batchExportLogs.length > 0" class="export-logs">
            <n-text depth="3" style="font-size: 12px;">{{ $t('workspaceMain.fileTree.quickExport.logs') }}</n-text>
            <n-scrollbar style="max-height: 200px; margin-top: 8px;">
              <div class="log-content">
                <div v-for="(log, index) in batchExportLogs" :key="index" class="log-item" :class="log.type">
                  <n-text :type="log.type === 'error' ? 'error' : log.type === 'warning' ? 'warning' : 'success'">
                    {{ log.message }}
                  </n-text>
                </div>
              </div>
            </n-scrollbar>
          </div>
        </n-space>

        <template #footer>
          <n-space justify="end">
            <n-button v-if="!batchExporting && !batchExportCompleted" @click="showBatchExportDialog = false">
              {{ $t('workspaceMain.fileTree.quickExport.cancel') }}
            </n-button>
            <n-button v-if="batchExporting" @click="stopBatchExport" type="error">
              {{ $t('workspaceMain.fileTree.quickExport.stop') }}
            </n-button>
            <n-button v-if="!batchExporting && !batchExportCompleted" type="primary" @click="startBatchExport"
              :disabled="batchExportCards.length === 0">
              {{ $t('workspaceMain.fileTree.quickExport.start') }}
            </n-button>
            <n-button v-if="batchExportCompleted" type="primary" @click="closeBatchExportDialog">
              {{ $t('workspaceMain.fileTree.quickExport.close') }}
            </n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- 高级导出对话框 -->
    <n-modal v-model:show="showAdvancedExportDialog">
      <n-card style="width: 95vw; max-width: 800px" :title="$t('workspaceMain.fileTree.advancedExport.title')" :bordered="false"
        size="huge" role="dialog" aria-modal="true">
        <n-space vertical size="medium">
          <!-- 基本信息 -->
          <n-space vertical size="small">
            <n-text depth="3" style="font-weight: 600; font-size: 14px;">{{
              $t('workspaceMain.fileTree.advancedExport.exportInfo') }}</n-text>
            <n-text depth="3" style="font-size: 12px;">
              {{ advancedExportTarget?.type === 'directory' ? $t('workspaceMain.fileTree.advancedExport.directory') :
                $t('workspaceMain.fileTree.advancedExport.card') }}: {{ advancedExportTarget?.path }}
            </n-text>
            <n-text v-if="advancedExportTarget?.type === 'directory'" depth="3" style="font-size: 12px;">
              {{ $t('workspaceMain.fileTree.advancedExport.foundCards') }}: {{ advancedExportCards.length }} {{
                $t('workspaceMain.fileTree.advancedExport.sheets') }}
            </n-text>
          </n-space>

          <!-- 导出参数设置 -->
          <!-- 导出参数设置 -->
          <n-form :model="advancedExportParams" label-placement="left" label-width="auto" size="small">
            <n-grid :cols="2" :x-gap="16" :y-gap="12">
              <!-- 第一行 -->
              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.format.label')">
                  <n-select v-model:value="advancedExportParams.format" :options="formatOptions" size="small" />
                </n-form-item>
              </n-grid-item>

              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.quality.label')"
                  v-if="advancedExportParams.format === 'JPG'">
                  <n-select v-model:value="advancedExportParams.quality" :options="qualityOptions" size="small" />
                </n-form-item>
              </n-grid-item>

              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.size.label')">
                  <n-select v-model:value="advancedExportParams.size" :options="sizeOptions" size="small" />
                </n-form-item>
              </n-grid-item>

              <!-- 第二行 -->
              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.dpi.label')">
                  <n-select v-model:value="advancedExportParams.dpi" :options="dpiOptions" size="small" />
                </n-form-item>
              </n-grid-item>



              <!-- 第三行 -->
              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.bleed.label')">
                  <n-select v-model:value="advancedExportParams.bleed" :options="bleedOptions" size="small" />
                </n-form-item>
              </n-grid-item>

              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.bleedMode.label')">
                  <n-select v-model:value="advancedExportParams.bleed_mode" :options="bleedModeOptions" size="small" />
                </n-form-item>
              </n-grid-item>

              <!-- 第四行 - 出血模型（跨列显示） -->
              <n-grid-item :span="2">
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.bleedModel.label')">
                  <n-select v-model:value="advancedExportParams.bleed_model" :options="bleedModelOptions"
                    size="small" />
                </n-form-item>
                <!-- Lama模型提示 -->
                <n-alert v-if="advancedExportParams.bleed_model === 'LaMa模型出血'" type="info" size="small"
                  style="margin-top: 8px;">
                  <template #icon>
                    <n-icon :component="SettingsOutline" />
                  </template>
                  <n-text style="font-size: 12px;">
                    {{ $t('workspaceMain.fileTree.advancedExport.lamaGuide.text') }}
                    <n-button text tag="a"
                      href="https://github.com/xziying44/arkham-homebrew/blob/v2/export_helper/INSTALL_zh-CN.md"
                      target="_blank" style="font-size: 12px; padding: 0; margin-left: 4px;">
                      {{ $t('workspaceMain.fileTree.advancedExport.lamaGuide.link') }}
                    </n-button>
                  </n-text>
                </n-alert>
              </n-grid-item>

            </n-grid>

            <!-- 滑动条控件 - 独立的一行 -->
            <n-grid :cols="3" :x-gap="16" :y-gap="12" style="margin-top: 16px;">
              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.saturation.label')">
                  <n-space vertical size="small" style="width: 100%;">
                    <n-slider v-model:value="advancedExportParams.saturation" :min="0" :max="2" :step="0.1" />
                    <n-input-number v-model:value="advancedExportParams.saturation" :min="0" :max="2" :step="0.01"
                      :precision="2" size="small" style="width: 100%;" />
                  </n-space>
                </n-form-item>
              </n-grid-item>

              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.brightness.label')">
                  <n-space vertical size="small" style="width: 100%;">
                    <n-slider v-model:value="advancedExportParams.brightness" :min="0" :max="2" :step="0.1" />
                    <n-input-number v-model:value="advancedExportParams.brightness" :min="0" :max="2" :step="0.01"
                      :precision="2" size="small" style="width: 100%;" />
                  </n-space>
                </n-form-item>
              </n-grid-item>

              <n-grid-item>
                <n-form-item :label="$t('workspaceMain.fileTree.advancedExport.gamma.label')">
                  <n-space vertical size="small" style="width: 100%;">
                    <n-slider v-model:value="advancedExportParams.gamma" :min="0" :max="2" :step="0.1" />
                    <n-input-number v-model:value="advancedExportParams.gamma" :min="0" :max="2" :step="0.01"
                      :precision="2" size="small" style="width: 100%;" />
                  </n-space>
                </n-form-item>
              </n-grid-item>
            </n-grid>
          </n-form>



          <!-- 导出进度 -->
          <div v-if="advancedExporting || advancedExportCompleted" class="advanced-export-progress">
            <n-progress v-if="advancedExporting" type="line" :percentage="advancedExportProgress" :show-indicator="true"
              status="active" :stroke-width="6" />

            <n-text v-if="advancedExporting" style="font-size: 12px; margin-top: 8px;">
              {{ $t('workspaceMain.fileTree.advancedExport.progress.exporting', {
                current: advancedExportedCount, total:
                  advancedExportCards.length
              }) }}
            </n-text>

            <n-text v-if="advancedExportCompleted" type="success" style="font-weight: 600;">
              {{ $t('workspaceMain.fileTree.advancedExport.progress.completed') }}
            </n-text>
          </div>

          <!-- 导出日志 -->
          <div v-if="advancedExportLogs.length > 0" class="export-logs">
            <n-text depth="3" style="font-size: 12px;">{{ $t('workspaceMain.fileTree.advancedExport.logs') }}</n-text>
            <n-scrollbar style="max-height: 120px; margin-top: 8px;">
              <div class="log-content">
                <div v-for="(log, index) in advancedExportLogs" :key="index" class="log-item" :class="log.type">
                  <n-text :type="log.type === 'error' ? 'error' : log.type === 'warning' ? 'warning' : 'success'"
                    style="font-size: 11px;">
                    {{ log.message }}
                  </n-text>
                </div>
              </div>
            </n-scrollbar>
          </div>
        </n-space>

        <template #footer>
          <n-space justify="end">
            <n-button v-if="!advancedExporting && !advancedExportCompleted" @click="showAdvancedExportDialog = false">
              {{ $t('workspaceMain.fileTree.advancedExport.cancel') }}
            </n-button>
            <n-button v-if="advancedExporting" @click="stopAdvancedExport" type="error">
              {{ $t('workspaceMain.fileTree.advancedExport.stop') }}
            </n-button>
            <n-button v-if="!advancedExporting && !advancedExportCompleted" type="primary" @click="startAdvancedExport"
              :disabled="advancedExportCards.length === 0">
              {{ $t('workspaceMain.fileTree.advancedExport.start') }}
            </n-button>
            <n-button v-if="advancedExportCompleted" type="primary" @click="closeAdvancedExportDialog">
              {{ $t('workspaceMain.fileTree.advancedExport.close') }}
            </n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- ArkhamDB导入警告对话框 -->
    <n-modal v-model:show="showArkhamDBImportDialog">
      <n-card style="width: 90vw; max-width: 500px" :title="$t('arkhamdbImport.title')" :bordered="false" size="huge"
        role="dialog" aria-modal="true">
        <n-space vertical size="large">
          <n-alert type="warning" :title="$t('arkhamdbImport.actions.import')">
            <template #icon>
              <n-icon :component="WarningOutline" />
            </template>
            {{ $t('arkhamdbImport.importWarning') }}
          </n-alert>

          <n-space vertical size="small">
            <n-text depth="3">{{ $t('arkhamdbImport.fileInfo.name') }}: {{ arkhamdbImportTarget?.label }}</n-text>
            <n-text depth="3">{{ $t('arkhamdbImport.targetDirectory.title') }}: {{ fileTreeData[0]?.label }}</n-text>
          </n-space>

          <n-space vertical size="small">
            <n-text strong>{{ $t('arkhamdbImport.importConfirm.title') }}</n-text>
            <n-text depth="2">{{ $t('arkhamdbImport.importConfirm.warning1') }}</n-text>
            <n-text depth="2">{{ $t('arkhamdbImport.importConfirm.warning2') }}</n-text>
            <n-text depth="2">{{ $t('arkhamdbImport.importConfirm.warning3') }}</n-text>
          </n-space>
        </n-space>

        <template #footer>
          <n-space justify="end">
            <n-button @click="showArkhamDBImportDialog = false">{{ $t('arkhamdbImport.actions.cancel') }}</n-button>
            <n-button type="warning" @click="confirmArkhamDBImport">{{ $t('arkhamdbImport.actions.import') }}</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

    <!-- ArkhamDB导入进度对话框 -->
    <n-modal v-model:show="showArkhamDBProgressDialog" :mask-closable="false">
      <n-card style="width: 95vw; max-width: 700px" :title="$t('arkhamdbImport.importResult.title')" :bordered="false" size="huge"
        role="dialog" aria-modal="true">
        <n-space vertical size="large">
          <!-- 导入状态 -->
          <n-space vertical size="small">
            <n-text v-if="arkhamdbImporting" style="font-weight: 600;">
              {{ $t('arkhamdbImport.importing') }}
            </n-text>
            <n-text v-else-if="arkhamdbImportCompleted" type="success" style="font-weight: 600;">
              {{ $t('arkhamdbImport.importCompleted') }}
            </n-text>
          </n-space>

          <!-- 导入结果信息 -->
          <div v-if="arkhamdbImportResult" class="import-result-info">
            <n-space vertical size="small">
              <n-text>{{ $t('arkhamdbImport.importResult.success', { count: arkhamdbImportResult.saved_count }) }}</n-text>
              <n-text>{{ $t('arkhamdbImport.importResult.totalCards') }}: {{ arkhamdbImportResult.total_cards }}</n-text>
              <n-text>{{ $t('arkhamdbImport.importResult.language') }}: {{ arkhamdbImportResult.language }}</n-text>
              <n-text>{{ $t('arkhamdbImport.importResult.targetDirectory') }}: {{ arkhamdbImportResult.work_dir }}</n-text>
            </n-space>

            <!-- 示例卡牌已隐藏，用户可以直接在文件树中查看导入的卡牌 -->
          </div>

          <!-- 导入日志 -->
          <div class="import-logs">
            <n-space justify="space-between" align="center">
              <n-text depth="3" style="font-weight: 600;">{{ $t('arkhamdbImport.importResult.logs') }}</n-text>
              <n-button size="tiny" @click="refreshImportLogs">
                <template #icon>
                  <n-icon :component="RefreshOutline" />
                </template>
                {{ $t('arkhamdbImport.actions.refresh') }}
              </n-button>
            </n-space>
            <n-scrollbar ref="arkhamdbLogScrollbar" style="max-height: 300px; margin-top: 8px;">
              <div class="log-content" ref="arkhamdbLogContent">
                <div v-if="arkhamdbImportLogs.length === 0" class="log-item">
                  <n-text depth="3">{{ $t('arkhamdbImport.noLogs') }}</n-text>
                </div>
                <div v-for="(log, index) in arkhamdbImportLogs" :key="index" class="log-item">
                  <n-text style="font-size: 12px; font-family: monospace; white-space: pre-wrap;">{{ log }}</n-text>
                </div>
              </div>
            </n-scrollbar>
          </div>
        </n-space>

        <template #footer>
          <n-space justify="end">
            <n-button v-if="arkhamdbImporting" type="error" @click="stopArkhamDBImport">
              {{ $t('arkhamdbImport.stopImport') }}
            </n-button>
            <n-button v-else type="primary" @click="closeArkhamDBImportDialog">
              {{ $t('arkhamdbImport.close') }}
            </n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>

  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted, computed, nextTick, onUnmounted } from 'vue';
import { NIcon, useMessage, NText, NTag } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import type { TreeOption, FormInst, FormRules } from 'naive-ui';

// 扩展TreeOption接口以支持卡牌类型
interface ExtendedTreeOption extends TreeOption {
  card_type?: string; // 卡牌类型
}
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
import { WorkspaceService, ApiError, CardService, TtsExportService, ArkhamDBService } from '@/api';
import type { CardData, ExportCardParams, ArkhamDBContentPack } from '@/api/types';

interface Props {
  width: number;
}

defineProps<Props>();

const emit = defineEmits<{
  'toggle': [];
  'go-back': [];
  'file-select': [keys: Array<string | number>, option?: TreeOption];
  'refresh-file-tree': [];
}>();

const { t } = useI18n();
const message = useMessage();

// 获取CPU核心数
const cpuCores = ref(navigator.hardwareConcurrency || 4);
const activeThreads = ref(Math.min(cpuCores.value, 4)); // 限制最大并发数为4

// 状态管理
const loading = ref(false);
const creating = ref(false);
const renaming = ref(false);
const deleting = ref(false);

// 复制粘贴相关状态
const copiedFile = ref<{ path: string; name: string; content: string } | null>(null);

// 批量导出相关状态（快速导出）
const showBatchExportDialog = ref(false);
const batchExporting = ref(false);
const batchExportCompleted = ref(false);
const batchExportTarget = ref<TreeOption | null>(null);
const batchExportCards = ref<string[]>([]);
const batchExportedCount = ref(0);
const batchExportProgress = ref(0);
const batchExportLogs = ref<{ type: 'success' | 'error' | 'warning', message: string }[]>([]);
const batchExportAborted = ref(false);

// 多线程并发相关状态（快速导出）
const activeExportTasks = ref<{ cardPath: string, cardName: string }[]>([]);
const exportQueue = ref<string[]>([]);
const completedTasks = ref(0);

// 高级导出相关状态
const showAdvancedExportDialog = ref(false);
const advancedExporting = ref(false);
const advancedExportCompleted = ref(false);
const advancedExportTarget = ref<TreeOption | null>(null);
const advancedExportCards = ref<string[]>([]);
const advancedExportedCount = ref(0);
const advancedExportProgress = ref(0);
const advancedExportLogs = ref<{ type: 'success' | 'error' | 'warning', message: string }[]>([]);
const advancedExportAborted = ref(false);

// 高级导出参数
const advancedExportParams = ref<ExportCardParams>({
  format: 'PNG',
  quality: 95,
  size: '63.5mm × 88.9mm (2.5″ × 3.5″)',
  dpi: 300,
  bleed: 2,
  bleed_mode: '裁剪',
  bleed_model: '镜像出血',
  saturation: 1.0,
  brightness: 1.0,
  gamma: 1.0
});

// 高级导出参数选项
const formatOptions = computed(() => [
  { label: t('workspaceMain.fileTree.advancedExport.format.png'), value: 'PNG' },
  { label: t('workspaceMain.fileTree.advancedExport.format.jpg'), value: 'JPG' }
]);

const qualityOptions = computed(() => [
  { label: t('workspaceMain.fileTree.advancedExport.quality.recommended'), value: 95 },
  { label: '90%', value: 90 },
  { label: '85%', value: 85 },
  { label: '80%', value: 80 },
  { label: '75%', value: 75 },
  { label: '70%', value: 70 },
  { label: t('workspaceMain.fileTree.advancedExport.quality.highest'), value: 100 }
]);

const sizeOptions = computed(() => [
  { label: '61mm × 88mm', value: '61mm × 88mm' },
  { label: '61.5mm × 88mm', value: '61.5mm × 88mm' },
  { label: '62mm × 88mm', value: '62mm × 88mm' },
  { label: t('workspaceMain.fileTree.advancedExport.size.standard'), value: '63.5mm × 88.9mm (2.5″ × 3.5″)' }
]);

const dpiOptions = [
  { label: '150 DPI', value: 150 },
  { label: '200 DPI', value: 200 },
  { label: '300 DPI', value: 300 },
  { label: '350 DPI', value: 350 },
  { label: '400 DPI', value: 400 },
  { label: '450 DPI', value: 450 },
  { label: '500 DPI', value: 500 },
  { label: '600 DPI', value: 600 },
  { label: '1200 DPI', value: 1200 }
];


const bleedOptions = computed(() => [
  { label: t('workspaceMain.fileTree.advancedExport.bleed.none'), value: 0 },
  { label: t('workspaceMain.fileTree.advancedExport.bleed.standard'), value: 2 },
  { label: t('workspaceMain.fileTree.advancedExport.bleed.enhanced'), value: 3 }
]);

const bleedModeOptions = computed(() => [
  { label: t('workspaceMain.fileTree.advancedExport.bleedMode.crop'), value: '裁剪' },
  { label: t('workspaceMain.fileTree.advancedExport.bleedMode.stretch'), value: '拉伸' }
]);

const bleedModelOptions = computed(() => [
  { label: t('workspaceMain.fileTree.advancedExport.bleedModel.mirror'), value: '镜像出血' },
  { label: t('workspaceMain.fileTree.advancedExport.bleedModel.lama'), value: 'LaMa模型出血' }
]);


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
const showArkhamDBImportDialog = ref(false);
const showArkhamDBProgressDialog = ref(false);

// ArkhamDB导入相关状态
const arkhamdbImporting = ref(false);
const arkhamdbImportCompleted = ref(false);
const arkhamdbImportLogs = ref<string[]>([]);
const arkhamdbImportTarget = ref<TreeOption | null>(null);
const arkhamdbImportContent = ref<ArkhamDBContentPack | null>(null);
const arkhamdbImportResult = ref<any>(null);
const logRefreshInterval = ref<NodeJS.Timeout | null>(null);

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

// ArkhamDB日志滚动条引用
const arkhamdbLogScrollbar = ref<any>(null);
const arkhamdbLogContent = ref<HTMLElement | null>(null);

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
const createFolderRules = computed((): FormRules => ({
  name: [
    { required: true, message: t('workspaceMain.fileTree.validation.folderNameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: t('workspaceMain.fileTree.validation.folderNameLength'), trigger: ['input', 'blur'] },
    {
      pattern: /^[^\\/:*?"<>|]+$/,
      message: t('workspaceMain.fileTree.validation.folderNameInvalid'),
      trigger: ['input', 'blur']
    }
  ]
}));

const createCardRules = computed((): FormRules => ({
  name: [
    { required: true, message: t('workspaceMain.fileTree.validation.cardNameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: t('workspaceMain.fileTree.validation.cardNameLength'), trigger: ['input', 'blur'] },
    {
      pattern: /^[^\\/:*?"<>|]+$/,
      message: t('workspaceMain.fileTree.validation.cardNameInvalid'),
      trigger: ['input', 'blur']
    }
  ]
}));

const renameRules = computed((): FormRules => ({
  filename: [
    { required: true, message: t('workspaceMain.fileTree.validation.filenameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 50, message: t('workspaceMain.fileTree.validation.filenameLength'), trigger: ['input', 'blur'] },
    {
      pattern: /^[^<>:"/\\|?*]*[^<>:"/\\|?* .]$/,
      message: t('workspaceMain.fileTree.validation.filenameInvalid'),
      trigger: ['input', 'blur']
    }
  ],
  extension: [
    {
      pattern: /^[^\\/:*?"<>|.]*$/,
      message: t('workspaceMain.fileTree.validation.extensionInvalid'),
      trigger: ['input', 'blur']
    }
  ]
}));

// 删除确认文本
const deleteConfirmText = computed(() => {
  if (!contextMenuTarget.value) return '';
  const isDirectory = contextMenuTarget.value.type === 'directory';
  const name = contextMenuTarget.value.label as string;
  const prefix = isDirectory ? t('workspaceMain.fileTree.delete.folderPrefix') : t('workspaceMain.fileTree.delete.filePrefix');
  return `${prefix} ${name}`;
});

// 创建选项
const createOptions = computed(() => [
  {
    label: t('workspaceMain.fileTree.contextMenu.newFolder'),
    key: 'folder',
    icon: () => h(NIcon, { component: FolderOutline })
  },
  {
    label: t('workspaceMain.fileTree.contextMenu.newCard'),
    key: 'card',
    icon: () => h(NIcon, { component: DocumentOutline })
  }
]);

// 右键菜单选项
const contextMenuOptions = computed(() => {
  if (!contextMenuTarget.value) return [];

  const isWorkspace = contextMenuTarget.value.type === 'workspace';
  const isDirectory = contextMenuTarget.value.type === 'directory';
  const isCard = contextMenuTarget.value.type === 'card';
  const isFile = !isWorkspace && !isDirectory;
  const isConfigFile = isFile && ['json', 'pack'].includes((contextMenuTarget.value.label as string).split('.').pop()?.toLowerCase() || '');

  const options = [];

  // 工作空间和目录可以创建子项
  if (isWorkspace || isDirectory) {
    options.push(
      {
        label: t('workspaceMain.fileTree.contextMenu.newFolder'),
        key: 'create-folder',
        icon: () => h(NIcon, { component: FolderOutline })
      },
      {
        label: t('workspaceMain.fileTree.contextMenu.newCard'),
        key: 'create-card',
        icon: () => h(NIcon, { component: DocumentOutline })
      }
    );

    // 为目录添加快速导出选项（原批量导出）
    options.push({
      label: t('workspaceMain.fileTree.contextMenu.quickExport'),
      key: 'batch-export',
      icon: () => h(NIcon, { component: ImageOutline })
    });

    // 为目录添加高级导出选项
    options.push({
      label: t('workspaceMain.fileTree.contextMenu.advancedExport'),
      key: 'advanced-export',
      icon: () => h(NIcon, { component: SettingsOutline })
    });

    // 为目录添加粘贴选项（如果有复制的内容）
    if (copiedFile.value && (isDirectory || isWorkspace)) {
      options.push({
        label: t('workspaceMain.fileTree.contextMenu.paste'),
        key: 'paste',
        icon: () => h(NIcon, { component: DocumentOutline })
      });
    }
  }

  // 为单个card文件添加复制和高级导出选项
  if (isCard) {
    options.push({
      label: t('workspaceMain.fileTree.contextMenu.copy'),
      key: 'copy',
      icon: () => h(NIcon, { component: DocumentOutline })
    });

    options.push({
      label: t('workspaceMain.fileTree.contextMenu.advancedExport'),
      key: 'advanced-export',
      icon: () => h(NIcon, { component: SettingsOutline })
    });
  }

  // 为JSON文件添加ArkhamDB导入选项
  if (isConfigFile) {
    options.push({
      label: t('arkhamdbImport.title'),
      key: 'arkhamdb-import',
      icon: () => h(NIcon, { component: DocumentOutline })
    });
  }

  // 非工作空间节点可以重命名和删除
  if (!isWorkspace) {
    if (options.length > 0) {
      options.push({ type: 'divider', key: 'divider1' });
    }
    options.push(
      {
        label: t('workspaceMain.fileTree.contextMenu.rename'),
        key: 'rename',
        icon: () => h(NIcon, { component: CreateOutline })
      },
      {
        label: t('workspaceMain.fileTree.contextMenu.delete'),
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
  if (['json', 'yml', 'yaml', 'toml', 'pack'].includes(extension)) return 'config';
  if (['csv', 'tsv', 'dat'].includes(extension)) return 'data';
  if (['css', 'scss', 'sass', 'less'].includes(extension)) return 'style';
  if (['txt', 'md', 'markdown'].includes(extension)) return 'text';

  return 'file';
};

// 转换API返回的文件树结构为组件所需格式
const convertFileTreeData = (node: any): ExtendedTreeOption => {
  const treeNode: ExtendedTreeOption = {
    label: node.label,
    key: node.key,
    type: node.type,
    path: node.path
  };

  // 保留card_type属性（如果存在）
  if (node.card_type) {
    treeNode.card_type = node.card_type;
  }

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
      message.error(`${t('workspaceMain.fileTree.messages.loadFailed')}: ${error.message}`);
    } else {
      message.error(t('workspaceMain.fileTree.messages.loadFailedNetwork'));
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

  // 基础文件类型图标映射
  const baseIconMap = {
    'workspace': { component: LayersOutline, color: '#667eea' },
    'directory': { component: FolderOpenOutline, color: '#ffa726' },
    'image': { component: ImageOutline, color: '#66bb6a' },
    'config': { component: GridOutline, color: '#ff7043' },
    'data': { component: GridOutline, color: '#ff7043' },
    'style': { component: SettingsOutline, color: '#ec407a' },
    'text': { component: DocumentOutline, color: '#8d6e63' },
    'file': { component: DocumentOutline, color: '#90a4ae' },
    'default': { component: DocumentOutline, color: '#90a4ae' }
  };

  // 卡牌类型图标映射
  const cardTypeIconMap = {
    '支援卡': { component: DocumentOutline, emoji: '📦' },
    '事件卡': { component: DocumentOutline, emoji: '⚡' },
    '技能卡': { component: DocumentOutline, emoji: '🎯' },
    '调查员': { component: DocumentOutline, emoji: '👤' },
    '调查员背面': { component: DocumentOutline, emoji: '🔄' },
    '定制卡': { component: DocumentOutline, emoji: '🎨' },
    '故事卡': { component: DocumentOutline, emoji: '📖' },
    '诡计卡': { component: DocumentOutline, emoji: '🎭' },
    '敌人卡': { component: DocumentOutline, emoji: '👹' },
    '地点卡': { component: DocumentOutline, emoji: '📍' },
    '密谋卡': { component: DocumentOutline, emoji: '🌙' },
    '密谋卡-大画': { component: DocumentOutline, emoji: '🌕' },
    '场景卡': { component: DocumentOutline, emoji: '🎬' },
    '场景卡-大画': { component: DocumentOutline, emoji: '🎞️' },
    '冒险参考卡': { component: DocumentOutline, emoji: '📋' }
  };

  // 如果是卡牌类型且有card_type属性
  if (option.type === 'card' && (option as ExtendedTreeOption).card_type) {
    const cardType = (option as ExtendedTreeOption).card_type as string;
    const cardIconConfig = cardTypeIconMap[cardType as keyof typeof cardTypeIconMap];

    if (cardIconConfig) {
      // 创建带emoji的图标
      return h('div', {
        style: {
          display: 'flex',
          alignItems: 'center',
          marginRight: '6px',
          fontSize: '14px'
        }
      }, [
        h('span', {
          style: {
            marginRight: '4px',
            fontSize: '12px'
          }
        }, cardIconConfig.emoji),
        h(NIcon, {
          component: cardIconConfig.component,
          color: '#42a5f5',
          size: 14
        })
      ]);
    }
  }

  // 普通卡牌类型（没有card_type属性的.card文件）
  if (option.type === 'card') {
    return h(NIcon, {
      component: DocumentOutline,
      color: '#42a5f5',
      size: 14,
      style: iconStyle
    });
  }

  // 其他文件类型
  const iconConfig = baseIconMap[option.type as keyof typeof baseIconMap] || baseIconMap.default;

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
    case 'batch-export':
      startBatchExportProcess();
      break;
    case 'advanced-export':
      startAdvancedExportProcess();
      break;
    case 'copy':
      handleCopy();
      break;
    case 'paste':
      handlePaste();
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
    case 'arkhamdb-import':
      startArkhamDBImportProcess();
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

    message.success(t('workspaceMain.fileTree.messages.createFolderSuccess'));
    showCreateFolderDialog.value = false;
    createFolderForm.value.name = '';
  } catch (error) {
    console.error('创建文件夹失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('workspaceMain.fileTree.messages.createFolderFailed')}: ${error.message}`);
    } else if (error.errors) {
      // 表单验证错误，不显示消息
    } else {
      message.error(t('workspaceMain.fileTree.messages.createFolderFailedRetry'));
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

    // 创建空的JSON对象（默认2.0版本用于双面卡牌）
    const defaultContent = '{"version": "2.0"}';

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

    message.success(t('workspaceMain.fileTree.messages.createCardSuccess'));
    showCreateCardDialog.value = false;
    createCardForm.value.name = '';
  } catch (error) {
    console.error('创建卡牌失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('workspaceMain.fileTree.messages.createCardFailed')}: ${error.message}`);
    } else if (error.errors) {
      // 表单验证错误，不显示消息
    } else {
      message.error(t('workspaceMain.fileTree.messages.createCardFailedRetry'));
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

    message.success(t('workspaceMain.fileTree.messages.renameSuccess'));
    showRenameDialog.value = false;
    renameForm.value.filename = '';
    renameForm.value.extension = '';
  } catch (error) {
    console.error('重命名失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('workspaceMain.fileTree.messages.renameFailed')}: ${error.message}`);
    } else if (error.errors) {
      // 表单验证错误，不显示消息
    } else {
      message.error(t('workspaceMain.fileTree.messages.renameFailedRetry'));
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

    message.success(t('workspaceMain.fileTree.messages.deleteSuccess'));
    showDeleteDialog.value = false;
  } catch (error) {
    console.error('删除失败:', error);
    if (error instanceof ApiError) {
      message.error(`${t('workspaceMain.fileTree.messages.deleteFailed')}: ${error.message}`);
    } else {
      message.error(t('workspaceMain.fileTree.messages.deleteFailedRetry'));
    }
  } finally {
    deleting.value = false;
  }
};

// 递归查找目录下的所有卡牌文件
const findAllCardFiles = async (directoryPath: string): Promise<string[]> => {
  try {
    // 通过API获取目录的完整文件树
    const fileTree = await WorkspaceService.getFileTree(false);

    const findCardsInNode = (node: any, targetPath: string): string[] => {
      const cards: string[] = [];

      if (node.path === targetPath && node.children) {
        // 找到目标目录，遍历其所有子项
        const traverseChildren = (children: any[]): string[] => {
          const result: string[] = [];
          for (const child of children) {
            if (child.type === 'card') {
              result.push(child.path);
            } else if (child.children) {
              result.push(...traverseChildren(child.children));
            }
          }
          return result;
        };
        return traverseChildren(node.children);
      }

      // 递归搜索子节点
      if (node.children) {
        for (const child of node.children) {
          cards.push(...findCardsInNode(child, targetPath));
        }
      }

      return cards;
    };

    return findCardsInNode(fileTree.fileTree, directoryPath);
  } catch (error) {
    console.error('获取目录下卡牌文件失败:', error);
    return [];
  }
};

// 开始快速批量导出流程
const startBatchExportProcess = async () => {
  if (!contextMenuTarget.value) return;

  try {
    batchExportTarget.value = contextMenuTarget.value;
    batchExportLogs.value = [];
    batchExportedCount.value = 0;
    batchExportProgress.value = 0;
    batchExportCompleted.value = false;
    batchExportAborted.value = false;
    activeExportTasks.value = [];
    exportQueue.value = [];
    completedTasks.value = 0;

    message.info(t('workspaceMain.fileTree.quickExport.scanning'));

    // 获取目录下所有卡牌文件
    batchExportCards.value = await findAllCardFiles(contextMenuTarget.value.path as string);

    if (batchExportCards.value.length === 0) {
      message.warning(t('workspaceMain.fileTree.quickExport.noCardsFound'));
      return;
    }

    // 根据卡牌数量调整并发数量
    activeThreads.value = Math.min(
      Math.max(1, Math.min(cpuCores.value, 4)),
      batchExportCards.value.length
    );

    showBatchExportDialog.value = true;

    addBatchExportLog('info', `${t('workspaceMain.fileTree.quickExport.foundCardsLog')}: ${batchExportCards.value.length} 张`);
    addBatchExportLog('info', `${t('workspaceMain.fileTree.quickExport.threadsLog')}: ${activeThreads.value}`);
  } catch (error) {
    console.error('扫描目录失败:', error);
    message.error(`${t('workspaceMain.fileTree.quickExport.scanFailed')}: ${error.message}`);
  }
};

// 快速导出单个卡牌任务
const exportCardTask = async (cardPath: string): Promise<{ success: boolean, cardName: string, error?: string }> => {
  const cardName = cardPath.split('/').pop()?.replace('.card', '') || `card_${Date.now()}`;

  try {
    // 添加到活动任务列表
    activeExportTasks.value.push({ cardPath, cardName });

    // 读取卡牌文件内容
    const content = await WorkspaceService.getFileContent(cardPath);
    const cardData = JSON.parse(content || '{}') as CardData;

    // 验证卡牌数据
    const validation = CardService.validateCardData(cardData);
    if (!validation.isValid) {
      throw new Error(`${t('workspaceMain.fileTree.quickExport.validationFailed')}: ${validation.errors.join(', ')}`);
    }

    // 导出图片到同目录
    const parentPath = cardPath.substring(0, cardPath.lastIndexOf('/'));
    const filename = `${cardName}.png`;

    await CardService.saveCard(cardData, filename, parentPath);

    return { success: true, cardName };
  } catch (error) {
    return { success: false, cardName, error: error.message };
  } finally {
    // 从活动任务列表中移除
    const index = activeExportTasks.value.findIndex(task => task.cardPath === cardPath);
    if (index > -1) {
      activeExportTasks.value.splice(index, 1);
    }
  }
};

// 多线程快速批量导出
const startBatchExport = async () => {
  if (batchExportCards.value.length === 0) return;

  batchExporting.value = true;
  batchExportedCount.value = 0;
  batchExportProgress.value = 0;
  batchExportCompleted.value = false;
  batchExportAborted.value = false;
  activeExportTasks.value = [];
  completedTasks.value = 0;

  // 初始化导出队
  exportQueue.value = [...batchExportCards.value];

  addBatchExportLog('info', t('workspaceMain.fileTree.quickExport.startLog'));
  addBatchExportLog('info', t('workspaceMain.fileTree.quickExport.usingThreads', { count: activeThreads.value }));

  let successCount = 0;
  let errorCount = 0;

  // 创建工作线程函数
  const worker = async (): Promise<void> => {
    while (exportQueue.value.length > 0 && !batchExportAborted.value) {
      const cardPath = exportQueue.value.shift();
      if (!cardPath) break;

      const result = await exportCardTask(cardPath);

      if (result.success) {
        successCount++;
        addBatchExportLog('success', t('workspaceMain.fileTree.quickExport.exportSuccess', { name: result.cardName }));
      } else {
        errorCount++;
        addBatchExportLog('error', t('workspaceMain.fileTree.quickExport.exportFailed', { name: result.cardName, error: result.error }));
      }

      // 更新进度
      completedTasks.value++;
      batchExportedCount.value = completedTasks.value;
      batchExportProgress.value = Math.round((completedTasks.value / batchExportCards.value.length) * 100);

      // 强制更新DOM
      await nextTick();
    }
  };

  try {
    // 启动多个并发工作线程
    const workers: Promise<void>[] = [];
    for (let i = 0; i < activeThreads.value; i++) {
      workers.push(worker());
    }

    // 等待所有工作线程完成
    await Promise.all(workers);

    batchExporting.value = false;
    batchExportCompleted.value = true;
    activeExportTasks.value = [];

    // 确保进度条显示100%
    batchExportProgress.value = 100;
    await nextTick();

    if (!batchExportAborted.value) {
      addBatchExportLog('success', t('workspaceMain.fileTree.quickExport.completedLog', { success: successCount, total: batchExportCards.value.length }));

      if (errorCount > 0) {
        addBatchExportLog('warning', t('workspaceMain.fileTree.quickExport.failedCount', { count: errorCount }));
      }

      // 批量导出完成后刷新文件树
      emit('refresh-file-tree');

      // 延迟显示成功消息，确保文件树刷新完成
      setTimeout(() => {
        if (successCount > 0) {
          message.success(t('workspaceMain.fileTree.quickExport.quickExportCompleted', { success: successCount, total: batchExportCards.value.length }));
        }
        if (errorCount > 0) {
          message.warning(t('workspaceMain.fileTree.quickExport.partialSuccess', { success: successCount, failed: errorCount }));
        }
      }, 500);
    }
  } catch (error) {
    console.error('快速批量导出过程中出现错误:', error);
    addBatchExportLog('error', `批量导出过程中出现错误: ${error.message}`);
    batchExporting.value = false;
    activeExportTasks.value = [];
  }
};

// 停止快速批量导出
const stopBatchExport = () => {
  batchExportAborted.value = true;
  exportQueue.value = []; // 清空队列
  addBatchExportLog('warning', t('workspaceMain.fileTree.quickExport.userStopped'));
  message.info(t('workspaceMain.fileTree.quickExport.stopping'));
};

// 关闭快速批量导出对话框
const closeBatchExportDialog = () => {
  showBatchExportDialog.value = false;
  batchExportTarget.value = null;
  batchExportCards.value = [];
  batchExportLogs.value = [];
  batchExportedCount.value = 0;
  batchExportProgress.value = 0;
  batchExportCompleted.value = false;
  batchExportAborted.value = false;
  activeExportTasks.value = [];
  exportQueue.value = [];
  completedTasks.value = 0;
};

// 添加快速导出日志
const addBatchExportLog = (type: 'success' | 'error' | 'warning' | 'info', message: string) => {
  batchExportLogs.value.push({
    type: type === 'info' ? 'success' : type,
    message: `[${new Date().toLocaleTimeString()}] ${message}`
  });
};

// 开始高级导出流程
const startAdvancedExportProcess = async () => {
  if (!contextMenuTarget.value) return;

  try {
    advancedExportTarget.value = contextMenuTarget.value;
    advancedExportLogs.value = [];
    advancedExportedCount.value = 0;
    advancedExportProgress.value = 0;
    advancedExportCompleted.value = false;
    advancedExportAborted.value = false;

    // 如果是单个card文件
    if (contextMenuTarget.value.type === 'card') {
      advancedExportCards.value = [contextMenuTarget.value.path as string];
    } else {
      // 如果是目录，扫描所有卡牌文件
      message.info(t('workspaceMain.fileTree.advancedExport.scanning'));
      advancedExportCards.value = await findAllCardFiles(contextMenuTarget.value.path as string);

      if (advancedExportCards.value.length === 0) {
        message.warning(t('workspaceMain.fileTree.advancedExport.noCardsFound'));
        return;
      }
    }

    showAdvancedExportDialog.value = true;
    addAdvancedExportLog('info', `${t('workspaceMain.fileTree.advancedExport.foundCardsLog')}: ${advancedExportCards.value.length} 张`);
  } catch (error) {
    console.error('准备高级导出失败:', error);
    message.error(`${t('workspaceMain.fileTree.advancedExport.prepareFailed')}: ${error.message}`);
  }
};

// 生成导出参数哈希值
const generateParamsHash = (params: ExportCardParams): string => {
  const paramString = JSON.stringify(params, Object.keys(params).sort());
  // 先用 encodeURIComponent 转换为 ASCII 安全的字符串
  const encodedString = encodeURIComponent(paramString);
  return btoa(encodedString).replace(/[+/=]/g, '');
};


// 高级导出单个卡牌
const advancedExportCard = async (cardPath: string): Promise<{ success: boolean, cardName: string, error?: string }> => {
  const cardName = cardPath.split('/').pop()?.replace('.card', '') || `card_${Date.now()}`;
  const paramsHash = generateParamsHash(advancedExportParams.value);

  try {
    // 构建导出文件名（不包含扩展名）
    const exportFilename = `${cardName}_advanced`;

    // 调用导出卡牌API
    await TtsExportService.exportCard(
      cardPath,
      exportFilename,
      advancedExportParams.value,
      paramsHash
    );

    return { success: true, cardName };
  } catch (error) {
    return { success: false, cardName, error: error.message || t('workspaceMain.fileTree.advancedExport.exportError') };
  }
};

// 开始高级导出（单线程）
const startAdvancedExport = async () => {
  if (advancedExportCards.value.length === 0) return;

  advancedExporting.value = true;
  advancedExportedCount.value = 0;
  advancedExportProgress.value = 0;
  advancedExportCompleted.value = false;
  advancedExportAborted.value = false;

  addAdvancedExportLog('info', t('workspaceMain.fileTree.advancedExport.startLog'));
  addAdvancedExportLog('info', t('workspaceMain.fileTree.advancedExport.paramsLog', {
    format: advancedExportParams.value.format,
    dpi: advancedExportParams.value.dpi,
    bleed: advancedExportParams.value.bleed
  }));

  let successCount = 0;
  let errorCount = 0;

  // 单线程顺序处理
  for (let i = 0; i < advancedExportCards.value.length && !advancedExportAborted.value; i++) {
    const cardPath = advancedExportCards.value[i];
    const result = await advancedExportCard(cardPath);

    if (result.success) {
      successCount++;
      addAdvancedExportLog('success', t('workspaceMain.fileTree.advancedExport.exportSuccess', { name: result.cardName }));
    } else {
      errorCount++;
      addAdvancedExportLog('error', t('workspaceMain.fileTree.advancedExport.exportFailed', { name: result.cardName, error: result.error }));
    }

    // 更新进度
    advancedExportedCount.value = i + 1;
    advancedExportProgress.value = Math.round(((i + 1) / advancedExportCards.value.length) * 100);

    // 强制更新DOM
    await nextTick();
  }

  advancedExporting.value = false;
  advancedExportCompleted.value = true;

  if (!advancedExportAborted.value) {
    addAdvancedExportLog('success', t('workspaceMain.fileTree.advancedExport.completedLog', { success: successCount, total: advancedExportCards.value.length }));

    if (errorCount > 0) {
      addAdvancedExportLog('warning', t('workspaceMain.fileTree.advancedExport.failedCount', { count: errorCount }));
    }

    // 高级导出完成后刷新文件树
    emit('refresh-file-tree');

    // 延迟显示成功消息
    setTimeout(() => {
      if (successCount > 0) {
        message.success(t('workspaceMain.fileTree.advancedExport.advancedExportCompleted', { success: successCount, total: advancedExportCards.value.length }));
      }
      if (errorCount > 0) {
        message.warning(t('workspaceMain.fileTree.advancedExport.partialSuccess', { success: successCount, failed: errorCount }));
      }
    }, 500);
  }
};

// 停止高级导出
const stopAdvancedExport = () => {
  advancedExportAborted.value = true;
  addAdvancedExportLog('warning', t('workspaceMain.fileTree.advancedExport.userStopped'));
  message.info(t('workspaceMain.fileTree.advancedExport.stopping'));
};

// 关闭高级导出对话框
const closeAdvancedExportDialog = () => {
  showAdvancedExportDialog.value = false;
  advancedExportTarget.value = null;
  advancedExportCards.value = [];
  advancedExportLogs.value = [];
  advancedExportedCount.value = 0;
  advancedExportProgress.value = 0;
  advancedExportCompleted.value = false;
  advancedExportAborted.value = false;

  // 重置高级导出参数为默认值
  advancedExportParams.value = {
    format: 'PNG',
    quality: 95,
    size: '63.5mm × 88.9mm (2.5″ × 3.5″)',
    dpi: 300,
    bleed: 2,
    bleed_mode: '裁剪',
    bleed_model: '镜像出血',
    saturation: 1.0,
    brightness: 1.0,
    gamma: 1.0
  };
};

// 添加高级导出日志
const addAdvancedExportLog = (type: 'success' | 'error' | 'warning' | 'info', message: string) => {
  advancedExportLogs.value.push({
    type: type === 'info' ? 'success' : type,
    message: `[${new Date().toLocaleTimeString()}] ${message}`
  });
};

// 处理复制功能
const handleCopy = async () => {
  if (!contextMenuTarget.value || contextMenuTarget.value.type !== 'card') {
    message.error(t('workspaceMain.fileTree.messages.copyFailed'));
    return;
  }

  try {
    const filePath = contextMenuTarget.value.path as string;
    const fileName = contextMenuTarget.value.label as string;
    
    // 读取文件内容
    const content = await WorkspaceService.getFileContent(filePath);
    
    // 保存到剪贴板状态
    copiedFile.value = {
      path: filePath,
      name: fileName,
      content: content || '{}'
    };
    
    message.success(t('workspaceMain.fileTree.messages.copySuccess'));
  } catch (error) {
    console.error('复制文件失败:', error);
    message.error(t('workspaceMain.fileTree.messages.copyFailed'));
  }
};

// 处理粘贴功能
const handlePaste = async () => {
  if (!copiedFile.value) {
    message.error(t('workspaceMain.fileTree.messages.pasteNoContent'));
    return;
  }

  if (!contextMenuTarget.value) {
    message.error(t('workspaceMain.fileTree.messages.pasteInvalidTarget'));
    return;
  }

  const isDirectory = contextMenuTarget.value.type === 'directory' || contextMenuTarget.value.type === 'workspace';
  if (!isDirectory) {
    message.error(t('workspaceMain.fileTree.messages.pasteInvalidTarget'));
    return;
  }

  try {
    const parentPath = contextMenuTarget.value.path;
    const originalName = copiedFile.value.name;
    
    // 生成新的文件名（避免重复）
    const newName = generateUniqueFileName(originalName, parentPath);
    
    // 创建新文件
    await WorkspaceService.createFile(newName, copiedFile.value.content, parentPath);
    
    // 构建新节点路径
    const newPath = parentPath ? `${parentPath}/${newName}` : newName;
    
    // 直接在文件树中添加新节点
    const newNode: TreeOption = {
      label: newName,
      key: newPath,
      type: 'card',
      path: newPath
    };
    
    addNodeToTree(fileTreeData.value, parentPath, newNode);
    
    message.success(t('workspaceMain.fileTree.messages.pasteSuccess'));
  } catch (error) {
    console.error('粘贴文件失败:', error);
    message.error(t('workspaceMain.fileTree.messages.pasteFailed'));
  }
};

// 生成唯一文件名（避免重复）
const generateUniqueFileName = (originalName: string, parentPath?: string): string => {
  // 检查目标目录中是否已存在同名文件
  const checkIfFileExists = (fileName: string): boolean => {
    const targetNode = findNodeByPath(fileTreeData.value, parentPath || '');
    if (!targetNode || !targetNode.children) return false;
    
    return targetNode.children.some(child => 
      child.label === fileName && child.type === 'card'
    );
  };
  
  // 如果文件不存在，直接返回原名
  if (!checkIfFileExists(originalName)) {
    return originalName;
  }
  
  // 解析文件名和扩展名
  const parsed = parseFileName(originalName);
  let counter = 1;
  
  // 生成新的文件名，直到找到不重复的
  let newName: string;
  do {
    if (parsed.extension) {
      newName = `${parsed.filename}_copy${counter}.${parsed.extension}`;
    } else {
      newName = `${parsed.filename}_copy${counter}`;
    }
    counter++;
  } while (checkIfFileExists(newName));
  
  return newName;
};

// ArkhamDB导入相关功能
// 开始ArkhamDB导入流程
const startArkhamDBImportProcess = async () => {
  if (!contextMenuTarget.value) return;

  try {
    arkhamdbImportTarget.value = contextMenuTarget.value;

    // 读取JSON文件内容
    const filePath = contextMenuTarget.value.path as string;
    const content = await WorkspaceService.getFileContent(filePath);

    // 解析内容包数据
    let contentPack: ArkhamDBContentPack;
    try {
      contentPack = JSON.parse(content || '{}') as ArkhamDBContentPack;
    } catch (error) {
      message.error('文件格式错误，无法解析为有效的JSON');
      return;
    }

    arkhamdbImportContent.value = contentPack;

    // 显示警告对话框
    showArkhamDBImportDialog.value = true;

  } catch (error) {
    console.error('读取文件失败:', error);
    message.error('读取文件失败，请检查文件是否可访问');
  }
};

// 确认ArkhamDB导入
const confirmArkhamDBImport = async () => {
  if (!arkhamdbImportContent.value || !arkhamdbImportTarget.value) {
    return;
  }

  try {
    // 关闭警告对话框，显示进度对话框
    showArkhamDBImportDialog.value = false;
    showArkhamDBProgressDialog.value = true;

    // 重置状态
    arkhamdbImporting.value = true;
    arkhamdbImportCompleted.value = false;
    arkhamdbImportLogs.value = [];
    arkhamdbImportResult.value = null;

    // 立即开始定时刷新日志（在导入过程中）
    startLogRefresh();

    // 调用API导入内容包
    const result = await ArkhamDBService.importContentPack({
      content_pack: arkhamdbImportContent.value,
      parent_path: '' // 导入到工作空间根目录
    });

    if (result.data) {
      arkhamdbImportResult.value = result.data;
      arkhamdbImportCompleted.value = true;
      arkhamdbImporting.value = false;

      // 导入完成后停止定时刷新，避免不必要的API请求
      if (logRefreshInterval.value) {
        clearInterval(logRefreshInterval.value);
        logRefreshInterval.value = null;
      }

      // 刷新文件树
      setTimeout(() => {
        emit('refresh-file-tree');
      }, 1000);

      message.success('ArkhamDB内容包导入成功！');
    }

  } catch (error) {
    console.error('ArkhamDB导入失败:', error);
    arkhamdbImporting.value = false;

    // 导入失败时也要停止定时刷新，避免不必要的API请求
    if (logRefreshInterval.value) {
      clearInterval(logRefreshInterval.value);
      logRefreshInterval.value = null;
    }

    // 显示错误信息
    if (error instanceof ApiError) {
      message.error(`导入失败: ${error.message}`);
      // 将错误信息添加到日志
      arkhamdbImportLogs.value.push(`[错误] ${error.message}`);
    } else {
      message.error('导入过程中发生未知错误');
      arkhamdbImportLogs.value.push('[错误] 导入过程中发生未知错误');
    }
  }
};

// 开始定时刷新日志
const startLogRefresh = () => {
  if (logRefreshInterval.value) {
    clearInterval(logRefreshInterval.value);
  }

  logRefreshInterval.value = setInterval(async () => {
    try {
      await refreshImportLogs();
    } catch (error) {
      console.error('刷新日志失败:', error);
    }
  }, 1000); // 每秒刷新一次
};

// 刷新导入日志
const refreshImportLogs = async () => {
  try {
    const logsResult = await ArkhamDBService.getImportLogs();
    if (logsResult.data && logsResult.data.logs) {
      // 将日志字符串按行分割
      const logLines = logsResult.data.logs.split('\n').filter(line => line.trim());
      arkhamdbImportLogs.value = logLines;

      // 只有在导入进行中时才自动滚动到最新日志
      // 导入完成后允许用户手动拖动查看历史日志
      if (arkhamdbImporting.value) {
        await nextTick();
        if (arkhamdbLogScrollbar.value) {
          arkhamdbLogScrollbar.value.scrollTo({ top: 999999, behavior: 'smooth' });
        }
      }
    }
  } catch (error) {
    console.error('获取导入日志失败:', error);
  }
};

// 停止ArkhamDB导入
const stopArkhamDBImport = () => {
  arkhamdbImporting.value = false;

  // 停止定时刷新
  if (logRefreshInterval.value) {
    clearInterval(logRefreshInterval.value);
    logRefreshInterval.value = null;
  }

  message.info('导入已停止');
};

// 关闭ArkhamDB导入对话框
const closeArkhamDBImportDialog = () => {
  showArkhamDBProgressDialog.value = false;

  // 停止定时刷新
  if (logRefreshInterval.value) {
    clearInterval(logRefreshInterval.value);
    logRefreshInterval.value = null;
  }

  // 重置状态
  arkhamdbImporting.value = false;
  arkhamdbImportCompleted.value = false;
  arkhamdbImportLogs.value = [];
  arkhamdbImportResult.value = null;
  arkhamdbImportTarget.value = null;
  arkhamdbImportContent.value = null;
};

// 组件挂载时加载数据
onMounted(() => {
  loadFileTree();
  console.log(`检测到 CPU 核心数: ${cpuCores.value}`);
});

// 组件卸载时清理定时器
onUnmounted(() => {
  if (logRefreshInterval.value) {
    clearInterval(logRefreshInterval.value);
    logRefreshInterval.value = null;
  }
});

// 导出方法供父组件调用
defineExpose({
  refreshFileTree
});
</script>

<style scoped>
/* 批量导出相关样式 */
/* 进度相关样式 */
.batch-export-status {
  text-align: center;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 并发任务状态显示 */
.concurrent-status {
  margin-top: 12px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.08);
  border-radius: 6px;
  border-left: 4px solid #667eea;
}

.active-tasks {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
  max-height: 80px;
  overflow-y: auto;
}

.active-tasks::-webkit-scrollbar {
  width: 4px;
}

.active-tasks::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.active-tasks::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 2px;
}

/* 高级导出进度样式 */
.advanced-export-progress {
  padding: 12px;
  background: rgba(118, 75, 162, 0.05);
  border-radius: 8px;
  border-left: 4px solid #764ba2;
}

.export-statistics {
  margin-top: 12px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 6px;
}

/* 进度条动画 */
:deep(.n-progress-graph-line-fill) {
  transition: width 0.3s ease;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

:deep(.n-progress-text) {
  font-weight: 600;
  color: #667eea;
}

.export-logs {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  background: #f8f9fa;
}

.log-content {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  margin-bottom: 4px;
  line-height: 1.4;
  word-wrap: break-word;
}

.log-item.error {
  color: #d32f2f;
}

.log-item.warning {
  color: #ed6c02;
}

.log-item.success {
  color: #2e7d32;
}

/* 进度条样式优化 */
:deep(.n-progress-text) {
  font-weight: 600;
}

:deep(.n-progress-graph-line-fill) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

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
  /* 移动端滚动优化 */
  -webkit-overflow-scrolling: touch;
  /* 确保滚动容器有正确的高度 */
  min-height: 0;
  height: 0;
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

/* 并发任务标签动画 */
:deep(.n-tag) {
  animation: tagFadeIn 0.3s ease-in-out;
}

@keyframes tagFadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 高级导出对话框样式优化 */
:deep(.n-form-item) {
  margin-bottom: 12px;
}

:deep(.n-form-item-label) {
  font-weight: 500;
  color: #374151;
  font-size: 12px;
}

:deep(.n-select) {
  min-width: 120px;
}

/* 高级导出网格布局优化 */
:deep(.n-grid-item .n-form-item) {
  margin-bottom: 8px;
}

:deep(.n-grid-item .n-form-item-label) {
  min-height: 20px;
  line-height: 20px;
}

:deep(.n-grid-item .n-select),
:deep(.n-grid-item .n-slider) {
  font-size: 12px;
}

/* 滑动条样式优化 */
:deep(.n-slider) {
  margin: 4px 0;
}

:deep(.n-slider-rail) {
  background: #e2e8f0;
}

:deep(.n-slider-fill) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

:deep(.n-slider-handle) {
  border: 2px solid #667eea;
  background: white;
}

:deep(.n-slider-handle:hover) {
  border-color: #5a67d8;
}

/* Lama模型提示样式 */
:deep(.n-alert) {
  font-size: 12px;
}

:deep(.n-alert .n-alert__icon) {
  font-size: 14px;
}

/* 高级导出进度条样式 */
.advanced-export-progress :deep(.n-progress-graph-line-fill) {
  background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
}

.advanced-export-progress :deep(.n-progress-text) {
  color: #764ba2;
}

/* 紧凑布局优化 */
:deep(.n-form) {
  margin: 0;
}

:deep(.n-grid) {
  margin: 0;
}

:deep(.n-space) {
  gap: 8px !important;
}

/* 高级导出对话框特定样式 */
:deep(.n-card__content) {
  padding: 16px !important;
}

:deep(.n-card__footer) {
  padding: 12px 16px !important;
  margin: 0 !important;
}

/* 滑动条数值显示优化 */
.n-form-item .n-text {
  font-size: 11px;
  font-family: monospace;
  color: #667eea;
  font-weight: 500;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  :deep(.n-grid) {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 800px) {
  :deep(.n-grid) {
    grid-template-columns: 1fr !important;
  }
}

/* 移动端文件树滚动优化 */
@media (max-width: 768px) {
  .file-tree-pane {
    height: 100vh;
    max-height: 100vh;
  }

  .file-tree-content {
    padding: 8px;
    /* 确保移动端滚动容器占满可用空间 */
    height: calc(100vh - 60px); /* 减去头部高度 */
    min-height: calc(100vh - 60px);
    /* 增强滚动体验 */
    overscroll-behavior: contain;
    touch-action: pan-y;
  }
}
</style>

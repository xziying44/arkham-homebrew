<template>
  <div class="package-editor-container">
    <!-- 上传页面 -->
    <div v-if="showUploadPage" class="upload-page">
      <div class="upload-page-header">
        <n-button @click="closeUploadPage" size="small">
          <template #icon>
            <n-icon :component="ArrowBackOutline" />
          </template>
          {{ t('common.buttons.back') }}
        </n-button>
        <h3>{{ getUploadPageTitle() }}</h3>
      </div>
      <div class="upload-page-content">
        <UniversalUploadDialog
          ref="uploadDialogRef"
          :upload-type="currentUploadType"
          :current-item="currentUploadItem"
          :upload-items="currentUploadItems"
          :config="packageData"
          :is-batch="isCurrentUploadBatch"
          @confirm="handleUploadConfirm"
          @cancel="closeUploadPage"
        />
      </div>
      <div class="upload-page-footer">
        <n-space>
          <n-button @click="closeUploadPage">{{ t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="triggerUpload" :loading="isAnyUploading">
            {{ getUploadButtonText() }}
          </n-button>
        </n-space>
      </div>
    </div>

    <!-- 主编辑器内容 -->
    <div v-else class="editor-main">
      <!-- 编辑器头部 -->
      <div class="editor-header">
        <div class="package-info">
          <h3>{{ packageData.meta?.name || t('contentPackage.common.unnamedPackage') }}</h3>
          <div class="package-meta">
            <n-tag type="info" size="small">{{ t(`contentPackage.languages.${packageData.meta?.language || 'zh-cn'}`)
            }}</n-tag>
            <n-tag v-for="type in (packageData.meta?.types || [])" :key="type" type="default" size="small">
              {{ t(`contentPackage.packageTypes.${type}`) }}
            </n-tag>
            <n-tag type="success" size="small">ID: {{ packageData.meta?.code || t('contentPackage.common.unknown') }}</n-tag>
          </div>
        </div>
        <div class="editor-actions">
          <n-button @click="showEditMetaDialog = true" size="small">
            <template #icon>
              <n-icon :component="CreateOutline" />
            </template>
            {{ t('contentPackage.common.editInfo') }}
          </n-button>
          <n-button type="primary" @click="handleSave" :loading="saving" size="small">
            <template #icon>
              <n-icon :component="SaveOutline" />
            </template>
            {{ t('contentPackage.common.save') }}
          </n-button>
        </div>
      </div>

      <!-- 编辑器内容 -->
    <div class="editor-content">
      <n-tabs type="card" default-value="info" animated>
        <!-- 基础信息标签页 -->
        <n-tab-pane name="info" :tab="$t('contentPackage.editor.tabs.info')">
          <div class="info-panel">
            <!-- 封面预览 -->
            <div class="banner-section">
              <h4>{{ $t('contentPackage.editor.sections.banner') }}</h4>
              <div class="banner-preview-container">
                <div class="banner-preview">
                  <img v-if="packageData.meta?.banner_url" :src="packageData.meta.banner_url"
                    :alt="t('contentPackage.editor.fields.banner')" />
                  <img v-else-if="packageData.banner_base64" :src="packageData.banner_base64"
                    :alt="t('contentPackage.editor.fields.banner')" />
                  <div v-else class="no-banner">
                    <n-icon :component="ImageOutline" size="48" />
                    <span>{{ $t('contentPackage.editor.noBanner') }}</span>
                  </div>
                </div>
                <!-- 上传云端按钮 - 当有base64数据时显示 -->
                <n-button v-if="packageData.banner_base64" type="primary" size="small"
                  @click="openBannerUploadPage" class="upload-cloud-btn">
                  <template #icon>
                    <n-icon :component="CloudUploadOutline" />
                  </template>
                  {{ packageData.meta?.banner_url ? t('contentPackage.upload.button.reuploadToCloud') :
                    t('contentPackage.upload.button.uploadToCloud') }}
                </n-button>
              </div>
            </div>

            <!-- 基础信息显示 -->
            <div class="info-section">
              <h4>{{ $t('contentPackage.editor.sections.basicInfo') }}</h4>
              <n-descriptions :column="2" bordered>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.code')">
                  <n-text code>{{ packageData.meta?.code || '未知' }}</n-text>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.name')">
                  <n-tag type="info" size="small">{{ packageData.meta?.name || '未命名内容包' }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.author')">
                  <n-tag type="success" size="small">{{ packageData.meta?.author || '未知作者' }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.language')">
                  <n-tag type="warning" size="small">{{ t(`contentPackage.languages.${packageData.meta?.language ||
                    'zh-cn'}`) }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.types')">
                  <n-tag v-for="type in (packageData.meta?.types || [])" :key="type" :type="getTypeTagColor(type)"
                    size="small">
                    {{ t(`contentPackage.packageTypes.${type}`) }}
                  </n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.status')">
                  <n-tag :type="getStatusTagType(packageData.meta?.status || 'draft')" size="small">
                    {{ getStatusLabel(packageData.meta?.status || 'draft') }}
                  </n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.dateUpdated')">
                  <n-tag type="default" size="small">{{ formatDate(packageData.meta?.date_updated || new
                    Date().toISOString()) }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item :label="$t('contentPackage.editor.fields.generator')">
                  <n-tag type="default" size="small">{{ packageData.meta?.generator || '未知' }}</n-tag>
                </n-descriptions-item>
              </n-descriptions>

              <!-- 描述 -->
              <div class="description-section">
                <h4>{{ $t('contentPackage.editor.fields.description') }}</h4>
                <n-card>
                  <n-text>{{ packageData.meta?.description || '暂无描述' }}</n-text>
                </n-card>
              </div>

              <!-- 外部链接 -->
              <div v-if="packageData.meta?.external_link" class="external-link-section">
                <h4>{{ $t('contentPackage.editor.fields.externalLink') }}</h4>
                <n-button text @click="openExternalLink">
                  <template #icon>
                    <n-icon :component="OpenOutline" />
                  </template>
                  {{ packageData.meta.external_link }}
                </n-button>
              </div>
            </div>
          </div>
        </n-tab-pane>

        <!-- 卡牌管理标签页 -->
        <n-tab-pane name="cards" :tab="$t('contentPackage.editor.tabs.cards')">
          <div class="cards-panel">
            <div class="cards-header">
              <h4>{{ $t('contentPackage.editor.sections.cards') }}</h4>
              <n-space>
                <n-button
                  v-if="v2Cards.length > 0"
                  type="warning"
                  @click="openCardBatchUploadPage"
                  size="small"
                >
                  <template #icon>
                    <n-icon :component="CloudUploadOutline" />
                  </template>
                  {{ t('contentPackage.common.batchUpload') }} ({{ v2CardsWithCloudUrls.length }}/{{ v2Cards.length }})
                </n-button>
                <n-button type="primary" @click="showAddCardDialog = true" size="small">
                  <template #icon>
                    <n-icon :component="AddOutline" />
                  </template>
                  {{ t('contentPackage.common.addCard') }}
                </n-button>
              </n-space>
            </div>

            <!-- 卡牌列表 -->
            <div class="cards-content">
              <div v-if="!packageData.cards || packageData.cards.length === 0" class="empty-cards">
                <n-empty :description="t('contentPackage.cards.empty.title')">
                  <template #icon>
                    <n-icon :component="DocumentTextOutline" />
                  </template>
                  <template #extra>
                    <n-text depth="3">{{ t('contentPackage.cards.empty.description') }}</n-text>
                  </template>
                </n-empty>
              </div>
              <div v-else class="cards-grid">
                <div v-for="(card, index) in packageData.cards" :key="card.filename" class="card-item"
                  :class="{ 'unsupported': getCardStatus(card.filename).version !== '2.0' }">
                  <!-- 状态图标 - 左上角 -->
                  <div v-if="hasAnyUrls(card)" class="status-icon">
                    <n-icon :component="hasCloudUrls(card) ? CloudOutline : FolderOutline" size="18"
                      :title="hasCloudUrls(card) ? t('contentPackage.upload.status.uploadedToCloud') : t('contentPackage.upload.status.savedToLocal')"
                      :class="hasCloudUrls(card) ? 'cloud-status-icon' : 'local-status-icon'" />
                  </div>

                  <div class="card-preview">
                    <div v-if="getCardStatus(card.filename).isGenerating" class="preview-loading">
                      <n-spin size="small" />
                    </div>
                    <div v-else-if="getCardStatus(card.filename).generationError" class="preview-error">
                      <n-icon :component="WarningOutline" />
                      <span class="error-text">{{ t('contentPackage.common.generationFailed') }}</span>
                    </div>
                    <div v-else-if="getCardStatus(card.filename).previewImage" class="preview-image">
                      <img :src="getCardStatus(card.filename).previewImage" :alt="card.filename" />
                    </div>
                    <div v-else class="preview-placeholder">
                      <n-icon :component="DocumentTextOutline" size="24" />
                    </div>
                  </div>
                  <div class="card-info">
                    <div class="card-name">
                      {{ card.filename }}
                    </div>
                    <div class="card-meta">
                      <n-space size="small">
                        <n-tag v-if="getCardStatus(card.filename).version !== '2.0'" type="error" size="tiny">
                          {{ t('contentPackage.common.unsupported') }} (v{{ getCardStatus(card.filename).version }})
                        </n-tag>
                        <n-tag v-else type="success" size="tiny">
                          v{{ getCardStatus(card.filename).version }}
                        </n-tag>
                        <!-- 卡牌标签显示 -->
                        <n-tag v-if="card.permanent" type="info" size="tiny">
                          {{ t('contentPackage.common.permanent') }}
                        </n-tag>
                        <n-tag v-if="card.exceptional" type="warning" size="tiny">
                          {{ t('contentPackage.common.exceptional') }}
                        </n-tag>
                        <n-tag v-if="card.myriad" type="success" size="tiny">
                          {{ t('contentPackage.common.myriad') }}
                        </n-tag>
                        <n-tag v-if="card.exile" type="error" size="tiny">
                          {{ t('contentPackage.common.exile') }}
                        </n-tag>
                      </n-space>
                    </div>
                  </div>
                  <div class="card-actions">
                    <n-button circle size="tiny" type="error" @click="removeCard(index)">
                      <template #icon>
                        <n-icon :component="TrashOutline" />
                      </template>
                    </n-button>
                  </div>
                  <!-- 卡牌操作按钮区域 - 移到底部 -->
                  <div class="card-bottom-actions">
                    <n-space vertical style="width: 100%;">
                      <!-- 标签编辑按钮 -->
                      <n-button type="info" size="small" @click="openEditTagsDialog(card)">
                        <template #icon>
                          <n-icon :component="CreateOutline" />
                        </template>
                        {{ t('contentPackage.common.editTags') }}
                      </n-button>

                      <!-- 上传按钮 -->
                      <n-button v-if="getCardStatus(card.filename).version === '2.0'" type="primary" size="small"
                        @click="openCardUploadPage(card)"
                        :loading="isCardUploading && uploadingCard?.filename === card.filename">
                        <template #icon>
                          <n-icon :component="CloudUploadOutline" />
                        </template>
                        {{ hasCloudUrls(card) ? t('contentPackage.upload.button.reupload') :
                          t('contentPackage.upload.button.uploadCard') }}
                      </n-button>
                    </n-space>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </n-tab-pane>

        <!-- 遭遇组管理标签页 -->
        <n-tab-pane name="encounters" :tab="$t('contentPackage.editor.tabs.encounters')">
          <div class="encounters-panel">
            <div class="encounters-header">
              <h4>{{ $t('contentPackage.editor.sections.encounters') }}</h4>
              <n-space>
                <n-button
                  v-if="encounters.length > 0"
                  type="warning"
                  @click="openEncounterBatchUploadPage"
                  size="small"
                >
                  <template #icon>
                    <n-icon :component="CloudUploadOutline" />
                  </template>
                  {{ t('contentPackage.common.batchUpload') }} ({{ encountersWithCloudUrls.length }}/{{ encounters.length }})
                </n-button>
                <n-button type="primary" @click="refreshEncounterGroups" size="small" :loading="refreshingEncounters">
                  <template #icon>
                    <n-icon :component="RefreshOutline" />
                  </template>
                  {{ t('contentPackage.common.refresh') }}
                </n-button>
              </n-space>
            </div>

            <!-- 遭遇组列表 -->
            <div class="encounters-content">
              <div v-if="!encounters || encounters.length === 0" class="empty-encounters">
                <n-empty :description="t('contentPackage.encounters.empty.title')">
                  <template #icon>
                    <n-icon :component="ImagesOutline" />
                  </template>
                  <template #extra>
                    <n-text depth="3">{{ t('contentPackage.encounters.empty.description') }}</n-text>
                  </template>
                </n-empty>
              </div>
              <div v-else class="encounters-grid">
                <div
                  v-for="encounter in encounters"
                  :key="encounter.code"
                  class="encounter-item"
                  :class="{ 'dragging': draggedEncounter?.code === encounter.code, 'drag-over': dragOverEncounter?.code === encounter.code }"
                  draggable="true"
                  @dragstart="handleDragStart(encounter, $event)"
                  @dragover="handleDragOver(encounter, $event)"
                  @dragleave="handleDragLeave"
                  @drop="handleDrop(encounter, $event)"
                  @dragend="handleDragEnd"
                >
                  <!-- 拖动手柄 -->
                  <div class="drag-handle" :title="t('contentPackage.encounters.dragToReorder')">
                    <n-icon :component="ReorderThreeOutline" size="20" />
                  </div>

                  <!-- 状态图标 - 左上角 -->
                  <div v-if="hasCloudUrl(encounter)" class="status-icon">
                    <n-icon :component="CloudOutline" size="18"
                      :title="t('contentPackage.upload.status.uploadedToCloud')"
                      class="cloud-status-icon" />
                  </div>
                  <div v-else-if="hasLocalUrl(encounter)" class="status-icon">
                    <n-icon :component="FolderOutline" size="18"
                      :title="t('contentPackage.upload.status.savedToLocal')"
                      class="local-status-icon" />
                  </div>

                  <div class="encounter-icon">
                    <div v-if="encounter.base64" class="icon-preview">
                      <img :src="encounter.base64" :alt="encounter.name" />
                    </div>
                    <div v-else class="icon-placeholder">
                      <n-icon :component="ImagesOutline" size="24" />
                    </div>
                  </div>
                  <div class="encounter-info">
                    <div class="encounter-name">
                      {{ encounter.name }}
                    </div>
                    <div class="encounter-code">
                      <n-text depth="3" style="font-size: 0.75rem;">{{ encounter.code.substring(0, 8) }}...</n-text>
                    </div>
                  </div>
                  <div class="encounter-actions">
                    <n-button circle size="tiny" type="info" @click="openEncounterUploadPage(encounter)"
                      :loading="isEncounterUploading && uploadingEncounter?.code === encounter.code">
                      <template #icon>
                        <n-icon :component="CloudUploadOutline" />
                      </template>
                    </n-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </n-tab-pane>

                <!-- 自动编号标签页 -->
        <n-tab-pane name="numbering" :tab="$t('contentPackage.editor.tabs.numbering')">
          <div class="numbering-panel">
            <h4>{{ $t('contentPackage.numbering.title') }}</h4>

            <!-- 编号配置区域 -->
            <div class="numbering-config">
              <n-card :title="$t('contentPackage.numbering.config.title')" :bordered="false">
                <n-form :label-width="140">
                  <n-form-item :label="$t('contentPackage.numbering.config.startNumber')">
                    <n-input-number v-model:value="numberingStartNumber" :min="1" :step="1" style="width: 200px;" />
                  </n-form-item>
                  <n-form-item :label="$t('contentPackage.numbering.config.noEncounterPosition')">
                    <n-radio-group v-model:value="numberingNoEncounterPosition">
                      <n-radio-button value="before">
                        {{ $t('contentPackage.numbering.config.positionBefore') }}
                      </n-radio-button>
                      <n-radio-button value="after">
                        {{ $t('contentPackage.numbering.config.positionAfter') }}
                      </n-radio-button>
                    </n-radio-group>
                  </n-form-item>
                  <n-form-item :label="$t('contentPackage.numbering.config.footerCopyright')">
                    <n-input v-model:value="numberingFooterCopyright" type="text"
                      :placeholder="$t('contentPackage.numbering.config.footerCopyrightPlaceholder')"
                      style="width: 400px;" />
                  </n-form-item>
                  <n-form-item :label="$t('contentPackage.numbering.config.footerIcon')">
                    <n-select v-model:value="numberingFooterIconPath"
                      :options="footerIconOptions"
                      :placeholder="$t('contentPackage.numbering.config.footerIconPlaceholder')"
                      style="width: 400px;"
                      clearable />
                  </n-form-item>
                </n-form>

                <template #action>
                  <n-space>
                    <n-button type="primary" @click="generateNumberingPlan" :loading="generatingPlan">
                      <template #icon>
                        <n-icon :component="ConstructOutline" />
                      </template>
                      {{ $t('contentPackage.numbering.actions.generatePlan') }}
                    </n-button>
                  </n-space>
                </template>
              </n-card>
            </div>

            <!-- 编号方案预览 -->
            <div v-if="numberingPlan.length > 0" class="numbering-preview">
              <n-card :title="$t('contentPackage.numbering.preview.title')" :bordered="false">
                <n-alert type="info" style="margin-bottom: 1rem;">
                  <template #icon>
                    <n-icon :component="InformationCircleOutline" />
                  </template>
                  {{ $t('contentPackage.numbering.preview.description') }}
                </n-alert>

                <div class="plan-summary">
                  <n-descriptions :column="2" bordered style="margin-bottom: 1rem;">
                    <n-descriptions-item :label="$t('contentPackage.numbering.preview.totalCards')">
                      <n-tag type="info" size="small">{{ numberingPlan.length }} 张</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.numbering.preview.numberRange')">
                      <n-tag type="success" size="small">
                        {{ numberingPlan[0]?.card_number }} - {{ numberingPlan[numberingPlan.length - 1]?.card_number }}
                      </n-tag>
                    </n-descriptions-item>
                  </n-descriptions>
                </div>

                <!-- 编号方案表格 -->
                <n-scrollbar style="max-height: 400px;">
                  <n-data-table
                    :columns="numberingTableColumns"
                    :data="numberingPlan"
                    :pagination="false"
                    :bordered="true"
                    size="small"
                  />
                </n-scrollbar>

                <template #action>
                  <n-space>
                    <n-button @click="clearNumberingPlan">
                      {{ $t('contentPackage.numbering.actions.cancelPlan') }}
                    </n-button>
                    <n-button type="primary" @click="applyNumberingPlan" :loading="applyingPlan">
                      <template #icon>
                        <n-icon :component="SaveOutline" />
                      </template>
                      {{ $t('contentPackage.numbering.actions.applyPlan') }}
                    </n-button>
                  </n-space>
                </template>
              </n-card>
            </div>

            <!-- 编号日志 -->
            <div v-if="numberingLogs.length > 0" class="numbering-logs">
              <n-card :title="$t('contentPackage.numbering.logs.title')" :bordered="false">
                <n-scrollbar style="max-height: 200px;">
                  <div class="logs-container">
                    <div v-for="(log, index) in numberingLogs" :key="index" class="log-item">
                      <n-text>{{ log }}</n-text>
                    </div>
                  </div>
                </n-scrollbar>
              </n-card>
            </div>
          </div>
        </n-tab-pane>

        <!-- 线上导出标签页 -->
        <n-tab-pane name="export-online" :tab="$t('contentPackage.editor.tabs.onlineExport')">
          <div class="export-panel">
            <h4>{{$t('contentPackage.editor.tabs.onlineExport')}}</h4>

            <!-- TTS导出区域 -->
            <div class="export-content">
              <n-card :title="$t('contentPackage.export.tts.title')" :bordered="false">
                <template #header-extra>
                  <n-tag type="info" size="small">Tabletop Simulator</n-tag>
                </template>

                <div class="tts-export-info">
                  <n-alert type="info" style="margin-bottom: 1rem;">
                    <template #icon>
                      <n-icon :component="ConstructOutline" />
                    </template>
                    {{ $t('contentPackage.export.tts.description') }}
                  </n-alert>

                  <n-descriptions :column="2" bordered style="margin-bottom: 1.5rem;">
                    <n-descriptions-item :label="$t('contentPackage.export.tts.packageName')">
                      <n-text strong>{{ packageData.meta?.name || t('contentPackage.common.unnamedPackage') }}</n-text>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.export.tts.cardCount')">
                      <n-tag type="info" size="small">{{ packageData.cards?.length || 0 }} 张</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.export.tts.cardsWithImages')">
                      <n-tag type="success" size="small">{{ cardsWithAnyUrls.length }} 张</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.export.tts.exportStatus')">
                      <n-tag :type="canExportToTts ? 'success' : 'warning'" size="small">
                        {{ canExportToTts ? t('contentPackage.export.tts.canExport') : t('contentPackage.export.tts.needImages') }}
                      </n-tag>
                    </n-descriptions-item>
                  </n-descriptions>

                  <!-- 卡牌状态列表 -->
                  <div v-if="packageData.cards && packageData.cards.length > 0" class="tts-cards-status">
                    <h5>{{ $t('contentPackage.export.tts.cardExportStatus') }}</h5>
                    <n-scrollbar style="max-height: 200px;">
                      <div class="tts-cards-list">
                        <div v-for="card in packageData.cards" :key="card.filename" class="tts-card-item">
                          <div class="tts-card-info">
                            <n-text>{{ card.filename }}</n-text>
                            <n-tag :type="getCardExportStatus(card).type" size="tiny" style="margin-left: 0.5rem;">
                              {{ getCardExportStatus(card).text }}
                            </n-tag>
                          </div>
                          <n-icon :component="getCardExportStatus(card).icon" :color="getCardExportStatus(card).color"
                            size="16" />
                        </div>
                      </div>
                    </n-scrollbar>
                  </div>
                </div>

                <template #action>
                  <n-space>
                    <n-button type="primary" @click="exportToTts" :loading="exportingToTts" :disabled="!canExportToTts">
                      <template #icon>
                        <n-icon :component="DownloadOutline" />
                      </template>
                      {{ t('contentPackage.export.tts.exportTTSItems') }}
                    </n-button>
                  </n-space>
                </template>
              </n-card>

              <!-- ArkhamDB导出区域 -->
              <n-card :title="$t('contentPackage.export.arkhamdb.title')" :bordered="false" style="margin-top: 1.5rem;">
                <template #header-extra>
                  <n-tag type="success" size="small">arkham.build</n-tag>
                </template>

                <div class="arkhamdb-export-info">
                  <n-alert type="success" style="margin-bottom: 1rem;">
                    <template #icon>
                      <n-icon :component="DownloadOutline" />
                    </template>
                    {{ $t('contentPackage.export.arkhamdb.description') }}
                  </n-alert>

                  <n-descriptions :column="2" bordered style="margin-bottom: 1.5rem;">
                    <n-descriptions-item :label="$t('contentPackage.export.arkhamdb.packageName')">
                      <n-text strong>{{ packageData.meta?.name || t('contentPackage.common.unnamedPackage') }}</n-text>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.export.arkhamdb.cardCount')">
                      <n-tag type="info" size="small">{{ packageData.cards?.length || 0 }} 张</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.export.arkhamdb.packageCode')">
                      <n-tag type="warning" size="small">{{ packageData.meta?.code || t('contentPackage.common.unknown') }}</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.export.arkhamdb.exportStatus')">
                      <n-tag type="success" size="small">
                        {{ t('contentPackage.export.arkhamdb.alwaysExportable') }}
                      </n-tag>
                    </n-descriptions-item>
                  </n-descriptions>

                  <div class="arkhamdb-description">
                    <h5>{{ $t('contentPackage.export.arkhamdb.exportDescription') }}</h5>
                    <n-space vertical size="small">
                      <n-text depth="3" v-for="(detail, index) in $tm('contentPackage.export.arkhamdb.exportDetails')" :key="index">
                        {{ $rt(detail) }}
                      </n-text>
                    </n-space>
                  </div>
                </div>

                <template #action>
                  <n-space>
                    <n-button type="success" @click="exportToArkhamdb" :loading="exportingToArkhamdb">
                      <template #icon>
                        <n-icon :component="DownloadOutline" />
                      </template>
                      {{ t('contentPackage.export.arkhamdb.exportArkhamDB') }}
                    </n-button>
                  </n-space>
                </template>
              </n-card>

              <!-- 导出日志对话框 -->
              <n-modal v-model:show="showExportLogsDialog" preset="dialog" :title="$t('contentPackage.export.tts.exportLogs')" style="width: 800px;">
                <div class="export-logs-content">
                  <n-scrollbar style="max-height: 400px;">
                    <div class="logs-container">
                      <div v-for="(log, index) in exportLogs" :key="index" :class="['log-item', getLogItemClass(log)]">
                        <n-text>{{ log }}</n-text>
                      </div>
                    </div>
                  </n-scrollbar>
                </div>
                <template #action>
                  <n-space>
                    <n-button @click="showExportLogsDialog = false">{{ t('contentPackage.export.tts.close') }}</n-button>
                    <n-button v-if="exportResult?.tts_path" type="primary" @click="openTtsFileLocation">
                      {{ t('contentPackage.export.tts.openFolder') }}
                    </n-button>
                  </n-space>
                </template>
              </n-modal>

              <!-- ArkhamDB导出日志对话框 -->
              <n-modal v-model:show="showArkhamdbExportLogsDialog" preset="dialog" :title="$t('contentPackage.export.arkhamdb.exportLogs')" style="width: 800px;">
                <div class="export-logs-content">
                  <n-scrollbar style="max-height: 400px;">
                    <div class="logs-container">
                      <div v-for="(log, index) in arkhamdbExportLogs" :key="index" :class="['log-item', getLogItemClass(log)]">
                        <n-text>{{ log }}</n-text>
                      </div>
                    </div>
                  </n-scrollbar>
                </div>
                <template #action>
                  <n-space>
                    <n-button @click="showArkhamdbExportLogsDialog = false">{{ t('contentPackage.export.arkhamdb.close') }}</n-button>
                    <n-button v-if="arkhamdbExportResult?.output_path" type="success" @click="openArkhamdbFileLocation">
                      {{ t('contentPackage.export.arkhamdb.openFolder') }}
                    </n-button>
                  </n-space>
                </template>
              </n-modal>
            </div>
          </div>
        </n-tab-pane>

        <!-- 实体导出标签页 -->
        <n-tab-pane name="export-physical" :tab="$t('contentPackage.pnp.title')">
          <div class="physical-export-panel">
            <h4>{{ $t('contentPackage.pnp.title') }}</h4>

            <!-- 上半部分：左右分栏 -->
            <div class="pnp-top-layout">
              <!-- 左侧：导出状态 -->
              <div class="pnp-status-section">
                <!-- 导出信息卡片 -->
                <n-card :title="$t('contentPackage.pnp.exportStatus.title')" :bordered="false" size="small" style="margin-bottom: 1rem;">
                  <n-descriptions :column="1" bordered size="small">
                    <n-descriptions-item :label="$t('contentPackage.pnp.exportStatus.packageName')">
                      <n-text strong>{{ packageData.meta?.name || t('contentPackage.common.unnamedPackage') }}</n-text>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.pnp.exportStatus.cardCount')">
                      <n-tag type="info" size="small">{{ packageData.cards?.length || 0 }} 张</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.pnp.exportStatus.doubleSidedCards')">
                      <n-tag type="success" size="small">{{ v2Cards.length }} 张</n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item :label="$t('contentPackage.pnp.exportStatus.exportStatus')">
                      <n-tag :type="v2Cards.length > 0 ? 'success' : 'warning'" size="small">
                        {{ v2Cards.length > 0 ? $t('contentPackage.pnp.exportStatus.canExport') : $t('contentPackage.pnp.exportStatus.needDoubleSidedCards') }}
                      </n-tag>
                    </n-descriptions-item>
                  </n-descriptions>
                </n-card>

                <!-- 导出说明 -->
                <n-alert type="info" size="small">
                  <template #icon>
                    <n-icon :component="InformationCircleOutline" />
                  </template>
                  <div>
                    <p><strong>{{ $t('contentPackage.pnp.exportParams.singleCard') }}：</strong>{{ $t('contentPackage.pnp.description.singleCardMode') }}</p>
                    <p><strong>{{ $t('contentPackage.pnp.exportParams.printSheet') }}：</strong>{{ $t('contentPackage.pnp.description.printSheetMode') }}</p>
                    <p style="margin-bottom: 0;"><strong>{{ $t('contentPackage.pnp.description.landscapeNote') }}</strong></p>
                  </div>
                </n-alert>
              </div>

              <!-- 右侧：导出参数 -->
              <div class="pnp-params-section">
                <n-card :title="$t('contentPackage.pnp.exportParams.title')" :bordered="false" size="small">
                  <n-form :label-width="100" size="small">
                    <!-- 导出模式 -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.exportMode')">
                      <n-radio-group v-model:value="pnpExportMode">
                        <n-space>
                          <n-radio value="single_card">{{ $t('contentPackage.pnp.exportParams.singleCard') }}</n-radio>
                          <n-radio value="print_sheet">{{ $t('contentPackage.pnp.exportParams.printSheet') }}</n-radio>
                          <n-radio value="images">{{ $t('contentPackage.pnp.exportParams.images') }}</n-radio>
                        </n-space>
                      </n-radio-group>
                    </n-form-item>

                    <!-- 纸张规格（仅打印纸模式） -->
                    <n-form-item v-if="pnpExportMode === 'print_sheet'" :label="$t('contentPackage.pnp.exportParams.paperSize')">
                      <n-select v-model:value="pnpPaperSize" :options="paperSizeOptions" />
                    </n-form-item>

                    <!-- 文件名前缀（仅图片模式） -->
                    <n-form-item v-if="pnpExportMode === 'images'" :label="$t('contentPackage.pnp.exportParams.prefix')">
                      <n-input v-model:value="pnpExportParams.prefix" :placeholder="$t('contentPackage.pnp.exportParams.prefixPlaceholder')" />
                    </n-form-item>

                    <!-- DPI -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.dpi')">
                      <n-input-number v-model:value="pnpExportParams.dpi" :min="150" :max="600" :step="50" style="width: 120px;" />
                    </n-form-item>

                    <!-- 卡牌规格 -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.cardSize')">
                      <n-select v-model:value="pnpExportParams.size" :options="cardSizeOptions" />
                    </n-form-item>

                    <!-- 出血尺寸 -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.bleedSize')">
                      <n-select v-model:value="pnpExportParams.bleed" :options="bleedOptions" style="width: 120px;" />
                    </n-form-item>

                    <!-- 出血模式 -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.bleedMode')">
                      <n-select v-model:value="pnpExportParams.bleed_mode" :options="bleedModeOptions" style="width: 120px;" />
                    </n-form-item>

                    <!-- 出血模型 -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.bleedModel')">
                      <n-select v-model:value="pnpExportParams.bleed_model" :options="bleedModelOptions" style="width: 120px;" />
                    </n-form-item>

                    <!-- 遭遇组模式 -->
                    <n-form-item :label="$t('contentPackage.pnp.encounterGroupMode.label')">
                      <n-select v-model:value="pnpExportParams.encounter_group_mode" :options="encounterGroupModeOptions" style="width: 120px;" />
                    </n-form-item>

                    <!-- 导出格式 -->
                    <n-form-item :label="$t('contentPackage.pnp.exportParams.exportFormat')">
                      <n-select v-model:value="pnpExportParams.format" :options="formatOptions" style="width: 120px;" />
                    </n-form-item>

                    <!-- 图片质量（仅JPG） -->
                    <n-form-item v-if="pnpExportParams.format === 'JPG'" :label="$t('contentPackage.pnp.exportParams.imageQuality')">
                      <n-slider v-model:value="pnpExportParams.quality" :min="50" :max="100" :step="5"
                        :marks="{ 50: '50', 75: '75', 90: '90', 100: '100' }" style="width: 200px;" />
                    </n-form-item>

                    <!-- 输出文件名 -->
                    <n-form-item :label="pnpExportMode === 'images' ? $t('contentPackage.pnp.exportParams.outputFolderName') : $t('contentPackage.pnp.exportParams.outputFilename')">
                      <n-input
                        v-model:value="pnpOutputFilename"
                        :placeholder="pnpExportMode === 'images' ? $t('contentPackage.pnp.exportParams.folderNamePlaceholder') : 'pnp_export.pdf'">
                        <template #suffix v-if="pnpExportMode !== 'images'">{{ $t('contentPackage.pnp.exportParams.pdfExtension') }}</template>
                      </n-input>
                    </n-form-item>

                    <!-- 导出按钮 -->
                    <n-form-item>
                      <n-button type="warning" @click="exportToPnp" :loading="exportingToPnp" :disabled="v2Cards.length === 0" block>
                        <template #icon>
                          <n-icon :component="PrintOutline" />
                        </template>
                        {{ exportingToPnp ? $t('contentPackage.pnp.exportParams.exporting') : $t('contentPackage.pnp.exportParams.startExport') }}
                      </n-button>
                    </n-form-item>
                  </n-form>
                </n-card>
              </div>
            </div>

            <!-- 下半部分：导出日志 -->
            <n-card :title="$t('contentPackage.pnp.exportLogs.title')" :bordered="false" size="small" style="margin-top: 1rem;">
              <template #header-extra>
                <n-space>
                  <n-tag v-if="exportingToPnp" type="warning">
                    <template #icon>
                      <n-spin :size="14" />
                    </template>
                    {{ $t('contentPackage.pnp.exportLogs.exporting') }}
                  </n-tag>
                  <n-tag v-else-if="pnpExportResult?.output_path" type="success">{{ $t('contentPackage.pnp.exportLogs.exportComplete') }}</n-tag>
                  <n-button v-if="pnpExportResult?.output_path && !exportingToPnp" type="warning" size="small" @click="openPnpFileLocation">
                    <template #icon>
                      <n-icon :component="FolderOutline" />
                    </template>
                    {{ $t('contentPackage.pnp.exportLogs.openFileLocation') }}
                  </n-button>
                </n-space>
              </template>

              <!-- 日志内容区域 -->
              <div v-if="pnpExportLogs.length === 0 && !exportingToPnp" class="empty-logs">
                <n-empty :description="$t('contentPackage.pnp.exportLogs.noLogsYet')" size="small">
                  <template #icon>
                    <n-icon :component="DocumentTextOutline" />
                  </template>
                </n-empty>
              </div>
              <n-scrollbar v-else style="max-height: 300px;">
                <div class="logs-container">
                  <div v-for="(log, index) in pnpExportLogs" :key="index" :class="['log-item', getLogItemClass(log)]">
                    <n-text>{{ log }}</n-text>
                  </div>
                  <!-- 导出中的加载动画 -->
                  <div v-if="exportingToPnp" class="log-item log-loading">
                    <n-spin size="small" />
                    <n-text style="margin-left: 0.5rem;">{{ $t('contentPackage.pnp.exportParams.exporting') }}</n-text>
                  </div>
                </div>
              </n-scrollbar>
            </n-card>
          </div>
        </n-tab-pane>

      </n-tabs>
    </div>
    </div>

    <!-- 编辑元数据对话框 -->
    <n-modal v-model:show="showEditMetaDialog" preset="dialog" :title="$t('contentPackage.editor.editMeta.title')"
      style="width: 600px;">
      <n-form ref="editFormRef" :model="editForm" :rules="editRules" label-placement="left" label-width="100px">
        <n-form-item path="name" :label="$t('contentPackage.editor.fields.name')">
          <n-input v-model:value="editForm.name" :placeholder="$t('contentPackage.editor.editMeta.namePlaceholder')"
            clearable />
        </n-form-item>
        <n-form-item path="description" :label="$t('contentPackage.editor.fields.description')">
          <n-input v-model:value="editForm.description" type="textarea"
            :placeholder="$t('contentPackage.editor.editMeta.descriptionPlaceholder')" :rows="3" clearable />
        </n-form-item>
        <n-form-item path="author" :label="$t('contentPackage.editor.fields.author')">
          <n-input v-model:value="editForm.author" :placeholder="$t('contentPackage.editor.editMeta.authorPlaceholder')"
            clearable />
        </n-form-item>
        <n-form-item path="language" :label="$t('contentPackage.editor.fields.language')">
          <n-select v-model:value="editForm.language" :options="localizedLanguageOptions" :placeholder="$t('contentPackage.editor.editMeta.languagePlaceholder')"
            clearable />
        </n-form-item>
        <n-form-item path="types" :label="$t('contentPackage.editor.fields.types')">
          <n-select v-model:value="editForm.types" :options="localizedPackageTypeOptions" multiple :placeholder="$t('contentPackage.editor.editMeta.typesPlaceholder')"
            clearable />
        </n-form-item>
        <n-form-item path="status" :label="$t('contentPackage.editor.fields.status')">
          <n-select v-model:value="editForm.status" :options="localizedStatusOptions" :placeholder="$t('contentPackage.editor.editMeta.statusPlaceholder')"
            clearable />
        </n-form-item>
        <n-form-item path="external_link" :label="$t('contentPackage.editor.fields.externalLink')">
          <n-input v-model:value="editForm.external_link"
            :placeholder="$t('contentPackage.editor.editMeta.externalLinkPlaceholder')" clearable />
        </n-form-item>
        <n-form-item :label="$t('contentPackage.editor.fields.banner')">
          <n-tabs type="line" default-value="url">
            <n-tab-pane name="url" :tab="$t('contentPackage.editor.editMeta.bannerUrl')">
              <n-input v-model:value="editForm.banner_url"
                :placeholder="$t('contentPackage.editor.editMeta.bannerUrlPlaceholder')" clearable />
            </n-tab-pane>
            <n-tab-pane name="file" :tab="$t('contentPackage.editor.editMeta.bannerFile')">
              <div class="banner-upload-container">
                <div v-if="!editForm.banner_base64" class="upload-area">
                  <n-upload :max="1" accept="image/*" @change="handleEditBannerUpload" :show-download-button="false"
                    :default-upload="false" :show-file-list="false">
                    <n-upload-dragger>
                      <div style="margin-bottom: 12px">
                        <n-icon size="48" :depth="3">
                          <CloudUploadOutline />
                        </n-icon>
                      </div>
                      <n-text style="font-size: 16px">
                        {{ $t('contentPackage.editor.editMeta.dragToUpload') }}
                      </n-text>
                      <n-p depth="3" style="margin: 8px 0 0 0">
                        {{ $t('contentPackage.editor.editMeta.uploadHint') }}
                      </n-p>
                    </n-upload-dragger>
                  </n-upload>
                </div>
                <div v-else class="banner-preview" @click="triggerEditFileInput">
                  <img :src="editForm.banner_base64" :alt="t('contentPackage.editor.sections.banner')" />
                  <div class="banner-preview-overlay">
                    <n-button circle type="error" @click.stop="handleEditBannerRemove">
                      <template #icon>
                        <n-icon :component="TrashOutline" />
                      </template>
                    </n-button>
                    <n-button circle type="primary" @click.stop="triggerEditFileInput">
                      <template #icon>
                        <n-icon :component="CreateOutline" />
                      </template>
                    </n-button>
                  </div>
                </div>
                <!-- 隐藏的文件输入框，用于重新上传 -->
                <input ref="editFileInputRef" type="file" accept="image/*" style="display: none"
                  @change="handleEditFileInputChange" />
              </div>
            </n-tab-pane>
          </n-tabs>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="closeEditDialog">{{ $t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="saveMetaChanges">{{ $t('contentPackage.actions.save') }}</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 添加卡牌对话框 -->
    <n-modal v-model:show="showAddCardDialog" preset="card" :title="t('contentPackage.cards.dialog.title')"
      style="width: 900px; height: 700px;">
      <CardFileBrowser v-model:visible="showAddCardDialog" @confirm="handleAddCards" />
    </n-modal>

    <!-- 上传云端对话框 -->
    <n-modal v-model:show="showUploadBannerDialog" preset="dialog"
      :title="t('contentPackage.upload.title.uploadBannerToCloud')" style="width: 600px;">
      <UniversalUploadDialog
        ref="bannerUploadDialogRef"
        upload-type="banner"
        :current-item="{ banner_base64: packageData.banner_base64, meta: packageData.meta }"
        :config="packageData"
        @confirm="handleUploadBanner"
        @cancel="showUploadBannerDialog = false" />
      <template #action>
        <n-space>
          <n-button @click="showUploadBannerDialog = false">{{ t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="triggerBannerUpload" :loading="isBannerUploading">
            {{ t('contentPackage.upload.action.startUpload') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showUploadCardDialog" preset="dialog"
      :title="t('contentPackage.upload.title.uploadCardToCloud')" style="width: 600px;">
      <UniversalUploadDialog
        ref="cardUploadDialogRef"
        upload-type="card"
        :current-item="uploadingCard"
        :config="packageData"
        @confirm="handleUploadCard"
        @cancel="showUploadCardDialog = false; uploadingCard = null" />
      <template #action>
        <n-space>
          <n-button @click="showUploadCardDialog = false; uploadingCard = null">{{ t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="triggerCardUpload" :loading="isCardUploading">
            {{ t('contentPackage.upload.action.startUpload') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 批量上传对话框 -->
    <n-modal v-model:show="showBatchUploadDialog" preset="dialog"
      :title="t('contentPackage.upload.title.batchUploadToCloud')" style="width: 700px;">
      <UniversalUploadDialog
        ref="batchUploadDialogRef"
        upload-type="card"
        :upload-items="v2Cards"
        :config="packageData"
        :is-batch="true"
        @confirm="handleBatchUpload"
        @cancel="showBatchUploadDialog = false" />
      <template #action>
        <n-space>
          <n-button @click="showBatchUploadDialog = false">{{ t('contentPackage.actions.cancel') }}</n-button>
          <n-button
            type="primary"
            @click="triggerBatchUpload"
            :loading="batchUploading"
            :disabled="v2Cards.length === 0"
          >
            {{ t('contentPackage.upload.action.startConfiguration', { count: v2Cards.length }) }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 编辑标签对话框 -->
    <n-modal v-model:show="showEditTagsDialog" preset="dialog" :title="t('contentPackage.tags.edit.title', { filename: editingCard?.filename || '' })"
      style="width: 500px;">
      <div class="edit-tags-container">
        <div class="tags-info">
          <n-alert type="info" style="margin-bottom: 1rem;">
            <template #icon>
              <n-icon :component="InformationCircleOutline" />
            </template>
            {{ t('contentPackage.tags.edit.description') }}
          </n-alert>
        </div>

        <n-form ref="editTagsFormRef" :model="editTagsForm" label-placement="left" label-width="100px">
          <n-form-item :label="t('contentPackage.tags.edit.permanent.label')">
            <n-switch v-model:value="editTagsForm.permanent" />
            <template #feedback>
              <n-text depth="3" style="font-size: 0.875rem;">
                {{ t('contentPackage.tags.edit.permanent.description') }}
              </n-text>
            </template>
          </n-form-item>

          <n-form-item :label="t('contentPackage.tags.edit.exceptional.label')">
            <n-switch v-model:value="editTagsForm.exceptional" />
            <template #feedback>
              <n-text depth="3" style="font-size: 0.875rem;">
                {{ t('contentPackage.tags.edit.exceptional.description') }}
              </n-text>
            </template>
          </n-form-item>

          <n-form-item :label="t('contentPackage.tags.edit.myriad.label')">
            <n-switch v-model:value="editTagsForm.myriad" />
            <template #feedback>
              <n-text depth="3" style="font-size: 0.875rem;">
                {{ t('contentPackage.tags.edit.myriad.description') }}
              </n-text>
            </template>
          </n-form-item>

          <n-form-item :label="t('contentPackage.tags.edit.exile.label')">
            <n-switch v-model:value="editTagsForm.exile" />
            <template #feedback>
              <n-text depth="3" style="font-size: 0.875rem;">
                {{ t('contentPackage.tags.edit.exile.description') }}
              </n-text>
            </template>
          </n-form-item>
        </n-form>

        <!-- 当前标签预览 -->
        <div class="current-tags-preview" v-if="hasAnyFormTags()">
          <h5>{{ t('contentPackage.tags.edit.preview') }}</h5>
          <n-space size="small">
            <n-tag v-if="editTagsForm.permanent" type="info" size="small">
              {{ t('contentPackage.common.permanent') }}
            </n-tag>
            <n-tag v-if="editTagsForm.exceptional" type="warning" size="small">
              {{ t('contentPackage.common.exceptional') }}
            </n-tag>
            <n-tag v-if="editTagsForm.myriad" type="success" size="small">
              {{ t('contentPackage.common.myriad') }}
            </n-tag>
            <n-tag v-if="editTagsForm.exile" type="error" size="small">
              {{ t('contentPackage.common.exile') }}
            </n-tag>
          </n-space>
        </div>
      </div>
      <template #action>
        <n-space>
          <n-button @click="closeEditTagsDialog">{{ t('contentPackage.tags.edit.cancel') }}</n-button>
          <n-button type="primary" @click="saveTagsChanges">{{ t('contentPackage.tags.edit.save') }}</n-button>
        </n-space>
      </template>
    </n-modal>


    <!-- 遭遇组上传对话框 -->
    <n-modal v-model:show="showUploadEncounterDialog" preset="dialog"
      :title="t('contentPackage.upload.title.uploadEncounterToCloud')" style="width: 600px;">
      <UniversalUploadDialog
        ref="encounterUploadDialogRef"
        upload-type="encounter"
        :current-item="uploadingEncounter"
        :config="packageData"
        @confirm="handleUploadEncounter"
        @cancel="showUploadEncounterDialog = false; uploadingEncounter = null" />
      <template #action>
        <n-space>
          <n-button @click="showUploadEncounterDialog = false; uploadingEncounter = null">{{ t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="triggerEncounterUpload" :loading="isEncounterUploading">
            {{ t('contentPackage.upload.action.uploadToCloud') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 遭遇组批量上传对话框 -->
    <n-modal v-model:show="showBatchEncounterUploadDialog" preset="dialog"
      :title="t('contentPackage.upload.title.batchUploadEncountersToCloud')" style="width: 700px;">
      <UniversalUploadDialog
        ref="batchEncounterUploadDialogRef"
        upload-type="encounter"
        :upload-items="encounters"
        :config="packageData"
        :is-batch="true"
        @confirm="handleBatchEncounterUpload"
        @cancel="showBatchEncounterUploadDialog = false" />
      <template #action>
        <n-space>
          <n-button @click="showBatchEncounterUploadDialog = false">{{ t('contentPackage.actions.cancel') }}</n-button>
          <n-button type="primary" @click="triggerBatchEncounterUpload" :loading="batchEncounterUploading">
            {{ t('contentPackage.upload.action.startUpload') }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import {
  useMessage,
  type FormInst,
  type FormRules,
  type UploadFileInfo
} from 'naive-ui';
import { useI18n } from 'vue-i18n';
import {
  CreateOutline,
  SaveOutline,
  ImageOutline,
  OpenOutline,
  ConstructOutline,
  DownloadOutline,
  CloudUploadOutline,
  CloudOutline,
  FolderOutline,
  TrashOutline,
  DocumentTextOutline,
  WarningOutline,
  AddOutline,
  InformationCircleOutline,
  ImagesOutline,
  RefreshOutline,
  ReorderThreeOutline,
  PrintOutline,
  ArrowBackOutline
} from '@vicons/ionicons5';
import type { ContentPackageFile, PackageType, ContentPackageCard, EncounterSet } from '@/types/content-package';
import { getPackageTypeOptions, getLanguageOptions, getStatusOptions } from '@/types/content-package';
import { WorkspaceService } from '@/api';
import { CardService } from '@/api/card-service';
import { ConfigService } from '@/api/config-service';
import { ImageHostService } from '@/api/image-host-service';
import { ContentPackageService } from '@/api/content-package-service';
import { v4 as uuidv4 } from 'uuid';
import CardFileBrowser from '@/components/CardFileBrowser.vue';
import UniversalUploadDialog from './UniversalUploadDialog.vue';

interface Props {
  package: ContentPackageFile;
  saving: boolean;
}

interface Emits {
  (e: 'save'): void;
  (e: 'update:package', value: ContentPackageFile): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const message = useMessage();
const { t } = useI18n();

// 编辑器状态
const showEditMetaDialog = ref(false);
const showAddCardDialog = ref(false);
const editFormRef = ref<FormInst | null>(null);

// 上传页面状态
const showUploadPage = ref(false);
const currentUploadType = ref<'banner' | 'card' | 'encounter'>('card');
const currentUploadItem = ref<any>(null);
const currentUploadItems = ref<any[]>([]);
const isCurrentUploadBatch = ref(false);
const uploadDialogRef = ref<any>(null);

// 上传云端状态 (保留用于兼容)
const showUploadBannerDialog = ref(false);
const showUploadCardDialog = ref(false);
const showBatchUploadDialog = ref(false);
const uploadingCard = ref<ContentPackageCard | null>(null);
const uploadProgress = ref(0);
const uploadLogs = ref<string[]>([]);
const isUploading = ref(false);
const isBannerUploading = ref(false);
const isCardUploading = ref(false);

// 批量上传状态
const batchUploading = ref(false);
const batchUploadProgress = ref(0);
const batchUploadStatus = ref('');

// 文件输入框引用
const editFileInputRef = ref<HTMLInputElement | null>(null);

// 上传对话框引用
const bannerUploadDialogRef = ref<any>(null);
const cardUploadDialogRef = ref<any>(null);
const batchUploadDialogRef = ref<any>(null);
const encounterUploadDialogRef = ref<any>(null);
const batchEncounterUploadDialogRef = ref<any>(null);


// 遭遇组相关状态
const encounters = ref<EncounterSet[]>([]);
const refreshingEncounters = ref(false);
const showUploadEncounterDialog = ref(false);
const showBatchEncounterUploadDialog = ref(false);
const uploadingEncounter = ref<EncounterSet | null>(null);
const isEncounterUploading = ref(false);

// 拖动排序相关状态
const draggedEncounter = ref<EncounterSet | null>(null);
const dragOverEncounter = ref<EncounterSet | null>(null);

// 遭遇组批量上传状态
const batchEncounterUploading = ref(false);
const batchEncounterUploadProgress = ref(0);
const batchEncounterUploadStatus = ref('');

// 标签编辑对话框状态
const showEditTagsDialog = ref(false);
const editingCard = ref<ContentPackageCard | null>(null);
const editTagsFormRef = ref<any>(null);
const editTagsForm = ref({
  permanent: false,
  exceptional: false,
  myriad: false,
  exile: false
});

// 自动编号相关状态
const numberingStartNumber = ref(1);
const numberingNoEncounterPosition = ref<'before' | 'after'>('before');
const numberingFooterCopyright = ref('');
const numberingFooterIconPath = ref('');
const numberingPlan = ref<any[]>([]);
const numberingLogs = ref<string[]>([]);
const generatingPlan = ref(false);
const applyingPlan = ref(false);

// 底标图标选项
const footerIconOptions = ref<Array<{ label: string; value: string }>>([]);

// TTS导出状态
const exportingToTts = ref(false);
const showExportLogsDialog = ref(false);
const exportLogs = ref<string[]>([]);
const exportResult = ref<any>(null);

// ArkhamDB导出状态
const exportingToArkhamdb = ref(false);
const showArkhamdbExportLogsDialog = ref(false);
const arkhamdbExportLogs = ref<string[]>([]);
const arkhamdbExportResult = ref<any>(null);

// PNP导出状态
const exportingToPnp = ref(false);
const pnpExportLogs = ref<string[]>([]);
const pnpExportResult = ref<any>(null);
const pnpExportMode = ref<'single_card' | 'print_sheet' | 'images'>('single_card');
const pnpPaperSize = ref('A4');
const pnpOutputFilename = ref('pnp_export');
const pnpExportParams = ref({
  format: 'PNG',
  dpi: 300,
  size: '63.5mm × 88.9mm (2.5″ × 3.5″)',
  bleed: 2,
  bleed_mode: '裁剪',
  bleed_model: '镜像出血',
  quality: 95,
  saturation: 1.0,
  brightness: 1.0,
  gamma: 1.0,
  encounter_group_mode: 'range', // 'classic' (经典模式-独立编号) 或 'range' (范围模式-复制图片)
  prefix: '' // 文件名前缀(仅在images模式下使用)
});

// PNP导出选项
const paperSizeOptions = computed(() => [
  { label: t('contentPackage.pnp.paperSizes.a4'), value: 'A4' },
  { label: t('contentPackage.pnp.paperSizes.a3'), value: 'A3' },
  { label: t('contentPackage.pnp.paperSizes.letter'), value: 'Letter' }
]);

const cardSizeOptions = computed(() => [
  { label: t('contentPackage.pnp.cardSizes.size61x88'), value: '61mm × 88mm' },
  { label: t('contentPackage.pnp.cardSizes.size61_5x88'), value: '61.5mm × 88mm' },
  { label: t('contentPackage.pnp.cardSizes.size62x88'), value: '62mm × 88mm' },
  { label: t('contentPackage.pnp.cardSizes.poker'), value: '63.5mm × 88.9mm (2.5″ × 3.5″)' }
]);

const bleedOptions = computed(() => [
  { label: t('contentPackage.pnp.exportParams.noBleed'), value: 0 },
  { label: '2mm', value: 2 },
  { label: '3mm', value: 3 }
]);

const bleedModeOptions = computed(() => [
  { label: t('contentPackage.pnp.exportParams.crop'), value: '裁剪' },
  { label: t('contentPackage.pnp.exportParams.stretch'), value: '拉伸' }
]);

const bleedModelOptions = computed(() => [
  { label: t('contentPackage.pnp.exportParams.mirror'), value: '镜像出血' },
  { label: t('contentPackage.pnp.exportParams.lama'), value: 'LaMa模型出血' }
]);

const encounterGroupModeOptions = computed(() => [
  { label: t('contentPackage.pnp.encounterGroupMode.range'), value: 'range' },
  { label: t('contentPackage.pnp.encounterGroupMode.classic'), value: 'classic' }
]);

const formatOptions = [
  { label: 'PNG', value: 'PNG' },
  { label: 'JPG', value: 'JPG' }
];

// 卡牌预览生成队列
const previewGenerationQueue = ref<string[]>([]);
const isGeneratingPreview = ref(false);

// 运行时卡牌状态管理（不保存到文件）
const cardStatusMap = ref<Map<string, {
  version: string;
  previewImage?: string;
  isGenerating: boolean;
  generationError?: string;
}>>(new Map());

// 编辑表单数据
const editForm = ref({
  name: '',
  description: '',
  author: '',
  external_link: '',
  banner_url: '',
  banner_base64: '',
  language: 'zh' as 'zh' | 'en',
  types: [] as PackageType[],
  status: 'final' as 'draft' | 'alpha' | 'beta' | 'complete' | 'final'
});

// 响应式的包数据
const packageData = computed({
  get: () => props.package,
  set: (value) => emit('update:package', value)
});

// 中止预览生成队列
const abortPreviewGeneration = () => {
  previewGenerationQueue.value = [];
  isGeneratingPreview.value = false;

  // 清除所有正在生成状态
  for (const [filename, status] of cardStatusMap.value.entries()) {
    if (status.isGenerating) {
      cardStatusMap.value.set(filename, {
        ...status,
        isGenerating: false,
        generationError: t('contentPackage.cards.status.generationStopped')
      });
    }
  }
};

// 表单验证规则
const editRules = computed((): FormRules => ({
  name: [
    { required: true, message: t('contentPackage.forms.validation.nameRequired'), trigger: ['input', 'blur'] },
    { min: 1, max: 100, message: t('contentPackage.forms.validation.nameLength'), trigger: ['input', 'blur'] }
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
      validator: (rule: any, value: PackageType[]) => {
        // 确保值是数组并且长度大于0
        if (!Array.isArray(value)) {
          return false;
        }
        return value.length > 0;
      },
      message: t('contentPackage.forms.validation.atLeastOneType'),
      trigger: ['change', 'blur']
    }
  ],
  status: [
    { required: true, message: t('contentPackage.forms.validation.statusRequired'), trigger: ['change', 'blur'] }
  ]
}));

// 获取内容包类型标签
const getPackageTypeLabel = (type: PackageType): string => {
  const option = localizedPackageTypeOptions.value.find(opt => opt.value === type);
  return option ? option.label : type;
};

// 获取内容包类型标签颜色
const getTypeTagColor = (type: PackageType): string => {
  const colorMap = {
    investigators: 'info',
    player_cards: 'success',
    campaign: 'error'
  };
  return colorMap[type] || 'default';
};

// 本地化的选项计算属性
const localizedPackageTypeOptions = computed(() => getPackageTypeOptions(t));
const localizedLanguageOptions = computed(() => getLanguageOptions(t));
const localizedStatusOptions = computed(() => getStatusOptions(t));

// 获取状态标签文本
const getStatusLabel = (status: string): string => {
  const statusOption = localizedStatusOptions.value.find(opt => opt.value === status);
  return statusOption ? statusOption.label : status;
};

// 获取状态标签颜色
const getStatusTagType = (status: string): string => {
  const colorMap = {
    draft: 'warning',
    alpha: 'info',
    beta: 'info',
    complete: 'success',
    final: 'success'
  };
  return colorMap[status as keyof typeof colorMap] || 'default';
};

// 格式化日期
const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleString('zh-CN');
  } catch {
    return dateString;
  }
};

// 打开外部链接
const openExternalLink = () => {
  if (packageData.value?.meta?.external_link) {
    window.open(packageData.value.meta.external_link, '_blank');
  }
};

// 处理保存
const handleSave = () => {
  emit('save', false);
};

// 处理编辑封面上传
const handleEditBannerUpload = async (data: { file: UploadFileInfo, fileList: UploadFileInfo[] }) => {
  if (data.file.file) {
    handleEditFileUpload(data.file.file);
  }
};

// 处理编辑封面移除
const handleEditBannerRemove = () => {
  editForm.value.banner_base64 = '';
};

// 触发编辑文件输入框
const triggerEditFileInput = () => {
  editFileInputRef.value?.click();
};

// 处理编辑文件输入框变化
const handleEditFileInputChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    handleEditFileUpload(file);
  }
  // 清空输入框，允许重复选择同一个文件
  target.value = '';
};

// 处理编辑文件上传
const handleEditFileUpload = (file: File) => {
  try {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        editForm.value.banner_base64 = e.target.result as string;
      }
    };
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('读取封面文件失败:', error);
    message.error(t('contentPackage.messages.readBannerFailed'));
  }
};

// 保存元数据更改
const saveMetaChanges = () => {
  if (!editFormRef.value) return;

  editFormRef.value.validate((errors) => {
    if (!errors) {
      // 更新包数据
      const updatedPackage = {
        ...packageData.value,
        meta: {
          ...packageData.value?.meta,
          name: editForm.value.name,
          description: editForm.value.description,
          author: editForm.value.author,
          language: editForm.value.language,
          types: editForm.value.types,
          status: editForm.value.status,
          external_link: editForm.value.external_link,
          banner_url: editForm.value.banner_url,
          date_updated: new Date().toISOString()
        },
        banner_base64: editForm.value.banner_base64 || packageData.value?.banner_base64
      };

      emit('update:package', updatedPackage);
      closeEditDialog();
      message.success(t('contentPackage.editor.editMeta.saveSuccess'));

      // 直接触发保存到文件，避免用户需要再次点击保存按钮
      emit('save', true);
    }
  });
};

// 关闭编辑对话框
const closeEditDialog = () => {
  showEditMetaDialog.value = false;
  editFormRef.value?.restoreValidation();
};

// 打开编辑对话框时初始化表单数据
const openEditDialog = () => {
  editForm.value = {
    name: packageData.value?.meta?.name || '',
    description: packageData.value?.meta?.description || '',
    author: packageData.value?.meta?.author || '',
    language: packageData.value?.meta?.language || 'zh',
    types: packageData.value?.meta?.types || [],
    status: packageData.value?.meta?.status || 'final',
    external_link: packageData.value?.meta?.external_link || '',
    banner_url: packageData.value?.meta?.banner_url || '',
    banner_base64: packageData.value?.banner_base64 || ''
  };
  showEditMetaDialog.value = true;
};

// 监听显示编辑对话框的变化
watch(showEditMetaDialog, (show) => {
  if (show) {
    openEditDialog();
  }
});

// 获取卡牌运行时状态
const getCardStatus = (filename: string) => {
  try {
    if (!cardStatusMap.value.has(filename)) {
      cardStatusMap.value.set(filename, {
        version: '1.0',
        isGenerating: false,
        generationError: undefined,
        previewImage: undefined
      });
    }
    return cardStatusMap.value.get(filename)!;
  } catch (error) {
    console.error('获取卡牌状态时出错:', error);
    return {
      version: '1.0',
      isGenerating: false,
      generationError: undefined,
      previewImage: undefined
    };
  }
};

// 卡牌管理相关方法

// 处理添加卡牌
const handleAddCards = async (items: any[]) => {
  try {
    const newCards: ContentPackageCard[] = [];

    // 处理选中的项目（文件夹和文件）
    for (const item of items) {
      if (item.type === 'directory') {
        // 如果是文件夹，递归获取所有.card文件
        const folderCards = await getCardsFromFolder(item.path);
        newCards.push(...folderCards);
      } else if (item.type === 'card') {
        // 如果是单个文件，读取版本信息
        const cardInfo = await getCardInfo(item.path);
        newCards.push(cardInfo);
      }
    }

    // 合并到现有卡牌列表（去重）
    const existingCards = packageData.value?.cards || [];
    const allCards = [...existingCards];

    for (const newCard of newCards) {
      if (!allCards.some(card => card.filename === newCard.filename)) {
        allCards.push(newCard);
      }
    }

    // 更新包数据
    const updatedPackage = {
      ...packageData.value,
      cards: allCards
    };

    emit('update:package', updatedPackage);

    // 立即更新 cardStatusMap 以确保UI显示正确的版本信息
    newCards.forEach(card => {
      cardStatusMap.value.set(card.filename, {
        version: card.version,
        isGenerating: false,
        generationError: undefined,
        previewImage: undefined
      });
    });

    // 开始生成预览图（仅对version 2.0的卡牌）
    startPreviewGeneration(newCards.filter(card => card.version === '2.0'));

    message.success(t('contentPackage.messages.addCardSuccess', { count: newCards.length }));
  } catch (error) {
    console.error('添加卡牌失败:', error);
    message.error(t('contentPackage.messages.addCardFailed'));
  }
};

// 从文件夹获取所有卡牌
const getCardsFromFolder = async (folderPath: string): Promise<ContentPackageCard[]> => {
  try {
    const response = await WorkspaceService.getFileTree(false);
    const cards: ContentPackageCard[] = [];

    const findCardsInFolder = (node: any): void => {
      if (node.path === folderPath && node.children) {
        // 找到目标文件夹，收集所有.card文件
        node.children.forEach((child: any) => {
          if (child.type === 'card' || (child.type === 'file' && child.label.endsWith('.card'))) {
            const cardInfo = {
              filename: child.path,
              version: '1.0' // 默认版本，后续会更新
            };
            cards.push(cardInfo);
          }
        });
      } else if (node.children) {
        // 递归查找
        node.children.forEach((child: any) => {
          findCardsInFolder(child);
        });
      }
    };

    findCardsInFolder(response.fileTree);

    // 读取每张卡牌的版本信息
    for (const card of cards) {
      try {
        const versionInfo = await checkCardVersion(card.filename);
        card.version = versionInfo.version;
      } catch (error) {
        card.version = '1.0';
      }
    }

    return cards;
  } catch (error) {
    console.error('获取文件夹卡牌失败:', error);
    return [];
  }
};

// 获取单个卡牌信息
const getCardInfo = async (filePath: string): Promise<ContentPackageCard> => {
  try {
    const versionInfo = await checkCardVersion(filePath);

    return {
      filename: filePath,
      version: versionInfo.version
    };
  } catch (error) {
    return {
      filename: filePath,
      version: '1.0'
    };
  }
};

// 删除卡牌
const removeCard = (index: number) => {
  const updatedPackage = {
    ...packageData.value,
    cards: [...(packageData.value?.cards || [])]
  };

  updatedPackage.cards?.splice(index, 1);
  emit('update:package', updatedPackage);

  message.success(t('contentPackage.messages.cardDeleted'));
};

// 检查卡牌是否有URL（云端或本地）
const hasAnyUrls = (card: ContentPackageCard): boolean => {
  return !!(card.front_url || card.back_url);
};

// 检查卡牌是否有云端URL
const hasCloudUrls = (card: ContentPackageCard): boolean => {
  const frontIsCloud = !!(card.front_url?.startsWith('http://') || card.front_url?.startsWith('https://'));
  const backIsCloud = !!(card.back_url?.startsWith('http://') || card.back_url?.startsWith('https://'));
  // 只有双面都是云端地址时才算云端状态
  return frontIsCloud && backIsCloud;
};

// 检查卡牌是否有本地URL
const hasLocalUrls = (card: ContentPackageCard): boolean => {
  return !!(card.front_url?.startsWith('file:///') || card.back_url?.startsWith('file:///'));
};

// 检查卡牌是否有任何标签
const hasAnyTags = (card: ContentPackageCard): boolean => {
  return !!(card.permanent || card.exceptional || card.myriad || card.exile);
};

// 检查表单是否有任何标签
const hasAnyFormTags = (): boolean => {
  return !!(editTagsForm.value.permanent || editTagsForm.value.exceptional ||
           editTagsForm.value.myriad || editTagsForm.value.exile);
};

// 遭遇组相关方法
// 检查遭遇组是否有云端URL
const hasCloudUrl = (encounter: EncounterSet): boolean => {
  return !!(encounter.icon_url?.startsWith('http://') || encounter.icon_url?.startsWith('https://'));
};

// 检查遭遇组是否有本地URL
const hasLocalUrl = (encounter: EncounterSet): boolean => {
  return !!(encounter.icon_url?.startsWith('file:///'));
};

// 计算属性：检查是否可以导出到TTS
const canExportToTts = computed(() => {
  return cardsWithAnyUrls.value.length > 0;
});

// 计算属性：获取已上传云端图片的卡牌
const cardsWithCloudUrls = computed(() => {
  if (!packageData.value?.cards) return [];
  return packageData.value.cards.filter(card => hasCloudUrls(card));
});

// 计算属性：获取有任意图片URL的卡牌（云端或本地）
const cardsWithAnyUrls = computed(() => {
  if (!packageData.value?.cards) return [];
  return packageData.value.cards.filter(card => hasAnyUrls(card));
});

// 获取卡牌导出状态
const getCardExportStatus = (card: ContentPackageCard) => {
  if (hasCloudUrls(card)) {
    return {
      type: 'success' as const,
      text: t('contentPackage.upload.status.cloud'),
      icon: CloudOutline,
      color: '#18a058'
    };
  } else if (hasLocalUrls(card)) {
    return {
      type: 'info' as const,
      text: t('contentPackage.upload.status.local'),
      icon: FolderOutline,
      color: '#2080f0'
    };
  } else {
    return {
      type: 'warning' as const,
      text: t('contentPackage.upload.status.noImage'),
      icon: WarningOutline,
      color: '#f0a020'
    };
  }
};

// 获取日志项的CSS类
const getLogItemClass = (log: string) => {
  const classes = [];

  // 空行检测（只包含空格或空字符串）
  if (!log || log.trim() === '') {
    classes.push('log-spacer');
    return classes.join(' ');
  }

  // 分隔线
  if (log.includes('━━━') || log.includes('──')) classes.push('log-divider');

  // 状态标识
  if (log.includes('✅') || log.includes('✓')) classes.push('log-success');
  if (log.includes('❌') || log.includes('✗')) classes.push('log-error');
  if (log.includes('⏳')) classes.push('log-processing');
  if (log.includes('💡')) classes.push('log-tip');
  if (log.includes('🚀')) classes.push('log-start');
  if (log.includes('🎉')) classes.push('log-complete');
  if (log.includes('📂')) classes.push('log-file');
  if (log.includes('💾')) classes.push('log-save');

  // 内容类型标识
  if (log.includes('📦')) classes.push('log-package');
  if (log.includes('📊') || log.includes('📏') || log.includes('📐')) classes.push('log-stats');
  if (log.includes('☁️')) classes.push('log-cloud');
  if (log.includes('💻')) classes.push('log-local');

  // 配置和参数
  if (log.includes('🎨') || log.includes('📄') || log.includes('✂️') || log.includes('🎯')) classes.push('log-stats');

  return classes.join(' ');
};

// 计算属性：所有v2.0卡牌
const v2Cards = computed(() => {
  if (!packageData.value?.cards) return [];
  return packageData.value.cards.filter(card => {
    const status = getCardStatus(card.filename);
    return status.version === '2.0';
  });
});

// 计算属性：已上传云端的v2.0卡牌
const v2CardsWithCloudUrls = computed(() => {
  if (!packageData.value?.cards) return [];
  return packageData.value.cards.filter(card => {
    const status = getCardStatus(card.filename);
    return status.version === '2.0' && hasCloudUrls(card);
  });
});

// 计算属性：未上传云端的v2.0卡牌
const v2CardsWithoutCloudUrls = computed(() => {
  if (!packageData.value?.cards) return [];
  return packageData.value.cards.filter(card => {
    const status = getCardStatus(card.filename);
    return status.version === '2.0' && !hasCloudUrls(card);
  });
});

// 计算属性：检查是否有v2.0卡牌需要上传
const hasV2CardsWithoutCloudUrls = computed(() => {
  return v2CardsWithoutCloudUrls.value.length > 0;
});

// 遭遇组相关计算属性
// 计算属性：已上传云端的遭遇组
const encountersWithCloudUrls = computed(() => {
  if (!encounters.value) return [];
  return encounters.value.filter(encounter => hasCloudUrl(encounter));
});

// 计算属性：未上传云端的遭遇组
const encountersWithoutCloudUrls = computed(() => {
  if (!encounters.value) return [];
  return encounters.value.filter(encounter => !hasCloudUrl(encounter));
});

// 上传配置
const uploadConfig = computed(() => {
  return {
    name: packageData.value?.meta?.name || '',
    path: packageData.value?.path || '',
    banner_base64: packageData.value?.banner_base64 || '',
    meta: packageData.value?.meta || {},
    cards: packageData.value?.cards || []
  };
});

// 自动编号表格列定义
const numberingTableColumns = computed(() => [
  {
    title: t('contentPackage.numbering.table.cardNumber'),
    key: 'card_number',
    width: 80,
    align: 'center' as const
  },
  {
    title: t('contentPackage.numbering.table.filename'),
    key: 'filename',
    width: 200,
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: t('contentPackage.numbering.table.name'),
    key: 'name',
    width: 150,
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: t('contentPackage.numbering.table.type'),
    key: 'type',
    width: 100
  },
  {
    title: t('contentPackage.numbering.table.encounterGroup'),
    key: 'encounter_group',
    width: 120,
    render: (row: any) => {
      return row.encounter_group || '-';
    }
  },
  {
    title: t('contentPackage.numbering.table.encounterGroupNumber'),
    key: 'encounter_group_number',
    width: 100,
    align: 'center' as const,
    render: (row: any) => {
      return row.encounter_group_number || '-';
    }
  },
  {
    title: t('contentPackage.numbering.table.quantity'),
    key: 'quantity',
    width: 60,
    align: 'center' as const
  }
]);

// 计算属性：检查是否有任何上传正在进行
const isAnyUploading = computed(() => {
  return isBannerUploading.value || isCardUploading.value || isEncounterUploading.value ||
         batchUploading.value || batchEncounterUploading.value;
});

// 打开封面上传页面
const openBannerUploadPage = () => {
  currentUploadType.value = 'banner';
  currentUploadItem.value = { banner_base64: packageData.value.banner_base64, meta: packageData.value.meta };
  currentUploadItems.value = [];
  isCurrentUploadBatch.value = false;
  showUploadPage.value = true;
};

// 打开单个卡牌上传页面
const openCardUploadPage = (card: ContentPackageCard) => {
  currentUploadType.value = 'card';
  currentUploadItem.value = card;
  currentUploadItems.value = [];
  isCurrentUploadBatch.value = false;
  uploadingCard.value = card;
  showUploadPage.value = true;
};

// 打开批量卡牌上传页面
const openCardBatchUploadPage = () => {
  currentUploadType.value = 'card';
  currentUploadItem.value = null;
  currentUploadItems.value = v2Cards.value;
  isCurrentUploadBatch.value = true;
  showUploadPage.value = true;
};

// 打开单个遭遇组上传页面
const openEncounterUploadPage = (encounter: EncounterSet) => {
  currentUploadType.value = 'encounter';
  currentUploadItem.value = encounter;
  currentUploadItems.value = [];
  isCurrentUploadBatch.value = false;
  uploadingEncounter.value = encounter;
  showUploadPage.value = true;
};

// 打开批量遭遇组上传页面
const openEncounterBatchUploadPage = () => {
  currentUploadType.value = 'encounter';
  currentUploadItem.value = null;
  currentUploadItems.value = encounters.value;
  isCurrentUploadBatch.value = true;
  showUploadPage.value = true;
};

// 关闭上传页面
const closeUploadPage = () => {
  showUploadPage.value = false;
  currentUploadItem.value = null;
  currentUploadItems.value = [];
  uploadingCard.value = null;
  uploadingEncounter.value = null;
};

// 获取上传页面标题
const getUploadPageTitle = (): string => {
  if (currentUploadType.value === 'banner') {
    return t('contentPackage.upload.title.uploadBannerToCloud');
  } else if (currentUploadType.value === 'card') {
    return isCurrentUploadBatch.value
      ? t('contentPackage.upload.title.batchUploadToCloud')
      : t('contentPackage.upload.title.uploadCardToCloud');
  } else if (currentUploadType.value === 'encounter') {
    return isCurrentUploadBatch.value
      ? t('contentPackage.upload.title.batchUploadEncountersToCloud')
      : t('contentPackage.upload.title.uploadEncounterToCloud');
  }
  return t('contentPackage.upload.title.upload');
};

// 获取上传按钮文本
const getUploadButtonText = (): string => {
  if (isCurrentUploadBatch.value) {
    return t('contentPackage.upload.action.startConfiguration', { count: currentUploadItems.value.length });
  }
  return t('contentPackage.upload.action.startUpload');
};

// 触发上传
const triggerUpload = () => {
  if (uploadDialogRef.value) {
    if (currentUploadType.value === 'banner') {
      isBannerUploading.value = true;
    } else if (currentUploadType.value === 'card') {
      if (isCurrentUploadBatch.value) {
        batchUploading.value = true;
      } else {
        isCardUploading.value = true;
      }
    } else if (currentUploadType.value === 'encounter') {
      if (isCurrentUploadBatch.value) {
        batchEncounterUploading.value = true;
      } else {
        isEncounterUploading.value = true;
      }
    }
    uploadDialogRef.value.handleConfirm();
  }
};

// 处理上传确认
const handleUploadConfirm = (updatedPackage: any) => {
  if (currentUploadType.value === 'banner') {
    isBannerUploading.value = false;
  } else if (currentUploadType.value === 'card') {
    if (isCurrentUploadBatch.value) {
      batchUploading.value = false;
    } else {
      isCardUploading.value = false;
    }
  } else if (currentUploadType.value === 'encounter') {
    if (isCurrentUploadBatch.value) {
      batchEncounterUploading.value = false;
    } else {
      isEncounterUploading.value = false;
    }
  }

  // 更新包数据
  emit('update:package', updatedPackage);

  // 更新本地遭遇组状态
  if (currentUploadType.value === 'encounter') {
    encounters.value = updatedPackage.encounter_sets || [];
  }

  // 直接触发保存到文件
  emit('save', true);

  // 不自动关闭上传页面，让用户查看日志后手动返回
  // closeUploadPage();

  // 显示成功消息
  if (currentUploadType.value === 'banner') {
    message.success(t('contentPackage.messages.bannerUploadSuccess'));
  } else if (currentUploadType.value === 'card') {
    if (isCurrentUploadBatch.value) {
      message.success(t('contentPackage.messages.batchUploadSuccess', { count: currentUploadItems.value.length }));
    } else {
      message.success(t('contentPackage.messages.cardUploadSuccess'));
    }
  } else if (currentUploadType.value === 'encounter') {
    if (isCurrentUploadBatch.value) {
      message.success(t('contentPackage.encounters.success.batchUploadSuccess', { count: currentUploadItems.value.length }));
    } else {
      message.success(t('contentPackage.encounters.success.uploadSuccess'));
    }
  }
};

// 显示上传卡牌对话框 (废弃,保留用于兼容)
const openUploadCardDialog = (card: ContentPackageCard) => {
  openCardUploadPage(card);
};

// 打开遭遇组上传对话框 (废弃,保留用于兼容)
const openUploadEncounterDialog = (encounter: EncounterSet) => {
  openEncounterUploadPage(encounter);
};

// 触发封面上传 (废弃,保留用于兼容)
const triggerBannerUpload = () => {
  isBannerUploading.value = true;
  if (bannerUploadDialogRef.value) {
    bannerUploadDialogRef.value.handleConfirm();
  }
};

// 触发卡牌上传
const triggerCardUpload = () => {
  isCardUploading.value = true;
  if (cardUploadDialogRef.value) {
    cardUploadDialogRef.value.handleConfirm();
  }
};

// 处理封面上传
const handleUploadBanner = (updatedPackage: any) => {
  isBannerUploading.value = false;
  showUploadBannerDialog.value = false;

  // 更新包数据
  emit('update:package', updatedPackage);

  // 直接触发保存到文件
  emit('save', true);

  message.success(t('contentPackage.messages.bannerUploadSuccess'));
};

// 处理卡牌上传
const handleUploadCard = (updatedPackage: any) => {
  isCardUploading.value = false;
  showUploadCardDialog.value = false;
  uploadingCard.value = null;

  // 更新包数据
  emit('update:package', updatedPackage);

  // 直接触发保存到文件
  emit('save', true);

  message.success(t('contentPackage.messages.cardUploadSuccess'));
};

// 触发批量上传
const triggerBatchUpload = () => {
  batchUploading.value = true;
  if (batchUploadDialogRef.value) {
    batchUploadDialogRef.value.handleConfirm();
  }
};

// 处理批量上传
const handleBatchUpload = (updatedPackage: any) => {
  batchUploading.value = false;
  showBatchUploadDialog.value = false;

  // 更新包数据
  emit('update:package', updatedPackage);

  // 直接触发保存到文件
  emit('save', true);

};

// 打开标签编辑对话框
const openEditTagsDialog = (card: ContentPackageCard) => {
  editingCard.value = card;
  editTagsForm.value = {
    permanent: card.permanent || false,
    exceptional: card.exceptional || false,
    myriad: card.myriad || false,
    exile: card.exile || false
  };
  showEditTagsDialog.value = true;
};

// 关闭标签编辑对话框
const closeEditTagsDialog = () => {
  showEditTagsDialog.value = false;
  editingCard.value = null;
  editTagsFormRef.value?.restoreValidation();
};

// 保存标签更改
const saveTagsChanges = () => {
  if (!editingCard.value) return;

  // 更新包数据中的卡牌标签
  const updatedPackage = { ...packageData.value };
  const cardIndex = updatedPackage.cards?.findIndex(c => c.filename === editingCard.value!.filename);

  if (cardIndex !== undefined && cardIndex >= 0) {
    updatedPackage.cards![cardIndex] = {
      ...updatedPackage.cards![cardIndex],
      permanent: editTagsForm.value.permanent,
      exceptional: editTagsForm.value.exceptional,
      myriad: editTagsForm.value.myriad,
      exile: editTagsForm.value.exile
    };

    // 更新包数据
    emit('update:package', updatedPackage);

    // 直接触发保存到文件
    emit('save', true);

    closeEditTagsDialog();
    message.success(t('contentPackage.common.cardTagsSaved'));
  }
};

// 开始批量上传
const startBatchUpload = async () => {
  if (v2Cards.value.length === 0) {
    message.warning(t('contentPackage.messages.noCardsToUpload'));
    return;
  }

  batchUploading.value = true;
  batchUploadProgress.value = 0;
  batchUploadStatus.value = t('contentPackage.messages.batchPreparing');

  const cardsToUpload = v2Cards.value;  // 改为使用所有v2卡牌
  const totalCards = cardsToUpload.length;
  let successCount = 0;
  let failureCount = 0;

  try {
    // 获取图床配置
    const config = await ConfigService.getConfig();

    // 验证配置
    const selectedHost = config.cloud_name ? 'cloudinary' : 'imgbb';
    let configValid = false;

    if (selectedHost === 'cloudinary') {
      configValid = !!(config.cloud_name && config.api_key && config.api_secret);
    } else {
      configValid = !!config.imgbb_api_key;
    }

    if (!configValid) {
      message.error(t('contentPackage.messages.imageHostConfigIncomplete'));
      batchUploading.value = false;
      return;
    }

    batchUploadStatus.value = t('contentPackage.messages.batchStarting');

    // 逐个上传卡牌
    for (let i = 0; i < cardsToUpload.length; i++) {
      const card = cardsToUpload[i];

      try {
        batchUploadStatus.value = t('contentPackage.messages.batchUploading', { filename: card.filename, index: i + 1, total: totalCards });

        // 读取卡牌数据
        const cardData = await WorkspaceService.getFileContent(card.filename);
        const parsedCard = JSON.parse(cardData);

        // 导出图片到工作目录
        const savedFiles = await CardService.saveCardEnhanced(parsedCard, card.filename.replace('.card', ''), {
          parentPath: '.cards',
          format: 'JPG',
          quality: 95,
          rotateLandscape: true  // 内容包导出时自动旋转横向图片
        });

        // 上传图片
        const uploadedUrls: { front?: string; back?: string } = {};

        if (savedFiles.length > 0) {
          // 清理文件名，移除路径分隔符和特殊字符
          const cleanCardName = card.filename.replace(/.*[\/\\]/, '').replace('.card', '');
          const frontOnlineName = `${cleanCardName}_front`;

          const frontResult = await ImageHostService.smartUpload(
            savedFiles[0],
            selectedHost,
            frontOnlineName
          );
          if (frontResult.code === 0 && frontResult.data?.url) {
            uploadedUrls.front = frontResult.data.url;
          }
        }

        if (savedFiles.length > 1) {
          // 清理文件名，移除路径分隔符和特殊字符
          const cleanCardName = card.filename.replace(/.*[\/\\]/, '').replace('.card', '');
          const backOnlineName = `${cleanCardName}_back`;

          const backResult = await ImageHostService.smartUpload(
            savedFiles[1],
            selectedHost,
            backOnlineName
          );
          if (backResult.code === 0 && backResult.data?.url) {
            uploadedUrls.back = backResult.data.url;
          }
        }

        // 更新卡牌的云端URL
        const updatedPackage = { ...packageData.value };
        const cardIndex = updatedPackage.cards?.findIndex(c => c.filename === card.filename);
        if (cardIndex !== undefined && cardIndex >= 0) {
          updatedPackage.cards![cardIndex] = {
            ...updatedPackage.cards![cardIndex],
            front_url: uploadedUrls.front,
            back_url: uploadedUrls.back
          };
        }

        // 更新包数据
        emit('update:package', updatedPackage);

        successCount++;

        // 更新进度
        batchUploadProgress.value = Math.round(((i + 1) / totalCards) * 100);

      } catch (error) {
        console.error(`上传卡牌失败: ${card.filename}`, error);
        failureCount++;
      }

      // 短暂延迟避免过于频繁的请求
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 保存最终结果
    emit('save', true);

    // 显示结果
    batchUploadStatus.value = t('contentPackage.messages.batchUploadCompleted', { success: successCount, failure: failureCount });

    if (failureCount === 0) {
      message.success(t('contentPackage.messages.batchUploadSuccess', { count: successCount }));
      setTimeout(() => {
        showBatchUploadDialog.value = false;
      }, 2000);
    } else {
      message.warning(t('contentPackage.messages.batchUploadCompleted', { success: successCount, failure: failureCount }));
    }

  } catch (error) {
    console.error('批量上传失败:', error);
    message.error(t('contentPackage.messages.batchUploadFailed'));
    batchUploadStatus.value = t('contentPackage.messages.batchUploadFailed');
  } finally {
    batchUploading.value = false;
  }
};

// 检查单张卡牌的版本
const checkCardVersion = async (filename: string): Promise<{
  version: string;
  isV2: boolean;
  error?: string;
}> => {
  try {
    // 直接读取文件内容来检查版本
    const cardData = await WorkspaceService.getFileContent(filename);
    const parsed = JSON.parse(cardData);
    const version = parsed.version || '1.0';
    const isV2 = version === '2.0';

    return {
      version,
      isV2,
      error: undefined
    };
  } catch (error) {
    return {
      version: '1.0',
      isV2: false,
      error: `读取文件失败: ${error.message}`
    };
  }
};

// 刷新卡牌版本信息
const refreshCardVersions = async () => {
  if (!packageData.value?.cards || packageData.value.cards.length === 0) {
    return;
  }

  const cards = packageData.value.cards;
  const v2Cards: ContentPackageCard[] = [];

  // 首先检查所有卡牌的版本
  for (const card of cards) {
    try {
      // 使用 checkCardVersion 函数来检查版本
      const versionInfo = await checkCardVersion(card.filename);

      cardStatusMap.value.set(card.filename, {
        version: versionInfo.version,
        isGenerating: false,
        generationError: versionInfo.error,
        previewImage: undefined
      });

      // 收集v2.0的卡牌用于预览生成
      if (versionInfo.version === '2.0') {
        v2Cards.push(card);
      }
    } catch (error) {
      cardStatusMap.value.set(card.filename, {
        version: '1.0',
        isGenerating: false,
        generationError: t('contentPackage.cards.status.versionCheckFailed'),
        previewImage: undefined
      });
    }
  }

  // 为所有v2.0的卡牌启动预览生成
  if (v2Cards.length > 0) {
    startPreviewGeneration(v2Cards);
  }
};

// 遭遇组管理方法
// 刷新遭遇组信息
const refreshEncounterGroups = async () => {
  if (!packageData.value?.path) {
    message.error(t('contentPackage.encounters.error.noPackagePath'));
    return;
  }

  refreshingEncounters.value = true;
  try {
    const result = await ContentPackageService.getEncounterGroups(packageData.value.path);

    // 转换API返回的数据为我们的格式
    const apiEncounters = result.encounter_groups || [];
    const existingEncounters = packageData.value.encounter_sets || [];

    // 合并数据，优先使用现有的icon_url和order，补充base64和relative_path
    const mergedEncounters: EncounterSet[] = apiEncounters.map((apiEncounter: any, index: number) => {
      const existing = existingEncounters.find(e => e.name === apiEncounter.name);
      if (existing) {
        return {
          ...existing,
          base64: apiEncounter.base64,
          relative_path: apiEncounter.relative_path,
          // 保留现有的 order，如果没有则使用当前索引
          order: existing.order !== undefined ? existing.order : index
        };
      } else {
        // 生成新的UUID code，并使用当前索引作为初始order
        return {
          code: uuidv4(),
          name: apiEncounter.name,
          base64: apiEncounter.base64,
          relative_path: apiEncounter.relative_path,
          order: index
        };
      }
    });

    // 按 order 排序
    mergedEncounters.sort((a, b) => (a.order || 0) - (b.order || 0));

    // 更新本地状态
    encounters.value = mergedEncounters;

    // 更新包数据
    const updatedPackage = {
      ...packageData.value,
      encounter_sets: mergedEncounters
    };
    emit('update:package', updatedPackage);

    // 触发保存到文件
    emit('save', true);

    message.success(t('contentPackage.encounters.success.refreshSuccess', { count: mergedEncounters.length }));
  } catch (error: any) {
    console.error('刷新遭遇组失败:', error);
    message.error(t('contentPackage.encounters.error.refreshFailed', { message: error.message }));
  } finally {
    refreshingEncounters.value = false;
  }
};

// 拖动排序相关方法
// 开始拖动
const handleDragStart = (encounter: EncounterSet, event: DragEvent) => {
  draggedEncounter.value = encounter;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/html', encounter.code);
  }
};

// 拖动经过
const handleDragOver = (encounter: EncounterSet, event: DragEvent) => {
  event.preventDefault();
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move';
  }
  dragOverEncounter.value = encounter;
};

// 拖动离开
const handleDragLeave = () => {
  dragOverEncounter.value = null;
};

// 放置
const handleDrop = (targetEncounter: EncounterSet, event: DragEvent) => {
  event.preventDefault();

  if (!draggedEncounter.value || draggedEncounter.value.code === targetEncounter.code) {
    draggedEncounter.value = null;
    dragOverEncounter.value = null;
    return;
  }

  // 重新排序遭遇组
  const newEncounters = [...encounters.value];
  const draggedIndex = newEncounters.findIndex(e => e.code === draggedEncounter.value!.code);
  const targetIndex = newEncounters.findIndex(e => e.code === targetEncounter.code);

  if (draggedIndex !== -1 && targetIndex !== -1) {
    // 移除被拖动的元素
    const [removed] = newEncounters.splice(draggedIndex, 1);
    // 插入到目标位置
    newEncounters.splice(targetIndex, 0, removed);

    // 更新所有遭遇组的 order
    const updatedEncounters = newEncounters.map((encounter, index) => ({
      ...encounter,
      order: index
    }));

    // 更新本地状态
    encounters.value = updatedEncounters;

    // 更新包数据
    const updatedPackage = {
      ...packageData.value,
      encounter_sets: updatedEncounters
    };
    emit('update:package', updatedPackage);

    // 触发保存
    emit('save', true);

    message.success(t('contentPackage.encounters.success.orderUpdated'));
  }

  draggedEncounter.value = null;
  dragOverEncounter.value = null;
};

// 拖动结束
const handleDragEnd = () => {
  draggedEncounter.value = null;
  dragOverEncounter.value = null;
};

// 为当前内容包开始预览生成
const startPreviewGenerationForCurrentPackage = async () => {
  try {
    if (!packageData.value?.cards || packageData.value.cards.length === 0) return;

    const validCards = packageData.value.cards.filter(card => {
      const status = getCardStatus(card.filename);
      return status.version === '2.0';
    });

    if (validCards.length === 0) return;

    // 添加到队列
    previewGenerationQueue.value.push(...validCards.map(card => card.filename));

    // 如果当前没有正在生成的，开始生成
    if (!isGeneratingPreview.value) {
      processPreviewQueue();
    }
  } catch (error) {
    // 预览生成失败时的错误处理
  }
};

// 开始预览图生成队列（兼容旧函数）
const startPreviewGeneration = async (cards: ContentPackageCard[]) => {
  const validCards = cards.filter(card => {
    const status = getCardStatus(card.filename);
    return status.version === '2.0';
  });

  if (validCards.length === 0) return;

  // 添加到队列
  previewGenerationQueue.value.push(...validCards.map(card => card.filename));

  // 如果当前没有正在生成的，开始生成
  if (!isGeneratingPreview.value) {
    processPreviewQueue();
  }
};

// 处理预览生成队列
const processPreviewQueue = async () => {
  if (previewGenerationQueue.value.length === 0) {
    isGeneratingPreview.value = false;
    return;
  }

  isGeneratingPreview.value = true;

  while (previewGenerationQueue.value.length > 0) {
    const filename = previewGenerationQueue.value.shift()!;

    try {
      // 标记为正在生成
      cardStatusMap.value.set(filename, {
        ...getCardStatus(filename),
        isGenerating: true,
        generationError: undefined
      });

      // 读取卡牌数据
      const cardData = await WorkspaceService.getFileContent(filename);
      const parsedCard = JSON.parse(cardData);

      // 生成预览图
      const result = await CardService.generateCard(parsedCard);

      // 更新预览图
      cardStatusMap.value.set(filename, {
        ...getCardStatus(filename),
        previewImage: result.image,
        isGenerating: false,
        generationError: undefined
      });

      // 预览图生成成功
    } catch (error) {
      // 预览图生成失败
      cardStatusMap.value.set(filename, {
        ...getCardStatus(filename),
        isGenerating: false,
        generationError: t('contentPackage.cards.status.generating')
      });
    }

    // 短暂延迟避免过于频繁的请求
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  isGeneratingPreview.value = false;
};

// TTS导出方法
const exportToTts = async () => {
  if (!packageData.value?.path) {
    message.error(t('contentPackage.upload.error.packagePathInvalid'));
    return;
  }

  if (!canExportToTts.value) {
    message.warning($t('contentPackage.export.tts.needImages'));
    return;
  }

  exportingToTts.value = true;
  exportLogs.value = [];

  try {
    // 添加调试信息
    console.log('TTS导出调试信息:', {
      packageData: packageData.value,
      packageDataExists: !!packageData.value,
      meta: packageData.value?.meta,
      metaExists: !!packageData.value?.meta,
      cards: packageData.value?.cards,
      cardsLength: packageData.value?.cards?.length,
      canExport: canExportToTts.value,
      cardsWithAnyUrls: cardsWithAnyUrls.value.length
    });

    // 添加开始日志
    exportLogs.value.push('🚀 开始导出到TTS...');
    exportLogs.value.push(`📦 内容包: ${packageData.value?.meta?.name || '未知内容包'}`);
    exportLogs.value.push(`📊 总卡牌数: ${packageData.value?.cards?.length || 0} 张`);
    exportLogs.value.push(`✅ 可导出卡牌: ${cardsWithAnyUrls.value.length} 张`);

    // 统计图片类型
    const cloudCards = cardsWithCloudUrls.value.length;
    const localCards = cardsWithAnyUrls.value.length - cloudCards;
    if (cloudCards > 0) {
      exportLogs.value.push(`☁️ 云端图片: ${cloudCards} 张`);
    }
    if (localCards > 0) {
      exportLogs.value.push(`💻 本地图片: ${localCards} 张`);
    }

    exportLogs.value.push('⏳ 正在处理卡牌数据...');

    const result = await ContentPackageService.exportToTts(packageData.value.path);

    // 添加成功日志
    exportLogs.value.push('✅ TTS物品导出成功！');

    // 确保result有logs属性
    if (result && Array.isArray(result.logs)) {
      // 过滤掉重复的开始日志，避免重复显示
      const backendLogs = result.logs.filter(log =>
        !log.includes('开始导出TTS') &&
        !log.includes('设置盒子信息') &&
        !log.includes('找到') &&
        !log.includes('成功读取卡牌') &&
        !log.includes('成功处理卡牌')
      );

      if (backendLogs.length > 0) {
        exportLogs.value.push(...backendLogs);
      }
    } else {
      exportLogs.value.push('📝 导出完成，但未收到详细处理日志');
    }

    // 添加文件保存信息
    if (result.tts_path) {
      exportLogs.value.push(`📂 TTS文件已保存到: ${result.tts_path}`);
    }
    if (result.local_path) {
      exportLogs.value.push(`💾 本地副本已保存到: ${result.local_path}`);
    }

    // 添加完成提示
    exportLogs.value.push('');
    exportLogs.value.push('🎉 导出完成！您可以在Tabletop Simulator中导入此物品。');
    exportLogs.value.push('💡 提示：导入后请在TTS中检查卡牌图片是否正常显示。');

    exportResult.value = result;
    showExportLogsDialog.value = true;
    message.success(t('contentPackage.export.tts.success.ttsExportSuccess'));

  } catch (error: any) {
    console.error('导出TTS物品失败:', error);

    // 添加错误信息
    exportLogs.value.push('❌ 导出失败！');

    if (error.code === 14002) {
      exportLogs.value.push(`💡 错误原因: ${error.message}`);
      exportLogs.value.push('💡 建议请检查卡牌是否已生成图片');
    } else {
      exportLogs.value.push(`💡 错误原因: ${error.message || '未知错误'}`);
      exportLogs.value.push('💡 建议请检查网络连接或重试导出');
    }

    showExportLogsDialog.value = true;
    message.error('TTS物品导出失败，请查看日志了解详情');
  } finally {
    exportingToTts.value = false;
  }
};

// 打开TTS文件位置
const openTtsFileLocation = () => {
  if (exportResult.value?.local_path) {
    // 提取目录路径
    const dirPath = exportResult.value.local_path.substring(0, exportResult.value.local_path.lastIndexOf('/'));
    if (dirPath) {
      WorkspaceService.openDirectory(dirPath).catch(error => {
        console.error('打开目录失败:', error);
        message.error('无法打开文件夹');
      });
    }
  } else if (exportResult.value?.tts_path) {
    message.info('文件已保存到TTS保存目录，请检查Tabletop Simulator的Saved Objects文件夹');
  }
};

// ArkhamDB导出方法
const exportToArkhamdb = async () => {
  if (!packageData.value?.path) {
    message.error(t('contentPackage.upload.error.packagePathInvalid'));
    return;
  }

  exportingToArkhamdb.value = true;
  arkhamdbExportLogs.value = [];

  try {
    // 添加开始日志
    arkhamdbExportLogs.value.push('🚀 开始导出到ArkhamDB格式...');
    arkhamdbExportLogs.value.push(`📦 内容包: ${packageData.value?.meta?.name || '未知内容包'}`);
    arkhamdbExportLogs.value.push(`📊 总卡牌数: ${packageData.value?.cards?.length || 0} 张`);
    arkhamdbExportLogs.value.push('⏳ 正在处理卡牌数据...');

    const result = await ContentPackageService.exportToArkhamdb(packageData.value.path);

    // 添加成功日志
    arkhamdbExportLogs.value.push('✅ ArkhamDB格式导出成功！');

    // 确保result有logs属性
    if (result && Array.isArray(result.logs)) {
      // 过滤掉重复的开始日志，避免重复显示
      const backendLogs = result.logs.filter(log =>
        !log.includes('开始导出ArkhamDB') &&
        !log.includes('内容包') &&
        !log.includes('总卡牌数')
      );

      if (backendLogs.length > 0) {
        arkhamdbExportLogs.value.push(...backendLogs);
      }
    } else {
      arkhamdbExportLogs.value.push('📝 导出完成，但未收到详细处理日志');
    }

    // 添加文件保存信息
    if (result.output_path) {
      arkhamdbExportLogs.value.push(`📂 ArkhamDB文件已保存到: ${result.output_path}`);
    }

    // 添加完成提示
    arkhamdbExportLogs.value.push('');
    arkhamdbExportLogs.value.push('🎉 导出完成！您可以将此文件用于arkham.build扩展包。');
    arkhamdbExportLogs.value.push('💡 提示：请检查导出的JSON文件格式是否符合arkham.build要求。');

    arkhamdbExportResult.value = result;
    showArkhamdbExportLogsDialog.value = true;
    message.success(t('contentPackage.export.arkhamdb.success.arkhamdbExportSuccess'));

  } catch (error: any) {
    console.error('导出ArkhamDB格式失败:', error);

    // 添加错误信息
    arkhamdbExportLogs.value.push('❌ 导出失败！');

    if (error.code === 14005) {
      arkhamdbExportLogs.value.push(`💡 错误原因: ${error.message}`);
      arkhamdbExportLogs.value.push('💡 建议请检查内容包数据完整性');
    } else {
      arkhamdbExportLogs.value.push(`💡 错误原因: ${error.message || '未知错误'}`);
      arkhamdbExportLogs.value.push('💡 建议请检查网络连接或重试导出');
    }

    showArkhamdbExportLogsDialog.value = true;
    message.error('ArkhamDB格式导出失败，请查看日志了解详情');
  } finally {
    exportingToArkhamdb.value = false;
  }
};

// 打开ArkhamDB文件位置
const openArkhamdbFileLocation = () => {
  if (arkhamdbExportResult.value?.output_path) {
    // 提取目录路径
    const dirPath = arkhamdbExportResult.value.output_path.substring(0, arkhamdbExportResult.value.output_path.lastIndexOf('/'));
    if (dirPath) {
      WorkspaceService.openDirectory(dirPath).catch(error => {
        console.error('打开目录失败:', error);
        message.error('无法打开文件夹');
      });
    }
  }
};

// PNP导出方法
const exportToPnp = async () => {
  if (!packageData.value?.path) {
    message.error(t('contentPackage.pnp.messages.invalidPackagePath'));
    return;
  }

  // 清空之前的日志和结果
  pnpExportLogs.value = [];
  pnpExportResult.value = null;
  exportingToPnp.value = true;

  // 滚动到日志区域（延迟以等待DOM更新）
  await nextTick();
  const logElement = document.querySelector('.physical-export-panel .logs-container');
  if (logElement) {
    logElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // 用于存储任务ID和轮询定时器
  let taskId: string | null = null;
  let pollTimer: NodeJS.Timeout | null = null;
  // 用于存储参数头部日志（静态部分，不会被后端日志覆盖）
  let paramHeaderLogs: string[] = [];

  // 轮询获取日志的函数
  const pollLogs = async () => {
    if (!taskId) return;

    try {
      const logData = await ContentPackageService.getPnpExportLogs(taskId);

      // 合并参数头部和后端日志
      pnpExportLogs.value = [...paramHeaderLogs, ...logData.logs];

      // 滚动到日志底部
      await nextTick();
      // 需要找到 n-scrollbar 内部的滚动容器
      const scrollbarContainer = document.querySelector('.physical-export-panel .n-scrollbar-container');
      if (scrollbarContainer) {
        scrollbarContainer.scrollTop = scrollbarContainer.scrollHeight;
      }

      // 检查状态
      if (logData.status === 'completed') {
        // 导出完成，停止轮询
        if (pollTimer) {
          clearInterval(pollTimer);
          pollTimer = null;
        }

        exportingToPnp.value = false;

        if (logData.result) {
          pnpExportResult.value = logData.result;
          // 根据导出模式显示不同的成功消息
          const successMsg = pnpExportMode.value === 'images'
            ? t('contentPackage.pnp.messages.exportImagesSuccess')
            : t('contentPackage.pnp.messages.exportSuccess');
          message.success(successMsg);
        }

        // 不关闭日志显示，用户可以继续查看日志
      } else if (logData.status === 'failed') {
        // 导出失败，停止轮询
        if (pollTimer) {
          clearInterval(pollTimer);
          pollTimer = null;
        }

        exportingToPnp.value = false;
        message.error(t('contentPackage.pnp.messages.exportFailed') + '，请查看日志了解详情');

        // 不关闭日志显示，用户可以继续查看错误信息
      }
      // 如果status === 'running'，继续轮询
    } catch (error) {
      console.error('获取导出日志失败:', error);
      // 出错时也停止轮询
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
      exportingToPnp.value = false;
    }
  };

  try {
    const modeText = pnpExportMode.value === 'single_card'
      ? t('contentPackage.pnp.exportParams.singleCard')
      : pnpExportMode.value === 'print_sheet'
        ? t('contentPackage.pnp.exportParams.printSheet')
        : t('contentPackage.pnp.exportParams.images');

    // 构建参数头部日志（这部分是静态的，不会被后端日志覆盖）
    paramHeaderLogs = [];
    const exportTypeLabel = pnpExportMode.value === 'images' ? 'PNP 图片' : 'PNP PDF';
    paramHeaderLogs.push(`🚀 开始导出 ${exportTypeLabel}...`);
    paramHeaderLogs.push(' '); // 空行用空格代替空字符串
    paramHeaderLogs.push(`📦 内容包名称: ${packageData.value?.meta?.name || t('contentPackage.common.unnamedPackage')}`);
    paramHeaderLogs.push(' ');
    paramHeaderLogs.push(`📊 卡牌数量: ${packageData.value?.cards?.length || 0}`);
    paramHeaderLogs.push(' ');
    paramHeaderLogs.push(`🎨 导出模式: ${modeText}`);
    paramHeaderLogs.push(' ');
    if (pnpExportMode.value === 'print_sheet') {
      paramHeaderLogs.push(`📄 纸张规格: ${pnpPaperSize.value}`);
      paramHeaderLogs.push(' ');
    }
    if (pnpExportMode.value === 'images' && pnpExportParams.value.prefix) {
      paramHeaderLogs.push(`🏷️ 文件名前缀: ${pnpExportParams.value.prefix}`);
      paramHeaderLogs.push(' ');
    }
    paramHeaderLogs.push(`📐 DPI: ${pnpExportParams.value.dpi}`);
    paramHeaderLogs.push(' ');

    // 解析卡牌规格显示
    const cardSizeText = pnpExportParams.value.size;
    // 尝试从选项中找到对应的标签
    const cardSizeOption = cardSizeOptions.value.find(opt => opt.value === cardSizeText);
    const cardSizeDisplay = cardSizeOption ? cardSizeOption.label : cardSizeText;
    paramHeaderLogs.push(`📏 卡牌规格: ${cardSizeDisplay}`);
    paramHeaderLogs.push(' ');

    // 添加出血信息
    const bleedOption = bleedOptions.value.find(opt => opt.value === pnpExportParams.value.bleed);
    const bleedDisplay = bleedOption ? bleedOption.label : `${pnpExportParams.value.bleed}mm`;
    paramHeaderLogs.push(`✂️ 出血尺寸: ${bleedDisplay}`);
    paramHeaderLogs.push(' ');

    // 添加遭遇组模式信息
    const encounterModeOption = encounterGroupModeOptions.value.find(opt => opt.value === pnpExportParams.value.encounter_group_mode);
    const encounterModeDisplay = encounterModeOption ? encounterModeOption.label : pnpExportParams.value.encounter_group_mode;
    paramHeaderLogs.push(`🎯 遭遇组编号: ${encounterModeDisplay}`);
    paramHeaderLogs.push(' ');

    // 添加分隔线
    paramHeaderLogs.push('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    paramHeaderLogs.push(' ');

    // 先显示参数头部
    pnpExportLogs.value = [...paramHeaderLogs];

    // 启动导出任务（后端会立即返回task_id）
    // 根据导出模式决定文件名格式
    const outputFilename = pnpExportMode.value === 'images'
      ? (pnpOutputFilename.value || 'pnp_images')
      : (pnpOutputFilename.value ? `${pnpOutputFilename.value}.pdf` : 'pnp_export.pdf');

    const result = await ContentPackageService.exportToPnp(
      packageData.value.path,
      pnpExportParams.value,
      outputFilename,
      pnpExportMode.value,
      pnpPaperSize.value
    );

    // 获取任务ID
    taskId = result.task_id || null;

    if (taskId) {
      // 开始轮询日志（每秒一次）
      pollTimer = setInterval(pollLogs, 1000);

      // 立即执行一次
      await pollLogs();
    } else {
      // 没有任务ID，显示错误
      pnpExportLogs.value = [...paramHeaderLogs, '', '❌ 无法启动导出任务：未获取到任务ID'];
      exportingToPnp.value = false;
    }

  } catch (error: any) {
    // 停止轮询
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }

    // 添加错误信息（保留参数头部）
    pnpExportLogs.value = [
      ...paramHeaderLogs,
      '',
      '❌ ' + t('contentPackage.pnp.messages.exportFailed') + '！',
      `💡 错误原因: ${error.message || '未知错误'}`,
      '💡 ' + t('contentPackage.pnp.messages.checkDataIntegrity')
    ];

    message.error(t('contentPackage.pnp.messages.exportFailed') + '，请查看日志了解详情');
    exportingToPnp.value = false;
  }
};

// 打开PNP文件位置
const openPnpFileLocation = () => {
  if (pnpExportResult.value?.output_path) {
    // 提取目录路径
    const dirPath = pnpExportResult.value.output_path.substring(0, pnpExportResult.value.output_path.lastIndexOf('/'));
    if (dirPath) {
      WorkspaceService.openDirectory(dirPath).catch(error => {
        console.error('打开目录失败:', error);
        message.error('无法打开文件夹');
      });
    }
  }
};

// 遭遇组上传相关方法
// 触发遭遇组上传
const triggerEncounterUpload = () => {
  isEncounterUploading.value = true;
  if (encounterUploadDialogRef.value) {
    encounterUploadDialogRef.value.handleConfirm();
  }
};

// 触发遭遇组批量上传
const triggerBatchEncounterUpload = () => {
  batchEncounterUploading.value = true;
  if (batchEncounterUploadDialogRef.value) {
    batchEncounterUploadDialogRef.value.handleConfirm();
  }
};

// 处理遭遇组上传
const handleUploadEncounter = (updatedPackage: any) => {
  isEncounterUploading.value = false;
  showUploadEncounterDialog.value = false;
  uploadingEncounter.value = null;

  // 更新包数据
  emit('update:package', updatedPackage);

  // 更新本地遭遇组状态
  encounters.value = updatedPackage.encounter_sets || [];

  // 直接触发保存到文件
  emit('save', true);

  message.success(t('contentPackage.encounters.success.uploadSuccess'));
};

// 处理遭遇组批量上传
const handleBatchEncounterUpload = (updatedPackage: any) => {
  batchEncounterUploading.value = false;
  showBatchEncounterUploadDialog.value = false;

  // 更新包数据
  emit('update:package', updatedPackage);

  // 更新本地遭遇组状态
  encounters.value = updatedPackage.encounter_sets || [];

  // 直接触发保存到文件
  emit('save', true);
};


// 开始遭遇组批量上传
const startBatchEncounterUpload = async () => {
  if (encounters.value.length === 0) {
    message.warning(t('contentPackage.encounters.error.noEncountersToUpload'));
    return;
  }

  batchEncounterUploading.value = true;
  batchEncounterUploadProgress.value = 0;
  batchEncounterUploadStatus.value = t('contentPackage.encounters.messages.batchPreparing');

  const encountersToUpload = encounters.value;
  const totalEncounters = encountersToUpload.length;
  let successCount = 0;
  let failureCount = 0;

  try {
    // 获取图床配置
    const config = await ConfigService.getConfig();
    const selectedHost = config.cloud_name ? 'cloudinary' : 'imgbb';

    batchEncounterUploadStatus.value = t('contentPackage.encounters.messages.batchStarting');

    // 逐个上传遭遇组图标
    for (let i = 0; i < encountersToUpload.length; i++) {
      const encounter = encountersToUpload[i];

      try {
        batchEncounterUploadStatus.value = t('contentPackage.encounters.messages.batchUploading', {
          name: encounter.name,
          index: i + 1,
          total: totalEncounters
        });

        // 检查是否有图标数据
        if (!encounter.base64 && !encounter.relative_path) {
          console.warn(`遭遇组 ${encounter.name} 没有图标数据，跳过上传`);
          continue;
        }

        // 创建临时文件用于上传
        const onlineName = `${encounter.name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}_icon`;

        let imagePath: string;
        // 优先使用relative_path，如果没有则使用base64
        if (encounter.relative_path) {
          imagePath = encounter.relative_path;
        } else if (encounter.base64) {
          imagePath = encounter.base64;
        } else {
          console.warn(`遭遇组 ${encounter.name} 没有可用的图标数据，跳过上传`);
          continue;
        }

        // 上传图片
        const result = await ImageHostService.smartUpload(
          imagePath,
          selectedHost,
          onlineName
        );

        if (result.code === 0 && result.data?.url) {
          // 更新遭遇组的icon_url
          const updatedPackage = { ...packageData.value };
          const encounterIndex = updatedPackage.encounter_sets?.findIndex(e => e.code === encounter.code);
          if (encounterIndex !== undefined && encounterIndex >= 0) {
            updatedPackage.encounter_sets![encounterIndex] = {
              ...updatedPackage.encounter_sets![encounterIndex],
              icon_url: result.data.url
            };
          }

          // 更新本地状态
          const localEncounterIndex = encounters.value.findIndex(e => e.code === encounter.code);
          if (localEncounterIndex >= 0) {
            encounters.value[localEncounterIndex].icon_url = result.data.url;
          }

          successCount++;
        } else {
          throw new Error(result.msg || '上传失败');
        }

        // 更新进度
        batchEncounterUploadProgress.value = Math.round(((i + 1) / totalEncounters) * 100);

      } catch (error) {
        console.error(`上传遭遇组失败: ${encounter.name}`, error);
        failureCount++;
      }

      // 短暂延迟避免过于频繁的请求
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 保存最终结果
    emit('save', true);

    // 显示结果
    batchEncounterUploadStatus.value = t('contentPackage.encounters.messages.batchUploadCompleted', {
      success: successCount,
      failure: failureCount
    });

    if (failureCount === 0) {
      setTimeout(() => {
        showBatchEncounterUploadDialog.value = false;
      }, 2000);
    } else {
      message.warning(t('contentPackage.encounters.messages.batchUploadCompleted', { success: successCount, failure: failureCount }));
    }

  } catch (error) {
    console.error('批量上传遭遇组失败:', error);
    message.error(t('contentPackage.encounters.error.batchUploadFailed'));
    batchEncounterUploadStatus.value = t('contentPackage.encounters.error.batchUploadFailed');
  } finally {
    batchEncounterUploading.value = false;
  }
};

// ==================== 自动编号相关方法 ====================

/**
 * 加载底标图标列表
 */
const loadFooterIconOptions = async () => {
  try {
    const fileTree = await WorkspaceService.getFileTree();

    // 提取根目录下的PNG图片
    const rootImages: Array<{ label: string; value: string }> = [];

    if (fileTree.fileTree.children) {
      for (const child of fileTree.fileTree.children) {
        // 只查找根目录下的直接子文件，且为PNG图片
        if (child.type === 'image' && child.path && child.label.toLowerCase().endsWith('.png')) {
          // 计算相对路径
          const rootPath = fileTree.fileTree.path.replace(/\\/g, '/');
          const absolutePath = child.path.replace(/\\/g, '/');
          let relativePath = '';

          if (absolutePath.startsWith(rootPath)) {
            relativePath = absolutePath.slice(rootPath.length);
            relativePath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
          } else {
            relativePath = child.path;
          }

          rootImages.push({
            label: child.label,
            value: relativePath
          });
        }
      }
    }

    // 按名称排序
    rootImages.sort((a, b) => a.label.localeCompare(b.label));
    footerIconOptions.value = rootImages;
  } catch (error) {
    console.error('加载底标图标列表失败:', error);
  }
};

/**
 * 生成卡牌编号方案
 */
const generateNumberingPlan = async () => {
  try {
    generatingPlan.value = true;
    numberingLogs.value = [];

    const packagePath = props.package.path;
    if (!packagePath) {
      message.error(t('contentPackage.numbering.errors.noPackagePath'));
      return;
    }

    // 调用API生成编号方案
    const result = await ContentPackageService.generateCardNumberingPlan(
      packagePath,
      numberingNoEncounterPosition.value,
      numberingStartNumber.value,
      numberingFooterCopyright.value,
      numberingFooterIconPath.value
    );

    numberingPlan.value = result.numbering_plan || [];
    numberingLogs.value = result.logs || [];

    if (numberingPlan.value.length > 0) {
      message.success(t('contentPackage.numbering.messages.planGenerateSuccess', {
        count: numberingPlan.value.length
      }));
    } else {
      message.warning(t('contentPackage.numbering.messages.noPlanGenerated'));
    }
  } catch (error: any) {
    console.error('生成编号方案失败:', error);
    message.error(t('contentPackage.numbering.errors.generatePlanFailed', {
      message: error.message || '未知错误'
    }));
  } finally {
    generatingPlan.value = false;
  }
};

/**
 * 应用卡牌编号方案
 */
const applyNumberingPlan = async () => {
  try {
    applyingPlan.value = true;

    const packagePath = props.package.path;
    if (!packagePath) {
      message.error(t('contentPackage.numbering.errors.noPackagePath'));
      return;
    }

    if (numberingPlan.value.length === 0) {
      message.error(t('contentPackage.numbering.errors.noPlanToApply'));
      return;
    }

    // 调用API应用编号方案
    const result = await ContentPackageService.applyCardNumbering(
      packagePath,
      numberingPlan.value
    );

    // 追加日志
    numberingLogs.value = [
      ...numberingLogs.value,
      ...(result.logs || [])
    ];

    if (result.updated_count > 0) {
      message.success(t('contentPackage.numbering.messages.planApplySuccess', {
        count: result.updated_count
      }));

      // 清除编号方案
      clearNumberingPlan();

      // 触发保存到文件
      emit('save');
    } else {
      message.warning(t('contentPackage.numbering.messages.noCardsUpdated'));
    }
  } catch (error: any) {
    console.error('应用编号方案失败:', error);
    message.error(t('contentPackage.numbering.errors.applyPlanFailed', {
      message: error.message || '未知错误'
    }));
  } finally {
    applyingPlan.value = false;
  }
};

/**
 * 清除编号方案
 */
const clearNumberingPlan = () => {
  numberingPlan.value = [];
};

// 监听内容包变化,自动刷新版本信息
watch(() => packageData.value, async (newPackage, oldPackage) => {
  if (newPackage && (!oldPackage ||
    newPackage.path !== oldPackage.path ||
    JSON.stringify(newPackage?.cards) !== JSON.stringify(oldPackage?.cards) ||
    JSON.stringify(newPackage?.encounter_sets) !== JSON.stringify(oldPackage?.encounter_sets))) {
    // 中止正在进行的预览生成队列
    abortPreviewGeneration();

    // 等待一小段时间确保DOM更新完成
    await nextTick();

    // 刷新版本信息
    await refreshCardVersions();

    // 加载底标图标选项
    await loadFooterIconOptions();

    // 刷新遭遇组信息
    if (newPackage.encounter_sets && newPackage.encounter_sets.length > 0) {
      // 按 order 排序后更新
      const sortedEncounters = [...newPackage.encounter_sets].sort((a, b) => (a.order || 0) - (b.order || 0));
      encounters.value = sortedEncounters;
    } else {
      // 如果没有遭遇组数据，尝试从API获取
      await refreshEncounterGroups();
    }
  }
}, { immediate: true, deep: true });

</script>

<style scoped>
.package-editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0;
  position: relative;
}

/* 上传页面样式 */
.upload-page {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.upload-page-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.upload-page-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

.upload-page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  min-height: 0;
}

.upload-page-footer {
  flex-shrink: 0;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
  display: flex;
  justify-content: flex-end;
}

/* 主编辑器内容样式 */
.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.editor-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.package-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.package-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.editor-content {
  flex: 1;
  padding: 2rem 3rem 2rem 2.5rem;
  min-height: 0;
  overflow-y: auto;
}

.editor-content :deep(.n-tabs-nav) {
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.editor-content :deep(.n-tabs-tab) {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
}

.info-panel {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.banner-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.banner-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

.banner-preview {
  width: 100%;
  max-width: 400px;
  height: 200px;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #f8f9fa;
}

.banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
}

.info-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

/* 表格标签样式加粗 */
.info-section :deep(.n-descriptions-table .n-descriptions-table-label) {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

/* 表格值颜色调整，降低对比度 */
.info-section :deep(.n-descriptions-table .n-descriptions-table-content) {
  color: #5a6c7d;
  font-size: 0.9rem;
}

.description-section {
  margin-top: 1.5rem;
}

.description-section h4 {
  margin: 0 0 0.75rem 0;
}

.external-link-section {
  margin-top: 1.5rem;
}

.external-link-section h4 {
  margin: 0 0 0.75rem 0;
}

.cards-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.cards-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.cards-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.cards-content {
  flex: 1;
  min-height: 400px;
}

.empty-cards {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  height: 100%;
  overflow-y: auto;
}

.card-item {
  position: relative;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 状态图标样式 - 重新设计 */
.status-icon {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(4px);
  transition: all 0.2s ease;
}

.cloud-status-icon {
  color: #10b981;
  filter: drop-shadow(0 1px 2px rgba(16, 185, 129, 0.3));
}

.local-status-icon {
  color: #3b82f6;
  filter: drop-shadow(0 1px 2px rgba(59, 130, 246, 0.3));
}

.status-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.cloud-status-icon:hover {
  color: #059669;
  filter: drop-shadow(0 2px 4px rgba(16, 185, 129, 0.4));
}

.local-status-icon:hover {
  color: #2563eb;
  filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.4));
}

.card-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-item.unsupported {
  border-color: #f56565;
  background: #fff5f5;
}

.card-item.unsupported:hover {
  border-color: #e53e3e;
}

.card-preview {
  width: 100%;
  height: 140px;
  border-radius: 6px;
  overflow: hidden;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
  border: 1px solid #e9ecef;
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #e53e3e;
  gap: 0.5rem;
}

.error-text {
  font-size: 0.75rem;
  font-weight: 500;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
}

.card-info {
  margin-bottom: 0.5rem;
}

.card-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  word-break: break-word;
  line-height: 1.2;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.card-item:hover .card-actions {
  opacity: 1;
}

.card-bottom-actions {
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
}

.card-bottom-actions .n-space {
  gap: 0.5rem !important;
}

.card-bottom-actions .n-button {
  width: 100%;
  height: 28px;
  padding: 0 0.75rem;
  font-size: 0.8rem;
  font-weight: 400;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.card-bottom-actions .n-button:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* 为编辑按钮添加轻微的hover效果 */
.card-bottom-actions .n-button--info-type:hover {
  background-color: #3090ff;
  border-color: #3090ff;
}

.export-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.export-panel h4 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.export-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
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
  height: 225px;
  /* 16:9 比例 */
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

/* 封面预览容器 */
.banner-preview-container {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.upload-cloud-btn {
  margin-top: 0.75rem;
  width: 100%;
  max-width: 400px;
}

/* 批量上传样式 */
.batch-upload-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.batch-upload-info h5 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.batch-upload-cards h5 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.batch-card-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.batch-card-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.batch-card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.batch-card-preview {
  width: 60px;
  height: 84px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dee2e6;
}

.batch-card-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
}

.batch-upload-progress h5 {
  margin: 0 0 0.75rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.batch-upload-status {
  margin-top: 0.5rem;
  text-align: center;
}

/* TTS导出样式 */
.tts-export-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ArkhamDB导出样式 */
.arkhamdb-export-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.arkhamdb-description h5 {
  margin: 0 0 0.75rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.tts-cards-status {
  margin-top: 1rem;
}

.tts-cards-status h5 {
  margin: 0 0 0.75rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.tts-cards-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tts-card-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.tts-card-info {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.export-logs-content {
  min-height: 300px;
}

.logs-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.9rem;
  line-height: 1.6;
  border: 1px solid #e9ecef;
}

.log-item {
  padding: 0.4rem 0.6rem;
  word-break: break-word;
  border-radius: 4px;
  background: white;
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
}

.log-item:hover {
  background: #f0f8ff;
  border-left-color: #667eea;
}

/* 特定类型日志的样式 */
.log-item.log-start {
  border-left-color: #667eea;
  font-weight: 600;
  background: #f0f4ff;
}

.log-item.log-package,
.log-item.log-stats {
  border-left-color: #28a745;
  background: #f8fff9;
}

.log-item.log-cloud {
  border-left-color: #17a2b8;
  background: #f0fbfc;
}

.log-item.log-local {
  border-left-color: #6f42c1;
  background: #f8f7ff;
}

.log-item.log-processing {
  border-left-color: #ffc107;
  background: #fffbf0;
}

.log-item.log-success {
  border-left-color: #28a745;
  background: #f8fff9;
}

.log-item.log-complete {
  border-left-color: #007bff;
  background: #e7f3ff;
  font-weight: 600;
}

.log-item.log-file,
.log-item.log-save {
  border-left-color: #fd7e14;
  background: #fff8f0;
}

.log-item.log-error {
  border-left-color: #dc3545;
  background: #fff5f5;
  font-weight: 500;
}

.log-item.log-tip {
  border-left-color: #6c757d;
  background: #f8f9fa;
  font-style: italic;
}

/* 空行样式 - 使用专门的类名 */
.log-item.log-spacer {
  height: 0.5rem;
  min-height: 0.5rem;
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  visibility: hidden;
}

.log-item.log-spacer .n-text {
  display: none;
}

/* 分隔线样式 */
.log-item.log-divider {
  background: transparent;
  border: none;
  padding: 0;
  text-align: center;
  color: #adb5bd;
  font-weight: 300;
}

/* 加载中样式 */
.log-item.log-loading {
  border-left-color: #667eea;
  background: #f0f4ff;
  display: flex;
  align-items: center;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 卡牌元数据标签样式 */
.card-meta .n-tag {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
}

/* 实体导出面板样式 */
.physical-export-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.physical-export-panel h4 {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
}

/* PNP上下布局 - 顶部左右分栏，底部日志 */
.pnp-top-layout {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.pnp-status-section {
  flex: 0 0 350px;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pnp-params-section {
  flex: 1;
  min-width: 400px;
}

.empty-logs {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.physical-export-panel .n-alert p {
  margin: 0.5rem 0;
}

.physical-export-panel .n-alert p:first-child {
  margin-top: 0;
}

.physical-export-panel .n-alert p:last-child {
  margin-bottom: 0;
}

/* 标签编辑对话框样式 */
.edit-tags-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.tags-info h5 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.current-tags-preview {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.current-tags-preview h5 {
  margin: 0 0 0.75rem 0;
  color: #2c3e50;
  font-size: 0.95rem;
  font-weight: 600;
}

/* 改进卡牌操作按钮布局 */
.card-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  gap: 0.25rem;
}

.card-item:hover .card-actions {
  opacity: 1;
}

.card-actions .n-button {
  width: 24px;
  height: 24px;
}

/* 遭遇组管理样式 */
.encounters-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.encounters-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.encounters-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.encounters-content {
  flex: 1;
  min-height: 400px;
}

.empty-encounters {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.encounters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  height: 100%;
  overflow-y: auto;
}

.encounter-item {
  position: relative;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  cursor: grab;
}

.encounter-item:active {
  cursor: grabbing;
}

.encounter-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

/* 拖动状态样式 */
.encounter-item.dragging {
  opacity: 0.5;
  cursor: grabbing;
  transform: scale(0.95);
  border-color: #667eea;
}

.encounter-item.drag-over {
  border-color: #48bb78;
  background: #f0fff4;
  box-shadow: 0 0 0 2px rgba(72, 187, 120, 0.3);
}

/* 拖动手柄 */
.drag-handle {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  cursor: grab;
  opacity: 0;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  z-index: 5;
}

.encounter-item:hover .drag-handle {
  opacity: 1;
}

.drag-handle:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.drag-handle:active {
  cursor: grabbing;
}

.encounter-icon {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e9ecef;
}

.icon-preview {
  width: 100%;
  height: 100%;
}

.icon-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.icon-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
}

.encounter-info {
  text-align: center;
  flex: 1;
  width: 100%;
}

.encounter-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  word-break: break-word;
  line-height: 1.2;
}

.encounter-code {
  color: #6c757d;
  font-size: 0.75rem;
}

.encounter-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.encounter-item:hover .encounter-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .package-meta {
    justify-content: center;
  }

  .editor-actions {
    justify-content: center;
  }

  .editor-content {
    padding: 1rem;
  }

  .banner-preview {
    max-width: 100%;
    height: 150px;
  }

  .batch-card-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .batch-card-preview {
    width: 100%;
    height: 120px;
  }

  .card-meta .n-tag {
    font-size: 0.7rem;
    padding: 0.1rem 0.25rem;
  }

  .card-bottom-actions .n-button {
    height: 26px;
    padding: 0 0.6rem;
    font-size: 0.75rem;
  }

  .card-bottom-actions .n-space {
    gap: 0.4rem !important;
  }
}
</style>
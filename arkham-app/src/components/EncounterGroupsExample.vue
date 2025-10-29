<template>
  <div class="encounter-groups-example">
    <n-card title="遭遇组API使用示例" :bordered="false">
      <template #header-extra>
        <n-button
          type="primary"
          @click="loadEncounterGroups"
          :loading="loading"
          size="small"
        >
          刷新遭遇组
        </n-button>
      </template>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <n-spin size="medium" />
        <span class="loading-text">正在获取遭遇组列表...</span>
      </div>

      <!-- 错误状态 -->
      <n-alert
        v-else-if="error"
        type="error"
        :title="error"
        closable
        @close="error = ''"
      />

      <!-- 成功状态 -->
      <div v-else-if="encounterGroups.length > 0">
        <n-space vertical>
          <!-- 统计信息 -->
          <n-statistic label="遭遇组数量" :value="encounterGroups.length" />

          <!-- 遭遇组列表 -->
          <n-scrollbar style="max-height: 300px">
            <n-list hoverable clickable>
              <n-list-item
                v-for="(group, index) in encounterGroups"
                :key="index"
                @click="selectEncounterGroup(group)"
                :class="{ 'selected': selectedGroup === group }"
              >
                <n-thing :title="group">
                  <template #description>
                    遭遇组 #{{ index + 1 }}
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-scrollbar>

          <!-- 选中信息 -->
          <div v-if="selectedGroup" class="selected-info">
            <n-alert type="success">
              <template #header>已选择遭遇组</template>
              {{ selectedGroup }}
            </n-alert>
          </div>
        </n-space>
      </div>

      <!-- 空状态 -->
      <n-empty
        v-else
        description="暂无遭遇组数据"
        :show-icon="true"
      >
        <template #extra>
          <n-button size="small" @click="loadEncounterGroups">
            重新加载
          </n-button>
        </template>
      </n-empty>
    </n-card>

    <!-- API调试信息 -->
    <n-card title="调试信息" :bordered="false" style="margin-top: 16px">
      <n-code :code="debugInfo" language="json" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  NCard,
  NButton,
  NSpin,
  NAlert,
  NSpace,
  NStatistic,
  NScrollbar,
  NList,
  NListItem,
  NThing,
  NEmpty,
  NCode
} from 'naive-ui';
import { ConfigService } from '@/api/config-service';
import type { ApiError } from '@/api/http-client';

// 响应式数据
const loading = ref(false);
const error = ref('');
const encounterGroups = ref<string[]>([]);
const selectedGroup = ref('');
const debugInfo = ref('');

/**
 * 加载遭遇组列表
 */
const loadEncounterGroups = async () => {
  loading.value = true;
  error.value = '';
  selectedGroup.value = '';

  try {
    console.log('🔄 开始加载遭遇组列表...');

    // 使用ConfigService获取遭遇组
    const groups = await ConfigService.getEncounterGroups();

    encounterGroups.value = groups;
    debugInfo.value = JSON.stringify({
      timestamp: new Date().toISOString(),
      count: groups.length,
      groups: groups,
      status: 'success'
    }, null, 2);

    console.log('✅ 遭遇组列表加载成功:', groups);
  } catch (err) {
    console.error('❌ 加载遭遇组列表失败:', err);

    let errorMessage = '加载遭遇组列表失败';

    if (err instanceof ApiError) {
      errorMessage = `API错误 (${err.code}): ${err.message}`;
      debugInfo.value = JSON.stringify({
        timestamp: new Date().toISOString(),
        error: {
          code: err.code,
          message: err.message,
          details: err.details
        },
        status: 'error'
      }, null, 2);
    } else {
      errorMessage = `系统错误: ${err instanceof Error ? err.message : String(err)}`;
      debugInfo.value = JSON.stringify({
        timestamp: new Date().toISOString(),
        error: {
          message: errorMessage,
          raw: err
        },
        status: 'error'
      }, null, 2);
    }

    error.value = errorMessage;
  } finally {
    loading.value = false;
  }
};

/**
 * 选择遭遇组
 */
const selectEncounterGroup = (group: string) => {
  selectedGroup.value = group;
  console.log('🎯 选择了遭遇组:', group);
};

/**
 * 手动测试API（用于调试）
 */
const testApiDirectly = async () => {
  try {
    const response = await fetch('/api/encounter-groups');
    const data = await response.json();
    console.log('直接API调用结果:', data);
    return data;
  } catch (error) {
    console.error('直接API调用失败:', error);
    throw error;
  }
};

// 组件挂载时自动加载数据
onMounted(() => {
  loadEncounterGroups();
});

// 暴露调试方法到全局（开发环境）
if (import.meta.env.DEV && typeof window !== 'undefined') {
  (window as any).encounterGroupsExample = {
    loadEncounterGroups,
    testApiDirectly,
    selectEncounterGroup
  };
  console.log('🔧 遭遇组示例组件调试方法已暴露到 window.encounterGroupsExample');
}
</script>

<style scoped>
.encounter-groups-example {
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px 0;
}

.loading-text {
  color: #666;
  font-size: 14px;
}

.selected-info {
  margin-top: 16px;
}

.selected :deep(.n-list-item) {
  background-color: #e6f7ff;
  border-color: #1890ff;
}

:deep(.n-code) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  max-height: 200px;
  overflow-y: auto;
}
</style>
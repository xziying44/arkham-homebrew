<template>
  <n-form-item :label="label">
    <n-space vertical size="small" style="width: 100%">
      <n-space align="center" justify="space-between">
        <n-text depth="3" style="font-size: 12px;">{{ modelPath || noneText }}</n-text>
        <n-space>
          <n-button size="small" type="primary" dashed @click="innerShow = true">{{ chooseText }}</n-button>
          <n-button size="small" quaternary type="error" @click="clear" v-if="modelPath">{{ clearText }}</n-button>
        </n-space>
      </n-space>
      <n-alert type="info" v-if="info">{{ info }}</n-alert>
    </n-space>
  </n-form-item>

  <n-modal v-model:show="innerShow" style="width: 80%; max-width: 800px;" preset="card">
    <template #header>
      <div class="bind-selector-header">
        <n-text>{{ modalTitle }}</n-text>
      </div>
    </template>
    <div class="bind-selector-content">
      <CardFileBrowser :visible="innerShow" :single-select="singleSelect"
        @update:visible="innerShow = $event"
        @confirm="onConfirm" />
    </div>
    <template #action>
      <n-space>
        <n-button @click="innerShow = false">{{ cancelText }}</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CardFileBrowser from './CardFileBrowser.vue'

interface BrowserItem { path: string }

interface Props {
  path: string
  label: string
  noneText: string
  chooseText: string
  clearText: string
  modalTitle: string
  cancelText: string
  info?: string
  singleSelect?: boolean
}

const props = withDefaults(defineProps<Props>(), { singleSelect: true })
const emit = defineEmits<{ 'update:path': [value: string] }>()

const innerShow = ref(false)
const modelPath = computed({
  get: () => props.path,
  set: (v: string) => emit('update:path', v)
})

const onConfirm = (items: BrowserItem[]) => {
  if (Array.isArray(items) && items.length > 0) {
    const first = items[0]
    if (first && typeof first.path === 'string') {
      modelPath.value = first.path
      innerShow.value = false
    }
  }
}

const clear = () => {
  modelPath.value = ''
}
</script>

<style scoped>
.bind-selector-content { min-height: 400px; }
.bind-selector-header { font-size: 16px; font-weight: 500; }
</style>


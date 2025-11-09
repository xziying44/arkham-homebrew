<script setup lang="ts">
// Usage: drop-in replacement for n-tree in FileTreePanel
// <VirtualFileTree
//   :data="displayedTreeData"
//   :expanded-keys="expandedKeys"
//   :selected-keys="selectedKeys"
//   :render-label="renderTreeLabel"
//   :render-prefix="renderTreePrefix"
//   :node-height="32"
//   @update:selected-keys="handleFileSelect"
//   @update:expanded-keys="handleExpandedKeysChange"
//   @contextmenu="(option, e) => handleRightClick(e, option)"
//   @dragstart="(option, e) => handleTreeNodeDragStart(e, option)"
// />
import { computed, h, ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { VirTree } from 'vue-virtual-tree'

// Keep local type compatible with existing FileTreePanel usage
export type Key = string | number

// The existing tree option shape used by FileTreePanel
export interface TreeOption {
  label: string
  key: Key
  type?: string
  path?: string
  children?: TreeOption[]
  // passthrough for extended fields like card_type/loadingState
  [k: string]: any
}

// vue-virtual-tree expected node shape
interface VvtNode {
  nodeKey: Key
  name: string
  level?: number
  loading?: boolean
  hasChildren?: boolean
  children?: VvtNode[]
  parentKey?: Key | null
}

const props = defineProps<{
  data: TreeOption[]
  expandedKeys: Key[]
  selectedKeys: Key[]
  renderLabel: (args: { option: TreeOption }) => any
  renderPrefix: (args: { option: TreeOption }) => any
  nodeHeight?: number
}>()

const emit = defineEmits<{
  (e: 'update:expanded-keys', keys: Key[]): void
  (e: 'update:selected-keys', keys: Key[], options: TreeOption[]): void
  (e: 'contextmenu', option: TreeOption, event: MouseEvent): void
  (e: 'dragstart', option: TreeOption, event: DragEvent): void
}>()

const nodeHeight = computed(() => props.nodeHeight ?? 32)
// Visible rows: computed from available height of the file-tree-content area
const remain = ref(12)
const host = ref<HTMLDivElement | null>(null)
let ro: ResizeObserver | null = null

const px = (v: string | null) => (v ? parseFloat(v) || 0 : 0)
const updateRemain = () => {
  // Try to use the full height of .file-tree-content minus toolbar height
  const hostEl = host.value
  if (!hostEl) return
  const contentEl = hostEl.closest('.file-tree-content') as HTMLElement | null
  if (!contentEl) return
  const toolbarEl = contentEl.querySelector('.file-tree-toolbar') as HTMLElement | null
  const contentRect = contentEl.getBoundingClientRect()
  const toolbarRect = toolbarEl?.getBoundingClientRect()
  const toolbarMB = toolbarEl ? px(getComputedStyle(toolbarEl).marginBottom) : 0
  const avail = Math.max(0, contentRect.height - (toolbarRect?.height || 0) - toolbarMB)
  const rows = Math.max(1, Math.ceil(avail / nodeHeight.value))
  remain.value = rows
}

onMounted(async () => {
  await nextTick()
  updateRemain()
  // Watch container size changes
  try {
    ro = new ResizeObserver(() => updateRemain())
    const target = host.value?.closest('.file-tree-pane') as Element | undefined
    if (target) ro.observe(target)
  } catch {
    // fallback to window resize
    window.addEventListener('resize', updateRemain)
  }
})

onBeforeUnmount(() => {
  if (ro) {
    try { ro.disconnect() } catch {}
    ro = null
  }
  window.removeEventListener('resize', updateRemain)
})

// Map of nodeKey -> original option for event/render mapping
const nodeMap = new Map<Key, TreeOption>()

const toVvtTree = (nodes: TreeOption[], parentKey: Key | null = null): VvtNode[] => {
  const result: VvtNode[] = []
  for (const n of nodes || []) {
    nodeMap.set(n.key, n)
    const v: VvtNode = {
      nodeKey: n.key,
      name: String(n.label ?? ''),
      hasChildren: Array.isArray(n.children) && n.children.length > 0,
      parentKey
    }
    if (n.children && n.children.length) {
      v.children = toVvtTree(n.children, n.key)
    }
    result.push(v)
  }
  return result
}

const source = computed<VvtNode[]>(() => {
  nodeMap.clear()
  return toVvtTree(props.data || [])
})

const defaultExpandedKeys = computed<Key[]>(() => props.expandedKeys || [])
const defaultSelectedKey = computed<Key>(() => props.selectedKeys?.[0] ?? '')

// render function for vue-virtual-tree
const renderNode = (node: VvtNode) => {
  const option = nodeMap.get(node.nodeKey) as TreeOption
  const draggable = option?.type === 'card'
  const isSelected = Array.isArray(props.selectedKeys) && props.selectedKeys.includes(node.nodeKey)

  const onClick = (e?: MouseEvent) => {
    if (e) e.stopPropagation()
    if (!option) return
    if (option.type === 'directory' || option.type === 'workspace') {
      const set = new Set<Key>(props.expandedKeys)
      if (set.has(option.key)) set.delete(option.key)
      else set.add(option.key)
      emit('update:expanded-keys', Array.from(set))
    } else {
      emit('update:selected-keys', [option.key], [option])
    }
  }

  // prefix + label container, reuse upstream renderers to keep visuals identical
  return h(
    'span',
    {
      class: ['n-tree-node-content', isSelected ? 'n-tree-node-content--selected' : ''],
      style: { display: 'inline-flex', alignItems: 'center', height: `${nodeHeight.value}px` },
      draggable,
      onDragstart: (e: DragEvent) => { e.stopPropagation(); if (draggable) emit('dragstart', option, e) },
      onContextmenu: (e: MouseEvent) => emit('contextmenu', option, e),
      onClick
    },
    [
      props.renderPrefix({ option }),
      props.renderLabel({ option })
    ]
  )
}

// bridge events to FileTreePanel-compatible update events
const onToggleExpand = (payload: { status: boolean; node: VvtNode }) => {
  const key = payload.node.nodeKey
  const set = new Set<Key>(props.expandedKeys)
  if (payload.status) set.add(key)
  else set.delete(key)
  emit('update:expanded-keys', Array.from(set))
}

// We handle click on our custom content to keep behavior consistent with original n-tree
</script>

<template>
  <div ref="host" class="vft-host">
    <VirTree
      class="virtual-file-tree"
      :source="source"
      :size="nodeHeight"
      :remain="remain"
      :default-expanded-keys="defaultExpandedKeys"
      :default-selected-key="defaultSelectedKey"
      :render="renderNode"
      @toggle-expand="onToggleExpand"
    />
  </div>
  <!-- Note: vue-virtual-tree emits kebab-case events in template usage -->
</template>

<style scoped>
.virtual-file-tree {
  width: 100%;
  height: 100%;
}
.vft-host { height: 100%; }

/* Ensure root container is block-level and fills height */
:deep(.vir-tree) {
  display: block !important;
  height: 100%;
}

/* Align arrow vertically and remove library hover/selected backgrounds to avoid double backgrounds */
:deep(.vir-tree-wrap .vir-tree-node) {
  /* keep left padding for indentation from library, but remove vertical paddings */
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  min-height: 32px;
  display: flex;
  align-items: center;
}
:deep(.vir-tree-wrap .vir-tree-node:hover) {
  background-color: transparent !important;
}
:deep(.vir-tree-wrap .vir-tree-node .node-content .node-title) {
  display: inline-flex;
  align-items: center;
  height: 32px;
}
:deep(.vir-tree-wrap .vir-tree-node .node-content .node-title.selected),
:deep(.vir-tree-wrap .node-selected .node-title) {
  background-color: transparent !important;
}
:deep(.vir-tree-wrap .vir-tree-node .node-arrow) {
  display: inline-flex;
  align-items: center;
  height: 32px;
  margin-right: 6px;
}

/* 滚动条样式统一到虚拟树内部（纵向与横向） */
:deep(.vir-tree-wrap) {
  height: 100%;
  overflow: auto;
}

/* 允许横向滚动（库内仅设置了 overflow-y），这里开启 x 轴滚动 */
:deep(.vir-list) {
  overflow: auto !important;
}

:deep(.vir-tree-wrap::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.vir-tree-wrap::-webkit-scrollbar-track) {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

:deep(.vir-tree-wrap::-webkit-scrollbar-thumb) {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.vir-tree-wrap::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(180deg, #5a67d8 0%, #6b46c1 100%);
}
</style>

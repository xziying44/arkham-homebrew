<template>
  <div class="body-rich-text-editor">
    <!-- Toolbar -->
    <div class="editor-toolbar">
      <!-- Format Tags -->
      <n-space size="small" class="toolbar-group">
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertTag('bold')">
              <template #icon>
                <n-icon :component="TextOutline" />
              </template>
              <strong>B</strong>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.bold') }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertTag('trait')">
              <template #icon>
                <n-icon :component="PricetagOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.trait') }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertTag('italic')">
              <template #icon>
                <n-icon :component="TextOutline" />
              </template>
              <em>I</em>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.italic') }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertTag('center')">
              <template #icon>
                <n-icon :component="ReorderFourOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.center') }}
        </n-tooltip>
      </n-space>

      <n-divider vertical />

      <!-- Flavor Tag with Modal -->
      <n-tooltip trigger="hover">
        <template #trigger>
          <n-button size="small" @click="showFlavorModal = true">
            <template #icon>
              <n-icon :component="ChatbubbleEllipsesOutline" />
            </template>
          </n-button>
        </template>
        {{ t('bodyRichTextEditor.tooltip.flavor') }}
      </n-tooltip>

      <n-divider vertical />

      <!-- Quick Insert -->
      <n-space size="small" class="toolbar-group">
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertText('<hr>')">
              <template #icon>
                <n-icon :component="RemoveOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.hr') }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="showSizeModal = true">
              <template #icon>
                <n-icon :component="ResizeOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.fontSize') }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertText('<fullname>')">
              <template #icon>
                <n-icon :component="PersonOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.fullname') }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertText('<upg>')">
              <template #icon>
                <n-icon :component="CheckboxOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.upg') }}
        </n-tooltip>
      </n-space>

      <n-divider vertical />

      <!-- Icon Popover Grid -->
      <n-popover
        trigger="click"
        placement="bottom-start"
        :width="320"
        v-model:show="showIconPopover"
      >
        <template #trigger>
          <n-button size="small">
            <template #icon>
              <n-icon :component="SparklesOutline" />
            </template>
            {{ t('bodyRichTextEditor.icons') }}
            <n-icon :component="ChevronDownOutline" style="margin-left: 4px;" />
          </n-button>
        </template>
        <div class="icon-grid">
          <div
            v-for="icon in iconList"
            :key="icon.key"
            class="icon-grid-item"
            @click="handleIconSelect(icon.emoji)"
          >
            <span class="icon-emoji">{{ icon.emoji }}</span>
            <span class="icon-label">{{ icon.label }}</span>
          </div>
        </div>
      </n-popover>

      <n-divider vertical />

      <!-- Spellcheck Switch -->
      <n-space align="center" class="toolbar-group">
        <n-text depth="3" style="font-size: 12px;">{{ t('bodyRichTextEditor.spellcheck') }}</n-text>
        <n-switch v-model:value="spellcheckEnabled" size="small" />
      </n-space>
    </div>

    <!-- Editor with Line Numbers -->
    <div class="editor-container">
      <div class="line-numbers" ref="lineNumbersRef">
        <template v-for="(lineInfo, index) in lineInfoList" :key="index">
          <div class="line-number" :style="{ height: lineInfo.height + 'px' }">
            {{ lineInfo.lineNum > 0 ? lineInfo.lineNum : '' }}
          </div>
        </template>
      </div>
      <textarea
        ref="textareaRef"
        class="editor-textarea"
        :value="value"
        :spellcheck="spellcheckEnabled"
        @input="handleInput"
        @scroll="syncScroll"
        @keydown="handleKeydown"
      />
    </div>

    <!-- Flavor Config Modal -->
    <n-modal
      v-model:show="showFlavorModal"
      preset="dialog"
      :title="t('bodyRichTextEditor.flavorModal.title')"
      style="width: 480px;"
    >
      <n-form label-placement="left" label-width="80px">
        <n-form-item :label="t('bodyRichTextEditor.flavorModal.align')">
          <n-select
            v-model:value="flavorConfig.align"
            :options="alignOptions"
            style="width: 100%;"
          />
        </n-form-item>
        <n-form-item :label="t('bodyRichTextEditor.flavorModal.padding')">
          <n-input-number
            v-model:value="flavorConfig.padding"
            :min="0"
            :max="99"
            style="width: 100%;"
          />
        </n-form-item>
        <n-form-item :label="t('bodyRichTextEditor.flavorModal.quote')">
          <n-switch v-model:value="flavorConfig.quote" />
        </n-form-item>
        <n-form-item :label="t('bodyRichTextEditor.flavorModal.flex')">
          <n-switch v-model:value="flavorConfig.flex" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showFlavorModal = false">{{ t('bodyRichTextEditor.common.cancel') }}</n-button>
          <n-button type="primary" @click="insertFlavorTag">{{ t('bodyRichTextEditor.common.confirm') }}</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Font Size Modal -->
    <n-modal
      v-model:show="showSizeModal"
      preset="dialog"
      :title="t('bodyRichTextEditor.sizeModal.title')"
      style="width: 320px;"
    >
      <n-form label-placement="left" label-width="80px">
        <n-form-item :label="t('bodyRichTextEditor.sizeModal.value')">
          <n-input-number
            v-model:value="fontSizeValue"
            :min="-99"
            :max="99"
            style="width: 100%;"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showSizeModal = false">{{ t('bodyRichTextEditor.common.cancel') }}</n-button>
          <n-button type="primary" @click="insertSizeTag">{{ t('bodyRichTextEditor.common.confirm') }}</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  TextOutline,
  PricetagOutline,
  ReorderFourOutline,
  ChatbubbleEllipsesOutline,
  RemoveOutline,
  ResizeOutline,
  PersonOutline,
  CheckboxOutline,
  SparklesOutline,
  ChevronDownOutline
} from '@vicons/ionicons5';

interface Props {
  value: string;
  cardLanguage?: string;
}

interface Emits {
  (e: 'update:value', value: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  cardLanguage: 'zh'
});
const emit = defineEmits<Emits>();

const { t } = useI18n();

// Refs
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const lineNumbersRef = ref<HTMLDivElement | null>(null);

// Constants
const DEFAULT_FLAVOR_CONFIG = {
  align: 'left' as 'left' | 'center',
  padding: 0,
  quote: false,
  flex: true
};

// State
const showFlavorModal = ref(false);
const showSizeModal = ref(false);
const showIconPopover = ref(false);
const fontSizeValue = ref(2);
const spellcheckEnabled = ref(false);

// Undo/Redo history management
interface HistoryState {
  value: string;
  cursorStart: number;
  cursorEnd: number;
}

const history = ref<HistoryState[]>([]);
const historyIndex = ref(-1);
const isUndoRedo = ref(false);
const MAX_HISTORY = 100;

// Push state to history
const pushHistory = (value: string, cursorStart: number, cursorEnd: number) => {
  if (isUndoRedo.value) return;

  // Remove any future states if we're not at the end
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1);
  }

  // Don't push if the value is the same as the last state
  const lastState = history.value[history.value.length - 1];
  if (lastState && lastState.value === value) {
    // Just update cursor position
    lastState.cursorStart = cursorStart;
    lastState.cursorEnd = cursorEnd;
    return;
  }

  history.value.push({ value, cursorStart, cursorEnd });

  // Limit history size
  if (history.value.length > MAX_HISTORY) {
    history.value.shift();
  }

  historyIndex.value = history.value.length - 1;
};

// Undo action
const undo = () => {
  if (historyIndex.value <= 0) return;

  isUndoRedo.value = true;
  historyIndex.value--;
  const state = history.value[historyIndex.value];

  emit('update:value', state.value);

  nextTick(() => {
    const textarea = textareaRef.value;
    if (textarea) {
      textarea.focus();
      textarea.selectionStart = state.cursorStart;
      textarea.selectionEnd = state.cursorEnd;
    }
    isUndoRedo.value = false;
  });
};

// Redo action
const redo = () => {
  if (historyIndex.value >= history.value.length - 1) return;

  isUndoRedo.value = true;
  historyIndex.value++;
  const state = history.value[historyIndex.value];

  emit('update:value', state.value);

  nextTick(() => {
    const textarea = textareaRef.value;
    if (textarea) {
      textarea.focus();
      textarea.selectionStart = state.cursorStart;
      textarea.selectionEnd = state.cursorEnd;
    }
    isUndoRedo.value = false;
  });
};

// Initialize history with initial value
watch(
  () => props.value,
  (newValue) => {
    if (!isUndoRedo.value && history.value.length === 0) {
      pushHistory(newValue || '', 0, 0);
    }
  },
  { immediate: true }
);

// Flavor config
const flavorConfig = ref({ ...DEFAULT_FLAVOR_CONFIG });

// Align options for flavor modal
const alignOptions = [
  { label: 'left', value: 'left' },
  { label: 'center', value: 'center' }
];

// Initialize spellcheck based on language
watch(
  () => props.cardLanguage,
  (newLang) => {
    const isEnglish = newLang?.toLowerCase().startsWith('en') || false;
    spellcheckEnabled.value = isEnglish;
  },
  { immediate: true }
);

// Line height constant (matches CSS: 14px * 1.6 = 22.4px)
const LINE_HEIGHT = 22.4;

// Measure helper canvas for text width calculation
let measureCanvas: HTMLCanvasElement | null = null;
let measureContext: CanvasRenderingContext2D | null = null;

const getMeasureContext = (): CanvasRenderingContext2D | null => {
  if (!measureContext) {
    measureCanvas = document.createElement('canvas');
    measureContext = measureCanvas.getContext('2d');
    if (measureContext) {
      // Match the textarea font
      measureContext.font = '14px "Fira Code", "Consolas", "Monaco", monospace';
    }
  }
  return measureContext;
};

// Get textarea width for text wrap calculation
const textareaWidth = ref(0);

const updateTextareaWidth = () => {
  if (textareaRef.value) {
    // Subtract padding (12px left + 12px right = 24px)
    textareaWidth.value = textareaRef.value.clientWidth - 24;
  }
};

// Line info list computed with visual wrap handling
interface LineInfo {
  lineNum: number; // Actual line number (0 for continuation rows)
  height: number;  // Height in pixels
}

const lineInfoList = computed<LineInfo[]>(() => {
  const lines = (props.value || '').split('\n');
  const result: LineInfo[] = [];
  const ctx = getMeasureContext();
  const containerWidth = textareaWidth.value || 300; // Fallback width

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (!ctx || containerWidth <= 0) {
      // Fallback: assume no wrap
      result.push({ lineNum: i + 1, height: LINE_HEIGHT });
      continue;
    }

    // Measure text width
    const textWidth = ctx.measureText(line).width;

    // Calculate how many visual rows this line occupies
    const visualRows = line.length === 0 ? 1 : Math.max(1, Math.ceil(textWidth / containerWidth));

    // First visual row shows the line number
    result.push({ lineNum: i + 1, height: LINE_HEIGHT });

    // Additional visual rows (continuation) show empty line number
    for (let j = 1; j < visualRows; j++) {
      result.push({ lineNum: 0, height: LINE_HEIGHT });
    }
  }

  return result;
});

// Setup resize observer for textarea width changes
let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  updateTextareaWidth();

  if (textareaRef.value) {
    resizeObserver = new ResizeObserver(() => {
      updateTextareaWidth();
    });
    resizeObserver.observe(textareaRef.value);
  }
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  measureCanvas = null;
  measureContext = null;
});

// Icon list with emoji for grid display
const iconList = computed(() => {
  return [
    { key: 'unique', emoji: '🏅', label: t('bodyRichTextEditor.iconLabels.unique') },
    { key: 'reaction', emoji: '⭕', label: t('bodyRichTextEditor.iconLabels.reaction') },
    { key: 'action', emoji: '➡️', label: t('bodyRichTextEditor.iconLabels.action') },
    { key: 'free', emoji: '⚡', label: t('bodyRichTextEditor.iconLabels.free') },
    { key: 'skull', emoji: '💀', label: t('bodyRichTextEditor.iconLabels.skull') },
    { key: 'cultist', emoji: '👤', label: t('bodyRichTextEditor.iconLabels.cultist') },
    { key: 'tablet', emoji: '📜', label: t('bodyRichTextEditor.iconLabels.tablet') },
    { key: 'elderThing', emoji: '👹', label: t('bodyRichTextEditor.iconLabels.elderThing') },
    { key: 'tentacle', emoji: '🐙', label: t('bodyRichTextEditor.iconLabels.tentacle') },
    { key: 'elderSign', emoji: '⭐', label: t('bodyRichTextEditor.iconLabels.elderSign') },
    { key: 'fist', emoji: '👊', label: t('bodyRichTextEditor.iconLabels.fist') },
    { key: 'book', emoji: '📚', label: t('bodyRichTextEditor.iconLabels.book') },
    { key: 'foot', emoji: '🦶', label: t('bodyRichTextEditor.iconLabels.foot') },
    { key: 'brain', emoji: '🧠', label: t('bodyRichTextEditor.iconLabels.brain') },
    { key: 'wild', emoji: '❓', label: t('bodyRichTextEditor.iconLabels.wild') },
    { key: 'dot', emoji: '🔵', label: t('bodyRichTextEditor.iconLabels.dot') },
    { key: 'curse', emoji: '🌑', label: t('bodyRichTextEditor.iconLabels.curse') },
    { key: 'bless', emoji: '🌟', label: t('bodyRichTextEditor.iconLabels.bless') },
    { key: 'frost', emoji: '❄️', label: t('bodyRichTextEditor.iconLabels.frost') },
    { key: 'investigator', emoji: '🕵️', label: t('bodyRichTextEditor.iconLabels.investigator') },
    { key: 'rogue', emoji: '🚶', label: t('bodyRichTextEditor.iconLabels.rogue') },
    { key: 'survivor', emoji: '🏕️', label: t('bodyRichTextEditor.iconLabels.survivor') },
    { key: 'guardian', emoji: '🛡️', label: t('bodyRichTextEditor.iconLabels.guardian') },
    { key: 'mystic', emoji: '🧘', label: t('bodyRichTextEditor.iconLabels.mystic') },
    { key: 'seeker', emoji: '🔍', label: t('bodyRichTextEditor.iconLabels.seeker') }
  ];
});

// Handlers
const handleInput = (e: Event) => {
  const target = e.target as HTMLTextAreaElement;
  const newValue = target.value;
  emit('update:value', newValue);

  // Push to history after input
  nextTick(() => {
    if (textareaRef.value) {
      pushHistory(newValue, textareaRef.value.selectionStart, textareaRef.value.selectionEnd);
    }
  });
};

const syncScroll = () => {
  if (textareaRef.value && lineNumbersRef.value) {
    lineNumbersRef.value.scrollTop = textareaRef.value.scrollTop;
  }
};

const handleKeydown = (e: KeyboardEvent) => {
  // Handle Ctrl+Z for undo
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault();
    undo();
    return;
  }

  // Handle Ctrl+Y or Ctrl+Shift+Z for redo
  if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
    e.preventDefault();
    redo();
    return;
  }

  // Handle Tab key for indentation
  if (e.key === 'Tab') {
    e.preventDefault();
    const textarea = textareaRef.value;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const value = props.value;

    const newValue = value.substring(0, start) + '  ' + value.substring(end);
    emit('update:value', newValue);

    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 2;
      pushHistory(newValue, start + 2, start + 2);
    });
  }
};

const getSelection = (): { start: number; end: number; selectedText: string } => {
  const textarea = textareaRef.value;
  if (!textarea) return { start: 0, end: 0, selectedText: '' };

  return {
    start: textarea.selectionStart,
    end: textarea.selectionEnd,
    selectedText: props.value.substring(textarea.selectionStart, textarea.selectionEnd)
  };
};

const insertAtCursor = (before: string, after: string, moveInsideIfNoSelection = true) => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const { start, end, selectedText } = getSelection();
  const value = props.value;

  let newValue: string;
  let newCursorPos: number;

  if (selectedText) {
    // Wrap selected text
    newValue = value.substring(0, start) + before + selectedText + after + value.substring(end);
    newCursorPos = start + before.length + selectedText.length + after.length;
  } else {
    // Insert at cursor
    newValue = value.substring(0, start) + before + after + value.substring(end);
    newCursorPos = moveInsideIfNoSelection ? start + before.length : start + before.length + after.length;
  }

  emit('update:value', newValue);

  nextTick(() => {
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = newCursorPos;
    pushHistory(newValue, newCursorPos, newCursorPos);
  });
};

const insertText = (text: string) => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const { start, end } = getSelection();
  const value = props.value;

  const newValue = value.substring(0, start) + text + value.substring(end);
  const newCursorPos = start + text.length;
  emit('update:value', newValue);

  nextTick(() => {
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = newCursorPos;
    pushHistory(newValue, newCursorPos, newCursorPos);
  });
};

const insertTag = (tagType: 'bold' | 'trait' | 'italic' | 'center') => {
  const tagMap = {
    bold: { before: '【', after: '】' },
    trait: { before: '{', after: '}' },
    italic: { before: '<i>', after: '</i>' },
    center: { before: '<center>', after: '</center>' }
  };

  const tag = tagMap[tagType];
  insertAtCursor(tag.before, tag.after);
};

const insertFlavorTag = () => {
  const { align, padding, quote, flex } = flavorConfig.value;

  // Build attributes, only include non-default values
  const attrs: string[] = [];
  if (align !== 'left') attrs.push(`align="${align}"`);
  if (flex !== true) attrs.push(`flex="${flex}"`);
  if (padding !== 0) attrs.push(`padding="${padding}"`);
  if (quote !== false) attrs.push(`quote="${quote}"`);

  const attrStr = attrs.length > 0 ? ' ' + attrs.join(' ') : '';
  const before = `<flavor${attrStr}>`;
  const after = '</flavor>';

  insertAtCursor(before, after);
  showFlavorModal.value = false;

  // Reset config
  flavorConfig.value = { ...DEFAULT_FLAVOR_CONFIG };
};

const insertSizeTag = () => {
  insertText(`<size "${fontSizeValue.value}">`);
  showSizeModal.value = false;
  fontSizeValue.value = 2;
};

const handleIconSelect = (emoji: string) => {
  insertText(emoji);
  showIconPopover.value = false;
};
</script>

<style scoped>
.body-rich-text-editor {
  display: flex;
  flex-direction: column;
  width: 100%;
  border: 1px solid var(--n-border-color);
  border-radius: 4px;
  overflow: hidden;
  background: var(--n-color);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--n-border-color);
  background: rgba(128, 128, 128, 0.05);
  flex-wrap: wrap;
  gap: 4px;
}

.toolbar-group {
  display: flex;
  align-items: center;
}

.editor-container {
  display: flex;
  min-height: 200px;
  max-height: 400px;
  position: relative;
}

.line-numbers {
  min-width: 40px;
  padding: 8px 4px;
  background: rgba(128, 128, 128, 0.08);
  border-right: 1px solid var(--n-border-color);
  text-align: right;
  user-select: none;
  overflow: hidden;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.line-number {
  color: rgba(128, 128, 128, 0.6);
  padding-right: 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  box-sizing: border-box;
}

.editor-textarea {
  flex: 1;
  padding: 8px 12px;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  background: transparent;
  color: var(--n-text-color);
  overflow-y: auto;
}

.editor-textarea:focus {
  outline: none;
}

/* Dark mode adjustments */
:deep(.n-button) {
  min-width: 32px;
}

:deep(.n-divider--vertical) {
  height: 24px;
  margin: 0 8px;
}

/* Icon grid styles */
.icon-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.icon-grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  min-height: 52px;
}

.icon-grid-item:hover {
  background-color: rgba(128, 128, 128, 0.15);
}

.icon-emoji {
  font-size: 20px;
  line-height: 1.2;
  margin-bottom: 2px;
}

.icon-label {
  font-size: 11px;
  color: rgba(128, 128, 128, 0.8);
  text-align: center;
  line-height: 1.2;
  max-width: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

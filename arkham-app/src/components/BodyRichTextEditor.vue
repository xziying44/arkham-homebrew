<template>
  <div class="body-rich-text-editor">
    <!-- Toolbar -->
    <div class="editor-toolbar">
      <!-- Format Tags -->
      <n-space size="small" class="toolbar-group">
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="wrapWithParagraph">
              <template #icon>
                <n-icon :component="ReorderFourOutline" />
              </template>
              P
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.paragraph') }}
        </n-tooltip>

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

        <n-tooltip v-if="isEnglishCard" trigger="hover">
          <template #trigger>
            <n-button size="small" @click="insertText('<nbsp>')">
              <template #icon>
                <n-icon :component="RemoveOutline" />
              </template>
              nbsp
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.nbsp') }}
        </n-tooltip>

        <n-popover
          trigger="click"
          placement="top-start"
          :width="220"
          v-model:show="showKeywordPopover"
        >
          <template #trigger>
            <n-button size="small">
              <template #icon>
                <n-icon :component="SparklesOutline" />
              </template>
              {{ t('bodyRichTextEditor.keywords') }}
              <n-icon :component="ChevronDownOutline" style="margin-left: 4px;" />
            </n-button>
          </template>
          <div class="keyword-list">
            <div
              v-for="keyword in keywordList"
              :key="keyword.value"
              class="keyword-item"
              @click="handleKeywordSelect(keyword.value)"
            >
              <span class="keyword-tag">{{ keyword.value }}</span>
              <span class="keyword-label">{{ keyword.label }}</span>
            </div>
          </div>
        </n-popover>
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
            <n-button size="small" @click="insertText('<fullnameb>')">
              <template #icon>
                <n-icon :component="PersonOutline" />
              </template>
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.fullnameBack') }}
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

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" @click="showIblockModal = true">
              <template #icon>
                <n-icon :component="PricetagsOutline" />
              </template>
              IB
            </n-button>
          </template>
          {{ t('bodyRichTextEditor.tooltip.iblock') }}
        </n-tooltip>
      </n-space>

      <n-divider vertical />

      <!-- Icon Popover Grid -->
      <n-popover
        trigger="click"
        placement="top-start"
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
        <div class="line-number-spacer" :style="{ height: lineNumberPaddingTop + 'px' }" />
        <template v-for="(lineInfo, index) in visibleLineInfoList" :key="lineNumberStartIndex + index">
          <div class="line-number" :style="{ height: lineInfo.height + 'px' }">
            {{ lineInfo.lineNum > 0 ? lineInfo.lineNum : '' }}
          </div>
        </template>
        <div class="line-number-spacer" :style="{ height: lineNumberPaddingBottom + 'px' }" />
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
      <n-form label-placement="left" label-width="120px">
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

    <!-- Icon Block Modal -->
    <n-modal
      v-model:show="showIblockModal"
      preset="dialog"
      :title="t('bodyRichTextEditor.iblockModal.title')"
      style="width: 720px;"
    >
      <n-form label-placement="left" label-width="120px">
        <n-form-item :label="t('bodyRichTextEditor.iblockModal.icon')">
          <div class="icon-grid icon-grid--selectable">
            <div
              v-for="icon in iblockIconGrid"
              :key="icon.key"
              class="icon-grid-item"
              :class="{ active: icon.value === iblockConfig.icon }"
              @click="iblockConfig.icon = icon.value"
            >
              <span class="icon-emoji">{{ icon.emoji }}</span>
              <span class="icon-label">{{ icon.label }}</span>
            </div>
          </div>
        </n-form-item>
        <n-form-item :label="t('bodyRichTextEditor.iblockModal.gap')">
          <n-input-number
            v-model:value="iblockConfig.gap"
            :min="0"
            :max="200"
            style="width: 100%;"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showIblockModal = false">{{ t('bodyRichTextEditor.common.cancel') }}</n-button>
          <n-button type="primary" @click="insertIblockTag">{{ t('bodyRichTextEditor.common.confirm') }}</n-button>
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
  PricetagsOutline,
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

const DEFAULT_IBLOCK_CONFIG = {
  icon: '',
  gap: 5
};

interface IblockOption {
  labelKey: string;
  value: string;
}

const IBLOCK_ICON_OPTIONS_ZH: IblockOption[] = [
  { labelKey: 'guardian', value: '守护者' },
  { labelKey: 'seeker', value: '探求者' },
  { labelKey: 'rogue', value: '流浪者' },
  { labelKey: 'mystic', value: '潜修者' },
  { labelKey: 'survivor', value: '生存者' },
  { labelKey: 'investigator', value: '调查员' },
  { labelKey: 'reaction', value: '反应' },
  { labelKey: 'action', value: '启动' },
  { labelKey: 'free', value: '免费' },
  { labelKey: 'skull', value: '骷髅' },
  { labelKey: 'cultist', value: '异教徒' },
  { labelKey: 'tablet', value: '石板' },
  { labelKey: 'elderThing', value: '古神' },
  { labelKey: 'tentacle', value: '触手' },
  { labelKey: 'elderSign', value: '旧印' },
  { labelKey: 'brain', value: '脑' },
  { labelKey: 'book', value: '书' },
  { labelKey: 'fist', value: '拳' },
  { labelKey: 'foot', value: '脚' },
  { labelKey: 'wild', value: '?' },
  { labelKey: 'unique', value: '独特' },
  { labelKey: 'dot', value: 'bul' },
  { labelKey: 'bless', value: '祝福' },
  { labelKey: 'curse', value: '诅咒' },
  { labelKey: 'frost', value: '雪花' }
];

const IBLOCK_ICON_OPTIONS_EN: IblockOption[] = [
  { labelKey: 'guardian', value: 'gua' },
  { labelKey: 'seeker', value: 'see' },
  { labelKey: 'rogue', value: 'rog' },
  { labelKey: 'mystic', value: 'mys' },
  { labelKey: 'survivor', value: 'sur' },
  { labelKey: 'investigator', value: 'per' },
  { labelKey: 'reaction', value: 'rea' },
  { labelKey: 'action', value: 'act' },
  { labelKey: 'free', value: 'fre' },
  { labelKey: 'skull', value: 'sku' },
  { labelKey: 'cultist', value: 'cul' },
  { labelKey: 'tablet', value: 'tab' },
  { labelKey: 'elderThing', value: 'mon' },
  { labelKey: 'tentacle', value: 'ten' },
  { labelKey: 'elderSign', value: 'eld' },
  { labelKey: 'brain', value: 'wil' },
  { labelKey: 'book', value: 'int' },
  { labelKey: 'fist', value: 'com' },
  { labelKey: 'foot', value: 'agi' },
  { labelKey: 'wild', value: 'wild' },
  { labelKey: 'unique', value: 'uni' },
  { labelKey: 'dot', value: 'bul' },
  { labelKey: 'bless', value: 'ble' },
  { labelKey: 'curse', value: 'cur' },
  { labelKey: 'frost', value: 'frost' }
];

// State
const showFlavorModal = ref(false);
const showSizeModal = ref(false);
const showIconPopover = ref(false);
const showKeywordPopover = ref(false);
const showIblockModal = ref(false);
const fontSizeValue = ref(2);
const spellcheckEnabled = ref(false);
const iblockConfig = ref({ ...DEFAULT_IBLOCK_CONFIG });

// Undo/Redo history management
interface HistoryState {
  value: string;
  cursorBeforeStart: number;  // 操作前的光标位置
  cursorBeforeEnd: number;
  cursorAfterStart: number;   // 操作后的光标位置
  cursorAfterEnd: number;
}

const history = ref<HistoryState[]>([]);
const historyIndex = ref(-1);
const isUndoRedo = ref(false);
const MAX_HISTORY = 100;

// Push state to history
// cursorBefore: 操作前光标位置, cursorAfter: 操作后光标位置
const pushHistory = (
  value: string,
  cursorBeforeStart: number,
  cursorBeforeEnd: number,
  cursorAfterStart: number,
  cursorAfterEnd: number
) => {
  if (isUndoRedo.value) return;

  // Remove any future states if we're not at the end
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1);
  }

  // Don't push if the value is the same as the last state
  const lastState = history.value[history.value.length - 1];
  if (lastState && lastState.value === value) {
    return;
  }

  history.value.push({
    value,
    cursorBeforeStart,
    cursorBeforeEnd,
    cursorAfterStart,
    cursorAfterEnd
  });

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

  // 当前条目的 cursorBefore 是"这次操作前"的光标位置
  const currentState = history.value[historyIndex.value];

  historyIndex.value--;
  const prevState = history.value[historyIndex.value];

  emit('update:value', prevState.value);

  nextTick(() => {
    const textarea = textareaRef.value;
    if (textarea) {
      textarea.focus();
      // 恢复到操作前的光标位置
      textarea.selectionStart = currentState.cursorBeforeStart;
      textarea.selectionEnd = currentState.cursorBeforeEnd;
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
      // 恢复到操作后的光标位置
      textarea.selectionStart = state.cursorAfterStart;
      textarea.selectionEnd = state.cursorAfterEnd;
    }
    isUndoRedo.value = false;
  });
};

// Initialize history with initial value
watch(
  () => props.value,
  (newValue) => {
    if (!isUndoRedo.value && history.value.length === 0) {
      pushHistory(newValue || '', 0, 0, 0, 0);
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

const isEnglishCard = computed(() => {
  const lang = props.cardLanguage?.toLowerCase() || '';
  return !(lang === 'zh' || lang === 'zh-cht');
});

const defaultIblockIcon = computed(() => 'bul');

const keywordList = computed(() => {
  if (isEnglishCard.value) {
    return [
      { value: '<pre>', label: t('bodyRichTextEditor.keywordLabels.pre') },
      { value: '<spa>', label: t('bodyRichTextEditor.keywordLabels.spa') },
      { value: '<for>', label: t('bodyRichTextEditor.keywordLabels.forced') },
      { value: '<hau>', label: t('bodyRichTextEditor.keywordLabels.haunted') },
      { value: '<obj>', label: t('bodyRichTextEditor.keywordLabels.objective') },
      { value: '<pat>', label: t('bodyRichTextEditor.keywordLabels.patrol') },
      { value: '<rev>', label: t('bodyRichTextEditor.keywordLabels.revelation') }
    ];
  }

  return [
    { value: '<猎物>', label: t('bodyRichTextEditor.keywordLabels.pre') },
    { value: '<生成>', label: t('bodyRichTextEditor.keywordLabels.spa') },
    { value: '<强制>', label: t('bodyRichTextEditor.keywordLabels.forced') },
    { value: '<闹鬼>', label: t('bodyRichTextEditor.keywordLabels.haunted') },
    { value: '<目标>', label: t('bodyRichTextEditor.keywordLabels.objective') },
    { value: '<巡逻>', label: t('bodyRichTextEditor.keywordLabels.patrol') },
    { value: '<显现>', label: t('bodyRichTextEditor.keywordLabels.revelation') }
  ];
});

const resolveIblockIcon = () => {
  const options = iblockIconOptions.value;
  if (options.length === 0) return '';

  const matchedCurrent = options.find((option) => option.value === iblockConfig.value.icon);
  if (matchedCurrent) return matchedCurrent.value;

  const matchedDefault = options.find((option) => option.value === defaultIblockIcon.value);
  return (matchedDefault || options[0]).value;
};

const iblockIconOptions = computed(() => {
  const source = isEnglishCard.value ? IBLOCK_ICON_OPTIONS_EN : IBLOCK_ICON_OPTIONS_ZH;
  return source.map((item) => ({
    label: t(`bodyRichTextEditor.iconLabels.${item.labelKey}`),
    value: item.value
  }));
});

const iblockIconGrid = computed(() => {
  const source = isEnglishCard.value ? IBLOCK_ICON_OPTIONS_EN : IBLOCK_ICON_OPTIONS_ZH;
  const valueMap = source.reduce<Record<string, string>>((acc, cur) => {
    acc[cur.labelKey] = cur.value;
    return acc;
  }, {});

  return iconList.value
    .filter((item) => valueMap[item.key])
    .map((item) => ({
      key: item.key,
      label: item.label,
      value: valueMap[item.key],
      emoji: item.emoji
    }));
});

watch(
  iblockIconOptions,
  (options) => {
    if (options.length === 0) {
      iblockConfig.value.icon = DEFAULT_IBLOCK_CONFIG.icon;
      return;
    }

    const resolvedIcon = resolveIblockIcon();
    if (iblockConfig.value.icon !== resolvedIcon) {
      iblockConfig.value.icon = resolvedIcon;
    }
  },
  { immediate: true }
);

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
const MIN_VISIBLE_LINE_COUNT = 10;
const LINE_BUFFER_COUNT = 5;
const textareaHeight = ref(0);
const textareaScrollTop = ref(0);

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

const updateTextareaMetrics = () => {
  if (textareaRef.value) {
    // Subtract padding (12px left + 12px right = 24px)
    textareaWidth.value = textareaRef.value.clientWidth - 24;
    textareaHeight.value = textareaRef.value.clientHeight;
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
  const containerWidth = textareaWidth.value > 0 ? textareaWidth.value : 300; // Fallback width

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

const lineNumberVirtualData = computed(() => {
  const total = lineInfoList.value.length;
  const viewportLineCount = Math.max(
    MIN_VISIBLE_LINE_COUNT,
    Math.ceil((textareaHeight.value || 0) / LINE_HEIGHT)
  );
  const rawStartIndex = Math.max(
    0,
    Math.floor((textareaScrollTop.value || 0) / LINE_HEIGHT) - LINE_BUFFER_COUNT
  );
  const startIndex = Math.min(rawStartIndex, Math.max(total - viewportLineCount, 0));
  const endIndex = Math.min(total, startIndex + viewportLineCount + LINE_BUFFER_COUNT * 2);

  return {
    items: lineInfoList.value.slice(startIndex, endIndex),
    paddingTop: startIndex * LINE_HEIGHT,
    paddingBottom: Math.max(0, (total - endIndex) * LINE_HEIGHT),
    startIndex
  };
});

const visibleLineInfoList = computed(() => lineNumberVirtualData.value.items);
const lineNumberPaddingTop = computed(() => lineNumberVirtualData.value.paddingTop);
const lineNumberPaddingBottom = computed(() => lineNumberVirtualData.value.paddingBottom);
const lineNumberStartIndex = computed(() => lineNumberVirtualData.value.startIndex);

// Setup resize observer for textarea width changes
let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  updateTextareaMetrics();

  if (textareaRef.value) {
    resizeObserver = new ResizeObserver(() => {
      updateTextareaMetrics();
    });
    resizeObserver.observe(textareaRef.value);

    // Track cursor position for undo/redo
    textareaRef.value.addEventListener('mouseup', updateLastCursor);
    textareaRef.value.addEventListener('focus', updateLastCursor);
  }

  nextTick(() => {
    textareaScrollTop.value = textareaRef.value?.scrollTop || 0;
  });
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  if (textareaRef.value) {
    textareaRef.value.removeEventListener('mouseup', updateLastCursor);
    textareaRef.value.removeEventListener('focus', updateLastCursor);
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

// Track last cursor position for handleInput
let lastCursorStart = 0;
let lastCursorEnd = 0;

// Update last cursor position on various events
const updateLastCursor = () => {
  if (textareaRef.value) {
    lastCursorStart = textareaRef.value.selectionStart;
    lastCursorEnd = textareaRef.value.selectionEnd;
  }
};

// Handlers
const handleInput = (e: Event) => {
  const target = e.target as HTMLTextAreaElement;
  const newValue = target.value;
  const cursorAfter = target.selectionStart;

  emit('update:value', newValue);

  // Push to history with cursor before (from lastCursor) and after
  nextTick(() => {
    pushHistory(newValue, lastCursorStart, lastCursorEnd, cursorAfter, cursorAfter);
    // Update last cursor for next operation
    updateLastCursor();
    syncScroll();
  });
};

const syncScroll = () => {
  if (textareaRef.value) {
    const { scrollTop } = textareaRef.value;
    textareaScrollTop.value = scrollTop;
    if (lineNumbersRef.value) {
      lineNumbersRef.value.scrollTop = scrollTop;
    }
  }
};

const handleKeydown = (e: KeyboardEvent) => {
  // Update last cursor position before any key action
  updateLastCursor();

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
    const newCursorPos = start + 2;
    emit('update:value', newValue);

    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = newCursorPos;
      pushHistory(newValue, start, end, newCursorPos, newCursorPos);
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
    // 记录操作前光标(start, end)和操作后光标(newCursorPos)
    pushHistory(newValue, start, end, newCursorPos, newCursorPos);
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
    // 记录操作前光标(start, end)和操作后光标(newCursorPos)
    pushHistory(newValue, start, end, newCursorPos, newCursorPos);
  });
};

const wrapWithParagraph = () => {
  insertAtCursor('<p>', '</p>');
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

const insertIblockTag = () => {
  const icon = resolveIblockIcon();
  const rawGap = Number.isFinite(iblockConfig.value.gap) ? Math.round(iblockConfig.value.gap) : DEFAULT_IBLOCK_CONFIG.gap;
  const gap = Math.min(200, Math.max(0, rawGap));

  if (!icon) {
    showIblockModal.value = false;
    iblockConfig.value = { ...DEFAULT_IBLOCK_CONFIG };
    return;
  }

  insertAtCursor(`<iblock icon="${icon}" gap="${gap}">`, '</iblock>');
  showIblockModal.value = false;
  iblockConfig.value = { ...DEFAULT_IBLOCK_CONFIG, icon };
};

const handleIconSelect = (emoji: string) => {
  insertText(emoji);
  showIconPopover.value = false;
};

const handleKeywordSelect = (value: string) => {
  insertText(value);
  showKeywordPopover.value = false;
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

.line-number-spacer {
  width: 100%;
  flex-shrink: 0;
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
  max-height: 320px;
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
  border: 1px solid transparent;
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

.icon-grid--selectable {
  margin-top: 4px;
  width: 100%;
  grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
  gap: 8px;
}

.icon-grid--selectable .icon-grid-item.active {
  border-color: var(--n-primary-color);
  background-color: rgba(24, 160, 88, 0.08);
}

.keyword-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 240px;
  overflow-y: auto;
}

.keyword-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.keyword-item:hover {
  background-color: rgba(128, 128, 128, 0.15);
}

.keyword-tag {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: var(--n-text-color);
}

.keyword-label {
  font-size: 12px;
  color: rgba(128, 128, 128, 0.8);
  margin-left: 12px;
}
</style>

# Components Module Documentation

This document provides a complete, multi‑layer reference for the Vue 3 components in this directory. It focuses on component architecture, composition patterns, and full API coverage (props, emits, and noteworthy types).

## 1) Overview
- Purpose: Frontend components for Arkham app authoring and deck/content workflows.
- Stack: Vue 3 + script setup + TypeScript, Composition API, Naive UI, vue‑i18n.
- Conventions: Typed `defineProps`/`defineEmits`, event‑driven updates, reactive local copies of inputs, and internationalization via `useI18n`.

## 2) Architecture & Dependencies
- Core editors/panels orchestrate specialized subcomponents:
  - `FormEditPanel.vue`: Primary card editor shell; composes `CardSideEditor`, `IllustrationLayoutEditor`, `DeckOptionEditor`, and `TtsScriptEditor`.
  - `DeckEditor.vue`: Deck building/export workflow; integrates `TTSExportGuide.vue` and TTS export services.
  - `PackageEditor.vue`: Content package editor; integrates `UniversalUploadDialog` and file browser tools.
- Shared utilities and panels:
  - `FileTreePanel.vue`, `ImagePreviewPanel.vue`, `WorkspaceSidebar.vue`, `ResizeSplitter.vue`.
  - Selectors/dialogs: `CardFileBrowser.vue`, `UniversalUploadDialog.vue`, `LanguageWelcomeModal.vue`.
- Child component imports (intra‑module):
  - `FormEditPanel.vue` → `CardSideEditor.vue`, `IllustrationLayoutEditor.vue`, `DeckOptionEditor.vue`, `TtsScriptEditor.vue`
  - `CardSideEditor.vue` → `FormField.vue`, `IllustrationLayoutEditor.vue`, `TextBoundaryEditor.vue`
  - `DeckEditor.vue` → `TTSExportGuide.vue`
  - `PackageEditor.vue` → `UniversalUploadDialog.vue`
  - `TtsScriptEditor.vue` → `CardFileBrowser.vue`
- External libraries used across components: Naive UI (`n-*` components), `@vicons/ionicons5`, `vue-i18n`, and project API services under `@/api`.

## 3) Component Catalog
- Editors
  - `FormEditPanel.vue` – Card editing hub (single/double‑sided cards, preview, cache & save workflows)
  - `CardSideEditor.vue` – Side‑specific card fields editor, type/language switching, collapsible illustration layout, text boundary drawer
  - `IllustrationLayoutEditor.vue` – Visual crop/offset/scale/rotate/flip editor for card art
  - `TextBoundaryEditor.vue` – Advanced text boundary adjustment (body boundaries + flavor padding)
  - `DeckOptionEditor.vue` – Investigator deck building options editor
  - `TtsScriptEditor.vue` – TTS scripting config editor (per card type), integrates file browser
  - 行为（V2 改造）：
    - 仅保存 `tts_config` 到卡文件（不再写入旧版 `tts_script` 字段）。
    - 预览调用后端 `POST /api/tts/generate`（一次性首帧 + 250ms 防抖；父写回屏蔽避免循环）。
    - 升级表脚本：将坐标保存到 `tts_config.upgrade.coordinates`，后端统一生成 Lua。
    - 签名卡：按相对路径保存 `{ path, count }`；显示名称取文件树 `name`（或文件名）。后端按路径解析稳定脚本 ID，GMNotes 继续输出旧式 `signatures`（ID 聚合）。
  - 封印脚本（新增）：
    - 适用范围：除“调查员”“定制卡（升级表）”以外的所有卡牌类型。
    - 前端配置：
      - 开关：`seal.enabled`
      - 可封印的标记：
        • 选项一：`seal.allTokens = true`（允许所有 Token）
        • 选项二：`seal.tokens: string[]`（从混沌标记集合多选：Elder Sign/+1/0/-1…/Skull/Cultist/Tablet/Elder Thing/Auto-fail/Bless/Curse/Frost）
      - 数量上限：`seal.max`（空/0 表示不限制；后端不注入 MAX_SEALED，从封印库默认 99 继承）
      - UI 细节：
        • 多选下拉全宽、带 emoji 与 i18n 标签；清空为独立按钮避免与下拉箭头冲突
        • “可封印所有 Token”复选框扩大点击区域并文本垂直居中
    - 预览：更改任何配置都会 250ms 防抖触发后端预览；结果回显到 GMNotes/LuaScript 预览框。
    - 运行时语言：菜单语言与标记名会根据卡片 `language` 传给后端，由 Lua 脚本内置 i18n（zh/英文）。
  - `DeckEditor.vue` – Deck content arrangement and export integration
  - `PackageEditor.vue` – Content package metadata and assets editor
  - `TTSExportGuide.vue` – Step‑by‑step guide for TTS export from a deck
- Panels/Navigation
  - `FileTreePanel.vue` – Project tree, file operations, export and sync actions
  - `ImagePreviewPanel.vue` – Live image/side preview with zoom/pan and loading state
  - `WorkspaceSidebar.vue` – Navigation for workspace modules (responsive)
  - `ResizeSplitter.vue` – Resizable splitter (vertical)
- Dialogs/Inputs
  - `FormField.vue` – Field renderer for many input types; emits rich edit events
  - `UniversalUploadDialog.vue` – Multi‑host image upload (banner/card/encounter) dialog
  - `CardFileBrowser.vue` – Directory/card picker dialog
  - `LanguageWelcomeModal.vue` – First‑run language selection modal

## 4) Component APIs (Props, Emits, Signatures)

Notes
- All components use Vue 3 `<script setup lang="ts">` with typed `defineProps`/`defineEmits`.
- Signatures show props and emits succinctly; optional props are marked with `?`. Defaults are noted when defined via `withDefaults`.

### IllustrationLayoutEditor.vue
Signature
```ts
IllustrationLayoutEditor(
  props: { imageSrc: string; layout?: Partial<PictureLayout>; card_type?: string },
  emits: { 'update:layout'(layout: PictureLayout): void }
)

type PictureLayout = {
  mode: 'auto' | 'custom';
  offset: { x: number; y: number };
  scale: number;
  crop: { top: number; right: number; bottom: number; left: number };
  rotation: number;
  flip_horizontal: boolean;
  flip_vertical: boolean;
}
```
Behavior
- Visual editor with drag to offset, wheel+Alt to scale, handles to crop, rotate/flip, deep sync with `layout` prop.
- Emits `update:layout` with a sanitized, fully merged layout.

### CardSideEditor.vue
Signature
```ts
CardSideEditor(
  props: {
    side: 'front' | 'back';
    cardData: any;
    cardTypeConfigs: Record<string, CardTypeConfig>;
    cardTypeOptions: any[];
    languageOptions: any[];
  },
  emits: {
    'update-card-data'(side: string, fieldKey: string, value: any): void;
    'update-card-type'(side: string, type: string): void;
    'trigger-preview'(): void;
  }
)

// Exposed methods (via defineExpose)
{
  cardTypeSection: Ref<HTMLElement | null>;
  propertiesSection: Ref<HTMLElement | null>;
  illustrationSection: Ref<HTMLElement | null>;
  textLayoutSection: Ref<HTMLElement | null>;
  cardInfoSection: Ref<HTMLElement | null>;
  expandIllustrationLayout(): void;
}
```
Behavior
- Manages a reactive clone of `cardData`; updates emit precise field changes and card type changes.
- Integrates `FormField` for per‑field rendering and `IllustrationLayoutEditor` for art.
- Features collapsible illustration layout settings with toggle button at bottom of card properties panel.
- Integrates `TextBoundaryEditor` via left-side drawer (no mask overlay) for advanced text boundary adjustments.
- Exposes section refs and `expandIllustrationLayout()` method for parent navigation:
  - Uses function refs pattern (`setCardTypeSection`, `setPropertiesSection`, etc.) to capture DOM elements from `<n-card>` component instances
  - Exposes refs via `defineExpose` (auto‑unwrapped by Vue 3, accessible without extra `.value` from parent)
  - `expandIllustrationLayout()`: Programmatically expands illustration section when called from parent navigation

### TextBoundaryEditor.vue
Signature
```ts
interface TextBoundary {
  body: {
    top: number;      // Range: -50 to 50
    bottom: number;   // Range: -50 to 50
    left: number;     // Range: -50 to 50
    right: number;    // Range: -50 to 50
  };
  flavor: {
    padding: number;  // Range: 0 to 100, default: 20
  };
}

TextBoundaryEditor(
  props: {
    cardType: string;
    textBoundary?: TextBoundary;
  },
  emits: {
    'update:text-boundary'(value: TextBoundary): void;
  }
)
```
Behavior
- Provides 5 sliders for precise text boundary adjustments: body (top/bottom/left/right) and flavor padding.
- Body boundaries: positive values expand outward, negative values shrink inward (-50px to +50px).
- Flavor padding: controls padding value for flavor text (0px to 100px, default 20px).
- Real-time updates with 0.5s debounced preview refresh.
- Integrates with backend `_tidy_body_flavor` and `draw_text` boundary_offset parameters.

### FileTreePanel.vue
Signature
```ts
FileTreePanel(
  props: { width: number; selectedFile?: TreeOption | null; unsavedFilePaths?: string[] },
  emits: {
    'toggle'(): void;
    'go-back'(): void;
    'file-select'(keys: Array<string | number>, option?: TreeOption): void;
    'refresh-file-tree'(): void;
  }
)
```
Behavior
- Hosts project tree interactions, export actions, and integrations with services (`WorkspaceService`, `CardService`, etc.).

Changelog (2025‑11‑10)
- FormEditPanel.vue: 当正面选择“调查员小卡”时，自动初始化背面为同类型，默认前=normal、后=grayscale 且共享插画。
- TtsScriptEditor.vue: 新增“调查员小卡”绑定调查员卡牌（选择路径）；绑定后脚本ID禁用，后端生成 `<investigator_id>-m`。
- FileTreePanel.vue: 文件树卡牌类型图标映射增加“调查员小卡”（🧩）。

Changelog (2025‑11‑11)
- PackageEditor.vue
  - 添加上传会话隔离：打开上传页面时冻结 `packageData`（深拷贝快照 `uploadConfigSnapshot`），所有上传对话框以快照为 `:config` 来源，避免切包导致上传写入错误包。
  - 在 `handleUploadConfirm` 中，若存在快照则强制对齐 `updatedPackage.path = snapshot.path`，作为保险丝。
  - 切换旧式上传模态的 `:config` 同步切换为使用快照。
- UniversalUploadDialog.vue
  - 封面文件唯一命名：基于包唯一标识（优先 `meta.code`，否则从 `path`/`name` 派生，最后回退 UUID），生成 `banners/<code>` 与 `banners/<code>_box`，彻底避免跨包 `banner/banner_box` 覆盖。
  - 上传成功后清空 `updatedPackage.banner_base64`，确保 UI 始终以 URL 显示、避免 base64 回退造成的“错乱”。
  - 不改变卡牌/遭遇组上传的既有命名策略。

### FormField.vue
Signature
```ts
FormField(
  props: { field: FormField; value: any; newStringValue: string },
  emits: {
    'update:value'(value: any): void;
    'update:new-string-value'(value: string): void;
    'add-multi-select-item'(value: string): void;
    'remove-multi-select-item'(index: number): void;
    'add-string-array-item'(): void;
    'remove-string-array-item'(index: number): void;
    'move-string-array-item-up'(index: number): void;
    'move-string-array-item-down'(index: number): void;
    'edit-string-array-item'(index: number, newValue: string): void;
    'remove-image'(): void;
  }
)
```
Behavior
- Renders heterogeneous field types with validation, list editing, and upload/remove events.

### FormEditPanel.vue
Signature
```ts
FormEditPanel(
  props: {
    showFileTree: boolean;
    showImagePreview: boolean;
    selectedFile?: TreeOption | null;
    isMobile?: boolean;
    unsavedFilesCount?: number;
  },
  emits: {
    'toggle-file-tree'(): void;
    'toggle-image-preview'(): void;
    'update-preview-image'(image: string | { front: string; back?: string }): void;
    'update-preview-side'(side: 'front' | 'back'): void;
    'update-preview-loading'(loading: boolean): void;
    'refresh-file-tree'(): void;
    'save-to-cache'(filePath: string, data: any): void;
    'load-from-cache'(filePath: string): void;
    'clear-cache'(filePath: string): void;
    'trigger-save-all'(): void;
  }
)
```
Behavior
- Orchestrates card edit flow (single/double‑sided), live preview updates, caching, and i18n‑aware type configs.
- Quick navigation bar (7 sections: cardType, properties, illustration, textLayout, cardInfo, ttsScript, deckOptions):
  - Defaults to collapsed state (displays as floating circle button)
  - Auto‑collapses after clicking any navigation item to scroll
  - Resets to collapsed state when switching files
  - Special handling for illustration: when collapsed, clicking its nav first expands the section (via `CardSideEditor.expandIllustrationLayout()`), then scrolls
- Accesses child section refs correctly via Vue 3's `defineExpose` auto‑unwrapping (no extra `.value` needed)

### ResizeSplitter.vue
Signature
```ts
ResizeSplitter(
  props: { isActive?: boolean; title?: string },
  emits: { 'start-resize'(event: MouseEvent): void }
)
```
Behavior
- Emits drag start for parent‑managed resizing.

### PackageEditor.vue
Signature
```ts
PackageEditor(
  props: { package: ContentPackageFile; saving: boolean },
  emits: { 'save'(): void; 'update:package'(value: ContentPackageFile): void }
)
```
Behavior
- Edit content package metadata/assets; integrates `UniversalUploadDialog` and file browser.

### LanguageWelcomeModal.vue
Signature
```ts
LanguageWelcomeModal(
  props: { show: boolean },
  emits: { 'update:show'(value: boolean): void; 'language-selected'(language: string): void }
)
```
Behavior
- First‑run language selection and persistence.

### ImagePreviewPanel.vue
Signature
```ts
ImagePreviewPanel(
  props: {
    width: number;
    currentImage: string | { front: string; back?: string };
    imageKey: string | null;
    currentSide: 'front' | 'back';
    isLoading?: boolean;
  },
  emits: { 'toggle'(): void; 'update-side'(side: 'front' | 'back'): void }
)
```
Behavior
- Live image preview with side switching, zoom/pan, and loading states; optimized for mobile.

### TtsScriptEditor.vue
Signature
```ts
TtsScriptEditor(
  props: {
    cardData: Record<string, any>;
    cardType: string;
    isDoubleSided?: boolean;      // default: false
    currentSide?: 'front' | 'back';// default: 'front'
  },
  emits: { 'update-tts-script'(data: TtsScriptData): void }
)

type TtsScriptData = {
  GMNotes: string;
  LuaScript: string;
  config?: {
    enablePhaseButtons: boolean;
    phaseButtonConfig: any;               // PhaseButtonConfig
    investigatorConfig: any;              // InvestigatorConfig
    assetConfig: any;                     // AssetConfig
    locationConfig: any;                  // LocationConfig
    scriptConfig: any;                    // ScriptConfig
    signatureConfig: Array<{ id: string; name: string; count: number }>;
    entryTokensConfig: any[];             // UseConfig[]
    gameStartConfig: { startsInPlay: boolean; startsInHand: boolean };
  };
}
```
Behavior
- Generates per‑type TTS Lua/GMNotes with optional phase buttons, location/asset/investigator options; integrates `CardFileBrowser`.

### TTSExportGuide.vue
Signature
```ts
TTSExportGuide(
  props: { deck: DeckFile },
  emits: {
    'back'(): void;
    'update:deck'(deck: DeckFile): void;
    'openSettings'(): void;
  }
)
```
Behavior
- Multi‑step export guide with image export settings and TTS metadata handling.

### UniversalUploadDialog.vue
Signature
```ts
type UploadType = 'banner' | 'card' | 'encounter';

UniversalUploadDialog(
  props: {
    uploadType: UploadType;
    currentItem?: any;
    uploadItems?: any[];
    config?: any;
    isBatch?: boolean;
  },
  emits: { 'confirm'(updatedPackage: any): void; 'cancel'(): void }
)
```
Behavior
- Handles single/batch uploads across supported hosts; emits final package update.

### WorkspaceSidebar.vue
Signature
```ts
WorkspaceSidebar(
  props: { activeItem: string },
  emits: { 'item-select'(key: string): void; 'go-back'(): void }
)
```
Behavior
- Responsive navigation with collapse on small screens; window resize listeners.

### DeckEditor.vue
Signature
```ts
DeckEditor(
  props: {
    deck: DeckFile | null;
    availableCards: CardFile[];
    availableImages: ImageFile[];
    saving?: boolean; // default: false
  },
  emits: { 'save'(): void; 'update:deck'(deck: DeckFile): void; 'load-images'(): void }
)
```
Behavior
- Compose deck contents (cards/cardbacks/images), search/filter, and integrate TTS export (`TTSExportGuide`).

### DeckOptionEditor.vue
Signature
```ts
DeckOptionEditor(
  props: {
    cardData: Record<string, any>;
    cardType: string;
    isDoubleSided?: boolean;       // default: false
    currentSide?: 'front' | 'back'; // default: 'front'
  },
  emits: { 'update-deck-options'(options: DeckOption[]): void }
)
```
Behavior
- Investigator deckbuilding constraints (faction, level, traits, slots, etc.); only shown for investigator/back types.

### CardFileBrowser.vue
Signature
```ts
type BrowserItem = { name: string; path: string; type: 'directory' | 'card'; fullPath: string };

CardFileBrowser(
  props: { visible: boolean },
  emits: {
    'update:visible'(value: boolean): void;
    'confirm'(items: BrowserItem[]): void;
  }
)
```
Behavior
- Directory and card selection tool used by editors to attach files.

## 5) Composition Patterns & Conventions
- Script setup + TS: All components use `<script setup lang="ts">` with typed `defineProps`/`defineEmits` (and `withDefaults` where appropriate).
- Reactive cloning: Editors typically clone incoming data into `reactive` local state, then emit granular updates (e.g., `CardSideEditor`, `FormEditPanel`).
- Computed setters: Two‑way logical bindings via computed getters/setters (e.g., current language, quantity) to centralize emit logic.
- Watchers for sync: `watch`/deep watch used to merge default structures and sanitize values (e.g., `IllustrationLayoutEditor` crop normalization).
- i18n first: All labels through `useI18n()`; components prefer keys over literals to support multi‑language UIs.
- UI kit: Naive UI components drive form structure; events propagate upward (parent owns mutation/persistence).
- File/services boundary: Side‑effectful ops are delegated to services under `@/api/*`.

## 6) Usage & Integration
- General usage example
```vue
<template>
  <FormEditPanel
    :show-file-tree="showTree"
    :show-image-preview="showPreview"
    :selected-file="selected"
    :is-mobile="isMobile"
    :unsaved-files-count="unsaved"
    @toggle-file-tree="onToggleTree"
    @toggle-image-preview="onTogglePreview"
    @update-preview-image="onPreviewImage"
    @update-preview-side="onPreviewSide"
    @update-preview-loading="onPreviewLoading"
    @refresh-file-tree="refreshTree"
    @trigger-save-all="saveAll"
  />
</template>
```
- Illustration layout editor example
```vue
<IllustrationLayoutEditor
  :image-src="imageUrl"
  :layout="artLayout"
  :card_type="cardType"
  @update:layout="artLayout = $event"
/>
```
- Deck export guide integration
```vue
<DeckEditor
  :deck="deck"
  :available-cards="cards"
  :available-images="images"
  :saving="isSaving"
  @save="saveDeck"
  @update:deck="deck = $event"
  @load-images="loadImages"
/>
```

---

Appendix: File Index
- Editors: `FormEditPanel.vue`, `CardSideEditor.vue`, `IllustrationLayoutEditor.vue`, `TextBoundaryEditor.vue`, `DeckOptionEditor.vue`, `TtsScriptEditor.vue`, `DeckEditor.vue`, `PackageEditor.vue`, `TTSExportGuide.vue`
- Panels: `FileTreePanel.vue`, `ImagePreviewPanel.vue`, `WorkspaceSidebar.vue`, `ResizeSplitter.vue`
- Dialogs/Inputs: `FormField.vue`, `UniversalUploadDialog.vue`, `CardFileBrowser.vue`, `LanguageWelcomeModal.vue`


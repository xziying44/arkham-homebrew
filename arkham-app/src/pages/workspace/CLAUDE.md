# workspace/

## Purpose and Scope
This folder contains the “Workspace” pages that power the in-app editing and management experience:
- Card and deck authoring (grid-based deck builder)
- Content package management for distribution/consumption
- Core workspace editor (file tree + form editor + image preview)
- Application settings and About page

These pages are rendered inside `WorkspacePage.vue` (at `src/pages/WorkspacePage.vue`) and compose the main working area after a project/workspace is chosen.

## Structure Overview
Directory organization of the workspace pages:
```
workspace/
  WorkspaceMain.vue   - Primary editor (file tree + form + preview)
  DeckBuilder.vue     - Deck authoring UI and persistence
  TTSItems.vue        - Content package manager (was TTS items)
  Settings.vue        - App + workspace configuration UI
  About.vue           - App information and links
```

## Key Components
### WorkspaceMain.vue
- Description: The central editing surface with a left file tree, middle JSON-based form editor, and right image preview, optimized for desktop and mobile.
- Responsibilities: File selection, preview coordination, unsaved cache management, responsive layout, and panel resizing.
- Public API
  #### Props
  - mode: 'file' | 'folder' — workspace open mode [required]
  - projectPath?: string — absolute/OS path of the project [optional]
  - projectName?: string — human-friendly project name [optional]
  #### Emits
  ##### `go-back(): void`
  - Purpose: Notify parent to navigate back to the home page.
  - Parameters: none
  - Returns: (void)

### DeckBuilder.vue
- Description: Visual deck builder for composing card grids, including shared back support and TTS metadata.
- Responsibilities: Load/save `.deck` files, browse available cards/images, and coordinate with `DeckEditor` for editing.
- Public API
  - Props: none
  - Emits: none

### TTSItems.vue (Content Package Manager)
- Description: Manage content packages (`.pack`), including metadata, banner, and included cards/encounter sets.
- Responsibilities: Create, load, update, and persist packages under `ContentPackage/`.
- Public API
  - Props: none
  - Emits: none

### Settings.vue
- Description: Configure app/workspace settings (language, workspace directories, footer icon) and GitHub image hosting.
- Responsibilities: Load and persist config, verify GitHub token, fetch repositories, and select directories/images from the workspace.
- Public API
  - Props: none
  - Emits: none

### About.vue
- Description: Static “About” page with project details, feature highlights, and copy-to-clipboard helpers.
- Responsibilities: Present information with small UX helpers (copy-to-clipboard, responsive layout).
- Public API
  - Props: none
  - Emits: none

## Dependencies
### Internal Dependencies
- `@/components/FileTreePanel.vue` — File navigation and selection (WorkspaceMain.vue)
- `@/components/FormEditPanel.vue` — JSON-based form editor (WorkspaceMain.vue)
- `@/components/ImagePreviewPanel.vue` — Image preview with face switching (WorkspaceMain.vue)
- `@/components/ResizeSplitter.vue` — Drag-to-resize splitter (WorkspaceMain.vue)
- `@/components/DeckEditor.vue` — Deck editing surface (DeckBuilder.vue)
- `@/components/PackageEditor.vue` — Content package editing surface (TTSItems.vue)
- `@/api` (`WorkspaceService`, `ConfigService`) — File tree, file IO, config persistence
- `@/api/github-service` — GitHub auth/status/repos for image hosting (Settings.vue)
- `@/types/content-package` — Package types, factories, and options (TTSItems.vue)

### External Dependencies
- `vue` — Composition API and `<script setup>` runtime
- `vue-i18n` — i18n translations and locale management
- `naive-ui` — UI components (forms, inputs, lists, modals, upload, etc.)
- `@vicons/ionicons5` — Icon set used across UIs
- `uuid` — Generate content package codes (TTSItems.vue)

## Integration Points
### Public APIs
- WorkspaceMain.vue
  - `go-back(): void` — Upward navigation signal to parent.

### Data Flow
- WorkspaceMain
  - Input: Tree selections; props (`mode`, `projectPath`, `projectName`).
  - Processing: Determines panel visibility by breakpoints; manages unsaved cache (`Map<string, any>`); coordinates preview image and face.
  - Output: Emits `go-back` on user action; updates child panels via events.
- DeckBuilder
  - Input: Workspace file tree (`WorkspaceService.getFileTree()`), `.deck` JSON files.
  - Processing: Normalizes legacy deck formats; populates deck list; coordinates with `DeckEditor`.
  - Output: Persists `.deck` via `WorkspaceService.saveFileContent`.
- TTSItems
  - Input: Workspace file tree and `.pack` JSON.
  - Processing: Create/update package meta and banner; maintain cards/encounter sets.
  - Output: Persists `.pack` via `WorkspaceService.createFile` / `saveFileContent`.
- Settings
  - Input: Existing config from `ConfigService.getConfig()` and workspace file tree.
  - Processing: Verify GitHub token; fetch repo list; choose directories/images; update language.
  - Output: Writes merged config via `ConfigService.saveConfig()`.

## Implementation Notes
### Design Patterns
- Composition API with `<script setup>` for concise component modules.
- Event-driven child↔parent communication (emits for navigation and panel control).
- Responsive layout: breakpoint-based conditional rendering; mobile full-screen modals.
- Dynamic child composition (e.g., DeckEditor/PackageEditor are injected as feature surfaces).

### Technical Decisions
- Use `markRaw` for component map in parent (`WorkspacePage.vue`) to avoid proxying.
- Cache unsaved edits with deep-copied snapshots to prevent mutation bleed-through.
- Normalize legacy deck data to current schema for backward compatibility.

### Considerations
- Performance: Throttle resize with `requestAnimationFrame`; conditional render heavy panels on small screens.
- Security: Never log or persist GitHub token beyond auth flow; avoid console logging secrets.
- Limitations: Settings only enumerates PNG images from root dir; package/deck schemas must be valid JSON.


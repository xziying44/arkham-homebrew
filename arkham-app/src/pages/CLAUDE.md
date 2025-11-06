# pages/

## Purpose and Scope
Top-level application pages for project selection and the main workspace.
- `HomePage.vue`: Landing screen to select/open a project and view recent projects.
- `WorkspacePage.vue`: Container for workspace sub-pages (editor, deck builder, packages, settings, about).

This folder orchestrates navigation from initial project selection to the working environment.

## Structure Overview
```
pages/
  HomePage.vue         - Landing and project selection (desktop/mobile layouts)
  WorkspacePage.vue    - Tabs/areas for workspace features
  workspace/           - Workspace feature pages (see workspace/CLAUDE.md)
```

## Key Components
### HomePage.vue
- Description: Welcome screen with language switcher, recent projects, and “Open Project” action (responsive for desktop/mobile).
- Responsibilities: Detect backend service status, list/manage recent projects, open a directory via backend, and emit navigation.
- Public API (Emits)
  #### `navigate-to-workspace(params: { mode: 'file' | 'folder'; projectPath: string; projectName: string }): void`
  - Purpose: Request parent/router to open the workspace with the selected project
  - Parameters:
    • params.mode ('file'|'folder'): open mode based on selection
    • params.projectPath (string): absolute/OS path for project root
    • params.projectName (string): display-friendly project name
  - Returns: (void)
  - Throws: none

### WorkspacePage.vue
- Description: Hosts the workspace areas and routes user actions across feature tabs.
- Responsibilities: Accept initial project context and switch among WorkspaceMain, DeckBuilder, ContentPackage, Settings, and About.
- Public API
  #### Props
  - mode: 'file' | 'folder' — open mode [required]
  - projectPath?: string — absolute path [optional]
  - projectName?: string — display name [optional]
  #### Emits
  ##### `navigate-to-home(): void`
  - Purpose: Request parent/router to return to the home screen
  - Parameters: none
  - Returns: (void)

## Dependencies
### Internal Dependencies
- `@/api/directory-service` — Choose directory, list/clear/remove recent (HomePage)
- `@/api` (`ConfigService`) — Load/save app configuration (HomePage/Workspace children)
- `@/api/http-client` (`ApiError`) — Typed error handling (HomePage)
- `@/locales` (`setLanguage`) — Apply language globally (HomePage)
- `@/components/LanguageWelcomeModal.vue` — First-visit language prompt (HomePage)
- `@/components/WorkspaceSidebar.vue` — Sidebar navigation (WorkspacePage)
- `./workspace/*` — Feature pages; see `workspace/CLAUDE.md`

### External Dependencies
- `vue` — Composition API and `<script setup>`
- `vue-i18n` — Internationalization
- `naive-ui` — UI components library
- `@vicons/ionicons5` — Icons used in buttons and lists

## Integration Points
### Public APIs
- `HomePage.vue` emits `navigate-to-workspace(...)` to move into the workspace
- `WorkspacePage.vue` emits `navigate-to-home()` to return to the home screen

### Data Flow
- Input → Processing → Output
  - HomePage
    • Input: Backend service status, recent directories, user action to open folder
    • Processing: Poll service; call DirectoryService; update UI state
    • Output: Emits `navigate-to-workspace` with project details
  - WorkspacePage
    • Input: Props (`mode`, `projectPath`, `projectName`)
    • Processing: Resolve active tab to component map; forward props to children
    • Output: Emits `navigate-to-home` on back action

## Implementation Notes
### Design Patterns
- Composition API with `<script setup>` and strongly-typed emits
- Event-driven navigation between top-level pages
- Responsive UIs (desktop split panes vs. mobile single-page with bottom nav)

### Technical Decisions
- Poll backend status every 5s on HomePage for connection feedback
- Map string keys to child components using `markRaw` (reduce proxy overhead)

### Considerations
- Performance: Avoid unnecessary renders on mobile; conditional sections per breakpoint
- Security: Handle `ApiError` gracefully; don’t expose raw errors to end users
- Limitations: WorkspacePage expects children defined under `workspace/` (see referenced doc)


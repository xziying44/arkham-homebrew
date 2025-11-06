# arkham-app/src

## Purpose and Scope

The `src` directory is the source code root for the arkham-app frontend module. It contains all application logic, UI components, API integrations, internationalization resources, and type definitions for the Vue 3 + TypeScript card design application. This directory serves as the primary development workspace for frontend functionality.

**Main Responsibilities**:
- Application initialization and bootstrapping
- Routing and page navigation
- Component composition and UI rendering
- Backend API communication
- Multi-language support
- Type safety and code organization

**Role**: Acts as the central hub for all frontend code, organizing functionality into logical subdirectories for maintainability and scalability.

## Structure Overview

```
src/
├── main.ts                  - Application entry point
├── App.vue                  - Root component
├── style.css                - Global styles
├── vite-env.d.ts            - Vite type declarations
├── api/                     - Backend API communication layer
├── assets/                  - Static assets (images, fonts)
├── components/              - Reusable Vue components
├── config/                  - Application configuration
├── locales/                 - Internationalization resources
├── pages/                   - Page-level components
└── types/                   - TypeScript type definitions
```

### Directory Descriptions

- **api/**: API service layer with HTTP client, endpoints, and service modules (workspace, card, TTS export, etc.)
- **assets/**: Static resources including card back images and other visual assets
- **components/**: Reusable UI components (file browser, editors, panels, etc.)
- **config/**: Card type configurations (Chinese/English), TTS script generators
- **locales/**: i18n translation files for Chinese (zh) and English (en)
- **pages/**: Top-level page components (HomePage, WorkspacePage, workspace sub-pages)
- **types/**: Shared TypeScript interfaces and type definitions

## Key Components

### main.ts
- **Description**: Application entry point and initialization
- **Responsibilities**:
  - Create Vue application instance
  - Register global plugins (i18n)
  - Configure context menu behavior
  - Mount application to DOM
- **Key Operations**:
  - Imports global fonts (Lato, FiraCode)
  - Configures right-click menu restrictions (preserves menu for input elements)
  - Initializes i18n for multi-language support

### App.vue
- **Description**: Root application component
- **Responsibilities**:
  - Application-wide configuration provider (Naive UI theme, locale)
  - Page routing between HomePage and WorkspacePage
  - Theme management (light/dark mode)
  - Global message provider
- **Key Features**:
  - Simple client-side routing via `currentPage` state
  - Workspace navigation parameter passing
  - Theme toggle functionality
- **State**:
  - `currentPage`: `'home' | 'workspace'` - Current active page
  - `theme`: `GlobalTheme | null` - Current theme (null = light, darkTheme = dark)
  - `workspaceParams`: Workspace navigation parameters (mode, path, name)

### style.css
- **Description**: Global CSS styles
- **Responsibilities**:
  - Reset default HTML/body styles
  - Prevent page-level scrolling (desktop app behavior)
  - Set global font family

## Dependencies

### Internal Dependencies
- `./api/` - Backend API communication services
- `./components/` - Reusable UI components
- `./config/` - Card type and script configurations
- `./locales/` - Translation resources
- `./pages/` - Page components
- `./types/` - TypeScript type definitions

### External Dependencies
- **vue** (3.5.18) - Core framework
- **naive-ui** (2.42.0) - UI component library (NConfigProvider, NGlobalStyle, NMessageProvider, themes)
- **vfonts** - Font packages (Lato, FiraCode)
- **@vue/compiler-sfc** - Vue single-file component compiler
- **axios** - HTTP client (used in api/)
- **vue-i18n** (9.14.5) - Internationalization plugin
- **date-fns-tz** - Date/timezone utilities
- **uuid** - Unique ID generation

## Integration Points

### Application Bootstrap Flow
```
main.ts (entry)
  ↓
Creates Vue app with App.vue
  ↓
Registers i18n plugin
  ↓
Configures context menu listener
  ↓
Mounts to #app element
```

### Page Navigation Flow
```
App.vue (root)
  ↓
HomePage (currentPage === 'home')
  ↓ navigateToWorkspace event
WorkspacePage (currentPage === 'workspace')
  ↓ navigateToHome event
HomePage
```

### API Communication
All backend communication flows through `./api/` service modules:
- Services import from `./api/index.ts`
- Unified HTTP client with error handling
- Type-safe request/response via TypeScript interfaces

### Theme Management
- App.vue provides theme via NConfigProvider
- Child components receive `is-dark` boolean prop
- Theme toggle propagates from App.vue → pages → components

### Internationalization
- i18n initialized in main.ts
- Locale resources loaded from `./locales/index.ts`
- Components use `$t()` function for translations

## Implementation Notes

### Design Patterns
- **Provider Pattern**: App.vue wraps application with NConfigProvider and NMessageProvider for global configuration
- **Composition API**: All components use Vue 3 `<script setup>` syntax
- **Service Layer**: API communication abstracted into dedicated service modules
- **Module Isolation**: Each subdirectory has its own CLAUDE.md documentation

### Technical Decisions
- **No Router Library**: Simple client-side routing via reactive state instead of Vue Router (reduces complexity for desktop app)
- **Context Menu Control**: Custom right-click prevention for desktop app feel, preserving functionality for input elements
- **Type Safety**: Strict TypeScript configuration ensures compile-time error detection
- **Font Loading**: Global fonts imported in main.ts to ensure availability before DOM rendering

### Configuration
- Vite development server proxy configured in `../vite.config.ts`
- TypeScript configuration in `../tsconfig.json`
- ESLint/Prettier configuration (if added) should reside in parent directory

### Performance Considerations
- **Lazy Loading**: Consider code-splitting for large pages/components (not currently implemented)
- **Virtual Scrolling**: Recommended for large card lists (implementation in components)
- **Asset Optimization**: Vite automatically optimizes assets during build

### Security Considerations
- Context menu disabled globally to prevent unintended actions (desktop app pattern)
- All backend API calls should validate responses and handle errors
- File paths and user input must be sanitized before sending to backend

### Known Limitations
- No browser history support (simple state-based routing)
- No deep linking or URL-based routing
- Context menu prevention may conflict with browser extensions
- Right-click behavior customization requires element-level checks

### Module Documentation
Each subdirectory contains detailed documentation:
- [@api/CLAUDE.md](./api/CLAUDE.md) - API service layer
- [@assets/CLAUDE.md](./assets/CLAUDE.md) - Static assets
- [@components/CLAUDE.md](./components/CLAUDE.md) - UI components
- [@config/CLAUDE.md](./config/CLAUDE.md) - Configuration files
- [@locales/CLAUDE.md](./locales/CLAUDE.md) - i18n resources
- [@pages/CLAUDE.md](./pages/CLAUDE.md) - Page components
- [@types/CLAUDE.md](./types/CLAUDE.md) - Type definitions

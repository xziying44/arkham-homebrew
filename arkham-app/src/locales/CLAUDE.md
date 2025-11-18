# Locales Module

## Purpose and Scope
Provides internationalization (i18n) setup and language resources for the application. This module initializes `vue-i18n` and exposes helper APIs to query and change the active UI language. It aggregates language packs under `en/` and `zh/` and serves as the single entry for all localized strings.

Note: Language persistence is managed by backend configuration, not by this module.

## Structure Overview
- `index.ts` – i18n bootstrapper; creates and exports the `i18n` instance, plus language helpers
- `en/` – English language pack (see `en/CLAUDE.md`)
- `zh/` – Chinese language pack (see `zh/CLAUDE.md`)

Exports from `index.ts`:
- Default export: `i18n` instance configured with messages `{ zh, en }`
- Named exports: `setLanguage(locale: string)`, `getCurrentLanguage(): string`

## Key Components
### i18n Bootstrap (`index.ts`)
- Description: Centralizes i18n configuration using `vue-i18n` with composition API and global injection.
- Responsibilities:
  - Load `en` and `zh` messages and provide them to Vue I18n
  - Initialize with default Chinese locale
  - Expose helpers to switch and query the current language (runtime only, persistence handled by backend)
- Key Methods:
  #### `setLanguage(locale: string): void`
  - Purpose: Switch the active UI language at runtime. Note: Language persistence should be handled via backend configuration service.
  - Parameters:
    • `locale` (string): Target language code. Expected values: `"zh" | "en"`.
  - Returns: `void`.
  - Throws: None expected.
  - Example:
    ```ts
    import { setLanguage } from 'src/locales'
    setLanguage('en')
    ```

  #### `getCurrentLanguage(): string`
  - Purpose: Retrieve the currently active UI language code.
  - Parameters: None.
  - Returns: `(string)` Active locale code (e.g., `"zh"` or `"en"`).
  - Throws: None expected.
  - Example:
    ```ts
    import { getCurrentLanguage } from 'src/locales'
    const lang = getCurrentLanguage()
    ```

- Exported APIs:
  - `default export` – `i18n` (Vue I18n instance)
  - `setLanguage(locale: string): void`
  - `getCurrentLanguage(): string`

## Dependencies
### Internal Dependencies
- `./en` – English language messages (namespaced domain objects)
- `./zh` – Chinese language messages (namespaced domain objects)

### External Dependencies
- `vue-i18n` – Core i18n engine for Vue (composition API, `globalInjection`)

## Integration Points
### Public APIs
- `i18n` – Register with the Vue app; templates and components can use `$t` due to `globalInjection: true`.
- `setLanguage(locale: string)` – Call to change language at runtime (persistence via backend).
- `getCurrentLanguage()` – Read current language for UI or routing decisions.

### Data Flow
- Input → Default locale `'zh'` (backend configuration should update this at app initialization)
- Processing → `createI18n({ locale: 'zh', fallbackLocale: 'zh', messages: { zh, en } })`
- Output → `$t('<domain>.<key>')` resolves to active language; missing keys fall back to `'zh'`

## Implementation Notes
### Design Patterns
- Aggregator: `index.ts` aggregates sub-packs (`en`, `zh`) and exposes a single i18n surface.
- Separation of concerns: Language persistence delegated to backend configuration service.

### Technical Decisions
- `legacy: false` to use composition API; `globalInjection: true` to allow `$t` in templates without per-component setup.
- `fallbackLocale: 'zh'` to ensure stable behavior when a key is missing in the current language.
- Language persistence moved to backend to avoid pywebview port randomization issues with browser storage.

### Considerations
- Performance: Static message objects; negligible runtime overhead.
- Security: No sensitive data stored in this module; persistence handled by backend.
- Limitations: Only `en` and `zh` shipped; additional languages require adding a new folder and wiring it in `index.ts`.

> For detailed keys and domains within each language, see:
> - `en/CLAUDE.md`
> - `zh/CLAUDE.md`

### Updates (Seal script editor keys)
- 新增 `ttsScriptEditor.seal.*` 键域（中/英均已对齐）：
  - `label`, `enable`, `tokens`, `tokensPlaceholder`, `clear`, `all`, `max`, `maxHint`
  - `tokenNames.<Elder Sign|Auto-fail|Skull|Cultist|Tablet|Elder Thing|Bless|Curse|Frost|+1|0|-1...>`
- 用途：TTS 脚本编辑器的“封印脚本”配置 UI（多选可封印 Token、全部 Token 勾选、数量上限与提示）。

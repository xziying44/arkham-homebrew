# content-package.ts

## Purpose and Scope
Defines the core TypeScript types and helper utilities for representing and constructing Content Package data used by the Arkham app. Responsibilities include:
- Standardizing content package metadata, cards, encounter sets, and file structures
- Providing default factory functions to initialize valid package objects
- Providing option lists (with and without localization) for UI selectors
Boundaries: pure data modeling and stateless helpers only; no I/O, persistence, or framework coupling.

## Structure Overview
- Exports: interfaces (`ContentPackageMeta`, `ContentPackageCard`, `EncounterSet`, `ContentPackage`, `ContentPackageFile`, `CreatePackageForm`, `PackageFormRules`), type alias (`PackageType`), factory functions (`createDefaultMeta`, `createDefaultPackage`), option generators (`getPackageTypeOptions`, `getLanguageOptions`, `getStatusOptions`), and static option constants (`PACKAGE_TYPE_OPTIONS`, `LANGUAGE_OPTIONS`, `STATUS_OPTIONS`).
- No imports; self-contained module.
- Grouping: types first, then default factories, then localized generators, then static option lists for backward compatibility.

## Key Components
### Interfaces and Types
- `export interface ContentPackageMeta`
  - Description: Metadata describing a content package (identity, display, status, typing, and dates).
  - Fields: `code: string`, `name: string`, `description: string`, `author: string`, `language: 'zh' | 'en'`, `banner_url: string`, `types: PackageType[]`, `status: 'draft' | 'alpha' | 'beta' | 'complete' | 'final'`, `date_updated: string`, `generator: string`, `external_link?: string`.

- `export interface ContentPackageCard`
  - Description: File and display data for a single card in a package.
  - Fields: `filename: string`, `version?: string`, `front_url?: string`, `back_url?: string`, `original_front_url?: string`, `original_back_url?: string`, `front_thumbnail_url?: string`, `back_thumbnail_url?: string`, `permanent?: boolean`, `exceptional?: boolean`, `myriad?: boolean`, `exile?: boolean`.

- `export interface EncounterSet`
  - Description: Metadata and asset references for an encounter set.
  - Fields: `code: string`, `name: string`, `icon_url?: string`, `base64?: string`, `relative_path?: string`, `order?: number`.

- `export interface ContentPackage`
  - Description: Full content package payload combining metadata, banner, cards, and encounter sets.
  - Fields: `meta: ContentPackageMeta`, `banner_base64: string`, `cards?: ContentPackageCard[]`, `encounter_sets?: EncounterSet[]`.

- `export type PackageType = 'investigators' | 'player_cards' | 'campaign'`
  - Description: Allowed content package categories.

- `export interface ContentPackageFile`
  - Description: File-oriented view of a content package bundling resolved meta and assets.
  - Fields: `name: string`, `path: string`, `meta: ContentPackageMeta`, `banner_base64: string`, `cards?: ContentPackageCard[]`, `encounter_sets?: EncounterSet[]`.

- `export interface CreatePackageForm`
  - Description: Form model for creating a new content package.
  - Fields: `name: string`, `description: string`, `author: string`, `language: 'zh' | 'en'`, `types: PackageType[]`, `external_link: string`, `banner_url: string`, `banner_base64: string`.

- `export interface PackageFormRules`
  - Description: Validation rule keys for the create/edit package form.
  - Fields: `name: string`, `description: string`, `author: string`, `language: string`, `types: string`.

### Factory Functions
#### `createDefaultMeta(): ContentPackageMeta`
- Purpose: Produce a default-initialized metadata object for new content packages.
- Parameters: none
- Returns: (ContentPackageMeta) Defaults include `language: 'zh'`, `status: 'final'`, `date_updated: new Date().toISOString()`, `generator: 'Arkham Card Maker 3.9'`.
- Throws: none

#### `createDefaultPackage(): ContentPackage`
- Purpose: Produce a default-initialized content package with empty collections.
- Parameters: none
- Returns: (ContentPackage) `{ meta: createDefaultMeta(), banner_base64: '', cards: [], encounter_sets: [] }`.
- Throws: none

### Option Generators (Localized)
All accept a translation function to localize labels without hard-coding a specific i18n library.

#### `getPackageTypeOptions(t: (key: string) => string): { label: string; value: PackageType }[]`
- Purpose: Build localized select options for `PackageType`.
- Parameters:
  • `t ((key: string) => string)`: Translation function applied to well-known i18n keys.
- Returns: (Array) List of `{ label, value }` for `investigators`, `player_cards`, `campaign`.
- Throws: none
- Example:
  ```ts
  const opts = getPackageTypeOptions(t);
  // [{ label: '…Investigators', value: 'investigators' }, …]
  ```

#### `getLanguageOptions(t: (key: string) => string): { label: string; value: 'zh' | 'en' }[]`
- Purpose: Build localized language options.
- Parameters:
  • `t ((key: string) => string)`: Translation function.
- Returns: (Array) Options for `'zh'` and `'en'`.
- Throws: none

#### `getStatusOptions(t: (key: string) => string): { label: string; value: 'draft' | 'alpha' | 'beta' | 'complete' | 'final' }[]`
- Purpose: Build localized status options.
- Parameters:
  • `t ((key: string) => string)`: Translation function.
- Returns: (Array) Options for `'draft' | 'alpha' | 'beta' | 'complete' | 'final'`.
- Throws: none

### Static Option Constants (Backward Compatibility)
- `PACKAGE_TYPE_OPTIONS: { label: string; value: PackageType }[]`
  - Purpose: Pre-localized (Chinese) package type options.
- `LANGUAGE_OPTIONS: { label: string; value: 'zh' | 'en' }[]`
  - Purpose: Pre-localized (Chinese) language options.
- `STATUS_OPTIONS: { label: string; value: 'draft' | 'alpha' | 'beta' | 'complete' | 'final' }[]`
  - Purpose: Pre-localized (Chinese) status options.

## Dependencies
### Internal Dependencies
- Type cross-references within this file only (e.g., `ContentPackage` uses `ContentPackageMeta`, `ContentPackageCard`, `EncounterSet`).

### External Dependencies
- None. Translation is injected via the `t` function parameter.

## Integration Points
### Public APIs
- `createDefaultMeta(): ContentPackageMeta` – Default metadata factory
- `createDefaultPackage(): ContentPackage` – Default package factory
- `getPackageTypeOptions(t): {label: string; value: PackageType}[]` – Localized options
- `getLanguageOptions(t): {label: string; value: 'zh' | 'en'}[]` – Localized options
- `getStatusOptions(t): {label: string; value: 'draft' | 'alpha' | 'beta' | 'complete' | 'final'}[]` – Localized options
- `PACKAGE_TYPE_OPTIONS` / `LANGUAGE_OPTIONS` / `STATUS_OPTIONS` – Static Chinese options

### Data Flow
- Input: UI or tooling calls default factories to initialize form state, then uses option generators to populate selectors.
- Processing: Callers modify `ContentPackageMeta` and assemble `ContentPackage` with cards and encounter sets.
- Output: Completed `ContentPackage` objects ready for serialization, validation, or export.

## Implementation Notes
### Design Patterns
- Factory: `createDefaultMeta` and `createDefaultPackage` centralize default initialization.
- Function Injection: Option generators accept `t` to keep localization decoupled from this module.

### Technical Decisions
- Default `status` is `'final'` and `language` is `'zh'` to match project conventions.
- `date_updated` uses `toISOString()` at call-time to ensure standardized timestamps.
- Static Chinese option arrays remain for backward compatibility alongside localized generators.

### Considerations
- Performance: Pure object creation; negligible overhead.
- Security: No I/O or external calls; ensure any `base64` content is sanitized by consumers if rendered.
- Limitations: Uniqueness of `meta.code` is not enforced here; callers must manage IDs. Time defaults are dynamic per invocation.


# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.0] - 2025-11-24

### Added
- **Rich Text Editor**: Added `BodyRichTextEditor` with support for paragraphs, non-breaking spaces (nbsp), and keyword tags.
- **UI Components**: Added special UI components with color adaptation; introduced editor grouping; replaced the numeric click component with a dial interface.
- **Card Configuration**: Added individual bottom icon configuration; Investigator card bottom info supports Full Art mode; added a new back name tag; bottom illustration info now supports Chinese characters.
- **Editor UX**: The editor remembers the selected tab when switching; export parameters are now saved.

### Improved
- **Full Art Cards**: Reduced the glow range and optimized script support.
- **Visual Polish**: Optimized fonts for Chinese bottom info; adjusted component order for Asset card values; fixed element offset issues.
- **Workflow & Performance**: Card images are no longer generated automatically on save to improve speed; optimized navigation position after uploads.

### Fixed
- **Editor**: Fixed jumping in editor groups; fixed a crash when calling `getFieldValue` on the mini-card back editor; fixed an issue where font size tags did not recognize negative numbers.
- **System Stability**: Implemented strong data isolation for saved card files to prevent corruption; fixed a persistence issue when reference IDs were empty during script generation; fixed the upload button getting stuck after a failure; added missing localization strings.

## [3.3.0] - 2025-11-17

### Added
- **Unofficial Large Art Card Templates**: Added three new unofficial large art card templates (Asset, Event, and Skill cards)
- **Linux Platform Support**: Official support for Linux distributions

### Changed
- Updated Rule Reference Mini Card type

## [3.2.1] - 2025-11-15

### Added
- **Custom Card Language Configuration**: Added support for custom card language configuration

### Changed
- **Deck Builder Feature Removed**: The deck builder feature has been officially deprecated. Users are advised to use the new Content Package module for related operations

### Improved
- **TTS Export Optimization**: Optimized card names and type tags when exporting to Tabletop Simulator (TTS)
- **File Size Limit Removed**: Removed file size restrictions when scanning card types
- **Visual Alignment**: Improved icon centering alignment on Location cards

### Fixed
- **TTS Export Fix**: Fixed incorrect tags when exporting Enemy and Treachery cards to TTS
- **Icon Misalignment**: Fixed bleed and misalignment issues with the "Commit" icon on Event cards
- **Text Tag Conflict**: Fixed conflict between `<size>` tag and `<font>` tag in text styles

---

## Version Notes

- **Major version (X.0.0)**: Incompatible API changes
- **Minor version (0.X.0)**: Backwards-compatible new features
- **Patch version (0.0.X)**: Backwards-compatible bug fixes

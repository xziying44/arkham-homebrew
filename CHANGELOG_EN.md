# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

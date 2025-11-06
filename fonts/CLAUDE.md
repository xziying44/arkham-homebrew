# Fonts Module

## Purpose

Provide multilingual typography assets and configuration for the Arkham JSON DIY card-generation system. This module centralizes font files and language-specific mappings for all text elements (titles, body, traits, etc.) and maintains bilingual template filename translations.

## Structure

- Font assets: `.ttf` and `.otf` files for English, Chinese, and Polish.
- Config: `language_config.json` for per-language font assignments and localized labels.
- Mappings: `filename_translation_mapping.json` for Chinese → English template filenames.
- Categories: Title, Subtitle, Card Type, Trait, Bold, Body, Flavor, Collection Info.

## Components

- Font assets
  - English
    - `Arkhamic.ttf`: Decorative title face
    - ArnoPro family: `ArnoPro-Regular.ttf` (body), `ArnoPro-Bold.ttf` (bold), `ArnoPro-Italic.ttf` (flavor), `ArnoPro-Smbd.ttf` (subtitle), `ArnoPro-BoldDisplay.otf` (card type), `ArnoPro-BoldItalic.otf` (trait)
    - NimbusRomNo9L family (primarily for Polish): `NimbusRomNo9L-Reg.ttf`, `NimbusRomNo9L-RegIta.ttf`, `NimbusRomNo9L-Med.ttf`, `NimbusRomNo9L-MedIta.ttf`
  - Chinese
    - `SourceHanSansSC-Regular.otf` (思源黑体) for bold
    - `founder-shuti.ttf` (方正舒体) for trait
    - System faces by name: `simfang` (body), `simfang-Italic` (flavor)
  - Special
    - `arkham-icons.ttf`: Iconography
    - `BODONI-ORNAMENTS.TTF`, `Bolton.ttf`: Decorative

- Configuration: `language_config.json`
  - Languages: zh, zh-CHT, en, pl
  - Schema
    - `fonts.<category>`: `{ name, size_percent, vertical_offset }`
      - `size_percent` ∈ [0.88, 1.0] typical
      - `vertical_offset` in px (0–9)
    - `texts`: localized card-type labels and UI strings
  - Font categories
    - `title`, `subtitle`, `card_type`, `trait`, `bold`, `body`, `flavor`, `collection_info`

- Filename mapping: `filename_translation_mapping.json`
  - Maps Chinese template filenames to English (e.g., `事件卡-守护者.png` → `event-card-guardian.png`)
  - Coverage
    - Event/Skill/Asset cards by class and level
    - Location (revealed/unrevealed, ±subtitle)
    - Scenario/Agenda/Act (front/back/mirror)
    - Weakness variants and UI elements
    - Bled/bleed versions for each template

## Dependencies

- Downstream modules load fonts defined here to render text and resolve template paths.
- Typical external: Pillow (`PIL.ImageFont.truetype`) or equivalent font loader.
- File-system access to `fonts/` directory for asset paths.

## Integration

- Font selection
  - Read `language_config.json`, choose `fonts[category]` for the current `language.code`.
  - Resolve `name` to a file in `fonts/` (e.g., `ArnoPro-Regular.ttf`) or system face (`simfang`).
  - Apply `size_percent` and `vertical_offset` during layout.

- Filename translation
  - Look up Chinese template filename in `filename_translation_mapping.json.images` to obtain the canonical English asset path.

- Typical flow
  1) Select language (zh/zh-CHT/en/pl)
  2) Load per-category font config
  3) Render text with configured face/scale/offset
  4) Resolve template filenames via mapping

## Notes

- Performance: Large CJK fonts (e.g., `SourceHanSansSC-Regular.otf` ~16.4 MB) may affect startup and memory.
- Licensing: Verify distribution/commercial terms for bundled fonts.
- Coverage: Ensure glyph/symbol support across languages; `arkham-icons.ttf` supplies game symbols.
- System fonts: Some names (e.g., `simfang`) rely on OS-installed faces.
- Limitations: Manual `vertical_offset` tuning; assets limited to what ships in `fonts/`.

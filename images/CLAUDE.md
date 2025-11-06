[根目录](../CLAUDE.md) > **images**

## Purpose
- Central repository of all card template images and visual assets for the Arkham JSON DIY card-generation system.
- Provides 305+ PNG templates covering card types, classes, levels, subtitle variants, and print-ready bleed versions.
- Enables deterministic, programmatic template selection via strict filename conventions.

## Structure
- Flat directory of `.png` assets, organized by naming conventions rather than subfolders.
- Major categories:
  - Player cards: `asset-`, `event-`, `skill-`, `weakness-`
  - Investigator: `investigator-*`
  - Location: `location-*` (revealed/unrevealed, connection, shroud)
  - Scenario/Campaign: `scenario-*`, `agenda-*`, `act-*`
  - Enemy/Encounter: `enemy-*`, `encounter-*`
  - Bleed (print-ready): `bled-*` (mirrors base templates)
  - UI and icons: `UI-*`, `commit-*`, `slot-*`, `custom-*`, `multiclass-*`
  - Misc: `upgrade-card-*.png`, `action-card-*.png`, `adventure-card-*.png`
- Naming patterns:
  - Base: `{type}-card-{class|variant}.png`
  - Subtitle: `{type}-card-{class}-subtitle.png`
  - Level: `{type}-card-level-{N}.png`
  - Bleed: `bled-{original-name}.png`

## Components
- Player card templates
  - Asset: class-specific (`asset-card-guardian.png` …), levels (`asset-card-level-1..5.png`), multiclass/subtitle variants, encounter variant.
  - Event: class-specific, levels (`event-card-level-1..5.png`), no-level, multiclass.
  - Skill: class-specific, subtitle variants, multiclass.
  - Weakness: asset/skill/event/treachery/enemy with `*-subtitle` forms.
- Investigator templates
  - Front/back/parallel/mini; stat and skill overlays in large/medium/small.
- Location templates
  - Revealed/unrevealed (±subtitle); `location-connection-*`, `location-shroud-*`.
- Scenario/Campaign templates
  - Scenario, Agenda, Act; front/back/mirror/large where applicable.
- Enemy & Encounter templates
  - Enemy (elite, subtitle, health-size variants); encounter front/back.
- Bleed templates (`bled-*`)
  - Print-ready equivalents for major types, including weakness and location.
- UI elements & icons
  - `UI-damage.png`, `UI-horror.png`, `UI-health-horror.png`
  - Commit icons: `commit-*` (skill combinations)
  - Slot icons: `slot-*` (hand, body, accessory, arcane, ally, tarot, …)
- Additional
  - `multiclass-*` banners, `upgrade-card-*.png`, `action-card[-small|-medium].png`, `adventure-card*.png`

## Dependencies
- Internal
  - Used by: `Card.py` (base layers), `create_card.py` (template selection), `ArkhamCardBuilder.py` (composite assembly)
  - Referenced by: `fonts/filename_translation_mapping.json` (zh→en filename mapping)
- External
  - Pillow (`PIL.Image.open`) to load templates
  - File-system access to `images/` path

## Integration
- Template selection (example):
  ```python
  name = f"{card_type}-card-{class_name}.png"
  if has_subtitle:
      name = f"{card_type}-card-{class_name}-subtitle.png"
  if level and level > 0:
      name = f"{card_type}-card-level-{level}.png"
  if print_bleed:
      name = f"bled-{name}"

  path = f"images/{name}"
  image = Image.open(path)
  ```
- Conventions
  - Base: `{type}-card-{variant}.png`; Class: `{type}-card-{class}.png`
  - Subtitle: `{type}-card-{class}-subtitle.png`; Level: `{type}-card-level-{N}.png`
  - Bleed: `bled-{original-name}.png`; UI: `{category}-{name}.png`
- Data flow
  1) Card config → 2) Filename resolution → 3) Load template → 4) Layer composition → 5) Export

## Notes
- Format: PNG for lossless quality and alpha; standardized dimensions (standard ~750×1050; mini variants; bleed adds margins).
- Organization: Flat directory relies on strict naming for deterministic lookup.
- Performance: 300+ images benefit from caching; consider memory usage for concurrent loads.
- Limitations: No vector/SVG; fixed dimensions; manual bleed assets; no built-in versioning.
- Compatibility: 未发现子目录 `CLAUDE.md`，当前文档为本目录单层聚合（来源：本目录文件与项目代码约定）。
- **Scenario/Agenda/Act**: 12 files total (3 types × 4 variations)
- **Custom designs**: 12 files
- **UI elements**: 3 files

### Template Resolution Examples
```
Card Type: Asset, Class: Guardian, Level: 0, No Subtitle
→ images/asset-card-guardian.png

Card Type: Asset, Class: Guardian, Level: 0, With Subtitle
→ images/asset-card-guardian-subtitle.png

Card Type: Event, Class: Seeker, Level: 3
→ images/event-card-level-3.png

Card Type: Weakness, Type: Treachery, With Subtitle
→ images/weakness-treachery-card-subtitle.png

Card Type: Location, Revealed: True, No Subtitle
→ images/location-card-revealed.png

Print Mode: Bleed, Card Type: Skill, Class: Mystic
→ images/bled-skill-card-mystic.png
```

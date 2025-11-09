# Purpose

This directory provides self‑contained Tabletop Simulator (TTS) object templates used to seed Arkham Horror LCG card content and a display/storage container. Each JSON file conforms to TTS’ saved object schema and is intended to be filled with project‑specific assets (card faces/backs, nicknames, etc.) by tools or manual editing.

# Structure

- `General.json` — Baseline upright card template (`CardCustom`) with a hidden back; suitable for most standard cards.
- `Act.json` — Sideways card variant (`CardCustom`) tuned for act/agenda style layouts.
- `Investigator.json` — Sideways card variant (`CardCustom`) with enlarged X/Z scale for investigator boards.
- `Box.json` — A container save with a single `Custom_Model_Bag` mesh to hold or display generated cards.

# Components

Shared card fields (present in `General.json`, `Act.json`, `Investigator.json`):

- `Name: "CardCustom"` — TTS custom card object type.
- `Transform` — Default placement/orientation. All cards ship with `rotY: 270.0` to align with the table coordinate system; adjust as needed.
- `Nickname`, `Description`, `GMNotes` — Metadata placeholders.
- `HideWhenFaceDown` — Controls whether face‑down cards are hidden in the fog of war; `true` in `General.json`, `false` in the sideways variants.
- `Hands` — Whether the object can go to player hands; `true` for card templates.
- `SidewaysCard` — Orientation flag; `true` for `Act.json` and `Investigator.json`, `false` for `General.json`.
- `CardID` — Deck/card identifier (default `100`). Keep consistent with TTS deck conventions when batching cards.
- `CustomDeck` — Deck image sources under a numeric key (here `"1"`):
  - `FaceURL` and `BackURL` — Image URLs for card face/back (empty by default; supply hosted images).
  - `NumWidth`, `NumHeight` — Grid dimensions (1×1 for single card sheets).
  - `BackIsHidden` — Back visibility (`true` in all templates).
  - `UniqueBack` — Whether each card has a unique back (`false` in `General.json`, `true` in sideways variants).
- `LuaScript`, `LuaScriptState`, `XmlUI` — Integration hooks left empty for project scripts/UI.

Side‑specific adjustments:

- `Act.json`
  - `SidewaysCard: true`
  - `HideWhenFaceDown: false`
  - `Transform.scaleX/scaleY/scaleZ: 1.0` (square card footprint)

- `Investigator.json`
  - `SidewaysCard: true`
  - `HideWhenFaceDown: false`
  - `Transform.scaleX: 1.15`, `scaleZ: 1.15` (wider board footprint)

Container template (`Box.json`):

- Top‑level save fields (`SaveName`, `VersionNumber`, etc.) align with TTS save schema.
- `ObjectStates[0]` — One `Custom_Model_Bag` object with:
  - `Transform.scaleY: 0.14` for a low‑profile box.
  - `CustomMesh.MeshURL` and `DiffuseURL` — Remote mesh and texture used by the bag.
  - `ContainedObjects: []` — Empty by default; populate with generated card objects when assembling a full save.
  - `Description` includes Chinese text (用于说明来源) and is safe to localize.

# Dependencies

- Tabletop Simulator saved object JSON schema (object types: `CardCustom`, `Custom_Model_Bag`).
- Hosted assets for images/meshes:
  - Card `FaceURL`/`BackURL` (HTTP(S) accessible, recommended stable hosting).
  - Bag `CustomMesh.MeshURL`/`DiffuseURL` (as provided, may be Steam CDN links).
- Editing environment capable of UTF‑8 (for non‑ASCII metadata such as Chinese in `Box.json`).

# Integration

Using the card templates (`General.json`, `Act.json`, `Investigator.json`):

- Duplicate the appropriate template per card to generate and set:
  - `CustomDeck["1"].FaceURL` to the card face image URL.
  - `CustomDeck["1"].BackURL` to the card back image URL.
  - `Nickname`, `Description`, and any `Tags` your workflow uses.
- Choose orientation/scale by template:
  - Standard upright cards → `General.json`.
  - Sideways cards (acts/agendas) → `Act.json`.
  - Investigator boards (wider) → `Investigator.json`.
- If assembling into a single TTS save, add each card object to `Box.json`’s `ContainedObjects` or merge into a larger `ObjectStates` array as needed by your build process.

Using the container (`Box.json`):

- Keep the provided `CustomMesh` URLs unless you have a project‑specific container.
- Populate `ContainedObjects` with fully specified card objects to ship a ready‑to‑load save.

# Notes

- Keep `CardID` values consistent with TTS deck conventions when batching cards within a `CustomDeck`.
- `UniqueBack` should be `true` if each card uses a distinct back image; otherwise `false` allows a shared back sheet.
- Orientation is controlled both by `SidewaysCard` and the `Transform.rot*` values; adjust only one axis at a time to avoid unintended rotations.
- Ensure all remote asset URLs are publicly reachable by TTS; prefer HTTPS.
- For localized metadata (e.g., Chinese), save files as UTF‑8 to avoid mojibake across platforms.

## Lua Script Templates (backend‑driven)

This repository also ships Lua script templates consumed by the backend TTS script generator to produce per‑card scripts:

- `phase_buttons.lua` — Investigator phase‑button helper
  - Placeholders:
    - `-- BUTTON_PARAMS_PLACEHOLDER --` → injected with `buttonParams` (labels/ids/colors)
    - `<!-- BUTTON_ID_INDEX_PLACEHOLDER -->` → `buttonIdToIndex` mapping
    - `<!-- BUTTON_COUNT -->` → number of buttons
  - Bundled modules included in‑template (via `__bundle_register`): `playercards/CardsWithHelper`, `playercards/CardsWithPhaseButtons`, `util/SideButtonCreator`

- `upgrade_sheet.lua` — Customizable upgrade sheet (Power Word)
  - Placeholders (front‑end syntax mirrored):
    - `${xInitial.toFixed(4)}`
    - `${xOffset.toFixed(4)}`
    - `${customizations}`
  - Bundled modules included in‑template: `core/GUIDReferenceApi`, `playermat/PlayermatApi`, `util/MathLib`, `util/SearchLib`
  - The backend computes layout params from pixel coordinates (group by row/Y; derive scales/offsets; emit `customizations` table) to ensure parity with the front‑end generator.

Consumption
- The backend module `bin/tts_script_generator.py` loads these Lua templates and performs placeholder substitution to produce final scripts for TTS objects.
- Prefer updating templates here rather than embedding large Lua strings in Python to keep maintenance simpler and front/back parity intact.

## Purpose

Provides rich text rendering for Arkham Horror DIY cards, turning HTML‑like annotated text into positioned draw operations on a PIL image. It parses tags, lays out text and inline images within polygonal regions, and renders with font stacks, alignment, and spacing rules tailored for Chinese/English mixed text.

## Structure

- `__init__.py` – Package metadata and public exports (`RichTextParser`, `RichTextRenderer`, `VirtualTextBox`).
- `HtmlTextParser.py` – HTML‑like tokenizer/parser producing `ParsedItem`s with fine‑grained text typing.
- `VirtualTextBox.py` – Polygonal layout engine that arranges `TextObject`/`ImageObject` rows with wrapping, spacing, centering, guide lines, and flex gaps.
- `RichTextRenderer.py` – High‑level renderer: preprocessing (emoji/alias → icon font), parsing, layout orchestration, and drawing to a `PIL.Image`.

## Components

- Parser (`HtmlTextParser.py`)
  - `TextType` enum: `ENGLISH`, `NUMBER`, `PUNCTUATION`, `SPACE`, `OTHER`, `HTML_START`, `HTML_END`, `HTML_SELF_CLOSE`, `ENGLISH_BLOCK`.
  - `ParsedItem`: tag + type + attributes + content.
  - `RichTextParser`:
    - Tag handling: supports `b`, `i`, `u`, `p`, `font`, `trait`, `flavor`, `em`, `br`, `hr`, `par`, `flex`, `nbsp`, `center`, `img`.
    - Attribute parsing (`name="value" | 'value' | value`).
    - Text splitting: per‑char classification in zh modes; compact block splitting for en modes; handles `&nbsp;`, hyphenated ranges, apostrophes, and newlines → `br`.
    - Balanced tag scanning with nested matching.

- Layout (`VirtualTextBox.py`)
  - Data objects: `TextObject`, `ImageObject`, `FlexObject`, `RenderItem`.
  - `VirtualTextBox` core:
    - Polygonal line bounds sampling; padding; paragraph spacing; line padding.
    - Wrapping rules for punctuation: `cannot_be_line_start` / `cannot_be_line_end`.
    - Line‑level behaviors: `set_line_center`/`cancel_line_center`, guide lines (`set_guide_lines`/`cancel_guide_lines`/`get_guide_line_segments`).
    - Flow control: `newline`, `new_paragraph`, `add_flex`, `get_render_list`, `get_remaining_vertical_distance`.

- Rendering (`RichTextRenderer.py`)
  - Config: `DefaultFonts`, `TextAlignment`, `DrawOptions`.
    - `DrawOptions` 新增 `opacity` (0~100) 与 `effects: list[dict]`，例如 `{"type":"shadow","size":8,"spread":20,"opacity":60,"color":(0,0,0)}`。
  - Helpers: `FontStack`, `HtmlTagStack`, `FontCache`, `ImageTag` (inline image sizing by width/height or by current font size).
  - Preprocessing: merges adjacent `<flavor ...>` blocks; maps emojis/aliases (e.g., factions, stats, chaos tokens) → `<font name="arkham-icons">{char}</font>`.
  - Public API:
    - `find_best_fit_font_size(text, polygon_vertices, padding, options)` → `VirtualTextBox` sized via binary search.
    - `draw_complex_text(text, polygon_vertices, padding, options[, draw_debug_frame])` → draws layout, guide lines, `<hr>` lines, and returns `RenderItem[]`.
    - `draw_line(text, position, alignment, options[, vertical])` → single-line horizontal/vertical typesetting, with optional underline/border effect.

## Dependencies

- Runtime
  - `Pillow` (`PIL.Image`, `PIL.ImageDraw`, `PIL.ImageFont.FreeTypeFont`).
  - `ResourceManager` (external module expected by project): `FontManager`, `ImageManager` with APIs:
    - `FontManager.get_font(name, size)` and `get_lang_font(label).name` (e.g., `'正文字体'`, `'加粗字体'`, `'风味文本字体'`, `'特性字体'`).
    - `ImageManager.get_image_by_src(src)` for `<img src="...">`.
- Standard library: `re`, `sys`, `dataclasses`, `enum`, `typing`, `unicodedata`.

## Integration

- Typical pipeline
  1. Create `PIL.Image` drawing surface.
  2. Provide `FontManager` and `ImageManager` (project‑specific implementation).
  3. Construct `RichTextRenderer(font_manager, image_manager, image, lang='zh'|'en')`.
  4. Choose an area (`polygon_vertices`) and `DrawOptions` (base font and color).
  5. Call `draw_complex_text` for multi‑paragraph HTML‑like content, or `draw_line` for one line.

- Minimal example
  - Initialize:
    - `renderer = RichTextRenderer(font_manager, image_manager, image, lang='zh')`
  - Block render:
    - `renderer.draw_complex_text(body_html, polygon_vertices=[(x1,y1),...], padding=10, options=DrawOptions(font_name='simfang', font_size=34, font_color='#000'))`
  - Single line:
    - `renderer.draw_line('标题', position=(cx, cy), alignment=TextAlignment.CENTER, options=DrawOptions(font_name='汉仪小隶书简', font_size=48))`

- Text features
  - HTML‑like tags: `<b>`, `<i>`, `<trait>`, `<font name size color offset>`, `<par>`, `<br>`, `<hr>`, `<flex>`, `<img src width height offset>`.
  - Flavor blocks: `<flavor [align=center padding=15 guide]>…</flavor>` apply italic, optional centering, padding, and guide lines; adjacent equal‑attribute blocks are merged.
  - Icons: emojis/aliases map to `arkham-icons` glyphs; ensure that font is available via `FontManager`.

## Notes

- Language: `lang='zh'` increases line spacing slightly (1.2 vs 1.1) and adjusts underline offsets; non‑zh uses simpler word‑block parsing for layout.
- Fonts: default families are resolved by `FontManager.get_lang_font` labels; ensure your font registry provides names for regular/bold/italic/trait and `arkham-icons`.
- Images: `<img>` scales by explicit `width`/`height` or current font size if omitted; supports `offset` for vertical alignment.
- Layout: polygon sampling picks conservative line bounds; `line_padding` can narrow per‑flavor lines; punctuation wrap rules avoid orphans.
- Rendering: `DrawOptions` supports border (stroke) and underline; vertical single-line mode is available in `draw_line`.
- 文本落笔通过 `enhanced_draw.EnhancedDraw` 统一完成，若 `options.effects` 或 `options.has_border` 设置了描边/阴影/发光，会按队列叠加；`options.opacity` 允许单行/块文字调节透明度。
- External modules: `ResourceManager` is assumed to be available on `PYTHONPATH`; this package does not ship it.
- No child `CLAUDE.md` files were detected; this document reflects the current code’s behavior and exported interfaces.


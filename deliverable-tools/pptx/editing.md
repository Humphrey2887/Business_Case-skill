# Editing Presentations

## Template-Based Workflow

When using an existing presentation as a template:

1. **Analyze existing slides**:
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
   Review `thumbnails.jpg` to see layouts, and markitdown output to see placeholder text.

2. **Plan slide mapping**: For each content section, choose a template slide.

   ⚠️ **USE VARIED LAYOUTS** — monotonous presentations are a common failure mode. Don't default to basic title + bullet slides. Actively seek out:
   - Multi-column layouts (2-column, 3-column)
   - Image + text combinations
   - Full-bleed images with text overlay
   - Quote or callout slides
   - Section dividers
   - Stat/number callouts
   - Icon grids or icon + text rows

   **Avoid:** Repeating the same text-heavy layout for every slide.

   Match content type to layout style (e.g., key points → bullet slide, team info → multi-column, testimonials → quote slide).

3. **Unpack**: `python scripts/office/unpack.py template.pptx unpacked/`

<!-- @AI_GENERATED -->
3a. **读取模板具名节（unpack 后强制第一步）**: unpack 之后，必须先读取 `ppt/presentation.xml` 中 `<p:extLst>` → `<p:ext uri="{521415D9-...}">` 内的 `<p14:sectionLst>`，解析出 `cover` / `content` / `ending` 三个具名节及其归组的 `<p14:sldId>`。可用 `section_style_binder.parse_sections(presentation_xml_path)` 完成解析。任何编辑动作之前必须先拿到这份具名节清单，作为角色绑定的样式来源依据（缺 cover/content 节即抛 `SectionStructureError`，须先重构母版）。

   > **硬规则 — 位置法角色识别（Positional Law）**: 首页 = `cover`，中间各页 = `content`，末页 = `ending` 或 `content`。
   >
   > **硬规则 — 固定映射（Fixed Mapping）**: `cover → cover` / `content → content` / `ending → ending`，不随临场判断变化。
   >
   > **硬规则 — ending 默认不启用**: `ending` 节为可选，ending 默认不启用，仅在被显式请求时才生成末页并绑定 ending 节样式；未请求时末页判为 `content`。
<!-- @AI_GENERATED: end -->

4. **Build presentation** (do this yourself, not with subagents):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides you want to reuse (`add_slide.py`)
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before step 5**

5. **Edit content**: Update text in each `slide{N}.xml`.
   **Use subagents here if available** — slides are separate XML files, so subagents can edit in parallel.

<!-- @AI_GENERATED -->
   **编辑阶段绑定（按角色 → 节，强制）**: 编辑每一页时，先按位置法角色识别判定该页角色（首=cover / 中=content / 末=ending 或 content），再按固定映射（cover→cover / content→content / ending→ending）确定性绑定到对应具名节的版式/样式。可用 `section_style_binder.bind_pages(sequence, sections, ending_requested)` 执行角色识别 + 固定映射绑定。所有 `content` 页统一指向同一个 content 节样式来源，保证同类页样式一致。ending 默认不启用（`ending_requested=False`），仅在被显式请求时才生成末页并绑定 ending 节。
<!-- @AI_GENERATED: end -->

6. **Clean**: `python scripts/clean.py unpacked/`

<!-- @AI_GENERATED -->
6a. **Pre-Delivery Gate（pack 之前强制门槛）**: 在运行 `pack.py` 之前，必须先通过 Pre-Delivery Gate。运行 `python scripts/pre_delivery_gate.py`（即 `pre_delivery_gate.run_gate(bound_pages, deck_text, value_tree_model)`），其聚合三项校验：
   - **G1 追溯校验（Traceability_Check）**: 逐页判定 `Style_Source` 是否等于该页角色对应的期望具名节；任一页错配即失败。
   - **G2 残留占位符门槛（Placeholder_Grep_Gate）**: grep 检查残留占位符文字（如 `xxxx` / `lorem` / `ipsum` / `Cover Page Style`）；命中任一即失败。
   - **G3 价值树节点化校验（Value-Tree Node-ization Check）**: 校验等式逐项独立直角框、单父树、保留运算符与父子关系；不满足即失败。

   任一门槛失败即阻断出片（非零退出并列出问题页），不得声明出片成功；通过后方可运行 `pack.py --original`。
<!-- @AI_GENERATED: end -->

7. **Pack**: `python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `unpack.py` | Extract and pretty-print PPTX |
| `add_slide.py` | Duplicate slide or create from layout |
| `clean.py` | Remove orphaned files |
| `pack.py` | Repack with validation |
| `thumbnail.py` | Create visual grid of slides |

### unpack.py

```bash
python scripts/office/unpack.py input.pptx unpacked/
```

Extracts PPTX, pretty-prints XML, escapes smart quotes.

### add_slide.py

```bash
python scripts/add_slide.py unpacked/ slide2.xml      # Duplicate slide
python scripts/add_slide.py unpacked/ slideLayout2.xml # From layout
```

Prints `<p:sldId>` to add to `<p:sldIdLst>` at desired position.

### clean.py

```bash
python scripts/clean.py unpacked/
```

Removes slides not in `<p:sldIdLst>`, unreferenced media, orphaned rels.

### pack.py

```bash
python scripts/office/pack.py unpacked/ output.pptx --original input.pptx
```

Validates, repairs, condenses XML, re-encodes smart quotes.

### thumbnail.py

```bash
python scripts/thumbnail.py input.pptx [output_prefix] [--cols N]
```

Creates `thumbnails.jpg` with slide filenames as labels. Default 3 columns, max 12 per grid.

**Use for template analysis only** (choosing layouts). For visual QA, use `soffice` + `pdftoppm` to create full-resolution individual slide images—see SKILL.md.

---

## Slide Operations

Slide order is in `ppt/presentation.xml` → `<p:sldIdLst>`.

**Reorder**: Rearrange `<p:sldId>` elements.

**Delete**: Remove `<p:sldId>`, then run `clean.py`.

**Add**: Use `add_slide.py`. Never manually copy slide files—the script handles notes references, Content_Types.xml, and relationship IDs that manual copying misses.

---

## Editing Content

**Subagents:** If available, use them here (after completing step 4). Each slide is a separate XML file, so subagents can edit in parallel. In your prompt to subagents, include:
- The slide file path(s) to edit
- **"Use the Edit tool for all changes"**
- The formatting rules and common pitfalls below

For each slide:
1. Read the slide's XML
2. Identify ALL placeholder content—text, images, charts, icons, captions
3. Replace each placeholder with final content

**Use the Edit tool, not sed or Python scripts.** The Edit tool forces specificity about what to replace and where, yielding better reliability.

### Formatting Rules

- **Bold all headers, subheadings, and inline labels**: Use `b="1"` on `<a:rPr>`. This includes:
  - Slide titles
  - Section headers within a slide
  - Inline labels like (e.g.: "Status:", "Description:") at the start of a line
- **Never use unicode bullets (•)**: Use proper list formatting with `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from the layout. Only specify `<a:buChar>` or `<a:buNone>`.

---

## Common Pitfalls

### Template Adaptation

When source content has fewer items than the template:
- **Remove excess elements entirely** (images, shapes, text boxes), don't just clear text
- Check for orphaned visuals after clearing text content
- Run visual QA to catch mismatched counts

When replacing text with different length content:
- **Shorter replacements**: Usually safe
- **Longer replacements**: May overflow or wrap unexpectedly
- Test with visual QA after text changes
- Consider truncating or splitting content to fit the template's design constraints

**Template slots ≠ Source items**: If template has 4 team members but source has 3 users, delete the 4th member's entire group (image + text boxes), not just the text.

### Multi-Item Content

If source has multiple items (numbered lists, multiple sections), create separate `<a:p>` elements for each — **never concatenate into one string**.

**❌ WRONG** — all items in one paragraph:
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**✅ CORRECT** — separate paragraphs with bold headers:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

Copy `<a:pPr>` from the original paragraph to preserve line spacing. Use `b="1"` on headers.

### Smart Quotes

Handled automatically by unpack/pack. But the Edit tool converts smart quotes to ASCII.

**When adding new text with quotes, use XML entities:**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| Character | Name | Unicode | XML Entity |
|-----------|------|---------|------------|
| `“` | Left double quote | U+201C | `&#x201C;` |
| `”` | Right double quote | U+201D | `&#x201D;` |
| `‘` | Left single quote | U+2018 | `&#x2018;` |
| `’` | Right single quote | U+2019 | `&#x2019;` |

### Other

- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing**: Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces)

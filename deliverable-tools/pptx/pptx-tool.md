---
name: pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX Skill

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

---

<!-- @AI_GENERATED -->
## ⛔ PRECEDENCE RULING — business-case skill（远景母版）场景优先级裁决（最高优先级，先于下方一切通用建议）

> **适用条件**：当本工具被 `business-case` skill（远景智能母版 master template）调用出片时，本裁决块**优先级高于**下文「Design Ideas」整节。

**优先级裁决（precedence / 优先）**：在该场景下，以下 **母版硬约束** 与逐页规格的优先级**高于（优先于 / precedence over / outrank）**本文件「Design Ideas」节的通用建议（通用配色表 / 拉丁字体配对 / 圆角图框母题 / 变换布局）：

- **`SKILL.md` 红线 1**：仅用指定母版 + 版式只用 "simple title only" + 仅封面（P1）用母版 cover 版式；
- **`SKILL.md` 红线 2**：只用母版动态取色取字（禁止引入母版色板以外的颜色与字体）；
- **`SKILL.md` 红线 4b（母版硬约束）**：**直角框铁律**（全 deck 禁止圆角框）/ 节点化铁律 / **固定版式**（roadmap 四阶段、ontology 四层横向架构）；
- **`ppt-deck-mapping` 逐页规格**：P1–P12 各页的固定版式与呈现规格。

**冲突裁决（必须遵守）**：当下方「Design Ideas」（**Design Ideas**：通用配色表 / 拉丁字体配对 / **圆角图框母题** / **变换布局**）与上述**母版硬约束**或逐页规格冲突时，**一律以母版硬约束与逐页规格为准**，让位通用建议；本场景下 **直角框 / 固定版式（right-angle / fixed-layout）** 为铁律，不得被通用 Design Ideas 覆盖。
<!-- @AI_GENERATED: end -->

<!-- @AI_GENERATED -->
## 模板节样式确定性绑定（business-case skill 强制 · 5.1/5.2/5.3，命中即阻断）

> 在 business-case skill（远景母版）场景下，"某一页该用哪张模板页样式"**不得临场判断 / 发散选偏**；每一张生成页的样式来源由其**角色（role）确定性映射**到唯一具名模板节（section），**必须**遵守以下硬规则。

**① 固定映射表（fixed mapping，必须 / MANDATORY）**：角色到具名节的映射固定唯一，不随执行时机变化：

| 页面角色 role | 绑定模板节 section |
|---|---|
| cover | **cover→cover** 节样式/版式 |
| content | **content→content** 节样式/版式 |
| ending | **ending→ending** 节样式/版式 |

- **必须**从母版 `ppt/presentation.xml` 节列表读取 `cover`、`content`、`ending` 三个具名节；同一角色**必须**始终绑定同一节样式来源（所有 content 页共用同一 content 节样式）。

**② 位置法角色识别（positional role detection，必须 / MANDATORY）**：角色由页面在生成序列中的位置确定性判定：

- **首=cover**：序列第一张页面判定为角色 cover；
- **中=content**：首页与末页之间的每一张页面判定为角色 content；
- **末=ending 或 content**：末页在 ending 被显式请求且存在时判定为 ending，否则判定为 content。

**③ ending 默认不启用（ending not invoked by default，必须 / MANDATORY）**：`ending` 节为**可选（optional）**，**ending 默认不启用**，仅在**显式请求**时才生成末页 ending 并绑定 ending 节样式；未显式请求时成片**不得**包含 ending 角色页面。

**强制门槛（命中即阻断）**：任一页面的样式来源（style source）与其角色对应的期望节不匹配，即判定确定性绑定未满足 → **阻断出片成功声明、返工**重绑，追溯校验（traceability check）通过后方可继续（追溯校验为出片前强制门槛，详见下方「残留占位符检查」旁的追溯校验门槛说明）。
<!-- @AI_GENERATED: end -->

<!-- @AI_GENERATED -->
## 封面占位符填充（business-case skill 强制）

- **强制（必须 / MANDATORY）**：封面（P1）只用母版 cover 版式；**必须**把真实**客户名 / 项目标题 / 日期**填入 cover 版式自带的**标题/副标题占位符（cover placeholder）**，**不得**另建浮动文本框顶替占位符，也不得残留母版默认占位文字（如 "Cover Page Style A"）。
- 内容页（P2 起）同理：标题**必须**填入母版自带标题占位符（placeholder），不另建浮动文本框。
<!-- @AI_GENERATED: end -->

<!-- @AI_GENERATED -->
## CJK 取字绑定（business-case skill 强制）

- **绑定母版 CJK 字体**：中文文本**必须**绑定母版指定的 CJK 字体（如 **Microsoft YaHei / 微软雅黑**），使中文 run 不回退到无字形的拉丁字体（消除逐元素 fallback / 字体异常）。
- **run 级中英字体分设**：中英混排文本做 **run 级（run-level）中英分别设置**——同一段落内，中文 run 用母版 CJK 字体、拉丁 run 用母版拉丁字体，**中英分设**而非整体套一个拉丁字体。
- **取字优先级**：本 skill 场景**只用母版取色取字**，该规则**优先于**下文通用**拉丁字体配对**表（font-pairing table）；通用「挑个性字体、别用默认 Arial」建议在本场景让位于母版取字。
<!-- @AI_GENERATED: end -->

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

<!-- @AI_GENERATED -->
> **⚠️ business-case skill 场景注记（见上方 PRECEDENCE RULING）**：本节为通用建议；在 business-case skill（远景母版）场景下，**禁用圆角图框母题与变换布局**（rounded image frames motif / vary-layout 在本场景**禁用**、让位），roadmap / ontology 一律使用**固定版式 + 直角框**。通用配色表与拉丁字体配对在本场景让位于母版取色取字。
<!-- @AI_GENERATED: end -->

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

<!-- @AI_GENERATED -->
> **business-case skill 场景（1.3/1.4）**：上述**圆角图框母题（rounded image frames）禁用**；本场景所有框 / 节点 / 卡片一律 **直角框（right-angle）**，无页面例外。
<!-- @AI_GENERATED: end -->

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

<!-- @AI_GENERATED -->
> **business-case skill 场景（1.3/1.4）**：**变换布局（vary-layout）禁用**——roadmap / ontology 等使用 `ppt-deck-mapping` 规定的**固定版式（fixed-layout）+ 直角框**，不得为求变化而偏离逐页固定规格。
<!-- @AI_GENERATED: end -->

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

<!-- @AI_GENERATED -->
## 价值树节点化绘制（business-case skill 强制 · 1.6）

> 通用工具无"节点化"概念；本节为 business-case skill 场景补齐**价值树节点化绘制强制指引**与**生成环节强制校验**。

**绘制强制指引：**
- **等式逐项成独立直角框**：价值方向/核心商业等式的**每个变量各自一个独立直角框**，框间用 ×／＋／－／÷／＝ 等运算符连接（如 `单位增重饲料成本` ＝ `料肉比` × `单位饲料价格` 必须是三个独立框，**禁止**拍平成一行公式文字）。
- **单父树**：每个下层节点**有且仅有一个上层父节点**，保持单父结构。
- **关键影响因子前置**：`quantify_priority = high` 的关键影响因子在 P6 前置呈现（关键影响因子总览）。
- **保留运算符与父子关系**：节点间的运算符与父子连接关系**必须保留**，不得丢失或拍平。

**生成环节强制校验（命中即阻断 / 返工）：**
- 生成价值树时执行节点化校验：若出现等式被拍平为纯文字、丢失运算符、丢失父子关系、或非单父结构，则判定**节点化未满足 → 阻断出片、返工**重绘为独立直角框 + 运算符/箭头，校验通过后方可继续。
<!-- @AI_GENERATED: end -->

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

<!-- @AI_GENERATED -->
### 残留占位符检查 —— 出片前强制门槛（business-case skill，命中即阻断）

> 在 business-case skill 场景下，残留占位符检查**不是建议，而是出片前强制门槛（HARD pre-delivery gate）**：**命中即阻断成功声明**（命中即阻断 / 返工），未清零不得交付。

grep 集合**必须**包含 `Cover Page Style`（母版默认封面占位文字）与版式占位符模式 `this.*(page|slide).*layout`，以及 `xxxx|lorem|ipsum`：

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout|Cover Page Style"
```

只要上述 grep **命中任一结果**（含残留 "Cover Page Style A" 等母版默认封面占位文字），即判定占位符未填，**强制门槛不通过 → 阻断出片成功声明**，必须先把真实客户名/项目标题/日期填入 cover 占位符、清空残留后复检至零，方可交付。
<!-- @AI_GENERATED: end -->

<!-- @AI_GENERATED -->
### 追溯校验（traceability check）—— 出片前强制门槛（business-case skill，命中即阻断）

> 与上方「残留占位符检查」并列，**追溯校验（traceability check）同为出片前强制门槛（HARD pre-delivery gate）**：出片前**必须**为成片每一页判定其样式来源（style source）是否等于该页角色（role）对应的期望节（section），依据即上方「模板节样式确定性绑定」的固定映射表（cover→cover / content→content / ending→ending）与位置法（首=cover / 中=content / 末=ending 或 content）。

- **命中即阻断**：只要任一页面的样式来源不等于其角色对应的期望节，即判定追溯校验不通过 → **阻断出片成功声明**并标识不匹配页面，返工重绑后复检，全部页面匹配方可交付。
- 追溯校验与残留占位符检查**均须通过**，任一不过即不得声明出片成功。
<!-- @AI_GENERATED: end -->

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images

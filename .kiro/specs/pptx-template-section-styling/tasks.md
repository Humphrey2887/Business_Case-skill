<!-- @AI_GENERATED -->
# Implementation Plan / 实施计划: pptx-template-section-styling

## Overview

本计划把设计文档拆解为可增量执行的编码任务，覆盖两层落地：Python 强制层（`section_style_binder.py`、`pre_delivery_gate.py`）与 Markdown 指引层（`pptx-tool.md` / `editing.md` / business-case `SKILL.md`），并固化既有回归防护（封面占位符填充、母版取色取字与 run 级中英分设、直角框/固定版式）。

实现语言为 **Python**（与既有 `deliverable-tools/pptx/scripts/` 一致），XML 处理统一使用 `defusedxml.minidom`（禁用 `xml.etree.ElementTree`，见设计 A4）。属性测试建议使用 `hypothesis`。

任务按「先前置确认母版结构 → 解析/识别/绑定 → 门槛 → 回归防护 → 指引层 → 集成布线」顺序增量推进，每个任务都建立在前序任务之上，末尾统一布线，避免出现游离未接入的代码。带 `*` 的子任务为可选（测试类），核心实现子任务不得跳过。

## Tasks

- [x] 1. 前置：确认并（必要时）重构母版三节结构（Assumptions A1–A3）
  - Unpack 母版模板 `templates/pptx/masters/envision-china-template-2023.pptx`（沿用现有 `unpack.py`），实探确认 A1（母版存在与路径）。
  - 读取 `ppt/presentation.xml`，确认 `<p:extLst>` 下 `<p:ext uri="{521415D9-36F7-43E2-AB2F-B90AF26B5E84}">` 内 `<p14:sectionLst>` 已含 `cover`/`content`/`ending` 三个具名节，且每节至少含一张模板 slide（A2）。
  - IF 母版未分节或节名不一致：新增/修正 `<p:sectionLst>`，按 `cover/content/ending` 归组各 `<p:sldId>`（A3），使用 `defusedxml.minidom` 读写，`pack.py --original` 回封验证可正常打开。
  - 在 spec 目录记录实探结论（节存在性、节名、各节 slide id、ending 是否存在），作为后续绑定与测试固件的事实依据。
  - _Requirements: 1.5_ _Assumptions: A1, A2, A3, A4_

- [x] 2. Checkpoint - 母版结构确认
  - Ensure all tests pass, ask the user if questions arise.（若母版无法满足三节结构或 ending 缺失策略不明，暂停并与用户确认后再继续。）

- [x] 3. 实现 `section_style_binder.py` 节解析与角色识别
  - [x] 3.1 实现 `parse_sections`（presentation.xml 节解析）
    - 在 `deliverable-tools/pptx/scripts/section_style_binder.py` 新建 `SectionInfo` dataclass 与 `parse_sections(presentation_xml_path)`。
    - 用 `defusedxml.minidom` 解析 `<p:ext uri="{521415D9-...}">` 内 `<p14:sectionLst>`，按 `name` 索引返回 `dict[str, SectionInfo]`，每节收集其 `<p14:sldId>` 分组到 `slide_ids`。
    - 缺 `cover` 或 `content` 节时抛 `SectionStructureError`；`ending` 缺失允许。定义 `SECTION_EXT_URI`、`KNOWN_SECTIONS` 常量。
    - 全部生成代码以 `# @AI_GENERATED` / `# @AI_GENERATED: end` 标注。
    - _Requirements: 1.5_

  - [x] 3.2 为 `parse_sections` 编写属性测试
    - **Property 3: 具名节解析完整性** — 对合法 `<p:sectionLst>` 固件，返回集合含 cover/content（存在时含 ending），每节关联其 sldId 分组；缺 cover/content 时报错。
    - 测试头标注 `Feature: pptx-template-section-styling, Property 3`。
    - **Validates: Requirements 1.5**

  - [x] 3.3 为 `parse_sections` 编写示例/边界测试
    - 用代表性 `presentation.xml` 固件（含/不含 ending 节；缺 content 报错）以 `defusedxml.minidom` 解析断言，防命名空间回归。
    - **Validates: Requirements 1.5**

  - [x] 3.4 实现 `detect_roles`（位置法角色识别）与 `Role` 枚举
    - 实现 `Role(str, Enum)` 与 `detect_roles(page_count, ending_requested)`：首页 COVER；首末之间 CONTENT；末页 ENDING（当 `ending_requested` 且 `page_count>=2`）否则 CONTENT；`page_count==1` 仅 `[COVER]`。
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2_

  - [x] 3.5 为 `detect_roles` 编写属性测试（位置法）
    - **Property 4: 位置法角色识别** — 非空序列首页为 cover，首末之间每页为 content。
    - **Validates: Requirements 2.1, 2.2**

  - [x] 3.6 为 `detect_roles` 编写属性测试（ending 可选性）
    - **Property 5: ending 可选性与末页角色** — 长度≥2 时，请求 ending 则末页为 ending，否则末页为 content 且序列不含任何 ending 角色页。
    - **Validates: Requirements 2.3, 2.4, 3.1, 3.2, 1.3**

- [x] 4. 实现 `section_style_binder.py` 确定性绑定
  - [x] 4.1 实现 `FIXED_MAPPING`、`BoundPage` 与 `bind_pages`
    - 定义 `FIXED_MAPPING = {COVER:"cover", CONTENT:"content", ENDING:"ending"}` 与 `BoundPage` dataclass。
    - 实现 `bind_pages(sequence, sections, ending_requested)`：调用 `detect_roles`，按固定映射设置 `page.role` 与 `page.style_source`；所有 content 页共享同一 content 节样式来源。
    - 实现 `_apply_section_layout(page, section)`：将该页 `slideN.xml.rels` 的 `slideLayout` 关系指向目标节模板 slide 的 layout，并以该节模板 slide 为样式骨架（`<p:ph>` 结构/母版引用），用 `defusedxml.minidom` 读写。
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 4.2 为 `bind_pages` 编写属性测试（确定性映射）
    - **Property 1: 角色→节确定性映射** — 每张 cover 页 `style_source=="cover"`，每张 content 页 `style_source=="content"`。
    - **Validates: Requirements 1.1, 1.2**

  - [x] 4.3 为 `bind_pages` 编写属性测试（content 一致性）
    - **Property 2: content 页样式来源一致性** — 含≥2 张 content 页时，所有 content 页 `style_source` 彼此相等，指向同一 content 节样式来源。
    - **Validates: Requirements 1.4**

- [x] 5. Checkpoint - 绑定层可核验
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. 实现 `pre_delivery_gate.py` 门槛
  - [x] 6.1 实现 `traceability_check`（G1 追溯校验）
    - 在 `deliverable-tools/pptx/scripts/pre_delivery_gate.py` 新建 `TraceResult` 与 `traceability_check(bound_pages)`：逐页判定 `style_source == FIXED_MAPPING[role]`，记录 `(index, role, expected, actual)`，`passed` 当且仅当无错配。
    - 提供从成片 `slideN.xml` 的 layout 关系反解其所属节的辅助函数（供实际成片校验用）。
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 6.2 为 `traceability_check` 编写属性测试
    - **Property 6: 追溯校验判定正确且门槛等价于无错配** — 逐页判定正确，门槛通过当且仅当无错配页；有错配时失败并标识全部不匹配页。
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [x] 6.3 实现 `placeholder_grep_gate`（G2 残留占位符门槛）
    - 定义 `PLACEHOLDER_PATTERNS = [xxxx, lorem, ipsum, this.*(page|slide).*layout, Cover Page Style]`，实现 `placeholder_grep_gate(deck_text)`，`re.IGNORECASE` 逐模式检查返回命中列表。
    - 文本来源约定为 `python -m markitdown output.pptx`（与现有 QA 一致）。
    - _Requirements: 9.1, 9.2, 6.3_

  - [x] 6.4 为 `placeholder_grep_gate` 编写属性测试
    - **Property 8: 残留占位符 grep 门槛** — 命中模式集合任一项则门槛失败；无命中则通过（含 `Cover Page Style`）。
    - **Validates: Requirements 9.1, 9.2, 6.3**

  - [x] 6.5 实现 `value_tree_check`（G3 价值树节点化校验）
    - 实现 `ValueTreeIssue` 与 `value_tree_check(model)`：检测「拍平为纯文字 / 丢失运算符 / 丢失父子边 / 非单父」四类违规（kinds: flattened / missing_operator / missing_edge / multi_parent），返回 issues 列表。
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 6.6 为 `value_tree_check` 编写属性测试（结构保持）
    - **Property 11: 价值树节点化结构保持** — 每变量为独立直角框、框间以运算符连接、每下层节点恰一父，渲染后运算符集合与父子边集合与输入模型一致。
    - **Validates: Requirements 10.1, 10.2, 10.3**

  - [x] 6.7 为 `value_tree_check` 编写属性测试（违规阻断）
    - **Property 12: 价值树违规阻断** — 出现拍平/丢运算符/丢父子/多父任一情况，门槛失败并要求返工重绘。
    - **Validates: Requirements 10.4**

  - [x] 6.8 实现 `run_gate`（门槛聚合）
    - 实现 `GateReport` 与 `run_gate(bound_pages, deck_text, value_tree_model=None)`：聚合 G1/G2/G3，任一失败则 `passed=False`；提供 CLI 入口（非零退出并列出问题页/命中模式/违规），置于 `pack.py` 之前运行。
    - _Requirements: 4.2, 6.3, 9.2, 10.4_

  - [x] 6.9 为 `run_gate` 编写集成测试
    - 组合 G1/G2/G3 各通过/失败场景，断言聚合语义与非零退出，验证阻断出片成功声明。
    - **Validates: Requirements 4.2, 9.2, 10.4**

- [x] 7. Checkpoint - 门槛层可核验
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. 回归防护固化（封面占位符 / 取色取字 / 直角框）
  - [x] 8.1 固化封面占位符填充
    - 在绑定 cover 节后，将真实客户名/项目标题/日期回填到 cover 版式自带 `<p:ph type="ctrTitle"/"subTitle">` 占位符；禁止新建浮动文本框；残留 `Cover Page Style` 交由 G2 拦截。
    - _Requirements: 6.1, 6.2_

  - [x] 8.2 为封面占位符填充编写属性测试
    - **Property 7: 封面占位符填充与母版占位符承载** — 封面文本均位于 cover 版式自带 `<p:ph>` 内，不产生无占位符的新建浮动文本框。
    - **Validates: Requirements 6.1, 6.2**

  - [x] 8.3 固化母版取色取字与 run 级中英字体分设
    - 颜色/字体仅从 Master_Template 动态提取；每个文本 run 按脚本分设：中文 run 用 `<a:ea typeface="母版CJK字体">`，拉丁 run 用 `<a:latin typeface="母版拉丁字体">`，同段落内中/英 run 分别设置，避免中文回退无字形拉丁字体。
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 8.4 为取色取字与 run 级分设编写属性测试
    - **Property 9: 母版取色取字与 run 级中英字体分设** — 文本 run 颜色/字体取自母版提取集合；中英混排段落中 CJK run 绑 CJK 字体、拉丁 run 绑拉丁字体。
    - **Validates: Requirements 7.1, 7.2, 7.3**

  - [x] 8.5 固化直角框与固定版式
    - 所有框/节点/卡片使用 `<a:prstGeom prst="rect">`（禁止 `roundRect`/圆角 adj）；roadmap/ontology 遵循 `ppt-deck-mapping` 固定版式规格。
    - _Requirements: 8.1, 8.2_

  - [x] 8.6 为直角框不变量编写属性测试
    - **Property 10: 直角框不变量** — 生成的框/节点/卡片几何为 `prstGeom prst="rect"`，不存在圆角框。
    - **Validates: Requirements 8.1**

  - [x] 8.7 为固定版式规格编写示例测试
    - 断言 roadmap/ontology 页遵循 `ppt-deck-mapping` 固定版式规格。
    - **Validates: Requirements 8.2**

- [x] 9. Markdown 指引层硬规则更新
  - [x] 9.1 更新 `pptx-tool.md` 硬规则块
    - 新增「模板节样式确定性绑定」硬规则：固定映射表（cover→cover / content→content / ending→ending）、位置法（首=cover、中=content、末=ending 或 content）、ending 默认不启用；并在「残留占位符检查」旁引用追溯校验为出片前强制门槛。以 `<!-- @AI_GENERATED -->` 标注。
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.2 更新 `editing.md` 的 Template-Based Workflow
    - 插入：unpack 后先读 `presentation.xml` 具名节；编辑阶段按角色绑定对应节；pack 前须过 Pre-Delivery Gate。以 `<!-- @AI_GENERATED -->` 标注。
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.3 更新 business-case `SKILL.md` 红线
    - 红线新增/强化：角色→节映射为硬红线；追溯校验失败即阻断出片成功声明；ending 默认不启用。以 `<!-- @AI_GENERATED -->` 标注。
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.4 为指引硬规则文本编写存在性测试
    - 用 grep 断言三处文件均含固定映射、位置法、ending 默认不启用的硬规则措辞。
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 10. 集成与布线
  - [x] 10.1 将 binder 与 gate 接入模板工作流
    - 在 `unpack.py → <p:sldIdLst> 操作 → 编辑 slideN.xml → clean.py → pack.py` 链路中接入：编辑阶段调用 `parse_sections`+`bind_pages`，`pack.py` 前调用 `run_gate`；确保无游离未接入代码。提供顶层 CLI/入口串起全流程。
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.2_

  - [x] 10.2 编写端到端集成测试（自动化）
    - 用 unpack 母版固件驱动 binder→gate 全链路（不含手动运行应用）：验证正常成片通过、错配/占位符残留/价值树违规被阻断。
    - **Validates: Requirements 1.1, 4.2, 9.2, 10.4**

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- 带 `*` 的子任务为可选（单元/属性/集成测试），可为更快 MVP 跳过；核心实现子任务不得跳过。
- 每个任务引用具体需求条款以保证可追溯；每条属性测试显式引用设计中的属性编号与其 Validates 需求。
- Checkpoint 保证增量验证；任务 1 为前置母版结构确认（A1–A3），须先完成。
- 全部 XML 读写使用 `defusedxml.minidom`（A4）；所有 AI 生成代码/文本块以 `@AI_GENERATED` 标注。

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["3.1", "3.4"] },
    { "id": 2, "tasks": ["3.2", "3.3", "3.5", "3.6"] },
    { "id": 3, "tasks": ["4.1"] },
    { "id": 4, "tasks": ["4.2", "4.3", "6.1", "6.3", "6.5"] },
    { "id": 5, "tasks": ["6.2", "6.4", "6.6", "6.7", "6.8"] },
    { "id": 6, "tasks": ["6.9", "8.1", "8.3", "8.5", "9.1", "9.2", "9.3"] },
    { "id": 7, "tasks": ["8.2", "8.4", "8.6", "8.7", "9.4", "10.1"] },
    { "id": 8, "tasks": ["10.2"] }
  ]
}
```
<!-- @AI_GENERATED: end -->

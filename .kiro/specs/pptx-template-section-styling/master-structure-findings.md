<!-- @AI_GENERATED -->
# Master Structure Findings / 母版结构实探结论

> Task 1 前置实探（Assumptions A1–A4）的事实记录。作为后续绑定实现（Task 3/4）、门槛（Task 6）与测试固件的事实依据。
> 生成/编辑工具：`unpack.py` / `pack.py`（`deliverable-tools/pptx/scripts/office/`），XML 读写统一 `defusedxml.minidom`（A4 满足）。

## A1 — 母版存在与路径 ✅ 确认

- **实际路径**：`templates/pptx/masters/envision-china-template-2023.pptx`（与设计假设路径一致，无需调整绑定工具的模板输入参数）。
- 母版含 **3 张 slide**（`ppt/slides/slide1.xml`、`slide2.xml`、`slide3.xml`）与 24 个 slideLayout。
- `unpack.py` 可正常解包（85 个 XML 文件）。

## A2 — 三节结构与具名节 ✅ 存在（但节名需归一，见 A3）

母版 `ppt/presentation.xml` 的 `<p:extLst>` 下 `<p:ext uri="{521415D9-36F7-43E2-AB2F-B90AF26B5E84}">` 内 **已含** `<p14:sectionLst>`，包含三个具名节，每节各含一张模板 slide：

| 顺序 | 实探原节名 | 归一后节名 | section GUID | 关联 `<p:sldId>` id | 关联 slide 文件 | slide 的 slideLayout | 角色（位置法） |
|------|-----------|-----------|--------------|---------------------|-----------------|----------------------|----------------|
| 1 | `Covers`  | `cover`   | `{81316CC1-DC07-724F-951F-344DE4F26084}` | 287 (rId7) | `slides/slide1.xml` | `slideLayout1.xml`  | cover |
| 2 | `Content` | `content` | `{BC31728A-994C-7647-ABEC-B14018EBDEF1}` | 276 (rId8) | `slides/slide2.xml` | `slideLayout14.xml` | content |
| 3 | `Ending`  | `ending`  | `{81C88842-2B13-470F-9360-8408E803334B}` | 295 (rId9) | `slides/slide3.xml` | `slideLayout4.xml`  | ending |

- `<p:sldIdLst>` 顺序为 287 → 276 → 295，与节顺序一致（首=cover、中=content、末=ending），符合位置法（Requirement 2）。
- 每节均**至少含一张模板 slide**（此处恰各含一张），可作为该节的版式/样式来源（section style source）。A2 结构性要求满足。
- 各节 slide 分别绑定不同 layout（1 / 14 / 4），即三节各有独立版式来源。

### 各 slide 语义/内容验证（确认角色）

- **slide1（cover）**：标题文本为母版默认占位文字 `Cover Page Style A`（属封面版式；此文字命中 R6.3/R9 的 `Cover Page Style` grep 门槛模式，说明这是模板占位而非真实内容）。
- **slide2（content）**：含 `Title here` / `标题在这里`，run 级中文使用 `<a:ea typeface="微软雅黑 Bold">`（CJK 字体 = 微软雅黑 / Microsoft YaHei）。确认为内容页版式。
- **slide3（ending）**：含 `Cover Page Style D` 与 `Empowering the Journey to Net Zero with Scalable and Composable Digital Foundations`。确认存在结尾页版式。

### ending 节存在性 ✅

- **`ending` 节存在**（`{81C88842-...}` → slide3 / slideLayout4）。因此 Requirement 3（ending 可选、默认不启用）在母版侧有版式支撑；「显式请求 ending 但母版缺 ending 节」的降级策略（design Error Handling）**在本母版无需触发**——ending 版式已就绪。

## A3 — 重构/修正 ✅ 已执行（仅节名归一，未改结构/分组）

**发现的不一致**：三节**结构与分组正确**，但**节名与设计期望不一致**：
- 设计 `KNOWN_SECTIONS = ("cover", "content", "ending")`（全小写），`parse_sections` 期望返回键集合 `{'cover','content','ending'}`。
- 母版实探节名为 `Covers`（复数、首字母大写）、`Content`（首字母大写）、`Ending`（首字母大写）。

**执行的修正**（最小改动，仅改 `<p14:section>` 的 `name` 属性，保留 GUID 与 `<p14:sldIdLst>` 分组不变）：
- `Covers` → `cover`
- `Content` → `content`
- `Ending` → `ending`

**执行方式**：
1. 备份原母版为 `envision-china-template-2023.backup-presection.pptx`（保存在 spec 目录，见文末「产物」）。
2. `unpack.py` 解包 → 用 `str_replace` 改 `presentation.xml` 三处 `name` 属性（`defusedxml.minidom` 已在 unpack/pack 全程使用，A4 满足）。
3. `pack.py --original <备份>` 回封，**验证通过**（`All validations PASSED!`）并成功写回原母版路径。
4. 复解包回读确认三节名现为 `cover` / `content` / `ending`（GUID 与 slide 分组不变），母版可正常打开。

> **重要（供 Task 2 Checkpoint 向用户确认）**：本次对**生产母版模板做了原地修改**（仅节名归一）。若团队更希望「保持母版原节名不变、改为在 `parse_sections` 侧做大小写/复数归一匹配」，则应回滚母版（用备份还原）并调整 Task 3.1 的解析策略。当前已采用「归一母版节名」方案，使母版成为干净的确定性事实源。

## A4 — XML 工具 ✅ 满足

- 全流程 XML 读写均经由 `unpack.py` / `pack.py`（内部使用 `defusedxml.minidom`）与编辑器 `str_replace`；未使用 `xml.etree.ElementTree`。

## 环境备注（供后续任务复用）

- 本机 `python` 未注册，使用 **`py`**（Python 3.13.14）执行脚本。
- 运行 `pack.py` 校验时，Windows 中文 locale 默认 GBK 编解码会导致校验器读取 `docProps/app.xml`、`docProps/custom.xml`（UTF-8）报 `'gbk' codec can't decode ...`。**解决办法：设置 `PYTHONUTF8=1`** 后校验通过。后续任务在本机运行 pack/校验时应设置该环境变量。
- `defusedxml` 版本 0.7.1 已安装。

## 结论摘要（事实依据）

- A1 ✅ 母版存在，路径与假设一致。
- A2 ✅ 三节结构存在，每节各一张模板 slide，顺序 cover→content→ending 与 sldIdLst 一致。
- A3 ✅ 已将节名归一为 `cover`/`content`/`ending`（结构/分组/GUID 不变），回封校验通过、可正常打开。
- A4 ✅ 全程 `defusedxml.minidom`。
- ending 节存在，Requirement 3 的「缺 ending」降级策略在本母版无需触发。

## 产物

- 修正后的母版（原地写回）：`templates/pptx/masters/envision-china-template-2023.pptx`
- 原母版备份：`.kiro/specs/pptx-template-section-styling/envision-china-template-2023.backup-presection.pptx`
- 临时解包目录 `_scratch_master_unpacked/`、`_scratch_verify_unpacked/` 已在 Task 1 结束后清理。
<!-- @AI_GENERATED: end -->

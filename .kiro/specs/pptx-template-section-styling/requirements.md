<!-- @AI_GENERATED -->
# Requirements Document

## Introduction

本特性在 business-case / 远景智能咨询 skill 从母版模板（`templates/pptx/masters/envision-china-template-2023.pptx`）出片时，强制实现**每一张生成幻灯片的角色（role）到具名模板节（section）样式的确定性映射**，消除当前"某一页该用哪张模板页样式"发散、依赖临场判断的非确定性选择，从而保证成片始终遵循远景母版视觉规范。

模板结构精简为**三页 / 三个具名节**：`cover`、`content`、`ending`。角色识别采用**位置法（positional）**：第一张 = cover，中间各张 = content，最后一张 = ending（仅在被显式请求时出现）。映射固定为 cover→cover、content→content、ending→ending。`ending` 节为**可选（optional）**，默认不启用（not invoked by default）。

修复跨两个层面落地：
- **Python 层**：读取模板 `ppt/presentation.xml` 中的具名节列表，按角色确定性地把每张生成页绑定到对应节的版式/样式，并提供可核验（verifiable）的校验；
- **Markdown 技能指引层**：将上述映射编码为硬规则（hard rules），写入 `pptx-tool.md` / `editing.md` / business-case `SKILL.md` 红线；
- **出片前门槛（pre-delivery gate）**：若任一页的样式来源与其角色不匹配，则阻断成功声明。

本文件同时把既有强制约束（封面占位符填充、母版取色取字与 run 级中英字体分设、直角框/固定版式、残留占位符 grep 门槛、价值树节点化校验）作为**回归防护**予以固化。

## Glossary

- **PPTX_Styling_Tool（样式绑定工具）**: Python 层工具/脚本，负责读取模板具名节并把生成页确定性绑定到对应节样式，并输出可核验校验结果。位于 `deliverable-tools/pptx/scripts/`。
- **Skill_Guidance（技能指引）**: Markdown 技能规则文档，包含 `pptx-tool.md`、`editing.md` 及 business-case `SKILL.md` 红线，将映射编码为硬规则。
- **Pre_Delivery_Gate（出片前门槛）**: 出片交付前执行的强制校验，任一校验失败即阻断成功声明。
- **Section（具名节）**: 模板 `ppt/presentation.xml` 节列表中的具名分节，取值为 `cover`、`content`、`ending` 之一。
- **Role（页面角色）**: 生成页的角色，取值为 `cover`、`content`、`ending` 之一，由位置法确定。
- **Positional_Role_Detection（位置法角色识别）**: 依据页面在生成序列中的位置确定角色——第一张为 `cover`，中间各张为 `content`，最后一张为 `ending`（当 ending 被显式请求且存在时）。
- **Style_Source（样式来源）**: 某一生成页实际套用样式所对应的模板节（或 NONE / 非模板节）。
- **Deterministic_Binding（确定性绑定）**: 对同一角色，工具始终绑定到唯一固定的对应节样式来源，不随执行时机变化。
- **Traceability_Check（可追溯校验）**: 对成片中每一页判定其 Style_Source 是否等于其 Role 对应的期望 Section 的可核验检查。
- **Master_Template（母版模板）**: `templates/pptx/masters/envision-china-template-2023.pptx`。
- **CJK_Font（母版 CJK 字体）**: 母版指定的中日韩字体，如 Microsoft YaHei / 微软雅黑。
- **Placeholder_Grep_Gate（残留占位符 grep 门槛）**: 以 grep 模式集合检查残留占位符文字的出片前门槛。

## Requirements

### Requirement 1: 角色到模板节样式的确定性映射

**User Story:** 作为使用 business-case skill 出片的顾问，我希望每一页的样式来源由其角色确定性决定，以便成片始终符合远景母版规范而不再发散选偏。

#### Acceptance Criteria

1. WHEN PPTX_Styling_Tool 处理一张角色为 cover 的生成页，THE PPTX_Styling_Tool SHALL 将该页的 Style_Source 绑定到 cover 节的版式/样式。
2. WHEN PPTX_Styling_Tool 处理一张角色为 content 的生成页，THE PPTX_Styling_Tool SHALL 将该页的 Style_Source 绑定到 content 节的版式/样式。
3. WHEN PPTX_Styling_Tool 处理一张角色为 ending 的生成页，THE PPTX_Styling_Tool SHALL 将该页的 Style_Source 绑定到 ending 节的版式/样式。
4. WHERE 生成序列包含多张角色为 content 的页面，THE PPTX_Styling_Tool SHALL 为所有 content 页绑定同一个 content 节样式来源。
5. THE PPTX_Styling_Tool SHALL 从 Master_Template 的 `ppt/presentation.xml` 节列表中读取 cover、content、ending 三个具名节。

### Requirement 2: 位置法角色识别

**User Story:** 作为顾问，我希望工具依据页面位置自动判定角色，以便无需为每页手工指定样式即可获得正确绑定。

#### Acceptance Criteria

1. WHEN PPTX_Styling_Tool 对生成序列执行 Positional_Role_Detection，THE PPTX_Styling_Tool SHALL 将序列中第一张页面判定为角色 cover。
2. WHEN PPTX_Styling_Tool 对生成序列执行 Positional_Role_Detection，THE PPTX_Styling_Tool SHALL 将序列中位于首页与末页之间的每一张页面判定为角色 content。
3. WHERE ending 节被显式请求且生成序列末页为 ending 页，THE PPTX_Styling_Tool SHALL 将序列中最后一张页面判定为角色 ending。
4. WHERE ending 节未被显式请求，THE PPTX_Styling_Tool SHALL 将序列中最后一张页面判定为角色 content。

### Requirement 3: ending 节可选且默认不启用

**User Story:** 作为顾问，我希望 ending 页默认不出现，仅在显式请求时才生成，以避免多出非预期的结尾页。

#### Acceptance Criteria

1. WHERE 出片请求未显式要求 ending 节，THE PPTX_Styling_Tool SHALL 生成不包含 ending 角色页面的成片。
2. WHERE 出片请求显式要求 ending 节，THE PPTX_Styling_Tool SHALL 在成片末尾生成一张角色为 ending 的页面并绑定 ending 节样式。

### Requirement 4: 可追溯校验与出片前门槛

**User Story:** 作为顾问，我希望出片前能确定性地核验每一页样式来源是否正确，以便偏离母版的页面在交付前被拦截。

#### Acceptance Criteria

1. WHEN Pre_Delivery_Gate 对成片执行 Traceability_Check，THE Pre_Delivery_Gate SHALL 为每一页判定其 Style_Source 是否等于该页 Role 对应的期望 Section。
2. IF 任一页面的 Style_Source 不等于其 Role 对应的期望 Section，THEN THE Pre_Delivery_Gate SHALL 阻断该成片的出片成功声明并标识不匹配页面。
3. WHEN 成片中所有页面的 Style_Source 均等于各自 Role 对应的期望 Section，THE Pre_Delivery_Gate SHALL 允许该成片通过 Traceability_Check。

### Requirement 5: 技能指引硬规则编码

**User Story:** 作为顾问，我希望映射规则以硬规则形式写入技能指引，以便生成过程遵循确定性映射而非临场判断。

#### Acceptance Criteria

1. THE Skill_Guidance SHALL 记载角色到节的固定映射规则（cover→cover 节、content→content 节、ending→ending 节）作为硬规则。
2. THE Skill_Guidance SHALL 记载 Positional_Role_Detection 规则（首页为 cover、中间页为 content、末页为 ending 或 content）。
3. THE Skill_Guidance SHALL 记载 ending 节默认不启用、仅在显式请求时启用的规则。

### Requirement 6: 封面占位符填充（回归防护）

**User Story:** 作为顾问，我希望封面继续把真实信息填入母版占位符，以便封面不出现浮动文本框或残留母版占位文字。

#### Acceptance Criteria

1. WHEN 生成一张已绑定 cover 节样式的封面页，THE PPTX_Styling_Tool SHALL 将真实客户名、项目标题、日期填入 cover 版式自带的标题/副标题占位符。
2. WHEN 生成封面页文本，THE PPTX_Styling_Tool SHALL 使用母版自带占位符承载文本，而非另建浮动文本框。
3. IF 成片中残留母版默认占位文字（如 `Cover Page Style`），THEN THE Pre_Delivery_Gate SHALL 阻断出片成功声明。

### Requirement 7: 母版取色取字与 run 级中英字体分设（回归防护）

**User Story:** 作为顾问，我希望文本继续只用母版取色取字并对中英混排做 run 级分设，以便中文不回退到无字形拉丁字体。

#### Acceptance Criteria

1. WHEN 生成任意页面文本，THE PPTX_Styling_Tool SHALL 仅从 Master_Template 动态提取颜色与字体。
2. WHEN 生成中文文本 run，THE PPTX_Styling_Tool SHALL 将该 run 绑定 CJK_Font。
3. WHEN 生成中英混排段落，THE PPTX_Styling_Tool SHALL 在 run 级对中文 run 与拉丁 run 分别设置母版 CJK 字体与母版拉丁字体。

### Requirement 8: 直角框与固定版式（回归防护）

**User Story:** 作为顾问，我希望所有框/节点/卡片继续使用直角框并遵循固定版式，以便成片符合母版硬约束。

#### Acceptance Criteria

1. WHEN 生成任意框、节点或卡片，THE PPTX_Styling_Tool SHALL 使用直角框。
2. WHERE 页面为 roadmap 或 ontology 等固定版式页，THE PPTX_Styling_Tool SHALL 遵循 `ppt-deck-mapping` 规定的固定版式规格。

### Requirement 9: 残留占位符 grep 门槛（回归防护）

**User Story:** 作为顾问，我希望出片前继续执行 grep 占位符门槛，以便未清零的占位符在交付前被拦截。

#### Acceptance Criteria

1. WHEN Pre_Delivery_Gate 执行 Placeholder_Grep_Gate，THE Pre_Delivery_Gate SHALL 使用包含 `xxxx`、`lorem`、`ipsum`、`this.*(page|slide).*layout`、`Cover Page Style` 的 grep 模式集合检查成片文本。
2. IF Placeholder_Grep_Gate 命中任一模式，THEN THE Pre_Delivery_Gate SHALL 阻断出片成功声明。

### Requirement 10: 价值树节点化校验（回归防护）

**User Story:** 作为顾问，我希望价值树/等式继续执行节点化校验，以便等式保持逐项独立直角框、单父树并保留运算符与父子关系。

#### Acceptance Criteria

1. WHEN 生成价值树或核心商业等式，THE PPTX_Styling_Tool SHALL 将等式中每个变量绘制为独立的直角框，并以运算符（×／＋／－／÷／＝）连接各框。
2. WHEN 生成价值树节点，THE PPTX_Styling_Tool SHALL 使每个下层节点有且仅有一个上层父节点。
3. WHEN 生成价值树，THE PPTX_Styling_Tool SHALL 保留节点间的运算符与父子连接关系。
4. IF 价值树出现等式被拍平为纯文字、丢失运算符、丢失父子关系或非单父结构，THEN THE Pre_Delivery_Gate SHALL 阻断出片成功声明并要求返工重绘。
<!-- @AI_GENERATED: end -->

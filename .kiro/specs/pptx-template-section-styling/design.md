<!-- @AI_GENERATED -->
# Design Document / 设计文档

## Overview

概述

本设计实现「**每张生成幻灯片的角色（Role）到具名模板节（Section）样式的确定性绑定**」，消除当前"某页该用哪张模板样式"发散、依赖临场判断的非确定性选择。

修复横跨两层落地，二者缺一不可：

1. **Python 强制层（enforcement layer）** —— 位于 `deliverable-tools/pptx/scripts/`。读取母版模板 `ppt/presentation.xml` 中的具名节列表（`cover` / `content` / `ending`），对生成序列执行位置法角色识别，把每张生成页确定性绑定到对应节的版式/样式，并产出**可核验（verifiable）**的追溯校验结果。
2. **Markdown 技能指引层（guidance layer）** —— `deliverable-tools/pptx/pptx-tool.md`、`deliverable-tools/pptx/editing.md` 以及 business-case `SKILL.md` 红线。把角色→节映射、位置法、ending 默认不启用编码为**硬规则（hard rules）**，使生成过程遵循确定性映射而非发散判断。

两层共同支撑一个**出片前门槛（Pre-Delivery Gate）**：追溯校验 + 残留占位符 grep 门槛 + 价值树节点化校验，任一失败即阻断出片成功声明。

设计严格沿用既有模板工作流：`unpack.py` → 在 `<p:sldIdLst>` 操作幻灯片 → 编辑 `slideN.xml` → `clean.py` → `pack.py --original template.pptx`。**新增能力嵌入该链路的编辑阶段与打包前门槛，而非替换链路。**

### Assumptions to Confirm at Implementation Time / 实现期需确认的假设

以下为设计假设，**须在实现开始时确认**：

- **A1（母版位置/存在）**：母版模板位于 `templates/pptx/masters/envision-china-template-2023.pptx` 且存在。若路径不符，绑定工具的模板输入参数需相应调整。
- **A2（三节结构）**：该母版 `ppt/presentation.xml` 的 `<p:sectionLst>` 已包含 `cover`、`content`、`ending` 三个具名节，且每节至少含一张模板 slide（作为该节的版式/样式来源）。
- **A3（可能需要重构）**：若母版尚未划分为 3 节，或节名不一致，则需先**重构母版为三节结构**（新增 `<p:sectionLst>`、按 `cover/content/ending` 归组 `<p:sldId>`），此为本特性前置任务。
- **A4（XML 工具）**：全部 XML 读写使用 `defusedxml.minidom`；**禁止**使用 `xml.etree.ElementTree`（会破坏 OOXML 命名空间）。

> 上述假设在需求文档中亦已作为待确认项标注；实现前应对 A1/A2/A3 做一次实探（unpack 母版并检查 `presentation.xml`）。

---

## Architecture

架构

```
┌───────────────────────────────────────────────────────────────────────┐
│  business-case / 远景智能 skill 出片请求 (endingRequested: bool)         │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │
                     ┌───────────▼───────────┐
                     │  Guidance Layer (MD)   │  硬规则：角色→节映射 / 位置法 /
                     │  pptx-tool.md          │  ending 默认不启用 → 指导生成
                     │  editing.md            │
                     │  business-case SKILL.md│
                     └───────────┬───────────┘
                                 │  遵循硬规则生成 slide 序列
                                 ▼
   unpack.py ──► <p:sldIdLst> 操作 ──► 编辑 slideN.xml ──► clean.py ──► pack.py
                                 │                                        │
                     ┌───────────▼────────────────────┐                  │
                     │  Python Enforcement Layer        │                 │
                     │  section_style_binder.py         │                 │
                     │   1. parse_sections(pres.xml)    │                 │
                     │   2. detect_roles(sequence)      │                 │
                     │   3. bind(role → section style)  │                 │
                     └───────────┬────────────────────┘                  │
                                 │ 每页写入 Style_Source（绑定 layout/section）  │
                                 ▼                                        ▼
                     ┌──────────────────────────────────────────────────────┐
                     │  Pre-Delivery Gate  (pre_delivery_gate.py)              │
                     │   G1 Traceability_Check  (Style_Source == expected)     │
                     │   G2 Placeholder_Grep_Gate (xxxx|lorem|ipsum|...)       │
                     │   G3 Value-Tree Node-ization Check                      │
                     │   ── 任一失败 → 阻断成功声明 (exit≠0, 列出问题页) ──      │
                     └──────────────────────────────────────────────────────┘
```

### 分层职责

| 层 | 制品 | 职责 | 对应需求 |
|----|------|------|----------|
| Python 强制层 | `section_style_binder.py` | 解析节、位置法角色识别、确定性绑定 | R1, R2, R3 |
| Python 强制层 | `pre_delivery_gate.py` | 追溯校验 + grep 门槛 + 节点化校验 | R4, R6.3, R9, R10 |
| Python 强制层（回归） | 现有生成逻辑 + binder | 封面占位符填充、母版取色取字、run 级中英分设、直角框/固定版式 | R6, R7, R8 |
| Markdown 指引层 | `pptx-tool.md` / `editing.md` / `SKILL.md` | 映射硬规则、位置法、ending 默认不启用 | R5 |

---

## Components and Interfaces

组件与接口

代码示例语言为 **Python**（与既有 `deliverable-tools/pptx/scripts/` 一致），XML 处理统一使用 `defusedxml.minidom`。

### Component 1: `section_style_binder.py`（角色→节确定性绑定）

位于 `deliverable-tools/pptx/scripts/section_style_binder.py`。

#### 1.1 presentation.xml 节解析（parse_sections）

`ppt/presentation.xml` 的节信息位于 PowerPoint 扩展 `<p:sectionLst>`（命名空间 `http://schemas.openxmlformats.org/presentationml/2006/main`，节扩展 URI `{521415D9-36F7-43E2-AB2F-B90AF26B5E84}`），结构形如：

```xml
<p:presentation ...>
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId2"/>
    <p:sldId id="257" r:id="rId3"/>
    <p:sldId id="258" r:id="rId4"/>
  </p:sldIdLst>
  <p:extLst>
    <p:ext uri="{521415D9-36F7-43E2-AB2F-B90AF26B5E84}">
      <p14:sectionLst xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">
        <p14:section name="cover"   id="{GUID-1}">
          <p14:sldIdLst><p14:sldId id="256"/></p14:sldIdLst>
        </p14:section>
        <p14:section name="content" id="{GUID-2}">
          <p14:sldIdLst><p14:sldId id="257"/></p14:sldIdLst>
        </p14:section>
        <p14:section name="ending"  id="{GUID-3}">
          <p14:sldIdLst><p14:sldId id="258"/></p14:sldIdLst>
        </p14:section>
      </p14:sectionLst>
    </p:ext>
  </p:extLst>
</p:presentation>
```

解析接口：

```python
# @AI_GENERATED
from defusedxml.minidom import parse
from dataclasses import dataclass, field

SECTION_EXT_URI = "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}"
KNOWN_SECTIONS = ("cover", "content", "ending")

@dataclass
class SectionInfo:
    name: str                       # "cover" | "content" | "ending"
    section_id: str                 # section GUID
    slide_ids: list[str] = field(default_factory=list)  # 该节归组的 <p:sldId> id 列表

def parse_sections(presentation_xml_path: str) -> dict[str, SectionInfo]:
    """读取 presentation.xml 的 <p:sectionLst>，返回按名索引的具名节。
    要求返回值键集合 == {'cover','content','ending'}（ending 可能缺省时另行处理）。
    使用 defusedxml.minidom；缺失 cover/content 节时抛 SectionStructureError。
    Validates: R1.5
    """
    ...
# @AI_GENERATED: end
```

- 每个具名节通过其 `slide_ids` 关联到该节的模板 slide；该模板 slide 的 `slideLayout` 关系（`slideN.xml.rels` → `slideLayoutM.xml`）即为该节的**版式/样式来源（section style source）**。
- 若 `cover` 或 `content` 节缺失 → 抛错（属结构性缺陷，须先按 A3 重构母版）。`ending` 缺失是允许的（见 R3）。

#### 1.2 位置法角色识别（detect_roles）

```python
# @AI_GENERATED
from enum import Enum

class Role(str, Enum):
    COVER = "cover"
    CONTENT = "content"
    ENDING = "ending"

def detect_roles(page_count: int, ending_requested: bool) -> list[Role]:
    """位置法角色识别（Positional_Role_Detection）。
    - 第一张 → COVER
    - 首末之间每张 → CONTENT
    - 末张 → ENDING（当 ending_requested 且 page_count>=2）否则 CONTENT
    page_count==1 时仅 [COVER]。
    Validates: R2.1, R2.2, R2.3, R2.4, R3.1, R3.2
    """
    if page_count <= 0:
        return []
    roles = [Role.COVER]
    if page_count == 1:
        return roles
    middle = page_count - 2
    roles += [Role.CONTENT] * middle
    roles.append(Role.ENDING if ending_requested else Role.CONTENT)
    return roles
# @AI_GENERATED: end
```

算法说明（确定性）：

| 位置 | 条件 | 角色 |
|------|------|------|
| index == 0 | 恒定 | `cover` |
| 0 < index < last | 恒定 | `content` |
| index == last | `ending_requested == true` | `ending` |
| index == last | `ending_requested == false` | `content` |

- ending 节**可选且默认不启用**：`ending_requested` 默认 `False`（R3.1）；仅显式请求时末页为 `ending`（R3.2）。

#### 1.3 确定性绑定（bind）

```python
# @AI_GENERATED
FIXED_MAPPING = {Role.COVER: "cover", Role.CONTENT: "content", Role.ENDING: "ending"}

@dataclass
class BoundPage:
    index: int
    role: Role
    style_source: str      # 实际绑定到的 section 名（Style_Source）
    slide_file: str        # unpacked/ppt/slides/slideN.xml

def bind_pages(sequence: list[BoundPage],
               sections: dict[str, SectionInfo],
               ending_requested: bool) -> list[BoundPage]:
    """对生成序列执行角色识别 + 固定映射绑定。
    role→section 固定：cover→cover, content→content, ending→ending。
    所有 content 页共享同一 content 节样式来源（一致性）。
    绑定动作 = 将该页 slideN.xml 的 slideLayout 关系指向目标节模板 slide 的 layout，
    并复制该节模板 slide 的样式骨架（占位符结构/母版引用），随后回填真实内容。
    Validates: R1.1, R1.2, R1.3, R1.4
    """
    roles = detect_roles(len(sequence), ending_requested)
    for page, role in zip(sequence, roles):
        target_section = FIXED_MAPPING[role]
        page.role = role
        page.style_source = target_section   # 确定性：同角色恒绑同一节
        _apply_section_layout(page, sections[target_section])
    return sequence
# @AI_GENERATED: end
```

**绑定机制（binding mechanism）**：绑定不是"复制整页文本"，而是让生成页在样式维度锚定到目标节的模板 slide：

1. 将生成页 `slideN.xml` 的 `slideN.xml.rels` 中 `slideLayout` 关系指向**目标节模板 slide 所用的 layout**；
2. 以目标节模板 slide 为样式骨架（占位符 `<p:ph>` 结构、母版引用），保证 `Style_Source` 稳定；
3. 真实内容通过占位符填充回写（见回归组件 R6）。
4. 所有 `content` 页统一指向 content 节的同一 layout/样式来源，保证同类页样式一致（R1.4）。

### Component 2: `pre_delivery_gate.py`（出片前门槛）

位于 `deliverable-tools/pptx/scripts/pre_delivery_gate.py`。在 `pack.py` 之前运行（或作为 pack 的前置检查），聚合三项门槛，**任一失败即以非零退出并列出问题**，阻断出片成功声明。

#### 2.1 Traceability_Check（追溯校验，G1）

```python
# @AI_GENERATED
@dataclass
class TraceResult:
    passed: bool
    mismatches: list[tuple[int, Role, str, str]]  # (index, role, expected, actual)

def traceability_check(bound_pages: list[BoundPage]) -> TraceResult:
    """逐页判定 Style_Source == 该页 Role 对应的期望 Section。
    通过 iff 所有页匹配；任一不匹配 → passed=False 并记录不匹配页。
    Validates: R4.1, R4.2, R4.3
    """
    mismatches = []
    for p in bound_pages:
        expected = FIXED_MAPPING[p.role]
        if p.style_source != expected:
            mismatches.append((p.index, p.role, expected, p.style_source))
    return TraceResult(passed=len(mismatches) == 0, mismatches=mismatches)
# @AI_GENERATED: end
```

- 期望 Section 由 `FIXED_MAPPING[role]` 决定；实际 `Style_Source` 从成片各 `slideN.xml` 的 layout 关系反向解析回其所属节。
- **门槛语义**：`passed == (mismatches 为空)` —— 即 gate 通过当且仅当无错配页（R4.2/R4.3 合并语义）。

#### 2.2 Placeholder_Grep_Gate（残留占位符门槛，G2）

```python
# @AI_GENERATED
import re

PLACEHOLDER_PATTERNS = [
    r"xxxx", r"lorem", r"ipsum",
    r"this.*(page|slide).*layout",
    r"Cover Page Style",
]

def placeholder_grep_gate(deck_text: str) -> list[str]:
    """对成片提取文本（markitdown 输出）逐模式检查，返回命中的模式列表。
    命中任一 → gate 失败。含母版默认封面占位文字 'Cover Page Style'。
    Validates: R6.3, R9.1, R9.2
    """
    flags = re.IGNORECASE
    return [p for p in PLACEHOLDER_PATTERNS if re.search(p, deck_text, flags)]
# @AI_GENERATED: end
```

- 文本来源：`python -m markitdown output.pptx`（与现有 QA 门槛一致）。
- `Cover Page Style` 命中即代表封面占位符未填 → 与 R6.3 同源阻断。

#### 2.3 Value-Tree Node-ization Check（价值树节点化校验，G3）

```python
# @AI_GENERATED
@dataclass
class ValueTreeIssue:
    kind: str    # "flattened" | "missing_operator" | "missing_edge" | "multi_parent"
    detail: str

def value_tree_check(model) -> list[ValueTreeIssue]:
    """校验价值树/核心商业等式的节点化结构：
    - 等式每个变量为独立直角框，框间以运算符（×＋－÷＝）连接（非拍平文字）
    - 单父树：每个下层节点有且仅有一个父节点
    - 保留运算符与父子连接关系
    命中任一违规 → 返回非空 issues → gate 失败并要求返工重绘。
    Validates: R10.1, R10.2, R10.3, R10.4
    """
    ...
# @AI_GENERATED: end
```

#### 2.4 门槛聚合

```python
# @AI_GENERATED
@dataclass
class GateReport:
    passed: bool
    trace: TraceResult
    placeholder_hits: list[str]
    value_tree_issues: list[ValueTreeIssue]

def run_gate(bound_pages, deck_text, value_tree_model=None) -> GateReport:
    """聚合 G1/G2/G3。任一失败 → passed=False，阻断出片成功声明。
    Validates: R4.2, R6.3, R9.2, R10.4
    """
    trace = traceability_check(bound_pages)
    hits = placeholder_grep_gate(deck_text)
    issues = value_tree_check(value_tree_model) if value_tree_model else []
    passed = trace.passed and not hits and not issues
    return GateReport(passed, trace, hits, issues)
# @AI_GENERATED: end
```

### Component 3: 回归防护组件（保持既有强制行为）

这些行为在绑定/门槛引入后**必须保持不变**，通过在绑定阶段与门槛阶段固化：

- **封面占位符填充（R6）**：绑定 cover 节后，将真实客户名/项目标题/日期回填到 cover 版式自带 `<p:ph type="ctrTitle"/subTitle">` 占位符；**禁止**新建浮动文本框；残留 `Cover Page Style` 由 G2 拦截。
- **母版取色取字 + run 级中英分设（R7）**：颜色/字体仅从母版动态提取；对每个文本 run 按脚本分设——`<a:rPr>` 中中文用 `<a:ea typeface="母版CJK字体"/>`（如 Microsoft YaHei），拉丁用 `<a:latin typeface="母版拉丁字体"/>`，同段落内中/英 run 分别设置，避免中文回退到无字形拉丁字体。
- **直角框/固定版式（R8）**：所有框/节点/卡片用直角框（`<a:prstGeom prst="rect">`，禁止 `roundRect`）；roadmap/ontology 遵循 `ppt-deck-mapping` 固定版式规格。

### Component 4: Markdown 指引层更新（R5）

在既有 business-case 硬规则块基础上，追加/强化"角色→节确定性映射"硬规则，三处文件保持一致：

| 文件 | 更新内容 |
|------|----------|
| `deliverable-tools/pptx/pptx-tool.md` | 新增「模板节样式确定性绑定」硬规则块：固定映射表（cover→cover / content→content / ending→ending）、位置法（首=cover、中=content、末=ending 或 content）、ending 默认不启用；并在「残留占位符检查」门槛旁引用追溯校验为出片前强制门槛。 |
| `deliverable-tools/pptx/editing.md` | 在「Template-Based Workflow」步骤中插入：unpack 后须先读取 `presentation.xml` 具名节，编辑阶段按角色绑定到对应节；pack 前须过 Pre-Delivery Gate。 |
| business-case `SKILL.md` | 红线新增/强化：角色→节映射为硬红线；追溯校验失败即阻断出片成功声明。 |

指引文本以硬规则（"必须 / MANDATORY / 命中即阻断"）措辞编码，确保生成过程遵循确定性映射而非临场判断。Markdown 更新块统一用 `<!-- @AI_GENERATED -->` 标注。

---

## Data Models

数据模型

```python
# @AI_GENERATED
# 角色枚举
class Role(str, Enum):
    COVER = "cover"; CONTENT = "content"; ENDING = "ending"

# 具名节
@dataclass
class SectionInfo:
    name: str; section_id: str; slide_ids: list[str]

# 绑定后的页
@dataclass
class BoundPage:
    index: int
    role: Role
    style_source: str    # 实际绑定节名；期望值 = FIXED_MAPPING[role]
    slide_file: str

# 固定映射（Deterministic_Binding 的核心不变量）
FIXED_MAPPING = {Role.COVER: "cover", Role.CONTENT: "content", Role.ENDING: "ending"}
# @AI_GENERATED: end
```

**关键不变量**：对任意页 `p`，正确成片满足 `p.style_source == FIXED_MAPPING[p.role]`。这是追溯校验的判定核心，也是全部映射属性的收敛点。

---

## Error Handling

错误处理

| 场景 | 处理 |
|------|------|
| `presentation.xml` 缺 `<p:sectionLst>` 或缺 cover/content 节 | 抛 `SectionStructureError`，提示按 A3 重构母版为三节结构；阻断出片。 |
| ending 节缺失但未请求 ending | 正常（R3.1），末页判为 content。 |
| ending 节缺失但显式请求 ending | 抛错并提示母版需补 ending 节，或降级为 content（须在实现期与用户确认策略）。 |
| 追溯校验发现错配页 | Gate 失败，列出 `(index, role, expected, actual)`，阻断成功声明（R4.2）。 |
| grep 命中占位符 | Gate 失败，列出命中模式，要求回填清零后复检（R9.2）。 |
| 价值树节点化违规 | Gate 失败，标注违规类型，要求返工重绘（R10.4）。 |
| 使用 `xml.etree` 导致命名空间损坏 | 设计禁止；统一 `defusedxml.minidom`（A4）。 |

---

## Testing Strategy

测试策略

采用**双轨测试**：属性测试（property-based，覆盖全输入空间，≥100 次迭代）+ 示例/边界单元测试（具体场景、集成点、文档内容检查）。

- **属性测试**覆盖：角色识别、确定性绑定、追溯校验、grep 门槛、run 级字体分设、直角框不变量、价值树结构。每条属性测试标注 `Feature: pptx-template-section-styling, Property N: ...`，并引用对应设计属性。
- **示例/集成测试**覆盖：`parse_sections` 对代表性 `presentation.xml` 固件的解析（R1.5）、roadmap/ontology 固定版式规格（R8.2）、Markdown 指引硬规则文本存在性（R5.1–5.3，用 grep 断言）。
- XML 处理测试固件均以 `defusedxml.minidom` 解析，防止命名空间回归。

---

## Correctness Properties

正确性属性

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: 角色→节确定性映射（cover/content）

*For any* 生成序列与解析所得具名节，经绑定后，每张角色为 `cover` 的页其 `Style_Source` 恒等于 `cover` 节，每张角色为 `content` 的页其 `Style_Source` 恒等于 `content` 节。

**Validates: Requirements 1.1, 1.2**

### Property 2: content 页样式来源一致性

*For any* 含两张及以上 `content` 角色页的生成序列，所有 `content` 页绑定的 `Style_Source` 为同一个 content 节样式来源（彼此相等）。

**Validates: Requirements 1.4**

### Property 3: 具名节解析完整性

*For any* 含合法 `<p:sectionLst>` 的 `presentation.xml`，`parse_sections` 返回的节集合包含 `cover`、`content` 两节（且当存在时含 `ending`），每节关联其 `<p:sldId>` 分组；缺 cover/content 时报错。

**Validates: Requirements 1.5**

### Property 4: 位置法角色识别

*For any* 非空生成序列，位置法识别结果满足：首页为 `cover`；索引位于首末之间的每页为 `content`。

**Validates: Requirements 2.1, 2.2**

### Property 5: ending 可选性与末页角色

*For any* 生成序列（长度 ≥ 2）：当显式请求 ending 时末页角色为 `ending` 且绑定 ending 节样式；当未请求 ending 时末页角色为 `content` 且成片不含任何 `ending` 角色页。

**Validates: Requirements 2.3, 2.4, 3.1, 3.2, 1.3**

### Property 6: 追溯校验判定正确且门槛等价于无错配

*For any* 成片，追溯校验逐页判定 `Style_Source == FIXED_MAPPING[role]`，且门槛通过当且仅当不存在任何错配页；存在错配时门槛失败并标识全部不匹配页。

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 7: 封面占位符填充与母版占位符承载

*For any* 已绑定 cover 节的封面页与真实封面数据（客户名/项目标题/日期），生成后这些文本均位于 cover 版式自带的 `<p:ph>` 占位符内，且不产生无占位符的新建浮动文本框。

**Validates: Requirements 6.1, 6.2**

### Property 8: 残留占位符 grep 门槛

*For any* 成片文本，若其命中模式集合 `{xxxx, lorem, ipsum, this.*(page|slide).*layout, Cover Page Style}` 中任一项，则出片前门槛失败并阻断成功声明；无命中则该门槛通过。

**Validates: Requirements 9.1, 9.2, 6.3**

### Property 9: 母版取色取字与 run 级中英字体分设

*For any* 生成的文本 run，其颜色与字体取值均取自 Master_Template 提取集合；且在中英混排段落中，含 CJK 字符的 run 绑定母版 CJK 字体、拉丁 run 绑定母版拉丁字体（run 级分设）。

**Validates: Requirements 7.1, 7.2, 7.3**

### Property 10: 直角框不变量

*For any* 生成的框、节点或卡片，其几何为直角框（`prstGeom prst="rect"`），不存在圆角框（无 `roundRect` 或圆角 `adj`）。

**Validates: Requirements 8.1**

### Property 11: 价值树节点化结构保持

*For any* 价值树或核心商业等式模型，渲染结果中每个变量为独立直角框、框间以运算符连接，每个下层节点恰有一个父节点，且渲染后保留的运算符集合与父子边集合与输入模型一致。

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 12: 价值树违规阻断

*For any* 出现等式被拍平为纯文字、丢失运算符、丢失父子关系或非单父结构的价值树，出片前门槛失败并要求返工重绘。

**Validates: Requirements 10.4**
<!-- @AI_GENERATED: end -->

# @AI_GENERATED
"""Pre-Delivery Gate（出片前门槛）—— 聚合 G1/G2/G3 校验。

本模块负责在 pack.py 之前对成片执行强制门槛校验，任一失败即阻断出片成功声明。
当前实现：
  - G1 Traceability_Check（追溯校验，Task 6.1）：逐页判定
    style_source == FIXED_MAPPING[role]，记录不匹配页 (index, role, expected, actual)。
  - 成片 slideN.xml → 所属节 反解辅助（供实际成片校验用）：读取该页
    slideN.xml.rels 的 slideLayout 关系，将 layout 反解回其对应的具名节。

（G2 残留占位符门槛 / G3 价值树节点化校验将在后续任务实现。）

XML 读写统一使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。
"""

import os
import re
import sys
from dataclasses import dataclass

from defusedxml.minidom import parse

# 允许作为脚本从 scripts/ 目录直接导入同级 section_style_binder 模块（与既有测试一致）。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from section_style_binder import (  # noqa: E402
    FIXED_MAPPING,
    Role,
    _iter_elements,
    _local_name,
    _resolve_target,
    _slide_rels_path,
)

# OOXML 关系命名空间与 slideLayout 关系类型（与 section_style_binder 保持一致）。
_RELATIONSHIP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_SLIDE_LAYOUT_REL_TYPE = _RELATIONSHIP_NS + "/slideLayout"

# 母版事实（Master facts）：具名节模板 slide 所用 layout 序号 → 节名。
# cover 节模板使用 slideLayout1，content 节使用 slideLayout14，ending 节使用 slideLayout4。
LAYOUT_TO_SECTION = {
    1: "cover",
    14: "content",
    4: "ending",
}

# 从 slideLayout Target（如 "../slideLayouts/slideLayout14.xml"）中提取版式序号。
_LAYOUT_NUMBER_RE = re.compile(r"slideLayout(\d+)\.xml$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# G1: Traceability_Check（追溯校验）—— Task 6.1
# ---------------------------------------------------------------------------


@dataclass
class TraceResult:
    """追溯校验结果。

    - passed:     当且仅当不存在任何错配页时为 True。
    - mismatches: 错配页列表，每项为 (index, role, expected, actual)：
                  index    页在生成序列中的位置（0 基）；
                  role     该页角色（Role）；
                  expected 期望节名 = FIXED_MAPPING[role]；
                  actual   该页实际 style_source。
    """

    passed: bool
    mismatches: list[tuple[int, Role, str, str]]


def traceability_check(bound_pages) -> TraceResult:
    """逐页判定 Style_Source == 该页 Role 对应的期望 Section（FIXED_MAPPING[role]）。

    通过 iff 所有页匹配；任一不匹配 → passed=False 并记录全部不匹配页
    (index, role, expected, actual)。

    Validates: Requirements 4.1, 4.2, 4.3
    """
    mismatches: list[tuple[int, Role, str, str]] = []
    for page in bound_pages:
        expected = FIXED_MAPPING[page.role]
        if page.style_source != expected:
            mismatches.append((page.index, page.role, expected, page.style_source))
    return TraceResult(passed=len(mismatches) == 0, mismatches=mismatches)


# ---------------------------------------------------------------------------
# 成片 slideN.xml → 所属节 反解（供实际成片追溯校验用）
# ---------------------------------------------------------------------------


def _layout_target_in_slide_rels(slide_rels_path: str) -> str | None:
    """在某成片 slide 的 .rels 中找到 slideLayout 关系的 Target（相对，含 ../）。

    使用 defusedxml.minidom 解析；未找到关系或文件不存在时返回 None。
    """
    if not os.path.exists(slide_rels_path):
        return None
    document = parse(slide_rels_path)
    for element in _iter_elements(document):
        if _local_name(element) != "Relationship":
            continue
        if element.getAttribute("Type") == _SLIDE_LAYOUT_REL_TYPE:
            return element.getAttribute("Target")
    return None


def layout_number_from_target(layout_target: str) -> int | None:
    """从 slideLayout Target 路径提取版式序号（如 slideLayout14.xml → 14）。

    无法识别时返回 None。
    """
    if not layout_target:
        return None
    match = _LAYOUT_NUMBER_RE.search(layout_target)
    return int(match.group(1)) if match else None


def resolve_section_for_slide(slide_file: str) -> str | None:
    """反解成片某页 slideN.xml 所属的具名节（Style_Source 的实际反向读取）。

    路径链：slideN.xml → slideN.xml.rels 的 slideLayout 关系 Target
        → 版式序号 → LAYOUT_TO_SECTION 映射回节名。

    用于对实际成片执行 Traceability_Check：将反解所得节名作为该页的 actual
    style_source，与 FIXED_MAPPING[role] 期望值比对。

    全部 XML 读写使用 defusedxml.minidom。无法解析（缺 rels / 缺关系 / 未知
    layout）时返回 None。

    Validates: Requirements 4.1
    """
    layout_target = _layout_target_in_slide_rels(_slide_rels_path(slide_file))
    if layout_target is None:
        return None
    # 规范化以稳健地提取文件名（容忍不同相对路径写法）。
    normalized = _resolve_target(
        os.path.join(os.path.dirname(slide_file), "_rels"), layout_target
    )
    layout_number = layout_number_from_target(os.path.basename(normalized))
    if layout_number is None:
        return None
    return LAYOUT_TO_SECTION.get(layout_number)
# @AI_GENERATED: end


# @AI_GENERATED
# ---------------------------------------------------------------------------
# G2: Placeholder_Grep_Gate（残留占位符门槛）—— Task 6.3
# ---------------------------------------------------------------------------

# 残留占位符检测模式（re.IGNORECASE 逐模式匹配）。
# 文本来源约定：`python -m markitdown output.pptx`（与现有 QA 流程一致）。
PLACEHOLDER_PATTERNS = [
    r"xxxx",
    r"lorem",
    r"ipsum",
    r"this.*(page|slide).*layout",
    r"Cover Page Style",
]


def placeholder_grep_gate(deck_text: str) -> list[str]:
    """G2 残留占位符门槛：在成片正文文本中逐模式检查残留占位符。

    deck_text 约定来自 `python -m markitdown output.pptx` 的输出。逐一以
    re.IGNORECASE 检查 PLACEHOLDER_PATTERNS，返回命中的模式列表。

    返回空列表表示门槛通过（无残留占位符）；非空表示存在残留占位符，应阻断出片。

    Validates: Requirements 9.1, 9.2, 6.3
    """
    flags = re.IGNORECASE
    return [p for p in PLACEHOLDER_PATTERNS if re.search(p, deck_text, flags)]
# @AI_GENERATED: end


# @AI_GENERATED
# ---------------------------------------------------------------------------
# G3: Value-Tree Node-ization Check（价值树节点化校验）—— Task 6.5
# ---------------------------------------------------------------------------

# 合法运算符集合：等式各框之间以下述运算符连接（乘/加/减/除/等号，全角）。
VALUE_TREE_OPERATORS = {"×", "＋", "－", "÷", "＝"}


@dataclass
class ValueTreeIssue:
    """价值树/核心商业等式节点化违规。

    - kind:   违规类别，取值之一：
              "flattened"        等式被拍平为纯文字（无独立节点框）；
              "missing_operator" 期望运算符连接但运算符缺失；
              "missing_edge"     期望父子层级但父子边缺失；
              "multi_parent"     存在下层节点拥有多个不同父节点（非单父树）。
    - detail: 可读的违规说明（含定位信息，便于返工重绘）。
    """

    kind: str
    detail: str


@dataclass
class ValueTreeModel:
    """价值树/核心商业等式的节点化结构模型（供 G3 校验）。

    该模型是对成片中价值树/等式渲染结果的抽象事实，字段含义：
    - nodes:            节点 id 列表；每个变量应渲染为一个独立直角框，
                        故一个节点 == 一个框。
    - operators:        连接各框的运算符列表（应为 VALUE_TREE_OPERATORS 子集）。
    - edges:            父子层级边列表，每项为 (parent, child) 元组。
    - flattened_text:   当等式被渲染为纯文字（而非节点化直角框）时，
                        置为该纯文字；否则为空串。
    - expects_operators:该结构存在等式关系、需要运算符连接时为 True。
    - expects_edges:    该结构存在父子层级、需要父子边时为 True。
    """

    nodes: list = None
    operators: list = None
    edges: list = None
    flattened_text: str = ""
    expects_operators: bool = False
    expects_edges: bool = False

    def __post_init__(self):
        # 允许省略列表字段，规整为空列表以便确定性校验。
        if self.nodes is None:
            self.nodes = []
        if self.operators is None:
            self.operators = []
        if self.edges is None:
            self.edges = []


def build_value_tree_model(
    nodes=None,
    operators=None,
    edges=None,
    flattened_text="",
    expects_operators=False,
    expects_edges=False,
) -> ValueTreeModel:
    """构建 ValueTreeModel 的便捷工厂（关键字参数，便于测试构造各种场景）。"""
    return ValueTreeModel(
        nodes=list(nodes) if nodes else [],
        operators=list(operators) if operators else [],
        edges=list(edges) if edges else [],
        flattened_text=flattened_text or "",
        expects_operators=expects_operators,
        expects_edges=expects_edges,
    )


def value_tree_check(model) -> list[ValueTreeIssue]:
    """校验价值树/核心商业等式的节点化结构：
    - 等式每个变量为独立直角框，框间以运算符（×＋－÷＝）连接（非拍平文字）
    - 单父树：每个下层节点有且仅有一个父节点
    - 保留运算符与父子连接关系
    命中任一违规 → 返回非空 issues → gate 失败并要求返工重绘。

    检测规则（确定性，返回 issues 列表；空列表表示通过）：
    - "flattened":        flattened_text 非空且 nodes 为空（等式塌缩为纯文字）——R10.1。
    - "missing_operator": expects_operators 为 True 但 operators 为空——R10.1/R10.3。
    - "missing_edge":     expects_edges 为 True 但 edges 为空（父子关系丢失）——R10.2/R10.3。
    - "multi_parent":     任一 child 在 edges 中出现多于一个不同 parent——R10.2。

    Validates: Requirements 10.1, 10.2, 10.3, 10.4
    """
    issues: list[ValueTreeIssue] = []

    nodes = list(getattr(model, "nodes", []) or [])
    operators = list(getattr(model, "operators", []) or [])
    edges = list(getattr(model, "edges", []) or [])
    flattened_text = getattr(model, "flattened_text", "") or ""
    expects_operators = bool(getattr(model, "expects_operators", False))
    expects_edges = bool(getattr(model, "expects_edges", False))

    # R10.1：等式被拍平为纯文字（有纯文字但无任何节点框）。
    if flattened_text and not nodes:
        issues.append(
            ValueTreeIssue(
                kind="flattened",
                detail=f"等式被拍平为纯文字（无独立直角框）：{flattened_text!r}",
            )
        )

    # R10.1/R10.3：期望运算符连接但运算符缺失。
    if expects_operators and not operators:
        issues.append(
            ValueTreeIssue(
                kind="missing_operator",
                detail="等式期望以运算符（×＋－÷＝）连接各框，但未检测到任何运算符。",
            )
        )

    # R10.2/R10.3：期望父子层级但父子边缺失。
    if expects_edges and not edges:
        issues.append(
            ValueTreeIssue(
                kind="missing_edge",
                detail="价值树期望存在父子层级连接，但未检测到任何父子边。",
            )
        )

    # R10.2：单父树——任一 child 不得拥有多个不同 parent。
    parents_by_child: dict = {}
    for parent, child in edges:
        parents_by_child.setdefault(child, set()).add(parent)
    for child, parents in parents_by_child.items():
        if len(parents) > 1:
            sorted_parents = sorted(str(p) for p in parents)
            issues.append(
                ValueTreeIssue(
                    kind="multi_parent",
                    detail=(
                        f"节点 {child!r} 拥有多个父节点 {sorted_parents}，"
                        "违反单父树约束。"
                    ),
                )
            )

    return issues
# @AI_GENERATED: end


# @AI_GENERATED
# ---------------------------------------------------------------------------
# 门槛聚合：GateReport / run_gate（Task 6.8）
# ---------------------------------------------------------------------------
#
# run_gate() 是编程聚合 API：将 G1（追溯校验）、G2（残留占位符门槛）、
# G3（价值树节点化校验）合并为单一门槛判定，任一失败即 passed=False，
# 阻断出片成功声明。
#
# 运行时序：本门槛必须在 pack.py 之前运行（或作为 pack 的前置检查）。
# 只有 run_gate(...).passed 为 True 时，方可继续执行
#   pack.py --original template.pptx
# 打包出片；否则应阻断并按报告返工重绘。
#
# 文本来源约定：deck_text 来自 `python -m markitdown output.pptx`
# 抽取出的成片正文文本（与既有 QA 流程一致）。


@dataclass
class GateReport:
    """出片前门槛聚合报告。

    - passed:             当且仅当 G1/G2/G3 全部通过时为 True。
    - trace:              G1 追溯校验结果（TraceResult）。
    - placeholder_hits:   G2 命中的残留占位符模式列表（空表示通过）。
    - value_tree_issues:  G3 价值树节点化违规列表（空表示通过/跳过）。
    """

    passed: bool
    trace: TraceResult
    placeholder_hits: list[str]
    value_tree_issues: list[ValueTreeIssue]


def run_gate(bound_pages, deck_text, value_tree_model=None) -> GateReport:
    """聚合 G1/G2/G3 三项门槛，任一失败 → passed=False，阻断出片成功声明。

    - G1：traceability_check(bound_pages) —— 逐页 style_source 与 FIXED_MAPPING 一致性。
    - G2：placeholder_grep_gate(deck_text) —— 成片正文残留占位符检测。
    - G3：value_tree_check(value_tree_model) —— 价值树/等式节点化校验（可选，
          未提供 value_tree_model 时跳过，issues 视为空）。

    Validates: Requirements 4.2, 6.3, 9.2, 10.4
    """
    trace = traceability_check(bound_pages)
    hits = placeholder_grep_gate(deck_text)
    issues = value_tree_check(value_tree_model) if value_tree_model else []
    passed = trace.passed and not hits and not issues
    return GateReport(passed, trace, hits, issues)


def _format_gate_report(report: GateReport) -> str:
    """将 GateReport 渲染为可读的多行报告（用于 CLI 输出与返工定位）。"""
    lines: list[str] = []
    if report.passed:
        lines.append("Pre-Delivery Gate: PASSED —— 三项门槛均通过，可继续 pack.py 出片。")
        return "\n".join(lines)

    lines.append("Pre-Delivery Gate: FAILED —— 存在违规，阻断出片（请在 pack.py 之前修复）。")

    # G1 追溯校验：列出问题页。
    if not report.trace.passed:
        lines.append("")
        lines.append("[G1] 追溯校验失败——以下页的 style_source 与期望节不一致：")
        for index, role, expected, actual in report.trace.mismatches:
            role_name = getattr(role, "name", role)
            lines.append(
                f"  - page #{index} (role={role_name}): 期望节={expected!r}, "
                f"实际 style_source={actual!r}"
            )

    # G2 残留占位符门槛：列出命中模式。
    if report.placeholder_hits:
        lines.append("")
        lines.append("[G2] 残留占位符门槛失败——命中以下模式：")
        for pattern in report.placeholder_hits:
            lines.append(f"  - {pattern!r}")

    # G3 价值树节点化校验：列出违规。
    if report.value_tree_issues:
        lines.append("")
        lines.append("[G3] 价值树节点化校验失败——以下违规：")
        for issue in report.value_tree_issues:
            lines.append(f"  - [{issue.kind}] {issue.detail}")

    return "\n".join(lines)


def _main(argv=None) -> int:
    """CLI 入口：运行出片前门槛，失败时列出问题并以非零码退出，通过则退出 0。

    务实取舍（见任务说明）：bound_pages 从真实成片重建较为复杂，CLI 默认聚焦
    在对「markitdown 抽取文本文件」执行 G2 残留占位符门槛，并可选叠加 G1/G3：
      - --deck-text PATH   markitdown 抽取的成片正文文本文件（G2，必填）。
      - --trace-json PATH  可选：bound_pages 的 JSON 事实（G1）。数组，每项
                           {"index": int, "role": "COVER|...", "style_source": str}。
      - --value-tree-json  可选：ValueTreeModel 的 JSON 事实（G3）。

    run_gate() 仍是完整的编程聚合 API；CLI 是其务实的命令行封装。

    退出码：门槛通过 0；门槛失败 2；用法/输入错误 1。
    本门槛必须在 pack.py 之前运行。
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(
        prog="pre_delivery_gate",
        description=(
            "出片前门槛（G1 追溯 / G2 残留占位符 / G3 价值树节点化）。"
            "必须在 pack.py 之前运行；任一失败以非零码退出并列出问题。"
        ),
    )
    parser.add_argument(
        "--deck-text",
        required=True,
        help="markitdown 抽取的成片正文文本文件路径（`python -m markitdown output.pptx` 的输出）。",
    )
    parser.add_argument(
        "--trace-json",
        default=None,
        help="可选：bound_pages 事实的 JSON 文件（G1 追溯校验）。",
    )
    parser.add_argument(
        "--value-tree-json",
        default=None,
        help="可选：ValueTreeModel 事实的 JSON 文件（G3 价值树节点化校验）。",
    )
    args = parser.parse_args(argv)

    # 读取 G2 文本。
    try:
        with open(args.deck_text, encoding="utf-8") as handle:
            deck_text = handle.read()
    except OSError as error:
        print(f"error: 无法读取 --deck-text 文件：{error}", file=sys.stderr)
        return 1

    # 可选 G1：从 JSON 事实重建 bound_pages（轻量占位对象，具备 run_gate 所需字段）。
    bound_pages: list = []
    if args.trace_json:
        try:
            with open(args.trace_json, encoding="utf-8") as handle:
                raw_pages = json.load(handle)
            for item in raw_pages:
                role_value = item["role"]
                role = Role[role_value] if isinstance(role_value, str) else role_value
                bound_pages.append(
                    _CliBoundPage(
                        index=item["index"],
                        role=role,
                        style_source=item["style_source"],
                    )
                )
        except (OSError, KeyError, ValueError) as error:
            print(f"error: 无法解析 --trace-json：{error}", file=sys.stderr)
            return 1

    # 可选 G3：从 JSON 事实构建 ValueTreeModel。
    value_tree_model = None
    if args.value_tree_json:
        try:
            with open(args.value_tree_json, encoding="utf-8") as handle:
                raw_model = json.load(handle)
            value_tree_model = build_value_tree_model(
                nodes=raw_model.get("nodes"),
                operators=raw_model.get("operators"),
                edges=[tuple(edge) for edge in raw_model.get("edges", [])],
                flattened_text=raw_model.get("flattened_text", ""),
                expects_operators=raw_model.get("expects_operators", False),
                expects_edges=raw_model.get("expects_edges", False),
            )
        except (OSError, ValueError) as error:
            print(f"error: 无法解析 --value-tree-json：{error}", file=sys.stderr)
            return 1

    report = run_gate(bound_pages, deck_text, value_tree_model)
    stream = sys.stdout if report.passed else sys.stderr
    print(_format_gate_report(report), file=stream)
    return 0 if report.passed else 2


@dataclass
class _CliBoundPage:
    """CLI 从 JSON 事实重建的轻量 bound page（仅含 run_gate/G1 所需字段）。"""

    index: int
    role: Role
    style_source: str


if __name__ == "__main__":
    raise SystemExit(_main())
# @AI_GENERATED: end

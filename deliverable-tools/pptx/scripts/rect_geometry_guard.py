# @AI_GENERATED
"""Right-angle box invariant + fixed-layout spec guard（直角框与固定版式固化）。

Task 8.5：固化直角框与固定版式（回归防护 · design.md Component 3 / R8）。
本模块负责两组不变量，供 Task 8.6（直角框属性测试）与 Task 8.7（固定版式示例测试）断言：

1. 直角框不变量（R8.1）—— 所有框/节点/卡片必须使用 ``<a:prstGeom prst="rect">``，
   禁止 ``roundRect`` 圆角族及带非零圆角 ``adj`` 的矩形：
     - ``rect_prst_geom_xml``  —— 返回全 deck 框/节点/卡片统一使用的直角框几何片段。
     - ``find_rounded_geoms``  —— 解析 slideN.xml，返回违规的圆角 prst 值列表
       （空列表 == 合规）。
     - ``is_all_right_angle``  —— 是否已全直角（委托 ``find_rounded_geoms``）。
     - ``enforce_rect_geom``   —— 将圆角几何重写为 ``rect`` 并移除圆角 adj，返回改写数量。

2. 固定版式规格校验（R8.2）—— roadmap/ontology 页遵循 ``ppt-deck-mapping`` 固定版式：
     - ``FIXED_LAYOUT_SPECS`` —— 固定版式期望（引用 ppt-deck-mapping 文档规格）。
     - ``check_fixed_layout`` —— 校验 roadmap（四阶段）/ ontology（四层横向架构）
       是否符合固定规格，返回违规描述字符串列表（空列表表示合规）。

XML 读写统一使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。

===========================================================================
圆角几何“违规集合”定义（treated as violations of the right-angle invariant）
===========================================================================
以下 OOXML preset geometry（``<a:prstGeom prst="...">``）被视为圆角违规，一律须
重写为 ``rect``（核心聚焦 roundRect 圆角族：no roundRect, no rounded adj）：

  - roundRect        圆角矩形（最常见的圆角框）
  - round1Rect       单角圆角矩形
  - round2SameRect   同侧两角圆角矩形
  - round2DiagRect   对角两角圆角矩形

此外，以 "round" 前缀开头的任何矩形 preset 亦按前缀兜底判为违规（覆盖未来可能新增的
圆角矩形变体）；另外，rect 族 prstGeom 若携带非零圆角 adj（``<a:avLst><a:gd .../>``）
亦判为违规——这两类都被 ``find_rounded_geoms`` 收集。

===========================================================================
fixed-layout 规格来源：workflows/business-pain-point/standards/ppt-deck-mapping.md
===========================================================================
  - P(11+N) 实施路径（Roadmap）：**固定四阶段**（需求摸排 → 数据汇聚与本体 →
    高价值场景上线 → 稳定运营与复制），每阶段 **4-5 条关键动作**。
  - P(10+N) 技术架构（Ontology）：**横向分层架构图，自下而上四层**
    （数据来源 / Ontology 本体 / Agent Skill / Agent 行动主体）；
    其中 Ontology 本体层 **三框必出**（语义关联本体层 / 态势感知本体层 / 仿真决策本体层）。
"""

from dataclasses import dataclass, field

from defusedxml.minidom import parse

# ---------------------------------------------------------------------------
# 常量：几何与圆角判定（R8.1）
# ---------------------------------------------------------------------------

# 直角框唯一合法几何：<a:prstGeom prst="rect">。
RECT_GEOMETRY = "rect"

# 全 deck 框/节点/卡片统一使用的直角框几何片段（canonical snippet）。
RECT_PRST_GEOM_XML = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'

# 圆角矩形几何（roundRect 圆角族，prst 显式为圆角形态）。
ROUNDED_RECT_GEOMETRIES = (
    "roundRect",
    "round1Rect",
    "round2SameRect",
    "round2DiagRect",
)

# 判定为“非直角/圆角”的几何全集（违规集合，聚焦 roundRect 族）。
ROUNDED_GEOMETRIES = frozenset(ROUNDED_RECT_GEOMETRIES)

# rect 族 preset（携带非零圆角 adj 时视为违规）。
RECT_FAMILY_GEOMETRIES = frozenset({RECT_GEOMETRY})


def rect_prst_geom_xml() -> str:
    """返回全 deck 框/节点/卡片统一使用的直角框几何片段（canonical snippet）。

    即 ``<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>``——MBB 风格直角框，
    无圆角 adjust。所有生成的框/节点/卡片几何应以此为准（R8.1）。

    Validates: Requirements 8.1
    """
    return RECT_PRST_GEOM_XML


def _is_rounded_prst(prst: str) -> bool:
    """判断某 prst 值是否为圆角矩形几何（非直角框）。

    显式命中 ``ROUNDED_GEOMETRIES``，或以 "round" 前缀开头的矩形几何（前缀兜底，
    覆盖未来新增的圆角矩形变体），均视为圆角。
    """
    if not prst:
        return False
    if prst in ROUNDED_GEOMETRIES:
        return True
    return prst.lower().startswith("round")


# ---------------------------------------------------------------------------
# minidom 遍历辅助（命名空间无关，兼容不同前缀写法）
# ---------------------------------------------------------------------------


def _iter_elements(node):
    """深度优先遍历 node 下所有 Element 子节点（含后代）。"""
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            yield child
            yield from _iter_elements(child)


def _local_name(element) -> str:
    """返回元素的本地名（去掉命名空间前缀）。"""
    if element.localName:
        return element.localName
    tag = element.tagName
    return tag.split(":", 1)[1] if ":" in tag else tag


def _load_document(slide_xml_path_or_document):
    """接受 slide xml 文件路径（str）或已解析的 minidom 节点，统一返回可遍历节点。

    使用 defusedxml.minidom 解析路径；已解析节点（含 nodeType 属性）原样返回。
    """
    if isinstance(slide_xml_path_or_document, str):
        return parse(slide_xml_path_or_document)
    if hasattr(slide_xml_path_or_document, "nodeType"):
        return slide_xml_path_or_document
    raise TypeError(
        "slide_xml_path 须为文件路径 str 或 minidom 节点，"
        f"实际为 {type(slide_xml_path_or_document)!r}"
    )


def _iter_prstgeom(document):
    """遍历文档中所有 <a:prstGeom> 元素。"""
    for element in _iter_elements(document):
        if _local_name(element) == "prstGeom":
            yield element


def _rounding_gd_count(prstgeom_element) -> int:
    """返回某 <a:prstGeom> 内 <a:avLst> 下非零圆角 adj（<a:gd>）的数量。

    OOXML 中 rect 族的圆角以 ``<a:avLst><a:gd name="adj" fmla="val N"/></a:avLst>``
    表达，N>0 即有圆角。空 fmla / val 0 视为无圆角（不计入）。
    """
    count = 0
    for descendant in _iter_elements(prstgeom_element):
        if _local_name(descendant) != "gd":
            continue
        fmla = descendant.getAttribute("fmla") or ""
        # 形如 "val 12500"；取末段数字，>0 即计为圆角 adj。
        parts = fmla.replace("val", " ").split()
        value = 0
        for token in parts:
            try:
                value = int(token)
                break
            except ValueError:
                continue
        if value > 0:
            count += 1
        elif not parts:
            # 无 fmla 的裸 <a:gd>（罕见）保守计为圆角 adj。
            count += 1
    return count


# ---------------------------------------------------------------------------
# 直角框不变量（R8.1）
# ---------------------------------------------------------------------------


def find_rounded_geoms(slide_xml_path) -> list[str]:
    """解析 slideN.xml，返回违反直角框不变量的圆角 prst 值列表（保序）。

    收集两类违规（空列表 == 合规）：
      - prst 为圆角矩形（roundRect / round1Rect / round2SameRect / round2DiagRect，
        或 "round" 前缀兜底）。
      - prst 为 rect 族但携带非零圆角 adj（``<a:avLst><a:gd fmla="val N"/>``，N>0）；
        此类以 ``"rect(adj)"`` 记入返回列表，指明是带圆角 adj 的 rect。

    slide_xml_path 可为 slide xml 文件路径（str）或已解析的 minidom 节点。

    Validates: Requirements 8.1
    """
    document = _load_document(slide_xml_path)
    rounded: list[str] = []
    for element in _iter_prstgeom(document):
        prst = element.getAttribute("prst")
        if _is_rounded_prst(prst):
            rounded.append(prst)
        elif prst in RECT_FAMILY_GEOMETRIES and _rounding_gd_count(element) > 0:
            # rect 上残留非零圆角 adj，暗示圆角，记为违规。
            rounded.append(f"{prst}(adj)")
    return rounded


def is_all_right_angle(slide_xml_path) -> bool:
    """当 slide 内不存在任何圆角框时返回 True（委托 ``find_rounded_geoms``）。

    True iff ``find_rounded_geoms`` 返回空列表——即所有框/节点/卡片均为直角
    ``prstGeom prst="rect"`` 且无非零圆角 adj。

    Validates: Requirements 8.1
    """
    return not find_rounded_geoms(slide_xml_path)


@dataclass
class RectEnforceReport:
    """``enforce_rect_geom`` 的详细执行报告（返回值主结果为 changed 计数 int）。

    - rounded_found:    被判为圆角并改写的原 prst 值列表（保序，便于审计）。
    - converted:        由圆角几何改写为 "rect" 的 <a:prstGeom> 数量。
    - adjusts_removed:  被移除的圆角 adjust（<a:gd>）数量。
    - shapes_checked:   检查过的 <a:prstGeom> 总数。
    - all_rect:         处理后是否已全直角（无任一圆角框/圆角 adjust）。
    - path:             被处理的 slide xml 路径。
    """

    rounded_found: list[str] = field(default_factory=list)
    converted: int = 0
    adjusts_removed: int = 0
    shapes_checked: int = 0
    all_rect: bool = True
    path: str = ""


def enforce_rect_geom(slide_xml_path: str, *, report: bool = False):
    """将 slide 内所有圆角几何重写为直角框，移除圆角 adj，并回写文件。

    对每个圆角 <a:prstGeom>：把 prst 改为 "rect"，并删除其 <a:avLst>（圆角 adjust
    容器，连同 <a:gd> 子节点）；对已是 "rect" 但残留非零圆角 adj 的 prstGeom 也剥离其
    <a:avLst>，以彻底硬化直角框不变量（R8.1）。

    默认返回**改写数量**（int）——被转成直角框的圆角 prstGeom 数（roundRect→rect）；
    ``report=True`` 时返回 :class:`RectEnforceReport`（含移除 adj 数等审计信息）。
    仅当发生改动时才回写文件（幂等：对已全直角的 slide 不写盘）。使用 defusedxml.minidom。

    Validates: Requirements 8.1
    """
    document = parse(slide_xml_path)
    rep = RectEnforceReport(path=slide_xml_path)
    changed = False

    for element in _iter_prstgeom(document):
        rep.shapes_checked += 1
        prst = element.getAttribute("prst")
        is_rounded = _is_rounded_prst(prst)
        rounding_adj = _rounding_gd_count(element) if prst in RECT_FAMILY_GEOMETRIES else 0

        if is_rounded:
            rep.rounded_found.append(prst)
            rep.converted += 1
            element.setAttribute("prst", RECT_GEOMETRY)
            changed = True

        # 移除圆角 adjust：圆角几何一律剥离；rect 上残留的非零圆角 adj 亦剥离。
        if is_rounded or rounding_adj > 0:
            if prst in RECT_FAMILY_GEOMETRIES and rounding_adj > 0 and not is_rounded:
                rep.rounded_found.append(f"{prst}(adj)")
            for child in list(element.childNodes):
                if child.nodeType == child.ELEMENT_NODE and _local_name(child) == "avLst":
                    removed = sum(
                        1
                        for descendant in _iter_elements(child)
                        if _local_name(descendant) == "gd"
                    )
                    element.removeChild(child)
                    rep.adjusts_removed += removed
                    if removed:
                        changed = True

    if changed:
        with open(slide_xml_path, "wb") as handle:
            handle.write(document.toxml(encoding="UTF-8"))

    # 以处理后的内存文档复检，确定是否已彻底直角化。
    rep.all_rect = not find_rounded_geoms(document)
    return rep if report else rep.converted


# ---------------------------------------------------------------------------
# 常量：固定版式规格（R8.2，来源 ppt-deck-mapping.md）
# ---------------------------------------------------------------------------

# 固定版式规格来源文档（引用 ppt-deck-mapping）。
FIXED_LAYOUT_SOURCE = (
    "workflows/business-pain-point/standards/ppt-deck-mapping.md"
)

# 实施路径（Roadmap）P(11+N)：固定四阶段。
ROADMAP_PHASES = 4
ROADMAP_PHASE_NAMES = (
    "需求摸排",
    "数据汇聚与本体",
    "高价值场景上线",
    "稳定运营与复制",
)
# 每阶段关键动作数量区间（强制：4-5 条）。
ROADMAP_ACTIONS_MIN = 4
ROADMAP_ACTIONS_MAX = 5

# 技术架构（Ontology）P(10+N)：横向分层架构，自下而上四层。
ONTOLOGY_LAYERS = 4
ONTOLOGY_LAYER_NAMES = (
    "数据来源",       # 第 1 层（底）
    "Ontology 本体",  # 第 2 层
    "Agent Skill",    # 第 3 层
    "Agent 行动主体",  # 第 4 层（顶）
)
# Ontology 本体层三框必出。
ONTOLOGY_BODY_BOXES = 3
ONTOLOGY_BODY_BOX_NAMES = (
    "语义关联本体层",
    "态势感知本体层",
    "仿真决策本体层",
)

# check_fixed_layout 支持的固定版式页类型。
FIXED_LAYOUT_PAGE_KINDS = ("roadmap", "ontology")

# 固定版式期望规格（deterministic，引用 ppt-deck-mapping；示例断言见 Task 8.7）。
FIXED_LAYOUT_SPECS = {
    "roadmap": {
        "source": f"{FIXED_LAYOUT_SOURCE} · P(11+N) 实施路径",
        "description": (
            "固定四阶段时间轴（需求摸排 → 数据汇聚与本体 → 高价值场景上线 → "
            "稳定运营与复制），每阶段 4-5 条关键动作，节点化时间轴连接、绝对日期。"
        ),
        "phases": ROADMAP_PHASES,
        "phase_names": ROADMAP_PHASE_NAMES,
        "actions_per_phase": (ROADMAP_ACTIONS_MIN, ROADMAP_ACTIONS_MAX),
    },
    "ontology": {
        "source": f"{FIXED_LAYOUT_SOURCE} · P(10+N) 技术架构",
        "description": (
            "横向分层架构图，自下而上四层（数据来源 / Ontology 本体 / Agent Skill / "
            "Agent 行动主体）；Ontology 本体层三框必出（语义关联 / 态势感知 / 仿真决策）；"
            "MBB 风格直角框，禁止圆角框。"
        ),
        "layers": ONTOLOGY_LAYERS,
        "layer_names": ONTOLOGY_LAYER_NAMES,
        "body_boxes": ONTOLOGY_BODY_BOXES,
        "body_box_names": ONTOLOGY_BODY_BOX_NAMES,
    },
}


def _get(model, key, default=None):
    """从 dict 或带属性对象中取值，兼容两种模型表示。"""
    if isinstance(model, dict):
        return model.get(key, default)
    return getattr(model, key, default)


def _check_roadmap(model) -> list[str]:
    """校验 roadmap 模型：固定四阶段，每阶段 4-5 条关键动作。返回违规描述列表。"""
    issues: list[str] = []
    phases = _get(model, "phases")
    if phases is None:
        return ["roadmap 模型缺少 phases 字段"]

    if len(phases) != ROADMAP_PHASES:
        issues.append(
            f"roadmap 须为固定 {ROADMAP_PHASES} 阶段，实际 {len(phases)} 阶段"
        )

    for index, phase in enumerate(phases):
        actions = _get(phase, "actions")
        if actions is None:
            continue  # 动作列表可选：未提供则不校验密度。
        count = len(actions)
        if not (ROADMAP_ACTIONS_MIN <= count <= ROADMAP_ACTIONS_MAX):
            name = _get(phase, "name", f"#{index}")
            issues.append(
                f"roadmap 阶段「{name}」须含 "
                f"{ROADMAP_ACTIONS_MIN}-{ROADMAP_ACTIONS_MAX} 条关键动作，"
                f"实际 {count} 条"
            )
    return issues


def _check_ontology(model) -> list[str]:
    """校验 ontology 模型：自下而上四层横向架构，本体层三框必出。返回违规描述列表。"""
    issues: list[str] = []
    layers = _get(model, "layers")
    if layers is None:
        return ["ontology 模型缺少 layers 字段"]

    if len(layers) != ONTOLOGY_LAYERS:
        issues.append(
            f"ontology 须为固定 {ONTOLOGY_LAYERS} 层横向架构，实际 {len(layers)} 层"
        )

    # 本体层三框必出：优先从名为 "Ontology 本体" 的层读取 boxes，
    # 否则回退到模型顶层 ontology_body_boxes 字段。
    body_boxes = None
    for layer in layers:
        if _get(layer, "name") == "Ontology 本体":
            body_boxes = _get(layer, "boxes")
            break
    if body_boxes is None:
        body_boxes = _get(model, "ontology_body_boxes")

    if body_boxes is not None and len(body_boxes) != ONTOLOGY_BODY_BOXES:
        issues.append(
            f"ontology 本体层须为 {ONTOLOGY_BODY_BOXES} 框必出，"
            f"实际 {len(body_boxes)} 框"
        )
    return issues


def check_fixed_layout(page_kind: str, model) -> list[str]:
    """校验 roadmap/ontology 页是否遵循 ``ppt-deck-mapping`` 固定版式规格。

    - page_kind == "roadmap"：固定四阶段（ROADMAP_PHASES），每阶段
      ROADMAP_ACTIONS_MIN-ROADMAP_ACTIONS_MAX 条关键动作。
    - page_kind == "ontology"：自下而上四层横向架构（ONTOLOGY_LAYERS），
      本体层三框必出（ONTOLOGY_BODY_BOXES）。

    model 可为 dict 或带同名属性的对象（保持简单，便于 Task 8.7 写示例测试）。
    返回违规描述字符串列表（空列表表示符合规格）。确定性、无副作用。

    Validates: Requirements 8.2
    """
    kind = (page_kind or "").strip().lower()
    if kind == "roadmap":
        return _check_roadmap(model)
    if kind == "ontology":
        return _check_ontology(model)
    return [f"未知固定版式页类型 {page_kind!r}；支持 {FIXED_LAYOUT_PAGE_KINDS}"]
# @AI_GENERATED: end

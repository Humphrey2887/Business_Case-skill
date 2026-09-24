# @AI_GENERATED
"""Cover placeholder filling for the envision PPTX master template (Task 8.1).

封面占位符填充（回归防护 R6.1 / R6.2）。本模块在 cover 节绑定完成后，把真实的
客户名 / 项目标题 / 日期回填到 cover 版式自带的占位符 `<p:ph>`（`ctrTitle`/`title`、
`subTitle`、`dt`）承载的 run 文本 `<a:t>` 中。

核心硬约束（Requirement 6.1 / 6.2 / Property 7）：
  - **只写入已存在的占位符形状**（`<p:sp>` 且其 `<p:nvSpPr>/<p:nvPr>/<p:ph>` 存在）；
  - **禁止新建浮动文本框**（不新增任何 `<p:sp>`）；
  - 残留母版默认占位文字（如 `Cover Page Style`）由 pre_delivery_gate 的 G2 grep 门槛拦截。

XML 读写统一使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。

本模块设计为纯净、可测试的 API：task 8.2 将据此断言 Property 7
（封面文本均位于 `<p:ph>` 占位符内，未引入无占位符的浮动文本框）。
"""

from dataclasses import dataclass, field

from defusedxml.minidom import parse

# ---------------------------------------------------------------------------
# 占位符类型常量（module-level constants）
#
# OOXML `<p:ph type="...">` 取值参见 ISO/IEC 29500 pml.xsd（title/body/ctrTitle/
# subTitle/dt/...）。母版 cover 版式可能使用 ctrTitle 或退化为普通 title 承载主标题，
# 因此主标题槽同时接受 ctrTitle 与 title。
# ---------------------------------------------------------------------------

# 主标题槽（承载项目标题 project_title）：优先 ctrTitle，其次 title。
CTR_TITLE_PH_TYPES = ("ctrTitle", "title")
# 副标题槽（承载客户名 client_name）。
SUBTITLE_PH_TYPES = ("subTitle",)
# 日期槽（承载日期 date）。
DATE_PH_TYPES = ("dt",)

# 逻辑字段名（FillReport 使用的稳定键）。
FIELD_PROJECT_TITLE = "project_title"
FIELD_CLIENT_NAME = "client_name"
FIELD_DATE = "date"


@dataclass
class ShapeText:
    """封面某个形状（`<p:sp>`）的文本承载信息。

    - ph_type:  占位符类型（`<p:ph>` 的 type 属性）；无 type 属性的占位符按 OOXML
                默认视为 "body"；非占位符形状为 None。
    - has_ph:   该形状是否含 `<p:ph>` 祖先（True=占位符形状；False=浮动文本框）。
    - text:     该形状 `<a:t>` 拼接出的可见文本（去除首尾空白后用于判定是否承载文本）。
    """

    ph_type: str | None
    has_ph: bool
    text: str


@dataclass
class FillReport:
    """fill_cover_placeholders 的回填结果报告。

    - filled:            成功回填的 {逻辑字段名: 命中的占位符类型}。
    - unfilled:          因无匹配的已存在占位符而未回填的逻辑字段名列表。
    - created_text_box:  是否新建了浮动文本框 —— 恒为 False（本模块的硬不变量）。
    """

    filled: dict[str, str] = field(default_factory=dict)
    unfilled: list[str] = field(default_factory=list)
    created_text_box: bool = False


# ---------------------------------------------------------------------------
# minidom 遍历辅助
# ---------------------------------------------------------------------------


def _iter_elements(node):
    """深度优先遍历 node 下所有 Element 子节点（含后代）。"""
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            yield child
            yield from _iter_elements(child)


def _local_name(element) -> str:
    """返回元素本地名（去命名空间前缀），兼容不同前缀写法。"""
    if element.localName:
        return element.localName
    tag = element.tagName
    return tag.split(":", 1)[1] if ":" in tag else tag


def _first_descendant(node, local_name):
    """返回 node 下首个本地名为 local_name 的后代元素，无则 None。"""
    for element in _iter_elements(node):
        if _local_name(element) == local_name:
            return element
    return None


def _iter_sp(document):
    """遍历文档中的所有 `<p:sp>`（形状）元素。"""
    for element in _iter_elements(document):
        if _local_name(element) == "sp":
            yield element


def _ph_type_of(sp):
    """返回该 `<p:sp>` 内 `<p:ph>` 的 type；有 ph 但无 type 属性返回 "body"；无 ph 返回 None。"""
    ph = _first_descendant(sp, "ph")
    if ph is None:
        return None
    ph_type = ph.getAttribute("type")
    return ph_type if ph_type else "body"


def _text_of_sp(sp) -> str:
    """拼接该形状全部 `<a:t>` 的文本。"""
    parts = []
    for element in _iter_elements(sp):
        if _local_name(element) != "t":
            continue
        for child in element.childNodes:
            if child.nodeType == child.TEXT_NODE:
                parts.append(child.data)
    return "".join(parts)


# ---------------------------------------------------------------------------
# 内省 / 校验 API（供 task 8.2 断言 Property 7）
# ---------------------------------------------------------------------------


def list_text_shapes(cover_slide_xml_path: str) -> list[ShapeText]:
    """返回封面 slide 中所有形状的文本承载信息（含是否为占位符）。

    供 task 8.2 断言 Property 7：所有承载文本的形状均应有 `<p:ph>` 祖先，
    即不存在无占位符的浮动文本框。

    使用 defusedxml.minidom 解析。
    """
    document = parse(cover_slide_xml_path)
    shapes: list[ShapeText] = []
    for sp in _iter_sp(document):
        ph_type = _ph_type_of(sp)
        shapes.append(
            ShapeText(
                ph_type=ph_type,
                has_ph=ph_type is not None,
                text=_text_of_sp(sp),
            )
        )
    return shapes


def cover_text_is_placeholder_borne(cover_slide_xml_path: str) -> bool:
    """判定封面所有可见文本是否均由占位符（`<p:ph>`）承载。

    返回 True 当且仅当：每个承载非空文本的形状都含 `<p:ph>` 祖先
    （不存在无占位符的浮动文本框）。空封面（无任何文本形状）视为 True。

    Validates: Requirements 6.2 (Property 7)
    """
    for shape in list_text_shapes(cover_slide_xml_path):
        if shape.text.strip() and not shape.has_ph:
            return False
    return True


# ---------------------------------------------------------------------------
# 回填实现
# ---------------------------------------------------------------------------


def _set_run_text(text_element, document, value: str) -> None:
    """将 `<a:t>` 元素的文本内容替换为 value（清空原有子节点后写入单个文本节点）。"""
    while text_element.firstChild is not None:
        text_element.removeChild(text_element.firstChild)
    text_element.appendChild(document.createTextNode(value))


def _write_text_into_placeholder(sp, document, value: str) -> None:
    """把 value 写入某占位符形状 `<p:sp>` 的 run 文本。

    仅在**已存在**的占位符形状内部操作，不新增任何 `<p:sp>`（不新建浮动文本框）：
      - 若形状已有 `<a:t>`：将首个 `<a:t>` 设为 value，其余 `<a:t>` 清空（消除残留占位文字）。
      - 若有 `<a:p>` 但无 `<a:t>`：在首个 `<a:p>` 内追加 `<a:r><a:t>value</a:t></a:r>`。
      - 若 txBody 存在但无 `<a:p>`：追加 `<a:p><a:r><a:t>value</a:t></a:r></a:p>`。
      - 若无 `<p:txBody>`：在形状内创建 `<p:txBody>` 并写入段落/run/文本。

    以上均为在既有占位符形状内部补齐 run/文本，不构成“新建文本框”。
    """
    txbody = _first_descendant(sp, "txBody")
    if txbody is None:
        txbody = document.createElement("p:txBody")
        txbody.appendChild(document.createElement("a:bodyPr"))
        txbody.appendChild(document.createElement("a:lstStyle"))
        sp.appendChild(txbody)

    text_elements = [
        element for element in _iter_elements(txbody) if _local_name(element) == "t"
    ]
    if text_elements:
        _set_run_text(text_elements[0], document, value)
        for extra in text_elements[1:]:
            _set_run_text(extra, document, "")
        return

    run = document.createElement("a:r")
    text_element = document.createElement("a:t")
    _set_run_text(text_element, document, value)
    run.appendChild(text_element)

    paragraph = _first_descendant(txbody, "p")
    if paragraph is None:
        paragraph = document.createElement("a:p")
        txbody.appendChild(paragraph)
    paragraph.appendChild(run)


def find_placeholder_shapes(slide_document) -> dict:
    """返回封面 slide 中所有占位符形状，按 `<p:ph>` type 索引。

    - 键为占位符类型（`<p:ph type="...">`；无 type 属性的占位符按 OOXML 默认视为
      "body"）；值为对应的 `<p:sp>` Element。
    - 仅收录**占位符形状**（含 `<p:ph>` 祖先）；无占位符的浮动文本框被排除。
    - 同一 type 出现多次时保留**首个**出现的形状（保序、稳定）。

    参数 slide_document 为 defusedxml.minidom 解析所得 Document（或任意可遍历的
    Element 根节点）。供 fill_cover_placeholders 与 task 8.2 复用。
    """
    shapes: dict = {}
    for sp in _iter_sp(slide_document):
        ph_type = _ph_type_of(sp)
        if ph_type is None:
            continue  # 非占位符形状（浮动文本框）—— 不收录。
        shapes.setdefault(ph_type, sp)
    return shapes


def _find_placeholder_shape(document, accepted_types, used_ids):
    """返回首个类型在 accepted_types 且尚未被占用的占位符形状 `<p:sp>`，无则 None。

    used_ids 以形状的 python id() 记录已被本次回填占用的形状，避免多字段写入同一占位符。
    accepted_types 顺序即优先级（例如主标题优先匹配 ctrTitle，其次 title）。
    """
    placeholders = find_placeholder_shapes(document)
    for accepted in accepted_types:
        sp = placeholders.get(accepted)
        if sp is not None and id(sp) not in used_ids:
            return sp
    return None


def fill_cover_placeholders(
    cover_slide_xml_path: str,
    *,
    client_name: str,
    project_title: str,
    date: str,
) -> FillReport:
    """把真实客户名 / 项目标题 / 日期回填到 cover 版式自带占位符，并回写 slide XML。

    字段→占位符映射（module-level constants）：
      - project_title → CTR_TITLE_PH_TYPES (ctrTitle 优先，title 退化)
      - client_name   → SUBTITLE_PH_TYPES  (subTitle)
      - date          → DATE_PH_TYPES       (dt)

    仅写入**已存在**的占位符形状；某字段无匹配占位符时记入 report.unfilled 且
    **不**新建浮动文本框（created_text_box 恒为 False）。写入后以 defusedxml.minidom
    回写文件（UTF-8）。

    Validates: Requirements 6.1, 6.2 (Property 7)
    """
    document = parse(cover_slide_xml_path)
    report = FillReport()
    used_ids: set[int] = set()

    # (逻辑字段名, 值, 接受的占位符类型集合)——顺序决定占用优先级。
    plan = [
        (FIELD_PROJECT_TITLE, project_title, CTR_TITLE_PH_TYPES),
        (FIELD_CLIENT_NAME, client_name, SUBTITLE_PH_TYPES),
        (FIELD_DATE, date, DATE_PH_TYPES),
    ]

    changed = False
    for field_name, value, accepted_types in plan:
        sp = _find_placeholder_shape(document, accepted_types, used_ids)
        if sp is None:
            report.unfilled.append(field_name)
            continue
        used_ids.add(id(sp))
        _write_text_into_placeholder(sp, document, value)
        report.filled[field_name] = _ph_type_of(sp)
        changed = True

    if changed:
        with open(cover_slide_xml_path, "wb") as handle:
            handle.write(document.toxml(encoding="UTF-8"))

    return report
# @AI_GENERATED: end

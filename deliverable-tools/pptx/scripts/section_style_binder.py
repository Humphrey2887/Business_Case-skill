# @AI_GENERATED
"""Role→Section deterministic style binding for the envision PPTX master template.

角色→具名节确定性绑定工具。本模块负责：
  1. parse_sections  —— 解析 ppt/presentation.xml 的 <p14:sectionLst> 具名节（Task 3.1）
  2. detect_roles    —— 位置法角色识别（Task 3.4）
  (bind_pages 等确定性绑定在后续任务实现。)

XML 读写统一使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。
"""

from dataclasses import dataclass, field
from enum import Enum

from defusedxml.minidom import parse

# PowerPoint 2010 扩展：节列表所在的 <p:ext> uri，以及 p14 命名空间。
SECTION_EXT_URI = "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}"
P14_NAMESPACE = "http://schemas.microsoft.com/office/powerpoint/2010/main"
# 归一后的合法节名（母版节名已在 Task 1/A3 归一为全小写）。
KNOWN_SECTIONS = ("cover", "content", "ending")
# cover / content 为结构性必需节；ending 可选（见 Requirement 3）。
REQUIRED_SECTIONS = ("cover", "content")


class SectionStructureError(Exception):
    """当 presentation.xml 缺少 <p14:sectionLst> 或缺少 cover/content 必需节时抛出。

    属结构性缺陷，须先按 Assumption A3 重构母版为三节结构再继续绑定。
    """


@dataclass
class SectionInfo:
    """presentation.xml 中的一个具名节（<p14:section>）。

    - name:       归一后的节名（"cover" | "content" | "ending"）
    - section_id: 节 GUID（<p14:section id="{...}">）
    - slide_ids:  该节 <p14:sldIdLst> 下各 <p14:sldId> 的 id（保序）
    """

    name: str
    section_id: str
    slide_ids: list[str] = field(default_factory=list)


def _iter_elements(node):
    """深度优先遍历 node 下所有 Element 子节点（含自身的后代）。"""
    for child in node.childNodes:
        # nodeType == 1 表示 ELEMENT_NODE。
        if child.nodeType == child.ELEMENT_NODE:
            yield child
            yield from _iter_elements(child)


def _local_name(element) -> str:
    """返回元素的本地名（去掉命名空间前缀），以兼容不同前缀写法。"""
    if element.localName:
        return element.localName
    tag = element.tagName
    return tag.split(":", 1)[1] if ":" in tag else tag


def _find_section_lst(document):
    """定位 SECTION_EXT_URI 对应 <p:ext> 内的 <p14:sectionLst> 元素，找不到返回 None。"""
    for element in _iter_elements(document):
        if _local_name(element) != "ext":
            continue
        if element.getAttribute("uri") != SECTION_EXT_URI:
            continue
        for descendant in _iter_elements(element):
            if _local_name(descendant) == "sectionLst":
                return descendant
    return None


def parse_sections(presentation_xml_path: str) -> dict[str, SectionInfo]:
    """读取 presentation.xml 的 <p14:sectionLst>，返回按名索引的具名节。

    解析 <p:ext uri="{521415D9-...}"> 内 <p14:sectionLst>，按 name 索引返回
    dict[str, SectionInfo]，每节收集其 <p14:sldId> 分组到 slide_ids。

    缺失 <p14:sectionLst> 或缺失 cover/content 必需节时抛 SectionStructureError；
    ending 缺失是允许的（见 Requirement 3）。

    使用 defusedxml.minidom 解析（设计 A4）。

    Validates: Requirements 1.5
    """
    document = parse(presentation_xml_path)
    section_lst = _find_section_lst(document)
    if section_lst is None:
        raise SectionStructureError(
            "presentation.xml 缺少 <p14:sectionLst>"
            f"（<p:ext uri=\"{SECTION_EXT_URI}\">）；"
            "请按 Assumption A3 重构母版为 cover/content/ending 三节结构。"
        )

    sections: dict[str, SectionInfo] = {}
    for element in _iter_elements(section_lst):
        if _local_name(element) != "section":
            continue
        name = element.getAttribute("name")
        section_id = element.getAttribute("id")
        slide_ids = [
            descendant.getAttribute("id")
            for descendant in _iter_elements(element)
            if _local_name(descendant) == "sldId"
        ]
        sections[name] = SectionInfo(
            name=name, section_id=section_id, slide_ids=slide_ids
        )

    missing = [name for name in REQUIRED_SECTIONS if name not in sections]
    if missing:
        raise SectionStructureError(
            "presentation.xml 缺少必需具名节: "
            f"{', '.join(missing)}（已解析到: {sorted(sections)}）；"
            "请按 Assumption A3 重构母版为 cover/content/ending 三节结构。"
        )

    return sections


class Role(str, Enum):
    COVER = "cover"
    CONTENT = "content"
    ENDING = "ending"


def detect_roles(page_count: int, ending_requested: bool) -> list[Role]:
    """位置法角色识别（Positional_Role_Detection）。
    - 第一张 → COVER
    - 首末之间每张 → CONTENT
    - 末张 → ENDING（当 ending_requested 且 page_count>=2）否则 CONTENT
    page_count<=0 时返回 []；page_count==1 时仅 [COVER]。
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


# @AI_GENERATED
# ---------------------------------------------------------------------------
# 确定性绑定（Deterministic_Binding）—— Task 4.1
#
# FIXED_MAPPING / BoundPage / bind_pages / _apply_section_layout。
# 核心不变量：对任意页 p，正确成片满足 p.style_source == FIXED_MAPPING[p.role]。
# XML 读写统一使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。
# ---------------------------------------------------------------------------

import os

# 角色→节固定映射（Deterministic_Binding 的核心不变量来源）。
FIXED_MAPPING = {
    Role.COVER: "cover",
    Role.CONTENT: "content",
    Role.ENDING: "ending",
}

# OOXML 关系命名空间与 slideLayout 关系类型。
_RELATIONSHIP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_SLIDE_LAYOUT_REL_TYPE = _RELATIONSHIP_NS + "/slideLayout"
_SLIDE_REL_TYPE = _RELATIONSHIP_NS + "/slide"


@dataclass
class BoundPage:
    """绑定后的生成页。

    - index:        页在生成序列中的位置（0 基）。
    - role:         位置法识别出的角色（Role）。
    - style_source: 实际绑定到的具名节名（Style_Source）；期望值 = FIXED_MAPPING[role]。
    - slide_file:   该页在解包目录中的 slide 路径（unpacked/ppt/slides/slideN.xml）。
    """

    index: int
    role: Role
    style_source: str
    slide_file: str


def _ppt_dir_from_slide_file(slide_file: str) -> str:
    """由 unpacked/ppt/slides/slideN.xml 推出 ppt 目录（.../ppt）。

    slide_file 形如 <root>/ppt/slides/slideN.xml；其上两级即 ppt 目录。
    """
    slides_dir = os.path.dirname(slide_file)  # <root>/ppt/slides
    return os.path.dirname(slides_dir)  # <root>/ppt


def _resolve_target(base_dir: str, target: str) -> str:
    """将 rels 中的相对 Target（可能含 ../）规范化为绝对路径。"""
    return os.path.normpath(os.path.join(base_dir, target))


def _sldid_to_rid(presentation_xml_path: str) -> dict[str, str]:
    """解析 presentation.xml 的 <p:sldIdLst>，返回 {sldId id: r:id}。"""
    document = parse(presentation_xml_path)
    mapping: dict[str, str] = {}
    for element in _iter_elements(document):
        if _local_name(element) != "sldId":
            continue
        sld_id = element.getAttribute("id")
        # r:id 属性带命名空间前缀；getAttribute 需用带前缀名，回退遍历属性。
        r_id = element.getAttribute("r:id")
        if not r_id:
            for attr_name, attr_value in element.attributes.items():
                if attr_name.split(":", 1)[-1] == "id" and attr_value.startswith("rId"):
                    r_id = attr_value
                    break
        if sld_id and r_id:
            mapping[sld_id] = r_id
    return mapping


def _rels_targets_by_id(rels_path: str) -> dict[str, str]:
    """解析 .rels 文件，返回 {Id: Target}。"""
    document = parse(rels_path)
    mapping: dict[str, str] = {}
    for element in _iter_elements(document):
        if _local_name(element) != "Relationship":
            continue
        rel_id = element.getAttribute("Id")
        target = element.getAttribute("Target")
        if rel_id:
            mapping[rel_id] = target
    return mapping


def _slide_file_for_section(section: SectionInfo, ppt_dir: str) -> str | None:
    """解析该节首个模板 slide 在解包目录中的 slide 文件绝对路径。

    路径链：section.slide_ids[0] (sldId id)
        → presentation.xml <p:sldIdLst> 得 r:id
        → presentation.xml.rels 得 slide Target（相对 ppt/）
    返回绝对路径；无法解析时返回 None（best-effort）。
    """
    if not section.slide_ids:
        return None
    presentation_xml = os.path.join(ppt_dir, "presentation.xml")
    presentation_rels = os.path.join(ppt_dir, "_rels", "presentation.xml.rels")
    if not (os.path.exists(presentation_xml) and os.path.exists(presentation_rels)):
        return None
    rid = _sldid_to_rid(presentation_xml).get(section.slide_ids[0])
    if not rid:
        return None
    target = _rels_targets_by_id(presentation_rels).get(rid)
    if not target:
        return None
    return _resolve_target(ppt_dir, target)


def _slide_rels_path(slide_file: str) -> str:
    """由 slide 文件路径推出其 .rels 路径（slides/_rels/slideN.xml.rels）。"""
    slides_dir = os.path.dirname(slide_file)
    return os.path.join(slides_dir, "_rels", os.path.basename(slide_file) + ".rels")


def _layout_target_in_slide_rels(slide_rels_path: str) -> str | None:
    """在某 slide 的 .rels 中找到 slideLayout 关系的 Target（相对，含 ../）。"""
    if not os.path.exists(slide_rels_path):
        return None
    document = parse(slide_rels_path)
    for element in _iter_elements(document):
        if _local_name(element) != "Relationship":
            continue
        if element.getAttribute("Type") == _SLIDE_LAYOUT_REL_TYPE:
            return element.getAttribute("Target")
    return None


def _repoint_layout_in_slide_rels(slide_rels_path: str, new_target: str) -> bool:
    """将某 slide .rels 中 slideLayout 关系的 Target 改写为 new_target 并回写。

    使用 defusedxml.minidom 读写。改写成功返回 True，未找到关系返回 False。
    """
    if not os.path.exists(slide_rels_path):
        return False
    document = parse(slide_rels_path)
    changed = False
    for element in _iter_elements(document):
        if _local_name(element) != "Relationship":
            continue
        if element.getAttribute("Type") == _SLIDE_LAYOUT_REL_TYPE:
            element.setAttribute("Target", new_target)
            changed = True
    if changed:
        with open(slide_rels_path, "wb") as handle:
            handle.write(document.toxml(encoding="UTF-8"))
    return changed


def _apply_section_layout(page: BoundPage, section: SectionInfo) -> bool:
    """将该页 slideN.xml.rels 的 slideLayout 关系指向目标节模板 slide 的 layout。

    绑定机制（design 1.3）：以目标节模板 slide 为样式骨架，让生成页在样式维度锚定
    到该节 layout——即把生成页 slide 的 slideLayout 关系 Target 重指向节模板 slide
    所用的同一 layout，保证 Style_Source 稳定、同类页样式一致（R1.4）。

    全部 XML 读写使用 defusedxml.minidom。当解包目录中缺少所需文件/关系时，本函数
    以 best-effort 方式跳过物理改写（bind_pages 已完成 role/style_source 的确定性
    逻辑绑定），返回是否实际执行了物理重指向。

    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """
    ppt_dir = _ppt_dir_from_slide_file(page.slide_file)

    # 1. 解析目标节模板 slide 文件。
    template_slide = _slide_file_for_section(section, ppt_dir)
    if template_slide is None:
        return False

    # 2. 取模板 slide 的 slideLayout Target（相对，含 ../）。
    template_layout_target = _layout_target_in_slide_rels(
        _slide_rels_path(template_slide)
    )
    if template_layout_target is None:
        return False

    # 3. 将模板 layout 规范化为绝对路径，再折算为“相对于本页 slide 的 _rels”的路径。
    template_slides_dir = os.path.dirname(template_slide)
    layout_abs = _resolve_target(
        os.path.join(template_slides_dir, "_rels"), template_layout_target
    )
    page_rels_dir = os.path.join(os.path.dirname(page.slide_file), "_rels")
    new_target = os.path.relpath(layout_abs, page_rels_dir).replace(os.sep, "/")

    # 4. 回写本页 slide .rels 的 slideLayout 关系 Target，锚定到该节 layout。
    return _repoint_layout_in_slide_rels(_slide_rels_path(page.slide_file), new_target)


def bind_pages(
    sequence: list[BoundPage],
    sections: dict[str, SectionInfo],
    ending_requested: bool,
) -> list[BoundPage]:
    """对生成序列执行角色识别 + 固定映射确定性绑定。

    role→section 固定：cover→cover, content→content, ending→ending。
    所有 content 页共享同一 content 节样式来源（确定性/一致性，R1.4）。

    对每页：设 page.role=role、page.style_source=FIXED_MAPPING[role]，随后调用
    _apply_section_layout 将该页 slide 的 slideLayout 关系锚定到目标节模板 slide
    的 layout（物理改写为 best-effort，逻辑绑定始终生效）。

    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """
    roles = detect_roles(len(sequence), ending_requested)
    for page, role in zip(sequence, roles):
        target_section = FIXED_MAPPING[role]
        page.role = role
        page.style_source = target_section  # 确定性：同角色恒绑同一节
        section = sections.get(target_section)
        if section is not None:
            _apply_section_layout(page, section)
    return sequence
# @AI_GENERATED: end

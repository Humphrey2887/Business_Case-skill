# @AI_GENERATED
"""Feature: pptx-template-section-styling — parse_sections 示例/边界测试 (Task 3.3)

Concrete example / boundary tests for ``parse_sections`` (pytest style, NOT hypothesis).

固件基于母版实探事实（master-structure-findings.md）：
    cover   → sldId 287 (rId7) → slide1 / slideLayout1
    content → sldId 276 (rId8) → slide2 / slideLayout14
    ending  → sldId 295 (rId9) → slide3 / slideLayout4

所有固件使用真实 OOXML 前缀（p:/p14:/r:）以及节扩展 URI
{521415D9-36F7-43E2-AB2F-B90AF26B5E84}，并通过 defusedxml.minidom 解析，
以防命名空间回归（例如误把带前缀的 p14:section 当作无前缀 section）。

覆盖场景：
    1. 三节齐全（cover/content/ending）→ 键集合与 slide_ids 精确匹配母版事实。
    2. 无 ending 节 → 仅 {cover, content}，不报错（Requirement 3：ending 可选）。
    3. 缺 content 节 → 抛 SectionStructureError。
    4. 完全无 <p14:sectionLst> → 抛 SectionStructureError。

Validates: Requirements 1.5
"""

import os
import sys

import pytest
from defusedxml.minidom import parseString

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section_style_binder import (  # noqa: E402
    SECTION_EXT_URI,
    SectionInfo,
    SectionStructureError,
    parse_sections,
)

# 母版实探事实：节名 → (section GUID, sldId)。
_SECTION_FACTS = {
    "cover": ("{81316CC1-DC07-724F-951F-344DE4F26084}", "287"),
    "content": ("{BC31728A-994C-7647-ABEC-B14018EBDEF1}", "276"),
    "ending": ("{81C88842-2B13-470F-9360-8408E803334B}", "295"),
}


def _section_xml(name: str) -> str:
    """构造单个 <p14:section> 片段（真实 p14: 前缀）。"""
    section_id, slide_id = _SECTION_FACTS[name]
    return (
        f'        <p14:section name="{name}" id="{section_id}">\n'
        f'          <p14:sldIdLst><p14:sldId id="{slide_id}"/></p14:sldIdLst>\n'
        "        </p14:section>"
    )


def _presentation_with_sections(*names: str) -> str:
    """构造含 <p14:sectionLst> 的 presentation.xml（真实 OOXML 前缀 + 节扩展 URI）。"""
    sections = "\n".join(_section_xml(name) for name in names)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        "<p:presentation"
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">\n'
        "  <p:sldIdLst>\n"
        '    <p:sldId id="287" r:id="rId7"/>\n'
        '    <p:sldId id="276" r:id="rId8"/>\n'
        '    <p:sldId id="295" r:id="rId9"/>\n'
        "  </p:sldIdLst>\n"
        "  <p:extLst>\n"
        f'    <p:ext uri="{SECTION_EXT_URI}">\n'
        "      <p14:sectionLst"
        ' xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">\n'
        f"{sections}\n"
        "      </p14:sectionLst>\n"
        "    </p:ext>\n"
        "  </p:extLst>\n"
        "</p:presentation>\n"
    )


def _presentation_without_section_lst() -> str:
    """构造完全没有 <p14:sectionLst>（也无 <p:extLst>）的 presentation.xml。"""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        "<p:presentation"
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        "  <p:sldIdLst>\n"
        '    <p:sldId id="287" r:id="rId7"/>\n'
        '    <p:sldId id="276" r:id="rId8"/>\n'
        "  </p:sldIdLst>\n"
        "</p:presentation>\n"
    )


def _write(tmp_path, content: str) -> str:
    """将 XML 写入临时文件，返回路径（parse_sections 接受文件路径）。"""
    path = tmp_path / "presentation.xml"
    path.write_text(content, encoding="utf-8")
    return str(path)


# --- 命名空间回归防护 --------------------------------------------------------


def test_fixtures_use_realistic_namespaced_prefixes():
    """固件以真实 p:/p14: 前缀与节扩展 URI 书写，能被 defusedxml.minidom 正确解析。

    交叉验证 DOM 中带前缀元素的 localName 去前缀后为期望本地名，
    防止解析器对命名空间前缀的回归。
    """
    document = parseString(_presentation_with_sections("cover", "content", "ending"))

    ext = document.getElementsByTagName("p:ext")[0]
    assert ext.getAttribute("uri") == SECTION_EXT_URI

    section_lst = document.getElementsByTagName("p14:sectionLst")
    assert len(section_lst) == 1
    assert section_lst[0].localName == "sectionLst"

    sections = document.getElementsByTagName("p14:section")
    assert len(sections) == 3
    assert [s.localName for s in sections] == ["section", "section", "section"]


# --- 场景 1：三节齐全 --------------------------------------------------------


def test_full_three_section_fixture(tmp_path):
    """三节齐全（cover/content/ending）→ 键集合与 slide_ids 精确匹配母版事实。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _presentation_with_sections("cover", "content", "ending"))

    sections = parse_sections(path)

    assert set(sections) == {"cover", "content", "ending"}
    assert isinstance(sections["cover"], SectionInfo)
    # slide_ids 精确匹配母版事实：287 / 276 / 295。
    assert sections["cover"].slide_ids == ["287"]
    assert sections["content"].slide_ids == ["276"]
    assert sections["ending"].slide_ids == ["295"]
    # section GUID 亦正确读取。
    assert sections["ending"].section_id == "{81C88842-2B13-470F-9360-8408E803334B}"


# --- 场景 2：无 ending 节（可选，不报错）------------------------------------


def test_fixture_without_ending_section(tmp_path):
    """无 ending 节 → 仅 {cover, content}，不报错（Requirement 3：ending 可选）。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _presentation_with_sections("cover", "content"))

    sections = parse_sections(path)

    assert set(sections) == {"cover", "content"}
    assert "ending" not in sections
    assert sections["cover"].slide_ids == ["287"]
    assert sections["content"].slide_ids == ["276"]


# --- 场景 3：缺 content 节 → 报错 -------------------------------------------


def test_fixture_missing_content_section_raises(tmp_path):
    """缺 content 必需节（仅 cover + ending）→ 抛 SectionStructureError。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _presentation_with_sections("cover", "ending"))

    with pytest.raises(SectionStructureError):
        parse_sections(path)


# --- 场景 4：完全无 <p14:sectionLst> → 报错 --------------------------------


def test_fixture_without_section_lst_raises(tmp_path):
    """完全无 <p14:sectionLst> → 抛 SectionStructureError。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _presentation_without_section_lst())

    with pytest.raises(SectionStructureError):
        parse_sections(path)
# @AI_GENERATED: end

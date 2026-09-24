# @AI_GENERATED
"""Feature: pptx-template-section-styling — parse_sections 示例/边界测试

Example / boundary tests for `parse_sections`.

用代表性 presentation.xml 固件（基于母版实探事实：cover/content/ending 对应
sldId 287/276/295）断言解析行为，并以 defusedxml.minidom 解析固件本身防命名空间回归：

  1. 三节齐全 → 解析为 3 节，slide_ids 正确（287 / 276 / 295）。
  2. 省略 ending → 仅 {cover, content}，不报错（Requirement 3：ending 可选）。
  3. 缺 content 节 → 抛 SectionStructureError。
  4. 完全缺失 <p14:sectionLst> → 抛 SectionStructureError。

命名空间回归防护：固件使用真实 OOXML 前缀（p:/p14:/r:），并交叉验证
带前缀写法与被测解析器对本地名（localName）的解析一致。

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
    SectionStructureError,
    parse_sections,
)


# --- presentation.xml 固件构造 ---------------------------------------------

# 母版实探事实（master-structure-findings.md）：
#   cover   → sldId 287 (rId7) → slide1 / slideLayout1
#   content → sldId 276 (rId8) → slide2 / slideLayout14
#   ending  → sldId 295 (rId9) → slide3 / slideLayout4
_SECTION_XML = {
    "cover": '        <p14:section name="cover" id="{81316CC1-DC07-724F-951F-344DE4F26084}">\n'
    "          <p14:sldIdLst><p14:sldId id=\"287\"/></p14:sldIdLst>\n"
    "        </p14:section>",
    "content": '        <p14:section name="content" id="{BC31728A-994C-7647-ABEC-B14018EBDEF1}">\n'
    "          <p14:sldIdLst><p14:sldId id=\"276\"/></p14:sldIdLst>\n"
    "        </p14:section>",
    "ending": '        <p14:section name="ending" id="{81C88842-2B13-470F-9360-8408E803334B}">\n'
    "          <p14:sldIdLst><p14:sldId id=\"295\"/></p14:sldIdLst>\n"
    "        </p14:section>",
}


def _make_presentation_xml(section_names):
    """构造一份带具名节的 presentation.xml 字符串（真实 OOXML 前缀）。"""
    sections = "\n".join(_SECTION_XML[name] for name in section_names)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:presentation'
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
        '      <p14:sectionLst'
        ' xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">\n'
        f"{sections}\n"
        "      </p14:sectionLst>\n"
        "    </p:ext>\n"
        "  </p:extLst>\n"
        "</p:presentation>\n"
    )


def _make_presentation_xml_no_sectionlst():
    """构造一份完全没有 <p14:sectionLst> 的 presentation.xml。"""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:presentation'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        "  <p:sldIdLst>\n"
        '    <p:sldId id="287" r:id="rId7"/>\n'
        "  </p:sldIdLst>\n"
        "</p:presentation>\n"
    )


def _write(tmp_path, content):
    """将 XML 写入临时文件并返回路径（parse_sections 接受文件路径）。"""
    path = tmp_path / "presentation.xml"
    path.write_text(content, encoding="utf-8")
    return str(path)


# --- 命名空间回归防护：固件自身以 defusedxml.minidom 解析 ---------------------


def test_fixture_parses_with_defusedxml_namespaced_prefixes():
    """固件用真实 OOXML 前缀（p:/p14:）书写，能被 defusedxml.minidom 正确解析。

    交叉验证：DOM 中带前缀元素的 localName 与被测解析器所依赖的本地名一致，
    防止命名空间前缀回归（例如误把 `p14:section` 当作无前缀 `section`）。
    """
    xml = _make_presentation_xml(["cover", "content", "ending"])
    document = parseString(xml)

    sections = document.getElementsByTagName("p14:section")
    assert len(sections) == 3
    # localName 去前缀后为 "section"，tagName 保留前缀。
    assert sections[0].localName == "section"
    assert sections[0].tagName == "p14:section"

    ext = document.getElementsByTagName("p:ext")[0]
    assert ext.getAttribute("uri") == SECTION_EXT_URI


# --- 场景 1：三节齐全 --------------------------------------------------------


def test_all_three_sections_present(tmp_path):
    """三节齐全 → 3 节，键集合与 slide_ids 精确匹配母版事实。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _make_presentation_xml(["cover", "content", "ending"]))

    sections = parse_sections(path)

    assert set(sections) == {"cover", "content", "ending"}
    assert sections["cover"].slide_ids == ["287"]
    assert sections["content"].slide_ids == ["276"]
    assert sections["ending"].slide_ids == ["295"]
    # section GUID 亦被正确读取。
    assert sections["cover"].section_id == "{81316CC1-DC07-724F-951F-344DE4F26084}"


# --- 场景 2：省略 ending（可选，不报错）-------------------------------------


def test_ending_omitted_yields_cover_and_content_only(tmp_path):
    """省略 ending → 仅 {cover, content}，无报错（Requirement 3：ending 可选）。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _make_presentation_xml(["cover", "content"]))

    sections = parse_sections(path)

    assert set(sections) == {"cover", "content"}
    assert "ending" not in sections
    assert sections["cover"].slide_ids == ["287"]
    assert sections["content"].slide_ids == ["276"]


# --- 场景 3：缺 content 节 → 报错 -------------------------------------------


def test_missing_content_section_raises(tmp_path):
    """缺 content 必需节 → 抛 SectionStructureError。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _make_presentation_xml(["cover", "ending"]))

    with pytest.raises(SectionStructureError):
        parse_sections(path)


# --- 场景 4：完全缺失 <p14:sectionLst> → 报错 -------------------------------


def test_missing_section_lst_entirely_raises(tmp_path):
    """完全缺失 <p14:sectionLst> → 抛 SectionStructureError。

    Validates: Requirements 1.5
    """
    path = _write(tmp_path, _make_presentation_xml_no_sectionlst())

    with pytest.raises(SectionStructureError):
        parse_sections(path)
# @AI_GENERATED: end

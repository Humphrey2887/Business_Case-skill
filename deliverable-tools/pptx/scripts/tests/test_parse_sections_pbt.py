# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 3: 具名节解析完整性

Property-based test for `parse_sections` (Component 1.1).

*For any* 含合法 <p:sectionLst> 的 presentation.xml，parse_sections 返回的节集合
包含 cover、content 两节（且当存在时含 ending），每节关联其 <p14:sldId> 分组；
缺 cover/content 时报错。

策略：随机生成合法 <p:sectionLst> 固件——节名（cover/content 恒含，ending 可选）、
随机 GUID、随机 <p14:sldId> 分组、随机节顺序——写入临时文件后调用 parse_sections，
断言返回 dict 的键集合与每节 slide_ids 与生成模型一致；并断言省略 cover 或 content
时抛 SectionStructureError。

XML 固件以 defusedxml（parseString）交叉解析，防命名空间回归；被测模块亦仅用
defusedxml.minidom（设计 A4，禁用 xml.etree）。

Validates: Requirements 1.5
"""

import os
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section_style_binder import (  # noqa: E402
    SECTION_EXT_URI,
    SectionStructureError,
    parse_sections,
)


# --- 生成器 -----------------------------------------------------------------

# GUID 片段（十六进制），用于拼装形如 {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX} 的节 id。
_HEX = "0123456789ABCDEF"


@st.composite
def _guids(draw):
    """生成一个 PowerPoint 风格的节 GUID: {8-4-4-4-12}。"""
    parts = [8, 4, 4, 4, 12]
    chunks = [
        "".join(draw(st.lists(st.sampled_from(_HEX), min_size=n, max_size=n)))
        for n in parts
    ]
    return "{" + "-".join(chunks) + "}"


# 唯一 slide id（正整数字符串），供各节分组时不重复取用。
_slide_id_pool = st.lists(
    st.integers(min_value=256, max_value=99999).map(str),
    min_size=2,
    max_size=12,
    unique=True,
)


@st.composite
def _section_models(draw):
    """生成一个合法节结构模型: {name: {"id": guid, "slide_ids": [...]}}。

    - cover / content 恒定存在（结构性必需，见 Requirement 1/3）。
    - ending 以随机布尔决定是否存在（可选）。
    - 每节分得 1..N 张 slide id，来自共享池且互不重复。
    - 节的书写顺序随机打乱，验证解析与顺序无关。
    """
    include_ending = draw(st.booleans())
    names = ["cover", "content"] + (["ending"] if include_ending else [])

    pool = draw(_slide_id_pool)
    # 确保池足够分给每节至少一张。
    while len(pool) < len(names):
        pool.append(str(int(pool[-1]) + 1))

    # 将池切分成 len(names) 段，每段非空。
    cut_points = sorted(
        draw(
            st.lists(
                st.integers(min_value=1, max_value=len(pool) - 1),
                min_size=len(names) - 1,
                max_size=len(names) - 1,
                unique=True,
            )
        )
    ) if len(names) > 1 else []
    bounds = [0, *cut_points, len(pool)]
    groups = [pool[bounds[i]:bounds[i + 1]] for i in range(len(names))]
    # 若因切点导致空段（不应发生，但兜底），补一张。
    for i, g in enumerate(groups):
        if not g:
            groups[i] = [pool[i]]

    model = {}
    for name, slide_ids in zip(names, groups):
        model[name] = {"id": draw(_guids()), "slide_ids": slide_ids}

    # 随机书写顺序。
    order = draw(st.permutations(list(model)))
    return model, list(order)


# --- 固件构造 ---------------------------------------------------------------


def _section_xml(name, guid, slide_ids):
    slds = "".join(f'<p14:sldId id="{sid}"/>' for sid in slide_ids)
    return (
        f'        <p14:section name="{name}" id="{guid}">\n'
        f"          <p14:sldIdLst>{slds}</p14:sldIdLst>\n"
        f"        </p14:section>"
    )


def _make_presentation_xml(model, order):
    """按给定书写顺序构造 presentation.xml 字符串（真实 OOXML 前缀）。"""
    sections = "\n".join(
        _section_xml(name, model[name]["id"], model[name]["slide_ids"])
        for name in order
    )
    # 顶层 <p:sldIdLst> 汇总所有 slide id（顺序不影响解析）。
    all_ids = [sid for name in order for sid in model[name]["slide_ids"]]
    sld_id_lst = "".join(
        f'    <p:sldId id="{sid}" r:id="rId{i + 2}"/>\n'
        for i, sid in enumerate(all_ids)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        "<p:presentation"
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">\n'
        "  <p:sldIdLst>\n"
        f"{sld_id_lst}"
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


def _write(tmp_path, content):
    path = tmp_path / "presentation.xml"
    path.write_text(content, encoding="utf-8")
    return str(path)


# --- Property 3: 合法固件的解析完整性 ---------------------------------------


@settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(spec=_section_models())
def test_parse_sections_completeness(spec, tmp_path):
    """Property 3: 合法 <p:sectionLst> → 键集合含 cover/content（存在时含 ending），
    每节 slide_ids 与生成模型一致。

    Validates: Requirements 1.5
    """
    model, order = spec
    path = _write(tmp_path, _make_presentation_xml(model, order))

    sections = parse_sections(path)

    # 键集合与生成模型一致：cover/content 必含，ending 当且仅当被生成时存在。
    assert set(sections) == set(model)
    assert "cover" in sections
    assert "content" in sections
    assert ("ending" in sections) == ("ending" in model)

    # 每节关联其 <p14:sldId> 分组，且 GUID 被正确读取。
    for name, expected in model.items():
        assert sections[name].name == name
        assert sections[name].section_id == expected["id"]
        assert sections[name].slide_ids == expected["slide_ids"]


# --- Property 3: 缺 cover/content 必需节 → 报错 -----------------------------


@settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    spec=_section_models(),
    drop=st.sampled_from(["cover", "content"]),
)
def test_parse_sections_missing_required_raises(spec, drop, tmp_path):
    """Property 3: 省略 cover 或 content 必需节 → 抛 SectionStructureError。

    Validates: Requirements 1.5
    """
    model, order = spec
    # 从模型与书写顺序中移除被 drop 的必需节。
    reduced = {name: v for name, v in model.items() if name != drop}
    reduced_order = [name for name in order if name != drop]
    path = _write(tmp_path, _make_presentation_xml(reduced, reduced_order))

    with pytest.raises(SectionStructureError):
        parse_sections(path)
# @AI_GENERATED: end

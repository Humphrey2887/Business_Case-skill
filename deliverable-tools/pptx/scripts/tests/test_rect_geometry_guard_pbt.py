# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 10: 直角框不变量

Property-based test for `rect_geometry_guard`（Component 3 / R8.1）。

Property 10（直角框不变量）—— 生成的框/节点/卡片几何须为 ``prstGeom prst="rect"``，
不存在圆角框。本测试从三个角度验证不变量：

1. 合规生成：仅由 ``rect_prst_geom_xml()`` 直角框组成的 slide（N 个框，N 由 hypothesis
   在 0..several 变动）→ ``find_rounded_geoms`` 返回 []，且 ``is_all_right_angle`` 为 True。
2. 圆角检测：在直角框中注入若干圆角几何（从 ``ROUNDED_RECT_GEOMETRIES`` 采样）后，
   ``find_rounded_geoms`` 非空，且以多重集合计恰好等于注入的圆角 prst 值，
   ``is_all_right_angle`` 为 False。
3. 固化幂等：对含圆角几何的 slide 执行 ``enforce_rect_geom`` 后，``is_all_right_angle``
   变为 True；再次执行 ``enforce_rect_geom`` 返回 0（幂等）。

固件在内存/临时目录构造：最小 <p:sld>，其 spTree 内含若干 <p:sp>，每个 <p:spPr>
携带 rect 直角框几何或圆角 roundRect 族几何（带非零圆角 adj）。使用 tmp_path 临时文件，
以文件路径传入被测函数。以 hypothesis 变动框数量与哪些为圆角，>=100 examples。

Validates: Requirements 8.1
"""

import collections
import os
import sys

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rect_geometry_guard import (  # noqa: E402
    ROUNDED_RECT_GEOMETRIES,
    enforce_rect_geom,
    find_rounded_geoms,
    is_all_right_angle,
    rect_prst_geom_xml,
)


# --- 固件构造 ---------------------------------------------------------------


def _rounded_prst_geom_xml(prst: str) -> str:
    """构造一个带非零圆角 adj 的圆角几何片段（如 roundRect）。"""
    return (
        f'<a:prstGeom prst="{prst}">'
        '<a:avLst><a:gd name="adj" fmla="val 16667"/></a:avLst>'
        "</a:prstGeom>"
    )


def _shape_xml(index: int, geom_xml: str) -> str:
    """构造一个 <p:sp>，其 <p:spPr> 携带给定几何片段。"""
    return (
        "      <p:sp>\n"
        "        <p:nvSpPr>\n"
        f'          <p:cNvPr id="{index + 2}" name="Box {index}"/>\n'
        "          <p:cNvSpPr/>\n"
        "          <p:nvPr/>\n"
        "        </p:nvSpPr>\n"
        "        <p:spPr>\n"
        f"          {geom_xml}\n"
        "        </p:spPr>\n"
        "      </p:sp>"
    )


def _make_slide_xml(geoms: list[str]) -> str:
    """按给定几何片段列表构造最小合法 <p:sld>（真实 OOXML 前缀）。"""
    shapes = "\n".join(_shape_xml(i, g) for i, g in enumerate(geoms))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        "<p:sld"
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">\n'
        "  <p:cSld>\n"
        "    <p:spTree>\n"
        "      <p:nvGrpSpPr>\n"
        '        <p:cNvPr id="1" name=""/>\n'
        "        <p:cNvGrpSpPr/>\n"
        "        <p:nvPr/>\n"
        "      </p:nvGrpSpPr>\n"
        "      <p:grpSpPr/>\n"
        f"{shapes}\n"
        "    </p:spTree>\n"
        "  </p:cSld>\n"
        "</p:sld>\n"
    )


def _write_slide(tmp_path, geoms: list[str]) -> str:
    path = tmp_path / "slide1.xml"
    path.write_text(_make_slide_xml(geoms), encoding="utf-8")
    return str(path)


# --- 生成器 -----------------------------------------------------------------

# 直角框数量：0..several（含空 slide 边界）。
_rect_counts = st.integers(min_value=0, max_value=8)

# 注入的圆角几何序列（至少 1 个），从 ROUNDED_RECT_GEOMETRIES 采样，允许重复。
_rounded_seqs = st.lists(
    st.sampled_from(ROUNDED_RECT_GEOMETRIES),
    min_size=1,
    max_size=6,
)


# --- Property 10.1: 合规生成 → 全直角，无圆角 ------------------------------


@settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(rect_count=_rect_counts)
def test_all_rect_boxes_are_compliant(rect_count, tmp_path):
    """Property 10.1: 仅由 rect_prst_geom_xml() 直角框组成的 slide → 合规。

    find_rounded_geoms == [] 且 is_all_right_angle == True。

    Validates: Requirements 8.1
    """
    geoms = [rect_prst_geom_xml() for _ in range(rect_count)]
    path = _write_slide(tmp_path, geoms)

    assert find_rounded_geoms(path) == []
    assert is_all_right_angle(path) is True


# --- Property 10.2: 注入圆角 → 精确检出，非全直角 -------------------------


@settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(rect_count=_rect_counts, rounded=_rounded_seqs)
def test_injected_rounded_geoms_are_detected(rect_count, rounded, tmp_path):
    """Property 10.2: 在直角框中注入圆角几何 → find_rounded_geoms 非空，

    且以多重集合计恰好等于注入的圆角 prst 值；is_all_right_angle == False。

    Validates: Requirements 8.1
    """
    geoms = [rect_prst_geom_xml() for _ in range(rect_count)]
    geoms.extend(_rounded_prst_geom_xml(prst) for prst in rounded)

    path = _write_slide(tmp_path, geoms)

    detected = find_rounded_geoms(path)
    assert detected  # 非空
    # 圆角 prst 以多重集合计恰好等于注入值（直角框不贡献违规）。
    assert collections.Counter(detected) == collections.Counter(rounded)
    assert is_all_right_angle(path) is False


# --- Property 10.3: 固化幂等 → 全直角，二次执行返回 0 ---------------------


@settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(rect_count=_rect_counts, rounded=_rounded_seqs)
def test_enforce_rect_geom_is_idempotent(rect_count, rounded, tmp_path):
    """Property 10.3: enforce_rect_geom 后全直角，且再次执行返回 0（幂等）。

    Validates: Requirements 8.1
    """
    geoms = [rect_prst_geom_xml() for _ in range(rect_count)]
    geoms.extend(_rounded_prst_geom_xml(prst) for prst in rounded)

    path = _write_slide(tmp_path, geoms)

    # 首次固化：改写数量应等于注入的圆角几何数量。
    converted = enforce_rect_geom(path)
    assert converted == len(rounded)
    assert is_all_right_angle(path) is True

    # 二次固化：已全直角，无改写（幂等）。
    assert enforce_rect_geom(path) == 0
    assert is_all_right_angle(path) is True
# @AI_GENERATED: end

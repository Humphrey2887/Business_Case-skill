# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 9: 母版取色取字与 run 级中英字体分设

Property-based test for `master_font_binder` (Task 8.3 module).

*For any* 中英混排段落文本与直接构造的 MasterTheme（已知字体/颜色集合）：
  - apply_master_fonts_to_paragraph 产出的每个 RunSpec：CJK run 绑母版 CJK 字体且
    attr=="a:ea"，拉丁 run 绑母版拉丁字体且 attr=="a:latin"；每个 run 的 typeface
    恒 ∈ theme.font_set；RunSpec.text 拼接 == 原文（无字符丢失/重排）。
  - split_runs_by_script 每段单一脚本（按 is_cjk 判定），拼接 == 输入。
  - resolve_master_color：对任意槽名返回母版值；对母版集合外的随机值抛
    ColorNotInMasterError（用 assume() 保证取值在集合外）。

策略：混排文本由 CJK 码点（小集合中文字符）与拉丁字母/数字/空格/西文标点组合而成。

Validates: Requirements 7.1, 7.2, 7.3
"""

import os
import sys

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from master_font_binder import (  # noqa: E402
    SCRIPT_CJK,
    SCRIPT_LATIN,
    ColorNotInMasterError,
    MasterTheme,
    apply_master_fonts_to_paragraph,
    is_cjk,
    resolve_master_color,
    split_runs_by_script,
)


# --- 固定母版主题：已知字体 / 颜色集合 --------------------------------------

# 直接构造一个已知的母版主题，字体/颜色集合固定且可断言。
MASTER = MasterTheme(
    latin_font="Calibri",
    cjk_font="微软雅黑",
    latin_major_font="Arial",
    cjk_major_font="微软雅黑",
    colors={
        "dk1": "000000",
        "lt1": "FFFFFF",
        "accent1": "1F2A44",
        "accent2": "C00000",
        "accent3": "2E75B6",
    },
)


# --- 生成器 -----------------------------------------------------------------

# 小集合中文字符（含常见汉字与全角标点），全部满足 is_cjk。
_CJK_CHARS = "远景智能中文母版风格测试报告，。；：、"

# 拉丁字符：字母、数字、空格、西文标点，全部不满足 is_cjk。
_LATIN_CHARS = "abcXYZ0189 .,-_/()"

_cjk_char = st.sampled_from(_CJK_CHARS)
_latin_char = st.sampled_from(_LATIN_CHARS)

# 混排文本：由 CJK / 拉丁字符交替抽样拼接而成，覆盖任意脚本切换。
_mixed_text = st.lists(
    st.one_of(_cjk_char, _latin_char),
    min_size=1,
    max_size=40,
).map("".join)


# --- Property 9.1 / 9.2: 段落 run 分设与母版字体绑定 ------------------------


@settings(max_examples=200)
@given(text=_mixed_text, use_minor=st.booleans())
def test_apply_master_fonts_binds_by_script(text, use_minor):
    """Property 9: 混排段落中 CJK run 绑 CJK 字体（a:ea）、拉丁 run 绑拉丁字体（a:latin），
    每个 run 字体 ∈ 母版集合，且文本拼接无损。

    Validates: Requirements 7.1, 7.2, 7.3
    """
    specs = apply_master_fonts_to_paragraph(text, MASTER, use_minor=use_minor)

    expected_cjk = MASTER.cjk_font if use_minor else MASTER.cjk_major_font
    expected_latin = MASTER.latin_font if use_minor else MASTER.latin_major_font

    for spec in specs:
        # 每个 run 单一脚本，且该 run 内所有字符与其脚本标注一致。
        assert spec.script in (SCRIPT_CJK, SCRIPT_LATIN)
        for ch in spec.text:
            assert (is_cjk(ch) is True) == (spec.script == SCRIPT_CJK)

        if spec.script == SCRIPT_CJK:
            assert spec.typeface == expected_cjk
            assert spec.attr == "a:ea"
        else:
            assert spec.typeface == expected_latin
            assert spec.attr == "a:latin"

        # run 字体恒取自母版提取集合（R7.1）。
        assert spec.typeface in MASTER.font_set

    # 文本无丢失/无重排：run 文本按序拼接 == 原文。
    assert "".join(spec.text for spec in specs) == text


# --- Property 9.3: split_runs_by_script 单脚本 + 拼接无损 --------------------


@settings(max_examples=200)
@given(text=_mixed_text)
def test_split_runs_by_script_single_script_and_lossless(text):
    """Property 9: split_runs_by_script 每段单一脚本（按 is_cjk），拼接 == 输入。

    Validates: Requirements 7.2, 7.3
    """
    segments = split_runs_by_script(text)

    # 拼接无损。
    assert "".join(seg_text for seg_text, _ in segments) == text

    prev_script = None
    for seg_text, script in segments:
        assert seg_text != ""  # 无空段
        assert script in (SCRIPT_CJK, SCRIPT_LATIN)
        # 段内所有字符脚本一致。
        for ch in seg_text:
            assert (is_cjk(ch) is True) == (script == SCRIPT_CJK)
        # 相邻段脚本必不同（否则应被合并为一段）。
        assert script != prev_script
        prev_script = script


# --- Property 9.4: resolve_master_color 只接受母版集合内颜色 ---------------


@settings(max_examples=200)
@given(slot=st.sampled_from(sorted(MASTER.colors)))
def test_resolve_master_color_returns_master_value_for_slot(slot):
    """Property 9: 任意母版槽名 → 返回母版颜色值（∈ 母版集合）。

    Validates: Requirements 7.1
    """
    value = resolve_master_color(slot, MASTER)
    assert value == MASTER.colors[slot]
    assert value in MASTER.color_values


@settings(max_examples=200)
@given(
    requested=st.text(
        alphabet="0123456789ABCDEFabcdefGHIJK-#", min_size=1, max_size=10
    )
)
def test_resolve_master_color_rejects_outside_master(requested):
    """Property 9: 母版集合外的颜色 → 抛 ColorNotInMasterError。

    Validates: Requirements 7.1
    """
    # 保证 requested 既非槽名，其规范化值也不在母版颜色值集合内。
    assume(requested not in MASTER.colors)
    normalized = requested.lstrip("#").upper()
    master_normalized = {v.lstrip("#").upper() for v in MASTER.colors.values()}
    assume(normalized not in master_normalized)

    with pytest.raises(ColorNotInMasterError):
        resolve_master_color(requested, MASTER)
# @AI_GENERATED: end

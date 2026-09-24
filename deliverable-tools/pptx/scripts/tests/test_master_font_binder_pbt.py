# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 9: 母版取色取字与 run 级中英字体分设

Property-based test (hypothesis) for `master_font_binder`（Task 8.3 module，Task 8.4 测试）。

Property 9 断言（直接构造已知字体/颜色的 MasterTheme，无需 XML）：

  1. **母版取色取字（font-from-master）**：对任意中英混排段落文本，
     apply_master_fonts_to_paragraph 产出的每个 RunSpec.typeface 恒 ∈ theme.font_set；
     resolve_master_color 对任意槽名 / 母版内十六进制值返回 ∈ theme.color_values 的颜色，
     对母版集合外的值抛 ColorNotInMasterError。

  2. **run 级中英字体分设（run-level separation）**：混排段落中每个 script=="cjk" 的
     RunSpec 满足 typeface==theme.cjk_font 且 attr=="a:ea"；每个 script=="latin" 的
     RunSpec 满足 typeface==theme.latin_font 且 attr=="a:latin"。所有 RunSpec.text 顺序
     拼接可无损重建原文；每个 run 的脚本与其字符 is_cjk 判定一致（cjk run 全 CJK，
     latin run 全非 CJK）。build_run_rpr / font_for_run 与 RunSpec 分设一致。

策略：混排文本由小集合 CJK 字符（远景智能能源…）与拉丁单词/数字组合，join 成串。

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
    build_run_rpr,
    font_for_run,
    is_cjk,
    resolve_master_color,
    split_runs_by_script,
)


# --- 固定母版主题：已知字体 / 颜色集合 --------------------------------------

MASTER = MasterTheme(
    latin_font="Calibri",
    cjk_font="微软雅黑",
    latin_major_font="Arial",
    cjk_major_font="思源黑体",
    colors={
        "dk1": "000000",
        "lt1": "FFFFFF",
        "dk2": "1F2A44",
        "accent1": "C00000",
        "accent2": "2E75B6",
        "accent3": "70AD47",
    },
)


# --- 生成器 -----------------------------------------------------------------

# 小集合 CJK 字符（含常见汉字与全角标点），全部满足 is_cjk。
_CJK_CHARS = "远景智能能源中文母版风格测试报告，。；："

# 拉丁 token：字母词 / 数字 / 空格 / 西文标点，全部不满足 is_cjk。
_LATIN_TOKENS = ["Envision", "AI", "Energy", "v2", "2024", " ", "-", ".", "()", "GW"]

_cjk_char = st.sampled_from(_CJK_CHARS)
_latin_token = st.sampled_from(_LATIN_TOKENS)

# 混排段落文本：CJK 单字与拉丁 token 交替抽样后拼接，覆盖任意脚本切换。
_mixed_text = st.lists(
    st.one_of(_cjk_char, _latin_token),
    min_size=1,
    max_size=40,
).map("".join)


# --- Property 9.1: 母版取色取字（typeface / color ∈ 母版集合） --------------


@settings(max_examples=200)
@given(text=_mixed_text, use_minor=st.booleans())
def test_run_typeface_and_color_from_master(text, use_minor):
    """Property 9: 每个 run 的 typeface ∈ theme.font_set；母版颜色 ∈ theme.color_values。

    Validates: Requirements 7.1
    """
    specs = apply_master_fonts_to_paragraph(text, MASTER, use_minor=use_minor)

    # 字体只取自母版提取集合（R7.1）。
    for spec in specs:
        assert spec.typeface in MASTER.font_set

    # 每个母版槽名 → 母版颜色值（∈ 母版颜色集合）。
    for slot, value in MASTER.colors.items():
        resolved_by_slot = resolve_master_color(slot, MASTER)
        resolved_by_hex = resolve_master_color(value.lower(), MASTER)
        assert resolved_by_slot == value
        assert resolved_by_hex == value
        assert resolved_by_slot in MASTER.color_values
        assert resolved_by_hex in MASTER.color_values


@settings(max_examples=200)
@given(
    requested=st.text(
        alphabet="0123456789ABCDEFabcdefGHIJKLMNOP-#", min_size=1, max_size=12
    )
)
def test_color_outside_master_rejected(requested):
    """Property 9: 母版集合外的颜色（既非槽名、其值也不在集合）→ ColorNotInMasterError。

    Validates: Requirements 7.1
    """
    assume(requested not in MASTER.colors)
    normalized = requested.lstrip("#").upper()
    master_normalized = {v.lstrip("#").upper() for v in MASTER.colors.values()}
    assume(normalized not in master_normalized)

    with pytest.raises(ColorNotInMasterError):
        resolve_master_color(requested, MASTER)


# --- Property 9.2: run 级中英字体分设 + 文本无损 + 脚本一致 ----------------


@settings(max_examples=200)
@given(text=_mixed_text, use_minor=st.booleans())
def test_run_level_cjk_latin_separation(text, use_minor):
    """Property 9: CJK run 绑 CJK 字体（a:ea）、拉丁 run 绑拉丁字体（a:latin）；
    文本拼接无损；run 脚本与字符 is_cjk 判定一致；build_run_rpr / font_for_run 一致。

    Validates: Requirements 7.2, 7.3
    """
    specs = apply_master_fonts_to_paragraph(text, MASTER, use_minor=use_minor)

    expected_cjk = MASTER.cjk_font if use_minor else MASTER.cjk_major_font
    expected_latin = MASTER.latin_font if use_minor else MASTER.latin_major_font

    for spec in specs:
        assert spec.script in (SCRIPT_CJK, SCRIPT_LATIN)
        # run 内所有字符与其脚本标注一致（cjk run 全 CJK；latin run 全非 CJK）。
        for ch in spec.text:
            assert (is_cjk(ch) is True) == (spec.script == SCRIPT_CJK)

        if spec.script == SCRIPT_CJK:
            assert spec.typeface == expected_cjk
            assert spec.attr == "a:ea"
        else:
            assert spec.typeface == expected_latin
            assert spec.attr == "a:latin"

        # font_for_run 与 RunSpec 分设一致。
        assert font_for_run(spec.script, MASTER, use_minor=use_minor) == spec.typeface

        # build_run_rpr 生成对应字体子元素 XML，含正确元素名与 typeface。
        rpr_xml = build_run_rpr(spec.script, MASTER, use_minor=use_minor)
        assert rpr_xml == f'<{spec.attr} typeface="{spec.typeface}"/>'

    # 文本无丢失/无重排：run 文本按序拼接 == 原文。
    assert "".join(spec.text for spec in specs) == text


@settings(max_examples=200)
@given(text=_mixed_text)
def test_split_runs_single_script_and_lossless(text):
    """Property 9: split_runs_by_script 每段单一脚本、相邻段脚本不同、拼接无损。

    Validates: Requirements 7.2, 7.3
    """
    segments = split_runs_by_script(text)

    assert "".join(seg_text for seg_text, _ in segments) == text

    prev_script = None
    for seg_text, script in segments:
        assert seg_text != ""
        assert script in (SCRIPT_CJK, SCRIPT_LATIN)
        for ch in seg_text:
            assert (is_cjk(ch) is True) == (script == SCRIPT_CJK)
        assert script != prev_script
        prev_script = script
# @AI_GENERATED: end

# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 6: 追溯校验判定正确且门槛等价于无错配

Property-based test for `traceability_check` from pre_delivery_gate.py.

逐页判定正确，门槛通过当且仅当无错配页；有错配时失败并标识全部不匹配页
(index, role, expected, actual)。

Validates: Requirements 4.1, 4.2, 4.3
"""

import os
import sys

from hypothesis import given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pre_delivery_gate import traceability_check  # noqa: E402
from section_style_binder import (  # noqa: E402
    FIXED_MAPPING,
    BoundPage,
    Role,
)

# 一组可能出现的 style_source 值：既含所有正确节名，也含明显错误的取值。
_WRONG_STYLE_SOURCES = ["cover", "content", "ending", "wrong", "", "COVER", "unknown"]


@st.composite
def _bound_page_sequences(draw):
    """生成随机 BoundPage 列表：随机 role，style_source 有时正确有时错误。

    对每页以一定概率取 FIXED_MAPPING[role]（正确），否则取任意候选值（可能恰好
    正确也可能错误），从而覆盖“全对 / 部分错配 / 全错”的输入空间。
    """
    page_count = draw(st.integers(min_value=0, max_value=60))
    pages = []
    for index in range(page_count):
        role = draw(st.sampled_from(list(Role)))
        use_correct = draw(st.booleans())
        if use_correct:
            style_source = FIXED_MAPPING[role]
        else:
            style_source = draw(st.sampled_from(_WRONG_STYLE_SOURCES))
        pages.append(
            BoundPage(
                index=index,
                role=role,
                style_source=style_source,
                slide_file=os.path.join(
                    "nonexistent_root", "ppt", "slides", f"slide{index + 1}.xml"
                ),
            )
        )
    return pages


@settings(max_examples=200)
@given(pages=_bound_page_sequences())
def test_traceability_check_correct_and_threshold(pages) -> None:
    """Property 6: 追溯校验判定正确且门槛等价于无错配。

    - passed 为 True 当且仅当每页 style_source == FIXED_MAPPING[role]（R4.1, R4.2）。
    - mismatches 恰好包含全部错配页，且每项为 (index, role, expected, actual)（R4.3）。

    Validates: Requirements 4.1, 4.2, 4.3
    """
    result = traceability_check(pages)

    # 独立计算期望的错配页集合与元组。
    expected_mismatches = [
        (page.index, page.role, FIXED_MAPPING[page.role], page.style_source)
        for page in pages
        if page.style_source != FIXED_MAPPING[page.role]
    ]

    # R4.1/R4.2: 门槛通过 iff 无任何错配页。
    assert result.passed == (len(expected_mismatches) == 0)

    # R4.3: 错配集合恰好等于独立计算所得（顺序无关的集合等价）。
    assert set(result.mismatches) == set(expected_mismatches)
    # 数量一致，防止重复/遗漏。
    assert len(result.mismatches) == len(expected_mismatches)

    # 每个 mismatch 元组结构正确：(index, role, expected, actual)。
    for index, role, expected, actual in result.mismatches:
        assert isinstance(role, Role)
        assert expected == FIXED_MAPPING[role]
        assert actual != expected
        # index 指向的页确实存在且信息一致。
        page = pages[index]
        assert page.role is role
        assert page.style_source == actual
# @AI_GENERATED: end

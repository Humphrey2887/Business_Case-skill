# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 4: 位置法角色识别

Property-based test for `detect_roles` positional role detection.

非空序列首页为 cover，首末之间每页为 content。

Validates: Requirements 2.1, 2.2
"""

import os
import sys

from hypothesis import given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section_style_binder import Role, detect_roles  # noqa: E402


@settings(max_examples=200)
@given(
    page_count=st.integers(min_value=1, max_value=500),
    ending_requested=st.booleans(),
)
def test_positional_role_detection_first_cover_middle_content(
    page_count: int, ending_requested: bool
) -> None:
    """Property 4: 非空序列首页为 cover；首末之间每页为 content。

    Validates: Requirements 2.1, 2.2
    """
    roles = detect_roles(page_count, ending_requested)

    # 结果长度与 page_count 一致（每页恰对应一个角色）。
    assert len(roles) == page_count

    # R2.1: 首页恒为 cover。
    assert roles[0] is Role.COVER

    # R2.2: 索引严格位于首末之间的每一页恒为 content。
    for middle_role in roles[1:-1]:
        assert middle_role is Role.CONTENT
# @AI_GENERATED: end

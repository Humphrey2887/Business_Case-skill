# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 4: 位置法角色识别

Property-based test (hypothesis) for `detect_roles` 位置法角色识别。

非空序列（page_count >= 1）首页为 cover；索引严格位于首末之间的每页为 content。

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
    page_count=st.integers(min_value=1, max_value=1000),
    ending_requested=st.booleans(),
)
def test_positional_first_cover_middle_content(
    page_count: int, ending_requested: bool
) -> None:
    """Property 4: 非空序列首页为 cover；首末之间每页为 content。

    对任意随机 page_count (>=1) 与 ending_requested，调用 detect_roles，断言：
      - result[0] == Role.COVER（首页恒为 cover）
      - 每个严格位于首末之间的索引 == Role.CONTENT（中间页恒为 content）

    Validates: Requirements 2.1, 2.2
    """
    roles = detect_roles(page_count, ending_requested)

    # 每页恰对应一个角色。
    assert len(roles) == page_count

    # R2.1: 非空序列首页恒为 cover。
    assert roles[0] is Role.COVER

    # R2.2: 每个严格位于首末之间（0 < index < last）的页恒为 content。
    for index in range(1, page_count - 1):
        assert roles[index] is Role.CONTENT
# @AI_GENERATED: end

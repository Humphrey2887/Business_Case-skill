# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 5: ending 可选性与末页角色

Property-based test (hypothesis, >=100 iterations) for `detect_roles` ending
optionality (Task 3.6).

对随机 page_count (>= 2) 与随机 ending_requested：
  - 请求 ending  → 末页角色为 Role.ENDING（绑定 ending 节样式）。
  - 未请求 ending → 末页角色为 Role.CONTENT 且整个序列不含任何 ending 角色页。

Validates: Requirements 2.3, 2.4, 3.1, 3.2, 1.3
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
    page_count=st.integers(min_value=2, max_value=500),
    ending_requested=st.booleans(),
)
def test_ending_optionality_and_last_page_role(
    page_count: int, ending_requested: bool
) -> None:
    """Property 5: 长度 >= 2 时末页角色由 ending_requested 确定性决定。

    - ending_requested 为真  → 末页为 Role.ENDING。
    - ending_requested 为假  → 末页为 Role.CONTENT 且序列不含任何 Role.ENDING 页。

    Validates: Requirements 2.3, 2.4, 3.1, 3.2, 1.3
    """
    roles = detect_roles(page_count, ending_requested)

    # 每页恰对应一个角色。
    assert len(roles) == page_count

    if ending_requested:
        # R2.3 / R3.2: 显式请求 ending 时末页恒为 ending（绑定 ending 节样式）。
        assert roles[-1] is Role.ENDING
    else:
        # R2.4: 未请求 ending 时末页判定为 content。
        assert roles[-1] is Role.CONTENT
        # R3.1 / 1.3: 未请求 ending 时成片不含任何 ending 角色页。
        assert Role.ENDING not in roles
# @AI_GENERATED: end

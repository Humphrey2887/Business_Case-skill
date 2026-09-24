# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 5: ending 可选性与末页角色

Property-based test for `detect_roles` ending optionality.

长度 >= 2 时：请求 ending 则末页为 ending 且绑定 ending 节样式；
未请求 ending 则末页为 content 且序列不含任何 ending 角色页。

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
@given(page_count=st.integers(min_value=2, max_value=500))
def test_ending_requested_last_page_is_ending(page_count: int) -> None:
    """Property 5 (请求 ending): 长度>=2 且显式请求 ending 时，末页角色为 ending。

    Validates: Requirements 2.3, 3.2
    """
    roles = detect_roles(page_count, ending_requested=True)

    # 每页恰对应一个角色。
    assert len(roles) == page_count

    # R2.3 / R3.2: 显式请求 ending 时末页恒为 ending 角色（绑定 ending 节样式）。
    assert roles[-1] is Role.ENDING


@settings(max_examples=200)
@given(page_count=st.integers(min_value=2, max_value=500))
def test_ending_not_requested_last_content_and_no_ending(page_count: int) -> None:
    """Property 5 (未请求 ending): 长度>=2 且未请求 ending 时，末页为 content
    且整个序列不含任何 ending 角色页。

    Validates: Requirements 2.4, 3.1, 1.3
    """
    roles = detect_roles(page_count, ending_requested=False)

    # 每页恰对应一个角色。
    assert len(roles) == page_count

    # R2.4: 未请求 ending 时末页判定为 content。
    assert roles[-1] is Role.CONTENT

    # R3.1 / 1.3: 未请求 ending 时成片不含任何 ending 角色页。
    assert all(role is not Role.ENDING for role in roles)
# @AI_GENERATED: end

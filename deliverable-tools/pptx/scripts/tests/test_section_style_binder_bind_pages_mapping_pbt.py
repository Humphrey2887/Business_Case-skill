# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 1: 角色→节确定性映射

Property-based test for `bind_pages` deterministic role→section mapping.

每张 cover 页 style_source == "cover"，每张 content 页 style_source == "content"。

Validates: Requirements 1.1, 1.2
"""

import os
import sys

from hypothesis import given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section_style_binder import (  # noqa: E402
    BoundPage,
    Role,
    SectionInfo,
    bind_pages,
)


def _dummy_sections() -> dict[str, SectionInfo]:
    """构造 cover/content/ending 三节固件。

    slide_ids 为空 → _slide_file_for_section 返回 None，_apply_section_layout
    best-effort 跳过物理改写，不触碰磁盘；bind_pages 的逻辑绑定始终生效。
    """
    return {
        "cover": SectionInfo(name="cover", section_id="{GUID-COVER}", slide_ids=[]),
        "content": SectionInfo(
            name="content", section_id="{GUID-CONTENT}", slide_ids=[]
        ),
        "ending": SectionInfo(name="ending", section_id="{GUID-ENDING}", slide_ids=[]),
    }


@settings(max_examples=200)
@given(
    page_count=st.integers(min_value=1, max_value=300),
    ending_requested=st.booleans(),
)
def test_role_section_deterministic_mapping(
    page_count: int, ending_requested: bool
) -> None:
    """Property 1: 绑定后每张 cover 页 style_source=="cover"，
    每张 content 页 style_source=="content"。

    使用不存在于磁盘的 dummy slide_file 路径；_apply_section_layout 以 best-effort
    方式跳过物理改写，故仅验证 bind_pages 的确定性逻辑绑定。

    Validates: Requirements 1.1, 1.2
    """
    # 生成序列：index 递增，role/style_source 由 bind_pages 覆写，slide_file 为占位路径。
    sequence = [
        BoundPage(
            index=i,
            role=Role.CONTENT,
            style_source="",
            slide_file=os.path.join(
                "nonexistent_root", "ppt", "slides", f"slide{i + 1}.xml"
            ),
        )
        for i in range(page_count)
    ]

    bound = bind_pages(sequence, _dummy_sections(), ending_requested)

    # 每页恰被绑定（返回序列长度不变）。
    assert len(bound) == page_count

    for page in bound:
        # R1.1: 角色为 cover 的页其 style_source 恒等于 "cover"。
        if page.role is Role.COVER:
            assert page.style_source == "cover"
        # R1.2: 角色为 content 的页其 style_source 恒等于 "content"。
        elif page.role is Role.CONTENT:
            assert page.style_source == "content"
# @AI_GENERATED: end

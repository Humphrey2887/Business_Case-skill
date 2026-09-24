# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 2: content 页样式来源一致性

Property-based test for `bind_pages` content-page style-source consistency.

含≥2 张 content 角色页的生成序列，所有 content 页绑定的 style_source
彼此相等，且共同指向同一 content 节样式来源（"content"）。

Validates: Requirements 1.4
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
    # page_count>=4 → 至少 2 张中间 content 页（首=cover、末=content 或 ending）。
    page_count=st.integers(min_value=4, max_value=300),
    ending_requested=st.booleans(),
)
def test_content_pages_share_single_style_source(
    page_count: int, ending_requested: bool
) -> None:
    """Property 2: 含≥2 张 content 页时，所有 content 页 style_source 彼此相等，
    共同指向同一 content 节样式来源。

    使用不存在于磁盘的 dummy slide_file 路径；_apply_section_layout 以 best-effort
    方式跳过物理改写，故仅验证 bind_pages 的确定性逻辑绑定。

    Validates: Requirements 1.4
    """
    # 生成序列：index 递增，role/style_source 由 bind_pages 覆写，slide_file 为占位路径。
    sequence = [
        BoundPage(
            index=i,
            role=Role.COVER,
            style_source="",
            slide_file=os.path.join(
                "nonexistent_root", "ppt", "slides", f"slide{i + 1}.xml"
            ),
        )
        for i in range(page_count)
    ]

    bound = bind_pages(sequence, _dummy_sections(), ending_requested)

    # 收集所有 content 角色页的 style_source。
    content_sources = [p.style_source for p in bound if p.role is Role.CONTENT]

    # page_count>=4 保证至少 2 张 content 页（首=cover，末=content/ending，中间≥2）。
    assert len(content_sources) >= 2

    # R1.4: 所有 content 页 style_source 彼此相等（集合仅含单一来源）。
    assert len(set(content_sources)) == 1
    # 且该唯一来源指向 content 节样式来源。
    assert content_sources[0] == "content"
# @AI_GENERATED: end

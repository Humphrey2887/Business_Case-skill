# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 8: 残留占位符 grep 门槛

Property-based test for `placeholder_grep_gate` from pre_delivery_gate.py.

命中 PLACEHOLDER_PATTERNS 任一项则门槛失败（返回非空且为模式子集）；
无命中则通过（返回 []）。并显式断言 `Cover Page Style`（任意大小写）触发命中。

Validates: Requirements 9.1, 9.2, 6.3
"""

import os
import re
import sys

from hypothesis import assume, given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pre_delivery_gate import (  # noqa: E402
    PLACEHOLDER_PATTERNS,
    placeholder_grep_gate,
)

# 可注入的占位符 token 样例：覆盖每个模式，含大小写变体与 "this...page/slide...layout"。
_INJECTION_TOKENS = [
    "xxxx",
    "XXXX",
    "lorem",
    "LOREM",
    "ipsum",
    "Ipsum",
    "Cover Page Style",
    "cover page style",
    "COVER PAGE STYLE",
    "this is the page layout",
    "This Slide Layout",
    "this old page master layout",
]

# 安全字母表：不含任何会构成占位符子串的字符组合。
# 关键约束：不含 'x'（避免 xxxx）、不含 'lorem'/'ipsum'/'cover'/'layout' 等词。
# 采用受限词表并用空格拼接，逐词再经 assume() 二次过滤以确保干净。
_SAFE_WORDS = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "summary",
    "revenue",
    "growth",
    "market",
    "strategy",
    "value",
    "tree",
    "node",
    "chart",
    "figure",
    "table",
    "result",
    "finding",
    "insight",
    "budget",
    "quarter",
]


def _matches(text: str) -> list[str]:
    """独立实现：返回命中的模式子集（re.IGNORECASE），作为 oracle。"""
    return [p for p in PLACEHOLDER_PATTERNS if re.search(p, text, re.IGNORECASE)]


@settings(max_examples=200)
@given(
    prefix=st.text(alphabet="abcdefg 0123456789", max_size=40),
    tokens=st.lists(st.sampled_from(_INJECTION_TOKENS), min_size=1, max_size=4),
    suffix=st.text(alphabet="abcdefg 0123456789", max_size=40),
)
def test_injection_makes_gate_fail(prefix, tokens, suffix) -> None:
    """注入性质：文本嵌入任一占位符 token → 门槛失败（非空且为模式子集）。

    Validates: Requirements 9.1, 9.2, 6.3
    """
    deck_text = prefix + " " + " ".join(tokens) + " " + suffix
    hits = placeholder_grep_gate(deck_text)

    # 门槛失败：至少命中一项。
    assert hits, f"expected non-empty hits for injected tokens, got {hits!r}"
    # 返回项必须是 PLACEHOLDER_PATTERNS 的子集（不返回未定义模式）。
    assert set(hits).issubset(set(PLACEHOLDER_PATTERNS))
    # 与独立 oracle 一致。
    assert hits == _matches(deck_text)


@settings(max_examples=200)
@given(words=st.lists(st.sampled_from(_SAFE_WORDS), max_size=30))
def test_clean_text_passes_gate(words) -> None:
    """干净性质：不含任何占位符 token 的文本 → 门槛通过（返回 []）。

    使用受限词表构造文本，再以 assume() 二次过滤，确保确实不含任何命中。

    Validates: Requirements 9.1, 9.2, 6.3
    """
    deck_text = " ".join(words)
    # 二次保险：若生成文本意外命中任一模式，则跳过该样例。
    assume(not _matches(deck_text))

    hits = placeholder_grep_gate(deck_text)
    assert hits == [], f"expected clean text to pass gate, got {hits!r}"


@settings(max_examples=200)
@given(
    prefix=st.text(alphabet="abcdefg 0123456789", max_size=40),
    variant=st.sampled_from(
        ["Cover Page Style", "cover page style", "COVER PAGE STYLE", "CoVeR PaGe StYlE"]
    ),
    suffix=st.text(alphabet="abcdefg 0123456789", max_size=40),
)
def test_cover_page_style_always_hits(prefix, variant, suffix) -> None:
    """显式性质：`Cover Page Style`（任意大小写）必定触发命中。

    Validates: Requirements 9.1, 9.2, 6.3
    """
    deck_text = prefix + " " + variant + " " + suffix
    hits = placeholder_grep_gate(deck_text)
    assert "Cover Page Style" in hits
# @AI_GENERATED: end

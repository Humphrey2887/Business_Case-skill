# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 12: 价值树违规阻断

Property-based test for `value_tree_check` from pre_delivery_gate.py.

对四类违规（flattened / missing_operator / missing_edge / multi_parent），
构造展现该违规的 ValueTreeModel，断言 value_tree_check 返回非空 issues（门槛失败），
且返回的 issues 中包含与注入违规类别匹配的 kind。并覆盖多违规组合场景，
断言所有期望 kind 均出现。

Validates: Requirements 10.4
"""

import os
import sys

from hypothesis import given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pre_delivery_gate import (  # noqa: E402
    build_value_tree_model,
    value_tree_check,
)

_VIOLATION_KINDS = ["flattened", "missing_operator", "missing_edge", "multi_parent"]


def _build_violation_model(kind: str, node_ids, parent_a, parent_b, child):
    """按指定违规类别构造一个展现该违规的 ValueTreeModel。

    - flattened:        有纯文字但无任何节点框（flattened_text 非空 + nodes 空）。
    - missing_operator: expects_operators=True 但 operators 为空。
    - missing_edge:     expects_edges=True 但 edges 为空。
    - multi_parent:     某 child 在 edges 中拥有两个不同 parent。
    """
    if kind == "flattened":
        return build_value_tree_model(
            nodes=[],
            flattened_text="营收 = 单价 × 销量",
        )
    if kind == "missing_operator":
        return build_value_tree_model(
            nodes=node_ids,
            operators=[],
            expects_operators=True,
        )
    if kind == "missing_edge":
        return build_value_tree_model(
            nodes=node_ids,
            edges=[],
            expects_edges=True,
        )
    if kind == "multi_parent":
        # 保证两个 parent 不同且 child 与它们不同。
        return build_value_tree_model(
            nodes=node_ids,
            edges=[(parent_a, child), (parent_b, child)],
        )
    raise AssertionError(f"unknown violation kind: {kind!r}")


@settings(max_examples=200)
@given(
    kind=st.sampled_from(_VIOLATION_KINDS),
    node_ids=st.lists(st.integers(min_value=0, max_value=50), min_size=1, max_size=6),
    triple=st.lists(
        st.integers(min_value=100, max_value=200), min_size=3, max_size=3, unique=True
    ),
)
def test_each_violation_blocks_gate(kind, node_ids, triple):
    """性质：任一违规类别 → value_tree_check 返回非空 issues 且含对应 kind。

    Validates: Requirements 10.4
    """
    parent_a, parent_b, child = triple
    model = _build_violation_model(kind, node_ids, parent_a, parent_b, child)

    issues = value_tree_check(model)

    # 门槛失败：至少一个 issue。
    assert issues, f"expected non-empty issues for violation {kind!r}, got {issues!r}"
    # 返回的 issues 中包含注入的违规类别。
    returned_kinds = {issue.kind for issue in issues}
    assert kind in returned_kinds, (
        f"expected kind {kind!r} in returned issues, got {returned_kinds!r}"
    )


@settings(max_examples=200)
@given(
    node_ids=st.lists(st.integers(min_value=0, max_value=50), min_size=1, max_size=6),
    triple=st.lists(
        st.integers(min_value=100, max_value=200), min_size=3, max_size=3, unique=True
    ),
)
def test_combined_violations_report_all_kinds(node_ids, triple):
    """性质：多违规组合 → issues 中同时出现全部四类 kind，门槛失败。

    Validates: Requirements 10.4
    """
    parent_a, parent_b, child = triple
    # 组合三类可共存的违规：
    #   flattened        —— 有纯文字但无节点框；
    #   missing_operator —— expects_operators=True 且 operators 为空；
    #   multi_parent     —— 同一 child 拥有两个不同 parent（需 edges 非空）。
    # 注意 multi_parent 需要非空 edges，与 missing_edge（要求 edges 为空）互斥，
    # 故此组合覆盖三类；missing_edge 已在上面的逐类测试中单独覆盖。
    model = build_value_tree_model(
        nodes=[],
        operators=[],
        edges=[(parent_a, child), (parent_b, child)],
        flattened_text="营收 = 单价 × 销量",
        expects_operators=True,
        expects_edges=False,
    )

    issues = value_tree_check(model)
    returned_kinds = {issue.kind for issue in issues}

    assert issues, "expected non-empty issues for combined violations"
    for expected in ("flattened", "missing_operator", "multi_parent"):
        assert expected in returned_kinds, (
            f"expected kind {expected!r} in {returned_kinds!r}"
        )
# @AI_GENERATED: end

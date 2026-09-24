# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 11: 价值树节点化结构保持

Property-based test for `value_tree_check` from pre_delivery_gate.py.

WELL-FORMED case（结构保持）：生成合法的节点化价值树模型 —
  - nodes 非空（每变量为独立直角框）；
  - 当 expects_operators 时，至少含一个来自 ×＋－÷＝ 的运算符连接各框；
  - edges 构成单父树（每个非根节点恰有一个父，父取自更早出现的节点）；
  - flattened_text 为空。
断言 value_tree_check 返回 []（无违规），且构建 + 校验不改变/丢失
运算符集合与父子边集合（模型仍暴露与构造时一致的 operators 集合与 edges 集合）。

Validates: Requirements 10.1, 10.2, 10.3
"""

import os
import sys

from hypothesis import given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pre_delivery_gate import (  # noqa: E402
    VALUE_TREE_OPERATORS,
    build_value_tree_model,
    value_tree_check,
)

# 合法运算符列表（排序以确定性采样）。
_OPERATORS = sorted(VALUE_TREE_OPERATORS)


@st.composite
def well_formed_value_trees(draw):
    """生成结构良好的节点化价值树模型。

    - nodes: 非空、id 唯一（node_0, node_1, ...）。
    - edges: 单父树 —— 每个非根节点（index>=1）恰分配一个父，父来自更早出现
             的节点（index < 自身），因此不可能出现多父/环，且每个 child 唯一。
    - operators: expects_operators 时至少 1 个（来自 ×＋－÷＝）；否则可为空。
    - flattened_text: 恒为空（well-formed 不拍平）。
    """
    node_count = draw(st.integers(min_value=1, max_value=8))
    nodes = [f"node_{i}" for i in range(node_count)]

    # 单父树：每个非根节点恰一父（取自更早节点）。
    expects_edges = node_count >= 2 and draw(st.booleans())
    edges = []
    if expects_edges:
        for child_index in range(1, node_count):
            parent_index = draw(st.integers(min_value=0, max_value=child_index - 1))
            edges.append((nodes[parent_index], nodes[child_index]))

    # 运算符：expects_operators 时至少一个。
    expects_operators = draw(st.booleans())
    if expects_operators:
        operators = draw(
            st.lists(st.sampled_from(_OPERATORS), min_size=1, max_size=6)
        )
    else:
        operators = draw(st.lists(st.sampled_from(_OPERATORS), min_size=0, max_size=6))

    model = build_value_tree_model(
        nodes=nodes,
        operators=operators,
        edges=edges,
        flattened_text="",
        expects_operators=expects_operators,
        expects_edges=expects_edges,
    )
    return model, operators, edges


@settings(max_examples=200)
@given(well_formed_value_trees())
def test_well_formed_value_tree_passes(payload) -> None:
    """结构良好的节点化价值树 → value_tree_check 返回 []（无违规）。

    Validates: Requirements 10.1, 10.2, 10.3
    """
    model, _operators, _edges = payload
    issues = value_tree_check(model)
    assert issues == [], f"expected no issues for well-formed model, got {issues!r}"


@settings(max_examples=200)
@given(well_formed_value_trees())
def test_operator_and_edge_sets_preserved(payload) -> None:
    """结构保持：构建 + 校验不改变/丢失运算符集合与父子边集合。

    模型仍暴露与构造时一致的 operators 集合与 edges 集合。

    Validates: Requirements 10.1, 10.2, 10.3
    """
    model, operators, edges = payload

    # 运算符集合保持一致。
    assert set(model.operators) == set(operators)
    # 运算符均为合法运算符集合子集。
    assert set(model.operators).issubset(VALUE_TREE_OPERATORS)
    # 父子边集合保持一致。
    assert set(model.edges) == set(edges)

    # 单父不变量：每个 child 恰有一个 parent。
    parents_by_child: dict = {}
    for parent, child in model.edges:
        parents_by_child.setdefault(child, set()).add(parent)
    for child, parents in parents_by_child.items():
        assert len(parents) == 1, f"child {child!r} has multiple parents {parents!r}"

    # 校验通过并不改变模型暴露的集合（再次读取仍一致）。
    value_tree_check(model)
    assert set(model.operators) == set(operators)
    assert set(model.edges) == set(edges)
# @AI_GENERATED: end

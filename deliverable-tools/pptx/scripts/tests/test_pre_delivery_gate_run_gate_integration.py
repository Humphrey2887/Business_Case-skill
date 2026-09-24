# @AI_GENERATED
"""Feature: pptx-template-section-styling, run_gate integration test

run_gate 与 CLI `_main` 的集成测试（pytest，示例法——非属性测试）。

组合 G1（追溯校验）/ G2（残留占位符门槛）/ G3（价值树节点化校验）各
通过/失败场景，断言聚合语义（任一失败 → GateReport.passed=False）与 CLI
非零退出码，验证「阻断出片成功声明」这一门槛职责。

覆盖场景：
  1. 全通过：正确绑定页 + 干净 deck_text + 合法 value_tree_model → passed True。
  2. 仅 G1 失败：一页 style_source 与 FIXED_MAPPING[role] 不符 → passed False，
     trace.passed False。
  3. 仅 G2 失败：干净页 + deck_text 含占位符 → passed False，placeholder_hits 非空。
  4. 仅 G3 失败：合法页 + 干净文本 + 违规 value_tree_model（拍平）→ passed False，
     value_tree_issues 非空。
  5. value_tree_model=None → G3 跳过（issues 为空），passed 取决于 G1/G2。

CLI `_main`（阻断语义）：
  - --deck-text 指向含占位符的临时文件 → 返回 2（门槛失败，非零退出阻断）。
  - --deck-text 指向干净文本、无 trace/value-tree → 返回 0（通过）。

Validates: Requirements 4.2, 9.2, 10.4
"""

import os
import sys

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pre_delivery_gate import (  # noqa: E402
    GateReport,
    build_value_tree_model,
    run_gate,
    _main,
)
from section_style_binder import (  # noqa: E402
    FIXED_MAPPING,
    BoundPage,
    Role,
)


# --- 固件构造辅助 -----------------------------------------------------------


def _page(index: int, role: Role, style_source: str | None = None) -> BoundPage:
    """构造 BoundPage；style_source 缺省取 FIXED_MAPPING[role]（正确绑定）。"""
    if style_source is None:
        style_source = FIXED_MAPPING[role]
    return BoundPage(
        index=index,
        role=role,
        style_source=style_source,
        slide_file=f"unpacked/ppt/slides/slide{index + 1}.xml",
    )


def _correctly_bound_pages() -> list[BoundPage]:
    """一组正确绑定的页序列（cover / content / ending 均 style_source 匹配）。"""
    return [
        _page(0, Role.COVER),
        _page(1, Role.CONTENT),
        _page(2, Role.ENDING),
    ]


def _clean_deck_text() -> str:
    """无任何残留占位符的成片正文文本。"""
    return "本页正文为交付级中文内容，无残留占位符，可继续出片。"


def _valid_value_tree_model():
    """合法价值树模型：节点化直角框 + 运算符连接 + 单父树。"""
    return build_value_tree_model(
        nodes=["营收", "单价", "销量"],
        operators=["＝", "×"],
        edges=[("营收", "单价"), ("营收", "销量")],
        flattened_text="",
        expects_operators=True,
        expects_edges=True,
    )


# --- run_gate 聚合语义场景 --------------------------------------------------


def test_run_gate_all_pass():
    """场景1：G1/G2/G3 全通过 → GateReport.passed True，各子结果均通过。"""
    report = run_gate(
        _correctly_bound_pages(),
        _clean_deck_text(),
        _valid_value_tree_model(),
    )
    assert isinstance(report, GateReport)
    assert report.passed is True
    assert report.trace.passed is True
    assert report.placeholder_hits == []
    assert report.value_tree_issues == []


def test_run_gate_g1_fail_only():
    """场景2：仅 G1 失败（一页 style_source 错配）→ passed False，trace 失败。"""
    pages = _correctly_bound_pages()
    # 将 content 页错绑到 cover 节，制造 style_source != FIXED_MAPPING[role]。
    pages[1] = _page(1, Role.CONTENT, style_source="cover")
    report = run_gate(pages, _clean_deck_text(), _valid_value_tree_model())
    assert report.passed is False
    assert report.trace.passed is False
    assert len(report.trace.mismatches) == 1
    # 其余两项门槛应保持通过，隔离失败来源为 G1。
    assert report.placeholder_hits == []
    assert report.value_tree_issues == []


def test_run_gate_g2_fail_only():
    """场景3：仅 G2 失败（deck_text 含占位符）→ passed False，命中非空。"""
    deck_text = "封面标题\nCover Page Style\n正文 xxxx 未替换。"
    report = run_gate(
        _correctly_bound_pages(),
        deck_text,
        _valid_value_tree_model(),
    )
    assert report.passed is False
    assert report.placeholder_hits  # 非空
    # 隔离失败来源为 G2。
    assert report.trace.passed is True
    assert report.value_tree_issues == []


def test_run_gate_g3_fail_only():
    """场景4：仅 G3 失败（等式被拍平为纯文字）→ passed False，issues 非空。"""
    flattened_model = build_value_tree_model(
        nodes=[],  # 无独立节点框
        operators=[],
        edges=[],
        flattened_text="营收＝单价×销量",  # 拍平为纯文字
        expects_operators=False,
        expects_edges=False,
    )
    report = run_gate(
        _correctly_bound_pages(),
        _clean_deck_text(),
        flattened_model,
    )
    assert report.passed is False
    assert report.value_tree_issues  # 非空
    assert any(issue.kind == "flattened" for issue in report.value_tree_issues)
    # 隔离失败来源为 G3。
    assert report.trace.passed is True
    assert report.placeholder_hits == []


def test_run_gate_value_tree_none_skips_g3():
    """场景5：value_tree_model=None → G3 跳过（issues 空），passed 取决于 G1/G2。"""
    # G1/G2 均通过时，跳过 G3 仍应整体通过。
    report_pass = run_gate(_correctly_bound_pages(), _clean_deck_text(), None)
    assert report_pass.value_tree_issues == []
    assert report_pass.passed is True

    # G2 失败时，即便 G3 跳过，整体仍失败——证明跳过 G3 不掩盖其他门槛。
    report_fail = run_gate(
        _correctly_bound_pages(),
        "残留 lorem ipsum 文本。",
        None,
    )
    assert report_fail.value_tree_issues == []
    assert report_fail.placeholder_hits
    assert report_fail.passed is False


def test_run_gate_multiple_gates_fail_aggregate():
    """聚合语义补充：G1 与 G2 同时失败 → passed False，两项失败信号并存。"""
    pages = _correctly_bound_pages()
    pages[0] = _page(0, Role.COVER, style_source="content")
    report = run_gate(pages, "封面 xxxx 未替换", _valid_value_tree_model())
    assert report.passed is False
    assert report.trace.passed is False
    assert report.placeholder_hits


# --- CLI _main 非零退出阻断语义 --------------------------------------------


def test_main_placeholder_returns_2(tmp_path):
    """CLI：--deck-text 含占位符 → _main 返回 2（门槛失败，非零退出阻断出片）。"""
    deck_file = tmp_path / "deck_text.md"
    deck_file.write_text("正文 xxxx 尚未替换的占位符。", encoding="utf-8")
    exit_code = _main(["--deck-text", str(deck_file)])
    assert exit_code == 2


def test_main_clean_returns_0(tmp_path):
    """CLI：干净 deck_text、无 trace/value-tree → _main 返回 0（通过）。"""
    deck_file = tmp_path / "deck_text.md"
    deck_file.write_text("交付级正文，无残留占位符。", encoding="utf-8")
    exit_code = _main(["--deck-text", str(deck_file)])
    assert exit_code == 0


def test_main_trace_json_g1_fail_returns_2(tmp_path):
    """CLI：--trace-json 提供错配页事实 → G1 失败 → _main 返回 2。"""
    import json

    deck_file = tmp_path / "deck_text.md"
    deck_file.write_text("干净正文。", encoding="utf-8")
    trace_file = tmp_path / "trace.json"
    trace_file.write_text(
        json.dumps(
            [
                {"index": 0, "role": "COVER", "style_source": "cover"},
                # content 页错绑到 cover → G1 失败。
                {"index": 1, "role": "CONTENT", "style_source": "cover"},
            ]
        ),
        encoding="utf-8",
    )
    exit_code = _main(
        ["--deck-text", str(deck_file), "--trace-json", str(trace_file)]
    )
    assert exit_code == 2
# @AI_GENERATED: end

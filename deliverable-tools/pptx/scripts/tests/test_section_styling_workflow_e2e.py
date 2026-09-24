# @AI_GENERATED
"""Feature: pptx-template-section-styling, end-to-end integration (Validates: Requirements 1.1, 4.2, 9.2, 10.4)

端到端集成测试（自动化，pytest 示例法）——以 unpack 母版固件驱动 binder→gate
全链路，不含手动运行 PowerPoint/LibreOffice。

被测编排入口：`section_styling_workflow.py`（Task 10.1 布线成果），它把
`section_style_binder.parse_sections/bind_pages` 与 `pre_delivery_gate.run_gate`
串接为「编辑阶段之后、pack.py 之前」的核心链路：
    unpack 母版 → build_sequence → parse_sections + bind_pages
        → reconstruct_style_sources（从成片 layout 反解实际 Style_Source）
        → run_gate（聚合 G1 追溯 / G2 残留占位符 / G3 价值树节点化）

母版固件：在测试时用 `office/unpack.py` 将母版模板解包到 pytest tmp_path。
母版路径：<skill_root>/templates/pptx/masters/envision-china-template-2023.pptx，
其中 skill_root 由测试文件向上回溯到「同时含 SKILL.md 与 templates/pptx/masters」
的目录稳健定位。母版含 cover/content/ending 三节，分别对应 slide1/slide2/slide3
（layout 1/14/4）。若母版缺失或解包失败，则以清晰理由 pytest.skip（不失败）。

覆盖场景（全部经由 binder→gate，无手动出片）：
  1. 正常成片通过（ending 请求 / 不请求两条路径）——Requirements 1.1。
  2. 错配被阻断（篡改某页 Style_Source 使追溯校验失败）——Requirements 4.2。
  3. 残留占位符被阻断（deck_text 含 "Cover Page Style" / "xxxx"）——Requirements 9.2。
  4. 价值树违规被阻断（拍平 / 非单父的价值树模型）——Requirements 10.4。

Validates: Requirements 1.1, 4.2, 9.2, 10.4
"""

import os
import sys
from dataclasses import replace

import pytest

# 允许从 tests/ 导入上级 scripts/ 的被测模块，以及 office/ 的 unpack 模块。
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_TESTS_DIR)
_OFFICE_DIR = os.path.join(_SCRIPTS_DIR, "office")
sys.path.insert(0, _SCRIPTS_DIR)
sys.path.insert(0, _OFFICE_DIR)

from section_styling_workflow import (  # noqa: E402
    UNRESOLVED_STYLE_SOURCE,
    parse_bind_and_gate,
)
from section_style_binder import Role  # noqa: E402
from pre_delivery_gate import build_value_tree_model, run_gate  # noqa: E402

# 干净成片正文（无任何残留占位符），供正常成片与隔离场景复用。
_CLEAN_DECK_TEXT = "本页正文为交付级中文内容，无残留占位符，可继续出片。"


# ---------------------------------------------------------------------------
# skill 根定位与母版解包固件
# ---------------------------------------------------------------------------


def _find_skill_root() -> str | None:
    """从测试文件向上回溯，返回同时含 SKILL.md 与 templates/pptx/masters 的目录。

    以「两者并存」为判据，可稳健区分 skill 根与其外层同名/含 SKILL.md 的父目录。
    找不到时返回 None。
    """
    current = _TESTS_DIR
    while True:
        skill_md = os.path.join(current, "SKILL.md")
        masters_dir = os.path.join(current, "templates", "pptx", "masters")
        if os.path.isfile(skill_md) and os.path.isdir(masters_dir):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # 抵达文件系统根
            return None
        current = parent


def _master_path() -> str | None:
    """返回母版模板绝对路径；不存在时返回 None（供 skip 判定）。"""
    root = _find_skill_root()
    if root is None:
        return None
    master = os.path.join(
        root, "templates", "pptx", "masters", "envision-china-template-2023.pptx"
    )
    return master if os.path.isfile(master) else None


@pytest.fixture
def unpacked_master(tmp_path) -> str:
    """将母版模板解包到 tmp_path 并返回解包根目录。

    通过 import 调用 office/unpack.py 的 unpack()（确定性、不依赖子进程/`py`）。
    母版缺失或解包失败（无 ppt/presentation.xml）时 pytest.skip，避免环境性失败。
    tmp_path 由 pytest 自动清理，无需手工清理临时文件。
    """
    master = _master_path()
    if master is None:
        pytest.skip(
            "母版模板 templates/pptx/masters/envision-china-template-2023.pptx 不存在，"
            "跳过端到端集成测试。"
        )

    import unpack as unpack_module  # office/ 已在 sys.path

    dest = tmp_path / "unpacked"
    _, message = unpack_module.unpack(
        master, str(dest), merge_runs=False, simplify_redlines=False
    )
    presentation = dest / "ppt" / "presentation.xml"
    if "Error" in message or not presentation.exists():
        pytest.skip(f"母版解包失败，跳过端到端集成测试：{message}")
    return str(dest)


# ---------------------------------------------------------------------------
# 场景 1：正常成片通过（Requirements 1.1）
# ---------------------------------------------------------------------------


def test_normal_deck_passes_with_ending_requested(unpacked_master):
    """正常成片 + 显式请求 ending：全链路通过，cover→cover / content→content /
    ending→ending 逐页可追溯（Requirements 1.1）。"""
    result = parse_bind_and_gate(
        unpacked_master, _CLEAN_DECK_TEXT, ending_requested=True
    )

    assert result.report.passed is True
    assert result.report.trace.passed is True
    assert result.report.placeholder_hits == []
    assert result.report.value_tree_issues == []

    verified = result.verified_pages
    assert len(verified) == 3
    # 逐页：role → 反解自成片 layout 的实际 Style_Source 均匹配固定映射。
    assert verified[0].role == Role.COVER and verified[0].style_source == "cover"
    assert verified[1].role == Role.CONTENT and verified[1].style_source == "content"
    assert verified[2].role == Role.ENDING and verified[2].style_source == "ending"


def test_normal_deck_passes_without_ending(unpacked_master):
    """正常成片 + 不请求 ending：末页判定为 content 并绑定 content 节，全链路通过，
    序列不含任何 ending 角色页（Requirements 1.1 / 3.1）。"""
    result = parse_bind_and_gate(
        unpacked_master, _CLEAN_DECK_TEXT, ending_requested=False
    )

    assert result.report.passed is True
    assert result.report.trace.passed is True

    verified = result.verified_pages
    assert len(verified) == 3
    assert verified[0].role == Role.COVER and verified[0].style_source == "cover"
    assert verified[1].role == Role.CONTENT and verified[1].style_source == "content"
    # 末页 role 回落为 content，且反解 Style_Source 亦为 content（binder 已重指向）。
    assert verified[2].role == Role.CONTENT and verified[2].style_source == "content"
    # 不请求 ending 时，成片不含任何 ending 角色页。
    assert all(page.role != Role.ENDING for page in verified)


# ---------------------------------------------------------------------------
# 场景 2：错配被阻断（Requirements 4.2）
# ---------------------------------------------------------------------------


def test_style_source_mismatch_is_blocked(unpacked_master):
    """将某页 Style_Source 篡改为错误节，追溯校验失败 → 门槛阻断出片（Requirements 4.2）。

    先经 binder→gate 得到通过基线，再故意把 content 页的 style_source 指向 "ending"
    （错配），直接以篡改后的 verified_pages 重跑 run_gate，验证 G1 失败即整体阻断。
    """
    result = parse_bind_and_gate(
        unpacked_master, _CLEAN_DECK_TEXT, ending_requested=True
    )
    assert result.report.passed is True  # 基线：未篡改时通过

    tampered = list(result.verified_pages)
    # content 页（index 1）错绑到 ending 节，制造 style_source != FIXED_MAPPING[role]。
    tampered[1] = replace(tampered[1], style_source="ending")

    report = run_gate(tampered, _CLEAN_DECK_TEXT)
    assert report.passed is False
    assert report.trace.passed is False
    # 错配页应被标识：content 页期望 content、实际 ending。
    mismatch_roles = [role for (_, role, _, _) in report.trace.mismatches]
    assert Role.CONTENT in mismatch_roles
    assert any(
        expected == "content" and actual == "ending"
        for (_, _, expected, actual) in report.trace.mismatches
    )


def test_unresolved_style_source_is_blocked(unpacked_master):
    """无法反解实际节（哨兵 UNRESOLVED）亦视为错配 → 门槛阻断（Requirements 4.2）。"""
    result = parse_bind_and_gate(
        unpacked_master, _CLEAN_DECK_TEXT, ending_requested=True
    )
    assert result.report.passed is True

    tampered = list(result.verified_pages)
    tampered[0] = replace(tampered[0], style_source=UNRESOLVED_STYLE_SOURCE)

    report = run_gate(tampered, _CLEAN_DECK_TEXT)
    assert report.passed is False
    assert report.trace.passed is False


# ---------------------------------------------------------------------------
# 场景 3：残留占位符被阻断（Requirements 9.2）
# ---------------------------------------------------------------------------


def test_placeholder_residue_is_blocked(unpacked_master):
    """deck_text 含 "Cover Page Style" / "xxxx" 残留占位符 → 门槛阻断（Requirements 9.2）。"""
    deck_text = "封面标题\nCover Page Style\n正文 xxxx 尚未替换。"
    result = parse_bind_and_gate(
        unpacked_master, deck_text, ending_requested=True
    )

    assert result.report.passed is False
    assert result.report.placeholder_hits  # 命中非空
    # 绑定本身仍应正确（隔离失败来源为 G2 残留占位符门槛）。
    assert result.report.trace.passed is True


# ---------------------------------------------------------------------------
# 场景 4：价值树违规被阻断（Requirements 10.4）
# ---------------------------------------------------------------------------


def test_value_tree_flattened_is_blocked(unpacked_master):
    """价值树被拍平为纯文字（无独立直角框）→ 门槛阻断（Requirements 10.4）。"""
    flattened_model = build_value_tree_model(
        nodes=[],
        operators=[],
        edges=[],
        flattened_text="营收＝单价×销量",  # 塌缩为纯文字
        expects_operators=False,
        expects_edges=False,
    )
    result = parse_bind_and_gate(
        unpacked_master,
        _CLEAN_DECK_TEXT,
        ending_requested=True,
        value_tree_model=flattened_model,
    )

    assert result.report.passed is False
    assert result.report.value_tree_issues  # 非空
    assert any(issue.kind == "flattened" for issue in result.report.value_tree_issues)
    # 隔离失败来源为 G3。
    assert result.report.trace.passed is True
    assert result.report.placeholder_hits == []


def test_value_tree_multi_parent_is_blocked(unpacked_master):
    """价值树出现非单父结构（某子节点多父）→ 门槛阻断（Requirements 10.4）。"""
    multi_parent_model = build_value_tree_model(
        nodes=["营收", "单价", "销量", "利润"],
        operators=["＝", "×"],
        # 子节点 "销量" 同时有 "营收" 与 "利润" 两个父，违反单父树。
        edges=[("营收", "单价"), ("营收", "销量"), ("利润", "销量")],
        expects_operators=True,
        expects_edges=True,
    )
    result = parse_bind_and_gate(
        unpacked_master,
        _CLEAN_DECK_TEXT,
        ending_requested=True,
        value_tree_model=multi_parent_model,
    )

    assert result.report.passed is False
    assert any(
        issue.kind == "multi_parent" for issue in result.report.value_tree_issues
    )
# @AI_GENERATED: end

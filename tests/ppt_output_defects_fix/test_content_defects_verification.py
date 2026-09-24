# @AI_GENERATED
"""
Fix-checking verification test — CONTENT-family defects (1.5-1.7)
spec: .kiro/specs/ppt-output-defects-fix  (Property 2: Bug Condition)

WHAT THIS IS
------------
This bugfix repairs INSTRUCTIONAL ASSETS (markdown), not executable code
(the original `build_deck.py` was deleted during post-delivery cleanup). So
the "tests" here are ASSET-CONSISTENCY STATIC CHECKS: they statically inspect
the real asset files and assert the FIXED state of the instructional assets.

This is the CONTENT-family counterpart to test_form_defects_exploration.py
(which covers the FORM family 1.1-1.4). It follows the SAME asset-consistency
static-check pattern, location and helpers.

EXPECTED OUTCOME (fix-checking protocol)
----------------------------------------
These assertions encode the FIXED state described by design.md
"Correctness Properties / Property 2" and "Fix Implementation" for the
content family (1.5-1.7). After the fix (tasks 3.2/3.3/3.4 + 3.1 nodeization)
is implemented, this test is expected to PASS, validating the repair:

  1.5  ppt-deck-mapping.md P8 carries an explicit precedence ruling that
       大类分组相邻 OUTRANKS 价值降序, still reaffirms 柱色与大类解释卡严格同色 /
       图例不得两类同色, and the pre-existing 「按大类分组、同组相邻排列」 survives.
  1.6  pptx-tool.md carries the value-tree nodeization mandatory guidance
       (等式逐项成独立直角框 / 单父树 / 关键影响因子前置 / 保留运算符与父子关系)
       AND a generation-time enforced check (节点化未满足即阻断/返工).
  1.7a SKILL.md §3.1 carves a pain-point P-x exception (痛点代号 permitted in
       the value-tree pain column as 「代号（中文名）」) while SC-x and yaml keys
       remain forbidden; ppt-deck-mapping.md still uses 「代号（中文名）」 (both
       files consistent — codenames kept); the absolute-prohibition wording
       ("PPT 上只出现痛点中文名，不出现 `P-1` 这类代号") is GONE (contradiction
       resolved).
  1.7b 03-value-tree-guide.md and 05-pain-point-guide.md carry the delivery-md
       carrier structure for the pain column (代号（中文名)) AND the AI-scenario
       three-part explanation 『运用[什么技术] → 实现[什么功能] → 达成[什么目标]』.

Validates: Requirements 2.5, 2.6, 2.7
"""

import re
from pathlib import Path

import pytest

# Repo root = <repo>/tests/ppt_output_defects_fix/this_file.py -> up 3
REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = REPO_ROOT / "SKILL.md"
PPTX_TOOL = REPO_ROOT / "deliverable-tools" / "pptx" / "pptx-tool.md"
STANDARDS_DIR = REPO_ROOT / "workflows" / "business-pain-point" / "standards"
DECK_MAP = STANDARDS_DIR / "ppt-deck-mapping.md"
VALUE_TREE_GUIDE = STANDARDS_DIR / "03-value-tree-guide.md"
PAIN_POINT_GUIDE = STANDARDS_DIR / "05-pain-point-guide.md"


def _load(path: Path) -> str:
    assert path.is_file(), f"asset not found (cannot run static check): {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def skill_text() -> str:
    return _load(SKILL_MD)


@pytest.fixture(scope="module")
def pptx_tool_text() -> str:
    return _load(PPTX_TOOL)


@pytest.fixture(scope="module")
def deck_map_text() -> str:
    return _load(DECK_MAP)


@pytest.fixture(scope="module")
def value_tree_guide_text() -> str:
    return _load(VALUE_TREE_GUIDE)


@pytest.fixture(scope="module")
def pain_point_guide_text() -> str:
    return _load(PAIN_POINT_GUIDE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _missing(text: str, needles) -> list:
    """Return the list of needles MISSING from text (substring, case-insensitive)."""
    low = text.lower()
    return [n for n in needles if n.lower() not in low]


def _matches_any(text: str, patterns) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


# ---------------------------------------------------------------------------
# 1.5 — P8 grouping ruling (大类分组相邻 优先于 价值降序)
# ---------------------------------------------------------------------------

def test_1_5_p8_grouping_precedence_ruling_present(deck_map_text):
    """FIXED state: ppt-deck-mapping.md P8 must contain an explicit precedence
    ruling that 「大类分组相邻」 OUTRANKS 「价值降序」 (grouping-adjacency takes
    precedence over value-descending), still reaffirms 柱色与右侧大类解释卡严格
    同色 / 图例不得两类同色, and keeps the pre-existing 「按大类分组、同组相邻排列」
    requirement.
    """
    text = deck_map_text

    # explicit precedence ruling: 大类分组相邻 > 价值降序
    has_precedence_ruling = _matches_any(
        text,
        [
            r"大类分组相邻.{0,8}优先于.{0,8}价值降序",
            r"「大类分组相邻」.{0,12}优先于.{0,12}「价值降序」",
            r"分组相邻.{0,8}>\s*价值降序",
            r"先按大类分组使同类相邻[，,].{0,12}组内再按价值降序",
        ],
    )
    # reaffirms 严格同色 + 图例不得两类同色
    reaffirms_same_color = "严格同色" in text
    reaffirms_no_two_same = _matches_any(text, [r"图例.{0,12}不得出现两类同色", r"图例不得两类同色"])
    # pre-existing grouping requirement survives
    keeps_grouping_requirement = "按大类分组、同组相邻排列" in text

    missing = []
    if not has_precedence_ruling:
        missing.append("precedence ruling 大类分组相邻 优先于 价值降序")
    if not reaffirms_same_color:
        missing.append("reaffirm 柱色与大类解释卡 严格同色")
    if not reaffirms_no_two_same:
        missing.append("reaffirm 图例不得两类同色")
    if not keeps_grouping_requirement:
        missing.append("pre-existing 「按大类分组、同组相邻排列」 requirement")

    assert not missing, (
        "CONTENT DEFECT 1.5 NOT FIXED — ppt-deck-mapping.md P8 grouping precedence "
        f"ruling incomplete. Missing fixed-state markers: {missing}"
    )


# ---------------------------------------------------------------------------
# 1.6 — Value-tree nodeization guidance + generation-time enforced check
# ---------------------------------------------------------------------------

def test_1_6_value_tree_nodeization_guidance_and_enforced_check(pptx_tool_text):
    """FIXED state: pptx-tool.md must contain the value-tree nodeization mandatory
    guidance — 等式逐项成独立直角框 / 单父树 / 关键影响因子前置 / 保留运算符与父子
    关系 — AND a generation-time enforced check (节点化未满足即阻断/返工).
    """
    text = pptx_tool_text

    # mandatory nodeization guidance markers
    has_equation_per_box = _matches_any(text, [r"等式逐项成独立直角框", r"每个变量各自一个独立直角框", r"逐项成.{0,6}框"])
    has_single_parent = "单父树" in text or "单父结构" in text
    has_key_factor_front = _matches_any(text, [r"关键影响因子前置", r"关键影响因子.{0,8}前置"])
    has_keep_operators = _matches_any(text, [r"保留运算符与父子关系", r"保留运算符.{0,8}父子关系"])

    # generation-time enforced check: nodeization unmet => block / rework
    has_enforced_check = _matches_any(
        text,
        [
            r"节点化未满足.{0,8}(阻断|返工)",
            r"节点化校验",
            r"命中即阻断.{0,8}返工",
            r"判定.{0,12}节点化未满足.{0,12}阻断",
        ],
    )

    missing = []
    if not has_equation_per_box:
        missing.append("等式逐项成独立直角框")
    if not has_single_parent:
        missing.append("单父树")
    if not has_key_factor_front:
        missing.append("关键影响因子前置")
    if not has_keep_operators:
        missing.append("保留运算符与父子关系")
    if not has_enforced_check:
        missing.append("generation-time enforced check (节点化未满足即阻断/返工)")

    assert not missing, (
        "CONTENT DEFECT 1.6 NOT FIXED — pptx-tool.md value-tree nodeization "
        f"guidance / enforced check incomplete. Missing fixed-state markers: {missing}"
    )


# ---------------------------------------------------------------------------
# 1.7a — Codename consistency (codenames KEPT, contradiction resolved)
# ---------------------------------------------------------------------------

def test_1_7a_skill_carves_painpoint_codename_exception(skill_text):
    """FIXED state: SKILL.md §3.1 must carve a pain-point P-x exception — the
    pain column codename `P-x` is PERMITTED, shown as 「代号（中文名）」 — while
    SC-x ids and yaml keys/enum values remain forbidden.
    """
    text = skill_text

    # exception carved for the pain-point codename
    carves_exception = _matches_any(
        text,
        [
            r"痛点代号例外",
            r"痛点列中的痛点代号\s*`?P-x`?\s*属.{0,4}许可",
            r"价值树痛点列.{0,16}`?P-x`?.{0,8}许可项",
        ],
    )
    shows_codename_form = "代号（中文名）" in text
    # other internal codes remain forbidden
    sc_x_still_forbidden = "SC-x" in text
    yaml_keys_still_forbidden = _matches_any(text, [r"yaml 键名", r"枚举值"])
    other_codes_still_forbidden = _matches_any(
        text,
        [r"其余所有内部代号一律仍禁止", r"其余.{0,6}内部代号.{0,8}禁止", r"其余内部代号仍禁止"],
    )

    missing = []
    if not carves_exception:
        missing.append("痛点代号 P-x exception carved in §3.1")
    if not shows_codename_form:
        missing.append("痛点列显示「代号（中文名）」")
    if not sc_x_still_forbidden:
        missing.append("SC-x still forbidden")
    if not yaml_keys_still_forbidden:
        missing.append("yaml 键名/枚举值 still forbidden")
    if not other_codes_still_forbidden:
        missing.append("其余内部代号仍禁止 (exception is scoped)")

    assert not missing, (
        "CONTENT DEFECT 1.7a NOT FIXED — SKILL.md §3.1 pain-code exception "
        f"incomplete or over-broad. Missing fixed-state markers: {missing}"
    )


def test_1_7a_absolute_prohibition_wording_removed(skill_text):
    """FIXED state: the contradiction is resolved — SKILL.md must NO LONGER state
    the absolute prohibition "PPT 上只出现痛点中文名，不出现 `P-1` 这类代号".
    Its continued presence would directly contradict ppt-deck-mapping's
    「代号（中文名）」 pain-column requirement.
    """
    has_absolute_prohibition = _matches_any(
        skill_text,
        [r"只出现痛点中文名[，,].{0,12}不出现\s*`?P-1`?\s*这类代号"],
    )
    assert not has_absolute_prohibition, (
        "CONTENT DEFECT 1.7a NOT FIXED — SKILL.md still carries the absolute "
        "prohibition 「PPT 上只出现痛点中文名，不出现 `P-1` 这类代号」, which "
        "contradicts ppt-deck-mapping's 「代号（中文名）」 pain-column rule."
    )


def test_1_7a_deck_mapping_keeps_codename_form(deck_map_text):
    """FIXED state: ppt-deck-mapping.md still uses 「代号（中文名）」 for the pain
    column (AS-IS, codenames kept). It is the authoritative basis the SKILL.md
    §3.1 exception defers to — both files now consistent.
    """
    assert "代号（中文名）" in deck_map_text, (
        "CONTENT DEFECT 1.7a NOT FIXED — ppt-deck-mapping.md no longer uses "
        "「代号（中文名）」 for the pain column; codename consistency broken."
    )


# ---------------------------------------------------------------------------
# 1.7b — Delivery-md carrier structure (pain column + AI-scenario three-part)
# ---------------------------------------------------------------------------

def _assert_carrier_structure(text: str, file_label: str):
    # pain column carrier in delivery md, using 代号（中文名）
    has_pain_carrier = _matches_any(text, [r"痛点列承载", r"痛点列.{0,12}承载", r"痛点列.{0,12}必须保留"])
    shows_codename_form = "代号（中文名）" in text
    # AI-scenario three-part explanation
    has_three_part = _matches_any(
        text,
        [r"运用\[?什么技术\]?\s*→\s*实现\[?什么功能\]?\s*→\s*达成\[?什么目标\]?", r"三段式"],
    )
    has_three_part_literal = "运用[什么技术]" in text and "实现[什么功能]" in text and "达成[什么目标]" in text

    missing = []
    if not has_pain_carrier:
        missing.append("痛点列承载结构 (pain-column carrier)")
    if not shows_codename_form:
        missing.append("痛点列「代号（中文名）」")
    if not (has_three_part or has_three_part_literal):
        missing.append("AI 场景三段式『运用[什么技术] → 实现[什么功能] → 达成[什么目标]』")
    return missing


def test_1_7b_value_tree_guide_carrier_structure(value_tree_guide_text):
    """FIXED state: 03-value-tree-guide.md must contain the delivery-md carrier
    structure for the pain column (代号（中文名)) AND the AI-scenario three-part
    explanation 『运用[什么技术] → 实现[什么功能] → 达成[什么目标]』.
    """
    missing = _assert_carrier_structure(value_tree_guide_text, "03-value-tree-guide.md")
    assert not missing, (
        "CONTENT DEFECT 1.7b NOT FIXED — 03-value-tree-guide.md delivery-md "
        f"carrier structure incomplete. Missing fixed-state markers: {missing}"
    )


def test_1_7b_pain_point_guide_carrier_structure(pain_point_guide_text):
    """FIXED state: 05-pain-point-guide.md must contain the delivery-md carrier
    structure for the pain column (代号（中文名)) AND the AI-scenario three-part
    explanation 『运用[什么技术] → 实现[什么功能] → 达成[什么目标]』.
    """
    missing = _assert_carrier_structure(pain_point_guide_text, "05-pain-point-guide.md")
    assert not missing, (
        "CONTENT DEFECT 1.7b NOT FIXED — 05-pain-point-guide.md delivery-md "
        f"carrier structure incomplete. Missing fixed-state markers: {missing}"
    )
# @AI_GENERATED: end

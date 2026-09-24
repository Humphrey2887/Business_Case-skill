# @AI_GENERATED
"""
Bug-condition exploration test — FORM-family defects (1.1-1.4)
spec: .kiro/specs/ppt-output-defects-fix  (Property 1: Bug Condition)

WHAT THIS IS
------------
This bugfix repairs INSTRUCTIONAL ASSETS (markdown), not executable code
(the original `build_deck.py` was deleted during post-delivery cleanup). So
the "tests" here are ASSET-CONSISTENCY STATIC CHECKS: they statically inspect
the real asset files and assert the FIXED state of the instructional assets.

EXPECTED OUTCOME (bugfix exploration protocol)
----------------------------------------------
These assertions encode the FIXED state described by design.md
"Correctness Properties / Property 1" and "Fix Implementation". On the CURRENT
(UNFIXED) assets they MUST FAIL. A failure here is the SUCCESS outcome: it
confirms the FORM-family defects exist (pptx-tool.md ships an all-Latin font
table, no master-CJK binding, no precedence ruling, and only an advisory
leftover-placeholder QA).

After the fix (tasks 3.1-3.4) is implemented, this same test is re-run
(task 3.5) and is expected to PASS, validating the repair.

Covered (design isBugCondition form-family + static asset-conflict checks):
  1.1  mandatory cover-placeholder fill + leftover-placeholder QA as HARD gate
  1.2  master CJK font (Microsoft YaHei) binding + run-level CJK/Latin split
       + 母版取字 precedence over the generic Latin font-pairing table
  1.3/1.4  precedence-ruling block: master hard-constraints (直角框/固定版式)
       outrank generic Design Ideas (rounded image frames motif / vary-layout)
  static conflict: precedence ruling is ABSENT on unfixed assets (encoded as
       the expected-fixed assertion so it fails now)
"""

import re
from pathlib import Path

import pytest

# Repo root = <repo>/tests/ppt_output_defects_fix/this_file.py -> up 3
REPO_ROOT = Path(__file__).resolve().parents[2]
PPTX_TOOL = REPO_ROOT / "deliverable-tools" / "pptx" / "pptx-tool.md"


def _load(path: Path) -> str:
    assert path.is_file(), f"asset not found (cannot run static check): {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def pptx_tool_text() -> str:
    return _load(PPTX_TOOL)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_all(text: str, needles) -> list:
    """Return the list of needles MISSING from text (case-insensitive)."""
    low = text.lower()
    return [n for n in needles if n.lower() not in low]


def _matches_any(text: str, patterns) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


# ---------------------------------------------------------------------------
# 1.3 / 1.4 — Precedence ruling block (master hard-constraints > Design Ideas)
# This is the structural root cause for the whole form-family, so assert first.
# ---------------------------------------------------------------------------

def test_1_3_1_4_precedence_ruling_block_present(pptx_tool_text):
    """FIXED state: pptx-tool.md must contain a precedence-ruling block stating
    that, in the business-case/master scenario, master hard-constraints
    (直角框 / 固定版式) and ppt-deck-mapping per-page specs OUTRANK the generic
    Design Ideas (rounded image frames motif / vary-layout / generic palette).

    UNFIXED: no such ruling exists -> FAILS (confirms defects 1.3 & 1.4 and the
    static conflict that Design Ideas currently override master hard-constraints).
    """
    text = pptx_tool_text

    # A precedence ruling must reference: priority + master hard constraint +
    # the generic Design Ideas it overrides + the concrete form constraints.
    has_priority = _matches_any(text, [r"优先", r"precedence", r"outrank", r"以母版.*为准"])
    has_master_constraint = _matches_any(text, [r"母版硬约束", r"master hard[- ]?constraint", r"红线\s*4b", r"硬约束"])
    references_design_ideas = "design ideas" in text.lower()
    has_rightangle_or_fixedlayout = _matches_any(text, [r"直角框", r"固定版式", r"fixed[- ]?layout", r"right[- ]?angle"])

    missing = []
    if not has_priority:
        missing.append("priority/precedence wording (优先/precedence/outrank)")
    if not has_master_constraint:
        missing.append("master-hard-constraint reference (母版硬约束/红线4b)")
    if not references_design_ideas:
        missing.append("explicit 'Design Ideas' being overridden")
    if not has_rightangle_or_fixedlayout:
        missing.append("直角框/固定版式 (right-angle/fixed-layout) ruling")

    assert not missing, (
        "FORM DEFECT 1.3/1.4 CONFIRMED — pptx-tool.md has NO precedence-ruling "
        "block; generic Design Ideas are left to override master hard-constraints. "
        f"Missing fixed-state markers: {missing}"
    )


# ---------------------------------------------------------------------------
# 1.1 — Cover placeholder mandatory fill + leftover-placeholder QA hard gate
# ---------------------------------------------------------------------------

def test_1_1_cover_placeholder_mandatory_fill_instruction(pptx_tool_text):
    """FIXED state: pptx-tool.md must contain a MANDATORY instruction to fill the
    cover layout's built-in title/subtitle placeholders with the real client
    name / project title / date (not build a floating textbox).

    UNFIXED: pptx-tool.md never mentions cover placeholders at all -> FAILS
    (confirms defect 1.1: cover title placeholder left as 'Cover Page Style A').
    """
    text = pptx_tool_text
    mentions_cover_placeholder = _matches_any(
        text,
        [r"cover.{0,40}(占位符|placeholder)", r"(占位符|placeholder).{0,40}cover", r"封面.{0,20}占位符"],
    )
    is_mandatory = _matches_any(text, [r"必须", r"强制", r"mandatory", r"MUST"])

    assert mentions_cover_placeholder and is_mandatory, (
        "FORM DEFECT 1.1 CONFIRMED — pptx-tool.md has NO mandatory cover-placeholder "
        "fill instruction; cover title placeholder is left unfilled "
        "(残留 'Cover Page Style A'). "
        f"mentions_cover_placeholder={mentions_cover_placeholder}, is_mandatory={is_mandatory}"
    )


def test_1_1_leftover_placeholder_qa_is_hard_predelivery_gate(pptx_tool_text):
    """FIXED state: the leftover-placeholder QA grep must be declared a HARD
    pre-delivery gate covering 'Cover Page Style' and the layout-placeholder
    pattern `this.*(page|slide).*layout` (hit => block declaring success).

    UNFIXED: the grep exists but is only advisory ('fix them before declaring
    success') and does NOT include 'Cover Page Style', nor is it a hard gate.
    -> FAILS (confirms the placeholder QA is only advisory).
    """
    text = pptx_tool_text
    covers_cover_page_style = "cover page style" in text.lower()
    has_layout_grep = re.search(r"this\.\*\(page\|slide\)\.\*layout", text) is not None
    declared_hard_gate = _matches_any(
        text,
        [r"强制门槛", r"出片前.*(强制|门槛)", r"hard\s*gate", r"阻断", r"命中即.*(阻断|返工)"],
    )

    missing = []
    if not covers_cover_page_style:
        missing.append("'Cover Page Style' in the QA grep set")
    if not has_layout_grep:
        missing.append("layout-placeholder grep pattern")
    if not declared_hard_gate:
        missing.append("HARD pre-delivery gate wording (强制门槛/阻断)")

    assert not missing, (
        "FORM DEFECT 1.1 (QA) CONFIRMED — leftover-placeholder QA is only advisory, "
        "not a hard pre-delivery gate, and omits 'Cover Page Style'. "
        f"Missing fixed-state markers: {missing}"
    )


# ---------------------------------------------------------------------------
# 1.2 — Master CJK font binding + run-level CJK/Latin split + 取字 precedence
# ---------------------------------------------------------------------------

def test_1_2_master_cjk_font_binding_present(pptx_tool_text):
    """FIXED state: pptx-tool.md must bind the master CJK font (Microsoft YaHei /
    微软雅黑) so CJK runs do not fall back to a glyph-less Latin font.

    UNFIXED: the font-pairing table is ALL-LATIN (Georgia/Calibri/Arial Black...)
    with no CJK font -> FAILS (confirms defect 1.2 字体异常 on P3/P10).
    """
    text = pptx_tool_text
    binds_cjk_font = _matches_any(text, [r"microsoft\s*yahei", r"微软雅黑", r"CJK\s*字体", r"中文字体.*母版", r"母版.*中文字体"])
    assert binds_cjk_font, (
        "FORM DEFECT 1.2 CONFIRMED — pptx-tool.md does NOT bind a master CJK font "
        "(Microsoft YaHei). The font-pairing table is all-Latin; CJK text falls back "
        "to a glyph-less Latin font causing per-element fallback / 字体异常."
    )


def test_1_2_run_level_cjk_latin_split_and_master_precedence(pptx_tool_text):
    """FIXED state: pptx-tool.md must require run-level CJK/Latin font split for
    mixed CJK/Latin text AND declare that 母版取字 (only use master colors/fonts)
    takes precedence over the generic Latin font-pairing table.

    UNFIXED: no run-level split guidance; the font section actively advises
    'pick an interesting font pairing, don't default to Arial' which CONFLICTS
    with 只用母版取色取字 -> FAILS (confirms defect 1.2 root cause).
    """
    text = pptx_tool_text
    has_run_level_split = _matches_any(
        text,
        [r"run\s*级", r"run[- ]?level", r"中英.*(分别设置|分设)", r"(分别设置|分设).*中英"],
    )
    has_master_typeface_precedence = _matches_any(
        text,
        [r"只用母版取色取字", r"母版取字.*优先", r"母版.*字.*优先于", r"优先于.*(拉丁|font[- ]?pairing|字体配对)"],
    )

    missing = []
    if not has_run_level_split:
        missing.append("run-level CJK/Latin split guidance")
    if not has_master_typeface_precedence:
        missing.append("母版取字 precedence over generic Latin font-pairing table")

    assert not missing, (
        "FORM DEFECT 1.2 (precedence) CONFIRMED — pptx-tool.md lacks run-level "
        "CJK/Latin split and does not declare 母版取字 precedence over the generic "
        "Latin font-pairing table (which still advises picking individualistic fonts). "
        f"Missing fixed-state markers: {missing}"
    )


# ---------------------------------------------------------------------------
# Static conflict detection — Design Ideas currently override master hard
# constraints (precedence ruling ABSENT). Encoded as the expected-fixed
# assertion: the generic motifs must be explicitly subordinated for this skill.
# ---------------------------------------------------------------------------

def test_static_conflict_generic_motifs_subordinated_to_master(pptx_tool_text):
    """FIXED state: the generic motifs that conflict with master hard-constraints
    — rounded image frames motif and 'vary layout' — must be explicitly
    subordinated/forbidden for the business-case skill scenario.

    UNFIXED: pptx-tool.md promotes 'rounded image frames' as a motif and
    "Don't repeat the same layout" (vary layouts), with NO subordination ->
    FAILS (confirms the unresolved conflict that produces 1.3/1.4).
    """
    text = pptx_tool_text
    low = text.lower()

    promotes_rounded = "rounded image frames" in low
    promotes_vary_layout = _matches_any(text, [r"don't repeat the same layout", r"vary columns", r"变换布局"])

    # The fixed state must subordinate these for the skill scenario.
    subordinates_for_skill = _matches_any(
        text,
        [r"禁用.*(圆角|变换布局)", r"(圆角图框|变换布局).*(让位|禁用|不适用)", r"本\s*skill.*(禁用|不使用).*圆角", r"business[- ]?case.*(禁用|let go|让位)"],
    )

    assert subordinates_for_skill, (
        "STATIC CONFLICT CONFIRMED — pptx-tool.md still promotes generic motifs "
        f"(rounded image frames={promotes_rounded}, vary-layout={promotes_vary_layout}) "
        "WITHOUT subordinating them to master hard-constraints for the business-case "
        "skill. The precedence ruling is ABSENT, so Design Ideas override 直角框/固定版式."
    )
# @AI_GENERATED: end

# @AI_GENERATED
"""
Preservation property test — non-defect (¬C(X)) behavior MUST NOT change
spec: .kiro/specs/ppt-output-defects-fix  (Property 3: Preservation)

WHAT THIS IS
------------
This bugfix repairs INSTRUCTIONAL ASSETS (markdown), not executable code
(the original `build_deck.py` was deleted during post-delivery cleanup). So
the "tests" here are ASSET-CONSISTENCY STATIC CHECKS: they statically inspect
the real asset files and lock in the CURRENT (unfixed) baseline that the fix
MUST preserve.

OBSERVATION-FIRST METHODOLOGY
-----------------------------
These assertions were derived by OBSERVING the CURRENT (UNFIXED) assets and
recording the invariants over the parts that must NOT change (¬C(X)), per
design.md "Preservation Requirements 3.1–3.6" / "Correctness Properties /
Property 3". They encode the baseline behavior to be preserved.

EXPECTED OUTCOME (preservation protocol)
----------------------------------------
On the CURRENT (UNFIXED) assets these assertions MUST PASS — they establish
the baseline. After the fix (tasks 3.1–3.4) is implemented, this same test is
re-run (task 3.7) and is STILL expected to PASS, proving no regression on the
non-defect input domain.

Covered (design Preservation Requirements 3.1–3.6):
  3.1  md-only delivery section/contract in SKILL.md / ppt-deck-mapping unchanged
  3.2  eleven-step analysis process (steps 01–11) product contracts &
       user checkpoints unchanged
  3.3  §3 red line still forbids OTHER internal codes (SC-x, yaml keys, step
       numbers) AND ppt-deck-mapping keeps 「代号（中文名）」 for the pain column
  3.4  untouched pages P2/P5/P9/P12 per-page specs in ppt-deck-mapping unchanged
  3.5  post-delivery cleanup (ppt-deck-mapping §6) delete/keep lists & safety
       constraints unchanged
  3.6  other unchanged invariants (口径一致 caliber rule, 节点化 rule, etc.)

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""

from pathlib import Path

import pytest

# Repo root = <repo>/tests/ppt_output_defects_fix/this_file.py -> up 3
REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = REPO_ROOT / "SKILL.md"
DECK_MAP = (
    REPO_ROOT / "workflows" / "business-pain-point" / "standards" / "ppt-deck-mapping.md"
)
STANDARDS_DIR = REPO_ROOT / "workflows" / "business-pain-point" / "standards"


def _load(path: Path) -> str:
    assert path.is_file(), f"asset not found (cannot run static check): {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def skill_text() -> str:
    return _load(SKILL_MD)


@pytest.fixture(scope="module")
def deck_map_text() -> str:
    return _load(DECK_MAP)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _missing(text: str, needles) -> list:
    """Return the list of needles MISSING from text (exact substring, case-insensitive)."""
    low = text.lower()
    return [n for n in needles if n.lower() not in low]


# ---------------------------------------------------------------------------
# 3.1 — md-only delivery section / contract unchanged
# ---------------------------------------------------------------------------

def test_3_1_md_only_delivery_contract_preserved(skill_text, deck_map_text):
    """Baseline: SKILL.md keeps the --format md option and the "同时产出 .md"
    delivery contract, and ppt-deck-mapping keeps the companion-.md clause.
    The fix targets pptx-path defects and MUST NOT touch md-only delivery.
    """
    skill_missing = _missing(
        skill_text,
        [
            "`--format`",          # Options flag for delivery format
            "`md`",                # md format value
            "同时产出 .md",         # companion .md delivery clause
            "<deck>.md",           # companion .md artifact in the on-disk layout
        ],
    )
    map_missing = _missing(
        deck_map_text,
        ["同时产出 .md"],          # ppt-deck-mapping companion .md clause
    )
    assert not skill_missing and not map_missing, (
        "PRESERVATION 3.1 VIOLATED — md-only delivery contract changed. "
        f"SKILL.md missing={skill_missing}, ppt-deck-mapping missing={map_missing}"
    )


# ---------------------------------------------------------------------------
# 3.2 — eleven-step analysis process (01–11) contracts & checkpoints unchanged
# ---------------------------------------------------------------------------

def test_3_2_eleven_step_overview_and_checkpoints_preserved(skill_text):
    """Baseline: SKILL.md keeps the eleven-step overview, the per-step product
    contract (process/0N-*.yaml落盘), and the user-checkpoint discipline.
    The pptx-asset fix MUST NOT alter the analysis process.
    """
    missing = _missing(
        skill_text,
        [
            "十一步总览",            # eleven-step overview section
            "用户检查点",            # user checkpoint discipline
            "process/0N-*.yaml",     # per-step structured product contract
            "0N-*.md",               # per-step readable intermediate draft
        ],
    )
    assert not missing, (
        "PRESERVATION 3.2 VIOLATED — eleven-step overview / product contract / "
        f"checkpoints changed. Missing baseline markers: {missing}"
    )


def test_3_2_eleven_step_rows_01_through_11_preserved(skill_text):
    """Baseline: every step 01–11 row is present in the SKILL.md overview table.
    Lock in each step number so the process contract cannot silently shrink.
    """
    low = skill_text.lower()
    missing_steps = [f"| {n:02d} |" for n in range(1, 12) if f"| {n:02d} |".lower() not in low]
    assert not missing_steps, (
        "PRESERVATION 3.2 VIOLATED — eleven-step overview rows changed. "
        f"Missing step rows: {missing_steps}"
    )


def test_3_2_eleven_step_guides_exist_on_disk(skill_text):
    """Baseline: the 01–11 standards guides referenced by the process exist.
    The fix touches only specific guides for carrier structure; it MUST NOT
    delete or rename the per-step guide set.
    """
    guide_globs = {
        1: "01-research-guide.md",
        2: "02-critical-mission-guide.md",
        3: "03-value-tree-guide.md",
        4: "04-kpi-factor-guide.md",
        5: "05-pain-point-guide.md",
        6: "06-pain-scoring-guide.md",
        7: "07-pain-cluster-guide.md",
        8: "08-scenario-guide.md",
        9: "09-valuation-guide.md",
        10: "10-ontology-guide.md",
        11: "11-roadmap-guide.md",
    }
    missing = [name for name in guide_globs.values() if not (STANDARDS_DIR / name).is_file()]
    assert not missing, (
        "PRESERVATION 3.2 VIOLATED — per-step standards guides missing on disk: "
        f"{missing}"
    )


# ---------------------------------------------------------------------------
# 3.3 — §3 red line still forbids OTHER internal codes; pain column keeps
#       「代号（中文名）」 (codenames kept — the controlled exception)
# ---------------------------------------------------------------------------

def test_3_3_red_line_still_forbids_other_internal_codes(skill_text):
    """Baseline: SKILL.md §3 "过程信息不进 PPT" red line and its §3.1 forbidden
    list survive, and continue to forbid the OTHER internal codes — scenario
    `SC-x` ids, yaml key names / enum values, and step numbers.

    The fix only carves out a controlled exception for the pain-column `P-x`
    codename; it MUST NOT weaken the rest of the §3 red line. (We intentionally
    do NOT assert on the `P-1`/痛点中文名 wording, which the fix will revise.)
    """
    missing = _missing(
        skill_text,
        [
            "过程信息不进 PPT",      # §3 red-line section survives
            "违禁内容清单",          # §3.1 forbidden list survives
            "SC-x",                  # scenario id still forbidden
            "scenario_id",           # yaml key still forbidden
            "value_status",          # yaml key still forbidden
            "to_verify",             # enum value still forbidden
            "步骤号",                # step numbers still forbidden
        ],
    )
    assert not missing, (
        "PRESERVATION 3.3 VIOLATED — §3 red line no longer forbids the OTHER "
        f"internal codes (non-pain-code intent broken). Missing markers: {missing}"
    )


def test_3_3_pain_column_keeps_codename_controlled_exception(deck_map_text):
    """Baseline: ppt-deck-mapping keeps 「代号（中文名）」 for the pain column
    (codenames kept — the controlled exception). This表述 is AS-IS preserved;
    it is the authoritative basis the §3.1 exception defers to.
    """
    assert "代号（中文名）" in deck_map_text, (
        "PRESERVATION 3.3 VIOLATED — ppt-deck-mapping pain-column 「代号（中文名）」 "
        "(codenames-kept controlled exception) was removed."
    )


# ---------------------------------------------------------------------------
# 3.4 — untouched pages P2 / P5 / P9 / P12 per-page specs unchanged
# ---------------------------------------------------------------------------

def test_3_4_untouched_page_specs_preserved(deck_map_text):
    """Baseline: the per-page spec headers for the pages NOT in scope of this
    fix (P2 执行摘要 / P5 客户 MC 分析 / P9 场景明细表 / P12=P(11+N) 实施路径)
    are present and unchanged. The fix MUST NOT regress these pages.
    """
    missing = _missing(
        deck_map_text,
        [
            "### P2 · 执行摘要",                 # P2 spec header
            "### P5 · 客户 Mission Critical 分析",  # P5 spec header
            "### P9 · 场景分析·场景明细表",        # P9 spec header
            "实施路径（步 11）",                  # P12 = P(11+N) roadmap spec
        ],
    )
    assert not missing, (
        "PRESERVATION 3.4 VIOLATED — untouched-page per-page specs changed. "
        f"Missing baseline headers: {missing}"
    )


# ---------------------------------------------------------------------------
# 3.5 — post-delivery cleanup (§6) delete/keep lists & safety constraints
# ---------------------------------------------------------------------------

def test_3_5_post_delivery_cleanup_lists_and_safety_preserved(deck_map_text):
    """Baseline: ppt-deck-mapping §6 交付后清理 keeps its delete-list, keep-list
    and safety constraints. The fix MUST NOT alter cleanup logic.
    """
    missing = _missing(
        deck_map_text,
        [
            "交付后清理",            # §6 section
            "删除清单",              # §6.2 delete list
            "保留清单",              # §6.3 keep list
            "<deck>.pptx",           # keep-list final deliverable entry
            "<deck>.md",             # keep-list companion .md entry
            "安全约束",              # §6.4 safety constraints
            "先成品",                # safety: deliverable-first then cleanup
            "范围锁定",              # safety: scope-locked deletion
            "逐条删除",              # safety: item-by-item deletion (no wildcard)
        ],
    )
    assert not missing, (
        "PRESERVATION 3.5 VIOLATED — post-delivery cleanup delete/keep lists or "
        f"safety constraints changed. Missing baseline markers: {missing}"
    )


# ---------------------------------------------------------------------------
# 3.6 — other unchanged invariants (caliber rule, node-ization rule, P8 grouping
#       requirement that pre-exists the fix)
# ---------------------------------------------------------------------------

def test_3_6_other_deck_invariants_preserved(deck_map_text):
    """Baseline: cross-cutting deck invariants that are NOT defect-scoped survive
    — 口径一致铁律 (caliber consistency), 节点化 (node-ization), 直角框 (right-angle
    boxes), and the pre-existing P8「按大类分组、同组相邻排列」requirement (the fix
    only ADDS a precedence ruling on top, it does not remove this requirement).
    """
    missing = _missing(
        deck_map_text,
        [
            "口径一致铁律",                  # caliber consistency rule
            "节点化",                        # node-ization rule
            "直角框",                        # right-angle box rule
            "按大类分组、同组相邻排列",        # pre-existing P8 grouping requirement
        ],
    )
    assert not missing, (
        "PRESERVATION 3.6 VIOLATED — cross-cutting deck invariants changed. "
        f"Missing baseline markers: {missing}"
    )
# @AI_GENERATED: end

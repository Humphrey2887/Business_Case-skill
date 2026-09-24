# @AI_GENERATED
"""Feature: pptx-template-section-styling, guidance hard-rules existence (Validates: Requirements 5.1, 5.2, 5.3)

存在性测试（示例式，pytest 风格；NOT hypothesis）：grep 三处指引文件，断言每个文件
均记载三类硬规则措辞——

    (a) 固定映射（Requirement 5.1）：cover→cover / content→content / ending→ending；
    (b) 位置法角色识别（Requirement 5.2）：首=cover / 中=content / 末=ending 或 content；
    (c) ending 默认不启用（Requirement 5.3）：ending 默认不启用 / not invoked by default。

三处指引文件（由 Task 9.1/9.2/9.3 更新）：
    1. deliverable-tools/pptx/pptx-tool.md
    2. deliverable-tools/pptx/editing.md
    3. SKILL.md（business-case-builder 交付红线）

正则对箭头两侧空白（cover→cover 与 cover → cover）、位置法措辞
（首=cover 与 首页 = cover）均做鲁棒匹配，避免因空格/词形差异误判缺失。
文件缺失时以清晰失败信息（而非静默 skip 掩盖）报出具体文件路径。

以 UTF-8 读取文件字节。路径相对仓库计算（从测试文件向上寻找 skill 根），保证可移植。

Validates: Requirements 5.1, 5.2, 5.3
"""

import re
from pathlib import Path

import pytest


def _find_skill_root() -> Path:
    """从本测试文件向上寻找 skill 根目录。

    skill 根的判定标志：同时含 ``SKILL.md`` 与 ``deliverable-tools/pptx`` 目录。
    这样无论仓库被 clone/移动到何处，都能可移植地定位三处指引文件。
    """
    for parent in Path(__file__).resolve().parents:
        if (parent / "SKILL.md").is_file() and (
            parent / "deliverable-tools" / "pptx"
        ).is_dir():
            return parent
    raise AssertionError(
        "无法从测试文件向上定位 skill 根（需同时含 SKILL.md 与 "
        "deliverable-tools/pptx）——请确认测试位于 skill 仓库内。"
    )


_SKILL_ROOT = _find_skill_root()

# 三处指引文件（相对 skill 根计算，保证可移植）。
_GUIDANCE_FILES = {
    "pptx-tool.md": _SKILL_ROOT / "deliverable-tools" / "pptx" / "pptx-tool.md",
    "editing.md": _SKILL_ROOT / "deliverable-tools" / "pptx" / "editing.md",
    "SKILL.md": _SKILL_ROOT / "SKILL.md",
}

# --- 硬规则措辞的鲁棒正则 ----------------------------------------------------
# 箭头 → (U+2192) 两侧允许可选空白：兼容 "cover→cover" 与 "cover → cover"。
_FIXED_MAPPING_PATTERNS = {
    "cover→cover": re.compile(r"cover\s*→\s*cover"),
    "content→content": re.compile(r"content\s*→\s*content"),
    "ending→ending": re.compile(r"ending\s*→\s*ending"),
}

# 位置法：允许 "首=cover" 与 "首页 = cover"、"中=content" 与 "中间各页 = content"
# 等词形/空白差异（= 兼容全角＝）。
_POSITIONAL_PATTERNS = {
    "首→cover": re.compile(r"首[^\n=＝]*[=＝]\s*cover"),
    "中→content": re.compile(r"中[^\n=＝]*[=＝]\s*content"),
    "末→ending": re.compile(r"末[^\n=＝]*[=＝]\s*ending"),
}

# ending 默认不启用：中文措辞或英文 "not invoked by default" 任一命中即可。
_ENDING_DEFAULT_OFF_PATTERN = re.compile(r"默认不启用|not invoked by default")


def _read_text(name: str) -> str:
    """以 UTF-8 读取指引文件；文件缺失时以清晰失败信息报出具体路径。"""
    path = _GUIDANCE_FILES[name]
    if not path.is_file():
        pytest.fail(f"必需的指引文件缺失：{name} -> {path}", pytrace=False)
    return path.read_bytes().decode("utf-8")


@pytest.fixture(params=sorted(_GUIDANCE_FILES), ids=sorted(_GUIDANCE_FILES))
def guidance_name(request):
    return request.param


def test_fixed_mapping_hard_rule_present(guidance_name):
    """(a) 固定映射：三处文件均含 cover→cover / content→content / ending→ending。

    Validates: Requirements 5.1
    """
    text = _read_text(guidance_name)
    missing = [
        label
        for label, pattern in _FIXED_MAPPING_PATTERNS.items()
        if not pattern.search(text)
    ]
    assert not missing, (
        f"{guidance_name} 缺少固定映射硬规则措辞：{missing}"
        f"（文件：{_GUIDANCE_FILES[guidance_name]}）"
    )


def test_positional_role_detection_hard_rule_present(guidance_name):
    """(b) 位置法角色识别：三处文件均含 首=cover / 中=content / 末=ending 措辞。

    Validates: Requirements 5.2
    """
    text = _read_text(guidance_name)
    missing = [
        label
        for label, pattern in _POSITIONAL_PATTERNS.items()
        if not pattern.search(text)
    ]
    assert not missing, (
        f"{guidance_name} 缺少位置法角色识别硬规则措辞：{missing}"
        f"（文件：{_GUIDANCE_FILES[guidance_name]}）"
    )


def test_ending_default_off_hard_rule_present(guidance_name):
    """(c) ending 默认不启用：三处文件均含 默认不启用 / not invoked by default。

    Validates: Requirements 5.3
    """
    text = _read_text(guidance_name)
    assert _ENDING_DEFAULT_OFF_PATTERN.search(text), (
        f"{guidance_name} 缺少 ending 默认不启用硬规则措辞"
        f"（默认不启用 / not invoked by default）"
        f"（文件：{_GUIDANCE_FILES[guidance_name]}）"
    )
# @AI_GENERATED: end

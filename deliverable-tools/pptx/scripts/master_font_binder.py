# @AI_GENERATED
"""Master-only color/font extraction + run-level CJK/Latin font split (Task 8.3).

母版取色取字与 run 级中英字体分设（回归防护 R7.1 / R7.2 / R7.3）。

本模块固化两条硬约束：
  1. **颜色/字体只从 Master_Template 动态提取**（R7.1）—— 由 `extract_master_fonts`
     解析主题 `ppt/theme/themeN.xml` 的 `<a:fontScheme>`，`extract_master_colors`
     解析 `<a:clrScheme>`，绝不硬编码字体/颜色。
  2. **每个文本 run 按脚本分设**（R7.2 / R7.3）—— 中英混排段落先按脚本切成同脚本
     连续片段（`split_runs_by_script`），中文 run 绑母版 CJK 字体并写入
     `<a:ea typeface="...">`，拉丁 run 绑母版拉丁字体并写入 `<a:latin typeface="...">`，
     避免中文回退到无字形的拉丁字体。

XML 读写统一使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。

本模块设计为纯净、可测试的 API：task 8.4 将据此断言 Property 9
（文本 run 颜色/字体取自母版提取集合；混排段落中 CJK run 绑 CJK 字体、拉丁 run 绑拉丁字体）。
"""

import os
from dataclasses import dataclass, field

from defusedxml.minidom import parse

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# DrawingML 命名空间（主题 fontScheme / clrScheme 所在）。
A_NAMESPACE = "http://schemas.openxmlformats.org/drawingml/2006/main"

# 中文（简体）East-Asian 脚本标签：主题 <a:font script="Hans"> 承载 CJK 字体。
CJK_SCRIPT_TAG = "Hans"

# 母版 CJK 字体的兜底默认值。当主题 <a:ea> 为空且无 Hans 脚本条目时使用。
# 远景母版实际使用 Microsoft YaHei / 微软雅黑（见 master-structure-findings.md），
# 作为“不落入无字形拉丁字体”的安全兜底。
DEFAULT_CJK_FONT = "微软雅黑"
# 拉丁字体兜底默认值（主题 majorFont/minorFont 缺 <a:latin> 时）。
DEFAULT_LATIN_FONT = "Calibri"

# clrScheme 需要提取的具名颜色槽。
COLOR_SLOTS = (
    "dk1", "lt1", "dk2", "lt2",
    "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
)

# run 脚本标签。
SCRIPT_CJK = "cjk"
SCRIPT_LATIN = "latin"


@dataclass
class MasterFonts:
    """从母版主题 <a:fontScheme> 提取的字体集合。

    - latin_major / latin_minor: majorFont / minorFont 的 <a:latin> typeface。
    - cjk_major  / cjk_minor:    majorFont / minorFont 的 CJK 字体
      （优先 <a:ea>，其次 <a:font script="Hans">，再兜底 DEFAULT_CJK_FONT）。
    """

    latin_major: str
    latin_minor: str
    cjk_major: str
    cjk_minor: str


@dataclass(frozen=True)
class MasterTheme:
    """母版主题的取色取字集合（R7.1 的唯一合法来源）。

    颜色与字体**只**从 Master_Template 的 `ppt/theme/themeN.xml` 动态提取，
    绝不硬编码。这是允许被 run 绑定的字体/颜色的收敛点：

    - latin_font:       正文拉丁字体（minorFont 的 <a:latin>）。
    - cjk_font:         正文 CJK 字体（minorFont 的 <a:ea>，如 "微软雅黑"/"Microsoft YaHei"）。
    - latin_major_font: 标题拉丁字体（majorFont 的 <a:latin>）。
    - cjk_major_font:   标题 CJK 字体（majorFont 的 <a:ea>）。
    - colors:           母版主题颜色映射 {scheme 槽名 → 十六进制/系统色}
                        （dk1/lt1/dk2/lt2/accent1..6）。这是**唯一合法的颜色来源**：
                        任何 run 颜色都必须取自该映射（见 resolve_master_color）。

    font_set 汇总全部母版字体，供 task 8.4 断言「run 字体 ∈ 母版提取集合」；
    color_values 汇总全部母版颜色值，供断言「run 颜色 ∈ 母版提取集合」。
    """

    latin_font: str
    cjk_font: str
    latin_major_font: str
    cjk_major_font: str
    colors: dict  # {scheme 槽名 → 十六进制/系统色}

    @property
    def font_set(self) -> frozenset:
        """母版提取的全部字体集合（run 字体必须取自其中）。"""
        return frozenset(
            {self.latin_font, self.cjk_font, self.latin_major_font, self.cjk_major_font}
        )

    @property
    def color_values(self) -> frozenset:
        """母版提取的全部颜色值集合（run 颜色必须取自其中）。"""
        return frozenset(self.colors.values())


@dataclass
class RunSpec:
    """单个文本 run 的分设规格（供 task 8.4 属性测试断言）。

    - text:     该 run 的文本（同脚本连续片段）。
    - script:   "cjk" | "latin"。
    - typeface: 该 run 绑定的母版字体名（cjk → 母版 CJK 字体；latin → 母版拉丁字体）。
    - attr:     该字体应写入 <a:rPr> 的属性元素名（"a:ea" for cjk / "a:latin" for latin）。
    """

    text: str
    script: str
    typeface: str
    attr: str = ""


# ---------------------------------------------------------------------------
# minidom 遍历辅助
# ---------------------------------------------------------------------------


def _iter_elements(node):
    """深度优先遍历 node 下所有 Element 子节点（含后代）。"""
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            yield child
            yield from _iter_elements(child)


def _local_name(element) -> str:
    """返回元素本地名（去命名空间前缀），兼容不同前缀写法。"""
    if element.localName:
        return element.localName
    tag = element.tagName
    return tag.split(":", 1)[1] if ":" in tag else tag


def _first_child_named(node, local_name):
    """返回 node 直接子元素中首个本地名匹配者，无则 None。"""
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE and _local_name(child) == local_name:
            return child
    return None


def _first_descendant(node, local_name):
    """返回 node 下首个本地名为 local_name 的后代元素，无则 None。"""
    for element in _iter_elements(node):
        if _local_name(element) == local_name:
            return element
    return None


# ---------------------------------------------------------------------------
# 主题路径定位（best-effort）
# ---------------------------------------------------------------------------


def find_theme_path(unpacked_root: str) -> str | None:
    """在解包目录中 best-effort 定位主要主题 XML（ppt/theme/theme1.xml）。

    先尝试常规约定 ppt/theme/theme1.xml；找不到则取 ppt/theme 下任一 themeN.xml。
    找不到返回 None。
    """
    conventional = os.path.join(unpacked_root, "ppt", "theme", "theme1.xml")
    if os.path.exists(conventional):
        return conventional
    theme_dir = os.path.join(unpacked_root, "ppt", "theme")
    if os.path.isdir(theme_dir):
        candidates = sorted(
            name for name in os.listdir(theme_dir)
            if name.startswith("theme") and name.endswith(".xml")
        )
        if candidates:
            return os.path.join(theme_dir, candidates[0])
    return None


# ---------------------------------------------------------------------------
# 母版取字（fontScheme）
# ---------------------------------------------------------------------------


def _latin_typeface(font_element) -> str:
    """从 majorFont/minorFont 元素读取 <a:latin> 的 typeface（缺则空串）。"""
    latin = _first_child_named(font_element, "latin")
    return latin.getAttribute("typeface") if latin is not None else ""


def _cjk_typeface(font_element) -> str:
    """从 majorFont/minorFont 元素读取 CJK 字体。

    优先顺序：<a:ea typeface> 非空 → <a:font script="Hans"> typeface 非空 → 空串。
    （空串由上层兜底 DEFAULT_CJK_FONT。）
    """
    ea = _first_child_named(font_element, "ea")
    if ea is not None:
        typeface = ea.getAttribute("typeface")
        if typeface:
            return typeface
    for child in font_element.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue
        if _local_name(child) == "font" and child.getAttribute("script") == CJK_SCRIPT_TAG:
            typeface = child.getAttribute("typeface")
            if typeface:
                return typeface
    return ""


def extract_master_fonts(theme_xml_path: str) -> MasterFonts:
    """解析母版主题 <a:fontScheme>，提取拉丁/CJK 的 major/minor 字体。

    - 拉丁字体取 <a:majorFont>/<a:minorFont> 的 <a:latin typeface>。
    - CJK 字体优先 <a:ea>，其次 <a:font script="Hans">，再兜底 DEFAULT_CJK_FONT。
    颜色/字体**只从母版主题动态提取**（R7.1），不硬编码。

    使用 defusedxml.minidom 解析。

    Validates: Requirements 7.1
    """
    document = parse(theme_xml_path)
    font_scheme = _first_descendant(document, "fontScheme")
    if font_scheme is None:
        # 主题无 fontScheme：全部兜底（仍不硬编码具体母版，仅安全默认）。
        return MasterFonts(
            latin_major=DEFAULT_LATIN_FONT,
            latin_minor=DEFAULT_LATIN_FONT,
            cjk_major=DEFAULT_CJK_FONT,
            cjk_minor=DEFAULT_CJK_FONT,
        )

    major = _first_child_named(font_scheme, "majorFont")
    minor = _first_child_named(font_scheme, "minorFont")

    latin_major = (_latin_typeface(major) if major is not None else "") or DEFAULT_LATIN_FONT
    latin_minor = (_latin_typeface(minor) if minor is not None else "") or DEFAULT_LATIN_FONT
    cjk_major = (_cjk_typeface(major) if major is not None else "") or DEFAULT_CJK_FONT
    cjk_minor = (_cjk_typeface(minor) if minor is not None else "") or DEFAULT_CJK_FONT

    return MasterFonts(
        latin_major=latin_major,
        latin_minor=latin_minor,
        cjk_major=cjk_major,
        cjk_minor=cjk_minor,
    )


# ---------------------------------------------------------------------------
# 母版取色（clrScheme）
# ---------------------------------------------------------------------------


def _resolve_color_value(slot_element) -> str:
    """从颜色槽元素（如 <a:dk1>）解析出十六进制/系统颜色值。

    - <a:srgbClr val="RRGGBB"> → 返回 val。
    - <a:sysClr val="..." lastClr="RRGGBB"> → 返回 lastClr（无则 val）。
    无法解析返回空串。
    """
    for child in slot_element.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue
        name = _local_name(child)
        if name == "srgbClr":
            return child.getAttribute("val")
        if name == "sysClr":
            return child.getAttribute("lastClr") or child.getAttribute("val")
    return ""


def extract_master_colors(theme_xml_path: str) -> dict:
    """解析母版主题 <a:clrScheme>，提取 dk1/lt1/dk2/lt2/accent1..6 颜色。

    返回 {槽名: 十六进制颜色值}。颜色**只从母版主题动态提取**（R7.1）。

    使用 defusedxml.minidom 解析。

    Validates: Requirements 7.1
    """
    document = parse(theme_xml_path)
    clr_scheme = _first_descendant(document, "clrScheme")
    colors: dict = {}
    if clr_scheme is None:
        return colors
    for child in clr_scheme.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue
        slot = _local_name(child)
        if slot in COLOR_SLOTS:
            value = _resolve_color_value(child)
            if value:
                colors[slot] = value
    return colors


# ---------------------------------------------------------------------------
# 母版主题聚合（取色 + 取字）
# ---------------------------------------------------------------------------


def extract_master_theme(theme_xml_path: str) -> MasterTheme:
    """从母版主题 themeN.xml 一次性提取字体与颜色，返回 MasterTheme。

    合并 extract_master_fonts（<a:fontScheme>）与 extract_master_colors
    （<a:clrScheme>）的结果——这是 run 级取色取字的**唯一合法来源**（R7.1）：
      - latin_font / cjk_font        取自 minorFont（正文字体）；
      - latin_major_font / cjk_major_font 取自 majorFont（标题字体）；
      - colors                       为主题颜色（dk1/lt1/dk2/lt2/accent1..6）的值集合。

    使用 defusedxml.minidom 解析（见设计 A4）。

    Validates: Requirements 7.1
    """
    fonts = extract_master_fonts(theme_xml_path)
    colors = extract_master_colors(theme_xml_path)
    return MasterTheme(
        latin_font=fonts.latin_minor,
        cjk_font=fonts.cjk_minor,
        latin_major_font=fonts.latin_major,
        cjk_major_font=fonts.cjk_major,
        colors=dict(colors),
    )


# ---------------------------------------------------------------------------
# run 级中英脚本切分
# ---------------------------------------------------------------------------


def is_cjk(char: str) -> bool:
    """判定单个字符是否属于 CJK / East-Asian 脚本。

    覆盖常见 East-Asian 区段：CJK 部首、符号标点、假名、统一表意文字（含扩展 A）、
    兼容表意文字、全角形式等。ASCII/拉丁/数字/西文标点返回 False。
    """
    if not char:
        return False
    code = ord(char[0])
    return (
        0x2E80 <= code <= 0x2EFF   # CJK 部首补充
        or 0x3000 <= code <= 0x303F  # CJK 符号和标点
        or 0x3040 <= code <= 0x30FF  # 平假名 / 片假名
        or 0x3100 <= code <= 0x312F  # 注音符号
        or 0x3400 <= code <= 0x4DBF  # CJK 扩展 A
        or 0x4E00 <= code <= 0x9FFF  # CJK 统一表意文字
        or 0xF900 <= code <= 0xFAFF  # CJK 兼容表意文字
        or 0xFF00 <= code <= 0xFFEF  # 全角/半角形式
    )


def split_runs_by_script(text: str) -> list:
    """将文本切分为「同脚本连续片段」列表，每段标注 "cjk" 或 "latin"。

    中英混排文本被拆成 per-script run，使 CJK 与拉丁可分别绑定母版字体
    （R7.2 / R7.3）。非 CJK 字符（拉丁字母、数字、空白、西文标点等）归入 "latin"。

    返回 list[tuple[str, str]]，元素为 (segment_text, script)；空串返回 []。

    示例："远景Envision智能" → [("远景","cjk"), ("Envision","latin"), ("智能","cjk")]

    Validates: Requirements 7.2, 7.3
    """
    if not text:
        return []
    segments: list = []
    current_chars: list = []
    current_script = None
    for char in text:
        script = SCRIPT_CJK if is_cjk(char) else SCRIPT_LATIN
        if current_script is None:
            current_script = script
            current_chars = [char]
        elif script == current_script:
            current_chars.append(char)
        else:
            segments.append(("".join(current_chars), current_script))
            current_script = script
            current_chars = [char]
    if current_chars:
        segments.append(("".join(current_chars), current_script))
    return segments


def build_run_specs(paragraph_text: str, fonts: MasterFonts, *, use_minor: bool = True) -> list:
    """给定段落文本与母版字体，产出每个 run 的分设规格（RunSpec 列表）。

    每个 RunSpec 记录 run 文本、脚本、应绑定的母版字体及其写入 <a:rPr> 的属性名：
      - CJK run  → typeface = 母版 CJK 字体，attr = "a:ea"
      - 拉丁 run → typeface = 母版拉丁字体，attr = "a:latin"

    use_minor=True 使用正文（minorFont）字体，False 使用标题（majorFont）字体。

    Validates: Requirements 7.2, 7.3
    """
    cjk_font = fonts.cjk_minor if use_minor else fonts.cjk_major
    latin_font = fonts.latin_minor if use_minor else fonts.latin_major
    specs: list = []
    for segment_text, script in split_runs_by_script(paragraph_text):
        if script == SCRIPT_CJK:
            specs.append(RunSpec(text=segment_text, script=SCRIPT_CJK,
                                 typeface=cjk_font, attr="a:ea"))
        else:
            specs.append(RunSpec(text=segment_text, script=SCRIPT_LATIN,
                                 typeface=latin_font, attr="a:latin"))
    return specs


def font_for_run(run_kind: str, theme: MasterTheme, *, use_minor: bool = True) -> str:
    """返回某个 run（按脚本分类）应绑定的母版字体名。

    这是 run→字体绑定的确定性收敛点，供 task 8.4 属性测试断言：
      - CJK run（run_kind=="cjk"）  → 母版 CJK 字体（避免中文回退无字形拉丁字体，R7.2）；
      - 拉丁 run（run_kind=="latin"）→ 母版拉丁字体（R7.3）。
    返回值恒 ∈ theme.font_set（母版提取集合）。

    use_minor=True 使用正文（minorFont）字体，False 使用标题（majorFont）字体。

    Validates: Requirements 7.2, 7.3
    """
    if run_kind == SCRIPT_CJK:
        return theme.cjk_font if use_minor else theme.cjk_major_font
    if run_kind == SCRIPT_LATIN:
        return theme.latin_font if use_minor else theme.latin_major_font
    raise ValueError(f"unknown run_kind: {run_kind!r} (expected 'cjk' or 'latin')")


# ---------------------------------------------------------------------------
# 将字体写入 run 的 <a:rPr>
# ---------------------------------------------------------------------------


def apply_run_fonts(rpr_element, script: str, fonts: MasterFonts, document,
                    *, use_minor: bool = True) -> str:
    """为某个 run 的 <a:rPr> 按脚本写入母版字体，返回实际绑定的 typeface。

    - CJK run（script=="cjk"）：写入 <a:ea typeface="母版 CJK 字体">，避免中文
      回退到无字形拉丁字体（R7.2）。
    - 拉丁 run（script=="latin"）：写入 <a:latin typeface="母版拉丁字体">（R7.3）。

    若 rPr 已有同名字体元素则改写其 typeface（幂等），否则新建并追加。
    document 为 defusedxml.minidom 解析所得 Document，用于 createElement。
    """
    cjk_font = fonts.cjk_minor if use_minor else fonts.cjk_major
    latin_font = fonts.latin_minor if use_minor else fonts.latin_major

    if script == SCRIPT_CJK:
        attr_name, typeface = "a:ea", cjk_font
    else:
        attr_name, typeface = "a:latin", latin_font

    local = attr_name.split(":", 1)[1]
    existing = _first_child_named(rpr_element, local)
    if existing is not None:
        existing.setAttribute("typeface", typeface)
    else:
        element = document.createElement(attr_name)
        element.setAttribute("typeface", typeface)
        rpr_element.appendChild(element)
    return typeface


# ---------------------------------------------------------------------------
# 基于 MasterTheme 的 rPr 字体子元素构造（无副作用，供 task 8.4 断言）
# ---------------------------------------------------------------------------


def _xml_escape_attr(value: str) -> str:
    """转义属性值中的 XML 特殊字符（字体名一般安全，防御性处理）。"""
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_run_rpr(script: str, master_theme: MasterTheme, *, use_minor: bool = True) -> str:
    """构造某个 run 应写入 `<a:rPr>` 的**字体子元素 XML**（字符串，无副作用）。

    按脚本分设，字体只取自 master_theme（R7.1）：
      - CJK run（script=="cjk"）  → `<a:ea typeface="母版 CJK 字体"/>`，避免中文回退
        到无字形拉丁字体（R7.2）；
      - 拉丁 run（script=="latin"）→ `<a:latin typeface="母版拉丁字体"/>`（R7.3）。

    use_minor=True 使用正文（minorFont）字体，False 使用标题（majorFont）字体。
    返回的 typeface 恒 ∈ master_theme.font_set。

    Validates: Requirements 7.1, 7.2, 7.3
    """
    typeface = font_for_run(script, master_theme, use_minor=use_minor)
    attr_name = "a:ea" if script == SCRIPT_CJK else "a:latin"
    return f'<{attr_name} typeface="{_xml_escape_attr(typeface)}"/>'


def apply_master_fonts_to_paragraph(
    paragraph_text: str, master_theme: MasterTheme, *, use_minor: bool = True
) -> list:
    """给定段落文本与母版主题，产出**每个 run 的字体分设规格**（RunSpec 列表）。

    段落先按脚本切成同脚本连续片段（split_runs_by_script），同段落内中/英 run
    分别绑定母版 CJK / 拉丁字体（R7.3），使 CJK run 不回退到无字形拉丁字体（R7.2）。
    每个 RunSpec 的 typeface 只取自 master_theme（R7.1），恒 ∈ master_theme.font_set。

    每个 RunSpec：
      - text:     该 run 文本（同脚本连续片段）；
      - script:   "cjk" | "latin"；
      - typeface: 该 run 绑定的母版字体（cjk→母版 CJK 字体；latin→母版拉丁字体）；
      - attr:     写入 `<a:rPr>` 的字体子元素名（cjk→"a:ea"；latin→"a:latin"）。

    RunSpec.attr + typeface 组合即可用 build_run_rpr 生成 rPr 字体子元素 XML。

    Validates: Requirements 7.1, 7.2, 7.3
    """
    specs: list = []
    for segment_text, script in split_runs_by_script(paragraph_text):
        typeface = font_for_run(script, master_theme, use_minor=use_minor)
        attr = "a:ea" if script == SCRIPT_CJK else "a:latin"
        specs.append(RunSpec(text=segment_text, script=script, typeface=typeface, attr=attr))
    return specs


# ---------------------------------------------------------------------------
# 颜色校验：颜色只能取自母版提取集合
# ---------------------------------------------------------------------------


class ColorNotInMasterError(ValueError):
    """请求的颜色不在母版提取集合内（R7.1 违规）。"""


def resolve_master_color(requested: str, master_theme: MasterTheme) -> str:
    """校验并返回一个**只来自母版提取集合**的颜色值（R7.1）。

    requested 可为：
      - scheme 槽名（如 "accent1"/"dk1"）—— 返回其在 master_theme.colors 中的十六进制值；
      - 十六进制颜色值（如 "1F2A44"，大小写不敏感）—— 若存在于母版颜色值集合则返回
        （规范化为母版内存储的原值）。

    若 requested 既非已知槽名、其值也不在母版颜色值集合内，则抛
    ColorNotInMasterError —— **拒绝母版集合外的颜色**，保证颜色只从母版动态提取。

    Validates: Requirements 7.1
    """
    if requested is None:
        raise ColorNotInMasterError("requested color is None")

    # 1) 作为 scheme 槽名解析。
    if requested in master_theme.colors:
        return master_theme.colors[requested]

    # 2) 作为十六进制值解析（大小写不敏感匹配母版颜色值）。
    normalized = requested.lstrip("#").upper()
    for value in master_theme.colors.values():
        if value.lstrip("#").upper() == normalized:
            return value

    raise ColorNotInMasterError(
        f"color {requested!r} is not in master-extracted set "
        f"{sorted(master_theme.colors.values())}"
    )
# @AI_GENERATED: end

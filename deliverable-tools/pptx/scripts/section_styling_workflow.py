# @AI_GENERATED
"""Top-level orchestration wiring the section-styling enforcement layer into the
既有模板工作流（Task 10.1 集成与布线）。

本模块把 Python 强制层（`section_style_binder` 的 `parse_sections`+`bind_pages`
与 `pre_delivery_gate` 的 `run_gate`）串接进既有模板链路：

    unpack.py → <p:sldIdLst> 操作 → 编辑 slideN.xml → clean.py → [本模块] → pack.py

即：在**编辑阶段之后、pack.py 之前**，对一个已解包的 deck 目录（unpacked/）：
  1. 读取 `ppt/presentation.xml` 的 `<p:sldIdLst>` 顺序，按序还原每张 slide 的
     `slideN.xml` 文件，构建 BoundPage 生成序列（build_sequence）。
  2. `parse_sections(ppt/presentation.xml)` 解析具名节，`bind_pages(...)` 执行
     位置法角色识别 + 固定映射确定性绑定（binder 内部完成 rels layout 重指向）。
  3. pack 之前，用 `pre_delivery_gate.resolve_section_for_slide(slide_file)` 从每张
     成片 slide 的 layout 关系**反解实际 Style_Source**，再 `run_gate(bound_pages,
     deck_text, value_tree_model)` 聚合 G1/G2/G3。门槛失败即阻断打包。
  4. 顶层 CLI 把全流程串起来：默认只做 bind+gate 并报告「是否可打包」（打包为操作者
     下一步，对应 editing.md step 6a）；可选 `--pack --original --out` 仅在门槛通过
     时才调用 office/pack.py。

设计约束：
  - 复用 `section_style_binder` / `pre_delivery_gate` 的既有函数（sldId→rId、rels
    解析、路径规范化、layout 反解），不重复实现。
  - 全部 XML 读取使用 defusedxml.minidom（禁用 xml.etree.ElementTree，见设计 A4）。
  - 无游离未接入代码：build_sequence → parse+bind → gate → (可选) pack 单一链路。

Validates: Requirements 1.1, 1.2, 1.3, 1.4, 4.2
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass

from defusedxml.minidom import parse

# 允许作为脚本从 scripts/ 目录直接导入同级模块（与既有脚本/测试一致）。
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)

from section_style_binder import (  # noqa: E402
    BoundPage,
    Role,
    SectionInfo,
    _iter_elements,
    _local_name,
    _rels_targets_by_id,
    _resolve_target,
    bind_pages,
    parse_sections,
)
from pre_delivery_gate import (  # noqa: E402
    GateReport,
    build_value_tree_model,
    resolve_section_for_slide,
    run_gate,
    _format_gate_report,
)

# 当某页的实际 Style_Source 无法从其 layout 关系反解时使用的哨兵值。
# 该值不属于任何具名节，故必然与 FIXED_MAPPING[role] 期望值不等 → 被门槛判为错配。
UNRESOLVED_STYLE_SOURCE = "UNRESOLVED"


# ---------------------------------------------------------------------------
# 解包目录路径与 <p:sldIdLst> 顺序还原
# ---------------------------------------------------------------------------


def _presentation_paths(unpacked_root: str) -> tuple[str, str, str]:
    """由解包根目录推出 (presentation.xml, presentation.xml.rels, ppt 目录)。"""
    ppt_dir = os.path.join(unpacked_root, "ppt")
    presentation_xml = os.path.join(ppt_dir, "presentation.xml")
    presentation_rels = os.path.join(ppt_dir, "_rels", "presentation.xml.rels")
    return presentation_xml, presentation_rels, ppt_dir


def _sldid_rid_in_order(presentation_xml_path: str) -> list[str]:
    """按 <p:sldIdLst> 出现顺序返回其 <p:sldId> 的 r:id 列表。

    仅遍历 <p:sldIdLst> 内的 <p:sldId>（携带 r:id 的关系引用），刻意忽略
    <p14:sectionLst> 内的 <p14:sldId>（无 r:id），从而严格得到「幻灯片放映顺序」。
    使用 defusedxml.minidom。
    """
    document = parse(presentation_xml_path)
    ordered_rids: list[str] = []
    for element in _iter_elements(document):
        if _local_name(element) != "sldIdLst":
            continue
        for child in _iter_elements(element):
            if _local_name(child) != "sldId":
                continue
            r_id = child.getAttribute("r:id")
            if not r_id:
                # r:id 属性带命名空间前缀；回退遍历属性寻找以 rId 开头的关系 id。
                for attr_name, attr_value in child.attributes.items():
                    if attr_name.split(":", 1)[-1] == "id" and attr_value.startswith(
                        "rId"
                    ):
                        r_id = attr_value
                        break
            if r_id:
                ordered_rids.append(r_id)
        break  # 只有一个 <p:sldIdLst>
    return ordered_rids


def ordered_slide_files(unpacked_root: str) -> list[str]:
    """按 <p:sldIdLst> 放映顺序返回各 slide 的 slideN.xml 绝对路径。

    路径链：<p:sldIdLst> 顺序 → r:id → presentation.xml.rels 的 slide Target
        → 规范化为绝对路径。使用既有 rels 解析/路径规范化辅助，避免重复实现。
    """
    presentation_xml, presentation_rels, ppt_dir = _presentation_paths(unpacked_root)
    if not (os.path.exists(presentation_xml) and os.path.exists(presentation_rels)):
        raise FileNotFoundError(
            f"解包目录缺少 presentation.xml 或其 .rels：{unpacked_root}"
        )
    targets = _rels_targets_by_id(presentation_rels)
    slide_files: list[str] = []
    for r_id in _sldid_rid_in_order(presentation_xml):
        target = targets.get(r_id)
        if target:
            slide_files.append(_resolve_target(ppt_dir, target))
    return slide_files


# ---------------------------------------------------------------------------
# 生成序列构建 → parse + bind → 反解实际 Style_Source → 门槛聚合
# ---------------------------------------------------------------------------


def build_sequence(unpacked_root: str) -> list[BoundPage]:
    """按放映顺序构建 BoundPage 生成序列（role/style_source 由 bind_pages 覆写）。

    每张 slide 依 <p:sldIdLst> 顺序生成一个 BoundPage，index 为 0 基放映位序，
    slide_file 指向该页的 slideN.xml。role/style_source 先占位，随后由
    bind_pages 依位置法与固定映射确定性覆写。
    """
    slide_files = ordered_slide_files(unpacked_root)
    return [
        BoundPage(
            index=index,
            role=Role.CONTENT,  # 占位，bind_pages 覆写
            style_source="",  # 占位，bind_pages 覆写
            slide_file=slide_file,
        )
        for index, slide_file in enumerate(slide_files)
    ]


def reconstruct_style_sources(bound_pages: list[BoundPage]) -> list[BoundPage]:
    """从每张成片 slide 的 layout 关系反解实际 Style_Source，返回校验用页列表。

    对每页调用 pre_delivery_gate.resolve_section_for_slide(slide_file)：
      - 反解成功 → 以反解所得节名作为该页实际 style_source；
      - 反解失败（缺 rels / 缺关系 / 未知 layout，返回 None）→ 记为
        UNRESOLVED_STYLE_SOURCE 哨兵，使其必然被追溯校验判为错配（按任务要求
        「无法解析实际节」= 门槛不匹配）。

    role 沿用 bind_pages 的位置法结果不变，从而门槛比对的是「实际反解 Style_Source
    vs 该页 role 的期望节」，反映真实成片而非逻辑绑定值。
    """
    verified: list[BoundPage] = []
    for page in bound_pages:
        actual = resolve_section_for_slide(page.slide_file)
        verified.append(
            BoundPage(
                index=page.index,
                role=page.role,
                style_source=actual if actual is not None else UNRESOLVED_STYLE_SOURCE,
                slide_file=page.slide_file,
            )
        )
    return verified


@dataclass
class WorkflowResult:
    """一次 parse+bind+gate 的完整结果。

    - sections:       parse_sections 解析出的具名节（按名索引）。
    - bound_pages:    bind_pages 后的页列表（style_source 为逻辑绑定目标节）。
    - verified_pages: 从成片 layout 关系反解实际 Style_Source 后的校验用页列表。
    - report:         run_gate 聚合门槛报告（passed 决定是否可打包）。
    """

    sections: dict[str, SectionInfo]
    bound_pages: list[BoundPage]
    verified_pages: list[BoundPage]
    report: GateReport


def parse_bind_and_gate(
    unpacked_root: str,
    deck_text: str,
    ending_requested: bool = False,
    value_tree_model=None,
) -> WorkflowResult:
    """编辑阶段之后、pack 之前的核心编排：parse_sections → bind_pages → run_gate。

    步骤：
      1. parse_sections(ppt/presentation.xml) 读取具名节（缺 cover/content 抛错）。
      2. build_sequence(unpacked_root) 按放映顺序构建生成序列。
      3. bind_pages(sequence, sections, ending_requested) 位置法角色识别 + 固定映射
         确定性绑定（内部完成每页 slide 的 slideLayout 关系重指向）。
      4. reconstruct_style_sources(...) 从成片反解实际 Style_Source。
      5. run_gate(verified_pages, deck_text, value_tree_model) 聚合 G1/G2/G3。

    返回 WorkflowResult；report.passed 为 True 时方可继续 pack.py 出片。

    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 4.2
    """
    presentation_xml, _, _ = _presentation_paths(unpacked_root)
    sections = parse_sections(presentation_xml)

    sequence = build_sequence(unpacked_root)
    bound_pages = bind_pages(sequence, sections, ending_requested)

    verified_pages = reconstruct_style_sources(bound_pages)
    report = run_gate(verified_pages, deck_text, value_tree_model)

    return WorkflowResult(
        sections=sections,
        bound_pages=bound_pages,
        verified_pages=verified_pages,
        report=report,
    )


# ---------------------------------------------------------------------------
# 可选：门槛通过后调用 office/pack.py 打包（非默认、非破坏性默认）
# ---------------------------------------------------------------------------


def pack_deck(
    unpacked_root: str,
    output_file: str,
    original_file: str,
) -> tuple[bool, str]:
    """仅在门槛已通过后调用 office/pack.py 打包成片（子进程调用，避免污染导入空间）。

    以子进程运行 `py office/pack.py <unpacked> <out> --original <template>`，cwd
    设为 office 目录（使其 `from validators import ...` 相对导入成立），并设置
    PYTHONUTF8=1（Windows 中文 locale 下 pack 校验器需要，见母版实探环境备注）。

    返回 (success, combined_output)。
    """
    office_dir = os.path.join(_SCRIPTS_DIR, "office")
    pack_script = os.path.join(office_dir, "pack.py")
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    completed = subprocess.run(
        [
            _python_executable(),
            pack_script,
            os.path.abspath(unpacked_root),
            os.path.abspath(output_file),
            "--original",
            os.path.abspath(original_file),
        ],
        cwd=office_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    success = completed.returncode == 0 and "Error" not in (completed.stdout or "")
    return success, output


def _python_executable() -> str:
    """返回用于子进程的 Python 可执行程序（优先当前解释器，回退到 `py`）。"""
    return sys.executable or "py"


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def _load_deck_text(path: str) -> str:
    """读取 markitdown 抽取的成片正文文本文件（UTF-8）。"""
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _load_value_tree_model(path: str):
    """从 JSON 事实构建 ValueTreeModel（可选 G3）。"""
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    return build_value_tree_model(
        nodes=raw.get("nodes"),
        operators=raw.get("operators"),
        edges=[tuple(edge) for edge in raw.get("edges", [])],
        flattened_text=raw.get("flattened_text", ""),
        expects_operators=raw.get("expects_operators", False),
        expects_edges=raw.get("expects_edges", False),
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="section_styling_workflow",
        description=(
            "模板节样式确定性绑定 + 出片前门槛的顶层编排。"
            "在编辑阶段之后、pack.py 之前运行：parse_sections + bind_pages 绑定，"
            "run_gate 聚合门槛，报告是否可打包。门槛通过退出 0，失败退出 2。"
        ),
    )
    parser.add_argument(
        "--unpacked",
        required=True,
        help="已解包并完成编辑的 deck 根目录（含 ppt/presentation.xml）。",
    )
    parser.add_argument(
        "--deck-text",
        required=True,
        help="markitdown 抽取的成片正文文本文件（`python -m markitdown out.pptx` 的输出）。",
    )
    parser.add_argument(
        "--ending",
        action="store_true",
        help="显式请求 ending 节（默认不启用，见 Requirement 3）。",
    )
    parser.add_argument(
        "--value-tree-json",
        default=None,
        help="可选：ValueTreeModel 事实的 JSON 文件（G3 价值树节点化校验）。",
    )
    parser.add_argument(
        "--pack",
        action="store_true",
        help="可选：门槛通过后调用 office/pack.py 打包（需配合 --original 与 --out）。",
    )
    parser.add_argument(
        "--original",
        default=None,
        help="打包校验用的原始模板 .pptx（仅 --pack 时需要）。",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="打包输出的 .pptx 路径（仅 --pack 时需要）。",
    )
    return parser


def _main(argv=None) -> int:
    """CLI 入口：parse+bind → gate → 报告；可选门槛通过后打包。

    退出码：门槛通过（且可选打包成功）0；门槛失败 2；用法/输入错误 1。
    默认不执行破坏性打包——CLI 职责为运行 bind+gate 并报告「是否可打包」；
    打包是操作者下一步（对应 editing.md step 6a）。仅 --pack 且门槛通过时才打包。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if not os.path.isdir(args.unpacked):
        print(f"error: --unpacked 不是目录：{args.unpacked}", file=sys.stderr)
        return 1

    try:
        deck_text = _load_deck_text(args.deck_text)
    except OSError as error:
        print(f"error: 无法读取 --deck-text 文件：{error}", file=sys.stderr)
        return 1

    value_tree_model = None
    if args.value_tree_json:
        try:
            value_tree_model = _load_value_tree_model(args.value_tree_json)
        except (OSError, ValueError) as error:
            print(f"error: 无法解析 --value-tree-json：{error}", file=sys.stderr)
            return 1

    if args.pack and not (args.original and args.out):
        print(
            "error: --pack 需要同时提供 --original <template.pptx> 与 --out <out.pptx>。",
            file=sys.stderr,
        )
        return 1

    try:
        result = parse_bind_and_gate(
            args.unpacked,
            deck_text,
            ending_requested=args.ending,
            value_tree_model=value_tree_model,
        )
    except Exception as error:  # 结构性缺陷等 → 阻断出片
        print(f"error: parse/bind/gate 失败：{error}", file=sys.stderr)
        return 1

    report = result.report
    stream = sys.stdout if report.passed else sys.stderr
    print(_format_gate_report(report), file=stream)

    if not report.passed:
        # 门槛失败 → 阻断打包，非零退出。
        return 2

    # 门槛通过：打印绑定摘要，报告可打包。
    print("", file=sys.stdout)
    print("绑定摘要（放映顺序 / role → 实际 Style_Source）：", file=sys.stdout)
    for page in result.verified_pages:
        role_name = getattr(page.role, "name", page.role)
        print(
            f"  #{page.index} {role_name} → {page.style_source} "
            f"({os.path.basename(page.slide_file)})",
            file=sys.stdout,
        )

    if args.pack:
        success, output = pack_deck(args.unpacked, args.out, args.original)
        print("", file=sys.stdout)
        print("office/pack.py 输出：", file=sys.stdout)
        print(output, file=sys.stdout)
        if not success:
            print("error: 打包失败。", file=sys.stderr)
            return 1
        print(f"已打包出片：{args.out}", file=sys.stdout)
        return 0

    print("", file=sys.stdout)
    print(
        "READY TO PACK —— 门槛通过。下一步由操作者执行 "
        "`pack.py --original <template.pptx>` 出片（editing.md step 6a）。",
        file=sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
# @AI_GENERATED: end

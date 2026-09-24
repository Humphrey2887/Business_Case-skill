# @AI_GENERATED
"""Feature: pptx-template-section-styling, Property 7: 封面占位符填充与母版占位符承载

Property-based test for `cover_placeholder_filler.fill_cover_placeholders`.

*For any* 已绑定 cover 节的封面页与真实封面数据（客户名/项目标题/日期），生成后这些
文本均位于 cover 版式自带的 `<p:ph>` 占位符内，且不产生无占位符的新建浮动文本框。

对任意由 hypothesis 生成的真实文本值（含 CJK / 拉丁 / 数字，非空）：
  - 回填后所有可见文本均由 `<p:ph>` 占位符承载
    （cover_text_is_placeholder_borne(path) 为 True）；
  - 形状数量不变（未新建浮动文本框；report.created_text_box 为 False）；
  - 每个已回填字段的文本出现在某个占位符形状内。

每个 hypothesis 示例使用独立临时固件（写入 → 运行 → 断言 → 清理）。
XML 文本经模块 DOM 写入（自动转义），故生成器无需回避 XML 特殊字符。

Validates: Requirements 6.1, 6.2
"""

import os
import sys
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st

# 允许从 tests/ 目录导入位于上级 scripts/ 的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cover_placeholder_filler as cpf  # noqa: E402


# 含 ctrTitle / subTitle / dt 三个占位符的最小 cover slide 固件；
# ctrTitle 内含母版默认占位文字 "Cover Page Style"（回填应覆盖清除）。
COVER_FIXTURE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:sp>
      <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/>
        <p:nvPr><p:ph type="ctrTitle"/></p:nvPr>
      </p:nvSpPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>
        <a:p><a:r><a:t>Cover Page Style</a:t></a:r></a:p>
      </p:txBody>
    </p:sp>
    <p:sp>
      <p:nvSpPr><p:cNvPr id="3" name="Subtitle"/><p:cNvSpPr/>
        <p:nvPr><p:ph type="subTitle" idx="1"/></p:nvPr>
      </p:nvSpPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t></a:t></a:r></a:p></p:txBody>
    </p:sp>
    <p:sp>
      <p:nvSpPr><p:cNvPr id="4" name="Date"/><p:cNvSpPr/>
        <p:nvPr><p:ph type="dt" idx="10"/></p:nvPr>
      </p:nvSpPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t></a:t></a:r></a:p></p:txBody>
    </p:sp>
  </p:spTree></p:cSld>
</p:sld>
"""


# 真实封面文本：CJK + 拉丁 + 数字混排字母表，非空且去除首尾空白后仍非空。
_ALPHABET = (
    st.characters(min_codepoint=0x4E00, max_codepoint=0x9FFF)  # CJK 统一表意
    | st.characters(min_codepoint=ord("A"), max_codepoint=ord("Z"))
    | st.characters(min_codepoint=ord("a"), max_codepoint=ord("z"))
    | st.characters(min_codepoint=ord("0"), max_codepoint=ord("9"))
)
_real_text = st.text(alphabet=_ALPHABET, min_size=1, max_size=40).filter(
    lambda s: s.strip() != ""
)


# 仅含 ctrTitle 占位符（subTitle / dt 缺失）的 cover 固件；
# 用于断言缺失占位符字段被记入 report.unfilled 且仍不新建浮动文本框。
COVER_FIXTURE_TITLE_ONLY = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:sp>
      <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/>
        <p:nvPr><p:ph type="ctrTitle"/></p:nvPr>
      </p:nvSpPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>
        <a:p><a:r><a:t>Cover Page Style</a:t></a:r></a:p>
      </p:txBody>
    </p:sp>
  </p:spTree></p:cSld>
</p:sld>
"""


def _write_fixture(xml: str = COVER_FIXTURE) -> str:
    """写入一份全新的 cover 固件到临时文件，返回其路径。"""
    fd, path = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(xml)
    return path


@settings(max_examples=150)
@given(
    client_name=_real_text,
    project_title=_real_text,
    date=_real_text,
)
def test_cover_text_is_placeholder_borne(
    client_name: str, project_title: str, date: str
) -> None:
    """Property 7: 回填任意真实文本后，封面文本均由 `<p:ph>` 占位符承载，
    形状数量不变（无新建浮动文本框），每个已填字段文本落在某占位符形状内。

    Validates: Requirements 6.1, 6.2
    """
    path = _write_fixture()
    try:
        shapes_before = cpf.list_text_shapes(path)

        report = cpf.fill_cover_placeholders(
            path,
            client_name=client_name,
            project_title=project_title,
            date=date,
        )

        # R6.2：绝不新建浮动文本框（模块硬不变量）。
        assert report.created_text_box is False

        # R6.2：形状数量不变——未新增任何 <p:sp>。
        shapes_after = cpf.list_text_shapes(path)
        assert len(shapes_after) == len(shapes_before)

        # R6.2 / Property 7：所有承载文本的形状均为占位符形状。
        assert cpf.cover_text_is_placeholder_borne(path) is True

        # 该固件三个占位符齐备，故三字段均应回填成功。
        assert report.unfilled == []
        assert set(report.filled) == {
            cpf.FIELD_PROJECT_TITLE,
            cpf.FIELD_CLIENT_NAME,
            cpf.FIELD_DATE,
        }

        # R6.1：每个已回填字段的文本出现在某个占位符形状（has_ph）内。
        placeholder_texts = [s.text for s in shapes_after if s.has_ph]
        for value in (client_name, project_title, date):
            assert any(value in text for text in placeholder_texts)
    finally:
        os.remove(path)


@settings(max_examples=150)
@given(
    client_name=_real_text,
    project_title=_real_text,
    date=_real_text,
)
def test_missing_placeholders_go_unfilled_without_new_box(
    client_name: str, project_title: str, date: str
) -> None:
    """Property 7 变体：subTitle / dt 占位符缺失时，对应字段记入 report.unfilled，
    仍绝不新建浮动文本框，且封面文本仍全部由 `<p:ph>` 占位符承载、形状数量不变。

    Validates: Requirements 6.1, 6.2
    """
    path = _write_fixture(COVER_FIXTURE_TITLE_ONLY)
    try:
        shapes_before = cpf.list_text_shapes(path)

        report = cpf.fill_cover_placeholders(
            path,
            client_name=client_name,
            project_title=project_title,
            date=date,
        )

        # R6.2：缺失占位符不触发新建浮动文本框。
        assert report.created_text_box is False

        # 仅 ctrTitle 存在 → project_title 命中，client_name / date 记入 unfilled。
        assert report.filled.get(cpf.FIELD_PROJECT_TITLE) == "ctrTitle"
        assert cpf.FIELD_CLIENT_NAME in report.unfilled
        assert cpf.FIELD_DATE in report.unfilled

        # R6.2：形状数量不变——未新增任何 <p:sp>。
        shapes_after = cpf.list_text_shapes(path)
        assert len(shapes_after) == len(shapes_before)

        # R6.2 / Property 7：所有承载文本的形状均为占位符形状。
        assert cpf.cover_text_is_placeholder_borne(path) is True

        # R6.1：已回填的 project_title 文本落在某占位符形状内。
        placeholder_texts = [s.text for s in shapes_after if s.has_ph]
        assert any(project_title in text for text in placeholder_texts)
    finally:
        os.remove(path)
# @AI_GENERATED: end

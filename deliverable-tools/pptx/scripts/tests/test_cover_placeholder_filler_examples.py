# @AI_GENERATED
"""Example/edge unit tests for cover_placeholder_filler (Task 8.1).

固定示例断言封面占位符回填把真实文本写入**已存在**的 `<p:ph>` 占位符，且不新建
浮动文本框（Requirements 6.1 / 6.2）。属性测试由 task 8.2 单独实现，此处仅覆盖
代表性示例与边界，防命名空间/回填行为回归。

使用 defusedxml.minidom（经 cover_placeholder_filler）解析固件。
"""

import os
import sys
import tempfile
import unittest

# 让测试可直接导入 scripts 目录下的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cover_placeholder_filler as cpf  # noqa: E402


# 含 ctrTitle / subTitle / dt 三个占位符的最小 cover slide 固件；
# ctrTitle 内含母版默认占位文字 "Cover Page Style"（用于断言残留被覆盖清除）。
COVER_WITH_PLACEHOLDERS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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

# 无 subTitle 占位符的 cover：应优雅跳过 client_name，且绝不新建浮动文本框。
COVER_ONLY_TITLE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:sp>
      <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/>
        <p:nvPr><p:ph type="title"/></p:nvPr>
      </p:nvSpPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>xxxx</a:t></a:r></a:p></p:txBody>
    </p:sp>
  </p:spTree></p:cSld>
</p:sld>
"""


def _write_fixture(xml: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(xml)
    return path


class TestFindPlaceholderShapes(unittest.TestCase):
    def test_keyed_by_ph_type(self):
        path = _write_fixture(COVER_WITH_PLACEHOLDERS)
        try:
            document = cpf.parse(path)
            shapes = cpf.find_placeholder_shapes(document)
            self.assertEqual(set(shapes), {"ctrTitle", "subTitle", "dt"})
        finally:
            os.remove(path)

    def test_excludes_floating_text_box(self):
        # 追加一个无 <p:ph> 的浮动文本框，确认不被收录。
        xml = COVER_WITH_PLACEHOLDERS.replace(
            "</p:spTree>",
            "<p:sp><p:nvSpPr><p:cNvPr id=\"9\" name=\"Floating\"/><p:cNvSpPr/>"
            "<p:nvPr/></p:nvSpPr>"
            "<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>floating</a:t>"
            "</a:r></a:p></p:txBody></p:sp></p:spTree>",
        )
        path = _write_fixture(xml)
        try:
            document = cpf.parse(path)
            shapes = cpf.find_placeholder_shapes(document)
            self.assertNotIn(None, shapes)
            self.assertEqual(set(shapes), {"ctrTitle", "subTitle", "dt"})
        finally:
            os.remove(path)


class TestFillCoverPlaceholders(unittest.TestCase):
    def test_fills_into_existing_placeholders(self):
        path = _write_fixture(COVER_WITH_PLACEHOLDERS)
        try:
            shapes_before = cpf.list_text_shapes(path)
            report = cpf.fill_cover_placeholders(
                path,
                client_name="远景能源",
                project_title="智能风机运维项目",
                date="2024-06",
            )
            # 三个字段均命中已存在占位符。
            self.assertEqual(
                report.filled,
                {
                    cpf.FIELD_PROJECT_TITLE: "ctrTitle",
                    cpf.FIELD_CLIENT_NAME: "subTitle",
                    cpf.FIELD_DATE: "dt",
                },
            )
            self.assertEqual(report.unfilled, [])
            self.assertFalse(report.created_text_box)

            content = open(path, "r", encoding="utf-8").read()
            self.assertIn("智能风机运维项目", content)
            self.assertIn("远景能源", content)
            self.assertIn("2024-06", content)
            # 母版默认占位文字被真实文本覆盖清除。
            self.assertNotIn("Cover Page Style", content)

            # 形状数量不变：未新建任何 <p:sp>（无浮动文本框）。
            shapes_after = cpf.list_text_shapes(path)
            self.assertEqual(len(shapes_after), len(shapes_before))
            # 所有承载文本的形状仍为占位符形状。
            self.assertTrue(cpf.cover_text_is_placeholder_borne(path))
        finally:
            os.remove(path)

    def test_missing_placeholder_is_skipped_without_new_box(self):
        path = _write_fixture(COVER_ONLY_TITLE)
        try:
            before = len(cpf.list_text_shapes(path))
            report = cpf.fill_cover_placeholders(
                path,
                client_name="远景能源",
                project_title="智能风机运维项目",
                date="2024-06",
            )
            # 无 subTitle / dt 占位符 → 记入 unfilled，不新建浮动文本框。
            self.assertIn(cpf.FIELD_CLIENT_NAME, report.unfilled)
            self.assertIn(cpf.FIELD_DATE, report.unfilled)
            self.assertFalse(report.created_text_box)
            # project_title 写入 title 占位符（ctrTitle 缺失时退化）。
            self.assertEqual(report.filled.get(cpf.FIELD_PROJECT_TITLE), "title")
            after = len(cpf.list_text_shapes(path))
            self.assertEqual(after, before)  # 形状数量不变。
            self.assertTrue(cpf.cover_text_is_placeholder_borne(path))
        finally:
            os.remove(path)

    def test_keyword_only_arguments(self):
        # client_name/project_title/date 为 keyword-only：位置传参应报错。
        path = _write_fixture(COVER_WITH_PLACEHOLDERS)
        try:
            with self.assertRaises(TypeError):
                cpf.fill_cover_placeholders(path, "a", "b", "c")  # type: ignore[misc]
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
# @AI_GENERATED: end

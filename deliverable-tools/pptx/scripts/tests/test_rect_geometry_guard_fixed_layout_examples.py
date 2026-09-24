# @AI_GENERATED
"""Feature: pptx-template-section-styling, fixed-layout examples (Validates: Requirements 8.2)

Task 8.7：为固定版式规格编写示例测试。

固定示例断言 roadmap / ontology 页遵循 ``ppt-deck-mapping`` 固定版式规格
（rect_geometry_guard.check_fixed_layout，R8.2）：

  - Roadmap（P(11+N) 实施路径）：固定四阶段（需求摸排 → 数据汇聚与本体 →
    高价值场景上线 → 稳定运营与复制），每阶段 4-5 条关键动作。
  - Ontology（P(10+N) 技术架构）：自下而上四层横向架构（数据来源 / Ontology 本体 /
    Agent Skill / Agent 行动主体）；Ontology 本体层三框必出（语义关联本体层 /
    态势感知本体层 / 仿真决策本体层）。

模型值取自 workflows/business-pain-point/standards/ppt-deck-mapping.md。
属性测试由 Task 8.6 单独实现，此处仅覆盖代表性示例与边界。
"""

import os
import sys
import unittest

# 让测试可直接导入 scripts 目录下的被测模块。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rect_geometry_guard as guard  # noqa: E402


def _compliant_roadmap_model() -> dict:
    """固定四阶段、每阶段 4-5 条关键动作的合规 roadmap 模型（值取自 ppt-deck-mapping）。"""
    return {
        "phases": [
            {
                "name": "需求摸排",
                "actions": ["痛点访谈", "现状梳理", "价值假设", "范围界定"],
            },
            {
                "name": "数据汇聚与本体",
                "actions": ["数据接入", "本体建模", "语义关联", "质量治理", "指标定义"],
            },
            {
                "name": "高价值场景上线",
                "actions": ["场景选型", "技能开发", "灰度试点", "效果评估"],
            },
            {
                "name": "稳定运营与复制",
                "actions": ["运营监控", "迭代优化", "经验沉淀", "横向复制", "规模推广"],
            },
        ]
    }


def _compliant_ontology_model() -> dict:
    """自下而上四层、本体层三框必出的合规 ontology 模型（值取自 ppt-deck-mapping）。"""
    return {
        "layers": [
            {"name": "数据来源", "boxes": ["SCADA", "工单", "传感器"]},
            {
                "name": "Ontology 本体",
                "boxes": ["语义关联本体层", "态势感知本体层", "仿真决策本体层"],
            },
            {"name": "Agent Skill", "boxes": ["检索", "推理"]},
            {"name": "Agent 行动主体", "boxes": ["运维 Agent"]},
        ]
    }


class TestFixedLayoutRoadmap(unittest.TestCase):
    def test_compliant_roadmap_has_no_violations(self):
        model = _compliant_roadmap_model()
        self.assertEqual(guard.check_fixed_layout("roadmap", model), [])

    def test_wrong_phase_count_is_violation(self):
        # 仅三阶段 → 违反固定四阶段规格。
        model = _compliant_roadmap_model()
        model["phases"] = model["phases"][:3]
        violations = guard.check_fixed_layout("roadmap", model)
        self.assertNotEqual(violations, [])

    def test_phase_with_too_few_actions_is_violation(self):
        # 某阶段仅 3 条动作（<4）→ 违反 4-5 条区间。
        model = _compliant_roadmap_model()
        model["phases"][0]["actions"] = ["痛点访谈", "现状梳理", "范围界定"]
        violations = guard.check_fixed_layout("roadmap", model)
        self.assertNotEqual(violations, [])

    def test_phase_with_too_many_actions_is_violation(self):
        # 某阶段 6 条动作（>5）→ 违反 4-5 条区间。
        model = _compliant_roadmap_model()
        model["phases"][2]["actions"] = ["a", "b", "c", "d", "e", "f"]
        violations = guard.check_fixed_layout("roadmap", model)
        self.assertNotEqual(violations, [])


class TestFixedLayoutOntology(unittest.TestCase):
    def test_compliant_ontology_has_no_violations(self):
        model = _compliant_ontology_model()
        self.assertEqual(guard.check_fixed_layout("ontology", model), [])

    def test_wrong_layer_count_is_violation(self):
        # 仅三层 → 违反自下而上四层规格。
        model = _compliant_ontology_model()
        model["layers"] = model["layers"][:3]
        violations = guard.check_fixed_layout("ontology", model)
        self.assertNotEqual(violations, [])

    def test_body_layer_not_three_boxes_is_violation(self):
        # Ontology 本体层仅两框（≠3）→ 违反三框必出规格。
        model = _compliant_ontology_model()
        model["layers"][1]["boxes"] = ["语义关联本体层", "态势感知本体层"]
        violations = guard.check_fixed_layout("ontology", model)
        self.assertNotEqual(violations, [])


class TestFixedLayoutUnknownKind(unittest.TestCase):
    def test_unknown_page_kind_is_violation(self):
        violations = guard.check_fixed_layout("timeline", {})
        self.assertNotEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
# @AI_GENERATED: end

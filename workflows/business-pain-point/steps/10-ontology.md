<!-- @AI_GENERATED -->
# 步骤 10 · 技术架构（Ontology）

**本步可选**：当 Business Case 需要展示"价值场景靠一套什么样的 AI 技术架构来兑现"时执行，产出一页 **AI 技术架构（Ontology）图**；纯诊断/纯价值论证可跳过，由步 09 直达步 11。

把前序已识别的数据、价值方向、关键 AI 场景与价值口径，翻译成一张**横向分层、自下而上四层**的技术架构：数据来源层 → Ontology 本体知识架构层（存在论/认识论/实践论）→ Agent Skill 层 → Agent 行动主体层。所有 agent、skill、本体对象、数据来源都必须可回溯到前序产物，**不凭空生成、不套固定行业模板**。

判定标准（四层定义、三本体框、生成规则、左右侧标签、校验闸门、输出模板）见 [../standards/10-ontology-guide.md](../standards/10-ontology-guide.md)。本文件只讲「在工作流里怎么执行这一步」。

---

## 输入

- `process/01-research.yaml`（行业、客户、业务流程、**数据来源**与数据缺口）
- `process/03-value-tree.yaml`（价值目标、价值方向、影响因子）
- `process/08-scenario.yaml`（关键 AI 场景、`ai_mechanism`、`closed_loop`）
- `process/09-valuation.yaml`（关键指标、单位、基准数据、价值测算口径）

> 不得凭空生成 ontology：每个数据来源/本体对象/skill/agent 都要能回溯到上述前序内容。

## 输出

- `process/10-ontology.yaml` — 结构化技术架构（四层 + 三本体框 + 可溯源）（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)；写入失败回退 `process/10-ontology.md`，结构不变）
- `10-ontology.md` — 可读中间稿，使用 guide 输出模板

## 执行流程与校验闸门

```
Task Progress:
- [ ] 1. 数据来源层（最底层）：从 01 Research（数据来源/数据台账）+ 03 影响因子 + 08 场景识别本案例的数据来源，按案例生成、不硬编码；每类数据标 linked_scenarios，缺口写 data_gaps（不进 PPT）。
- [ ] 2. Ontology 本体层（三框）：按案例填 存在论（业务实体/对象/关系/属性）、认识论（状态识别/监测/判断/归因）、实践论（决策/优化/仿真/推荐/执行）；每框 2-4 个案例对象/能力；向下连数据、向上撑 skill。
- [ ] 3. Agent Skill 层：按案例场景生成 agent 执行任务所调用的能力（非业务场景、非系统模块）；每个 skill 关联 ontology 层与数据来源，能解释"agent 为什么能做这件事"。
- [ ] 4. Agent 行动主体层（最上层）：按案例行业与关键场景生成 4-6 个 agent（行动主体），每个体现它负责什么决策/业务动作，对应前序关键 AI 场景；空间不足优先保留最高价值场景对应的 agent。
- [ ] 5. ⛔ 校验闸门：可溯源（agent/skill/本体/数据均回溯前序）/ 层级一致（四层自下而上连贯）/ 非硬编码行业模板 / PPT 就绪（四层+三框+左右标签可绘、直角框）。
- [ ] 6. 渲染输出 + 写 yaml。
```

> 数据缺口、内部状态字段只留在过程文件，**绝不进 PPT**。

---

## 用户检查点 ★（本步骤结束前的必须动作）

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

在输出技术架构后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）。停止时按 STOP 模板抛出以下确认话术：

> "这是支撑价值兑现的 AI 技术架构（四层）。请确认：
> 1. 最底层数据来源是否覆盖贵司关键业务数据、且都可获得？
> 2. 存在论/认识论/实践论三类本体对象是否贴合贵司业务？
> 3. 顶层 agent（行动主体）是否对应本次最关键的 AI 场景与决策？
>
> 确认后我们将进入步骤 11（实施路径）。"

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 6 步，过校验闸门，写 yaml + md，呈现检查点。
- **多 agent（探测到能力时）**：PL 派一个「Architecture Expert」按四层从前序产物构建 ontology；Partner 用可溯源 + 层级一致 + 非硬编码 + PPT 就绪闸门复核。协调统一经 PL（hub-and-spoke）。

## 与上下游的衔接

- **上游**：步 01 数据来源/缺口；步 03 价值方向/影响因子；步 08 关键 AI 场景与闭环；步 09 关键指标/单位/基准。
- **下游**：步 11 **实施路径**把本步的 **agent / agent skill / 数据接入** 作为可被排入四阶段建设波次的"建设对象"。
<!-- @AI_GENERATED: end -->

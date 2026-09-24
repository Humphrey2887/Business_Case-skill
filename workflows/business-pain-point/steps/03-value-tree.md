<!-- @AI_GENERATED -->
# 步骤 03 · Value Tree 价值树拆解（端到端价值链）

承接步骤 02 用户确认的**价值方向**与**关键经营命题**，把价值树拆成可直接服务 Business Case 与 PPT 的**端到端价值链**，从左到右 8 层：

综合目标 → 成本/收益类型 → 价值方向 → 关键抓手 → 影响因子 → 痛点分析 → 痛点权重 → AI 场景。

判定标准（端到端结构、方向驱动、MECE 按案例选口径、价值方向运算符、影响因子单位、痛点与痛点权重、AI 场景、闸门、与下游边界、示例与模板）见 [../standards/03-value-tree-guide.md](../standards/03-value-tree-guide.md)。本文件说明工作流执行步骤。

---

## 输入

- `process/02-critical-mission.yaml`（步 2 产出），**必须读取**：
  - `confirmed_customer_mission.mission_critical`（命题，作树根）+ `primary_kpi` + `key_levers`
  - `confirmed_customer_mission.value_direction`（cost_down / revenue_up / both）
  - `downstream_contract.value_tree_mode`（single_cost_tree / single_revenue_tree / cost_and_revenue_trees）
  - `downstream_contract.tree_calibers_required`（须建哪些口径的树）
  - `downstream_contract.must_use_process_hotspots` / `must_use_data_ledger_metrics`（须承接的流程热点与数据指标）
- `process/01-research.yaml`（行业研究、客户流程成本/收益拆分、数据台账——用于选分类口径与影响因子单位）
- 客户背景与行业基本信息

## 输出

- `process/03-value-tree.yaml` — 端到端价值链结构化数据（综合目标 / 成本收益类型 / 价值方向 / 关键抓手 / 影响因子(带单位) / 痛点 / 痛点权重 / AI 场景；按方向 1-2 棵树），供下游读取（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `03-value-tree.md` — 可读文档，使用 guide 第 11 节输出模板

> 边界提示：本步影响因子**必须带单位**；其 `baseline / data_source` 由第 4 步校验补齐。本步建立"目标 → AI 场景"完整链路初版，场景机制由第 8 步深化（回写 `scenario_id`）。

## 执行流程

按 guide 推进：

```
Task Progress:
- [ ] 1. 输入读取与建树模式：读步 02 的 confirmed_customer_mission 与 downstream_contract。**按 value_tree_mode 决定建几棵树**：single_cost_tree→仅成本树（cost_saving）；single_revenue_tree→仅收益树（revenue_uplift）；cost_and_revenue_trees→成本树+收益树两棵，分离不混用。未确认方向则回退步 02。
- [ ] 2. 一级分类口径：每棵树选 classification_basis（按案例定，不写死），写 classification_rationale，确保同层单一口径、MECE、不混主题/科目（no_mixed_basis）。
- [ ] 3. 价值方向拆解：把成本/收益类型拆成带运算符（+/-/×/÷）的 value_directions，解释如何构成上层，能下钻到关键抓手。
- [ ] 4. 关键抓手：列能影响价值方向的业务抓手（动作方向，不一定是指标）。
- [ ] 5. 影响因子（带单位）：定位可量化/采集/干预的数据指标，**每个必须附 unit**；单位不确定填"待确认"+data_gap；无单位不得入树。
- [ ] 6. 痛点分析（全局唯一）：在每棵树的 `pain_library` 里定义痛点（一条一个 id + 中文名 + 根因句式），影响因子用 `pain_contributions.pain_ref` 按「代号（中文名）」引用，不重复写正文；一条痛点可被多个影响因子引用。
- [ ] 7. 痛点权重：为每条引用估算该痛点对**本影响因子**变动的根因贡献，标 weight_basis；**同一影响因子下 pain_contributions 权重合计=100%**（非 Step 06 优先级评分）。
- [ ] 8. AI 场景：为痛点配 AI 场景（数据→识别→预测/优化/推荐→闭环），原则一因子一场景，合并写 merge_reason；给 scenario_id 供步 08 回写。
- [ ] 9. ⛔ 闸门校验：方向匹配 / 口径单一 / 分类依据 / MECE / 价值方向运算符 / 影响因子单位 / 每因子挂痛点 / 痛点权重合计100% / AI 场景（见 guide 第 9 节）。
- [ ] 10. 渲染输出：生成 Markdown 端到端价值链（含成本树/收益树）+ 写 yaml。
```

### 闸门：端到端价值链底线（不通过则重拆）

参见 guide 第 9 节九道闸门。重点：

0. **方向匹配 + 口径单一**：树数量与 `value_tree_mode` 一致；`both` 必须成本树 + 收益树分离，每棵 `tree_type` 单一、不混成本与收益。
1. **分类口径按案例 + 不混口径**：每棵树写明 `classification_basis` 与 `rationale`，同层不混"主题口径"与"财务科目口径"，父子关系严格成立。
2. **价值方向带运算符**：`operator_logic` 必须含 +/-/×/÷，不能只写动作词。
3. **影响因子带单位**：无单位不得入树（缺则"待确认"+`data_gap`）。
4. **每因子挂痛点 + 权重合计 100%**：同一影响因子下痛点权重加总必须 = 100%。
5. **AI 场景非泛动作**：场景必须是 AI 技术方案，说明数据/识别/预测优化/闭环。

## 用户检查点 ★

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

将生成的端到端价值链（成本树 / 收益树）呈现给用户后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）。停止时按 STOP 模板抛出以下确认话术：

> "这是基于您选定方向拆解的端到端价值链：从综合目标一直拆到影响因子、痛点权重与 AI 场景。请确认：
> 1. 一级分类口径是否贴合贵司管理/财务口径？
> 2. 影响因子及其单位是否准确、可采集？
> 3. 各影响因子下的痛点与权重（根因贡献）是否符合实际？
> 确认后，我们将进入步骤 04（影响因子单位/基线/数据源校验）。"

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 10 步，过九道闸门，写 yaml + md，呈现检查点。
- **多 agent（探测到能力时）**：PL 派一个「Value Tree Expert」按 guide 拆端到端价值链；Partner 用九道闸门复核（重点查：口径是否单一不混、价值方向是否带运算符、影响因子是否带单位、痛点权重是否合计 100%、场景是否真 AI 场景）。协调统一经 PL（hub-and-spoke），不依赖队友互发消息。

## 与上下游的衔接

- 上游：步 2 的 `confirmed_customer_mission` 提供综合目标（命题）、主 KPI / 关键抓手，并由 `downstream_contract.value_tree_mode` / `tree_calibers_required` **直接决定本步建几棵树、各树口径**；步 1 的行业研究 / 流程成本收益拆分 / 数据台账支撑分类口径与影响因子单位。
- 下游：
  - 步 4「影响因子数据就绪校验」**校验并补充**影响因子的单位、baseline、数据源。
  - 步 5「痛点业务化精修」深化痛点业务化（避免"缺系统/缺平台"）。
  - 步 6「痛点评分」做**业务优先级评分**——与本步**痛点权重（根因贡献）不同，不可混用**。
  - 步 8「关键场景」深化 AI 场景机制、数据输入输出与业务闭环，并**回写本步 `scenario_id`**。
  - 步 9「价值量化」基于本步价值方向与场景测算价值。
<!-- @AI_GENERATED: end -->

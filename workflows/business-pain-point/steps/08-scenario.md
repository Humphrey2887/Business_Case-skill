# 步骤 08 · 关键场景识别与筛选

承接步骤 07 的大痛点与**步骤 03 已起草的 AI 场景**，本步骤深化场景机制并经**现实可行性筛选**，产出关键场景组合 + 被排除场景及原因，并**回写 03 的 `scenario_id`**。关键场景不能只靠理论价值推导，必须能落地。

判定标准（定义、识别流程、5 道筛选门槛、7 条成立条件、数量原则、示例与模板）见 [../standards/08-scenario-guide.md](../standards/08-scenario-guide.md)。本文件只讲「在工作流里怎么执行这一步」。

---

## 输入

- `process/03-value-tree.yaml`（步 3 已起草的 AI 场景 `scenarios`，含 `scenario_id` / `ai_mechanism` 初稿；本步深化并回写同一 id）
- `process/07-pain-cluster.yaml`（步 7 大痛点 `big_pains`，为场景组织起点）
- 经 `member_pains` 回溯 03 `pain_library` / `06-pain-scoring.yaml` / `04-kpi-factor.yaml`，取核心痛点与影响因子（按「代号（中文名）」引用）
- `--length`（决定关键场景数量目标：3min→3-4 / 5min→5-6 / 10min→6-8）

## 输出

- `process/08-scenario.yaml` — 结构化场景组合 + 被排除场景（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `08-scenario.md` — 可读文档，使用 guide 第 7 节输出模板

每个关键场景需带：`id`（沿用 03 scenario_id）、`from_value_tree`、`name`、`linked_big_pain`、`linked_pains`（代号（中文名））、`impact_factors`、`ai_mechanism`、`business_action`、`closed_loop`（业务动作闭环节点）、`feasibility`（5 维）、`value_status`（ready / to_verify）。

## 执行流程与可行性筛选闸门

Agent 必须严格按顺序执行（对齐 guide 第 2 节识别流程）：

```
Task Progress:
- [ ] 1. 读取大痛点与 03 场景：取步骤 07 的 big_pains，并读 03 已起草的场景（scenario_id / ai_mechanism）；经 member_pains 回溯各核心痛点（代号（中文名））的影响因子。
- [ ] 2. 痛点-KPI-影响因子映射：在每个大痛点下，沿核心痛点→KPI→影响因子铺开。
- [ ] 3. 生成场景机会池：围绕每个影响因子提出"可执行业务动作改善KPI"的候选场景。
- [ ] 4. ⛔ 可行性筛选 (Gate)：逐条过 5 门槛——客户可控性 / 数据可得性 / 优化空间 / 业务闭环 / 价值可量化；不通过按表处理（排除 / 降级背景约束 / 改前置条件 / 作辅助能力 / 标注待验证）。
- [ ] 5. 排除与保留说明：记录每个被排除/降级场景的原因与方法论归类。
- [ ] 6. 合并与命名：相近场景合并，按"AI 场景"命名（落到 AI 解决方案，非系统名、非泛业务动作）；**沿用并回写 03 的 scenario_id**，03 未覆盖的新增场景标 from_value_tree: false。
- [ ] 7. 确定关键场景组合：按 --length 目标数量收敛，渲染输出 + 写 yaml。
```

> 数量目标：按 `--length` 取 3-4 / 5-6 / 6-8；若可行场景不足目标下限，如实说明（不硬凑），并把潜力场景标 `to_verify`。

---

<!-- @AI_GENERATED -->
## 用户检查点 ★ (本步骤结束前的必须动作)

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

在输出关键场景组合 + 被排除场景后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）。停止时按 STOP 模板抛出以下确认话术：
<!-- @AI_GENERATED: end -->


> “这是为各大痛点识别并经可行性筛选后保留的关键场景组合，以及被排除/降级的场景及原因。请您确认：
> 1. 保留的场景是否都在贵司‘可控、数据可得、有优化空间’范围内、且有明确可执行业务动作？
> 2. 被排除/降级的判断是否符合实际（有没有该捞回或该再砍的）？
>
> 确认无误后，我们将进入步骤 09（价值量化）。”

**注意**：在用户明确回复“确认”或给出修改意见之前，流程强制暂停，不允许自行进入下一步。

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 7 步，过 5 门槛筛选，写 yaml + md，呈现检查点。
- **多 agent（探测到能力时）**：PL 派一个「Scenario Expert」铺场景机会池并按可行性筛选；Partner 复核门槛（重点抓"客户可控性""数据可得性"是否被高估、是否出现纯系统场景）。协调统一经 PL（hub-and-spoke），不依赖队友互发消息。

## 与上下游的衔接

- **上游**：步 07 提供大痛点主叙事（及其核心痛点、KPI、影响因子的回溯链）。
- **下游**：步 09 **价值量化**——对本步保留的关键场景建立 baseline 与收益测算，把 `value_status: to_verify` 的场景补齐量化。（注：实施路径在第 10 步。）

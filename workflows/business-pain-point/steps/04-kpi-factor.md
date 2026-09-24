<!-- @AI_GENERATED -->
# 步骤 04 · 影响因子数据就绪校验

承接步骤 03 端到端价值树里已带单位的「影响因子」，本步**不新造 KPI/因子、不碰痛点**，核心任务是把影响因子"**上秤**"：敲定单位、补齐当前基线与数据来源，过可测量 + 因果直接性双闸门，并标出可纳入第 9 步重点测算的子集。

判定标准（定义、上秤规范、校验闸门、输出模板）见 [../standards/04-kpi-factor-guide.md](../standards/04-kpi-factor-guide.md)。

---

## 输入

- `process/03-value-tree.yaml`（步 3 价值树的 `impact_factors`，含 `factor` / `unit` / `data_source` / `data_gap`）
- `process/01-research.yaml`（数据台账 `data_ledger`，用于核对口径与基线来源）
- 客户背景 / 历史数据 / 内部口径（如有）

## 输出

- `process/04-kpi-factor.yaml` — 影响因子数据就绪清单（`impact_factor_readiness`），供下游读取（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `04-kpi-factor.md` — 可读文档，使用 guide 第 6 节输出模板

每个影响因子需带：`from_value_tree`（路径）、`outcome_type`、`unit`、`baseline`(或"待调研")、`data_source`、`proxy`(战略/定性类)、`measurable`、`causal_directness`、`quantify_priority`。

## 执行流程与强管控闸门

```
Task Progress:
- [ ] 1. 读取影响因子：遍历步骤 03 各树的 impact_factors（已带 unit）。
- [ ] 2. 敲定单位：03 中 unit=待确认 的在此敲定；仍无法确定则转入 data_gaps。
- [ ] 3. 上秤补齐：为每个影响因子补【当前基线(或"待调研") + 数据来源】；战略/定性因子用 proxy 上秤（含单位/基线/数据源）。
- [ ] 4. 可量化标记：标 measurable 与 quantify_priority(high/mid/low)，圈出可纳入第 9 步重点测算的子集（可选聚焦核心因子，不撒胡椒面）。
- [ ] 5. ⛔ 可测量性拦截 (Gate 1)：影响因子或其 proxy 指不出具体系统/台账 → 打回或转 data_gaps。
- [ ] 6. ⛔ 因果直接性拦截 (Gate 2)：影响因子若无法通过调整系统参数/业务动作直接改变其价值方向 → 打回（回到 03 重拆）。
- [ ] 7. 渲染输出：生成 Markdown 清单 + 写 yaml。
```

> 本步**不处理痛点**：痛点在 03 `pain_library` 定义、05 业务化精修、06 优先级评分。本步只管影响因子的"数据就绪"。

---

## 用户检查点 ★ (本步骤结束前的必须动作)

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

在完成校验并生成清单后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）。停止时按 STOP 模板抛出以下确认话术：

> "这是价值树底层影响因子的数据就绪校验。请确认：
> 1. 这些影响因子目前在贵司是否有对应数据源（系统/台账）可追踪？
> 2. 标注的基线是否可取得、口径是否一致？
>
> 确认无误后，我们将进入步骤 05（痛点业务化精修）。"

**注意**：用户明确"确认"或给修改意见前，流程强制暂停，不允许自行进入下一步。

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 7 步，过双闸门，写 yaml + md，呈现检查点。
- **多 agent（探测到能力时）**：PL 派一个「Data Readiness Expert」对影响因子上秤；Partner 用可测量性 + 因果直接性双闸门复核。协调统一经 PL（hub-and-spoke）。

## 与上下游的衔接

- **上游**：步 03 提供端到端价值树（含带单位的影响因子）；步 01 数据台账提供口径与基线来源。
- **下游**：
  - 步 05「痛点业务化精修」对 03 `pain_library` 的痛点做业务化校验（与本步并行，本步不产痛点）。
  - 步 09「价值量化」按本步 `impact_factor_readiness` 的 `baseline` / `data_source` / `quantify_priority` 取数测算。
<!-- @AI_GENERATED: end -->

# 步骤 09 · 价值量化

承接步骤 08 保留的关键场景，本步骤沿 Value Tree 对每个场景建立收益测算逻辑，给出关键假设与待确认数据。严格区分"出金额"（baseline 已存在）与"只出框架"（baseline 待建），并按 ready / to_verify 做汇总分账，不编数、不用类比承诺。

判定标准（定义、两条通用公式、量化逻辑示例库、数据使用规则、value_status 绑定与回填升级、汇总规则、深度档位、输出模板）见 [../standards/09-valuation-guide.md](../standards/09-valuation-guide.md)。本文件只讲「在工作流里怎么执行这一步」。

---

## 输入

- `process/08-scenario.yaml`（步 8 保留场景 `scenarios`，含 `impact_factors` / `ai_mechanism` / `closed_loop` / `value_status`）
- 经 `impact_factors` 回溯 `04-kpi-factor.yaml` 的 `impact_factor_readiness`，取每个影响因子的 `baseline` / `unit` / `data_source`
- 参 `03-value-tree.yaml` 确认 价值方向 → 影响因子 的传导，选对公式
- `--length`（决定测算深度：3min 粗区间 / 5min 区间+主敏感度 / 10min 区间+敏感度+情景上下限）

## 输出

- `process/09-valuation.yaml` — 逐场景**两段式**测算 + 汇总分账（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `09-valuation.md` — 可读文档，使用 guide 第 8 节输出模板

每个场景测算需带：**段一**（`caliber`/`unit`/`scope`/`period`、`baseline` + `baseline_tier` + 来源、`assumptions` 每条标 `data_type`）+ **段二**（`ai_mechanism`、`closed_loop`、`key_indicators`（带单位）、`formula`、`estimated_value`）+ `value_status` / `result_type` / `content_completeness` / `to_confirm` / `counts_in_rollup`。

## 执行流程与数据诚实闸门

Agent 必须严格按顺序执行（对齐 guide 第 2/4b/4c/5/6 节）：

```
Task Progress:
- [ ] 1. 读取场景：取步骤 08 的 scenarios 及其 value_status / impact_factors / ai_mechanism / closed_loop。
- [ ] 2. 回溯 Baseline + 定基准档位：经 impact_factors 回 04 impact_factor_readiness 取 baseline / unit / data_source；按 **企业基准(enterprise) > 行业基准(industry) > 显式假设(assumption)** 取数并标 baseline_tier；缺企业基准记为待确认。
- [ ] 3. 选公式：逐场景在两条通用公式中择一（Baseline×可改善×可兑现 或 业务量×单位价差/成本差×捕捉率）。
- [ ] 4. 组织两段式内容：段一=假设/基准/口径（caliber/unit/scope/period）；段二=机制(ai_mechanism)/闭环(closed_loop)/关键指标及单位(key_indicators)/价值提升测算。
- [ ] 5. 列关键假设：每个参数给取值并标 data_type（client_real / industry_public / internal_assumption / analogy）+ 来源/口径。
- [ ] 6. ⛔ 数据诚实 + 基准优先闸门 (Gate)：value_status=ready → 出收益区间(quantified) + 两段齐全；to_verify 或缺企业 baseline → 只出框架(framework_only)、至少段一+机制、列 to_confirm；有企业基准必须用企业基准，用行业/假设档须标 baseline_tier 与"参考同业/基于假设"；类比不承诺；不擅自给 to_verify 填 baseline。
- [ ] 7. 汇总分账：ready/quantified 场景区间加总为 Business Case 总价值；to_verify/framework 列入潜在价值池，不计入总额。
- [ ] 8. 写 yaml + md，输出待确认数据清单（缺哪条 baseline/参数、属哪个场景、回填即可量化）。
```

> 深度按 `--length`：3min 给粗区间；5min 给区间 + 标出最敏感假设；10min 给区间 + 敏感度 + 保守/中性/乐观情景。

---

<!-- @AI_GENERATED -->
## 用户检查点 ★ (本步骤结束前的必须动作，含数据回填)

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

完成本步产物落盘并输出摘要后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）；停止时按 STOP 模板抛出以下确认话术，并**逐条索要待确认数据**：
<!-- @AI_GENERATED: end -->


> "这是各关键场景的价值测算逻辑、关键假设与汇总。其中 [N] 个场景因缺 baseline/关键参数，目前只给了测算框架、进入潜在价值池。请您确认：
> 1. 各场景的测算公式与关键假设（尤其标了'内部假设'的可改善比例/可兑现比例/捕捉率）是否合理、是否偏乐观？
> 2. 以下待确认数据能否回填？回填后我会把对应场景升级为可量化并计入总价值：
>    - [SC-x] 缺 [baseline/参数]（来源建议：[第4步数据源]）
>    - [SC-y] 缺 [baseline/参数]
>
> 您回填的，我立即重算并入总额；暂时无法提供的保留在潜在价值池。确认后我们将进入步骤 10（技术架构 / Ontology）。"

**回填处理**：用户回填某场景的 baseline/参数后，将其 `value_status` 改 `ready`、`result_type` 改 `quantified`、重算 `estimated_value`、`counts_in_rollup` 改 `true`，并更新 `rollup`（从 `potential_pool` 移入 `business_case_value`）。

**注意**：模式为"主动索要但不阻断"——用户可选择不回填，流程不强制暂停在数据收集上；但在用户明确回复"确认"或给出修改/回填之前，不允许自行进入下一步。

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 7 步，过数据诚实闸门，写 yaml + md，呈现检查点并索要待确认数据。
- **多 agent（探测到能力时）**：PL 派一个「Quant Expert」按公式建模、列假设与区间；Partner 复核（重点抓"假设是否过度乐观""是否把 to_verify 当 ready 出了金额""是否拿类比案例承诺收益""汇总是否只加了 ready"）。协调统一经 PL（hub-and-spoke），不依赖队友互发消息。

## 与上下游的衔接

- **上游**：步 08 提供保留场景及其 `ai_mechanism` / `closed_loop` / `value_status`；步 04 提供影响因子 baseline / 数据源；步 03 提供 价值方向→影响因子 传导。
<!-- @AI_GENERATED -->
- **下游**：步 10 **技术架构（Ontology）**——把本步量化的价值场景翻译成四层 AI 技术架构（数据来源 → 本体三框 → Agent Skill → Agent 行动主体），再由步 11 **实施路径**按价值量级与可行性把 agent/skill/数据接入排布建设波次（quick win 先行）。
<!-- @AI_GENERATED: end -->

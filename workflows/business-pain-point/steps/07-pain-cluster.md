# 步骤 07 · 大痛点组合

承接步骤 06 的核心痛点池，本步骤把核心痛点**按经营逻辑聚合为 2-3 个「大痛点」**，形成 Business Case 的痛点主叙事——把零散痛点收敛成少数几条能打动决策层、且挂得上价值的主线。

判定标准（定义、组合规则、校验闸门、示例与模板）见 [../standards/07-pain-cluster-guide.md](../standards/07-pain-cluster-guide.md)。本文件只讲「在工作流里怎么执行这一步」。

---

## 输入

- `process/06-pain-scoring.yaml`（步 6 的 `core_pain_pool`：`tier: core` 为组合对象；`tier: strategic_background` 仅供附录）

## 输出

- `process/07-pain-cluster.yaml` — 结构化大痛点（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `07-pain-cluster.md` — 可读文档，使用 guide 第 6 节输出模板（主叙事 + 附录）

每个大痛点需带：`name`（一句话经营问题+价值空间）、`member_pains`（归属核心痛点，按「代号（中文名）」引用 03 pain_library）、`supporting_factors`、`value_contribution`。

## 执行流程与校验闸门

Agent 必须严格按顺序执行以下 6 步：

```
Task Progress:
- [ ] 1. 读取核心池：取步骤 06 中 tier=core 的核心痛点（按「代号（中文名）」引用，含 priority_score / business_context）。
- [ ] 2. 经营逻辑聚类：按"同一经营问题/价值链环节"把核心痛点聚成 2-3 个大痛点（不按技术模块）。
- [ ] 3. 绑定支撑：为每个大痛点写明 归属核心痛点（代号（中文名））+ 支撑影响因子 + 价值贡献。
- [ ] 4. ⛔ 校验闸门 (Gate)：经营问题导向（非技术模块、无"缺XX系统"）；可回溯（每个大痛点≥1核心痛点+KPI）；服务决策（能引出投入取舍）。任一不过则重组。
- [ ] 5. 附录归集：把 tier=strategic_background 的痛点写入"附录·长期战略议题"，注明升入主叙事的触发条件，不进主叙事。
- [ ] 6. 渲染输出：生成主叙事 + 附录 Markdown，并写 yaml。
```

---

<!-- @AI_GENERATED -->
## 用户检查点 ★ (本步骤结束前的必须动作)

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

在输出大痛点主叙事后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）。停止时按 STOP 模板抛出以下确认话术：
<!-- @AI_GENERATED: end -->


> “这是为 Business Case 收敛出的 2-3 个大痛点主叙事。请您确认：
> 1. 这几个大痛点是否就是站在贵司经营决策视角、最该下决心解决的几件大事？
> 2. 是否按‘经营问题’而非‘技术模块’组合，且每个都挂得上 KPI 与价值？
>
> 如需调整组合方式请指出；确认无误后，我们将进入步骤 08（关键场景识别与筛选）。”

**注意**：在用户明确回复“确认”或给出修改意见之前，流程强制暂停，不允许自行进入下一步。

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 6 步，过校验闸门，写 yaml + md，呈现检查点。
- **多 agent（探测到能力时）**：PL 派一个「Business Case Architect」按经营逻辑聚类并撰写主叙事；Partner 复核闸门（重点抓"是否按技术模块切分""是否挂得上 KPI/价值"）。协调统一经 PL（hub-and-spoke），不依赖队友互发消息。

## 与上下游的衔接

- **上游**：步 06 提供经评分与硬门槛锁定的核心痛点池（及降级的战略/背景痛点）。
- **下游**：步 08 **关键场景识别与筛选**——在每个大痛点下识别并筛选可落地的关键场景（大痛点不限制后续场景数量）。（注：价值量化在第 9 步、实施路径在第 10 步。）

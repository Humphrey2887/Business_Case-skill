<!-- @AI_GENERATED -->
# 步骤 02 · Critical Mission 判断（Mission Critical，v1.8）

本步做**两层判断**：

- **第一层 · 价值方向**：基于 Step 01 的行业普遍 MC、客户流程成本/收益拆分与数据台账，判断本次 Business Case 该**降本（cost_down）/ 增收（revenue_up）/ 降本增收都要（both）**，并请用户确认方向。
- **第二层 · 客户 Mission Critical**：在用户选定方向下，确认客户「当前必须优先解决、且足以支撑 Business Case 的上位使命 / 核心约束 / 关键业务命题」，产出**按方向分桶的候选 + 对比 + AI 推荐 + 最终确认**，并写明驱动 Step 03 价值树结构的下游契约。

核心逻辑：

```
Step 01 输出：行业普遍 MC + 客户流程成本/收益拆分 + 数据台账
        ↓
Step 02 判断：客户该降本、增收，还是两者都要
        ↓
用户选择：cost_down / revenue_up / both
        ↓
Step 03 价值树：按选择生成成本树、收益树，或成本+收益两棵树
```

判定标准（核心定义、硬规则、材料使用规则、从大到小表达、候选/对比/推荐模板、能碳规则、不得推荐规则、Step 01 输入使用、行业-客户对齐、流程经济性诊断、方向选择、方向驱动价值树、输出模板）见 [../standards/02-critical-mission-guide.md](../standards/02-critical-mission-guide.md)。本文件只讲「在工作流里怎么执行这一步」。

---

## 输入

- 用户提供的客户背景 / 项目 brief（必需）
- `process/01-research.yaml`（步 1 结构化调研产出，**v1.8 要求必须先 Research 再判断**），**必须读取**：
  - `industry_common_mission_critical` —— 行业普遍 MC（判断行业普遍压力）
  - `business_process_economics` —— 客户流程成本/收益拆分（判断客户自身经济性热点）
  - `data_ledger` —— 数据台账（判断数据可信度、口径）
  - `research_synthesis.initial_client_mc_options` —— Step 01 给出的客户 MC 初步方向候选
  - `company_research` / `industry_research` —— 公司本体与行业研究底料
- 客户所在行业 / 公司本体信息（**强制前置，见下**）
- 用户上传的材料 / 方案 / 产品介绍（**仅作 Research 输入与场景证据，不得直接当 Mission Critical**）

## 输出

- `process/02-critical-mission.yaml` — 结构化结果（含行业-客户对齐、流程经济性诊断、价值方向诊断、按方向分桶候选、用户方向选择、最终客户命题、下游契约），供下游读取（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `02-critical-mission.md` — 可读文档，使用 guide 第 13 节最终输出模板

关键产出：`industry_client_mc_alignment`、`process_economics_diagnosis`、`value_direction_diagnosis`（含 AI 推荐方向）、`candidate_groups`（cost_down / revenue_up / both 分桶）、`user_value_direction_choice`（用户选择）、`confirmed_customer_mission`（含 `value_direction`）、`downstream_contract`（驱动 Step 03）。

## 强制前置（开跑前必须做）

v1.8 硬规则 1/2 要求：**先 Research，再判断；先判断客户公司本体，再判断上传材料中的项目场景。**因此本步执行前必须先确认：

1. 分析对象是哪个客户 / 哪个行业？客户**公司本体**是什么（组织类型、核心职责、价值逻辑）？
2. 该客户靠什么创造价值？（靠什么赚钱 / 最大成本项 / 核心资产 / 最稀缺资源 / 最影响经营的运营瓶颈 / 外部政策市场是否在放大问题）
3. 用户是否上传了材料？若有，**先归位**（公司战略 / 业务线 / 项目方案 / 产品系统），明确它在公司级命题中的分支位置——**不得被材料牵引**直接立题。

若行业 / 公司本体信息或 Step 01 关键输入缺失，先向用户提问补齐或在 `data_gaps` 标注，再进入分析。

## 执行流程

```
Task Progress:
- [ ] 1. 读取 Step 01：行业普遍 MC、客户流程成本/收益拆分、data ledger、客户 MC 初步选项、公司/行业研究。
- [ ] 2. 行业-客户对齐：判断客户 MC 与行业普遍 MC 是一致 / 偏离 / 更聚焦 / 数据不足（写 industry_client_mc_alignment）。
- [ ] 3. 流程经济性诊断：从 business_process_economics 识别成本热点、收益热点、资产/风险热点（写 process_economics_diagnosis，每条带证据与数据可信度）。
- [ ] 4. 价值方向判断：判断本次 Business Case 更适合降本、增收，还是两者都要，给 AI 推荐方向 + caveat（写 value_direction_diagnosis）。
- [ ] 5. 候选分桶：按 cost_down / revenue_up / both 生成客户 MC 候选，每个候选标明来源流程热点、与行业 MC 关系、价值树含义（写 candidate_groups）；候选中仍须含 ≥1 能碳相关 Option（默认不推荐，除非满足 guide 第7节 5 条件）。
- [ ] 6. ⛔ 用户选择点（第一层）：请用户确认 降本 / 增收 / 降本增收都要（写 user_value_direction_choice）。AI 可推荐但不得替用户选择。
- [ ] 7. 最终 MC 确认（第二层）：在用户选定方向下确认 Mission Critical、主 KPI、关键抓手；过"从大到小表达"与"不得推荐"校验；建立项目→公司级命题连接链（guide 第12节）。
- [ ] 8. 下游契约：写 downstream_contract，明确 Step 03 应生成成本树、收益树，还是成本+收益两棵树，以及必须用到的流程热点与数据台账指标。
```

### 闸门 0：关键问题锚定到公司级命题（不通过则重定位）

Mission Critical 必须锚定**高管最心急的公司级命题**（最大成本项/周期性生存压力/核心约束），**而非我们项目本身的主题**（guide 第12节）。若把项目主题（如"零碳园区""某平台"）直接当公司级命题，打回——改为公司级命题 + 用连接链论证项目如何改善它。

### 闸门 1：从大到小表达（不通过则改写）

每个候选必须先表达上位使命，再表达关键抓手 / 主 KPI（guide 第4节）。把抓手或 KPI 放在前面的，打回改写。

### 闸门 2：不得推荐校验（不通过则不能作为推荐项）

推荐项不得是：上传材料项目主题 / 纯 KPI / 技术系统平台产品 / 单一抓手 / 未说明为何必须优先 / 无法拆 Value Tree / 缺可量化主 KPI / 能碳 Option 仅因材料出现被强推（guide 第10节）。**此外**：不得脱离 Step 01 行业 MC 与流程经济性数据凭空生成客户 MC（guide 第14/16节）。

### 闸门 3：能碳 Option 必含但不默认推荐

候选中必须包含 ≥1 个能碳相关 Option；它只有在满足 guide 第7节 5 条件时才可被推荐，否则定位为分支 / 业务线级 / 项目级 / 解决方案场景。

### 闸门 4：价值方向先于命题锁定（不通过则不进 Step 03）

**用户未确认价值方向（cost_down / revenue_up / both）前，不得锁死最终 MC、不得写 downstream_contract、不得进入 Step 03**（guide 第17节）。用户选 `both` 时，下游契约必须为 `cost_and_revenue_trees`，不得把成本与收益混进一棵树/一个等式（guide 第18节）。

## 用户检查点 ★（两段式）

> ⛔ 硬闸门：本步含检查点 A 与检查点 B 两个检查点，二者均为交付红线级约束。执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过授权 / 过程信息通道边界）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。每个检查点在产物落盘并输出摘要后，执行体**必须停止、等待用户确认，未获用户确认不得写入下一步文件**；严禁自问自答代替用户确认。

**检查点 A · 价值方向选择（先问，强制）**：完成本层产物落盘并输出摘要后，执行体**必须停止并等待用户确认，未获用户确认不得进入检查点 B、不得写下一步文件**。把「Research 摘要 + 行业-客户对齐 + 流程经济性诊断（成本/收益/资产风险热点）+ AI 推荐方向及理由」呈现给用户，并按 STOP 模板提问：

> "基于行业普遍 Mission Critical 与您的业务流程成本/收益拆分，本次 Business Case 有三种方向：
> 1. **降本**：围绕成本热点建立成本节约型价值树。
> 2. **增收**：围绕收入/价格/销量/转化建立收益提升型价值树。
> 3. **降本增收都要**：分别建立成本树与收益树，后续价值树拆成两棵。
> 我的建议是【AI 推荐方向 + 理由 + caveat】。请确认本次选择哪一种方向？"

收到用户确认（恢复口令）后，方可写入 `user_value_direction_choice`（`selected_direction` + `implication_for_value_tree`）。

**检查点 B · 最终 Mission Critical 确认**：完成本步产物落盘并输出摘要后，执行体**必须停止并等待用户确认，未获用户确认不得写下一步文件、不得进入步骤 03**。在所选方向的候选桶里，把「≥3 候选（含能碳 Option）+ 对比表 + AI 推荐项 + 项目→公司级命题连接链 + 8 条推荐理由」呈现给用户。**v1.8：最终 Mission Critical 由业务负责人结合客户判断确认**。收到用户确认（恢复口令）后，方可写 `confirmed_customer_mission`（含 `value_direction`）与 `downstream_contract`，才进入步骤 03。

> 优先级：用户选择高于 AI 推荐。若用户方向选择与 AI 推荐不同，保留 AI 的 caveat，但一律按用户选择驱动下游。

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 读 Step 01 → 行业-客户对齐 → 流程经济性诊断 → 方向判断 → 候选分桶 → 检查点 A 取方向 → 选定方向下确认 MC 与连接链 → 过五闸门 → 写 downstream_contract → 写 yaml + md → 检查点 B。
- **多 agent（探测到能力时）**：PL 派一个「行业/使命 Expert」做行业-客户对齐、流程经济性诊断、方向诊断与按方向分桶候选；Partner 用公司级锚定 + 从大到小 + 不得推荐 + 能碳条件 + 方向先于命题 五闸门复核。协调统一经 PL（hub-and-spoke），不依赖队友互发消息。

## 与上下游的衔接

- 上游：步 1 结构化调研提供行业普遍 MC、客户流程成本/收益拆分、数据台账、客户 MC 初步候选与公司/行业研究（v1.8 要求 Research 前置）。
- 下游：步 03 Value Tree **由本步 `downstream_contract` 直接驱动**：
  - 用户选 `cost_down` → 只生成成本价值树（`caliber: cost_saving`）。
  - 用户选 `revenue_up` → 只生成收益价值树（`caliber: revenue_uplift`）。
  - 用户选 `both` → 至少生成成本树 + 收益树两棵，分别 MECE、不混用。
  其 `confirmed_customer_mission.mission_critical`（上位使命）作树根、`primary_kpi` 作量化锚点、`key_levers` 作关键抓手候选；`downstream_contract.must_use_process_hotspots` / `must_use_data_ledger_metrics` 作为价值树与后续量化的锚点；上传材料按定位落到对应分支，作为后续场景/抓手证据，而非树根。
<!-- @AI_GENERATED: end -->

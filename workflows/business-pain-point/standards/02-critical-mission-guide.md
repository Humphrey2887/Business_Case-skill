<!-- @AI_GENERATED -->
# Mission Critical 判断标准（v1.8）

> 本文件是 `business-pain-point` 工作流第 2 步（Critical Mission 判断）的领域标准。
> 定义内容来自业务负责人提供的权威文档（Mission Critical Skill 规则 v1.8），逐字保留要点，仅做结构化编排。
> 执行说明见 [../steps/02-critical-mission.md](../steps/02-critical-mission.md)。

---

## 目录

- [1. 核心定义](#1-核心定义)
- [2. 硬规则](#2-硬规则)
- [3. 材料使用规则](#3-材料使用规则)
- [4. 从大到小表达规则](#4-从大到小表达规则)
- [5. Mission Critical 与 KPI 的分工](#5-mission-critical-与-kpi-的分工)
- [6. 候选项生成模板](#6-候选项生成模板)
- [7. 能碳 Option 规则](#7-能碳-option-规则)
- [8. 候选项对比表](#8-候选项对比表)
- [9. 推荐理由模板](#9-推荐理由模板)
- [10. 不得推荐规则](#10-不得推荐规则)
- [11. 牧原案例示例](#11-牧原案例示例)
- [12. 方案方视角：项目/产品/服务如何连接并改善公司级命题](#12-方案方视角项目产品服务如何连接并改善公司级命题)
- [13. 最终输出模板](#13-最终输出模板)
- [14. 新版 Step 01 输入使用规则](#14-新版-step-01-输入使用规则)
- [15. 行业 MC 与客户 MC 对齐规则](#15-行业-mc-与客户-mc-对齐规则)
- [16. 客户流程经济性诊断规则](#16-客户流程经济性诊断规则)
- [17. 降本/增收/两者都要选择规则](#17-降本增收两者都要选择规则)
- [18. 用户选择如何驱动 Value Tree](#18-用户选择如何驱动-value-tree)
- [19. 红线](#19-红线)

---

## 1. 核心定义

**Mission Critical** = 客户当前必须优先解决、且足以支撑 Business Case 的**上位使命、核心约束或关键业务命题**。

- **主 KPI / 核心约束指标** = Mission Critical 的量化锚点。
- **关键抓手** = 支撑 Mission Critical 改善的主要业务路径。

三者关系：

| 概念 | 回答的问题 |
| :-- | :-- |
| Mission Critical | 客户最必须解决的**上位问题** |
| 主 KPI | 衡量该问题是否被改善 |
| 关键抓手 | 推动该问题改善的**业务路径** |

示例：

- **Mission Critical**：提升穿越猪周期的盈利韧性
- **主 KPI**：周期底部利润率 / 生猪养殖完全成本
- **关键抓手**：降低生猪养殖完全成本

## 2. 硬规则

1. **必须先 Research，再判断。**
2. **必须先判断客户公司本体，再判断上传材料中的项目场景。**
3. 每次**至少输出 3 个候选 Mission Critical**，并**按价值方向分桶**（`cost_down` / `revenue_up` / `both`，见 §17/§18）。
4. 每个候选项**必须有主 KPI / 核心约束指标**。
5. 候选项中**必须包含至少 1 个能碳相关 Option**。
6. 推荐理由必须解释**为什么是该 Mission Critical**，而不是为什么是该 KPI。
7. Mission Critical 表达必须**从上位使命到关键抓手**，不能把抓手或 KPI 放在前面。
8. 最终 Mission Critical 由**业务负责人结合客户判断确认**。

### 步 01 输入接口（必读）

步 02 必须读取步骤 01 的以下产出作为判断依据：

- `industry_common_mission_critical`（行业普遍 Mission Critical）
- `business_process_economics`（客户业务流程成本/收益拆分）
- `data_ledger`（数据台账）
- `research_synthesis.initial_client_mc_options`（客户 MC 初步候选）

步 02 的**客户 Mission Critical 判断必须说明**：

1. 与**行业普遍 Mission Critical** 是一致、偏离还是更聚焦；
2. **客户流程成本/收益热点**支持降本、增收还是两者兼有；
3. 哪些判断受**数据缺口**影响。

> 接口预留：后续将在步 02 增加用户选择"降本 / 增收 / 降本增收都要"。本节先埋接口（`research_synthesis.initial_client_mc_options` 已按三方向给出候选），不要求一次性完成该交互。

## 3. 材料使用规则

用户上传的材料、方案页、项目规划、产品介绍、合作路线图，**只能作为 Research 输入和场景证据**。不得因为材料聚焦某个主题，就直接把该主题写成 Mission Critical。

- ❌ 错误逻辑：上传材料是零碳园区 → 所以 Mission Critical 是降低单位能碳成本。
- ✅ 正确逻辑：客户公司本体分析 → 判断公司级 Mission Critical → 拆解 Value Tree / Constraint Tree → 判断上传材料落在哪个分支 → 判断该材料是否支撑公司级 Business Case。

上传材料可能对应三种位置：

| 材料类型 | 在 Mission Critical 分析中的位置 |
| :-- | :-- |
| 公司战略材料 | 可能支撑公司级 Mission Critical |
| 业务线材料 | 可能支撑业务线级 Mission Critical |
| 项目 / 方案材料 | 通常只是某个分支下的场景或抓手 |
| 产品 / 系统材料 | 只能作为实现路径，不能直接成为 Mission Critical |

## 4. 从大到小表达规则

Mission Critical 必须**先表达上位使命，再表达关键抓手或主 KPI**。

推荐表达：

> 提升 / 保障 / 优化 / 降低 + **上位业务结果 / 核心约束**，核心抓手是 + **关键抓手 / 主 KPI**

或：

> 提升 / 保障 / 优化 + **上位业务结果**，降低 / 提升 + **关键抓手指标**

示例对比：

| 不推荐（抓手/KPI 在前） | 推荐（上位使命在前） |
| :-- | :-- |
| 降低生猪养殖完全成本，提升穿越猪周期的盈利韧性 | 提升穿越猪周期的盈利韧性，降低生猪养殖完全成本 |
| 降低畜牧园区单位能碳成本，打造零碳园区 | 提升畜牧园区低碳运营经济性，降低单位能碳成本 |
| 提升新能源消纳率，保障电网安全稳定运行 | 保障高比例新能源接入下的电网安全稳定运行，提升新能源消纳能力 |
| 提升公交班次兑现率，保障公共交通服务可靠性 | 提升公共交通服务可靠性，提升公交班次兑现率 |
| 降低绿氢单位成本，推动氢能商业化 | 推动绿氢商业化闭环，降低绿氢单位成本 |

## 5. Mission Critical 与 KPI 的分工

| 项目 | 回答的问题 | 示例 |
| :-- | :-- | :-- |
| Mission Critical | 客户最必须解决的上位问题是什么？ | 提升穿越猪周期的盈利韧性 |
| 主 KPI | 如何衡量这个问题是否改善？ | 周期底部利润率 / 生猪养殖完全成本 |
| 关键抓手 | 通过什么业务方向改善？ | 降低完全成本、提升屠宰利润、稳定出栏 |
| Value / Constraint Tree | 这个问题由哪些驱动构成？ | 饲料、健康、能碳、人工、资产利用 |
| 价值测算 | 改善后能产生多少价值？ | 出栏重量 × 成本下降幅度 |

注意：

- 主 KPI 是**锚点**，不是推荐理由的中心。
- 关键抓手是**业务路径**，不是 Mission Critical 本身。
- 上传材料通常落在**关键抓手或子分支**里。

## 6. 候选项生成模板

```markdown
Option X：【候选 Mission Critical】
- 类型：
- Mission Critical 层级：公司级 / 业务线级 / 项目级
- 主 KPI / 核心约束指标：
- 关键抓手：
- 为什么该 Mission Critical 成立：
- 主 KPI 如何衡量该 Mission Critical：
- 影响的关键结果或核心约束：
- 关键证据：
- 可拆解方向：
- 上传材料对应位置：（如无上传材料，可写"不适用"）
- 关联流程热点（linked_process_hotspots，来自 §16）：
- 与行业 MC 关系（industry_mc_alignment）：
- 价值树含义（value_tree_implication：single_cost_tree / single_revenue_tree / cost_and_revenue_trees）：
- 不确定性：
```

> 候选必须**按价值方向归入 `candidate_groups`**（`cost_down` / `revenue_up` / `both`），不再是扁平列表；每桶仍须含 ≥1 能碳相关 Option（按 §7 归入对应方向）。

## 7. 能碳 Option 规则

每次候选项中**必须包含至少一个能碳相关 Option**，但它**不默认成为推荐项**。

能碳 Option 只有在满足以下条件时，才可推荐为最终 Mission Critical：

1. 它是客户当前**上位业务命题**，而非上传材料中的单一项目；
2. 能源 / 碳成本或收益对客户**公司级结果影响显著**；
3. 外部政策、客户需求、电价、碳价或绿电要求正在**放大该问题**；
4. **数据可获得**，且可以支撑价值测算；
5. 客户有**明确动作空间**。

否则，能碳 Option 应定位为：公司级 Mission Critical 下的分支 / 业务线级 Mission Critical / 项目级 Mission Critical / 或某个解决方案场景。

**能碳 Option 必须归入价值方向桶（v2 分桶要求）**：能碳 Option 仍须保留，但在 `candidate_groups` 中必须归入某个方向，不再单独游离：

| 能碳情形 | 归入方向 |
| :-- | :-- |
| 能源成本高（降本驱动） | `cost_down` |
| 碳资产收益（增收驱动） | `revenue_up` |
| 能源成本 + 碳收益都显著 | `both` |

## 8. 候选项对比表

| 候选 Mission Critical | 层级 | 主 KPI | 关键抓手 | 类型 | 使命关键性 | 约束强度 | 经营/价值影响 | 趋势压力 | 证据强度 | 可拆解性 | 可行动性 | 能碳相关性 | 客户契合度 | 推荐判断 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|

评分时注意：

- 评分对象是 **Mission Critical 本身**，不是 KPI。
- "关键抓手清晰" **不等于** "Mission Critical 成立"。
- "能碳相关性高" **不代表** 优先级最高。
- 评分在**各价值方向桶内**进行；最终取舍以**用户方向选择（§17.2）**为先。

## 9. 推荐理由模板

```markdown
### AI 推荐优先项
- 推荐 Mission Critical：
- 层级：
- 主 KPI / 核心约束指标：
- 关键抓手：

### 推荐理由
1. 客户本体匹配：为什么它符合客户公司的组织类型、核心职责和价值逻辑。
2. 核心矛盾命中：为什么它抓住了客户当前最主要的经营压力、系统约束或不可失败事项。
3. 优先级判断：为什么它是当前必须优先解决的问题，而不是一般重要问题。
4. 相对其他候选项的优势：为什么它比其他候选 Mission Critical 更适合作为主线。
5. 其他候选项的定位：其他 Option 是子约束、驱动项、业务线主线、项目级主线，还是能碳支线。
6. 上传材料的位置：若用户提供材料，必须说明材料落在公司级 Mission Critical 的哪个分支，而不是被材料牵引。
7. Business Case 支撑性：为什么它足够大、可量化、可拆解、可行动，能支撑后续价值测算。
8. 主 KPI 的作用：主 KPI 如何衡量该 Mission Critical（不能把推荐理由写成 KPI 说明）。
```

## 10. 不得推荐规则

以下候选项**不得推荐为最终公司级 Mission Critical**：

- 只是上传材料里的项目主题；
- 只是 KPI，不是上位业务命题；
- 只是技术、系统、平台、产品或 Agent；
- 只是单一解决方案抓手；
- 没有明确说明为什么客户必须优先解决；
- 无法拆成 Value Tree / Constraint Tree；
- 缺少可量化主 KPI；
- 能碳 Option 只因材料出现而被强行推荐。

## 11. 牧原案例示例

**错误 Mission Critical**：降低畜牧园区单位能碳净成本
- 原因：上传材料主要是零碳园区、绿电直连、HVAC 和碳资产。
- 问题：被上传材料牵引，跳过了牧原公司本体分析。

**正确公司级 Mission Critical**：提升穿越猪周期的盈利韧性，降低生猪养殖完全成本。
- 主 KPI：周期底部利润率 / 生猪养殖完全成本。

Value Tree：

```
提升穿越猪周期的盈利韧性
├─ 降低生猪养殖完全成本
│  ├─ 饲料成本
│  ├─ 猪群健康
│  ├─ 生产效率
│  ├─ 人工效率
│  ├─ 资产利用
│  └─ 能碳与环保成本
├─ 提升屠宰肉食单猪利润
├─ 稳定出栏和现金流
└─ 优化资本结构
```

上传材料位置：

```
能碳与环保成本
├─ 零碳园区示范
├─ 绿电直连
├─ HVAC 能效提升
└─ 碳资产开发
```

因此，远景合作材料应被定位为：支撑"提升穿越猪周期的盈利韧性"下的**能碳与环保成本分支**，而不是直接定义牧原公司级 Mission Critical。

## 12. 方案方视角：项目/产品/服务如何连接并改善公司级命题

> 这是本步**面向客户讲故事的关键一节**，决定我们的方案能否打动高管。

**原则**：Mission Critical 必须锚定到**高管最心急的公司级命题**（最大成本项 / 周期性生存压力 / 核心约束），**而不是我们项目本身的主题**。我们项目的主题（能碳、数字化、某系统等）通常只占成本/价值的一小块，高管未必关心；但我们要论证的是——**我们的项目/产品/服务能改善价值树上的某些分支，并把改善传导到公司级主 KPI，从而帮客户解决他们最心急的问题**。

> 牧原例：高管最关心饲料价格与猪周期（饲料占完全成本 55–60%），不关心能源（<3%）。所以公司级命题立为"提升穿越猪周期的盈利韧性，降低生猪养殖完全成本"；而我们的零碳园区项目要论证的是——它不仅省能碳那一小块，更能**通过种养循环/低豆日粮/余能利用等降低饲料与综合成本**，从而拉低完全成本、帮客户跨越猪周期。

**做法（必须显式建立"连接链"）**：

1. **锚定公司级命题与主 KPI**：先按本指南确定高管最心急的公司级 Mission Critical 与主 KPI（如：完全成本 / 周期底部利润率）。
2. **定位项目落点**：说明我们的项目/产品/服务落在价值树的哪个分支（如：能碳与环保成本分支；但其影响可外溢到饲料、健康、资产利用等分支）。
3. **画出传导链**：`我们的项目/产品/服务 → 改善哪些影响因子 → 传导到哪条价值方向 → 改善公司级主 KPI → 改善公司级命题`。每一跳都要能说清因果，不能跳跃。
4. **量化连接**：尽量给出该传导链上每一跳的量级（哪怕是区间/示意），让高管看到"这个项目对我最在意的那个数字到底有多大帮助"。
5. **诚实边界**：若项目对公司级主 KPI 的直接贡献有限，要如实说明，并讲清它的**间接价值/战略价值**（如样板复制、合规风险对冲），不得夸大传导。

**通用性说明**：本节不限能碳。任何项目/产品/服务（数字化、某平台、某优化方案等）都应按"项目 → 价值树分支 → 公司级主 KPI → 公司级命题"这条链来论证其与高管心急问题的连接。**反模式**：直接把项目主题（如"建设某某平台"）当成公司级 Mission Critical（违反第 3 节材料使用规则与第 10 节不得推荐规则）。

> 输出落点：该"连接链"写入候选项的 `decomposable_directions` / 推荐理由的"Business Case 支撑性"，并在交付 PPT 的关键任务页/价值树页显式呈现（见 `ppt-deck-mapping.md`）。

## 13. 最终输出模板

```markdown
## Mission Critical 分析（两层：价值方向 → 客户命题）

### 一、Research 摘要（先 Research、先判公司本体）
- 客户类型 / 公司本体 / 行业环境 / 外部趋势 / 核心职责 / 关键约束 / 上传材料定位：

### 二、读取 Step 01 输入
- 行业普遍 Mission Critical：[方向 + 命题]
- 客户流程成本/收益拆分要点：
- 数据台账可信度 / 缺口：
- Step 01 客户 MC 初步方向候选：

### 三、行业-客户对齐
- 关系：[一致 / 偏离 / 更聚焦 / 数据不足]
- 客户特殊观察 + 对候选生成的影响：

### 四、流程经济性诊断
- 成本热点 / 收益热点 / 资产·风险热点（每条带证据 + 数据可信度）：

### 五、价值方向诊断（AI 建议，非最终）
- cost_down / revenue_up / both 各是否成立 + 理由 + 证据
- AI 推荐方向 + 理由 + caveat：

### 六、按方向分桶的候选 Mission Critical
**cost_down 桶**
- COST-1：命题（从大到小表达）/ 层级 / 主 KPI / 关键抓手 / 关联流程热点 / 与行业 MC 关系 / 证据 / value_tree_implication=single_cost_tree / 不确定性
**revenue_up 桶**
- REV-1：…（value_tree_implication=single_revenue_tree）
**both 桶**
- BOTH-1：…（value_tree_implication=cost_and_revenue_trees）
> 每桶仍须含 ≥1 能碳相关 Option（按 §7 归入对应方向）。

### 七、★ 用户方向选择（第一层，强制）
- 选定方向：[cost_down / revenue_up / both]（用户确认，优先于 AI）
- 对价值树的含义：[single_cost_tree / single_revenue_tree / cost_and_revenue_trees]

### 八、项目/产品/服务 → 公司级命题 连接链
- 我们的项目/产品/服务 → 价值树分支 → 改善的影响因子 → 价值方向 → 公司级主 KPI → 公司级命题
- 各跳量级（示意/区间）+ 诚实边界：

### 九、最终客户 Mission Critical（第二层）
- value_direction：[= 用户选择]
- Mission Critical / 主 KPI / 关键抓手 / 选定候选 id / 选择理由：

### 十、下游契约（驱动 Step 03）
- value_tree_mode：[single_cost_tree / single_revenue_tree / cost_and_revenue_trees]
- tree_calibers_required / must_use_process_hotspots / must_use_data_ledger_metrics：

### 人工确认
价值方向与最终 Mission Critical 均由业务负责人结合客户判断确认（两段式：先确认方向，再确认命题）。
```

---

## 14. 新版 Step 01 输入使用规则

步骤 02 **必须读取**步骤 01（结构化 Research）的以下产出，作为判断依据，不得脱离它们凭空立题：

| Step 01 字段 | 在 Step 02 的用途 |
| :-- | :-- |
| `industry_common_mission_critical` | 判断行业普遍压力方向，作为客户 MC 对齐基准（第 15 节） |
| `business_process_economics` | 识别客户自身的成本/收益/资产风险热点（第 16 节） |
| `data_ledger` | 判断每条数据可信度与口径，标注哪些判断受数据缺口影响 |
| `research_synthesis.initial_client_mc_options` | 接收 Step 01 的初步方向候选，作为方向诊断与候选生成的起点 |
| `company_research` / `industry_research` | 公司本体与行业研究底料 |

读取结果写入 yaml 的 `research_inputs` 摘要块。缺任一关键输入时，在 `data_gaps` 显式标注并向用户索要，不得静默跳过。

## 15. 行业 MC 与客户 MC 对齐规则

判断客户当前 MC 与行业普遍 MC 的关系，写入 `industry_client_mc_alignment.relationship`：

| 取值 | 含义 |
| :-- | :-- |
| `aligned` | 一致：客户痛点基本符合行业普遍问题 |
| `deviated` | 偏离：客户有特殊业务结构，MC 与行业普遍不同 |
| `more_focused` | 更聚焦：行业问题较宽，客户 MC 应落到某个特定流程/业务线 |
| `insufficient_data` | 数据不足：无法判断，需要用户补充 |

必须给出 `client_specific_observation`（客户特殊观察）、`implication_for_candidate_generation`（对候选生成的影响）与 `evidence`。

## 16. 客户流程经济性诊断规则

从 `business_process_economics` 识别三类热点，写入 `process_economics_diagnosis`：

- **成本热点（cost_hotspots）**：占总成本比例高 / 金额大 / 波动大 / 可控性强 / 外部趋势正在放大。
- **收益热点（revenue_hotspots）**：收入占比高 / 毛利贡献高 / 转化·价格·销量存在改善空间 / 客户有经营动作空间。
- **资产或风险热点（asset_or_risk_hotspots）**：资产利用率低 / 合规风险高 / 损失规模大。

每条热点必须带 `why_material`（为何重要）、`evidence` 与 `data_confidence`（数据可信度，来自 data ledger）。数据不足的热点照实标低可信度，不得伪装成客户真实数据。

## 17. 降本/增收/两者都要选择规则

### 17.1 AI 方向诊断（建议，非最终）

写入 `value_direction_diagnosis`，对 `cost_down` / `revenue_up` / `both` 各给 `supported` + `rationale` + `supporting_processes` + `evidence`，并给 `recommendation.suggested_direction` + `reason` + `caveat`。判断标准：

- 客户流程**成本热点明显且可控性强** → 推荐 `cost_down`。
- **收入/价格/销量/转化问题更明显** → 推荐 `revenue_up`。
- 成本与收益**都有明确数据支撑且都足够大** → 推荐 `both`。
- 某方向**只有愿景、没有数据** → 不强行推荐，列为潜在方向或 `data_gap`。

### 17.2 用户选择（强制检查点，最终）

必须新增一个强制用户检查点，先确认价值方向再确认 MC，写入 `user_value_direction_choice`：

- `selected_direction`：`cost_down | revenue_up | both`
- `implication_for_value_tree`：`single_cost_tree | single_revenue_tree | cost_and_revenue_trees`

规则：

- AI 可推荐方向，但**不能替用户最终选择**；用户选择优先级高于 AI 推荐。
- 用户选择与 AI 推荐不同时，保留 AI `caveat`，但按用户选择驱动下游。
- 用户选 `both` 时，Step 03 必须生成两棵树，不能混成一棵。

### 17.3 最终 MC 表达规则（按方向）

确认 `confirmed_customer_mission`（含 `value_direction`）时：

- `cost_down`：MC 表达"降低某类关键成本 / 提升成本竞争力 / 改善利润韧性"。
- `revenue_up`：MC 表达"提升某类收入 / 提升单客价值 / 提升价格或销量 / 提升变现效率"。
- `both`：表达为复合命题，但**必须声明后续拆为成本树 + 收益树**，不能在一句核心等式里混用成本和收益。

## 18. 用户选择如何驱动 Value Tree

写入 `downstream_contract`，Step 03 行为被直接驱动：

| 用户选择 | `value_tree_mode` | `tree_calibers_required` | Step 03 行为 |
| :-- | :-- | :-- | :-- |
| `cost_down` | `single_cost_tree` | `[cost_saving]` | 只生成成本价值树 |
| `revenue_up` | `single_revenue_tree` | `[revenue_uplift]` | 只生成收益价值树 |
| `both` | `cost_and_revenue_trees` | `[cost_saving, revenue_uplift]` | 至少生成成本树 + 收益树，分别 MECE，不混用 |

`downstream_contract` 还须带 `must_use_process_hotspots`（Step 03/后续必须承接的流程热点）与 `must_use_data_ledger_metrics`（必须引用的数据台账指标）。

## 19. 红线

- 不得脱离 Step 01 的行业 MC 和流程经济性数据生成客户 MC。
- 不得只凭上传材料或单一项目主题推荐客户 MC。
- 不得在用户未选择价值方向前锁死 Value Tree 结构（不写 `downstream_contract`、不进 Step 03）。
- 用户选择 `both` 时，不得把成本和收益混进一棵树，必须拆成成本树 + 收益树。
- 如果流程成本/收益数据不足，必须标注 `data_gaps`，不得假装有企业真实数据。
- 命题表达、行业-客户对齐判断、流程经济性诊断中凡出现可量化声明（趋势/规模/占比/增减/效率/对比/目标/质量/缺口/金额/周期/排名等，见 SKILL.md 铁律 7），必须带具体数字（企业真实 → 行业平均 → 模拟，标来源），不得只定性。这些数值是 P2/P5 交付页的数据来源。
<!-- @AI_GENERATED: end -->

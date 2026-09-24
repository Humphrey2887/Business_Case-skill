# business-pain-point 过程文件 YAML 模板

本工作流每一步把结构化结果写入 `process/<step>.yaml`，作为下游步骤的单一事实源。
若 YAML 写入失败，回退为 `process/<step>.md`（保持相同结构，用 markdown 标题/列表）。

> 已定义步骤 01–10 的模板。模板演进时与各步 standards/steps 保持对齐。

---

## 目录

- [01 · 结构化 Research](#01--结构化-research)
- [02 · Mission Critical](#02--mission-critical)
- [03 · Value Tree](#03--value-tree)
- [04 · 影响因子数据就绪校验](#04--影响因子数据就绪校验)
- [05 · 痛点业务化精修](#05--痛点业务化精修)
- [06 · 痛点评分与核心确认](#06--痛点评分与核心确认)
- [07 · 大痛点组合](#07--大痛点组合)
- [08 · 关键场景](#08--关键场景)
- [09 · 价值量化](#09--价值量化)
<!-- @AI_GENERATED -->
- [10 · 技术架构（Ontology）](#10--技术架构ontology)
<!-- @AI_GENERATED: end -->
- [11 · 实施路径](#11--实施路径)

---

<!-- @AI_GENERATED -->
## 01 · 结构化 Research

文件：`process/01-research.yaml`

字段对应标准文档 [../standards/01-research-guide.md](../standards/01-research-guide.md)。本步以结构化研究模块产出五项交付（案例公司研究 / 所在行业研究 / 行业普遍 MC / 业务流程成本收益拆分 / 数据台账），并收敛出客户 MC 初步候选，作为步 02 判断的输入。

```yaml
step: "01-research"
industry: "<客户行业>"
client: "<客户/分析对象>"
topic: "<项目主题/分析议题>"
input_identification:             # 阶段1：输入识别
  client_confirmed: true
  industry_confirmed: true
  uploaded_materials:
    - name: ""
      type: ""                    # 方案/年报/产品介绍/流程材料 等
      role: ""                    # 仅作 Research 输入与场景证据，不得直接当 Mission Critical
company_research:                 # 阶段2：案例公司研究
  company_ontology:               # 公司本体优先：先判本体，再看上传材料
    org_type: ""
    core_business: ""
    core_responsibility: ""
    value_creation: ""            # 靠什么赚钱 / 最大成本项 / 核心资产 / 最稀缺资源 / 运营瓶颈
    largest_cost_items: []
    key_assets: []
    key_constraints: []
  revenue_structure:
    - item: ""
      share: ""
      amount: ""
      period: ""
      source: ""
      confidence: ""              # high | medium | low
  cost_structure:
    - item: ""
      share: ""
      amount: ""
      period: ""
      source: ""
      confidence: ""
  key_business_data:              # 关键经营数据，逐条标口径与来源类型
    - metric: ""
      value: ""
      unit: ""
      period: ""
      entity_scope: ""            # 集团/子公司/单园区/单工厂 等
      source_type: ""             # client_real | company_public | industry_public | estimate | internal_assumption | analogy
      source: ""
      confidence: ""
  uploaded_material_position: ""  # 归位：公司战略/业务线/项目方案/产品系统；落在公司级命题哪个分支；无则 '不适用'
industry_research:                # 阶段3：所在行业研究（必须独立完成）
  industry_value_logic: ""
  industry_revenue_model: ""
  industry_cost_structure:
    - item: ""
      share: ""
      amount: ""
      source: ""
      confidence: ""
  industry_profit_drivers:
    - driver: ""
      logic: ""
      evidence: ""
  common_constraints:
    - constraint: ""
      impact: ""
      evidence: ""
  external_trends:
    - trend: ""
      impact: ""
      source: ""
      confidence: ""
  benchmarks:
    - case: ""
      what_happened: ""
      result: ""
      implication_for_client: ""
      source: ""
industry_common_mission_critical: # 阶段4：行业普遍 Mission Critical（行业普遍命题，非客户特定，非解决方案）
  direction: ""                   # cost_down | revenue_up | both | risk_or_compliance | asset_efficiency | uncertain
  statement: ""
  rationale: ""
  evidence:
    - point: ""
      source: ""
      source_type: ""
      confidence: ""
business_process_economics:       # 阶段5：客户业务流程成本/收益拆分（不使用固定流程模板）
  - process: ""
    basis: ""                     # 行业价值链 | 公司年报分部 | 上传材料 | 管理口径 | 行业通用假设（必填）
    business_stage: ""            # 可选：上游/中游/下游或业务线
    cost_or_revenue_item: ""
    type: ""                      # cost | revenue | asset | risk
    share_of_total: ""
    amount: ""
    unit: ""                      # 元/年、万元/年、元/吨、%、kWh 等
    period: ""                    # 如 FY2025、2025H1
    entity_scope: ""              # 集团/子公司/单园区/单工厂/行业平均 等
    source: ""
    source_type: ""               # client_real | company_public | industry_public | estimate | internal_assumption | unavailable
    confidence: ""                # high | medium | low
    data_gap: ""
data_ledger:                      # 阶段6：数据台账（所有关键数据统一登记）
  - metric: ""
    value: ""
    unit: ""
    period: ""
    entity_scope: ""
    source_type: ""               # client_real | company_public | industry_public | estimate | internal_assumption | analogy
    source: ""
    confidence: ""                # high | medium | low
    used_in: ["industry_mc", "company_mc", "process_economics"]  # value_tree | valuation 等
    caveat: ""
research_synthesis:               # 阶段6：综合判断（交步 02 的输入，不锁死最终客户 MC）
  industry_common_mc: ""
  client_cost_pressure: ""
  client_revenue_pressure: ""
  client_process_cost_hotspots: []
  client_process_revenue_hotspots: []
  initial_client_mc_options:      # 仅作步 02 候选输入
    - direction: "cost_down"
      statement: ""
      evidence: []
    - direction: "revenue_up"
      statement: ""
      evidence: []
    - direction: "both"
      statement: ""
      evidence: []
  recommended_next_step_input: ""
data_gaps:
  - gap: ""
    affects: ""
    needed_from_user: ""
# @AI_GENERATED
internal_checklist_ledger:            # 收资清单内部台账（仅供内部；不生成对外文件，在检查点口头/对话告知客户）
  organized_by: "industry_value_chain"  # industry_value_chain | company_structure（动态推导依据，非固定模板）
  items:
    - material_name: ""               # 资料名称
      usage: ""                       # 用途（向客户说明时改写为客户语言）
      necessity: ""                   # 必需 | 可选
      blocks_core_analysis: true      # true=缺失阻断核心分析→必需；false=仅降精度→可选
      gap_attribution:                # 缺口归属（超集追溯）
        from_data_gaps: []            # 引用 data_gaps 的索引/gap 文案键
        from_process_data_gap: []     # 引用 business_process_economics[].process 的键
        extra_analysis_needed: false  # true=缺口列表未覆盖、分析所需的额外补充项
# @AI_GENERATED: end
gates:
  company_research_complete: ""
  industry_research_complete: ""
  industry_mc_generated: ""
  process_economics_complete: ""
  data_ledger_complete: ""
  data_honesty_check: ""
status: "complete"                # complete | in_progress | blocked
```

**字段要点：**

- **公司/行业双研究**：`company_research` 与 `industry_research` 是两个独立且都必须完成的模块；不得只研究公司而忽略行业，也不得只堆行业趋势而不收敛 MC。
- **行业普遍 MC**：`industry_common_mission_critical.direction` 取六枚举之一，`statement` 必须是行业普遍命题、不是客户特定命题，也不得写成解决方案。
- **业务流程不硬编码**：`business_process_economics[].basis` 必填；客户真实流程优先于行业通用价值链，冲突以客户为准；缺客户真实流程时用行业通用价值链作临时假设并在 `data_gap` 标注。
- **数据诚实**：`data_ledger[].source_type` 与各处 `source_type` 必填，区分客户真实 / 公司公开 / 行业公开 / 估算 / 内部假设 / 类比 / 不可得；不得把行业平均/假设伪装成客户真实数据。
- **下游契约**：`industry_common_mission_critical` + `business_process_economics` + `data_ledger` + `research_synthesis.initial_client_mc_options` 传给步 02；步 01 只形成候选输入，**不锁死最终客户 MC**。
- **收资台账为超集**：`internal_checklist_ledger.items` 必须折叠纳入每条 `data_gaps` 与每条非空 `business_process_economics[].data_gap`（经 `gap_attribution` 追溯：`from_data_gaps` / `from_process_data_gap` 标明来源），并可含缺口列表未覆盖、但分析所需的额外补充项（`extra_analysis_needed: true`）——即台账内容严格 ⊇ 缺口来源。
- **一致性约束**：`blocks_core_analysis` 与 `necessity` 必须一致（`true`→必需、`false`→可选）。
- **仅供内部、口头告知**：本台账仅供内部；不生成对外 Word/文件，收资项在步骤 01 既有用户检查点以客户语言口头/对话形式告知客户（区分必需/可选）。
<!-- @AI_GENERATED: end -->

---

## 02 · Mission Critical

<!-- @AI_GENERATED -->
文件：`process/02-critical-mission.yaml`

字段对应标准文档 [../standards/02-critical-mission-guide.md](../standards/02-critical-mission-guide.md)（v1.8）。**两层判断**：先基于 Step 01 判断价值方向（降本/增收/两者）并请用户确认，再在所选方向下确认客户 Mission Critical，最后写明驱动 Step 03 的下游契约。

```yaml
step: "02-critical-mission"
industry: "<客户行业>"
client: "<客户/分析对象>"
research_inputs:                  # 必须读取 Step 01（结构化 Research）的产出摘要
  industry_common_mission_critical: "<引用 01 的行业普遍 MC：方向 + 命题>"
  business_process_economics_summary: "<引用 01 的客户流程成本/收益拆分要点>"
  data_ledger_summary: "<引用 01 数据台账：哪些数据可信、哪些待补>"
  initial_client_mc_options: ["<引用 01 research_synthesis 的初步方向候选>"]
research_summary:                 # 先 Research 再判断（硬规则1/2）；公司本体判断
  client_type: "<客户类型>"
  company_ontology: "<客户公司本体判断：组织类型/核心职责/价值逻辑>"
  industry_environment: "<行业 / 系统环境>"
  external_trends: "<外部趋势>"
  core_responsibility: "<客户核心职责 / 价值逻辑>"
  key_constraints: "<关键约束或经营压力>"
  uploaded_material_position: "<上传材料定位：公司战略/业务线/项目方案/产品系统；落在公司级命题哪个分支>"
industry_client_mc_alignment:     # 行业普遍 MC 与客户 MC 的关系（guide 第15节）
  relationship: "aligned"         # aligned | deviated | more_focused | insufficient_data
  industry_common_mc: ""
  client_specific_observation: ""
  implication_for_candidate_generation: ""
  evidence: []
process_economics_diagnosis:      # 基于 01 的流程经济性，识别热点（guide 第16节）
  cost_hotspots:
    - process: ""
      cost_item: ""
      share_or_amount: ""
      why_material: ""            # 占比高/金额大/波动大/可控性强/趋势放大
      evidence: []
      data_confidence: ""         # high | medium | low（来自 data ledger）
  revenue_hotspots:
    - process: ""
      revenue_item: ""
      share_or_amount: ""
      why_material: ""            # 收入占比/毛利贡献/价格销量转化空间/动作空间
      evidence: []
      data_confidence: ""
  asset_or_risk_hotspots:
    - process: ""
      item: ""
      value_impact: ""           # 资产利用率低/合规风险高/损失规模大
      why_material: ""
      evidence: []
      data_confidence: ""
value_direction_diagnosis:        # AI 方向诊断（建议，非最终；guide 第17.1节）
  cost_down:
    supported: true
    rationale: ""
    supporting_processes: []
    evidence: []
  revenue_up:
    supported: false
    rationale: ""
    supporting_processes: []
    evidence: []
  both:
    supported: false
    rationale: ""
    condition: ""
  recommendation:
    suggested_direction: "cost_down"   # cost_down | revenue_up | both
    reason: ""
    caveat: ""
candidate_groups:                 # 按方向分桶生成候选；每桶可多个；仍须含 ≥1 能碳 Option
  cost_down:
    - id: "COST-1"
      mission_critical: "<从大到小表达：上位使命在前，抓手/KPI 在后>"
      level: "company"            # company | business_line | project
      primary_kpi: "<主 KPI / 核心约束指标>"
      key_levers: ["<关键抓手>"]
      linked_process_hotspots: ["<来自 process_economics_diagnosis 的成本热点>"]
      industry_mc_alignment: "<与行业普遍 MC 的关系：一致/偏离/更聚焦>"
      evidence: ["<关键证据>"]
      value_tree_implication: "single_cost_tree"
      energy_carbon_related: false
      uncertainty: ""
  revenue_up:
    - id: "REV-1"
      mission_critical: ""
      level: "company"
      primary_kpi: ""
      key_levers: []
      linked_process_hotspots: ["<来自 revenue_hotspots>"]
      industry_mc_alignment: ""
      evidence: []
      value_tree_implication: "single_revenue_tree"
      energy_carbon_related: false
      uncertainty: ""
  both:
    - id: "BOTH-1"
      mission_critical: "<复合命题，声明后续拆成本树+收益树，不在一个等式混用>"
      level: "company"
      primary_kpi: ""
      key_levers: []
      linked_process_hotspots: []
      industry_mc_alignment: ""
      evidence: []
      value_tree_implication: "cost_and_revenue_trees"
      energy_carbon_related: false
      uncertainty: ""
comparison:                        # 可选：对所选方向桶内候选打分（评分对象是 MC 本身，不是 KPI）
  - id: "COST-1"
    scores:
      mission_criticality: 0
      constraint_strength: 0
      business_value_impact: 0
      trend_pressure: 0
      evidence_strength: 0
      decomposability: 0
      actionability: 0
      client_fit: 0
    energy_carbon_relevance: "<能碳相关性：高/中/低>"
    recommend_judgment: "<推荐/不推荐及一句话理由>"
recommendation:                    # 所选方向下的 AI 推荐项 + 连接链 + 8 条理由
  recommended_id: "COST-1"
  mission_critical: "<推荐命题>"
  level: "<层级>"
  primary_kpi: "<主 KPI>"
  key_levers: ["<关键抓手>"]
  connection_chain:                # 项目/产品/服务 → 公司级命题 连接链（guide 第12节）
    our_offering: "<我们的项目/产品/服务>"
    value_tree_branch: "<落在价值树哪个分支>"
    chain: "<项目 → 改善的影响因子 → 价值方向 → 公司级主KPI → 公司级命题>"
    magnitude_per_hop: "<各跳量级，示意/区间>"
    honest_boundary: "<直接贡献有限处 + 间接/战略价值说明>"
  reasons:                         # 8 条推荐理由（解释为什么是该命题，不是该 KPI）
    client_ontology_fit: ""
    core_conflict_hit: ""
    priority_judgment: ""
    advantage_over_others: ""
    other_candidates_position: ""
    uploaded_material_position: ""
    business_case_support: ""
    primary_kpi_role: ""
user_value_direction_choice:      # ⛔ 第一层用户检查点（guide 第17.2节）
  status: "pending"               # pending | confirmed
  selected_direction: ""          # cost_down | revenue_up | both（用户选定，优先级高于 AI）
  selected_by_user: false
  user_comment: ""
  implication_for_value_tree: ""  # single_cost_tree | single_revenue_tree | cost_and_revenue_trees
confirmed_customer_mission:       # 第二层：所选方向下确认最终客户命题
  value_direction: ""             # cost_down | revenue_up | both（= 用户选择）
  mission_critical: ""
  primary_kpi: ""
  key_levers: []
  selected_candidate_id: ""       # 引用 candidate_groups 中的候选 id
  confirmation_status: "pending"  # pending | confirmed
  reason_for_selection: ""
downstream_contract:              # 驱动 Step 03（guide 第18节）
  value_tree_mode: ""             # single_cost_tree | single_revenue_tree | cost_and_revenue_trees
  tree_calibers_required: []      # [cost_saving] | [revenue_uplift] | [cost_saving, revenue_uplift]
  must_use_process_hotspots: []   # Step 03/后续必须承接的流程热点
  must_use_data_ledger_metrics: []# 必须引用的数据台账指标
data_gaps:
  - gap: ""
    affects: ""
    needed_from_user: ""
status: "complete"                 # complete | in_progress | blocked
```

**字段要点：**

- **必读 Step 01**：`research_inputs` 必须摘要引用 01 的 `industry_common_mission_critical` / `business_process_economics` / `data_ledger` / `research_synthesis.initial_client_mc_options`；缺则进 `data_gaps`（guide 第14节）。
- **行业-客户对齐**：`industry_client_mc_alignment.relationship` 取 aligned / deviated / more_focused / insufficient_data（guide 第15节）。
- **流程经济性诊断**：`process_economics_diagnosis` 三类热点每条带 `why_material` / `evidence` / `data_confidence`（guide 第16节）。
- **方向诊断为建议**：`value_direction_diagnosis.recommendation` 是 AI 建议，**不是最终**；最终以 `user_value_direction_choice.selected_direction` 为准（用户优先）。
- **按方向分桶**：`candidate_groups` 分 cost_down / revenue_up / both；每候选标 `linked_process_hotspots`、`industry_mc_alignment`、`value_tree_implication`；仍须含 ≥1 `energy_carbon_related: true`。
- **两段确认**：先 `user_value_direction_choice`（第一层方向）后 `confirmed_customer_mission`（第二层命题，含 `value_direction`）。
- **下游契约**：`downstream_contract` 驱动 Step 03 生成成本树 / 收益树 / 两棵树；`both` 必须为 `cost_and_revenue_trees`、`tree_calibers_required: [cost_saving, revenue_uplift]`，不得混进一棵树。
- 上传材料按 `uploaded_material_position` 落到价值树某分支，作为后续场景/抓手证据，不得直接当树根。
<!-- @AI_GENERATED: end -->

---

## 03 · Value Tree

<!-- @AI_GENERATED -->
文件：`process/03-value-tree.yaml`

字段对应标准文档 [../standards/03-value-tree-guide.md](../standards/03-value-tree-guide.md)。新版价值树是**端到端价值链**，固定从左到右 8 层：综合目标 → 成本/收益类型 → 价值方向 → 关键抓手 → 影响因子 → 痛点分析 → 痛点权重 → AI 场景。**由 02 用户方向驱动**：cost_down→仅成本树；revenue_up→仅收益树；both→成本树 + 收益树（≥2 棵，分离不混用）。

```yaml
step: "03-value-tree"
industry: "<客户行业>"
client: "<客户/分析对象>"
mission_critical: "<引用 02 confirmed_customer_mission.mission_critical>"
value_direction: "cost_down"          # cost_down | revenue_up | both（引自 02 用户选择）
value_tree_mode: "single_cost_tree"   # single_cost_tree | single_revenue_tree | cost_and_revenue_trees（引自 02 downstream_contract）
trees:                                # cost_down→1棵成本树；revenue_up→1棵收益树；both→成本树+收益树≥2棵
  - tree_id: "T-cost-1"
    tree_type: "cost_saving"          # cost_saving | revenue_uplift（树内单一，不混用）
    integrated_goal: "降低成本"        # 第1层·综合目标（= 02 用户方向）
    root_equation: "<树根价值等式，左侧口径与 tree_type 一致>"
    classification_basis: ""          # 第2层一级分类口径（按案例选，不写死）：财务成本属性 | 成本科目 | 业务流程 | 价值链环节 | 收入驱动因素 | 客户经营链路 | 客户管理口径
    classification_rationale: ""      # 为什么本案例选该口径、它如何构成综合目标
    mece_check:
      collectively_exhaustive: ""     # 各分类合计/连乘是否完整构成综合目标
      mutually_exclusive: ""          # 同层是否互斥、无重复计算
      no_mixed_basis: true            # 同层是否未混用不同口径（如主题口径 vs 财务科目）
    pain_library:                     # 本树痛点全局唯一定义（B 模型）：一条痛点一个 id，下方影响因子按 id 引用，不重复写痛点正文
      - pain_id: "P-1"
        pain_name: "燃料质量识别不足"     # 短中文名；全流程引用该痛点一律用「代号（中文名）」，如 P-1（燃料质量识别不足）
        pain_statement: "<由于[根因]，导致[影响因子]无法稳定改善，进而影响[价值方向/成本收益结果]>"
        affected_factors: ["<该痛点拖累的影响因子，可多个>"]
        business_consequence: ""      # 第5步回填：终局经营代价（落到七类经营结果之一）
        outcome_type: ""              # 第5步回填：七类经营结果之一
        anti_pattern_ok: ""           # 第5步回填：是否过反模式闸门（非"缺系统/平台/能力"）
        priority_score: ""            # 第6步回填：四维加权优先级总分（满分10）
        tier: ""                      # 第6步回填：core | strategic_background | excluded
    branches:                         # 第2层·成本/收益类型（同层同一口径，MECE）
      - cost_or_revenue_type: ""      # 如：燃料成本 / 销量
        operator_to_siblings: "+"     # 与同级如何构成上一层：+ | - | × | ÷
        value_directions:             # 第3层·价值方向（带运算关系的价值变化机制）
          - direction: ""             # 如：燃料成本降低
            operator_logic: ""        # 必须带运算符，如：单位燃料发电量提升 × 燃料采购总价格降低
            key_levers:               # 第4层·关键抓手（业务动作方向，不一定是数据指标）
              - lever: ""             # 如：增强燃烧经济性
                impact_factors:       # 第5层·影响因子（可量化/采集/干预的数据指标，必须带单位）
                  - factor: ""        # 如：燃料低位发热量
                    unit: ""          # 必填，如 MJ/kg；无法确定填 "待确认" 并写 data_gap
                    data_source: ""   # 数据来源/系统/台账
                    data_gap: ""      # 单位/口径待确认时说明
                    pain_contributions:   # 第6-7层·引用 pain_library 的痛点 + 该痛点对本影响因子的根因权重
                      - pain_ref: "P-1（燃料质量识别不足）"  # 代号（中文名）；引用本树 pain_library 的 pain_id
                        pain_weight: 0     # 该痛点对本影响因子变动的根因贡献(%)；同一影响因子下合计=100
                        weight_basis: "expert_estimate"  # client_real | industry_public | expert_estimate | internal_assumption | to_validate
                    pain_weight_check:
                      sum_to_100: true     # 同一影响因子下 pain_contributions 权重合计是否=100%
                      note: ""
                    scenarios:        # 第8层·AI 场景（用 AI 技术打包解决痛点，非泛业务动作）
                      - scenario_id: "SC-1"
                        name: ""      # 如：AI 燃料质量识别与燃烧参数自适应优化
                        ai_mechanism: "<用什么数据 → 识别什么模式 → 做什么预测/优化/推荐 → 如何闭环到业务动作>"
                        linked_pains: ["P-1（燃料质量识别不足）"]  # 代号（中文名）
                        expected_factor_improvement: "<改善哪个影响因子、方向/量级（示意）>"
                        merge_reason: ""  # 多因子合并为一个综合场景时填合并理由；否则留空
  # - tree_id: "T-rev-1"  tree_type: "revenue_uplift"  integrated_goal: "提升收益"  ...（value_direction=both 时并列收益树，结构同上）
gates:
  tree_mode_match: "<trees 是否与 value_tree_mode 一致：both 必须≥2棵且成本/收益分离>"
  caliber_single: "<每棵树 tree_type 与 root_equation 左侧口径是否单一、未混用>"
  classification_basis_stated: "<每棵树是否写明 classification_basis 与 rationale、同层未混口径>"
  mece: "<同层是否互斥且完整构成上层（no_mixed_basis）>"
  operator_logic_present: "<每条 value_directions.direction 是否带运算符、能下钻到抓手>"
  factor_unit_required: "<每个影响因子是否带 unit；无单位不得入树>"
  pain_per_factor: "<每个影响因子是否至少挂 1 个痛点>"
  pain_weight_sum_100: "<同一影响因子下痛点权重合计是否=100%>"
  ai_scenario_required: "<每个场景是否为 AI 场景（说明数据/识别/预测优化/闭环），非泛业务动作>"
status: "complete"             # complete | in_progress | blocked
```

**字段要点：**

- **方向驱动**：`value_direction` / `value_tree_mode` 引自 02 `confirmed_customer_mission` 与 `downstream_contract`；`both` 必须成本树 + 收益树分离，不混进一棵树/一个等式。
- **八层结构**：综合目标 → 成本/收益类型 → 价值方向 → 关键抓手 → 影响因子 → 痛点 → 痛点权重 → AI 场景，逐层下钻、可溯源。
- **分类口径按案例**：`classification_basis` **不写死**，必须填 `classification_rationale`；同层单一口径、MECE、不混"主题口径"与"财务科目"（`no_mixed_basis`）。
- **价值方向带运算符**：`value_directions[].operator_logic` 必须含 +/-/×/÷，不能只写动作词。
- **影响因子必带单位**：`impact_factors[].unit` 必填；无法确定填 `待确认` 并写 `data_gap`；**无单位不得入树**。
- **痛点统一术语**：用 `pains` / `pain_weight`，禁用 `small_pains` / `small_pain_weight`。
- **痛点全局唯一（B 模型）**：每棵树的痛点在 `pain_library` 里**只定义一次**（一条痛点一个 `pain_id` + `pain_name` 中文名）；影响因子下用 `pain_contributions[].pain_ref` 按 id 引用，不重复写痛点正文。一条痛点可被多个影响因子引用（各自给 per-factor 权重）。
- **引用必带中文名**：全流程引用痛点一律写「代号（中文名）」，如 `P-1（燃料质量识别不足）`（含 `pain_contributions.pain_ref`、`scenarios.linked_pains`、下游 05/06 的引用）。
- **同一条痛点、多步加属性**：`pain_library` 是痛点单一事实源——03 给根因权重并挂场景；05 回填 `business_consequence`/`outcome_type`/`anti_pattern_ok`；06 回填 `priority_score`/`tier`。下游**不新建痛点**，只在同 id 上补字段。
- **痛点权重 = 根因贡献**：同一影响因子下 `pain_contributions[].pain_weight` 合计 = 100%（`pain_weight_check.sum_to_100`）；`weight_basis` 标来源；**不等于 Step 06 痛点优先级评分**（后者是跨痛点的业务重要性，回填在 `pain_library[].priority_score`）。
- **AI 场景**：必须是 AI 技术方案（说明数据/识别/预测优化/闭环），非泛业务动作；原则一因子一场景，合并需写 `merge_reason`；`scenario_id` 供 Step 08 深化回写。
- **边界**：Step 04 校验补单位/baseline/数据源；Step 05 深化痛点业务化；Step 06 做优先级评分（≠ 本步痛点权重）；Step 08 深化场景机制并回写 `scenario_id`；Step 09 测算价值。
<!-- @AI_GENERATED: end -->

---

<!-- @AI_GENERATED -->
## 04 · 影响因子数据就绪校验

文件：`process/04-kpi-factor.yaml`

字段对应标准文档 [../standards/04-kpi-factor-guide.md](../standards/04-kpi-factor-guide.md)。本步**不再新造 KPI/痛点**，而是对 `03-value-tree.yaml` 的 `impact_factors` 做"上秤"校验：敲定单位、补 `baseline` / `data_source`，过可测量 + 因果直接性闸门，标出可纳入第 9 步测算的子集。痛点不在本步处理（在 03 定义、05 业务化）。

```yaml
step: "04-kpi-factor"
mission_critical: "<引用 02 confirmed_customer_mission.mission_critical>"
value_direction: "<引用 02/03 value_direction：cost_down | revenue_up | both>"
impact_factor_readiness:        # 对 03 每个影响因子做数据就绪校验（不新造因子）
  - factor: "<引用 03 impact_factors.factor>"
    from_value_tree: "<所属 树/成本收益类型/价值方向/关键抓手 路径>"
    outcome_type: "<七类经营结果之一：收入增长/成本降低/利润提升/资产效率/运营效率/风险损失/战略价值>"
    unit: "<引用 03 的 unit；03 标'待确认'的在此敲定>"
    baseline: "<当前基线数值，或 '待调研'>"
    data_source: "<ERP/CRM/SCADA/MES/能碳台账/人工台账 等>"
    proxy: "<战略/定性因子填代理指标(含单位/基线/数据源)，否则留空>"
    measurable: true            # 是否可上秤（有单位 + 数据源 / 可信 proxy）
    causal_directness: "<改因子 → 价值方向的直接传导说明（过 Gate 2）>"
    quantify_priority: "high"   # high | mid | low：是否纳入第 9 步重点测算
focus_factors: ["<聚焦的核心影响因子（不撒胡椒面，可选收敛）>"]
gates:
  measurability: "<可测量性闸门结论；战略类用 proxy 通过的说明>"
  causal_directness: "<因果直接性闸门结论>"
  unit_completeness: "<03 中 unit=待确认 的是否已敲定，否则转入 data_gaps>"
data_gaps:
  - "<标注 '待调研' 的基线、缺失的数据源、未定单位等>"
status: "complete"            # complete | in_progress | blocked
```

**字段要点：**

- **校验而非新造**：`impact_factor_readiness` 逐条对应 03 的 `impact_factors`，本步只补 `baseline` / `data_source` / `proxy` 并过闸门，不新造因子，也不碰痛点。
- **上秤三件套**：每个因子（或其 proxy）必须有 `unit` / `baseline` / `data_source`；战略/定性因子用 `proxy` 上秤。
- Gate 1（可测量性）：因子或其 proxy 必须指得到具体系统/台账，否则打回或转 `data_gaps`。
- Gate 2（因果直接性）：因子必须可通过系统参数/业务动作直接改变其价值方向。
- **下游契约**：第 9 步价值量化按 `impact_factor_readiness` 的 `baseline` / `data_source` / `quantify_priority` 取数测算；痛点业务化在第 5 步、痛点优先级在第 6 步。
<!-- @AI_GENERATED: end -->

---

<!-- @AI_GENERATED -->
## 05 · 痛点业务化精修

文件：`process/05-pain-point.yaml`

字段对应标准文档 [../standards/05-pain-point-guide.md](../standards/05-pain-point-guide.md)。本步**不新建痛点**，而是对 `03-value-tree.yaml` 各树 `pain_library` 里**已定义的同一批痛点**做业务化精修：过反模式闸门（非"缺系统/平台"）、因果闭环到七类经营结果，并在**同一 `pain_id`** 上回填 `business_consequence` / `outcome_type` / `anti_pattern_ok`。引用痛点一律带中文名。

```yaml
step: "05-pain-point"
mission_critical: "<引用 02 命题，校准痛点是否对齐经营主线>"
refined_pains:                  # 引用并精修 03 pain_library 的同一批痛点（同 id，不新建）
  - pain_ref: "P-1（燃料质量识别不足）"  # 代号（中文名），引用 03 树级 pain_library 的 pain_id
    affected_factors: ["<来自 03 的被拖累影响因子>"]
    business_context: "<业务情境/作业环节，如：月度采购窗口、出口合规审查；非第8步正式场景>"
    kpi_degradation: "<影响因子/价值方向负面状态：无法稳定改善 / 波动剧烈 等>"
    refined_statement: "<业务化精修后的痛点表达（不含'缺XX系统'，因果完整）>"
    outcome_type: "<七类经营结果之一>"      # 回填 03 pain_library.outcome_type
    business_consequence: "<终局经营代价，必须具体，过 Gate 2>"  # 回填 03 pain_library.business_consequence
    anti_pattern_ok: true       # 是否过反模式闸门（非'缺系统/平台/能力'、非照搬原话）→ 回填 03 pain_library.anti_pattern_ok
    merged_from: ["<若由多条合并，列被并入的代号（中文名）>"]
gates:
  anti_pattern: "<反模式闸门结论：是否排除'缺XX系统/平台/能力'与照搬原话>"
  causal_closure: "<因果闭环闸门结论：每条是否指向7类经营结果中的具体代价>"
  id_consistency: "<是否沿用 03 pain_library 的 pain_id、未新造痛点、引用带中文名>"
data_gaps:
  - "<精修中暴露的待补信息>"
status: "complete"            # complete | in_progress | blocked
```

**字段要点：**

- **同一批痛点、同 id**：`refined_pains[].pain_ref` 必须引用 03 `pain_library` 的 `pain_id`（带中文名），**不新建痛点**；本步是业务化精修与校验，回填 03 pain_library 的对应字段。
- **去重合并**：若 03 出现实质重复的痛点，本步可合并，用 `merged_from` 留痕（合并后仍是一个 id）。
- Gate 1（反模式）：`refined_statement` 不得含"缺乏 XX 系统/平台/工具/能力"等缺药式表达。
- Gate 2（因果闭环）：`business_consequence` 必须落在七类经营结果之一（含战略价值），不能停在中间过程指标。
- **边界**：本步只做痛点业务化（定性精修），**不打优先级分**（优先级在第 6 步）；也不改 03 的痛点根因权重。
- 下游第 6 步痛点评分读取本文件精修后的痛点（同 id）做业务优先级评分。
<!-- @AI_GENERATED: end -->

---

## 06 · 痛点评分与核心确认

文件：`process/06-pain-scoring.yaml`

字段对应标准文档 [../standards/06-pain-scoring-guide.md](../standards/06-pain-scoring-guide.md) 第 2/3/5 节。本步对 03 `pain_library`（经 05 业务化精修的同一批痛点）做**业务优先级**四维打分排序，过硬门槛锁定核心痛点池，并把 `priority_score` / `tier` 回填到 03 `pain_library`。**优先级评分 ≠ 03 的痛点根因权重**。

```yaml
step: "06-pain-scoring"
mission_critical: "<引用 02 步命题>"
weights: { value: 0.40, trend: 0.25, solvability: 0.20, verifiability: 0.15 }
scored_pain_points:
  - pain_ref: "P-1（燃料质量识别不足）"  # 代号（中文名），引用 03 pain_library（经 05 精修）
    linked_factors: ["<关联影响因子（来自 03/04）>"]
    scores: { value: 10, trend: 10, solvability: 6, verifiability: 10 }  # 每维 10/8/6/4/2
    weighted_score: 9.2        # = 10*0.4 + 10*0.25 + 6*0.2 + 10*0.15（满分10）→ 回填 pain_library.priority_score
    business_context: "<落点：业务情境/作业环节>"
    conclusion: "core"         # core | strategic_background | excluded → 回填 pain_library.tier
core_pain_pool:
  - pain_ref: "P-1（燃料质量识别不足）"
    tier: "core"               # core（本轮主攻）| strategic_background（保留观察）
    weighted_score: 9.2
    note: "<降级原因等，如：可验证性<6，缺 baseline>"
gates:
  ranking: "<按加权总分排序结论>"
  hard_gates: "<可解决性≥3 / 可验证性≥3否则降级 / 能落到业务情境 的校验结论>"
  not_root_cause_weight: "<确认本步是业务优先级评分，未与 03 痛点根因权重混用>"
status: "complete"             # complete | in_progress | blocked
```

**字段要点：**

- `scored_pain_points[].pain_ref` 引用 03 `pain_library` 的 `pain_id`（带中文名），**不新造痛点**；评分对象是 05 精修后的同一批痛点。
- `weighted_score` 必须等于四维按 40/25/20/15 的加权和（每维取 10/8/6/4/2，满分 10）；结果回填 `pain_library.priority_score`，`conclusion`/`tier` 回填 `pain_library.tier`。
- 硬门槛：可解决性<6 → `excluded`；可验证性<6 → `strategic_background`（不进核心池）；核心池原则上取加权前 3-5 且过门槛者。
- **业务优先级 ≠ 根因贡献**：本步是跨痛点的业务重要性排序；03 的 `pain_weight` 是某影响因子内的根因贡献占比，两者不可混用。
- 下游第 7 步大痛点组合直接读取本文件的 `core_pain_pool`（按 `代号（中文名）` 引用）。

---

## 07 · 大痛点组合

文件：`process/07-pain-cluster.yaml`

字段对应标准文档 [../standards/07-pain-cluster-guide.md](../standards/07-pain-cluster-guide.md) 第 2/3 节。本步把 `06-pain-scoring.yaml` 的核心痛点（tier=core）按经营逻辑聚成 2-3 个大痛点。

```yaml
step: "07-pain-cluster"
mission_critical: "<引用 02 步命题>"
big_pains:
  - id: "BP-1"
    name: "<一句话经营问题 + 价值空间，非技术模块名>"
    member_pains: ["P-1（燃料质量识别不足）", "P-3（人工经验偏差）"]   # 引用 06 核心池（= 03 pain_library 同 id），带中文名
    supporting_factors:
      - "<支撑该大痛点的影响因子（来自 03/04）>"
    value_contribution: "<对哪类经营结果、量级或方向>"
  - id: "BP-2"
    name: "<...>"
    member_pains: ["P-2（含氧量调节滞后）", "P-5（…）"]
    supporting_factors: ["<...>"]
    value_contribution: "<...>"
strategic_background_notes:
  - pain_ref: "<来自 06 的 strategic_background 痛点：代号（中文名）>"
    reason: "<为何暂不进主叙事，如：可验证性<6、缺 baseline>"
    promote_trigger: "<升入主叙事的触发条件，如：补齐复制 capex/标准化占比数据>"
gates:
  business_problem_oriented: "<是否按经营问题而非技术模块组合、无'缺XX系统'>"
  traceability: "<每个大痛点是否可追到≥1核心痛点+影响因子>"
  serves_decision: "<是否能支撑投入取舍决策>"
status: "complete"             # complete | in_progress | blocked
```

**字段要点：**

- `big_pains` 控制在 2-3 个；`name` 必须是"经营问题 + 价值空间"句式，不得是技术模块名。
- `member_pains` 必须引用 06 核心池中 `tier: core` 的痛点（= 03 `pain_library` 同 id），写「代号（中文名）」，保证可回溯。
- 第 6 步降级的 `strategic_background` 痛点只进 `strategic_background_notes`，不进 `big_pains`。
- 下游第 8 步关键场景识别在每个大痛点下展开（大痛点不限制后续场景数量）。

---

## 08 · 关键场景

文件：`process/08-scenario.yaml`

字段对应标准文档 [../standards/08-scenario-guide.md](../standards/08-scenario-guide.md) 第 1/3/5 节。本步**承接 03 已起草的 AI 场景**（按 `scenario_id` 深化机制、可行性与 value_status，并**回写 03 的 scenario_id**），并在 `07-pain-cluster.yaml` 的 big_pains 下补齐/筛选场景，经 5 门槛。

```yaml
step: "08-scenario"
mission_critical: "<引用 02 步命题>"
length: "5min"                        # 3min | 5min | 10min | 10min+，决定场景数量目标
scenario_count_target: "5-6"         # 3min→3-4 / 5min→5-6 / 10min→6-8
scenarios:
  - id: "SC-1"                        # 沿用 03 value-tree 的 scenario_id（回写深化，不另起编号）
    from_value_tree: true            # true=承接 03 起草的场景；false=本步新增场景
    name: "<AI 场景名，承接 03，可细化>"
    linked_big_pain: "BP-1"
    linked_pains: ["P-1（燃料质量识别不足）"]   # 引用 03 pain_library 同 id，带中文名
    impact_factors: ["<改善的影响因子（来自 03/04）>"]
    ai_mechanism: "<深化 03：用什么数据 → 识别什么模式 → 预测/优化/推荐 → 闭环到业务动作>"
    business_action: "<形成闭环的可执行动作>"
    closed_loop: ["<预测>", "<决策>", "<动作>", "<反馈>"]   # 业务动作闭环节点，供第 9 步段二/交付节点化绘制
    feasibility:
      controllability: true          # 客户可控性
      data_availability: true        # 数据可得、可持续、可合法使用
      optimization_space: true       # 存在实际优化空间
      closed_loop: true              # 能从预测/分析走到动作
      value_quantifiable: true       # 能建 baseline / 收益口径
    value_status: "ready"            # ready=baseline数值已存在+收益口径清晰 | to_verify=baseline待建/待调研（机制成熟也算）
excluded_scenarios:
  - scenario: "<被排除/降级的场景或方向>"
    handling: "excluded"             # excluded | downgraded | precondition | assist_only
    reason: "<排除/降级原因>"
    methodology_category: "<数据可得性不足 / 优化空间不足 / 客户可控性弱 / 客户决策权不足 / 政府定价 / 已有能力重复 / 业务闭环不足>"
gates:
  feasibility_summary: "<5 门槛筛选结论>"
  count_check: "<保留场景数 vs --length 目标；不足下限的说明>"
  scenario_id_writeback: "<是否沿用并回写 03 的 scenario_id，未另起编号>"
status: "complete"                    # complete | in_progress | blocked
```

**字段要点：**

- **承接并回写 03**：场景 `id` 沿用 03 `scenarios.scenario_id`（`from_value_tree: true`），本步深化 `ai_mechanism` / 可行性 / `value_status`，回写同一 id；本步可新增 03 未覆盖的场景（`from_value_tree: false`）。
- 每个场景必须可回溯：`linked_big_pain`（07）→ `linked_pains`（03 pain_library 同 id，带中文名）→ `impact_factors`（03/04）。
- `name` 是 AI 场景（落到 AI 解决方案），**不是泛业务动作、也不是系统/平台名**。
- `value_status: to_verify` 的场景交给第 9 步补 baseline / 收益口径后再量化。
- `excluded_scenarios` 必须留痕原因与方法论归类，供复盘与对客户说明。
- 下游第 9 步价值量化直接读取本文件的 `scenarios`。

---

## 09 · 价值量化

文件：`process/09-valuation.yaml`

字段对应标准文档 [../standards/09-valuation-guide.md](../standards/09-valuation-guide.md)。本步对 `08-scenario.yaml` 保留场景逐个建立测算逻辑，回溯 `04-kpi-factor.yaml` 的 `impact_factor_readiness` 取 baseline，按 ready/to_verify 出金额或框架并分账汇总。每个场景按**两段式内容**组织（供交付分页）：段一=假设/基准/口径；段二=机制/闭环/关键指标及单位/价值提升测算。**价值提升测算优先用企业基准，无企业数据再用行业基准或显式假设**。

```yaml
step: "09-valuation"
mission_critical: "<引用 02 步命题>"
length: "5min"                          # 3min | 5min | 10min | 10min+，决定测算深度
valuations:
  - scenario_id: "SC-1"                 # 引自 08 的 scenarios.id（= 03 scenario_id）
    name: "<场景名（AI 场景）>"
    # ── 段一 · 假设 / 基准 / 口径 ──
    caliber: "cost_saving"              # cost_saving | revenue_uplift（与价值树同口径）
    unit: "<关键指标单位，如 元/吨、g/kWh、%>"
    scope: "<主体范围：集团 / 单厂 / 单园区 / 行业平均>"
    period: "<时间口径，如 元/年、FY2025>"
    impact_factor: "<对应影响因子（来自 08/03；带单位）>"
    baseline: "<基准数值，或 '待确认'>"
    baseline_tier: "enterprise"         # enterprise（企业基准·最优先）| industry（行业基准）| assumption（显式假设）
    baseline_source: "<来源：04 impact_factor_readiness 的 data_source / 行业报告 / 假设说明>"
    assumptions:
      - param: "可改善比例"
        value: "<如 8%>"
        data_type: "internal_assumption"  # client_real | industry_public | internal_assumption | analogy
        note: "<口径/来源>"
    # ── 段二 · 机制 / 闭环 / 关键指标及单位 / 价值提升测算 ──
    ai_mechanism: "<承接 03/08：用什么数据 → 识别什么 → 预测/优化/推荐 → 如何闭环到业务动作>"
    closed_loop: ["<预测>", "<决策>", "<动作>", "<反馈>"]   # 业务动作闭环节点（供节点化绘制）
    key_indicators:
      - factor: "<关键指标/影响因子>"
        unit: "<单位>"
    formula: "Baseline × 可改善比例 × 可兑现比例"   # 或 业务量 × 单位价差/成本差 × 捕捉率
    estimated_value: ""                  # ready 给区间(如 800万-1200万元/年)；framework_only 留空
    scenarios_band:                      # 仅 10min/10min+ 给三情景；否则留空
      conservative: ""
      neutral: ""
      optimistic: ""
    # ── 状态与回填 ──
    value_status: "to_verify"            # 引自 08；用户在检查点回填后可 to_verify → ready
    result_type: "framework_only"        # quantified（出区间）| framework_only（只出框架）
    counts_in_rollup: false              # ready/quantified=true 计入总额；to_verify=false
    content_completeness: "page1_full + page2_mechanism_only"  # ready→page1_full+page2_full；to_verify→段一+机制，测算待回填
    to_confirm:                          # 缺哪条 baseline/参数，供检查点逐条索要
      - "<缺失的 baseline / 关键参数>"
    promotable_to_ready: true            # 回填 to_confirm 即可量化升级
rollup:
  business_case_value: "<Σ ready/quantified 场景区间>"
  potential_pool:                        # to_verify 场景，不计入总额
    - scenario_id: "SC-1"
      note: "<回填 X 后可贡献 Y 量级>"
  basis: "<只加总 ready/quantified 的说明>"
gates:
  data_honesty: "<ready 出金额 / to_verify 只出框架 / 类比不承诺 / 未擅自填 baseline 的校验>"
  assumption_traceability: "<每条假设是否标了 data_type 与来源>"
  baseline_priority: "<价值提升是否优先用企业基准(enterprise)；无则行业(industry)/显式假设(assumption)，且 baseline_tier 已标注>"
  two_segment_complete: "<每个 ready 场景是否齐备段一(假设/基准/口径)+段二(机制/闭环/关键指标及单位/测算)；to_verify 至少齐段一+机制>"
data_gaps:
  - "<汇总层面的整体数据缺口>"
status: "complete"                       # complete | in_progress | blocked
```

**字段要点：**

- **两段式内容**：每个场景按 段一（假设/基准/口径）+ 段二（机制/闭环/关键指标及单位/价值提升测算）组织；`content_completeness` 标完整度——`ready` 两段齐全，`to_verify` 至少段一 + 机制、测算标"待回填"。
- **基准优先级（硬规则）**：价值提升测算 baseline 取数优先级 = 企业基准（`enterprise`/client_real）> 行业基准（`industry`/industry_public）> 显式假设（`assumption`/internal_assumption）；用了行业/假设档必须在 `baseline_tier` 标注，并在交付页脚标"参考同业 / 基于假设"。
- `value_status` 引自 08（严格口径）；只有 `ready` 才出 `estimated_value` 区间（`result_type: quantified`），`to_verify` 一律 `framework_only` 不出确定金额。
- 每条 `assumptions[].data_type` 必填，标清是客户真实 / 行业公开 / 内部假设 / 类比；类比不得作承诺。
- 汇总分账：`rollup.business_case_value` 只加 `counts_in_rollup: true`（ready/quantified）的场景；`to_verify` 进 `potential_pool`，不计入总额。
- 数据回填升级：用户在检查点回填 `to_confirm` 后，将该场景 `value_status→ready`、`result_type→quantified`、补 `estimated_value`、`counts_in_rollup→true`，并把它从 `potential_pool` 移入 `business_case_value`。
- 下游第 10 步实施路径按本文件的价值量级与可行性排优先级。

---

<!-- @AI_GENERATED -->
## 10 · 技术架构（Ontology）

文件：`process/10-ontology.yaml`

字段对应标准文档 [../standards/10-ontology-guide.md](../standards/10-ontology-guide.md)。**本步可选**：把前序数据/价值方向/关键 AI 场景/价值口径翻译成一张横向分层、自下而上四层的 **AI 技术架构（Ontology）**：数据来源层 → Ontology 本体层（存在论/认识论/实践论三框）→ Agent Skill 层 → Agent 行动主体层。所有内容按案例生成、可回溯前序，不套固定行业模板。

```yaml
step: "10-ontology"
client: "<客户/分析对象>"
industry: "<客户行业>"
architecture_title: "<一句话论点式标题（客户语言，不含内部词）>"
data_sources:                          # 第1层·数据来源（按案例生成，不硬编码）
  - name: "<数据类，如 生产数据/交易数据/质量数据>"
    category: "<业务数据 | 外部数据 | 设备数据 | 财务数据 等>"
    source_system_or_owner: "<来源系统/台账/责任方>"
    linked_scenarios: ["SC-1"]         # 回溯步 08 场景
    data_gaps: ["<缺口，仅过程文件，不进 PPT>"]
ontology_layers:                       # 第2层·三本体框（必须保留三框）
  existence:                           # 语义关联本体层（存在论）
    name: "语义关联本体层（存在论）"
    objects: ["<业务实体/对象：资产/客户/订单/设备/产品/供应商/合同/资源 等>"]
    relationships: ["<对象间关系>"]
    attributes: ["<关键属性>"]
  cognition:                           # 态势感知本体层（认识论）
    name: "态势感知本体层（认识论）"
    state_objects: ["<状态对象：异常/趋势/绩效/风险/状态评估>"]
    diagnosis_rules: ["<识别/监测/判断/归因 规则>"]
    signals: ["<监测信号/指标>"]
  practice:                            # 仿真决策本体层（实践论）
    name: "仿真决策本体层（实践论）"
    decision_objects: ["<决策对象：计划/调度/组合/策略>"]
    simulation_logic: ["<仿真/推演逻辑>"]
    optimization_actions: ["<优化/推荐/执行 动作>"]
agent_skills:                          # 第3层·Agent Skill（按案例生成；非业务场景、非系统模块）
  - skill_name: "<能力，如 指标树装配与口径映射 / 偏差解释与量化归因>"
    description: "<解释 agent 为什么能做这件事>"
    linked_ontology_layer: "<existence | cognition | practice（可多）>"
    linked_data_sources: ["<数据来源 name>"]
    linked_scenarios: ["SC-1"]
agents:                                # 第4层·Agent 行动主体（4-6 个，对应关键 AI 场景）
  - agent_name: "<按案例行业/场景，如 采购优化工程师 / 质量分析工程师>"
    responsibility: "<负责什么决策/业务动作>"
    linked_skills: ["<skill_name>"]
    linked_scenarios: ["SC-1"]
    expected_business_action: "<期望产生的业务动作>"
side_labels:                           # 左右侧层级标签（必须保留层级逻辑）
  left: ["智能体调度与技能编排", "本体知识架构", "设备控制与数据接入"]   # 非设备密集型可改 "业务系统与数据接入"
  right: ["行动主体", "物理引擎", "知识骨架", "感知接入"]
optionality:
  enabled: true                        # 纯诊断/纯价值论证可设 false 跳过，09 → 11 直达
  skip_reason: ""
architecture_checks:
  traceability: "<agent/skill/本体/数据是否均回溯 01/03/08/09>"
  layer_consistency: "<四层自下而上是否连贯、三本体框是否齐全>"
  no_hardcoded_industry_template: "<是否按案例生成、未套死电力等固定模板>"
  ppt_readiness: "<四层+三框+左右标签可绘、直角框、无内部字段/过程词>"
checkpoint_status: "pending"           # pending | confirmed
status: "complete"                     # complete | in_progress | blocked
```

**字段要点：**

- **四层结构**：数据来源 → Ontology 本体(三框) → Agent Skill → Agent 行动主体，自下而上、可溯源。
- **三本体框必须保留**：`ontology_layers` 必含 `existence`/`cognition`/`practice`；框内按案例生成，**不写死电力行业**，每框 2-4 个对象/能力。
- **可溯源**：每个 `agents` → `agent_skills` → `ontology_layers` → `data_sources` 均回溯前序 01/03/08/09；顶层 agent 的 `linked_scenarios` 对应步 08 关键 AI 场景。
- **Agent 4-6 个**：行动主体，体现 `responsibility` 与 `expected_business_action`；空间不足优先保留最高价值场景对应的 agent。
- **Skill 边界**：是 agent 调用的能力，**不等于业务场景、不等于系统模块**；每个 skill 关联某 ontology 层。
- **左右标签保留**：`side_labels` 体现层级逻辑；非设备密集型把"设备控制与数据接入"改"业务系统与数据接入"。
- **PPT 风格**：MBB 直角框、**禁止圆角框**；`data_gaps` 与内部字段只留过程文件、不进 PPT。
- **可选性**：`optionality.enabled=false` 表示本步被跳过（纯诊断/纯价值论证），工作流由步 09 直达步 11。
- **回退**：写 `.yaml` 失败时回退 `process/10-ontology.md`，结构不变。
- 下游第 11 步实施路径把 **agent / agent skill / 数据接入** 作为可被排入四阶段建设波次的"建设对象"。
<!-- @AI_GENERATED: end -->

---

## 11 · 实施路径

文件：`process/11-roadmap.yaml`

字段对应标准文档 [../standards/11-roadmap-guide.md](../standards/11-roadmap-guide.md) 第 2/3/4/5 节。**本步可选**：把 `09-valuation.yaml` 场景按价值×就绪排波次、编排进固定四阶段并按 T0 算绝对日期。

```yaml
step: "11-roadmap"
mission_critical: "<引用 02 步命题>"
project_start: "<T0，用户提供的启动时间，如 2026-07；缺则向用户索要，试跑可假设并标注>"
hard_deadline: "<硬截止，可空>"
cadence: "quarterly"                    # annual（集团级年度）| quarterly（单一场景季度）
scenario_sequencing:                   # 价值 × 就绪 → 波次
  - scenario_id: "SC-3"                 # 引自 08/09
    value_tier: "high"                  # high | mid | low（来自第9步价值量级）
    readiness: "to_verify"             # ready | to_verify（来自第8步 value_status）
    wave: "wave1"                       # wave1（阶段3首批）| wave2 | wave3（阶段4）
    rationale: "<排序理由：如数据可得最快、缺数据底座需排后等>"
phases:                                # 固定 4 个，不随 --length 增减
  - id: "P1"
    name: "需求摸排与场景定标"
    duration: "2-4周"
    window: "<绝对日期区间，由 T0+周期算出，如 2026-07>"
    goal: "<阶段目标>"
    key_actions: ["<关键动作>"]
    deliverables: ["<交付物>"]
    scenarios: ["<本阶段涉及场景或前置>"]
    milestones: ["<里程碑>"]
  - id: "P2"                            # 数据汇聚与本体构建（2-3个月）——回填第9步 to_confirm
  - id: "P3"                            # 高价值场景与智能体上线（3-6个月）——wave1 首批
  - id: "P4"                            # 稳定运营与复制扩展（6-12个月及以后）
build_boundary:
  hq_unified: "<总部统建：数据底座/本体/模型/平台>"
  regional_adapt: "<区域适配：电价/补贴/资源禀赋参数化>"
  onsite_exec: "<现场执行：配方/调度/设备操作>"
dependencies_risks:
  - item: "<依赖或风险>"
    type: "dependency"                 # dependency | risk
    mitigation: "<缓解措施>"
benchmark_refs:                        # PPT 时间参考映射（可空）
  - material: "AI+燃煤 Value Based"
    mapping: "<原始时间表达 → 阶段映射>"
gates:
  date_feasibility: "<绝对日期是否基于 T0、节奏是否现实>"
  sequencing_logic: "<缺数据场景未被排进首批波次的校验>"
status: "complete"                     # complete | in_progress | blocked
```

**字段要点：**

- `phases` 固定 4 个；`--length` 只影响每阶段铺开的场景数量与详略，不增减阶段。
- `project_start` 为绝对日期编排的前提；缺 T0 时 `status` 应为 `in_progress` 并在检查点索要（试跑可假设并显式标注）。
- `scenario_sequencing`：缺数据底座的高价值场景（`readiness: to_verify`）**不得**排进 `wave1`；其前置（数据/MRV/基线）落在 `P2`。
- 闭环：`P2` 的 `key_actions` 应显式回填第 9 步 `to_confirm`，回填后对应场景价值由潜在池升入 Business Case 总价值。
- 下游为工作流收尾：交付物组装（按 `--format`）与后续步骤建议。

<!-- @AI_GENERATED -->
# 步骤 05 · 痛点业务化精修

步骤 03 已在每棵树的 `pain_library` 里建立了**痛点全局唯一定义**（一条痛点一个 id + 中文名 + 根因句式）。本步**不新建痛点**，核心任务是对这同一批痛点做**业务化精修与合规校验**：过反模式闸门（非"缺系统/平台"）、因果闭环到七类经营结果，并在**同一 `pain_id`** 上回填 `business_consequence` / `outcome_type` / `anti_pattern_ok`。引用痛点一律写「代号（中文名）」。

判定标准（核心原则、标准公式、反模式红线、示例与模板）见 [../standards/05-pain-point-guide.md](../standards/05-pain-point-guide.md)。本文件只讲「在工作流里怎么执行这一步」。

---

## 输入

- `process/03-value-tree.yaml`（各树 `pain_library` 的痛点定义 + `impact_factors` 上的 `pain_contributions`）
- `process/02-critical-mission.yaml`（命题，用于校准痛点是否对齐经营主线，可选参考）

## 输出

- `process/05-pain-point.yaml` — 精修后的痛点清单 `refined_pains`（同 id，带中文名），并回填 03 `pain_library`（模板见 [../templates/yaml-formats.md](../templates/yaml-formats.md)）
- `05-pain-point.md` — 可读文档，使用 guide 第 5 节输出模板

每条痛点需带：`pain_ref`(代号（中文名），引用 03)、`affected_factors`、`business_context`、`kpi_degradation`、`refined_statement`、`outcome_type`、`business_consequence`、`anti_pattern_ok`、`merged_from`(如有合并)。

## 执行流程与内部强管控

```
Task Progress:
- [ ] 1. 读取痛点：遍历 03 各树 pain_library 的痛点（按 代号（中文名） 引用），不新建痛点。
- [ ] 2. 业务化精修：对每条痛点套用标准句式打磨——「在【业务情境】中，由于【影响因子】存在【缺陷】，导致【影响因子/价值方向】【负面状态】，进而影响【七类经营结果之一】」。
- [ ] 3. ⛔ 反模式词汇拦截 (Gate 1)：若含「缺乏 XX 系统/平台/工具/能力」「没有 XX 系统」等字眼，重写；标 anti_pattern_ok。
- [ ] 4. ⛔ 因果闭环拦截 (Gate 2)：痛点后半句必须指向七类经营结果中某一类的具体经营代价，否则重构；回填 business_consequence / outcome_type。
- [ ] 5. 去重合并：03 出现实质重复的痛点可合并为一个 id，用 merged_from 留痕（合并后仍是一个 id）。
- [ ] 6. 渲染输出：生成 Markdown 痛点清单 + 写 yaml，并把 business_consequence/outcome_type/anti_pattern_ok 回填 03 pain_library。
```

> 边界：本步只做**痛点业务化（定性精修）**，**不打优先级分**（优先级在第 6 步），也**不改 03 的痛点根因权重**（那是某影响因子内的归因占比）。

---

## 用户检查点 ★ (本步骤结束前的必须动作)

> ⛔ 硬闸门：本检查点为交付红线级约束，执行契约（五环节 / STOP 模板 / 恢复口令 / 批量跳过）以 [../standards/checkpoint-protocol.md](../standards/checkpoint-protocol.md) 为准。

在输出精修后的痛点清单后，Agent **必须停止、等待用户确认**，未获用户确认**不得写入下一步文件**（禁止自问自答）。停止时按 STOP 模板抛出以下确认话术：

> "这是对价值树痛点的业务化精修。请审核：
> 1. 这些痛点是否完全排除了'缺系统/缺平台'的表述陷阱？
> 2. 指出的业务代价是否足以引起管理层重视？
>
> 若某条痛点'不够痛'或不符实际，请指出，我重新打磨因果链；确认后进入步骤 06（痛点优先级评分）。"

**注意**：用户明确"确认"或给修改意见前，流程强制暂停。

## 单 agent / 多 agent 两种跑法

- **单 agent（基线，全平台可跑）**：当前 agent 顺序走完 6 步，过双闸门（反模式 + 因果闭环），写 yaml + md，呈现检查点。
- **多 agent（探测到能力时）**：PL 派一个「Pain Point Expert」对 03 痛点做业务化精修；Partner 用反模式红线 + 因果闭环双闸门复核。协调统一经 PL（hub-and-spoke）。

## 与上下游的衔接

- **上游**：步 03 提供痛点全局定义（`pain_library`，含根因权重）；本步精修同一批痛点、不新建。
- **下游**：步 06 **痛点优先级评分**——对本步精修后的同一批痛点（同 id）做四维业务优先级打分；**与 03 的痛点根因权重不同，不可混用**。（注：大痛点组合在第 7 步、关键场景深化在第 8 步；本步不做场景立项、不映射解决方案。）
<!-- @AI_GENERATED: end -->

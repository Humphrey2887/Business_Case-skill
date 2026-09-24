<!-- @AI_GENERATED -->
# Bugfix Requirements Document

## Introduction

在使用 business-case / 远景智能咨询 skill 从母版模板（`templates/pptx/masters/envision-china-template-2023.pptx`）出片时，长期存在**生成的 PPT 未按母版/模板样式生成**的问题：封面页与内容页所套用的版式/样式并非母版中预期的模板页样式，导致成片偏离远景母版视觉规范。

根因在于当前工具指引仅有"仅封面（P1）用母版 cover 版式"这类**非强制、非确定性**的约定，缺少把**每一页都绑定到具名模板节（section）**的强制机制——生成时对"某一页该用哪张模板页样式"的选择是发散的、依赖临场判断的，因而经常选偏。

本次修复通过将 PPT 模板**精简为三页并划分为两个具名节**来消除这种不确定性：
- 第一页所在的节命名为 **cover**；
- 第二、三页所在的节命名为 **content**。

生成时强制：**封面页一律套用 cover 节下的模板页样式；内容页一律套用 content 节下的模板页样式**，使样式选择变为确定性（deterministic），从而保证成片始终遵循母版模板样式。

## Bug Analysis

### Current Behavior (Defect)

当前生成过程中，页面到模板样式的映射是非确定性的，导致成片偏离母版：

1.1 WHEN 生成一张封面页 THEN 系统可能套用非 cover 节的模板页样式（未确定性地绑定到 cover 节模板页），导致封面样式偏离母版预期
1.2 WHEN 生成一张内容页 THEN 系统可能套用非 content 节的模板页样式（如误用封面版式或母版内其它非预期版式），导致内容页样式偏离母版预期
1.3 WHEN 存在多张同类型页面（多张内容页）THEN 系统对样式来源的选择不稳定，同类页面之间样式不一致
1.4 WHEN 生成完成 THEN 成片中出现未遵循母版模板样式的页面，且缺少一个确定性规则可据以判定"这一页样式来源是否正确"

### Expected Behavior (Correct)

修复后，页面到模板节样式的映射是确定性的：

2.1 WHEN 生成一张封面页 THEN 系统 SHALL 一律套用 **cover 节**下的模板页样式
2.2 WHEN 生成一张内容页 THEN 系统 SHALL 一律套用 **content 节**下的模板页样式
2.3 WHEN 存在多张同类型页面（多张内容页）THEN 系统 SHALL 对所有内容页套用同一个 content 节模板页样式来源，保证同类页面样式一致
2.4 WHEN 生成完成 THEN 成片中每一页 SHALL 可依据其角色（封面/内容）确定性地追溯到其模板节样式来源（cover → cover 节；content → content 节），不存在样式来源不明或偏离母版的页面

### Unchanged Behavior (Regression Prevention)

以下既有行为在修复后必须保持不变：

3.1 WHEN 页面为封面且已正确绑定 cover 节模板页 THEN 系统 SHALL CONTINUE TO 把真实客户名/项目标题/日期填入 cover 版式自带的标题/副标题占位符，而非另建浮动文本框（保留封面占位符填充强制约束）
3.2 WHEN 生成任意页面文本 THEN 系统 SHALL CONTINUE TO 只用母版动态取色取字，并对中英混排做 run 级中英字体分设（保留 CJK 取字绑定约束）
3.3 WHEN 生成任意框/节点/卡片 THEN 系统 SHALL CONTINUE TO 使用直角框（禁止圆角框）并遵循母版硬约束与固定版式规格
3.4 WHEN 出片前执行残留占位符检查 THEN 系统 SHALL CONTINUE TO 以 grep 强制门槛（含 `Cover Page Style` 等）阻断未清零占位符的成功声明
3.5 WHEN 内容页需要呈现价值树/等式 THEN 系统 SHALL CONTINUE TO 执行节点化绘制与生成环节强制校验（等式逐项独立直角框、单父树、保留运算符与父子关系）

## Bug Condition & Properties

### Bug Condition Function

识别触发 bug 的输入——即"某一页的样式来源与其角色所对应的模板节不一致"：

```pascal
FUNCTION isBugCondition(slide)
  INPUT: slide with fields { role, styleSourceSection }
         role ∈ { COVER, CONTENT }
         styleSourceSection = 该页实际套用的模板节（或 NONE / 非模板节）
  OUTPUT: boolean

  // 期望的确定性映射
  expectedSection ← IF slide.role = COVER THEN "cover" ELSE "content"

  // 当实际样式来源不等于期望模板节时，即命中 bug
  RETURN slide.styleSourceSection ≠ expectedSection
END FUNCTION
```

### Property Specification (Fix Checking)

对所有命中 bug 条件的输入，修复后的生成过程必须把该页样式来源纠正为其角色对应的模板节：

```pascal
// Property: Fix Checking - 确定性模板节样式绑定
FOR ALL slide WHERE isBugCondition(slide) DO
  result ← generate'(slide)
  expectedSection ← IF slide.role = COVER THEN "cover" ELSE "content"
  ASSERT result.styleSourceSection = expectedSection
END FOR
```

### Preservation Goal (Preservation Checking)

对所有未命中 bug 条件的输入（样式来源本就与角色对应节一致），修复后的行为与原行为一致：

```pascal
// Property: Preservation Checking
FOR ALL slide WHERE NOT isBugCondition(slide) DO
  ASSERT generate(slide) = generate'(slide)
END FOR
```

其中 **generate** 为修复前的生成过程，**generate'** 为修复后的生成过程。
<!-- @AI_GENERATED: end -->

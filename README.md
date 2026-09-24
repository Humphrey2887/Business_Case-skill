<!-- @AI_GENERATED -->
# Business Case Builder（远景咨询 Skill · 痛点驱动十一步法）

一个面向企业客户的 **Business Case 构建 Skill**。它以"痛点驱动的十一步法"，从客户真实经营命题出发，逐层拆解到可量化的痛点与场景，最终产出能打动决策层的 **Business Case PPT（及配套 .md）**。

> 入口、路由、参数、工作流、交付红线等**权威定义在 [`SKILL.md`](SKILL.md)**。本文件只是面向使用者的总览与导航；遇到冲突一律以 `SKILL.md` 为准。

## 这个 Skill 做什么

不是把资料总结成报告，而是一套**结构化的经营价值论证方法**：

- **痛点驱动，不是技术驱动**：从客户经营命题出发，逐层拆到可量化的痛点与场景，最后才谈解决方案与价值。严禁把"缺某系统/平台/能力"当痛点。
- **公司本体优先**：先判客户公司靠什么创造价值、最大成本项、核心约束，再看上传材料落在哪个分支，不被材料牵引立题。
- **可溯源 + 数据诚实**：每条痛点/场景/价值都能沿 id 链回溯到上游；区分客户真实 / 行业公开 / 内部假设 / 类比，只有数据就绪的场景金额计入 Business Case 总额。
- **过程严谨，交付干净**：分析过程留在过程文件里，交付 PPT 只呈现给决策层看的结论叙事。

## 什么时候用

- "帮客户做一份 business case / 价值论证 PPT"
- "分析这家公司的业务痛点、梳理关键经营命题（Mission Critical）"
- "价值树拆解、场景价值量化、技术架构（Ontology）、实施路线图"
- 零碳/能碳价值论证、AI 场景价值评估

**不要触发于**：普通邮件/日程/HR 行政、纯技术架构选型、与经营价值论证无关的简单财务计算。

## 十一步工作流（导航）

01 结构化 Research · 02 Mission Critical 判断 · 03 Value Tree 拆解 · 04 影响因子数据就绪校验 · 05 痛点业务化精修 · 06 痛点评分与核心确认 · 07 大痛点组合 · 08 关键场景识别 · 09 价值量化 · 10 技术架构（Ontology，可选）· 11 实施路径（可选）。

- 每步执行前先读该步的 `workflows/business-pain-point/steps/0N-*.md`（怎么做）+ `standards/0N-*-guide.md`（判定标准），**做到第 N 步才读第 N 步那一对文件（懒加载）**。
- 各步 process YAML 数据契约见 `workflows/business-pain-point/templates/yaml-formats.md`。
- **参数（`--length` / `--format` / `--lang` / `--audience`）、深度档位、交付红线、12 页 PPT 映射等完整规范以 [`SKILL.md`](SKILL.md) 与 `standards/ppt-deck-mapping.md` 为权威**，此处不复述以免漂移。

## 运行前置条件（环境依赖）

方法论本体是纯 Markdown/YAML，无需运行环境即可阅读与推进；只有**交付物渲染**与**取色/看图**这几处才需要工具链。各工具的详细依赖以其自身文档为准：

| 用途 | 依赖 | 说明 |
|------|------|------|
| 动态取色 | Python 3.x（标准库） | `scripts/extract_theme_colors.py`，无第三方依赖。Windows 上若 `python` 不在 PATH，用 `py` 启动。 |
| PPTX 生成 | 见 `deliverable-tools/pptx/pptx-tool.md` | 需 `markitdown`（`python -m markitdown`）及 Node 侧 pptxgenjs/docx 等，具体以该文档为准。 |
| Word 生成 | 见 `deliverable-tools/docx/docx-tool.md` | 需 Node 的 docx-js（`npm install -g docx`），并依赖 pandoc / LibreOffice(`soffice`) / poppler(`pdftoppm`) 等系统工具。 |
| HTML slides | 无 | `deliverable-tools/frontend-slides/`，零依赖单 HTML。 |
| 本地看图（可选） | `mcp` + `Pillow` | `deliverable-tools/image-mcp/`，由 Kiro 通过 `.kiro/settings/mcp.json` 自动拉起，详见该目录 README。 |

> 收资清单能力（步 01）不依赖任何脚本或工具链：内部台账为 YAML，收资项在检查点口头/内联告知客户。

## 产物落盘

```
md_result/<project>/
├── process/0N-*.yaml      # 各步结构化产物（单一事实源）
└── 0N-*.md                # 各步可读中间稿
ppt_result/<project>/
├── <deck>.pptx            # 最终 Business Case PPT
└── <deck>.md              # 与 PPT 同名的配套交付 .md（面向客户成稿）
```

每一步：读当前步那一对文件 → 读上游 `process/` 文件作输入 → 执行流程过校验闸门 → 写 `process/0N-*.yaml`（失败回退 `.md`）→ 同步产出 `0N-*.md` 可读稿 → ★ 用户检查点确认后再进入下一步。

## 目录结构

```
envision_consulting_skill/
├── SKILL.md                       # 主 Skill 定义（入口与路由 · 权威）
├── README.md                      # 本文件（总览与导航）
├── scripts/
│   └── extract_theme_colors.py    # 从母版动态取色
├── workflows/business-pain-point/
│   ├── steps/01..11-*.md          # 每步"怎么做"（执行流程 + 检查点）
│   ├── standards/01..11-*-guide.md# 每步"判定标准/闸门/红线/模板"
│   ├── standards/ppt-deck-mapping.md  # 十一步产物 → 12 页 PPT 映射标准
│   └── templates/yaml-formats.md  # 各步 process YAML 数据契约
├── templates/
│   ├── brand-spec.md / README.md
│   ├── pptx/{masters,references}  # PPT 母版 + 参考样例
│   └── docx/{masters,references}
├── deliverable-tools/
│   ├── pptx/                       # PowerPoint 生成
│   ├── docx/                       # Word 生成
│   ├── frontend-slides/            # HTML slides
│   └── image-mcp/                  # 本地图片读取 MCP（含 README）
├── md_result/  ppt_result/  doc_result/   # 产物输出区（含 process/ 过程文件）
└── .kiro/
    ├── settings/mcp.json
    └── specs/                      # 已有特性 spec（取色器、流程质量校验、技术架构等）
```

## 关键原则

- **做客户的思考伙伴，不做报告生成器。** 命题不成立、数据对不上时，敢于打回重做。
- **证据驱动叙事。** 讲清哪些是硬数据、哪些是推断。
- **每个图表都回答一个问题；每条结论都要"so what"。** 不指向经营决策的数据点就是噪声。
<!-- @AI_GENERATED: end -->

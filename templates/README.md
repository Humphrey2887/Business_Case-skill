# 品牌模版与优秀范例（templates/）

本目录存放**客户/公司品牌母版**与**优秀范例**，供交付阶段生成咨询报告（docx）与咨询 PPT（pptx）时套用。

> 与其它 templates 区分：
> - `workflows/business-pain-point/templates/`：过程 **YAML schema**
> - `workflows/business-pain-point/standards/ppt-deck-mapping.md`：Business Case PPT 页面映射与视觉标准
> - `deliverable-tools/`：PPTX / DOCX 等交付物生成与编辑工具说明
> - 本目录 `templates/`：**品牌母版与范例文件**（.pptx / .docx）

## 四个文件夹

| 文件夹 | 放什么 | 调用方式 |
| :-- | :-- | :-- |
| `pptx/masters/` | PPT **母版**（定义版式与品牌；封面/目录/章节为固定版式页） | 「使用 \<名称\> 母版」 |
| `pptx/references/` | PPT **优秀范例**（成品 deck，仅作风格/论证结构参考） | 「参考 \<名称\> 优秀范例」 |
| `docx/masters/` | Word 报告**母版** | 「使用 \<名称\> 母版」 |
| `docx/references/` | Word 报告**优秀范例** | 「参考 \<名称\> 优秀范例」 |

## 调用语法

生成交付物时可指定，例如：

> 「为牧原案例生成咨询 PPT，**使用 牧原 母版，参考 AI燃煤 优秀范例**」

解析规则：
- 「使用 X 母版」→ 在对应 `masters/` 按文件名（或本文件别名表）匹配 X。
- 「参考 Y 优秀范例」→ 在对应 `references/` 匹配 Y，仅借鉴风格/版面，**不照搬其数据**。
- 未指定母版 → 用默认专业风格生成，并提示"待套母版"。

## 命名约定

- 文件名用简洁可识别的名字：`<品牌或项目>-master.pptx`、`<项目>-sample.pptx`。
- 母版中**封面 / 目录 / 章节分隔**应为固定版式页；内容页样式以 [brand-spec.md](brand-spec.md) 规范为准。
- 别名表（可选）：若想用中文短名调用，在各子文件夹 README 里登记「别名 → 文件名」。

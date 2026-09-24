// @AI_GENERATED
// Generate a single-slide PPTX of the POWER FACTORS UNITY (REMS) architecture.
// Layout: dark title banner + horizontal Unity REMI AI-engine band +
// 3 VERTICAL domain columns (each: colored header strip + 3 module cards, each
// card holds its items as a 2-column chip grid) + 2 foundation bands.
// Rectangular boxes only.
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.title = "POWER FACTORS UNITY 综合架构";

const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

const CN = "Microsoft YaHei";
const INK = "2B2F38";
const INK_SOFT = "55606F";

// domain palettes (referenced from the layered reference image)
const DOMAINS = [
  {
    name: "监控控制域", code: "M&C", band: "E6F0FB", line: "5B9BD5", head: "2E6DA4",
    modules: [
      { name: "SCADA", items: ["本地 / 中央两级监控", "多协议接入 104/61850/Modbus", "全站设备监控 · 告警", "组合到设备下钻"] },
      { name: "PPC · 电站控制", items: ["有功控制 · 功率分配", "无功 / 功率因数 · 调压", "爬坡率 · 动态 setpoint", "零功率 / 零注入控制", "70+ 电网 grid code"] },
      { name: "EMS · 能量管理", items: ["日前 / 日内 / 实时调度", "辅助服务（调频）", "储能 SOC · 电池保护边界", "负价限电 · 降不平衡", "VPP 聚合 · sub-200ms"] },
    ],
  },
  {
    name: "技术资产域", code: "TAM", band: "ECE6F7", line: "9179C7", head: "6A4CA5",
    modules: [
      { name: "APM · 资产性能管理", items: ["风光储统一性能视图", "停机 / 降电 / 欠发分类", "能量损失瀑布", "期望 vs 实际 · 基线归因", "根因诊断 · 可用率产出"] },
      { name: "AI Insights · 洞察", items: ["异常摘要 · 可能原因", "优先级排序", "推荐下一步动作", "计算失败解释", "自然语言问答"] },
      { name: "FSM · 现场服务", items: ["CM + PM 工单", "200+ 风光标准任务库", "排班派工 · 技师状态", "三类仓库存 · 跨库调拨", "采购优化 · 维护 KPI"] },
    ],
  },
  {
    name: "商业资产域", code: "CAM", band: "FAF2D6", line: "E0B02E", head: "9A7B10",
    modules: [
      { name: "Asset Oversight", items: ["组合资产全景 / 中央登记", "电站到合同下钻", "合同 / 监管合规 · 审计日志", "服务商 / 收益监督", "保修 / 保险索赔 · 角色看板"] },
      { name: "Invoice Mgmt", items: ["集中发票 · 自动开票", "费率表 rate schedule", "整合公用事业账单", "付款状态监控 · 延误告警", "财务报表 · 现金流管理"] },
      { name: "Commercial Events", items: ["商业影响事件账本", "停机 / 事故 / 限电", "收益 · 电量损失影响计算", "claim · 责任方 / 合同关联", "保修 / 保险事件 · 合规追踪"] },
    ],
  },
];

// ---- helpers ----
function rect(x, y, w, h, fill, line, lw = 1.25) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line, width: lw } });
}
function chip(txt, x, y, w, h, line) {
  slide.addText(txt, {
    x, y, w, h, fill: { color: "FFFFFF" }, line: { color: line, width: 0.75 },
    fontFace: CN, fontSize: 8.5, color: INK, align: "center", valign: "middle", margin: 1,
  });
}

// ================= TITLE BANNER =================
rect(0.35, 0.2, 12.6, 0.5, "233044", "1B2432");
slide.addText(
  [
    { text: "POWER FACTORS UNITY ", options: { bold: true, fontSize: 20, color: "FFFFFF" } },
    { text: "（REMS 套件）综合架构", options: { bold: true, fontSize: 16, color: "CBD5E1" } },
  ],
  { x: 0.6, y: 0.2, w: 12.1, h: 0.5, fontFace: CN, align: "left", valign: "middle", margin: 0 }
);

// ================= UNITY REMI — HORIZONTAL AI ENGINE =================
const remiY = 0.78, remiH = 0.58;
rect(0.35, remiY, 12.6, remiH, "E3F3F1", "2A9D8F", 1.5);
slide.addText(
  [
    { text: "★ Unity REMI ", options: { bold: true, fontSize: 13, color: "1F7A6B" } },
    { text: "— 横向 AI 引擎（Sense → Predict → Act → Automate）", options: { bold: true, fontSize: 12, color: "1F7A6B" } },
    { text: "     自然语言问答 / 摘要 / 异常解释 · 归因 + 建议下一步", options: { fontSize: 10.5, color: INK_SOFT } },
  ],
  { x: 0.6, y: remiY, w: 12.1, h: remiH, fontFace: CN, align: "center", valign: "middle", margin: 0 }
);

// ================= 3 VERTICAL DOMAIN COLUMNS =================
const colTop = 1.44, colH = 4.74;
const colGap = 0.25;
const colW = (12.6 - 2 * colGap) / 3;
const startX = 0.35;

DOMAINS.forEach((d, di) => {
  const cx = startX + di * (colW + colGap);
  // column band
  rect(cx, colTop, colW, colH, d.band, d.line, 1.5);
  // colored header strip
  rect(cx + 0.12, colTop + 0.1, colW - 0.24, 0.34, d.head, d.head);
  slide.addText(
    [
      { text: d.name + "  ", options: { bold: true, fontSize: 12.5, color: "FFFFFF" } },
      { text: d.code, options: { bold: true, fontSize: 11, color: "E8EEF6" } },
    ],
    { x: cx + 0.12, y: colTop + 0.1, w: colW - 0.24, h: 0.34, fontFace: CN, align: "center", valign: "middle", margin: 0 }
  );

  // 3 module cards stacked
  const modX = cx + 0.15, modW = colW - 0.30;
  const modsTop = colTop + 0.52;
  const modsBottom = colTop + colH - 0.1;
  const moduleGap = 0.12;
  const moduleH = (modsBottom - modsTop - 2 * moduleGap) / 3;

  d.modules.forEach((m, mi) => {
    const my = modsTop + mi * (moduleH + moduleGap);
    rect(modX, my, modW, moduleH, "FFFFFF", d.line, 1);
    // module header
    slide.addText(m.name, {
      x: modX + 0.1, y: my + 0.04, w: modW - 0.2, h: 0.22, fontFace: CN, fontSize: 9.5, bold: true,
      color: d.head, align: "left", valign: "middle", margin: 0,
    });
    // items as 2-column chip grid
    const items = m.items;
    const rows = Math.ceil(items.length / 2);
    const gx = modX + 0.1, gy = my + 0.3;
    const gw = modW - 0.2, gh = moduleH - 0.38;
    const cGap = 0.08, rGap = 0.05;
    const chipW = (gw - cGap) / 2;
    const chipH = (gh - (rows - 1) * rGap) / rows;
    items.forEach((t, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const isLastAlone = i === items.length - 1 && items.length % 2 === 1;
      if (isLastAlone) {
        chip(t, gx, gy + row * (chipH + rGap), gw, chipH, d.line);
      } else {
        chip(t, gx + col * (chipW + cGap), gy + row * (chipH + rGap), chipW, chipH, d.line);
      }
    });
  });
});

// ================= FOUNDATION BANDS =================
const SLATE_LINE = "7986CB";
const f1Y = colTop + colH + 0.1; // 6.28
rect(0.35, f1Y, 12.6, 0.36, "E5E8F0", SLATE_LINE, 1.25);
slide.addText(
  [
    { text: "Unity 数据底座：", options: { bold: true, color: "3A4266" } },
    { text: "统一资产模型 / 时序 / 事件 / 损失计算 / 权限 / API", options: { color: INK } },
  ],
  { x: 0.6, y: f1Y, w: 12.1, h: 0.36, fontFace: CN, fontSize: 11, align: "center", valign: "middle", margin: 0 }
);

const f2Y = f1Y + 0.44;
rect(0.35, f2Y, 12.6, 0.44, "DDE0EA", SLATE_LINE, 1.25);
slide.addText(
  [
    { text: "现场与外部：", options: { bold: true, color: "3A4266" } },
    { text: "风光储设备 · Local SCADA/EMS/PPC        |        市场电价 · PPA 合同 · 调度指令 · 电网约束", options: { color: INK } },
  ],
  { x: 0.6, y: f2Y, w: 12.1, h: 0.44, fontFace: CN, fontSize: 11, align: "center", valign: "middle", margin: 0 }
);

pres.writeFile({ fileName: "powerfactors-architecture.pptx" }).then((f) => console.log("WROTE " + f));
// @AI_GENERATED: end

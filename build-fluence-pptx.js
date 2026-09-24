// @AI_GENERATED
// Generate a single-slide PPTX of the FLUENCE full-stack architecture,
// styled as a layered diagram (left labels + colored bands + rectangular boxes).
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.title = "FLUENCE 全栈架构";

const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

const CN = "Microsoft YaHei";

// ---- palette (referenced from the layered reference image) ----
const INK = "2B2F38";
const INK_SOFT = "55606F";
const C = {
  blue:   { band: "E6F0FB", line: "5B9BD5" },
  yellow: { band: "FAF2D6", line: "E0B02E" },
  purple: { band: "ECE6F7", line: "9179C7" },
  slate:  { band: "E5E8F0", line: "7986CB" },
  groupBlue:   "D9E8F8",
  groupYellow: "F6E9BF",
};

// ---- helpers ----
function band(x, y, w, h, c) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: c.band }, line: { color: c.line, width: 1.5 },
  });
}
function container(x, y, w, h, fillColor, lineColor) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: fillColor }, line: { color: lineColor, width: 1.25 },
  });
}
function boxText(txt, x, y, w, h, lineColor, fontSize = 11.5) {
  slide.addText(txt, {
    x, y, w, h, fill: { color: "FFFFFF" }, line: { color: lineColor, width: 1 },
    fontFace: CN, fontSize, color: INK, align: "center", valign: "middle", margin: 1,
  });
}
function caption(txt, x, y, w) {
  slide.addText(txt, {
    x, y, w, h: 0.28, fontFace: CN, fontSize: 10.5, color: INK_SOFT,
    align: "left", valign: "middle", margin: 0,
  });
}
function layerLabel(cn, en, cy) {
  slide.addText(
    [
      { text: cn, options: { bold: true, fontSize: 15, color: INK, breakLine: true } },
      { text: en, options: { fontSize: 10, color: INK_SOFT } },
    ],
    { x: 0.3, y: cy - 0.4, w: 1.65, h: 0.8, fontFace: CN, align: "right", valign: "middle", margin: 0 }
  );
}

// ================= TITLE BANNER =================
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.4, y: 0.28, w: 12.5, h: 0.72, fill: { color: "233044" }, line: { color: "1B2432", width: 1.25 },
});
slide.addText(
  [
    { text: "FLUENCE ", options: { bold: true, fontSize: 24, color: "FFFFFF" } },
    { text: "全栈架构", options: { bold: true, fontSize: 22, color: "FFFFFF", breakLine: true } },
    { text: "“硬件 + 控制 OS + 数字应用” 垂直一体（储能为核心）", options: { fontSize: 12, color: "CBD5E1" } },
  ],
  { x: 0.7, y: 0.28, w: 11.9, h: 0.72, fontFace: CN, align: "left", valign: "middle", margin: 0 }
);

// band geometry
const BX = 2.05, BW = 10.85;

// ================= LAYER 1: DIGITAL PLATFORM (yellow) =================
const L1Y = 1.08, L1H = 3.02;
band(BX, L1Y, BW, L1H, C.yellow);
layerLabel("数字平台层", "Fluence IQ", L1Y + L1H / 2);
caption("云端微服务 + API + 伙伴应用生态（含第三方系统）", BX + 0.2, L1Y + 0.1, BW - 0.4);

const cardY = 1.55, cardH = 2.05, cardW = 5.075;
const card1X = 2.25, card2X = 7.625;

const products = [
  {
    x: card1X, group: C.groupYellow, line: C.yellow.line,
    name: "Mosaic", sub: "智能竞价 / 交易", aum: "13.3 GW AUM",
    chips: ["ML 价格预测", "多市场最优竞价", "DART 日前/实时协优", "风险管理设置", "5 分钟级 intra-hour", "RL 策略持续进化"],
  },
  {
    x: card2X, group: C.groupBlue, line: C.blue.line,
    name: "Nispera", sub: "资产性能管理 APM", aum: "15.5 GW AUM",
    chips: ["实时监控", "自动报表", "AI 性能分析", "预测性维护（附加模块）", "隐藏性能问题识别", "商业 KPI 可视"],
  },
];

products.forEach((p) => {
  container(p.x, cardY, cardW, cardH, p.group, p.line);
  // header name + sub
  slide.addText(
    [
      { text: p.name + " ", options: { bold: true, fontSize: 15, color: INK } },
      { text: p.sub, options: { fontSize: 10.5, color: INK_SOFT } },
    ],
    { x: p.x + 0.15, y: cardY + 0.08, w: cardW - 1.5, h: 0.35, fontFace: CN, align: "left", valign: "middle", margin: 0 }
  );
  // AUM badge
  slide.addText(p.aum, {
    x: p.x + cardW - 1.3, y: cardY + 0.1, w: 1.15, h: 0.3,
    fill: { color: "FFFFFF" }, line: { color: p.line, width: 1 },
    fontFace: CN, fontSize: 10, bold: true, color: INK, align: "center", valign: "middle", margin: 0,
  });
  // chips grid 2 x 3
  const gx = p.x + 0.15, gy = cardY + 0.53;
  const chipW = 2.3125, chipH = 0.42, colGap = 0.15, rowGap = 0.06;
  p.chips.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    boxText(c, gx + col * (chipW + colGap), gy + row * (chipH + rowGap), chipW, chipH, p.line, 11);
  });
});

// note + dashed separator
slide.addShape(pres.shapes.LINE, {
  x: BX + 0.2, y: 3.68, w: BW - 0.4, h: 0, line: { color: C.yellow.line, width: 1, dashType: "dash" },
});
slide.addText("两大产品并列，各自闭环；平台层做数据集成，但不做跨域利润归因", {
  x: BX + 0.2, y: 3.72, w: BW - 0.4, h: 0.3, fontFace: CN, fontSize: 10.5, color: INK_SOFT,
  align: "left", valign: "middle", margin: 0,
});

// ================= LAYER 2: FLUENCE OS (purple) =================
const L2Y = 4.20, L2H = 1.15;
band(BX, L2Y, BW, L2H, C.purple);
layerLabel("控制层", "Fluence OS", L2Y + L2H / 2);
caption("储能控制操作系统 · 单站到全 fleet", BX + 0.2, L2Y + 0.06, BW - 0.4);

const l2InnerX = BX + 0.2, l2InnerW = BW - 0.4;
const os1 = ["构网 (grid forming)", "微网", "快速调频", "下垂控制", "电压支撑"];
let ow1 = (l2InnerW - 4 * 0.12) / 5;
os1.forEach((t, i) => boxText(t, l2InnerX + i * (ow1 + 0.12), L2Y + 0.44, ow1, 0.33, C.purple.line, 11));
const os2 = ["综合控制", "资产管理", "系统可视"];
let ow2 = (l2InnerW - 2 * 0.12) / 3;
os2.forEach((t, i) => boxText(t, l2InnerX + i * (ow2 + 0.12), L2Y + 0.44 + 0.39, ow2, 0.33, C.purple.line, 11));

// ================= LAYER 3: HARDWARE (blue) =================
const L3Y = 5.43, L3H = 0.82;
band(BX, L3Y, BW, L3H, C.blue);
layerLabel("硬件层", "BESS 系统集成", L3Y + L3H / 2);
caption("Fluence 储能硬件", BX + 0.2, L3Y + 0.06, BW - 0.4);

const hw = ["电池系统", "PCS 功率电子", "本地硬件", "数据中心 / 电网级方案"];
let hwW = (l2InnerW - 3 * 0.12) / 4;
hw.forEach((t, i) => boxText(t, l2InnerX + i * (hwW + 0.12), L3Y + 0.42, hwW, 0.33, C.blue.line, 11));

// ================= LAYER 4: ASSETS & MARKET (slate) =================
const L4Y = 6.33, L4H = 0.82;
band(BX, L4Y, BW, L4H, C.slate);
layerLabel("资产与市场层", "Assets & Market", L4Y + L4H / 2);
caption("发电资产（含第三方系统）· 电力市场", BX + 0.2, L4Y + 0.06, BW - 0.4);

const assets = ["储能电站", "风电", "光伏", "水电站", "第三方系统", "电力市场"];
let asW = (l2InnerW - 5 * 0.12) / 6;
assets.forEach((t, i) => boxText(t, l2InnerX + i * (asW + 0.12), L4Y + 0.42, asW, 0.33, C.slate.line, 11));

pres.writeFile({ fileName: "fluence-architecture.pptx" }).then((f) => console.log("WROTE " + f));
// @AI_GENERATED: end

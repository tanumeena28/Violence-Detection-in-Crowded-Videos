const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/sessions/modest-pensive-wozniak/mnt/.claude/skills/pptx/scripts/apply_theme.js");

const THEME = {
  name: "PoseNotPrivacy",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "11162B",
    lt1: "FFFFFF",
    dk2: "1A2347",
    lt2: "EEF1F8",
    accent1: "00A896",
    accent2: "E8552F",
    accent3: "F2A93B",
    accent4: "5B7FD4",
    accent5: "7C8AA8",
    accent6: "CADCFC",
    hlink: "00A896",
    folHlink: "7C8AA8",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Privacy Leakage and Baseline Validity in Federated Skeleton-Based Action Recognition";
pres.subject = "BTech Final Year Project Phase 1 Review";
pres.author = "Vishal Gautam";

const C = pres.SchemeColor;
const FOOT = "Privacy Leakage and Baseline Validity in Federated Skeleton-Based HAR  ·  Phase 1 Review";

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: 0.8, y: 1.25, w: 11.7, h: 0.4,
      fontSize: 14, bold: true, charSpacing: 3, color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.8, w: 11.7, h: 1.95,
      fontSize: 38, bold: true, color: C.background1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.95, w: 11.0, h: 1.0,
      fontSize: 17, color: THEME.colors.accent6, align: "left", valign: "top", margin: 0 }, text: " " } },
    { placeholder: { options: { name: "meta", type: "body", x: 0.8, y: 5.55, w: 11.0, h: 1.0,
      fontSize: 13, color: THEME.colors.accent5, align: "left", valign: "top", margin: 0 }, text: " " } },
  ],
});

pres.defineSlideMaster({
  title: "DIVIDER",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: 0.8, y: 2.6, w: 11.7, h: 0.5,
      fontSize: 15, bold: true, charSpacing: 4, color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 3.15, w: 11.7, h: 1.2,
      fontSize: 40, bold: true, color: C.background1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.4, w: 10.5, h: 0.8,
      fontSize: 16, color: THEME.colors.accent6, align: "left", valign: "top", margin: 0 }, text: " " } },
  ],
  slideNumber: { x: 12.5, y: 6.95, w: 0.5, h: 0.3, fontSize: 11, color: THEME.colors.accent5, align: "right" },
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.42, w: 12.1, h: 0.95,
      fontSize: 33, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { text: { text: FOOT, options: { x: 0.6, y: 6.98, w: 8.0, h: 0.3, fontSize: 10,
      color: THEME.colors.accent5, align: "left", valign: "middle", margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 12.3, y: 6.98, w: 0.4, h: 0.3, fontSize: 11, color: THEME.colors.accent5, align: "right" },
});

pres.defineSlideMaster({
  title: "CONTENT_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.42, w: 12.1, h: 0.95,
      fontSize: 33, bold: true, color: C.background1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { text: { text: FOOT, options: { x: 0.6, y: 6.98, w: 8.0, h: 0.3, fontSize: 10,
      color: THEME.colors.accent5, align: "left", valign: "middle", margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 12.3, y: 6.98, w: 0.4, h: 0.3, fontSize: 11, color: THEME.colors.accent5, align: "right" },
});

pres.defineSlideMaster({
  title: "TABLE_SLIDE",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.42, w: 12.1, h: 0.95,
      fontSize: 33, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: " " } },
    { placeholder: { options: { name: "tbl", type: "body", x: 0.6, y: 1.55, w: 12.1, h: 4.9,
      fontSize: 12, color: C.text1, margin: 0 }, text: " " } },
    { text: { text: FOOT, options: { x: 0.6, y: 6.98, w: 8.0, h: 0.3, fontSize: 10,
      color: THEME.colors.accent5, align: "left", valign: "middle", margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 12.3, y: 6.98, w: 0.4, h: 0.3, fontSize: 11, color: THEME.colors.accent5, align: "right" },
});

// ---------------------------------------------------------------- helpers
const roundRect = () => pres.ShapeType.roundRect;
const rect = () => pres.ShapeType.rect;
const ellipse = () => pres.ShapeType.ellipse;
const chevron = () => pres.ShapeType.chevron;
const triangle = () => pres.ShapeType.triangle;

function card(slide, x, y, w, h, fill, name) {
  slide.addShape(roundRect(), {
    x, y, w, h, rectRadius: 0.07,
    fill: { color: fill }, line: { width: 0 }, objectName: name,
  });
}

function badge(slide, x, y, d, fill, label, labelColor, name) {
  slide.addShape(ellipse(), { x, y, w: d, h: d, fill: { color: fill }, line: { width: 0 }, objectName: name });
  slide.addText(label, {
    x, y, w: d, h: d, fontSize: d > 0.5 ? 17 : 13, bold: true,
    color: labelColor, align: "center", valign: "middle", margin: 0, isTextBox: true,
  });
}

function arrowRight(slide, x, yMid, w, color, name) {
  const t = 0.032, hw = 0.15, hh = 0.2;
  slide.addShape(rect(), { x, y: yMid - t / 2, w: Math.max(w - hw, 0.02), h: t, fill: { color }, line: { width: 0 }, objectName: name + "-l" });
  slide.addShape(triangle(), { x: x + w - hw, y: yMid - hh / 2, w: hw, h: hh, rotate: 90, fill: { color }, line: { width: 0 }, objectName: name + "-h" });
}

// two horizontal stubs joined by a vertical bar, so two streams visually merge
function mergeConnector(slide, xStart, yTop, yBot, xJoin, color, name) {
  const t = 0.032;
  slide.addShape(rect(), { x: xStart, y: yTop - t / 2, w: xJoin - xStart, h: t, fill: { color }, line: { width: 0 }, objectName: name + "-s1" });
  slide.addShape(rect(), { x: xStart, y: yBot - t / 2, w: xJoin - xStart, h: t, fill: { color }, line: { width: 0 }, objectName: name + "-s2" });
  slide.addShape(rect(), { x: xJoin - t / 2, y: yTop - t / 2, w: t, h: (yBot - yTop) + t, fill: { color }, line: { width: 0 }, objectName: name + "-v" });
}

function statBlock(slide, x, y, w, big, bigColor, label, labelH) {
  slide.addText(big, { x, y, w, h: 0.9, fontSize: 52, bold: true, color: bigColor,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  slide.addText(label, { x, y: y + 0.92, w, h: labelH || 1.5, fontSize: 14, color: C.text1,
    align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
}

function bullets(slide, items, opts) {
  const runs = items.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i !== items.length - 1, paraSpaceAfter: 9 },
  }));
  slide.addText(runs, Object.assign({
    fontSize: 15, color: C.text1, align: "left", valign: "top", margin: 0, isTextBox: true,
  }, opts));
}

// ================================================================ SECTION: opening
pres.addSection({ title: "Opening" });

// ---- 1. Title
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
s.addShape(ellipse(), { x: 10.4, y: -1.5, w: 5.2, h: 5.2, fill: { color: "232E58" }, line: { width: 0 }, objectName: "glow" });
s.addShape(ellipse(), { x: 11.6, y: -0.6, w: 2.6, h: 2.6, fill: { color: THEME.colors.accent1, transparency: 72 }, line: { width: 0 }, objectName: "glow2" });
s.addText("B.TECH FINAL YEAR PROJECT  ·  PHASE 1 REVIEW", { placeholder: "eyebrow" });
s.addText([{ text: "Privacy Leakage and Baseline Validity in\nFederated Skeleton-Based Action Recognition", options: {} }], { placeholder: "title" });
s.addText("An empirical re-examination of two 2025 federated learning studies, with preliminary results on the released dataset", { placeholder: "body" });
s.addText([
  { text: "Vishal Gautam", options: { bold: true, color: THEME.colors.accent6, breakLine: true } },
  { text: "Built on three source papers: FLTA 2025  ·  ICCV Workshops 2025  ·  arXiv 2020", options: { breakLine: true } },
  { text: "October 2026", options: {} },
], { placeholder: "meta" });
s.addNotes(
`OPENING (about 60 seconds)

"Sir/Ma'am, my project is a critical re-examination of two very recent 2025 papers on federated, privacy-preserving human action recognition, plus one 2020 dataset-and-architecture paper that I use as a reference point.

Both 2025 papers claim that by discarding camera pixels and keeping only skeleton keypoints, they protect the identity of the people recorded. Neither paper runs a single experiment to verify that. I have now tested it on the dataset one of them released, and identity is recoverable well above chance. I also re-examine their accuracy claims with proper statistical reporting."

Frame it as research, not a survey. You read three papers, found four specific problems, and designed experiments to settle them.

ANTICIPATED QUESTION — "Is this just a reproduction study?"
Answer: No. There are four contributions, only one of which is replication. There is also a new architecture (C3), a privacy attack-and-defense study that neither paper attempted (C4), and an aggregation sweep the original authors explicitly listed as future work (C2).`
);

// ---- 2. The claim
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
s.addText("Principal findings", { placeholder: "title" });
card(s, 0.6, 1.75, 3.85, 3.35, THEME.colors.lt2, "c1");
card(s, 4.72, 1.75, 3.85, 3.35, THEME.colors.lt2, "c2");
card(s, 8.85, 1.75, 3.85, 3.35, THEME.colors.lt2, "c3");
statBlock(s, 0.95, 2.1, 3.2, "+12.4", THEME.colors.accent2,
  "points of accuracy P3 reports for federated over centralized training.\n\nCentralized is normally the upper bound. We assess whether this reflects a weak baseline.", 1.95);
statBlock(s, 5.07, 2.1, 3.2, "0", THEME.colors.accent2,
  "privacy experiments across both papers whose central claim is privacy.\n\nNeither lists the omission in its limitations section.", 1.95);
statBlock(s, 9.2, 2.1, 3.2, "-24 pts", THEME.colors.accent1,
  "of identity leakage removed by hip-centring, for 0.4 points of gesture accuracy.\n\nOur own result: the released skeletons leak identity, but most of it is positional.", 1.95);
s.addText("The first two are published claims; the third is a result we have already produced and present later in this review", {
  x: 0.6, y: 5.35, w: 12.1, h: 0.4, fontSize: 13, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true,
});
s.addNotes(
`THE CORE PITCH (about 2 minutes) — the most important slide in the deck.

Left — "+12.4": P3 claims federated learning BEATS centralized training. In federated learning theory, pooling all data on one machine is the upper bound you aspire to; FedAvg usually does slightly worse, especially with non-IID data. So this result is backwards, and I explain on the Gap 1 slide why I suspect their centralized baseline was weak.

Middle — "0": Both 2025 papers are built on the premise that skeletons are private. P5 calls them "anonymous" and "desensitized." Neither paper has a single table, figure, or experiment about privacy. I searched both PDFs for re-identification, membership inference, leakage, biometric, and gait. Nothing.

Right — "-24 pts": This is OUR result, not theirs. I downloaded P3's released dataset and trained a linear classifier to predict WHICH of the five subjects produced a given skeleton window. On the data as released it gets 59.3%, against 20% chance and a 26.6% majority baseline. But I then found most of that was absolute position rather than body shape — the coordinates are frame-normalised, so where someone stood is encoded. Hip-centring drops leakage to 35.2% while costing only 0.4 points of gesture accuracy.

Say clearly: "So this is no longer a proposal to test the privacy claim. I tested it, found the representation does leak, found that most of the leakage is a positional recording artifact rather than biometrics, and identified a fix that is close to free. Section 03 has the detail."

ANTICIPATED QUESTION — "Isn't it arrogant to say a published ICCV workshop paper is wrong?"
Answer: I am not claiming the papers are wrong about anything they measured. I am claiming one of their premises was never tested, and when I test it, it fails. That is normal science, and I present it with its limitations stated.`
);

// ---- 3. Roadmap
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
s.addText("Scope of this review", { placeholder: "title" });
const road = [
  ["01", "Reviewed literature", "What each of the three papers does, and the results they report", THEME.colors.accent4],
  ["02", "Identified research gaps", "Baseline validity, statistical reporting, unverified privacy, aggregation", THEME.colors.accent2],
  ["03", "Preliminary analysis", "Verification of the released dataset, and our first privacy result", THEME.colors.accent1],
  ["04", "Proposed contributions", "Four contributions, including a new architecture and a privacy audit", THEME.colors.accent1],
  ["05", "Resources and schedule", "Data, compute, the 15-day plan, and risk assessment", THEME.colors.accent3],
];
road.forEach((r, i) => {
  const y = 1.68 + i * 1.04;
  card(s, 0.6, y, 12.1, 0.9, i === 2 ? "E6F7F4" : "F7F9FD", "road" + i);
  badge(s, 0.85, y + 0.17, 0.56, r[3], r[0], "FFFFFF", "rb" + i);
  s.addText(r[1], { x: 1.62, y: y + 0.08, w: 3.5, h: 0.4, fontSize: 17, bold: true,
    color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[2], { x: 1.62, y: y + 0.45, w: 10.7, h: 0.38, fontSize: 13,
    color: THEME.colors.accent5, align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`ROADMAP (about 30 seconds) — keep this brief, it is signposting only.

"I will go through the three papers quickly, show how they fit together, then spend most of the time on the four gaps I found and what I propose to build. I will finish with resources and my 15-day plan."

If the slot is short, say: "If you want, I can jump straight to the gaps on slide 10 and the proposal on slide 16." Offering that shows you know which parts matter.`
);

// ================================================================ SECTION: papers
pres.addSection({ title: "01 Papers Studied" });

// ---- 4. Divider
s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "01 Papers Studied" });
s.addText("SECTION 01", { placeholder: "eyebrow" });
s.addText("Reviewed literature", { placeholder: "title" });
s.addText("Two 2025 federated skeleton papers, and one 2020 dataset-plus-architecture paper used as the accuracy reference", { placeholder: "body" });
s.addNotes(`Transition slide. "First, what I actually read."`);

// ---- 5. At a glance table
s = pres.addSlide({ masterName: "TABLE_SLIDE", sectionTitle: "01 Papers Studied" });
s.addText("Comparative summary of the reviewed works", { placeholder: "title" });
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, fontSize: 13, valign: "middle" } });
const lbl = (t) => ({ text: t, options: { bold: true, color: THEME.colors.dk2, fill: { color: THEME.colors.lt2 }, valign: "middle" } });
const cel = (t) => ({ text: t, options: { color: THEME.colors.dk1, valign: "middle" } });
s.addTable([
  [hdr(""), hdr("P3 — FLTA 2025"), hdr("P5 — ICCV Workshops 2025"), hdr("P7 — arXiv 2020")],
  [lbl("Task"), cel("8 industrial hand gestures"), cel("Crime vs normal (binary)"), cel("Violent vs non-violent")],
  [lbl("Input"), cel("FastPose, 13 joints, 26-dim per frame, 20-frame windows"), cel("OpenPose, 25 keypoints \u00D7 2 people, 150-dim per frame"), cel("RGB frames + dense optical flow")],
  [lbl("Model"), cel("LSTM (2\u00D7128) and Transformer encoder (4 layers, d=128)"), cel("LSTM, 2 layers, 512 hidden units"), cel("Flow Gated Network, 3D CNN, 0.27M params")],
  [lbl("Training"), cel("Centralized, local, FedAvg, FedEnsemble — 5 clients"), cel("Centralized vs FedAvg — 7 clients"), cel("Centralized only")],
  [lbl("Data"), cel("Custom, 5 subjects, 29,963 frames — public on HuggingFace"), cel("UCF-Crime subset, 496 videos, 5 classes"), cel("RWF-2000, 2,000 clips of 5 seconds")],
  [lbl("Headline"), cel("FL beats centralized by +12.4 points"), cel("AUC above 0.85 (no results table given)"), cel("87.25% accuracy")],
  [lbl("Privacy"), cel("Claimed, never measured"), cel("Claimed, never measured"), cel("Not a design goal")],
], {
  placeholder: "tbl", x: 0.6, y: 1.55, w: 12.1,
  colW: [1.35, 3.55, 3.6, 3.6], rowH: 0.6,
  fontSize: 12, fontFace: "Calibri", border: { type: "solid", color: "D8DEEC", pt: 1 },
  valign: "middle", margin: 0.08, autoPage: false,
});
s.addNotes(
`THE COMPARISON (about 90 seconds)

Walk down the rows, not across the columns. "All three do human action recognition from video. The difference is what they feed the model and how they train it."

Key observations to say out loud:
- P3 and P5 both throw away pixels and keep skeletons. P7 keeps pixels and adds optical flow.
- P3 and P5 both use federated learning. P7 is centralized.
- P7 is from 2020 but gets 87.25% with only 0.27 million parameters, which is roughly 45 times smaller than two-stream I3D at 24.6 million. That efficiency matters for my architecture contribution later.
- Bottom row is the punchline: privacy is claimed by two papers and measured by none.

ANTICIPATED QUESTION — "Why is a 2020 paper in a 2026 project?"
Answer: Two reasons. Its dataset RWF-2000 is still the cleanest balanced real-surveillance benchmark with proper anti-leakage splitting. And its flow-gating mechanism is the specific idea I am porting to skeletons in contribution C3.

ANTICIPATED QUESTION — "Why does P5 have no results table?"
Answer: I could not find one. The paper has five figures, two of which are a radar plot and a grouped bar chart, and only two numbers in the running text. That is part of gap 2.`
);

// ---- 6. P3
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 Papers Studied" });
s.addText("P3 — Federated skeleton-based action recognition", { placeholder: "title" });
s.addText("Hegiste, Goyal, Legler, Ruskowski  ·  FLTA 2025  ·  RPTU Kaiserslautern-Landau", {
  x: 0.6, y: 1.32, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: THEME.colors.accent5,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const p3flow = ["RGB-D video", "FastPose\n13 joints", "26-dim \u00D7 20\nwindows", "LSTM /\nTransformer", "8 gestures"];
p3flow.forEach((t, i) => {
  const x = 0.6 + i * 2.49;
  card(s, x, 1.82, 2.1, 0.92, i === 4 ? THEME.colors.accent4 : THEME.colors.lt2, "p3f" + i);
  s.addText(t, { x: x + 0.05, y: 1.82, w: 2.0, h: 0.92, fontSize: 12.5, bold: i === 4,
    color: i === 4 ? "FFFFFF" : C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  if (i < 4) arrowRight(s, x + 2.14, 2.28, 0.32, THEME.colors.accent5, "p3a" + i);
});
s.addText("Reported accuracy on the pooled global test set (Transformer)", {
  x: 0.6, y: 2.95, w: 6.0, h: 0.35, fontSize: 13, bold: true, color: C.text1,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const p3res = [["Centralized", "57.1%", THEME.colors.accent5], ["FedAvg", "69.5%", THEME.colors.accent4], ["FedEnsemble", "73.4%", THEME.colors.accent1]];
p3res.forEach((r, i) => {
  const y = 3.38 + i * 0.54;
  s.addText(r[0], { x: 0.6, y, w: 1.9, h: 0.48, fontSize: 13, color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  const barW = (parseFloat(r[1]) / 100) * 3.1;
  s.addShape(rect(), { x: 2.55, y: y + 0.11, w: barW, h: 0.26, fill: { color: r[2] }, line: { width: 0 }, objectName: "p3b" + i });
  s.addText(r[1], { x: 2.6 + barW, y, w: 0.9, h: 0.48, fontSize: 13, bold: true, color: r[2], align: "left", valign: "middle", margin: 0, isTextBox: true });
});
card(s, 7.1, 2.9, 5.6, 1.7, "FDEEE9", "p3warn");
s.addText("On an unseen 6th participant", { x: 7.4, y: 3.02, w: 5.0, h: 0.35, fontSize: 13, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "Centralized  11.71%", options: { bold: true, breakLine: true } },
  { text: "FedAvg  64.29%          FedEnsemble  69.98%", options: {} },
], { x: 7.4, y: 3.42, w: 5.0, h: 1.05, fontSize: 15, color: C.text1, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.3 });
card(s, 0.6, 5.25, 12.1, 1.15, THEME.colors.lt2, "p3note");
s.addText([
  { text: "Relevance as primary testbed:  ", options: { bold: true } },
  { text: "the processed per-client skeletons are published on HuggingFace, and every sample carries both an action label and a client ID. No pose extraction needed, and subject identity is available for the privacy attack.", options: {} },
], { x: 0.95, y: 5.4, w: 11.4, h: 0.85, fontSize: 14, color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`P3 WALKTHROUGH (about 2 minutes) — the most important paper for us.

The pipeline across the top: depth camera, FastPose reduces each frame to 13 joints which is 26 numbers, sliding windows of 20 frames, then either an LSTM or a Transformer, out comes one of 8 gestures like grab, stop, up, down.

Bottom-left bars: centralized 57.1%, FedAvg 69.5%, FedEnsemble 73.4%. Notice the ordering is backwards from what theory predicts.

Right box in red is the dramatic one: on a sixth participant never seen in training, the centralized model scores 11.71%, which is actually just BELOW the 12.5% you would get guessing one of eight classes, while federated gets 64%. Be precise that this number is from the unseen-participant evaluation in their Table II, not from the global test set where centralized scores 57.1%. The paper itself says the centralized model "just predicted Stop label for most of the actions." That is a collapsed model, not a fair baseline.

Bottom bar: this is why I chose this paper as my main testbed. The data is already pose-extracted and public, so I skip the expensive step, and critically every sample is tagged with which participant it came from, which is exactly what I need to attack privacy.

ANTICIPATED QUESTION — "57% accuracy seems low for 8 gestures. Is the dataset bad?"
Answer: Possibly, and that is itself worth reporting. Chance is 12.5%, so 57% is well above chance but far from deployable. One of my metrics is per-class confusion matrices, which the original paper never provides, specifically to diagnose whether certain gestures are inherently confusable or whether it is a training problem.`
);

// ---- 7. P5
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 Papers Studied" });
s.addText("P5 — Federated skeleton-based anomaly detection", { placeholder: "title" });
s.addText("Famouri, Hossain, Imteaj  ·  ICCV Workshops 2025  ·  Southern Illinois / Florida Atlantic", {
  x: 0.6, y: 1.32, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: THEME.colors.accent5,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const p5flow = ["UCF-Crime\n496 videos", "Sample at\n1 frame/sec", "OpenPose\n25 keypoints", "Max 2 people\n150-dim", "LSTM 512\nbinary"];
p5flow.forEach((t, i) => {
  const x = 0.6 + i * 2.49;
  card(s, x, 1.82, 2.1, 0.92, i === 4 ? THEME.colors.accent4 : THEME.colors.lt2, "p5f" + i);
  s.addText(t, { x: x + 0.05, y: 1.82, w: 2.0, h: 0.92, fontSize: 12.5, bold: i === 4,
    color: i === 4 ? "FFFFFF" : C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  if (i < 4) arrowRight(s, x + 2.14, 2.28, 0.32, THEME.colors.accent5, "p5a" + i);
});
card(s, 0.6, 3.05, 5.9, 3.1, THEME.colors.lt2, "p5a");
s.addText("Contributions of the paper", { x: 0.95, y: 3.2, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "First federated framework using skeletons for crime classification in surveillance",
  "7 clients under FedAvg, split at video level so no video spans two clients",
  "Explicitly ethical framing: discard pixels, keep motion",
], { x: 0.95, y: 3.65, w: 5.25, h: 2.3, fontSize: 14 });
card(s, 6.8, 3.05, 5.9, 3.1, "FDEEE9", "p5b");
s.addText("Methodological limitations", { x: 7.15, y: 3.2, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "No results table anywhere — only a radar plot and a bar chart",
  "Only two numbers in the text: AUC above 0.85, precision 0.64 to 0.72",
  "One label per whole video sequence, so a 10-minute video with a 5-second fight trains as entirely 'crime' — P5 names this weak-supervision problem in its introduction but does not adopt an MIL formulation to address it",
  "No privacy experiment despite privacy being the entire premise",
], { x: 7.15, y: 3.65, w: 5.25, h: 2.3, fontSize: 14 });
s.addNotes(
`P5 WALKTHROUGH (about 90 seconds)

Pipeline: they take 496 videos from UCF-Crime covering fighting, shooting, assault, robbery and normal. They sample one frame per second, run OpenPose, keep at most two people because most fights involve two, giving 150 numbers per frame, and feed an LSTM that outputs crime or not.

Left box, credit where due: this is genuinely the first federated skeleton framework for crime classification, the client splitting is done properly at video level to avoid leakage, and the ethical motivation is clearly argued.

Right box, the problems. The one I would emphasise: there is no results table in the entire paper. You cannot cite a number from it. On the label noise: be precise here — P5 does NOT label individual frames. It feeds the whole variable-length sequence to the LSTM, takes the last valid output, and produces one logit per video. The problem is dilution, not per-frame mislabelling: a long video containing a brief violent event trains entirely as 'crime'. P5 explicitly names this in its introduction, calling the normal frames 'noisy labels' in a weakly supervised setting, but it never adopts a multiple-instance learning formulation to handle it. Interestingly, the very paper they cite for the dataset (Sultani 2018) solved this with multiple-instance learning. P5 does not use it.

ANTICIPATED QUESTION — "Will you fix the label noise problem too?"
Answer: I scoped it out for the 15-day timeline. It was my idea number 4 — reformulate as multiple-instance learning over skeleton bags to get temporal localization. It is a good follow-up for Phase 2, but it needs the heavier UCF-Crime pose extraction and MIL training is less stable, so it did not fit the deadline.`
);

// ---- 8. P7
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 Papers Studied" });
s.addText("P7 — RWF-2000 and the Flow Gated Network", { placeholder: "title" });
s.addText("Cheng, Cai, Li  ·  arXiv 2020  ·  Duke Kunshan / Sun Yat-sen", {
  x: 0.6, y: 1.32, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: THEME.colors.accent5,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 1.8, 7.5, 3.1, THEME.colors.lt2, "p7diag");
s.addText("The gating mechanism to be adapted", { x: 0.9, y: 1.92, w: 6.9, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.9, 2.35, 2.3, 0.7, "FFFFFF", "p7rgb");
s.addText("RGB 3D-CNN\nReLU", { x: 0.9, y: 2.35, w: 2.3, h: 0.7, fontSize: 12.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.9, 3.65, 2.3, 0.7, "FFFFFF", "p7opt");
s.addText("Flow 3D-CNN\nsigmoid", { x: 0.9, y: 3.65, w: 2.3, h: 0.7, fontSize: 12.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
mergeConnector(s, 3.2, 2.70, 4.00, 3.5, THEME.colors.accent5, "p7m");
arrowRight(s, 3.52, 3.35, 0.41, THEME.colors.accent5, "p7a1");
badge(s, 3.95, 3.07, 0.56, THEME.colors.accent2, "\u00D7", "FFFFFF", "p7mul");
arrowRight(s, 4.53, 3.35, 0.3, THEME.colors.accent5, "p7a2");
card(s, 4.88, 2.95, 1.55, 0.8, "FFFFFF", "p7pool");
s.addText("temporal\nmax-pool", { x: 4.88, y: 2.95, w: 1.55, h: 0.8, fontSize: 12.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
arrowRight(s, 6.45, 3.35, 0.3, THEME.colors.accent5, "p7a3");
card(s, 6.8, 2.95, 1.15, 0.8, THEME.colors.accent4, "p7fc");
s.addText("FC\nclass", { x: 6.8, y: 2.95, w: 1.15, h: 0.8, fontSize: 12.5, bold: true, color: "FFFFFF",
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Flow output passes through a sigmoid, so it acts as a learned 0-to-1 gate on the RGB features before pooling", {
  x: 0.9, y: 4.47, w: 6.9, h: 0.32, fontSize: 11.5, italic: true, color: THEME.colors.accent5,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 8.4, 1.8, 4.3, 3.1, THEME.colors.lt2, "p7res");
s.addText("Accuracy on RWF-2000", { x: 8.7, y: 1.92, w: 3.7, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
const p7r = [["RGB only", "84.50%"], ["Flow only", "75.50%"], ["Fusion (theirs)", "87.25%"], ["I3D two-stream", "81.50%"]];
p7r.forEach((r, i) => {
  const y = 2.42 + i * 0.52;
  s.addText(r[0], { x: 8.7, y, w: 2.5, h: 0.45, fontSize: 13, bold: i === 2,
    color: i === 2 ? THEME.colors.accent1 : C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 11.2, y, w: 1.2, h: 0.45, fontSize: 13, bold: i === 2,
    color: i === 2 ? THEME.colors.accent1 : C.text1, align: "right", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("0.27M parameters vs 24.6M for two-stream I3D", { x: 8.7, y: 4.47, w: 3.7, h: 0.32, fontSize: 11.5,
  italic: true, color: THEME.colors.accent5, align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 5.25, 12.1, 1.15, "E6F7F4", "p7take");
s.addText([
  { text: "Relevance to this project:  ", options: { bold: true } },
  { text: "P7 is the non-private accuracy ceiling we measure ourselves against, and its multiplicative gating idea is what we port into the skeleton domain as contribution C3.", options: {} },
], { x: 0.95, y: 5.4, w: 11.4, h: 0.85, fontSize: 14, color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`P7 WALKTHROUGH (about 2 minutes) — spend time on the diagram, it sets up C3.

The mechanism: two parallel 3D CNN branches, one on RGB frames and one on optical flow. The RGB branch ends in ReLU so it outputs feature magnitudes. The flow branch ends in a sigmoid so it outputs values between 0 and 1. They MULTIPLY them. Where there is no motion the gate is near zero and those features get suppressed before temporal max-pooling; where there is motion the gate is near one and features survive.

Their framing: instead of a human choosing a pooling strategy, the network learns which time steps matter. That is the idea I want.

Right panel: RGB alone 84.5%, flow alone 75.5%, gated fusion 87.25%. So the gating genuinely adds about 3 points over the better single stream. And it does it with 0.27 million parameters against 24.6 million for two-stream I3D, roughly 90 times smaller.

ANTICIPATED QUESTION — "Why not just use this model directly on your problem?"
Answer: Because it needs RGB pixels, which is exactly what the privacy-preserving setting forbids. The whole tension of my project is that the accurate model needs pixels and the private model cannot have them. My C3 contribution asks whether the gating trick survives when you replace pixels with joints and optical flow with joint velocity.`
);

// ---- 9. The triangle
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "01 Papers Studied" });
s.addText("Relationship between the reviewed works", { placeholder: "title" });
card(s, 4.3, 1.75, 4.7, 1.5, "243055", "tri7");
s.addText([
  { text: "P7 — RWF-2000", options: { bold: true, color: THEME.colors.accent6, breakLine: true, fontSize: 15 } },
  { text: "Clean balanced benchmark, a published 87.25% ceiling, and the gating mechanism", options: { fontSize: 13, color: "FFFFFF" } },
], { x: 4.6, y: 1.92, w: 4.1, h: 1.2, align: "left", valign: "top", margin: 0, isTextBox: true });
card(s, 0.9, 4.1, 4.7, 1.5, "243055", "tri5");
s.addText([
  { text: "P5 — Pose to Protect", options: { bold: true, color: THEME.colors.accent6, breakLine: true, fontSize: 15 } },
  { text: "The privacy-motivated skeleton pipeline for surveillance", options: { fontSize: 13, color: "FFFFFF" } },
], { x: 1.2, y: 4.27, w: 4.1, h: 1.2, align: "left", valign: "top", margin: 0, isTextBox: true });
card(s, 7.7, 4.1, 4.7, 1.5, "243055", "tri3");
s.addText([
  { text: "P3 — Federated HAR", options: { bold: true, color: THEME.colors.accent6, breakLine: true, fontSize: 15 } },
  { text: "The four-paradigm evaluation protocol, and public labelled data", options: { fontSize: 13, color: "FFFFFF" } },
], { x: 8.0, y: 4.27, w: 4.1, h: 1.2, align: "left", valign: "top", margin: 0, isTextBox: true });
badge(s, 6.12, 3.40, 1.1, THEME.colors.accent1, "", "FFFFFF", "tricore");
s.addText("GAP", { x: 6.12, y: 3.40, w: 1.1, h: 1.1, fontSize: 15, bold: true, color: "FFFFFF",
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Neither 2025 paper combines a clean benchmark, a measured privacy claim, and a rigorous multi-paradigm protocol — though skeleton privacy itself is an established research area we must cite", {
  x: 1.5, y: 6.05, w: 10.3, h: 0.8, fontSize: 15, italic: true, color: THEME.colors.accent6,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`THE SYNTHESIS (about 60 seconds) — this is the slide that justifies combining the papers.

"Each paper supplies something the others lack.

P7 gives me a clean, balanced, properly split benchmark and a published accuracy ceiling — but it is centralized and not private at all.

P5 gives me the privacy-motivated skeleton pipeline — but on messy weakly-labelled data with no results table.

P3 gives me the rigorous evaluation protocol comparing four training paradigms plus a held-out subject — and public pre-extracted data.

Put them together and the hole in the middle is obvious: nobody has run a privacy-preserving skeleton pipeline on a clean benchmark with a rigorous protocol AND actually measured the privacy."

IMPORTANT — do not overclaim novelty here. Skeleton privacy and anonymisation is an established research area; Moon et al., "Anonymization for Skeleton Action Recognition" (AAAI 2023) studies exactly the privacy-utility trade-off, and skeleton-based violence detection on RWF-2000 already exists and reportedly exceeds P7 (SPIL, ECCV 2020, around 89%). VERIFY BOTH CITATIONS before presenting — they were flagged in review and could not be checked offline.

The correct framing is actually stronger: because prior work had already shown skeletons are not anonymous, these two 2025 papers asserting anonymity without testing it is a more serious omission, not a less interesting one.

ANTICIPATED QUESTION — "So is your contribution just combining three existing things?"
Answer: The combination is one contribution of four. The defensible novelty is narrower than "nobody has studied skeleton privacy": it is that these two specific federated papers rest on an untested premise, and that on their own released data most of the leakage turns out to be a positional recording artifact with a near-free fix.`
);

// ================================================================ SECTION: gaps
pres.addSection({ title: "02 Gaps Identified" });

// ---- 10. Divider
s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "02 Gaps Identified" });
s.addText("SECTION 02", { placeholder: "eyebrow" });
s.addText("Identified research gaps", { placeholder: "title" });
s.addText("Every gap below is traceable to a specific sentence, table or omission in the source papers", { placeholder: "body" });
s.addNotes(
`Transition. "Now the part I spent most of my reading time on.

I want to stress that each of these four is traceable to a specific sentence or a specific absence in the papers. I am not speculating about what they might have done wrong — I am pointing at what is printed and what is missing."`
);

// ---- 11. Gap 1
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 Gaps Identified" });
s.addText("Gap 1 — Baseline validity of the headline result", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent2, "1", "FFFFFF", "g1b");
s.addText("Centralized training on pooled data is the conventional upper bound for FedAvg. P3 reports the reverse.", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.62, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const ev = [
  ["Their own text", "On the unseen 6th participant (Table II, not the global test) the centralized model \"just predicted 'Stop' label for most of the actions\", scoring 11.71% — just below the 12.5% chance level for 8 classes"],
  ["Training description", "The centralized arm is described only as \"trained on this combined dataset for 500 epochs\" with no augmentation. An early-stopping patience of 15 is stated globally, but whether it applied here is ambiguous"],
  ["Budget matching", "500 epochs on pooled data and 500 local epochs on one-fifth of the data are not the same number of global gradient steps, though the paper claims the budgets are matched"],
  ["Their own ablation", "FedEnsemble takes the same pooled data, re-splits it IID, and still gains +16.3 — consistent with parameter averaging acting as a regularizer rather than with decentralization itself"],
];
ev.forEach((e, i) => {
  const y = 2.3 + i * 1.03;
  card(s, 0.6, y, 12.1, 0.92, i === 3 ? "FDEEE9" : THEME.colors.lt2, "g1c" + i);
  s.addText(e[0], { x: 0.95, y: y + 0.05, w: 2.3, h: 0.82, fontSize: 13, bold: true,
    color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(e[1], { x: 3.35, y: y + 0.05, w: 9.05, h: 0.82, fontSize: 12.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("Note in fairness: P3 designed the FedEnsemble condition deliberately to isolate the ensemble effect, and says so. We are not claiming they missed it", {
  x: 0.6, y: 6.45, w: 12.1, h: 0.4, fontSize: 12, italic: true, color: THEME.colors.accent5,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`GAP 1 (about 2.5 minutes) — the slide your professor is most likely to challenge. Know it cold.

Open with the theory: "In federated learning, if you could pool everyone's data on one server you would, because that is the best case. FedAvg is what you settle for when privacy forbids pooling, and it normally costs you a little accuracy, especially when clients have different data distributions. P3 reports federated beating centralized by 12.4 points. That is backwards, so either something important is going on, or the baseline is broken."

Then the four pieces of evidence in order. The strongest is the first: their own paper says the centralized model predicted 'Stop' for almost everything and scored 11.71% on eight classes where chance is 12.5%. A model performing at chance is not a tuned baseline, it is a failed training run.

The fourth row is subtle but important. Their FedEnsemble experiment takes the SAME pooled data, splits it into five IID shards, and runs FedAvg. There is no privacy benefit and no data difference — yet it beats centralized by 16.3 points. The only thing that changed is iterated parameter averaging. That points at averaging as a regularizer, not at federation.

CRITICAL — read the bottom line out loud. P3 explicitly designed FedEnsemble to isolate the ensemble effect and interprets it that way. I am NOT claiming I caught something they missed. What I am claiming is that their design raises the question and does not test it.

ANTICIPATED QUESTION — "Maybe federated really does regularize better. Why assume it's an artifact?"
Answer: It might, and that is exactly the experiment. If I give the centralized model dropout, weight decay and early stopping, and match gradient steps rather than epochs, and the federated advantage survives, then it is real and that is a positive finding I will report. My claim is only that it is currently untested, not that I know the answer.

ANTICIPATED QUESTION — "Have you contacted the authors?"
Answer: Not yet. Worth doing, and I can email them about whether early stopping was active on the centralized arm. Their dataset being public means I can proceed either way.`
);

// ---- 12. Gap 2
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 Gaps Identified" });
s.addText("Gap 2 — Absence of statistical reporting", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent2, "2", "FFFFFF", "g2b");
s.addText("Conclusions are drawn from 9-to-16-point differences using single training runs", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.62, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 2.3, 5.9, 2.5, THEME.colors.lt2, "g2a");
s.addText("P3", { x: 0.95, y: 2.42, w: 5.2, h: 0.4, fontSize: 18, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Single-run point estimates throughout",
  "No seeds, no standard deviations, no confidence intervals",
  "Only 5 clients with small per-client datasets, so run-to-run spread could rival the reported effect",
], { x: 0.95, y: 2.88, w: 5.25, h: 1.8, fontSize: 14 });
card(s, 6.8, 2.3, 5.9, 2.5, "FDEEE9", "g2b2");
s.addText("P5", { x: 7.15, y: 2.42, w: 5.2, h: 0.4, fontSize: 18, bold: true, color: THEME.colors.accent2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "No results table in the entire paper",
  "Only a radar plot and a grouped bar chart",
  "Two numbers in running text: AUC above 0.85, precision 0.64 to 0.72 from 3 to 5 clients",
  "No accuracy, F1 or AUC given for the headline model — nothing citable",
], { x: 7.15, y: 2.88, w: 5.25, h: 1.8, fontSize: 14 });
card(s, 0.6, 5.05, 12.1, 1.3, "E6F7F4", "g2fix");
s.addText([
  { text: "Highest value-per-hour experiment:  ", options: { bold: true } },
  { text: "three seeds of P3's federated-versus-centralized comparison. If the seed-to-seed spread approaches the claimed 12.4 points, the headline dissolves — and that costs us three training runs of a few minutes each.", options: {} },
], { x: 0.95, y: 5.2, w: 11.4, h: 1.0, fontSize: 14.5, color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`GAP 2 (about 90 seconds) — the most defensible gap. Nobody can argue against reporting variance.

"Both papers report single numbers. P3 draws conclusions from differences of 9 to 16 points without reporting any measure of run-to-run variation. With only five clients and a few thousand samples each, neural network training is noisy — different random initialisations can easily swing accuracy several points. Without error bars you cannot tell a real effect from noise."

P5 is worse. Point at the right box: no results table at all. Five figures, two of which are a radar plot and a bar chart. If I wanted to cite P5's accuracy in my related-work section, I could not, because the number does not appear.

Then the green box, which is the practical point: fixing this is nearly free. Three seeds, a few minutes each, and I either confirm their effect with error bars or I show it was noise. This is my day-2 experiment and it is the single highest value-per-hour thing in the whole project.

ANTICIPATED QUESTION — "Three seeds is not many. Shouldn't you run more?"
Answer: Agreed, three is the minimum for a standard deviation. These models are tiny — 128-dimensional hidden states over 20 time steps — so runs take seconds to a few minutes on the lab GPU. I plan three as the floor and will push to five or ten if the schedule allows, since it costs almost nothing.`
);

// ---- 13. Gap 3 (the big one, dark)
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "02 Gaps Identified" });
s.addText("Gap 3 — The privacy claim is unverified", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent2, "3", "FFFFFF", "g3b");
s.addText("The central unverified assumption of both 2025 papers", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.55, fontSize: 16, bold: true, color: THEME.colors.accent6,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 2.2, 5.9, 1.75, "243055", "g3q");
s.addText("Stated in the papers", { x: 0.95, y: 2.32, w: 5.2, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "P5 calls skeletons ", options: { color: "FFFFFF" } },
  { text: "\"anonymous\"", options: { bold: true, color: THEME.colors.accent6 } },
  { text: " and ", options: { color: "FFFFFF" } },
  { text: "\"desensitized\"", options: { bold: true, color: THEME.colors.accent6, breakLine: true } },
  { text: "P3 says sharing only weights means ", options: { color: "FFFFFF" } },
  { text: "\"preserving data privacy\"", options: { bold: true, color: THEME.colors.accent6 } },
], { x: 0.95, y: 2.75, w: 5.25, h: 1.05, fontSize: 14, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.25 });
card(s, 6.8, 2.2, 5.9, 1.75, "243055", "g3z");
s.addText("Privacy evaluation reported", { x: 7.15, y: 2.32, w: 5.2, h: 0.35, fontSize: 14, bold: true,
  color: "FFC266", align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "Nothing.", options: { bold: true, fontSize: 22, color: "FFFFFF", breakLine: true } },
  { text: "Zero privacy experiments in either paper, and neither acknowledges the omission in its limitations section", options: { fontSize: 13, color: THEME.colors.accent6 } },
], { x: 7.15, y: 2.7, w: 5.25, h: 1.1, fontSize: 14, align: "left", valign: "top", margin: 0, isTextBox: true });
const g3rows = [
  ["P3's stated limitations", "Only 5 clients  ·  FedAvg only  ·  RGB-D pose fragility"],
  ["P5's stated limitations", "OpenPose fails under occlusion, distance and low light"],
  ["But established biometrics", "Body proportions and gait identify individuals — skeletons encode both"],
  ["And the attack is available", "P3's public dataset tags every sample with one of 5 participant IDs"],
];
g3rows.forEach((r, i) => {
  const y = 4.12 + i * 0.6;
  s.addText(r[0], { x: 0.6, y, w: 3.3, h: 0.52, fontSize: 13, bold: true,
    color: i < 2 ? "A8BBDE" : THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 4.0, y, w: 8.7, h: 0.52, fontSize: 13.5,
    color: i < 2 ? THEME.colors.accent6 : "FFFFFF", align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`GAP 3 (about 2.5 minutes) — the emotional centre of the talk. Slow down here.

"This is the most important gap, and the one I have already produced a preliminary result for.

Both papers exist because of privacy. That is their entire motivation. P5's abstract calls skeleton features a 'simplified, anonymous, and efficient' representation, and the introduction says they extract 'desensitized' motion data. P3 states that because only weights and sample counts are shared, data privacy is preserved.

Neither paper runs a single privacy experiment. I searched both PDFs for re-identification, attack, membership inference, leakage, biometric, and gait. Nothing.

And this is not a case of authors flagging a known limitation they ran out of time for. P3's limitations section lists three things: client count, using only FedAvg, and pose estimation fragility. P5's discussion lists OpenPose failures under occlusion and low light. Privacy evaluation appears in neither list. The assumption is invisible to them.

Meanwhile, gait recognition is a well-established biometric field — people are identifiable from how they walk, and body proportions like limb-length ratios are stable identifying features. A skeleton sequence encodes both of those directly.

And the final line is what makes this a project rather than a complaint: P3's public dataset attaches a participant ID to every single sample. The attack is directly mountable on the exact representation they claim is private."

ANTICIPATED QUESTION — "Skeletons have no face. How can they identify anyone?"
Answer: Identity does not require a face. Gait recognition is a mature biometric field precisely because walking patterns are individual. And the skeleton encodes limb length ratios — shoulder width relative to arm length, for instance — which are anatomically stable per person. P3 normalizes by shoulder distance, which removes overall scale but not ratios between limbs.

ANTICIPATED QUESTION — "Five subjects is a tiny dataset. Does the attack mean anything?"
Answer: Honest answer: it is an existence proof, not a magnitude estimate. Five-way classification is much easier than identifying someone from a population of thousands. If I get high accuracy, I have shown leakage exists and the claim needs qualification. I cannot claim to have measured how bad it would be in deployment, and I will say that explicitly in the paper.`
);

// ---- 14. Gap 4
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 Gaps Identified" });
s.addText("Gap 4 — Limited aggregation strategy", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent3, "4", "FFFFFF", "g4b");
s.addText("P3 uses weighted FedAvg alone, and names the alternatives as future work in its own limitations section", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.62, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const aggs = [
  ["FedAvg", "Weighted average of client weights. The only rule P3 tests", THEME.colors.accent5],
  ["FedProx", "Adds a proximal term limiting client drift. Designed for non-IID data", THEME.colors.accent1],
  ["FedAdam", "Adaptive server-side optimizer instead of plain averaging", THEME.colors.accent1],
  ["FedBN", "Keeps batch-norm statistics local. Targets exactly the per-client variation P3 motivates", THEME.colors.accent1],
  ["Personalized heads", "Shared encoder, per-client classifier. Never attempted despite client heterogeneity being the paper's premise", THEME.colors.accent1],
];
aggs.forEach((a, i) => {
  const y = 2.28 + i * 0.82;
  card(s, 0.6, y, 12.1, 0.72, i === 0 ? "F2F4F9" : "E6F7F4", "g4c" + i);
  s.addText(a[0], { x: 0.95, y, w: 2.5, h: 0.72, fontSize: 15, bold: true,
    color: a[2], align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(a[1], { x: 3.5, y, w: 8.9, h: 0.72, fontSize: 13, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("P3's own Limitations section names FedProx, FedAdam, FedBN and personalized FL as future work", {
  x: 0.6, y: 6.42, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`GAP 4 (about 60 seconds) — the safest gap, because the authors invited it.

"This is the least controversial gap because P3 identifies it themselves. Their limitations section names FedProx, FedAdam, FedBN and personalized federated learning as things that may improve robustness under non-IID data. They simply did not run them.

The one I find most interesting is FedBN. P3's entire motivation is that different workers move differently — that is their non-IID story. FedBN keeps batch normalization statistics local to each client precisely to handle that kind of feature-distribution shift. It is the textbook match for their problem and it is untested.

Same for personalized heads: a shared encoder with a per-client classifier. Their framing is about client heterogeneity, yet every client gets the identical global model."

ANTICIPATED QUESTION — "Is adding known algorithms really a contribution?"
Answer: On its own it would be thin, which is why it is contribution C2 of four rather than the headline. Its value is that it tests whether P3's conclusions are specific to FedAvg or general to federated learning. If FedProx closes the centralized-versus-federated gap, that is informative about the mechanism.`
);

// ================================================================ SECTION: preliminary analysis
pres.addSection({ title: "03 Preliminary Analysis" });
const FIG = "/sessions/modest-pensive-wozniak/mnt/outputs/analysis/figs";

// ---- Divider
s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "03 Preliminary Analysis" });
s.addText("SECTION 03", { placeholder: "eyebrow" });
s.addText("Preliminary analysis of the released dataset", { placeholder: "title" });
s.addText("We have downloaded P3's published data, verified it against the paper, and produced a first privacy result", { placeholder: "body" });
s.addNotes(
`Transition — and the moment to signal that this is not just a reading exercise.

"Before proposing experiments, I downloaded the dataset P3 released and checked whether it matches what the paper describes. It mostly does, with one notable exception. And while verifying it, I was able to run a first version of the privacy attack, which produced a result I did not expect to have this early."`
);

// ---- Dataset verification + integrity finding
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Analysis" });
s.addText("Dataset verification against the paper", { placeholder: "title" });
const ver = [
  ["Frame count", "29,963 frames total across train / val / test", "Matches the paper exactly", true],
  ["Client structure", "5 clients, each with x and y files per split", "As described", true],
  ["Feature width", "26 values per frame = 13 joints × 2 coordinates", "As described", true],
  ["Subject identity", "Label files are “gesture,client_id” — identity is an explicit column", "Enables the privacy attack directly", true],
  ["Joint layout", "Recovered empirically from per-joint variance", "Wrists move most; knees and ankles near-static", true],
  ["Integrity", "centralized_x_train.txt stops at exactly 2,097,152 bytes (2 MiB) mid-row — 13,441 complete rows of 26,403", "A repaired file is also published; per-client files are intact", false],
];
ver.forEach((v, i) => {
  const y = 1.48 + i * 0.80;
  card(s, 0.6, y, 12.1, 0.72, v[3] ? "E6F7F4" : "FDEEE9", "v" + i);
  s.addText(v[0], { x: 0.95, y, w: 1.9, h: 0.74, fontSize: 13, bold: true,
    color: v[3] ? THEME.colors.accent1 : THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(v[1], { x: 3.0, y, w: 5.6, h: 0.74, fontSize: 12, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(v[2], { x: 8.75, y, w: 3.65, h: 0.74, fontSize: 11.5, italic: true,
    color: v[3] ? "4A5A7A" : THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("We cannot infer what the authors trained on. But a third party reproducing the centralized baseline from the obvious filename would train on 51% of the data — the exact arm whose collapse the headline claim depends on. We will test both files.", {
  x: 0.6, y: 6.42, w: 12.1, h: 0.34, fontSize: 11.5, italic: true, color: THEME.colors.accent2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`DATASET VERIFICATION (about 2 minutes) — shows you did real work, not just reading.

Walk the green rows quickly: frame count matches the paper's 29,963 exactly, five clients as described, 26 values per frame as described. The fourth row matters for the privacy work — the label files are comma-separated "gesture,client_id", so subject identity is not something I had to infer, it is an explicit column in the released data.

Row five: the paper lists the joints but not their order in the file, so I recovered the layout empirically by looking at mean positions and variance. Wrists move most, which is what you expect for upper-body gestures. Knees and ankles barely move and are mostly noise — that is a useful observation for the architecture work, because a quarter of the input dimensions carry almost no task signal.

Then the red row, which is the interesting find. The centralized training file stops at exactly 2,097,152 bytes, which is 2 mebibytes, and it stops in the middle of a number — no final newline. It contains 13,441 rows where the matching label file has 26,403. That is a classic upload truncation. The authors also published a repaired file with the correct 26,403 rows, so they clearly knew.

Read the bottom line carefully and do NOT overclaim. I cannot tell what they actually trained on. But anyone reproducing their centralized baseline would reach for the obviously-named file and silently train on half the data. And the centralized arm is exactly the one that collapsed to predicting "Stop". So this is a plausible mechanism for Gap 1, and I will test both files and report the difference.

ANTICIPATED QUESTION — "So are you saying their result is just a truncated file?"
Answer: No, I am saying it is a hypothesis I can now test cheaply, and that it is one of at least three candidate explanations alongside missing regularization and epoch-versus-step budget matching. I will report which one accounts for the gap.`
);

// ---- FIG 1 heterogeneity
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Analysis" });
s.addText("Measured client heterogeneity", { placeholder: "title" });
s.addImage({ path: FIG + "/fig1_heterogeneity.png", x: 0.6, y: 1.52, w: 12.1, h: 4.916 });
s.addNotes(
`CLIENT HETEROGENEITY (about 90 seconds)

This is the non-IID structure, computed from the released files rather than taken from the paper's figure.

Each cell is a client-gesture pair: the percentage of that client's frames, and the raw frame count beneath it.

Two things to point at:
- Client 5, gesture 3 ("left") has 64 frames. Client 2 has 862 for the same gesture. That is a 13-fold imbalance within one gesture class across clients.
- Client 1 devotes 23.5% of its data to "stop" while Client 3 gives it 10.8%.

Why this matters for the project: this is exactly the regime where FedProx and FedBN are supposed to help and where plain FedAvg struggles, which is Gap 4. It also means plain accuracy is a misleading metric, because a model can score well while ignoring the rare classes — hence macro-F1 and confusion matrices in my evaluation plan.

Note the caption: I confirmed the gesture names by checking them against the mean poses in the next figure, rather than assuming the alphabetical order the paper implies.`
);

// ---- FIG 2 skeletons
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Analysis" });
s.addText("The data itself: mean skeleton per gesture", { placeholder: "title" });
s.addImage({ path: FIG + "/fig2_skeletons.png", x: 0.6, y: 1.52, w: 12.1, h: 4.879 });
s.addNotes(
`THE SKELETONS (about 90 seconds) — the slide that proves you understand the data.

These are plotted directly from the released keypoints: for each gesture, the mean position of all 13 joints, with the skeleton edges drawn in. Marker size and colour show how much each joint varies.

Use them to validate the label mapping out loud: "G8 up shows a raised arm. G6 stop shows both hands lifted in front of the body. G5 right and G3 left show the arm extended to opposite sides. G7 ungrab has both arms out. So the alphabetical label ordering the paper implies is confirmed by the poses themselves — I did not have to assume it."

Then the technical observation: the dark red joints are the knees and ankles. They have high variance but it is noise, not signal — these are upper-body gestures and the lower body is both irrelevant and poorly estimated. Roughly a third of the 26 input dimensions contribute almost nothing to the task. That is a concrete motivation for my architecture work and a candidate privacy defense, because limb-length geometry in the lower body may be carrying identity while contributing nothing to gesture recognition.

ANTICIPATED QUESTION — "Could you just drop the lower-body joints?"
Answer: That is one of the defenses I plan to evaluate. It would be an ideal outcome: if dropping joints that carry no task signal also reduces identity leakage, you get privacy for free. The privacy-utility curve is designed to answer exactly that.`
);

// ---- FIG 3 leakage (the headline)
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Analysis" });
s.addText("Preliminary result: leakage is positional and removable", { placeholder: "title" });
s.addImage({ path: FIG + "/fig3_leakage.png", x: 0.6, y: 1.58, w: 12.1, h: 4.76 });
s.addNotes(
`THE HEADLINE RESULT (about 3 minutes) — slow down, and tell the correction story honestly. It is the most credible thing in the deck.

"I trained a linear classifier — multinomial logistic regression, nothing more — to predict which of the five subjects produced a given 26-by-20 skeleton window. This is the exact representation both papers call anonymous. On the data as released it identifies the subject 59.3% of the time, against 20% chance and a 26.6% majority-class baseline.

But I did not stop there, and this is the important part. I asked what the classifier was actually using. The released coordinates are frame-normalised, not body-centred, so absolute position in the image is encoded. If each participant stood in a slightly different spot, the attacker could identify them from WHERE they are rather than from their body — a recording artifact, not a biometric. I measured it: mean hip position does differ measurably between subjects.

So I re-ran the attack under increasing invariance. Subtract the hip midpoint, making it translation-invariant, and leakage falls from 59.3% to 35.2%. Also divide by shoulder width and it stays at 35.3%. Strip position out entirely and use only frame-to-frame velocity, and it drops to 23.8%, essentially chance.

So roughly two-thirds of what I first measured was positional artifact. The residual 35% still sits meaningfully above the 26.6% majority baseline, and that residue is consistent with real body geometry — I measured client 1's shoulders as visibly narrower than the others."

Then the right panel, which is the actual contribution:

"The useful finding is the trade. Hip-centring removes 24 points of identity leakage and costs 0.4 points of gesture accuracy. That is very close to free, and it is a concrete recommendation any of these pipelines could adopt tomorrow. Velocity-only is the opposite: it removes the leakage but destroys the task, dropping gesture accuracy to 16% against a 12.5% chance level, so it is not a viable defense."

Then the limitations, in your own words before anyone asks:
- One recording session per subject, so clothing, camera and body are constant. This is identity-plus-session linkage, not cross-session re-identification.
- Five-way identification is far easier than open-set identification against a large population.
- The absolute gesture accuracy here is inflated by temporal adjacency in the 88/6/6 within-block split. The comparison between representations is valid because every row is inflated identically, but do not quote 98.8% as a task result.

ANTICIPATED QUESTION — "Your first number was wrong. Why should I trust the second?"
Answer: Because I found the problem myself and the fix is a standard invariance test. The confound was positional, so I removed position in three increasingly strict ways and reported all of them. The direction a result moves when you remove a suspected confound is the evidence — and here it moved a lot, which is exactly why reporting the raw 59.3% alone would have been misleading.

ANTICIPATED QUESTION — "So is there any real privacy problem left?"
Answer: Yes, two. The residual 35% is above the majority baseline, so body geometry carries some identity. And more practically, the papers use the raw representation, in which leakage is 59.3%. The positional component is still identifying information in a deployed system even if it is not biometric.`
);

// ---- Interpretation
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "03 Preliminary Analysis" });
s.addText("What this changes about the project", { placeholder: "title" });
card(s, 0.6, 1.5, 5.9, 2.15, "243055", "int1");
s.addText("Before this result", { x: 0.95, y: 1.62, w: 5.2, h: 0.38, fontSize: 15, bold: true,
  color: "A8BBDE", align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("A proposal to test whether skeletons leak identity. The headline would have been a method and a benchmark, with the privacy question open.", {
  x: 0.95, y: 2.05, w: 5.25, h: 1.5, fontSize: 13.5, color: "FFFFFF",
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
card(s, 6.8, 1.5, 5.9, 2.15, "0F3D38", "int2");
s.addText("After this result", { x: 7.15, y: 1.62, w: 5.2, h: 0.38, fontSize: 15, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("A measured finding plus a working mitigation: leakage is largely positional, and hip-centring removes 24 points of it for 0.4 points of accuracy.", {
  x: 7.15, y: 2.05, w: 5.25, h: 1.5, fontSize: 13.5, color: "FFFFFF",
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
const impl = [
  ["Risk retired", "C4 has already produced a result, and a defense that works", THEME.colors.accent1],
  ["Scope sharpened", "C4 shifts from “does it leak” to “what kind of leakage, and what does removing it cost”", THEME.colors.accent1],
  ["New hypothesis", "The truncated centralized file gives Gap 1 a concrete, testable mechanism", THEME.colors.accent3],
  ["Corrected in review", "Two-thirds of our first 59.3% was a positional artifact. We found it, removed it, and report both numbers", "A8BBDE"],
];
impl.forEach((r, i) => {
  const y = 3.95 + i * 0.68;
  s.addText(r[0], { x: 0.6, y, w: 2.9, h: 0.6, fontSize: 13.5, bold: true, color: r[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 3.65, y, w: 9.05, h: 0.6, fontSize: 13.5, color: "FFFFFF",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`INTERPRETATION (about 90 seconds) — the "so what" slide.

"This changes the shape of the project. I came in planning to propose testing whether skeletons leak identity. I have now tested it, so the question is no longer open.

The practical consequence is that my riskiest contribution is already de-risked. On the risk slide later I had listed 'the attack may fail' as a real possibility. It did not fail, so that risk is retired and C4 is now the strongest rather than the most speculative part of the work.

It also sharpens the scope. C4 is no longer 'does the representation leak' — it is 'how much does it leak, does it scale, and what accuracy do you give up to stop it'. That is the privacy-utility curve, and it is a more useful contribution than a yes/no answer.

And the dataset inspection handed me a concrete mechanism for Gap 1 that I did not have before: a truncated centralized training file."

End on the honest line. Do not let the last word be the strong claim; let it be the limitation. It builds far more credibility with an examiner.`
);

// ================================================================ SECTION: proposal
pres.addSection({ title: "04 Proposed Work" });

// ---- 15. Divider
s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "04 Proposed Work" });
s.addText("SECTION 04", { placeholder: "eyebrow" });
s.addText("Proposed contributions", { placeholder: "title" });
s.addText("Four contributions, ordered so that each one is independently publishable if later ones run out of time", { placeholder: "body" });
s.addNotes(`Transition. "So that is what is wrong. Here is what I propose to do about it."`);

// ---- 16. Four contributions
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("Four proposed contributions, plus one stretch objective", { placeholder: "title" });
const contribs = [
  ["C1", "Corrected re-evaluation", "Regularized centralized baseline, matched gradient steps, 3 seeds with error bars, 5-fold leave-one-subject-out", THEME.colors.accent1],
  ["C2", "Aggregation and personalization sweep", "FedProx, FedAdam, FedBN, and a shared-encoder / per-client-head variant — discharging P3's stated future work", THEME.colors.accent1],
  ["C3", "Skeleton Flow-Gated Network", "Port P7's multiplicative gating from pixels to joints: gate joint positions by joint velocity, then pool", THEME.colors.accent1],
  ["C4", "Privacy audit with defenses", "Subject re-identification and membership inference attacks, then four defenses, as a privacy-utility curve", THEME.colors.accent2],
  ["C5", "Cross-domain validation on RWF-2000", "Stretch goal only. Measures the gap against P7's 87.25% RGB ceiling if dataset access arrives in time", THEME.colors.accent5],
];
contribs.forEach((c, i) => {
  const y = 1.52 + i * 0.98;
  card(s, 0.6, y, 12.1, 0.86, i === 4 ? "F2F4F9" : (i === 3 ? "FDEEE9" : "E6F7F4"), "cc" + i);
  badge(s, 0.85, y + 0.16, 0.58, c[3], c[0], "FFFFFF", "cb" + i);
  s.addText(c[1], { x: 1.62, y: y + 0.05, w: 5.0, h: 0.4, fontSize: 16, bold: true,
    color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(c[2], { x: 1.62, y: y + 0.43, w: 10.7, h: 0.42, fontSize: 12.5,
    color: "4A5A7A", align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("C1 alone is a publishable reproducibility study. Each later contribution adds to it rather than depending on it", {
  x: 0.6, y: 6.5, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`THE PROPOSAL (about 2 minutes)

Go through C1 to C4, then flag C5 as explicitly optional.

The design principle is in the bottom line and it matters for a 15-day project: these are ordered so each is independently publishable. If I only finish C1, I have a reproducibility study. C1 plus C4 is a strong paper. All four is the full version. Nothing downstream blocks on something upstream failing.

For C1, highlight the leave-one-subject-out change. P3 tested generalization on exactly one held-out participant, which is a sample size of one. I rotate through all five clients, so I get five measurements and can report a mean and spread.

ANTICIPATED QUESTION — "Can you really do four contributions in 15 days?"
Answer: Yes, because of one specific decision: I am using P3's pre-extracted skeleton data rather than raw video. Pose estimation is the expensive step and it is already done and published. Every model in the grid is small enough to train in seconds to minutes. Slide 21 has the day-by-day plan, and days 1 to 10 are the critical path with day 11 as buffer.

ANTICIPATED QUESTION — "What if you only finish two?"
Answer: C1 and C4 are the two I would protect, because together they make the paper's argument: the accuracy claims rest on weak baselines and the privacy claim was never tested. C2 and C3 are additive.`
);

// ---- 17. C3 architecture
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("C3 — The Skeleton Flow-Gated Network", { placeholder: "title" });
s.addText("P7 gates RGB features by optical flow. We gate joint positions by joint velocity — same mechanism, new modality", {
  x: 0.6, y: 1.3, w: 12.1, h: 0.38, fontSize: 14, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 1.85, 8.3, 3.1, THEME.colors.lt2, "c3d");
card(s, 0.9, 2.35, 2.25, 0.7, "FFFFFF", "c3pos");
s.addText("Joint positions\n26 \u00D7 20  \u2192  ReLU", { x: 0.9, y: 2.35, w: 2.25, h: 0.7, fontSize: 11.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.9, 3.70, 2.25, 0.7, "FFFFFF", "c3vel");
s.addText("Joint velocity\nframe deltas  \u2192  sigmoid", { x: 0.9, y: 3.70, w: 2.25, h: 0.7, fontSize: 11.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
mergeConnector(s, 3.15, 2.70, 4.05, 3.45, THEME.colors.accent5, "c3m");
arrowRight(s, 3.47, 3.375, 0.43, THEME.colors.accent5, "c3a1");
badge(s, 3.92, 3.095, 0.56, THEME.colors.accent1, "\u00D7", "FFFFFF", "c3mul");
arrowRight(s, 4.50, 3.375, 0.30, THEME.colors.accent5, "c3a2");
card(s, 4.85, 2.975, 1.65, 0.8, "FFFFFF", "c3pool");
s.addText("gated\ntemporal pool", { x: 4.85, y: 2.975, w: 1.65, h: 0.8, fontSize: 11.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
arrowRight(s, 6.52, 3.375, 0.30, THEME.colors.accent5, "c3a3");
card(s, 6.87, 2.975, 1.75, 0.8, THEME.colors.accent1, "c3out");
s.addText("8 gestures", { x: 6.87, y: 2.975, w: 1.75, h: 0.8, fontSize: 12.5, bold: true, color: "FFFFFF",
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Where joints are still, the gate closes and those time steps are suppressed before pooling", {
  x: 0.9, y: 4.52, w: 7.7, h: 0.3, fontSize: 11.5, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 9.2, 1.85, 3.5, 3.1, "FFF6E6", "c3hon");
s.addText("Scope of the novelty claim", { x: 9.5, y: 1.97, w: 2.9, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.accent3, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("Two-stream skeleton networks with motion channels already exist, for example 2s-AGCN.\n\nWhat we adapt is the multiplicative gating, which is not standard in the skeleton literature — not the two-stream idea itself.", {
  x: 9.5, y: 2.4, w: 2.9, h: 2.45, fontSize: 12, color: C.text1,
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.1 });
card(s, 0.6, 5.15, 12.1, 1.35, THEME.colors.lt2, "c3ab");
s.addText("Ablation study and design targets", { x: 0.95, y: 5.25, w: 5.0, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "Four-way ablation:  ", options: { bold: true } },
  { text: "position only   ·   velocity only   ·   concatenation   ·   multiplicative gating", options: {} },
  { text: "        Targets:  ", options: { bold: true } },
  { text: "under 0.27M parameters, with CPU inference latency measured for edge deployment", options: {} },
], { x: 0.95, y: 5.63, w: 11.4, h: 0.78, fontSize: 13, color: C.text1, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.2 });
s.addNotes(
`C3 — THE ARCHITECTURE (about 2 minutes)

"P7's insight was that optical flow can act as a gate: where nothing is moving, suppress those features before pooling. I want to test whether that idea transports to skeletons.

The skeleton analogue of optical flow is joint velocity — just the frame-to-frame difference of keypoint coordinates. So: one branch encodes joint positions and ends in ReLU, a second branch encodes joint velocities and ends in a sigmoid, and I multiply them. Where the body is still, the gate closes and those time steps contribute less to the pooled representation."

Point at the amber box and read it out. This is important for your credibility: two-stream skeleton networks already exist. 2s-AGCN uses bone and motion streams. If I claimed two-stream skeletons as novel, a reviewer would reject it immediately. What is not standard in the skeleton literature is the multiplicative sigmoid gate — motion streams are normally concatenated or fused by averaging predictions. That distinction is exactly what my four-way ablation tests: concatenation versus gating, with everything else held constant.

Targets: P7 got 0.27 million parameters with video. Working on 26 numbers per frame instead of 224x224 pixels, I should come in well under that, which supports the CPU and edge-deployment story both P3 and P5 care about.

ANTICIPATED QUESTION — "Isn't velocity just a linear function of position? What new information does it add?"
Answer: It adds no new information in the information-theoretic sense, correct. But it changes the inductive bias — the network does not have to learn to difference adjacent frames before it can use motion, and more importantly the sigmoid gate uses motion to modulate rather than to predict. The ablation against plain concatenation is precisely the experiment that tests whether this helps.

ANTICIPATED QUESTION — "Why not use a graph convolutional network like ST-GCN?"
Answer: It would be a good additional baseline and I may add it if time permits. I kept the comparison to P3's LSTM and Transformer because those are the models whose numbers I am contesting, so holding the input and protocol identical makes the comparison clean.`
);

// ---- 18. C4 privacy audit
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("C4 — Quantifying the unverified privacy assumption", { placeholder: "title" });
card(s, 0.6, 1.5, 5.9, 2.3, "FDEEE9", "c4att");
s.addText("Attack models", { x: 0.95, y: 1.62, w: 5.2, h: 0.38, fontSize: 17, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "Subject re-identification", options: { bold: true, breakLine: true } },
  { text: "Train a classifier to predict which of 5 participants produced a skeleton window. Chance is 20%", options: { breakLine: true } },
  { text: "Membership inference", options: { bold: true, breakLine: true } },
  { text: "Shadow models against the federated updates. Chance AUC is 0.5", options: {} },
], { x: 0.95, y: 2.05, w: 5.25, h: 1.65, fontSize: 13, color: C.text1, align: "left", valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 4 });
card(s, 6.8, 1.5, 5.9, 2.3, "E6F7F4", "c4def");
s.addText("Candidate defenses", { x: 7.15, y: 1.62, w: 5.2, h: 0.38, fontSize: 17, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Random joint dropout, especially the near-static lower-body joints",
  "Hip-centring and scale normalisation (measured: -24 pts leakage, -0.4 pts accuracy)",
  "Temporal subsampling of frames",
  "DP-SGD noise applied to client updates",
], { x: 7.15, y: 2.05, w: 5.25, h: 1.65, fontSize: 13 });
card(s, 0.6, 4.0, 12.1, 1.55, THEME.colors.lt2, "c4out");
s.addText("Primary output: a privacy-utility curve", { x: 0.95, y: 4.12, w: 6.0, h: 0.38, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("Each defense is a point trading attack success against task accuracy. The curve tells a practitioner how much gesture-recognition accuracy they must give up to push identity leakage back toward chance — a number that does not currently exist in this literature.", {
  x: 0.95, y: 4.55, w: 11.4, h: 0.85, fontSize: 13.5, color: C.text1,
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
card(s, 0.6, 5.75, 12.1, 1.05, "E6F7F4", "c4cav");
s.addText([
  { text: "Status:  ", options: { bold: true } },
  { text: "the re-identification attack is implemented, and one defense is already measured — hip-centring cuts leakage 59.3% to 35.2% for 0.4 points of accuracy (Section 03). Velocity-only is ruled out: it destroys the task. Remaining: membership inference, joint dropout, DP-SGD.", options: {} },
], { x: 0.95, y: 5.88, w: 11.4, h: 0.8, fontSize: 13, color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`C4 — THE PRIVACY AUDIT (about 2 minutes) — the distinctive contribution.

"Two attacks. The first is subject re-identification: I take the exact same 26-by-20 skeleton windows the gesture classifier consumes, and I train a different classifier to predict which participant produced them. Random guessing across five people gets 20%. Whatever I get above that is leakage.

The second is membership inference against the federated updates — using shadow models to ask whether a particular sample was in a client's training set. Chance there is an AUC of 0.5.

Then four defenses, from cheap to expensive. Joint dropout and temporal subsampling are nearly free. Velocity-only is interesting because differencing removes absolute limb lengths, which is plausibly where much of the identity signal lives. DP-SGD gives formal guarantees but usually costs the most accuracy."

The green-grey box is the deliverable: a privacy-utility curve. Right now a practitioner building one of these systems has no idea what privacy they are buying or what accuracy it costs. This curve answers that.

Read the amber caveat out loud — do not let the professor raise it first. Five-way classification is much easier than open-set identification against thousands of people. A positive result proves leakage exists; it does not quantify deployment risk. Saying this yourself is far stronger than being caught.

ANTICIPATED QUESTION — "What if the attack fails and skeletons turn out to be private?"
Answer: That is still a publishable result, and a reassuring one — it would be the first actual evidence for a claim the field has been asserting without support. It is a weaker headline, which is why C1 through C3 do not depend on it.

ANTICIPATED QUESTION — "Is running attacks on a public dataset ethical?"
Answer: Yes. The data is published openly by the authors for research, the participants are consenting volunteers in a lab study, and the purpose is defensive — showing a privacy weakness so it can be fixed. This is standard practice in privacy research, and I also evaluate defenses rather than only demonstrating the attack.`
);

// ---- 19. Experimental design
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("Experimental design and evaluation metrics", { placeholder: "title" });
card(s, 0.6, 1.5, 5.9, 2.45, THEME.colors.lt2, "edg");
s.addText("Experiment grid", { x: 0.95, y: 1.62, w: 5.2, h: 0.38, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
const grid = [["4", "training paradigms"], ["4", "aggregation rules"], ["3", "architectures"], ["3", "random seeds"], ["5", "LOSO folds"]];
grid.forEach((g, i) => {
  const y = 2.08 + i * 0.36;
  s.addText(g[0], { x: 0.95, y, w: 0.5, h: 0.33, fontSize: 15, bold: true, color: THEME.colors.accent1,
    align: "right", valign: "middle", margin: 0, isTextBox: true });
  s.addText(g[1], { x: 1.55, y, w: 4.6, h: 0.33, fontSize: 13.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
card(s, 6.8, 1.5, 5.9, 2.45, "E6F7F4", "edw");
s.addText("Feasibility within the schedule", { x: 7.15, y: 1.62, w: 5.2, h: 0.38, fontSize: 16, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("Inputs are 26 numbers over 20 frames and models use 128-dimensional hidden states. Individual runs finish in seconds to a few minutes on the lab GPU.\n\nPose extraction is already done and published, so it never enters the critical path.", {
  x: 7.15, y: 2.05, w: 5.25, h: 1.75, fontSize: 13, color: C.text1,
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
s.addText("Metrics, going beyond the single accuracy figure P3 relies on", {
  x: 0.6, y: 4.05, w: 12.1, h: 0.38, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const mets = [
  ["Task quality", "Accuracy and macro-F1, because the 8 gesture classes are imbalanced across clients", THEME.colors.accent4],
  ["Diagnosis", "Confusion matrices, to quantify the collapse-to-one-class failure P3 only described in prose", THEME.colors.accent4],
  ["Deployment", "Parameter count, CPU inference latency, and uplink bytes per communication round", THEME.colors.accent3],
  ["Privacy", "Re-identification top-1 against a 20% chance baseline, and membership inference AUC against 0.5", THEME.colors.accent2],
];
mets.forEach((m, i) => {
  const y = 4.46 + i * 0.56;
  card(s, 0.6, y, 12.1, 0.46, i % 2 === 0 ? "F7F9FD" : "FFFFFF", "em" + i);
  s.addText(m[0], { x: 0.95, y, w: 2.1, h: 0.5, fontSize: 13, bold: true, color: m[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(m[1], { x: 3.15, y, w: 9.25, h: 0.5, fontSize: 12.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`EXPERIMENTAL DESIGN (about 90 seconds)

The grid looks large but explain why it is cheap. The inputs are 26 numbers per frame over 20 frames — that is 520 values per sample, which is nothing. The models have 128-dimensional hidden states. On a lab GPU each run takes seconds to a few minutes, so the full grid is a matter of hours, not days.

Then the metrics, and stress why each is there rather than just listing them:
- Macro-F1 because the classes are imbalanced across clients, so plain accuracy can hide a model that ignores rare gestures.
- Confusion matrices specifically because P3 described their model collapsing to 'Stop' but never showed a confusion matrix. I want to quantify what they only narrated.
- Deployment metrics because both papers motivate edge deployment but neither measures latency or bandwidth.
- Privacy metrics with explicit chance baselines, so the numbers are interpretable.

ANTICIPATED QUESTION — "Will you run the full cross-product? That is 4 x 4 x 3 x 3 x 5 runs."
Answer: No, and I should be precise about that. The paradigms and the aggregation rules overlap — aggregation rules only apply to the federated conditions. The realistic total is in the low hundreds of runs, not the full cross-product, and at a few minutes each that is well within a couple of days of GPU time.`
);

// ================================================================ SECTION: resources
pres.addSection({ title: "05 Resources & Plan" });

// ---- 20. Divider
s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "05 Resources & Plan" });
s.addText("SECTION 05", { placeholder: "eyebrow" });
s.addText("Resources, schedule and risk assessment", { placeholder: "title" });
s.addText("What we need, what we will do day by day, and what could go wrong", { placeholder: "body" });
s.addNotes(`Transition. "Finally, the practical side."`);

// ---- 21. Resources
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 Resources & Plan" });
s.addText("Resources required", { placeholder: "title" });
const res = [
  ["Primary dataset", "P3's processed skeletons, public on HuggingFace as WSKL/FederatedHAR. Pre-extracted, so no pose estimation needed. A few megabytes", THEME.colors.accent1, "Secured"],
  ["Compute", "College lab GPU server. Models are small; the binding constraint is our time, not GPU hours", THEME.colors.accent1, "Available"],
  ["Software", "PyTorch, a custom FedAvg simulation loop, Opacus for DP-SGD, scikit-learn for the attack classifiers", THEME.colors.accent1, "Open source"],
  ["Reference code", "P7's public GitHub repository, used to implement the gating mechanism faithfully rather than from prose", THEME.colors.accent1, "Public"],
  ["Stretch dataset", "RWF-2000, which routes through a signed access agreement. Requested on day 1, needed only for C5", THEME.colors.accent3, "Requested"],
  ["Fallbacks", "RLVS, Hockey Fight and UCF-Crime are all freely downloadable if RWF-2000 does not arrive", THEME.colors.accent5, "Standby"],
];
res.forEach((r, i) => {
  const y = 1.52 + i * 0.82;
  card(s, 0.6, y, 12.1, 0.73, i < 4 ? "E6F7F4" : "F7F9FD", "rs" + i);
  s.addText(r[0], { x: 0.95, y, w: 2.3, h: 0.73, fontSize: 13.5, bold: true, color: r[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 3.35, y, w: 7.85, h: 0.73, fontSize: 12.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[3], { x: 11.3, y, w: 1.1, h: 0.73, fontSize: 11.5, bold: true, color: r[2],
    align: "right", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("The key scoping decision: using pre-extracted skeletons removes pose estimation from the critical path entirely, which is what makes four contributions feasible in 15 days", {
  x: 0.6, y: 6.45, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`RESOURCES (about 90 seconds)

Lead with the good news: almost everything is already secured or free. The only item with any uncertainty is RWF-2000, and it is deliberately the only optional contribution.

Emphasise the italic line at the bottom, because it is the single decision that makes this project fit the deadline. Running OpenPose or FastPose over thousands of videos would consume days. P3 published the processed skeletons, so that cost is zero for us.

If your professor asks what you need from THEM: GPU server access confirmation, and approval to proceed. That is it. No budget, no hardware purchase, no data collection, no ethics clearance beyond using an already-public research dataset.

ANTICIPATED QUESTION — "What if the HuggingFace dataset is taken down or is not what you expect?"
Answer: That is the single point of failure and I am checking it first, on day one, before anything else. If it is unavailable the plan changes immediately: I would pivot to RLVS with my own pose extraction, which costs about two to three days and would mean dropping one contribution. Better to discover that on day one than day four.`
);

// ---- 22. Timeline
s = pres.addSlide({ masterName: "TABLE_SLIDE", sectionTitle: "05 Resources & Plan" });
s.addText("Project schedule", { placeholder: "title" });
const th = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, fontSize: 13, valign: "middle" } });
const tD = (t, f) => ({ text: t, options: { bold: true, color: THEME.colors.dk2, fill: { color: f }, valign: "middle", align: "center" } });
const tC = (t) => ({ text: t, options: { color: THEME.colors.dk1, valign: "middle" } });
const tO = (t, c) => ({ text: t, options: { color: c, bold: true, valign: "middle" } });
s.addTable([
  [th("Days"), th("Work"), th("Output")],
  [tD("1", "CADCFC"), tC("Environment setup, download dataset, reproduce P3's published numbers as-is. Request RWF-2000 access"), tO("Baseline reproduced", THEME.colors.accent4)],
  [tD("2-3", "CADCFC"), tC("Regularized centralized and local baselines. Three-seed variance measurement"), tO("C1 core result", THEME.colors.accent4)],
  [tD("4-5", "CADCFC"), tC("All four paradigms under 5-fold leave-one-subject-out. FedProx, FedAdam, FedBN, personalized heads"), tO("C1 and C2 tables", THEME.colors.accent4)],
  [tD("6-7", "E6F7F4"), tC("Skeleton Flow-Gated Network: implementation, four-way ablation, parameter and latency benchmarking"), tO("C3 table", THEME.colors.accent1)],
  [tD("8-9", "FDEEE9"), tC("Subject re-identification attack and membership inference with shadow models"), tO("C4 headline", THEME.colors.accent2)],
  [tD("10", "FDEEE9"), tC("Four defenses, and the privacy-utility curve"), tO("C4 figure", THEME.colors.accent2)],
  [tD("11", "FFF6E6"), tC("Deliberate buffer. RWF-2000 work only if access has arrived"), tO("C5 if feasible", THEME.colors.accent3)],
  [tD("12", "F2F4F9"), tC("Final figures, tables and confusion matrices"), tO("All exhibits", THEME.colors.accent5)],
  [tD("13-15", "F2F4F9"), tC("Writing: draft, revise, reference check"), tO("Paper draft", THEME.colors.accent5)],
], {
  placeholder: "tbl", x: 0.6, y: 1.55, w: 12.1,
  colW: [1.0, 8.4, 2.7], rowH: 0.45,
  fontSize: 12, fontFace: "Calibri", border: { type: "solid", color: "D8DEEC", pt: 1 },
  valign: "middle", margin: 0.07, autoPage: false,
});
s.addText("Days 1 to 10 are the critical path. Day 11 is unallocated on purpose, because something will go wrong", {
  x: 0.6, y: 6.5, w: 12.1, h: 0.38, fontSize: 12.5, italic: true, color: THEME.colors.accent5,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`THE PLAN (about 90 seconds)

Walk the colour bands rather than every row: blue is the replication and aggregation work, green is the architecture, red is the privacy audit, amber is buffer, grey is writing.

Two things to call out explicitly:

First, day 1 includes requesting RWF-2000 access even though it is only needed for the optional contribution. The request costs ten minutes and the reply may take a week, so starting the clock early is free.

Second, point at day 11 and say it plainly: "I have left a full day unallocated. In a 15-day schedule with this many moving parts, something will break, and a plan with no slack is a plan that fails." Professors respond well to a student who has budgeted for failure rather than assuming everything works.

ANTICIPATED QUESTION — "Three days for writing seems short."
Answer: It is tight. Two things mitigate it: I am generating every figure and table by day 12 so writing is assembly rather than analysis, and I have already written the full proposal document with the motivation, gap analysis and related work sections largely drafted. Those sections transfer almost directly into the paper.`
);

// ---- 23. Risks
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 Resources & Plan" });
s.addText("Risk assessment and mitigation", { placeholder: "title" });
const risks = [
  ["Dataset access", "RWF-2000 routes through a signed agreement and may not arrive in time", "Demoted to the only optional contribution. Requested day 1. Three free fallback datasets identified", THEME.colors.accent3],
  ["Attack generality", "Our result comes from one recording session per subject, so the residual 35.2% may not transfer across sessions", "Reported as identity-plus-session linkage, not open-set re-identification. The measured defense (hip-centring) stands regardless", THEME.colors.accent3],
  ["We may confirm P3", "The federated advantage might survive a properly regularized baseline", "The design holds either way. Framing is \"under what conditions does this hold\", never \"they are wrong\"", THEME.colors.accent1],
  ["The 52.6-point claim", "Confirmed: the public release contains only clients 1-5, so P3's 6th participant is absent", "That specific number is not reproducible. We state this plainly rather than quietly substituting a different protocol", THEME.colors.accent2],
];
risks.forEach((r, i) => {
  const y = 1.52 + i * 1.3;
  card(s, 0.6, y, 12.1, 1.22, i === 3 ? "FDEEE9" : "F7F9FD", "rk" + i);
  s.addText(r[0], { x: 0.95, y: y + 0.08, w: 2.6, h: 0.45, fontSize: 14.5, bold: true, color: r[3],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 0.95, y: y + 0.52, w: 2.6, h: 0.58, fontSize: 11.5, color: "4A5A7A",
    align: "left", valign: "top", margin: 0, isTextBox: true });
  s.addText("Mitigation", { x: 3.75, y: y + 0.08, w: 1.5, h: 0.4, fontSize: 11, bold: true,
    color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[2], { x: 3.75, y: y + 0.44, w: 8.65, h: 0.68, fontSize: 13, color: C.text1,
    align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.1 });
});
s.addNotes(
`RISKS (about 90 seconds) — do not skip this slide. Showing you have thought about failure is what separates a proposal from a wish.

Note that the original "what if the attack fails" risk is now retired — it succeeded, so row 2 instead covers the honest limitation of that success. Row 3 is the one to dwell on. A professor will reasonably ask "what if you do all this work and the original paper turns out to be right?" The answer is that the project is designed to be valuable either way. A rigorous replication with leave-one-subject-out, seed variance and four aggregation rules is a contribution whichever direction the numbers point. And my framing throughout is "under what conditions does federated training exceed centralized training, and why" — not "this paper is wrong."

Row 4 is me being upfront about something inconvenient. The most dramatic number I am contesting, the 52.6-point gain, uses a sixth participant whose data may not be in the public release. If so, I cannot reproduce that specific claim at all. I would rather say that in the proposal than have it surface as a surprise in Phase 2.

ANTICIPATED QUESTION — "What is your single biggest risk?"
Answer: The HuggingFace dataset not being what I expect. Everything else has a fallback or degrades gracefully. That is why it is the first thing I check on day one, before writing any code.`
);

// ---- 24. Closing
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "05 Resources & Plan" });
s.addText("EXPECTED OUTCOMES", { placeholder: "eyebrow" });
s.addText("Expected outcomes and request", { placeholder: "title" });
s.addText("The field has been reporting optimistic accuracy from under-specified baselines, while asserting a privacy property it never tested. Both are correctable with careful, inexpensive experiments.", { placeholder: "body" });
s.addText([
  { text: "Deliverables:", options: { bold: true, color: THEME.colors.accent1, breakLine: true } },
  { text: "Short paper with four contributions  ·  public code repository  ·  reproducible scripts", options: { color: "FFFFFF", breakLine: true, paraSpaceAfter: 12 } },
  { text: "Target venue:", options: { bold: true, color: THEME.colors.accent1, breakLine: true } },
  { text: "IEEE conference, or a CVPR / WACV-style workshop", options: { color: "FFFFFF", breakLine: true, paraSpaceAfter: 12 } },
  { text: "Asking for:", options: { bold: true, color: THEME.colors.accent1, breakLine: true } },
  { text: "Approval to proceed, and confirmation of lab GPU access", options: { color: "FFFFFF" } },
], { x: 0.8, y: 4.7, w: 11.0, h: 2.2, fontSize: 14, align: "left", valign: "top", margin: 0, isTextBox: true });
s.addNotes(
`CLOSING (about 60 seconds)

Deliver the narrative sentence slowly, because it is the whole project in one line: "The field has been reporting optimistic accuracy from under-specified baselines, while asserting a privacy property it never tested. Both are correctable with careful, inexpensive experiments."

Then be concrete about what you want: approval to proceed and GPU access. End with "I am happy to take questions, and I have the full written proposal with every number referenced to its source paper if you would like to see it."

Having the proposal document ready is a strong close — it shows the deck is a summary of real work, not the work itself.

IF ASKED "what will you have by the next review?"
Answer: C1 and C4 results at minimum — the corrected baselines with error bars, and the privacy audit with the attack result. Those two make the paper's argument. C2 and C3 add to it.

IF ASKED "why should this be published rather than just submitted as a project?"
Answer: Because the privacy result does not exist anywhere in this literature. Two 2025 papers at reasonable venues built on an assumption nobody has tested. Whether it holds or fails, measuring it is new information.`
);

// ---------------------------------------------------------------- write
(async () => {
  await pres.writeFile({ fileName: "/sessions/modest-pensive-wozniak/mnt/outputs/deck/Phase1_Review.pptx" });
  await applyTheme("/sessions/modest-pensive-wozniak/mnt/outputs/deck/Phase1_Review.pptx", THEME);
  console.log("built + themed");
})();

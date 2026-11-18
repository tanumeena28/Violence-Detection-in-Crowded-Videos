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
  slideNumber: { x: 12.3, y: 6.98, w: 0.4, h: 0.3, fontSize: 11, color: THEME.colors.accent5, align: "right" },
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
// ================================================================ SECTION: opening
pres.addSection({ title: "Opening" });

// ---- 1. Title
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
s.addShape(ellipse(), { x: 10.4, y: -1.5, w: 5.2, h: 5.2, fill: { color: "232E58" }, line: { width: 0 }, objectName: "glow" });
s.addShape(ellipse(), { x: 11.6, y: -0.6, w: 2.6, h: 2.6, fill: { color: THEME.colors.accent1, transparency: 72 }, line: { width: 0 }, objectName: "glow2" });
s.addText("B.TECH FINAL YEAR PROJECT  ·  PHASE 1 REVIEW", { placeholder: "eyebrow" });
s.addText("Violence and Goon Detection in a\nCrowd or Protest", { placeholder: "title" });
s.addText("A privacy-preserving skeleton-based approach, with a measured audit of what the skeleton representation does and does not conceal", { placeholder: "body" });
s.addText([
  { text: "Vishal Gautam", options: { bold: true, color: THEME.colors.accent6, breakLine: true } },
  { text: "Built on three source papers: FLTA 2025  ·  ICCV Workshops 2025  ·  arXiv 2020", options: { breakLine: true } },
  { text: "October 2026", options: {} },
], { placeholder: "meta" });
s.addNotes(
`OPENING (about 60 seconds)

"My project is violence and goon detection in crowds and protests. The approach I am proposing is to do it from human pose skeletons rather than raw camera footage, because the deployment setting — protest monitoring — is one where identifying individuals is itself the harm we need to avoid.

I have already done preliminary work on that privacy question, and it produced a result I will show you: the skeleton representation these methods rely on is not as anonymous as the literature assumes, but most of the leakage turns out to be removable almost for free."

Frame the structure up front: three papers reviewed, four gaps found, one component already measured, and a concrete plan for the rest.

ANTICIPATED QUESTION — "Why skeletons and not just a video classifier?"
Answer: Three reasons, in order of importance for this application. Protest surveillance has a chilling effect on lawful assembly, so a representation that discards appearance is the ethically defensible default. Skeletons are also far cheaper — the strongest comparable RGB model is 0.27M parameters but needs optical flow at inference. And they are robust to lighting and clothing. The cost is accuracy in crowds, which is exactly the gap I am proposing to work on.`
);

// ---- 2. The problem
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
s.addText("The problem, and why privacy is load-bearing here", { placeholder: "title" });
card(s, 0.6, 1.5, 5.9, 2.5, THEME.colors.lt2, "pr1");
s.addText("The detection task", { x: 0.95, y: 1.62, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Crowds and protests are exactly where manual monitoring fails: many people, many cameras, rare events",
  "Most violence is brief and localised to a few individuals within a large scene",
  "Operators need to know not only that violence occurred, but which person committed it",
], { x: 0.95, y: 2.08, w: 5.25, h: 1.8, fontSize: 13.5 });
card(s, 6.8, 1.5, 5.9, 2.5, "FDEEE9", "pr2");
s.addText("Why this setting raises the stakes", { x: 7.15, y: 1.62, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Protest is lawful assembly; surveillance of it has a documented chilling effect",
  "A system that identifies individuals at a protest causes harm even when it is accurate",
  "So the representation we compute on matters as much as the accuracy we reach",
], { x: 7.15, y: 2.08, w: 5.25, h: 1.8, fontSize: 13.5 });
card(s, 0.6, 4.25, 12.1, 2.0, "E6F7F4", "pr3");
s.addText("The approach this project takes", { x: 0.95, y: 4.4, w: 6.0, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("Detect violence from 2D pose skeletons rather than pixels, so appearance, clothing and face are never processed; attribute the violent act to a specific person in the scene; and — because the literature asserts rather than tests the privacy of skeletons — measure how much identity the representation actually leaks, and what it costs to remove it.", {
  x: 0.95, y: 4.82, w: 11.4, h: 1.3, fontSize: 14, color: C.text1,
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
s.addNotes(
`THE PROBLEM (about 2 minutes)

Left box is the task. The operational need in a crowd is not just "was there violence in this clip" — a human still has to scrub the footage to find who did it. Person-level attribution is what makes the output actionable, and it is also what the registered title asks for with "goon detection".

Right box is why this application is different from, say, industrial safety monitoring. Protest is lawful assembly. A system that works perfectly and identifies protesters has still caused harm. So unlike most computer vision projects, the choice of input representation is an ethical decision and not only an engineering one.

Bottom box is the thesis: use skeletons for the ethical reason, attribute to individuals for the operational reason, and — critically — do not simply assume the skeleton representation is anonymous, because I have measured that it is not.

ANTICIPATED QUESTION — "Isn't detecting violence at protests itself the problematic application?"
Answer: It is genuinely dual-use and I have a slide on it next. The short version: the same pipeline that flags an assault can be repurposed to identify participants, and the difference lies in the representation and in what is retained. That is why the privacy measurement is a core contribution rather than an afterthought.`
);

// ---- 3. Scope and definitions
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
s.addText("Scope and operational definitions", { placeholder: "title" });
const defs = [
  ["Violence", "A clip-level binary label: does the clip contain a physically aggressive act between people", "Standard across RWF-2000, RLVS, Hockey Fight and Crowd Violence", THEME.colors.accent4],
  ["“Goon”", "A person performing a violent act in the clip — defined by observable behaviour, never by appearance, group membership or any inferred person type", "Operationalised as per-person violent-action attribution", THEME.colors.accent1],
  ["Crowd", "Scenes with more than two simultaneously visible people, where occlusion and scale variation are the norm", "Excludes the two-person cap that prior skeleton work assumes", THEME.colors.accent4],
  ["Out of scope", "Identity, demographics, intent prediction, pre-crime inference, and any claim about who a person is", "The system answers what happened, not who someone is", THEME.colors.accent2],
];
defs.forEach((d, i) => {
  const y = 1.52 + i * 1.18;
  card(s, 0.6, y, 12.1, 1.04, i === 3 ? "FDEEE9" : (i === 1 ? "E6F7F4" : "F7F9FD"), "df" + i);
  s.addText(d[0], { x: 0.95, y: y + 0.1, w: 2.0, h: 0.92, fontSize: 16, bold: true, color: d[3],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(d[1], { x: 3.1, y: y + 0.1, w: 6.1, h: 0.92, fontSize: 12.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(d[2], { x: 9.4, y: y + 0.1, w: 3.0, h: 0.92, fontSize: 11.5, italic: true,
    color: "4A5A7A", align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`SCOPE AND DEFINITIONS (about 2 minutes) — do not skip this slide, and expect to be questioned on row 2.

The definition of "goon" is the one that matters. I define it as a behaviour — a person performing a violent act in this clip — and explicitly not as a type of person. That distinction is both scientific and ethical.

Scientifically: a model can be trained and evaluated against an observable act. It cannot be trained against "being a goon", because there is no ground truth for that and no dataset annotates it. Any model claiming to detect a person-type would be learning appearance correlates, which is exactly the failure mode the fairness literature documents.

Ethically: the person-type framing is what turns a violence detector into a profiling system. Defining the target as an act bounds what the system can be used for.

Row 3 matters technically: I define a crowd as more than two simultaneously visible people, because the closest prior work — P5 — caps its input at exactly two. That cap is the gap I am attacking, so the definition has to be explicit.

Row 4 is the negative scope, and I would read it out loud. The system answers what happened, not who someone is. That is also what makes my privacy contribution coherent rather than contradictory.

ANTICIPATED QUESTION — "Your title says goon detection. Isn't that labelling people?"
Answer: The title names the application as it is commonly described, and this slide is where I make it precise. What the system outputs is "this skeleton performed a violent act in this window". It carries no persistent identity and no claim about the person beyond the observed action.`
);

// ---- 4. Ethics and dual use
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "Opening" });
s.addText("Ethics, dual use, and an honest tension", { placeholder: "title" });
card(s, 0.6, 1.45, 12.1, 1.45, "4A2A24", "eth0");
s.addText("The tension in this project, stated plainly", { x: 0.95, y: 1.56, w: 11.4, h: 0.38, fontSize: 15, bold: true,
  color: "FFC266", align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("Our own preliminary result shows that skeleton data leaks subject identity. Identifying individuals at a protest is precisely the harm that finding warns about. A tool built to flag violent acts can be repurposed to enumerate participants.", {
  x: 0.95, y: 1.95, w: 11.4, h: 0.85, fontSize: 14, color: "FFFFFF",
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
const eth = [
  ["Representation", "No pixels, faces or clothing are processed or stored — only joint coordinates", THEME.colors.accent1],
  ["Measured hardening", "Hip-centring removes 24 points of identity leakage for 0.4 points of accuracy; we apply it by default", THEME.colors.accent1],
  ["No persistent identity", "Person-level output is scoped to a single clip; no cross-clip or cross-camera re-identification is built", THEME.colors.accent1],
  ["Behaviour, not person", "The label space contains acts only. No demographic or person-type inference exists in the model", THEME.colors.accent1],
  ["Stated in the paper", "We publish the leakage measurement as a limitation of the method, not only as a feature of it", THEME.colors.accent3],
];
eth.forEach((e, i) => {
  const y = 3.12 + i * 0.66;
  s.addText(e[0], { x: 0.6, y, w: 3.0, h: 0.58, fontSize: 13.5, bold: true, color: e[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(e[1], { x: 3.75, y, w: 8.95, h: 0.58, fontSize: 13.5, color: "FFFFFF",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("A detector that cannot be audited for identity leakage should not be deployed on lawful assembly. Measuring it is therefore part of the method, not a separate ethics exercise", {
  x: 0.6, y: 6.5, w: 12.1, h: 0.34, fontSize: 12, italic: true, color: THEME.colors.accent6,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`ETHICS AND DUAL USE (about 2 minutes) — this slide exists because a reviewer raised the contradiction, and it is a fair one.

Open by naming the tension rather than defending against it: "There is a real contradiction in this project and I want to state it myself. My preliminary result shows skeletons leak identity. The application is protest monitoring. Identifying people at protests is exactly the harm that result warns about."

Then the mitigations, which are concrete rather than aspirational:
- The representation never touches pixels, so appearance and face are structurally unavailable.
- I have measured a defense, not just proposed one. Hip-centring cuts leakage by 24 points at a cost of 0.4 points of task accuracy, so it is applied by default rather than offered as an option.
- Person-level output is scoped to one clip. There is no tracking across clips or cameras, which is the step that turns attribution into surveillance.
- The label space contains acts only.

Close on the last line: a detector that cannot be audited for identity leakage should not be deployed on lawful assembly. That reframes the privacy audit from an add-on into a precondition, which is also the strongest justification for why it belongs in this project at all.

ANTICIPATED QUESTION — "Could this be misused by police or a government?"
Answer: Yes, and I will not claim otherwise. What I can control is the design: no appearance data, measured identity hardening, no persistent identity, and publishing the leakage measurement so that anyone deploying it knows the residual risk. Being explicit about dual use is more defensible than claiming the method is neutral.`
);

// ---- 5. Contents
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
s.addText("Scope of this review", { placeholder: "title" });
const road = [
  ["01", "Reviewed literature", "Three papers: the closest violence benchmark, the closest skeleton pipeline, and the federated protocol", THEME.colors.accent4],
  ["02", "Identified research gaps", "Crowd scalability, person-level attribution, unverified privacy, baseline validity", THEME.colors.accent2],
  ["03", "Preliminary work completed", "Dataset verification, a data integrity finding, and a measured privacy result", THEME.colors.accent1],
  ["04", "Proposed contributions", "Multi-person detection, person-level attribution, a gated architecture, privacy hardening", THEME.colors.accent1],
  ["05", "Resources and schedule", "Datasets, compute, the 13-day plan, and risk assessment", THEME.colors.accent3],
];
road.forEach((r, i) => {
  const y = 1.68 + i * 1.04;
  card(s, 0.6, y, 12.1, 0.9, i === 2 ? "E6F7F4" : "F7F9FD", "road" + i);
  badge(s, 0.85, y + 0.17, 0.56, r[3], r[0], "FFFFFF", "rb" + i);
  s.addText(r[1], { x: 1.62, y: y + 0.08, w: 3.5, h: 0.4, fontSize: 17, bold: true,
    color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[2], { x: 1.62, y: y + 0.45, w: 10.7, h: 0.38, fontSize: 13,
    color: "4A5A7A", align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(`ROADMAP (30 seconds) — signposting only. Note that section 03 is work already done, not proposed.`);

// ================================================================ SECTION 01
pres.addSection({ title: "01 Literature" });

s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "01 Literature" });
s.addText("SECTION 01", { placeholder: "eyebrow" });
s.addText("Reviewed literature", { placeholder: "title" });
s.addText("The closest violence benchmark, the closest skeleton-based pipeline, and the federated evaluation protocol", { placeholder: "body" });
s.addNotes(`Transition. "Three papers, each covering a different part of what this project needs."`);

// ---- at a glance
s = pres.addSlide({ masterName: "TABLE_SLIDE", sectionTitle: "01 Literature" });
s.addText("The three papers, and what each contributes here", { placeholder: "title" });
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, fontSize: 13, valign: "middle" } });
const lbl = (t) => ({ text: t, options: { bold: true, color: THEME.colors.dk2, fill: { color: THEME.colors.lt2 }, valign: "middle" } });
const cel = (t) => ({ text: t, options: { color: THEME.colors.dk1, valign: "middle" } });
s.addTable([
  [hdr(""), hdr("P7 — arXiv 2020"), hdr("P5 — ICCV Workshops 2025"), hdr("P3 — FLTA 2025")],
  [lbl("Task"), cel("Violence vs non-violence in real surveillance clips"), cel("Crime vs normal from skeletons"), cel("8 industrial hand gestures")],
  [lbl("Input"), cel("RGB frames + dense optical flow"), cel("OpenPose, 25 keypoints × max 2 people"), cel("FastPose, 13 joints, 26-dim")],
  [lbl("Data"), cel("RWF-2000: 2,000 clips of 5 s"), cel("UCF-Crime subset, 496 videos"), cel("Custom, 5 subjects — public")],
  [lbl("Result"), cel("87.25% at 0.27M params"), cel("AUC above 0.85 (no results table)"), cel("FL beats centralized by +12.4")],
  [lbl("People"), cel("Unbounded (pixel-level)"), cel("Capped at 2"), cel("Single subject per frame")],
  [lbl("Relevance"), cel("Our accuracy reference and the gating idea we adapt"), cel("Closest skeleton pipeline — and the 2-person cap we must break"), cel("Evaluation protocol, and our privacy testbed")],
], {
  placeholder: "tbl", x: 0.6, y: 1.55, w: 12.1,
  colW: [1.45, 3.5, 3.6, 3.55], rowH: 0.62,
  fontSize: 12, fontFace: "Calibri", border: { type: "solid", color: "D8DEEC", pt: 1 },
  valign: "middle", margin: 0.08, autoPage: false,
});
s.addNotes(
`THE COMPARISON (about 2 minutes) — note the ordering has changed: P7 first, because it is now the closest prior work.

Walk down the rows. The two rows to dwell on are "People" and "Relevance".

"People" is the crux of this project. P7 works on pixels so it has no explicit person limit, but it also gives no per-person output. P5 caps its input at exactly two people — it says most conflicts involve two, and zero-pads when fewer are detected. P3 is single-subject. So none of the three operates in a crowd with per-person output, which is what my title requires.

"Relevance" says what I take from each: P7 gives the accuracy reference and the gating mechanism, P5 gives the skeleton pipeline and the limitation to break, P3 gives the evaluation protocol and — because its data is public with subject labels — the testbed for the privacy audit.

ANTICIPATED QUESTION — "Why is a 2020 paper your closest prior work?"
Answer: Because RWF-2000 is still the standard real-surveillance violence benchmark with proper anti-leakage splitting, and its Flow Gated Network remains a strong, very small baseline. I should also flag that skeleton-based violence detection on RWF-2000 does exist in the literature and reportedly exceeds P7 — I cite that on the gaps slide and it is a comparison I must make.`
);

// ---- P7
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 Literature" });
s.addText("P7 — RWF-2000 and the Flow Gated Network", { placeholder: "title" });
s.addText("Cheng, Cai, Li  ·  arXiv 2020  ·  the closest prior work and our accuracy reference", {
  x: 0.6, y: 1.32, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
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
badge(s, 3.95, 3.07, 0.56, THEME.colors.accent2, "×", "FFFFFF", "p7mul");
arrowRight(s, 4.53, 3.35, 0.3, THEME.colors.accent5, "p7a2");
card(s, 4.88, 2.95, 1.55, 0.8, "FFFFFF", "p7pool");
s.addText("temporal\nmax-pool", { x: 4.88, y: 2.95, w: 1.55, h: 0.8, fontSize: 12.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
arrowRight(s, 6.45, 3.35, 0.3, THEME.colors.accent5, "p7a3");
card(s, 6.8, 2.95, 1.15, 0.8, THEME.colors.accent4, "p7fc");
s.addText("violent /\nnot", { x: 6.8, y: 2.95, w: 1.15, h: 0.8, fontSize: 11.5, bold: true, color: "FFFFFF",
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Flow passes through a sigmoid, so motion acts as a learned 0-to-1 gate on appearance features before pooling", {
  x: 0.9, y: 4.47, w: 6.9, h: 0.32, fontSize: 11.5, italic: true, color: "4A5A7A",
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
  italic: true, color: "4A5A7A", align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 5.25, 12.1, 1.15, "FDEEE9", "p7take");
s.addText([
  { text: "Two things to carry forward:  ", options: { bold: true } },
  { text: "the multiplicative gating idea, which we port to joint velocity in C3 — and P7's own Table IV, which shows flow-based methods degrade on the Crowd Violence dataset because optical flow breaks under camera motion and low resolution.", options: {} },
], { x: 0.95, y: 5.4, w: 11.4, h: 0.85, fontSize: 14, color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`P7 (about 2 minutes) — spend time on the diagram, it sets up C3, and on the red box, which sets up the crowd gap.

The mechanism: two parallel 3D CNN branches, one on RGB and one on optical flow. RGB ends in ReLU, flow ends in a sigmoid, and they are multiplied. Where nothing moves the gate closes and those features are suppressed before temporal max-pooling. Their framing is that the network learns which time steps matter instead of a human choosing a pooling rule.

Right panel: fused gating gives 87.25%, about three points over the better single stream, at 0.27 million parameters against 24.6 million for two-stream I3D.

Then the red box, which is the important part for my project. P7's own Table IV reports that methods carrying optical flow drop significantly on the Crowd Violence dataset, and the paper explains why: optical flow assumes brightness constancy, small motion and locally uniform motion, and crowded low-resolution footage with camera movement violates all three. So the strongest prior approach degrades precisely in the setting my title names. That is an argument for a skeleton-based approach and also a warning about how hard crowds are.

ANTICIPATED QUESTION — "If P7 gets 87% why not just use it?"
Answer: Two reasons. It needs pixels, which is what the privacy motivation forbids. And it gives one label per clip with no per-person output, so it cannot do the attribution half of my title.`
);

// ---- P5
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 Literature" });
s.addText("P5 — Pose to Protect: skeleton-based crime detection", { placeholder: "title" });
s.addText("Famouri, Hossain, Imteaj  ·  ICCV Workshops 2025  ·  the closest skeleton pipeline", {
  x: 0.6, y: 1.32, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const p5flow = ["UCF-Crime\n496 videos", "Sample at\n1 frame/sec", "OpenPose\n25 keypoints", "Max 2 people\n150-dim", "LSTM 512\nbinary"];
p5flow.forEach((t, i) => {
  const x = 0.6 + i * 2.49;
  card(s, x, 1.82, 2.1, 0.92, i === 3 ? THEME.colors.accent2 : (i === 4 ? THEME.colors.accent4 : THEME.colors.lt2), "p5f" + i);
  s.addText(t, { x: x + 0.05, y: 1.82, w: 2.0, h: 0.92, fontSize: 12.5, bold: i >= 3,
    color: i >= 3 ? "FFFFFF" : C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  if (i < 4) arrowRight(s, x + 2.14, 2.28, 0.32, THEME.colors.accent5, "p5a" + i);
});
card(s, 0.6, 3.05, 5.9, 3.1, THEME.colors.lt2, "p5a");
s.addText("What it establishes", { x: 0.95, y: 3.2, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Skeletons alone carry enough signal to classify aggressive events in real surveillance footage",
  "Explicitly privacy-motivated: it calls the representation “anonymous” and “desensitized”",
  "Federated across 7 clients, split at video level so no video spans two clients",
], { x: 0.95, y: 3.65, w: 5.25, h: 2.3, fontSize: 13.5 });
card(s, 6.8, 3.05, 5.9, 3.1, "FDEEE9", "p5b");
s.addText("Where it stops short for our setting", { x: 7.15, y: 3.2, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Input capped at two people, with zero-padding when fewer are detected — unusable in a crowd",
  "Admits OpenPose is unreliable under occlusion, distance and low light, which is the crowd regime",
  "One label per whole sequence, so no indication of which person was violent",
  "No results table anywhere; and privacy is asserted but never measured",
], { x: 7.15, y: 3.65, w: 5.25, h: 2.3, fontSize: 13.5 });
s.addNotes(
`P5 (about 2 minutes) — this is the paper my method most directly extends, and the red box is my gap list.

Pipeline: 496 UCF-Crime videos covering fighting, shooting, assault, robbery and normal, sampled at one frame per second, OpenPose keypoints, at most two people giving 150 numbers per frame, into an LSTM that emits one logit per video.

Left box, credit where due: it establishes that skeletons alone are sufficient signal for aggressive-event classification on real footage, it is explicitly privacy-motivated, and the federated client splitting is done properly at video level.

Right box is where my project starts. The two-person cap is the headline limitation — the paper justifies it by saying most conflicts involve two people, which is reasonable for a mugging and wrong for a protest. It also admits OpenPose degrades under occlusion, distance and low light, and that is a description of crowd footage.

Third bullet is the attribution gap. Be precise here: P5 does NOT label individual frames. It feeds the whole variable-length sequence in, takes the last valid output, and produces one logit for the video. So the problem is dilution and the absence of per-person output, not per-frame mislabelling. P5 names the weak-supervision issue in its introduction, calling the normal frames noisy labels, but never adopts a multiple-instance learning formulation to address it.

One more citable inconsistency worth a footnote in the paper: P5 contradicts itself on normalization. Section 3.2 describes hip-centred coordinates with confidence dropped, which implies 100 dimensions for two people; Section 4.1.2 describes frame-normalized coordinates in zero-to-one with confidence kept, which gives the 150 the model actually consumes. That matters to me because, as I will show, whether coordinates are hip-centred or frame-normalized changes identity leakage substantially.`
);

// ---- P3
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 Literature" });
s.addText("P3 — Federated skeleton-based action recognition", { placeholder: "title" });
s.addText("Hegiste, Goyal, Legler, Ruskowski  ·  FLTA 2025  ·  evaluation protocol, and our privacy testbed", {
  x: 0.6, y: 1.32, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 1.8, 5.9, 2.4, THEME.colors.lt2, "p3a");
s.addText("What we take from it", { x: 0.95, y: 1.92, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "A four-paradigm protocol: centralized, local, FedAvg and federated ensemble, on one shared test set",
  "A public dataset where every sample carries a subject identifier — rare, and exactly what a privacy audit needs",
], { x: 0.95, y: 2.38, w: 5.25, h: 1.7, fontSize: 13.5 });
card(s, 6.8, 1.8, 5.9, 2.4, "FDEEE9", "p3b");
s.addText("Why it is not our task", { x: 7.15, y: 1.92, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Eight industrial hand gestures from five subjects — single person, clean indoor capture",
  "No violence, no crowd, no multi-person interaction of any kind",
], { x: 7.15, y: 2.38, w: 5.25, h: 1.7, fontSize: 13.5 });
card(s, 0.6, 4.45, 12.1, 1.95, "E6F7F4", "p3c");
s.addText("Its role in this project", { x: 0.95, y: 4.58, w: 6.0, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("P3 is not our application. It is the only public skeleton dataset we found that labels subject identity on every sample, which makes it the one place a privacy audit can actually be run. We use it for exactly that, and for nothing else. Its reported claim that federated training beats centralized training is also worth re-testing, because it inverts the usual ordering — that is Gap 4.", {
  x: 0.95, y: 5.0, w: 11.4, h: 1.25, fontSize: 14, color: C.text1,
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
s.addNotes(
`P3 (about 90 seconds) — be clear about why an industrial-gesture paper is in a violence-detection review.

The honest answer is in the green box: P3 is not my application and I am not pretending it is. It earns its place for one specific reason — it is the only public skeleton dataset I could find where every single sample carries a subject identifier. Privacy audits need identity labels, and almost no skeleton dataset publishes them. So P3 is my privacy testbed, and that is all it is.

It also contributes the evaluation protocol: four training paradigms compared on one shared test set, plus a held-out subject. That structure is worth borrowing regardless of task.

And its headline claim — federated beating centralized by 12.4 points — inverts the usual ordering, so it is worth re-testing. That is Gap 4 and I keep it as a secondary contribution rather than the headline.

ANTICIPATED QUESTION — "Why not run the privacy audit on your violence data instead?"
Answer: Because violence datasets do not publish subject identity labels. RWF-2000 is YouTube footage with no participant IDs, and RLVS is the same. Without identity labels you cannot train or evaluate a re-identification attack. P3's data is the only place the experiment is possible, which is also why its result transfers as a representation-level finding rather than a dataset-specific one.`
);

// ---- the crowd gap
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "01 Literature" });
s.addText("Where all three fall short in a crowd", { placeholder: "title" });
const cg = [
  ["P5: hard cap of 2 people", "Input is fixed at two skeletons with zero-padding. A protest scene has tens of people and the architecture cannot represent them", THEME.colors.accent2],
  ["P5: pose fails in the crowd regime", "The paper itself reports OpenPose degrading under occlusion, distance and low light — the defining conditions of crowd footage", THEME.colors.accent2],
  ["P7: optical flow degrades", "Its own Table IV shows flow-based methods dropping on Crowd Violence; flow assumes brightness constancy and small, locally uniform motion", THEME.colors.accent2],
  ["All three: no per-person output", "Every one emits a single label per clip or per window. None can say which person acted", THEME.colors.accent3],
  ["No standard protest benchmark", "Crowd Violence (246 clips) is the closest crowd-specific set. Nothing is annotated at protest or person level", THEME.colors.accent3],
];
cg.forEach((r, i) => {
  const y = 1.5 + i * 1.0;
  card(s, 0.6, y, 12.1, 0.88, i < 3 ? "3A2420" : "243055", "cg" + i);
  s.addText(r[0], { x: 0.95, y: y + 0.04, w: 3.5, h: 0.8, fontSize: 13.5, bold: true, color: r[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 4.6, y: y + 0.04, w: 7.8, h: 0.8, fontSize: 12.5, color: "FFFFFF",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("The crowd setting is simultaneously the hardest case for these methods and the one our title requires. That is the project", {
  x: 0.6, y: 6.5, w: 12.1, h: 0.34, fontSize: 12.5, italic: true, color: THEME.colors.accent6,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`THE CROWD GAP (about 2 minutes) — this is the slide that connects the literature to my title, and it was missing from my first draft.

Go through the five rows. The first three are limitations the papers state or demonstrate themselves, which makes them hard to argue with:

Row 1: P5 fixes its input at two people and zero-pads. This is not a tuning choice, it is baked into the 150-dimensional input. A protest has tens of people.

Row 2: P5's own discussion says OpenPose was inconsistent when people were partially occluded, too far from the camera, or in low light. That is a precise description of crowd surveillance footage.

Row 3: P7's Table IV shows methods carrying optical flow drop on Crowd Violence, and the paper explains it as a violation of the three optical-flow assumptions. So the strongest pixel-based approach also weakens in crowds.

Row 4 is the attribution gap — none of the three can say which person acted, so none of them does the second half of my title.

Row 5 is an honest limitation of the whole area: there is no standard protest benchmark. Crowd Violence has only 246 clips, and nothing is annotated at person level. I address that with weak supervision plus a small hand-annotated evaluation subset, which I cover in the proposal section.

Close on the bottom line: the crowd is both the hardest case for these methods and the case my title requires. That is precisely why there is a project here.`
);
// ================================================================ SECTION 02
pres.addSection({ title: "02 Gaps" });

s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "02 Gaps" });
s.addText("SECTION 02", { placeholder: "eyebrow" });
s.addText("Identified research gaps", { placeholder: "title" });
s.addText("Each gap is traceable to a specific statement, omission or table in the source papers", { placeholder: "body" });
s.addNotes(`Transition. "Four gaps, each traceable to something printed or conspicuously absent in the papers."`);

// ---- Gap 1: crowd scalability
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 Gaps" });
s.addText("Gap 1 — Crowd scalability", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent2, "1", "FFFFFF", "g1b");
s.addText("No existing skeleton pipeline for aggressive-behaviour detection handles more than two people", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.62, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const g1 = [
  ["Architectural, not incidental", "P5's input is a fixed 150-dimensional vector: 2 people × 25 keypoints × 3 values. More people cannot be represented without changing the model"],
  ["Pose quality collapses", "P5 reports OpenPose failing under occlusion, distance and low light. In a crowd all three hold simultaneously"],
  ["Pixel methods also weaken", "P7's Table IV shows optical-flow methods degrading on Crowd Violence, so the pixel-based alternative is not a free fallback"],
  ["What is needed", "A set-structured or permutation-invariant encoder over a variable number of skeletons, with per-person representations retained rather than concatenated"],
];
g1.forEach((e, i) => {
  const y = 2.3 + i * 1.03;
  card(s, 0.6, y, 12.1, 0.92, i === 3 ? "E6F7F4" : THEME.colors.lt2, "g1c" + i);
  s.addText(e[0], { x: 0.95, y: y + 0.05, w: 2.9, h: 0.82, fontSize: 13, bold: true,
    color: i === 3 ? THEME.colors.accent1 : THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(e[1], { x: 4.0, y: y + 0.05, w: 8.4, h: 0.82, fontSize: 12.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("This is the primary gap the project addresses, and it is the one the registered title requires", {
  x: 0.6, y: 6.45, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`GAP 1 (about 2 minutes) — the primary gap.

Row 1 is the key technical point: the two-person limit is not a hyperparameter, it is the input dimensionality. P5's vector is 2 × 25 × 3 = 150. You cannot feed it five people. Any fix requires changing the architecture, not the configuration.

Row 2 and 3 together say the crowd regime is hard both ways: skeleton extraction degrades, and the pixel alternative degrades too. I want to be honest that this is a genuinely difficult setting rather than an oversight nobody noticed.

Row 4 is what I propose: treat the frame as a variable-size SET of skeletons rather than a fixed concatenation, encode each person separately, and pool permutation-invariantly. That keeps per-person representations, which is also what enables attribution in Gap 2.

ANTICIPATED QUESTION — "How many people can your approach handle?"
Answer: The encoder is per-person so it is unbounded in principle; in practice it is bounded by what the pose estimator can detect, which is the real constraint. I plan to report accuracy as a function of the number of detected people, because I expect degradation and I would rather measure it than claim it does not happen.`
);

// ---- Gap 2: attribution
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 Gaps" });
s.addText("Gap 2 — No person-level attribution", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent2, "2", "FFFFFF", "g2b");
s.addText("Every reviewed method emits one label per clip. None identifies which person acted", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.62, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 2.25, 5.9, 2.4, "FDEEE9", "g2a");
s.addText("The supervision problem", { x: 0.95, y: 2.37, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "No violence dataset annotates which person is violent — labels are clip-level only",
  "So person-level attribution cannot be trained by direct supervision",
  "P5 names this weak-supervision problem in its introduction but does not address it",
], { x: 0.95, y: 2.82, w: 5.25, h: 1.7, fontSize: 13.5 });
card(s, 6.8, 2.25, 5.9, 2.4, "E6F7F4", "g2c");
s.addText("The principled route", { x: 7.15, y: 2.37, w: 5.2, h: 0.4, fontSize: 16, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "Treat each clip as a bag and each detected person as an instance",
  "Multiple-instance learning: a clip is violent if at least one person is violent",
  "Attribution then falls out of the instance scores, with no person-level labels needed",
], { x: 7.15, y: 2.82, w: 5.25, h: 1.7, fontSize: 13.5 });
card(s, 0.6, 4.9, 12.1, 1.45, THEME.colors.lt2, "g2d");
s.addText([
  { text: "Evaluation plan:  ", options: { bold: true } },
  { text: "MIL needs no person labels to train, but it does need them to evaluate. We will hand-annotate which person is violent in a small held-out subset (target 80–100 clips) and report person-level precision and recall against it. This is the only part of the project that requires manual annotation, and it is deliberately small.", options: {} },
], { x: 0.95, y: 5.05, w: 11.4, h: 1.15, fontSize: 13.5, color: C.text1, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.15 });
s.addNotes(
`GAP 2 (about 2 minutes) — this is the "goon detection" half of the title, and the method answer is MIL.

Left box is the obstacle: no violence dataset labels which individual was violent. RWF-2000, RLVS, Hockey Fight and Crowd Violence are all clip-level. So you cannot simply train a per-person classifier.

Right box is the standard solution, and it is the same formulation Sultani et al. used for UCF-Crime: treat the clip as a bag of instances, where each instance is one detected person. Train against the clip label with a max-over-instances rule, so the model learns that a clip is violent if at least one person in it is violent. Attribution then comes out of the per-instance scores for free, with no person-level supervision.

This is also the gap in P5 that I noted earlier: P5 cites the very paper that introduced MIL for this dataset and then does not use it.

Bottom box is the honest part. MIL trains without person labels but cannot be EVALUATED without them. So I will hand-annotate a small held-out subset — target 80 to 100 clips, marking which skeleton is violent — and report person-level precision and recall. That is the only manual annotation in the project and it is scoped deliberately small so it fits the schedule.

ANTICIPATED QUESTION — "Isn't 80 clips too few to evaluate on?"
Answer: It is small, and I will report it with confidence intervals rather than as a point estimate. It is enough to distinguish "attribution works" from "attribution is at chance", which is the claim I need. A larger annotation effort is the obvious Phase 2 extension.`
);

// ---- Gap 3: privacy
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "02 Gaps" });
s.addText("Gap 3 — The privacy claim is unverified", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent2, "3", "FFFFFF", "g3b");
s.addText("The justification for using skeletons at all rests on an untested assumption", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.55, fontSize: 16, bold: true, color: THEME.colors.accent6,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 2.2, 5.9, 1.75, "243055", "g3q");
s.addText("Stated in the papers", { x: 0.95, y: 2.32, w: 5.2, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "P5 calls skeletons ", options: { color: "FFFFFF" } },
  { text: "“anonymous”", options: { bold: true, color: THEME.colors.accent6 } },
  { text: " and ", options: { color: "FFFFFF" } },
  { text: "“desensitized”", options: { bold: true, color: THEME.colors.accent6, breakLine: true } },
  { text: "P3 says sharing only weights means ", options: { color: "FFFFFF" } },
  { text: "“preserving data privacy”", options: { bold: true, color: THEME.colors.accent6 } },
], { x: 0.95, y: 2.75, w: 5.25, h: 1.05, fontSize: 14, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.25 });
card(s, 6.8, 2.2, 5.9, 1.75, "243055", "g3z");
s.addText("Privacy evaluation reported", { x: 7.15, y: 2.32, w: 5.2, h: 0.35, fontSize: 14, bold: true,
  color: "FFC266", align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "None.", options: { bold: true, fontSize: 22, color: "FFFFFF", breakLine: true } },
  { text: "No privacy experiment in either paper, and neither acknowledges the omission in its limitations section", options: { fontSize: 13, color: THEME.colors.accent6 } },
], { x: 7.15, y: 2.7, w: 5.25, h: 1.1, fontSize: 14, align: "left", valign: "top", margin: 0, isTextBox: true });
const g3rows = [
  ["Prior work already warned", "Skeleton anonymisation is an established area — identity in pose data is a known risk, not a novel suspicion", "A8BBDE"],
  ["So the omission is serious", "Asserting anonymity in 2025 without testing it, when the risk was already documented, is a substantive gap", THEME.colors.accent1],
  ["And it is load-bearing here", "Privacy is the entire reason this project uses skeletons. If the premise fails, the design rationale fails with it", THEME.colors.accent1],
  ["We have now measured it", "Section 03 reports what the representation actually leaks, and what removing it costs", "FFC266"],
];
g3rows.forEach((r, i) => {
  const y = 4.12 + i * 0.6;
  s.addText(r[0], { x: 0.6, y, w: 3.4, h: 0.52, fontSize: 13, bold: true, color: r[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 4.1, y, w: 8.6, h: 0.52, fontSize: 13, color: "FFFFFF",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`GAP 3 (about 2 minutes)

"Both 2025 papers exist because of privacy. P5's abstract calls the skeleton representation anonymous and its introduction calls the data desensitized. P3 says that because only weights are shared, data privacy is preserved. Neither paper runs a single privacy experiment, and neither lists the omission in its limitations — P3's limitations cover client count, aggregation and pose fragility; P5's cover OpenPose failures."

Then row 1, and be careful to get the credit right: skeleton anonymisation is an existing research area. There is prior work studying exactly the privacy-utility trade-off in skeleton action recognition — Moon et al., AAAI 2023, is the reference I was pointed to and I must verify and cite it. This does NOT weaken my critique, it strengthens it: the risk was already documented, so asserting anonymity in 2025 without testing is a more serious omission.

IMPORTANT, FLAG TO SELF: I could not verify the Moon et al. citation or the SPIL ECCV 2020 result offline. Confirm both before presenting, and do not state either as fact until checked.

Row 3 is why this matters for my project specifically, not just as a critique of theirs: privacy is the whole reason I am using skeletons instead of pixels. If skeletons are not private, my design rationale collapses. So I had to test it, and that is Section 03.`
);

// ---- Gap 4: baseline validity
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 Gaps" });
s.addText("Gap 4 — Baseline validity and statistical reporting", { placeholder: "title" });
badge(s, 0.6, 1.5, 0.52, THEME.colors.accent3, "4", "FFFFFF", "g4b");
s.addText("A secondary gap, inherited from the federated literature we build evaluation practice on", {
  x: 1.3, y: 1.45, w: 11.4, h: 0.62, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const g4 = [
  ["Inverted ordering", "P3 reports federated training beating centralized by +12.4 points. Centralized pooling is normally the upper bound for FedAvg", THEME.colors.accent2],
  ["A collapsed baseline", "On the unseen 6th participant (their Table II) the centralized model scored 11.71% — just below the 12.5% chance level for 8 classes", THEME.colors.accent2],
  ["Budget not matched in steps", "500 epochs on pooled data and 500 local epochs on one-fifth of the data are not equal numbers of global gradient steps", THEME.colors.accent2],
  ["No variance anywhere", "Single-run point estimates throughout, with conclusions drawn from 9-to-16-point differences. P5 reports no results table at all", THEME.colors.accent2],
  ["A concrete mechanism", "The released centralized training file is truncated to 51% of its rows (Section 03). Anyone reproducing it naively trains on half the data", THEME.colors.accent3],
];
g4.forEach((e, i) => {
  const y = 2.3 + i * 0.84;
  card(s, 0.6, y, 12.1, 0.74, i === 4 ? "FFF6E6" : THEME.colors.lt2, "g4c" + i);
  s.addText(e[0], { x: 0.95, y, w: 3.0, h: 0.74, fontSize: 13, bold: true, color: e[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(e[1], { x: 4.1, y, w: 8.3, h: 0.74, fontSize: 12.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("In fairness: P3 designed its federated-ensemble condition deliberately to isolate the ensemble effect, and says so. We are not claiming they missed it", {
  x: 0.6, y: 6.5, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`GAP 4 (about 2 minutes) — a secondary gap, but the most defensible one, and it shapes how I will report my own numbers.

Row 1: in federated learning, pooling all data centrally is the upper bound you aspire to. FedAvg normally costs a little accuracy, especially under non-IID data. P3 reports the reverse.

Row 2, and be precise about the number: 11.71% is from their Table II, the unseen sixth participant, not the global test set where centralized reaches 57.1%. And 11.71% is just BELOW the 12.5% chance level for eight classes, not above it. A model at chance is a failed training run, not a tuned baseline.

Row 3 is the budget-matching objection. They claim equal epochs make the comparison fair, but 500 epochs over pooled data and 500 local epochs over a fifth of the data are not the same number of updates to the global model.

Row 4 is the one nobody can argue with: no seeds, no standard deviations, no confidence intervals, and conclusions drawn from differences of 9 to 16 points. P5 is worse — no results table at all.

Row 5 is my own finding from inspecting the released data, and it gives this gap a concrete testable mechanism rather than just a suspicion. Detail is in Section 03.

Read the fairness line at the bottom out loud. P3 explicitly designed the FedEnsemble condition to isolate the ensemble effect and interprets it that way. I am not claiming to have caught something they missed — I am claiming the question their design raises was not tested.

ANTICIPATED QUESTION — "Why does this matter if federated learning isn't your main contribution?"
Answer: Two reasons. It is the evaluation practice I am inheriting, so if I copy their protocol I inherit the flaw. And multi-camera protest monitoring is a natural federated setting, so if I extend to it I need to know whether the reported advantage is real.`
);
// ================================================================ SECTION 03
pres.addSection({ title: "03 Preliminary Work" });
const FIG = "/sessions/modest-pensive-wozniak/mnt/outputs/analysis/figs";

s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "03 Preliminary Work" });
s.addText("SECTION 03", { placeholder: "eyebrow" });
s.addText("Preliminary work already completed", { placeholder: "title" });
s.addText("Verification of the one public skeleton dataset with identity labels, a data integrity finding, and a measured privacy result with a working defense", { placeholder: "body" });
s.addNotes(
`Transition — and the moment to signal this is not only a reading exercise.

"Before proposing the main pipeline, I tested the assumption the whole approach rests on. I downloaded P3's dataset, verified it against the paper, found an integrity problem, and ran the privacy experiment neither 2025 paper performed. This section is completed work, not proposal."`
);

// ---- dataset verification
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Work" });
s.addText("Dataset verification, and an integrity finding", { placeholder: "title" });
const ver = [
  ["Frame count", "29,963 frames across train / val / test", "Matches the paper exactly", true],
  ["Subject identity", "Label files are “gesture,client_id” — identity is an explicit column", "What makes the privacy audit possible", true],
  ["Feature width", "26 values per frame = 13 joints × 2 coordinates", "As described", true],
  ["Joint layout", "Recovered empirically from per-joint variance", "Wrists move most; knees and ankles near-static", true],
  ["Coordinate frame", "Values mostly in 0.3–0.9 — frame-normalised, not body-centred", "This turns out to matter a great deal", false],
  ["Integrity", "centralized_x_train.txt stops at exactly 2,097,152 bytes (2 MiB) mid-row — 13,441 complete rows of 26,403", "A repaired file is also published; per-client files are intact", false],
];
ver.forEach((v, i) => {
  const y = 1.48 + i * 0.80;
  card(s, 0.6, y, 12.1, 0.72, v[3] ? "E6F7F4" : "FDEEE9", "v" + i);
  s.addText(v[0], { x: 0.95, y, w: 2.0, h: 0.72, fontSize: 13, bold: true,
    color: v[3] ? THEME.colors.accent1 : THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(v[1], { x: 3.1, y, w: 5.5, h: 0.72, fontSize: 12, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(v[2], { x: 8.75, y, w: 3.65, h: 0.72, fontSize: 11.5, italic: true,
    color: v[3] ? "4A5A7A" : THEME.colors.accent2, align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("A third party reproducing the centralized baseline from the obvious filename would train on 51% of the data — the exact arm whose collapse Gap 4 depends on. We will test both files", {
  x: 0.6, y: 6.42, w: 12.1, h: 0.34, fontSize: 11.5, italic: true, color: THEME.colors.accent2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`DATASET VERIFICATION (about 2 minutes) — shows real engagement with the data.

Green rows: frame count matches the paper's 29,963 exactly, and the second row is the one that makes this project possible — label files are comma-separated "gesture,client_id", so subject identity is an explicit column, not something I had to infer.

Row 4: the paper lists the joints but not their order in the file, so I recovered it from mean positions and variance. Wrists move most, which is right for upper-body gestures; knees and ankles are near-static. That matters later because low-signal joints are candidate things to drop.

Row 5 is flagged amber because it became central: the coordinates are frame-normalised rather than body-centred. That means absolute position in the image is encoded, and as I will show on the next-but-two slide, that is where most of the apparent privacy leakage came from.

Row 6 is the integrity finding. The centralized training file stops at exactly 2,097,152 bytes — two mebibytes — mid-row, with 13,441 complete rows where the label file has 26,403. Classic transfer truncation. A repaired file is also published and I verified it equals the concatenation of the five per-client files, so the repair is sound.

Read the bottom line but do not overclaim: I cannot tell what the authors trained on. What I can say is that anyone reproducing the centralized baseline from the obvious filename trains on half the data, and the centralized arm is exactly the one that collapsed. I will test both files and report the difference.`
);

// ---- fig1
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Work" });
s.addText("Measured client heterogeneity", { placeholder: "title" });
s.addImage({ path: FIG + "/fig1_heterogeneity.png", x: 0.6, y: 1.52, w: 12.1, h: 4.916 });
s.addNotes(
`CLIENT HETEROGENEITY (about 60 seconds) — keep this brief, it supports the federated component rather than the headline.

Computed from the released files rather than taken from the paper's figure. Each cell gives the percentage of that client's frames plus the raw count.

Two points: client 5 has 64 frames of gesture 3 where client 2 has 862, a 13.5-fold imbalance within one class. And client 1 devotes 23.5% of its data to "stop" where client 3 gives it 10.8%.

Why it matters: this is the non-IID regime where FedProx and FedBN are supposed to help and plain FedAvg struggles. It also means plain accuracy is misleading, since a model can score well while ignoring rare classes — which is why I report macro-F1 and confusion matrices.

If short on time, skip to the next slide; this one is supporting evidence.`
);

// ---- fig2
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Work" });
s.addText("The data itself: mean skeleton per gesture", { placeholder: "title" });
s.addImage({ path: FIG + "/fig2_skeletons.png", x: 0.6, y: 1.52, w: 12.1, h: 4.879 });
s.addNotes(
`THE SKELETONS (about 90 seconds)

Plotted directly from the released keypoints: per gesture, the mean position of all 13 joints with the skeleton edges drawn, marker size and colour showing per-joint variance.

Use it to validate the labels out loud: "G8 up shows a raised arm. G6 stop shows both hands lifted. G5 right and G3 left show the arm extended to opposite sides. So the alphabetical label ordering the paper implies is confirmed by the poses themselves — I did not assume it."

Then the technical observation, which feeds the privacy work: the dark red joints are knees and ankles. High variance but it is noise, not signal — these are upper-body gestures and the lower body is both irrelevant and poorly estimated. Roughly a third of the input dimensions carry almost no task information, which makes them free to perturb or drop as a privacy defense.`
);

// ---- fig3: the headline preliminary result
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 Preliminary Work" });
s.addText("Measured: leakage is positional, and removable", { placeholder: "title" });
s.addImage({ path: FIG + "/fig3_leakage.png", x: 0.6, y: 1.58, w: 12.1, h: 4.761 });
s.addNotes(
`THE HEADLINE PRELIMINARY RESULT (about 3 minutes) — the most credible slide in the deck, because it includes a correction I made to my own work.

"I trained a linear classifier — multinomial logistic regression, nothing more — to predict which of the five subjects produced a given skeleton window. This is the exact representation both 2025 papers call anonymous. On the data as released it identifies the subject 59.3% of the time, against 20% chance and a 26.6% majority-class baseline.

But I did not stop there, and this is the important part. I asked what the classifier was actually using. The released coordinates are frame-normalised, not body-centred, so absolute position in the image is encoded — and I measured that subjects did stand in measurably different places. So the attacker might be identifying where someone stood rather than who they are, which is a recording artifact and not a biometric.

So I re-ran it under increasing invariance. Subtract the hip midpoint and leakage falls from 59.3% to 35.2%. Also divide by shoulder width and it stays at 35.3%. Remove position entirely and use only frame-to-frame velocity and it drops to 23.8%, essentially chance.

Roughly two-thirds of what I first measured was positional artifact. The residual 35% still sits above the 26.6% majority baseline, and that residue is consistent with genuine body geometry — client 1's shoulders measure visibly narrower than the others."

Then the right panel, which is the actual contribution:

"The useful result is the trade. Hip-centring removes 24 points of leakage and costs 0.4 points of task accuracy. That is close to free, and it is a concrete recommendation any of these pipelines could adopt — including mine, where I now apply it by default. Velocity-only is the opposite: it removes leakage but destroys the task, dropping to 16% against a 12.5% chance level, so it is ruled out as a defense."

Limitations, in your own words before anyone asks:
- One recording session per subject, so clothing, camera and body are constant. This is identity-plus-session linkage, not cross-session re-identification.
- Five-way identification is far easier than open-set identification in a crowd.
- The absolute gesture accuracy here is inflated by temporal adjacency in the 88/6/6 within-block split. Comparisons between representations are valid because every row is inflated identically — do not quote 98.8% as a task result.

ANTICIPATED QUESTION — "Your first number was wrong. Why trust the second?"
Answer: Because I found the problem myself and the fix is a standard invariance test. The direction a result moves when you remove a suspected confound is the evidence, and here it moved a long way — which is exactly why reporting 59.3% alone would have been misleading.

ANTICIPATED QUESTION — "Does this transfer to crowd footage?"
Answer: Not directly, and I will not claim it does. What transfers is the representation-level lesson: frame-normalised coordinates encode position, which is identifying. In a crowd that is arguably worse, because position also encodes who someone was standing next to. Testing that needs identity-labelled crowd data, which does not exist publicly.`
);

// ---- what this establishes
s = pres.addSlide({ masterName: "CONTENT_DARK", sectionTitle: "03 Preliminary Work" });
s.addText("What this establishes for the main project", { placeholder: "title" });
const est = [
  ["The design rationale survives, with a caveat", "Skeletons are a defensible privacy choice, but not automatically anonymous. They must be hardened and audited, not assumed safe", THEME.colors.accent1],
  ["One defense is already measured", "Hip-centring is applied by default in our pipeline: -24 points of leakage for -0.4 points of accuracy", THEME.colors.accent1],
  ["One candidate defense is ruled out", "Velocity-only representations remove leakage but destroy the task. A negative result worth reporting", THEME.colors.accent3],
  ["Gap 4 gained a testable mechanism", "The truncated centralized file is a concrete hypothesis for P3's collapsed baseline", THEME.colors.accent3],
  ["Corrected during review", "Two-thirds of our first 59.3% figure was a positional artifact. We found it, removed it, and report both numbers", "A8BBDE"],
];
est.forEach((r, i) => {
  const y = 1.6 + i * 1.0;
  card(s, 0.6, y, 12.1, 0.88, i === 4 ? "243055" : "1F3A44", "es" + i);
  s.addText(r[0], { x: 0.95, y: y + 0.04, w: 3.9, h: 0.8, fontSize: 13.5, bold: true, color: r[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 5.0, y: y + 0.04, w: 7.4, h: 0.8, fontSize: 12.5, color: "FFFFFF",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`WHAT THIS ESTABLISHES (about 90 seconds) — the "so what" slide. Connect the privacy work back to the violence project.

Row 1 is the key interpretive point. Someone could read my result as undermining my own approach: if skeletons leak identity, why use them? The answer is that they are still far better than pixels, and now I can say by how much and under what conditions. The design rationale survives but it is conditional — skeletons have to be hardened and audited, not assumed safe.

Row 2: I am not proposing a defense, I have measured one, and it is in the pipeline by default.

Row 3 is a negative result and worth stating: velocity-only removes the leakage but destroys the task. Reporting what does not work is part of an honest contribution.

Row 5 is the correction, and I would end on it deliberately. Ending on the limitation rather than the strong claim builds far more credibility than the reverse.`
);

// ================================================================ SECTION 04
pres.addSection({ title: "04 Proposed Work" });

s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "04 Proposed Work" });
s.addText("SECTION 04", { placeholder: "eyebrow" });
s.addText("Proposed contributions", { placeholder: "title" });
s.addText("Four contributions plus one stretch objective, ordered so that each is independently reportable if later ones run out of time", { placeholder: "body" });
s.addNotes(`Transition. "So that is what is missing, and what I have already established. Here is the plan for the rest."`);

// ---- contributions
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("Proposed contributions", { placeholder: "title" });
const contribs = [
  ["C1", "Crowd-scale skeleton violence detection", "A set-structured encoder over a variable number of skeletons, removing the two-person cap. Evaluated on RLVS and Crowd Violence against an RGB reference", THEME.colors.accent1],
  ["C2", "Person-level attribution (“goon detection”)", "Multiple-instance learning over per-person instances, evaluated on a hand-annotated subset. Delivers the second half of the title", THEME.colors.accent1],
  ["C3", "Skeleton Flow-Gated Network", "Port P7's multiplicative gating from pixels to joints: gate joint positions by joint velocity, then pool", THEME.colors.accent1],
  ["C4", "Privacy audit and hardening", "Identity leakage measured and largely mitigated (Section 03). Remaining: membership inference, joint dropout, DP-SGD", "7C8AA8"],
  ["C5", "Federated multi-camera extension", "Stretch objective. Treats each camera as a client, with the corrected baselines from Gap 4", THEME.colors.accent5],
];
contribs.forEach((c, i) => {
  const y = 1.52 + i * 0.98;
  card(s, 0.6, y, 12.1, 0.86, i === 3 ? "EDF0F6" : (i === 4 ? "F2F4F9" : "E6F7F4"), "cc" + i);
  badge(s, 0.85, y + 0.14, 0.58, i === 3 ? THEME.colors.accent1 : c[3], c[0], "FFFFFF", "cb" + i);
  s.addText(c[1], { x: 1.62, y: y + 0.05, w: 5.4, h: 0.4, fontSize: 15.5, bold: true,
    color: C.text1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(c[2], { x: 1.62, y: y + 0.43, w: 10.7, h: 0.4, fontSize: 12, color: "4A5A7A",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  if (i === 3) {
    s.addText("DONE", { x: 11.5, y: y + 0.05, w: 0.95, h: 0.4, fontSize: 11, bold: true,
      color: THEME.colors.accent1, align: "right", valign: "middle", margin: 0, isTextBox: true });
  }
});
s.addText("C4 is substantially complete. C1 and C2 are the critical path; C3 adds the architectural contribution; C5 only if the schedule allows", {
  x: 0.6, y: 6.5, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`THE PROPOSAL (about 2 minutes)

C1 and C2 together are the title: crowd-scale detection plus person-level attribution. They are the critical path.

C1 removes the two-person cap with a set-structured encoder — each detected skeleton encoded separately, then pooled permutation-invariantly, so the model takes however many people the pose estimator finds.

C2 is the attribution half, via multiple-instance learning, with a small hand-annotated evaluation subset.

C3 is the architectural contribution carried over: P7's multiplicative gating ported to joint velocity.

C4 is marked DONE because the main experiment is complete — identity leakage measured, one defense measured, one ruled out. What remains is membership inference and the other two defenses.

C5 is explicitly a stretch objective. Federated learning is well-motivated for multi-camera monitoring and I have the corrected protocol, but it is not what the title asks for and I will not let it consume critical-path time.

Say the ordering principle out loud: these are ordered so each is independently reportable. If only C1 and C4 finish, I have a crowd-scale detector plus a privacy audit, which is a paper.

ANTICIPATED QUESTION — "Can you really do all this in 13 days?"
Answer: C4 is already done, which buys me time. The honest answer is that C1 and C2 are the critical path and C3 and C5 are at risk. The schedule slide marks exactly where I would cut.`
);

// ---- the pipeline
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("Proposed pipeline", { placeholder: "title" });
const pipe = [["Crowd or protest\nvideo", THEME.colors.lt2, C.text1],
               ["Multi-person pose\n(N skeletons, N unbounded)", THEME.colors.lt2, C.text1],
               ["Hip-centred normalisation\n(privacy hardening)", "E6F7F4", C.text1],
               ["Per-person encoder\n+ MIL pooling", THEME.colors.accent4, "FFFFFF"]];
pipe.forEach((p, i) => {
  const x = 0.6 + i * 3.12;
  card(s, x, 1.85, 2.7, 1.05, p[1], "pp" + i);
  s.addText(p[0], { x: x + 0.05, y: 1.85, w: 2.6, h: 1.05, fontSize: 12, bold: i === 3,
    color: p[2], align: "center", valign: "middle", margin: 0, isTextBox: true });
  if (i < 3) arrowRight(s, x + 2.76, 2.375, 0.3, THEME.colors.accent5, "pa" + i);
});
card(s, 0.6, 3.3, 12.1, 1.85, THEME.colors.lt2, "pout");
s.addText("Two outputs from one pass", { x: 0.95, y: 3.42, w: 6.0, h: 0.38, fontSize: 15, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.95, 3.88, 5.45, 1.08, "FFFFFF", "po1");
s.addText([
  { text: "Clip level — violence detection", options: { bold: true, breakLine: true, fontSize: 13 } },
  { text: "Violent / non-violent, trained directly from the clip labels every dataset provides", options: { fontSize: 11.5, color: "4A5A7A" } },
], { x: 1.2, y: 3.98, w: 4.95, h: 0.9, align: "left", valign: "top", margin: 0, isTextBox: true });
card(s, 6.9, 3.88, 5.45, 1.08, "FFFFFF", "po2");
s.addText([
  { text: "Person level — attribution", options: { bold: true, breakLine: true, fontSize: 13 } },
  { text: "Which skeleton performed the violent act, from MIL instance scores — no person labels needed to train", options: { fontSize: 11.5, color: "4A5A7A" } },
], { x: 7.15, y: 3.98, w: 4.95, h: 0.9, align: "left", valign: "top", margin: 0, isTextBox: true });
const feat = [
  ["No pixel data leaves the pose stage", THEME.colors.accent1],
  ["Unbounded people, set-structured", THEME.colors.accent1],
  ["Identity hardening measured, not assumed", THEME.colors.accent1],
  ["No cross-clip identity retained", THEME.colors.accent1],
];
feat.forEach((f, i) => {
  const x = 0.6 + i * 3.06;
  card(s, x, 5.45, 2.9, 0.75, "F7F9FD", "pf" + i);
  s.addText(f[0], { x: x + 0.12, y: 5.45, w: 2.66, h: 0.75, fontSize: 11.5, bold: true,
    color: f[1], align: "center", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`THE PIPELINE (about 2 minutes) — walk it left to right, then the two outputs.

Stage 1 to 2: a multi-person pose estimator — YOLOv8-pose or RTMPose — gives me N skeletons per frame with N unbounded, rather than P5's fixed two.

Stage 3 is where the privacy work enters the design rather than sitting beside it. Hip-centring is applied by default because I measured that it removes 24 points of identity leakage for 0.4 points of accuracy. This is the one stage that exists because of a result rather than an assumption.

Stage 4: each person is encoded separately by the temporal encoder — which is where C3's gated architecture goes — and then pooled across people with a multiple-instance rule.

The two outputs are the point. From one forward pass I get the clip-level violence label, which is trainable from the labels every dataset already provides, and the per-person attribution, which comes out of the instance scores without needing person-level supervision.

The four boxes along the bottom are the design properties I can defend: no pixels past the pose stage, unbounded people, measured identity hardening, and no cross-clip identity.

ANTICIPATED QUESTION — "What pose estimator, and does it work in crowds?"
Answer: YOLOv8-pose or RTMPose, both top-down multi-person. They degrade under occlusion and at distance, which is the honest limitation, and I plan to report accuracy against the number of detected people so the degradation is visible rather than hidden.

ANTICIPATED QUESTION — "Why MIL pooling rather than just max over people?"
Answer: Max over instances IS the simplest MIL rule and it is my baseline. I also want to try attention pooling, because max is brittle when pose estimation is noisy — one bad skeleton can dominate the clip score.`
);
// ---- C3 architecture
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("C3 — The Skeleton Flow-Gated Network", { placeholder: "title" });
s.addText("P7 gates appearance features by optical flow. We gate joint positions by joint velocity — same mechanism, new modality", {
  x: 0.6, y: 1.3, w: 12.1, h: 0.38, fontSize: 14, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.6, 1.85, 8.3, 3.1, THEME.colors.lt2, "c3d");
card(s, 0.9, 2.35, 2.25, 0.7, "FFFFFF", "c3pos");
s.addText("Joint positions\n26 × 20  →  ReLU", { x: 0.9, y: 2.35, w: 2.25, h: 0.7, fontSize: 11.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
card(s, 0.9, 3.70, 2.25, 0.7, "FFFFFF", "c3vel");
s.addText("Joint velocity\nframe deltas  →  sigmoid", { x: 0.9, y: 3.70, w: 2.25, h: 0.7, fontSize: 11.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
mergeConnector(s, 3.15, 2.70, 4.05, 3.45, THEME.colors.accent5, "c3m");
arrowRight(s, 3.47, 3.375, 0.43, THEME.colors.accent5, "c3a1");
badge(s, 3.92, 3.095, 0.56, THEME.colors.accent1, "×", "FFFFFF", "c3mul");
arrowRight(s, 4.50, 3.375, 0.30, THEME.colors.accent5, "c3a2");
card(s, 4.85, 2.975, 1.65, 0.8, "FFFFFF", "c3pool");
s.addText("gated\ntemporal pool", { x: 4.85, y: 2.975, w: 1.65, h: 0.8, fontSize: 11.5, color: C.text1,
  align: "center", valign: "middle", margin: 0, isTextBox: true });
arrowRight(s, 6.52, 3.375, 0.30, THEME.colors.accent5, "c3a3");
card(s, 6.87, 2.975, 1.75, 0.8, THEME.colors.accent1, "c3out");
s.addText("per-person\nviolence score", { x: 6.87, y: 2.975, w: 1.75, h: 0.8, fontSize: 11, bold: true, color: "FFFFFF",
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Where a person is still, the gate closes and those time steps are suppressed before pooling", {
  x: 0.9, y: 4.52, w: 7.7, h: 0.3, fontSize: 11.5, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
card(s, 9.2, 1.85, 3.5, 3.1, "FFF6E6", "c3hon");
s.addText("Scope of the novelty claim", { x: 9.5, y: 1.97, w: 2.9, h: 0.35, fontSize: 13.5, bold: true,
  color: THEME.colors.accent3, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText("Two-stream skeleton networks with motion channels already exist, for example 2s-AGCN. Skeleton-based violence detection on RWF-2000 also already exists and reportedly exceeds P7.\n\nWhat we adapt is the multiplicative gating, which is not standard in the skeleton literature — not the two-stream idea, and not the task.", {
  x: 9.5, y: 2.4, w: 2.9, h: 2.45, fontSize: 11.5, color: C.text1,
  align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.08 });
card(s, 0.6, 5.15, 12.1, 1.35, THEME.colors.lt2, "c3ab");
s.addText("Ablation study and design targets", { x: 0.95, y: 5.25, w: 5.0, h: 0.35, fontSize: 14, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addText([
  { text: "Four-way ablation:  ", options: { bold: true } },
  { text: "position only  ·  velocity only  ·  concatenation  ·  multiplicative gating", options: {} },
  { text: "", options: { breakLine: true } },
  { text: "Note:  ", options: { bold: true } },
  { text: "we already measured that velocity alone carries almost no task signal (16.3% on 8 gestures), so the gate must modulate rather than predict.", options: {} },
], { x: 0.95, y: 5.63, w: 11.4, h: 0.78, fontSize: 12.5, color: C.text1, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.2 });
s.addNotes(
`C3 (about 2 minutes)

"P7's insight was that motion can act as a gate: where nothing moves, suppress those features before pooling. The skeleton analogue of optical flow is joint velocity — the frame-to-frame difference of keypoints. So one branch encodes positions and ends in ReLU, a second encodes velocities and ends in a sigmoid, and they multiply. Where a person is still, their contribution is suppressed. In a crowd that is useful: most people in a protest are not fighting, and the gate should naturally down-weight them."

Read the amber box out loud — it is important for credibility and it was tightened after review. Two-stream skeleton networks already exist; 2s-AGCN uses bone and motion streams. And skeleton-based violence detection on RWF-2000 already exists and reportedly beats P7, around 89%, which I must verify and cite. So neither the two-stream idea nor the task is novel. What I am adapting is specifically the multiplicative sigmoid gate, which is not standard in skeleton work — motion streams are normally concatenated or late-fused.

FLAG TO SELF: verify the SPIL ECCV 2020 citation before presenting. If it is accurate it becomes a required comparison, not an optional one.

The ablation note is useful evidence: I already measured on P3's data that velocity alone gets 16.3% on 8 gestures against a 12.5% chance level. So velocity carries almost no standalone signal, which means the gate has to modulate the position stream rather than predict on its own. That is exactly the design and the ablation tests it.

ANTICIPATED QUESTION — "Velocity is just a linear function of position. What does it add?"
Answer: No new information in the information-theoretic sense. What changes is the inductive bias — the network does not have to learn to difference frames before it can use motion, and the sigmoid uses motion to modulate rather than to classify. Concatenation versus gating, with everything else fixed, is precisely what the ablation measures.`
);

// ---- experimental design
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Proposed Work" });
s.addText("Experimental design and evaluation metrics", { placeholder: "title" });
card(s, 0.6, 1.5, 5.9, 2.5, THEME.colors.lt2, "ed1");
s.addText("Datasets", { x: 0.95, y: 1.62, w: 5.2, h: 0.38, fontSize: 16, bold: true,
  color: THEME.colors.dk2, align: "left", valign: "middle", margin: 0, isTextBox: true });
const dsl = [["RLVS", "2,000 clips, free — primary"], ["Crowd Violence", "246 clips, crowded scenes — the crowd case"],
             ["Hockey Fight", "1,000 clips, free — sanity baseline"], ["RWF-2000", "access requested — stretch"],
             ["P3 FederatedHAR", "privacy audit only (done)"]];
dsl.forEach((d, i) => {
  const y = 2.06 + i * 0.38;
  s.addText(d[0], { x: 0.95, y, w: 2.2, h: 0.35, fontSize: 12.5, bold: true, color: THEME.colors.accent1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(d[1], { x: 3.2, y, w: 3.1, h: 0.35, fontSize: 11.5, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
card(s, 6.8, 1.5, 5.9, 2.5, "E6F7F4", "ed2");
s.addText("Comparisons we owe the reader", { x: 7.15, y: 1.62, w: 5.2, h: 0.38, fontSize: 16, bold: true,
  color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
bullets(s, [
  "P7's Flow Gated Network as the RGB reference (87.25% on RWF-2000)",
  "Published skeleton-based violence results on RWF-2000 — to verify and cite",
  "A two-person-capped variant, reproducing P5's constraint to quantify what removing it buys",
], { x: 7.15, y: 2.06, w: 5.25, h: 1.8, fontSize: 12.5 });
s.addText("Metrics", { x: 0.6, y: 4.06, w: 12.1, h: 0.38, fontSize: 16, bold: true, color: THEME.colors.dk2,
  align: "left", valign: "middle", margin: 0, isTextBox: true });
const mets = [
  ["Clip level", "Accuracy, macro-F1 and AUC, with mean ± standard deviation over 3 seeds", THEME.colors.accent4],
  ["Person level", "Precision and recall of violent-person attribution on the hand-annotated subset, with confidence intervals", THEME.colors.accent1],
  ["Crowd behaviour", "Accuracy as a function of the number of detected people — the degradation curve, reported not hidden", THEME.colors.accent3],
  ["Privacy", "Subject re-identification against chance and majority baselines; membership inference AUC against 0.5", THEME.colors.accent2],
  ["Deployment", "Parameter count and CPU inference latency per clip", "7C8AA8"],
];
mets.forEach((m, i) => {
  const y = 4.5 + i * 0.47;
  card(s, 0.6, y, 12.1, 0.40, i % 2 === 0 ? "F7F9FD" : "FFFFFF", "em" + i);
  s.addText(m[0], { x: 0.95, y, w: 2.1, h: 0.38, fontSize: 12.5, bold: true, color: m[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(m[1], { x: 3.15, y, w: 9.25, h: 0.38, fontSize: 12, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
});
s.addNotes(
`EXPERIMENTAL DESIGN (about 2 minutes)

Datasets, and be honest about the compromise: RLVS is the primary set because it is free, balanced and 2,000 clips. Crowd Violence is only 246 clips but it is the closest thing to a crowd-specific benchmark that is freely available, so it carries the crowd claim despite its size. Hockey Fight is a sanity baseline. RWF-2000 is requested but gated, so it stays a stretch. P3's data is used only for the privacy audit.

State the limitation directly: there is no standard protest benchmark. Crowd Violence plus the fighting and assault classes of UCF-Crime are the closest available proxies, and I will say so in the paper rather than implying I have protest data.

Comparisons: the RGB reference, the published skeleton result on RWF-2000 that I must verify, and — this one matters — a deliberately two-person-capped variant of my own model. Reproducing P5's constraint inside my own pipeline is how I quantify what removing the cap actually buys, with everything else held constant.

Metrics, and why each is there: macro-F1 because violence datasets are imbalanced in practice; person-level precision and recall with confidence intervals because the annotated subset is small; the degradation curve against number of detected people because I expect crowds to hurt and would rather measure it; privacy metrics with explicit chance baselines; and deployment cost because the skeleton argument is partly an efficiency argument.

ANTICIPATED QUESTION — "246 clips is very small for a crowd claim."
Answer: Agreed, and it is the weakest part of the evaluation. I report it with confidence intervals and treat it as indicative rather than definitive. The degradation curve on RLVS, which has varying numbers of people, carries more statistical weight for the crowd claim than Crowd Violence does on its own.`
);

// ================================================================ SECTION 05
pres.addSection({ title: "05 Resources & Plan" });

s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: "05 Resources & Plan" });
s.addText("SECTION 05", { placeholder: "eyebrow" });
s.addText("Resources, schedule and risk", { placeholder: "title" });
s.addText("What we need, what we will do day by day, and what could go wrong", { placeholder: "body" });
s.addNotes(`Transition. "Finally, the practical side."`);

// ---- resources
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 Resources & Plan" });
s.addText("Resources required", { placeholder: "title" });
const res = [
  ["Primary video data", "RLVS (2,000 clips), Crowd Violence (246), Hockey Fight (1,000) — all freely downloadable", THEME.colors.accent1, "Free"],
  ["Privacy testbed", "P3's FederatedHAR, public on HuggingFace, already downloaded and analysed", THEME.colors.accent1, "Done"],
  ["Compute", "College lab GPU server. Pose extraction over ~3,200 clips is the one substantial GPU cost", THEME.colors.accent1, "Available"],
  ["Pose estimator", "YOLOv8-pose or RTMPose, pretrained — multi-person, no training required", THEME.colors.accent1, "Open source"],
  ["Software", "PyTorch, Ultralytics, Opacus for DP-SGD, numpy and matplotlib", THEME.colors.accent1, "Open source"],
  ["Manual annotation", "Person-level violence labels on 80–100 held-out clips, for C2 evaluation only", THEME.colors.accent3, "~4 hours"],
  ["Stretch dataset", "RWF-2000, via signed access agreement. Requested day 1, needed only for the C5 comparison", THEME.colors.accent3, "Requested"],
];
res.forEach((r, i) => {
  const y = 1.5 + i * 0.73;
  card(s, 0.6, y, 12.1, 0.65, i < 5 ? "E6F7F4" : "FFF6E6", "rs" + i);
  s.addText(r[0], { x: 0.95, y, w: 2.5, h: 0.65, fontSize: 13, bold: true, color: r[2],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 3.55, y, w: 7.6, h: 0.65, fontSize: 12, color: C.text1,
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[3], { x: 11.25, y, w: 1.15, h: 0.65, fontSize: 11.5, bold: true, color: r[2],
    align: "right", valign: "middle", margin: 0, isTextBox: true });
});
s.addText("Nothing on the critical path is gated behind an access request, and the privacy component is already complete", {
  x: 0.6, y: 6.68, w: 12.1, h: 0.32, fontSize: 12, italic: true, color: "4A5A7A",
  align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`RESOURCES (about 90 seconds)

Lead with the good news: every dataset on the critical path is freely downloadable, the pose estimator is pretrained so there is no training cost there, and the privacy component is already finished.

The one new substantial cost is GPU time for pose extraction over roughly 3,200 clips. At a few seconds per clip on a lab GPU that is hours, not days, and it is a one-time cost because I cache the extracted skeletons.

The one genuinely manual item is the person-level annotation for C2 evaluation — 80 to 100 clips, marking which skeleton is violent. I estimate about four hours. It is the only annotation in the project and it is deliberately scoped small.

Point at the bottom line: unlike my earlier plan, nothing on the critical path waits on an access request. RWF-2000 is requested on day 1 but only feeds the optional comparison.

What I need from you: confirmation of GPU server access, and approval of this scope.`
);

// ---- schedule
s = pres.addSlide({ masterName: "TABLE_SLIDE", sectionTitle: "05 Resources & Plan" });
s.addText("Project schedule — 13 days", { placeholder: "title" });
const th = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, fontSize: 13, valign: "middle" } });
const tD = (t, f) => ({ text: t, options: { bold: true, color: THEME.colors.dk2, fill: { color: f }, valign: "middle", align: "center" } });
const tC = (t) => ({ text: t, options: { color: THEME.colors.dk1, valign: "middle" } });
const tO = (t, c) => ({ text: t, options: { color: c, bold: true, valign: "middle" } });
s.addTable([
  [th("Days"), th("Work"), th("Output")],
  [tD("1", "CADCFC"), tC("Download RLVS, Crowd Violence, Hockey Fight. Request RWF-2000 access. Set up pose extraction"), tO("Data in place", THEME.colors.accent4)],
  [tD("2-3", "CADCFC"), tC("Multi-person pose extraction over all clips; cache skeletons. Hip-centred normalisation applied by default"), tO("Skeleton corpus", THEME.colors.accent4)],
  [tD("4-5", "E6F7F4"), tC("Set-structured per-person encoder; clip-level violence baseline. Two-person-capped variant for comparison"), tO("C1 result", THEME.colors.accent1)],
  [tD("6-7", "E6F7F4"), tC("MIL pooling; hand-annotate 80–100 clips; person-level attribution evaluation"), tO("C2 result", THEME.colors.accent1)],
  [tD("8", "E6F7F4"), tC("Skeleton Flow-Gated Network and its four-way ablation"), tO("C3 result", THEME.colors.accent1)],
  [tD("9", "FDEEE9"), tC("Degradation curve vs number of detected people; macro-F1 and seed variance across all models"), tO("Crowd analysis", THEME.colors.accent2)],
  [tD("10", "FDEEE9"), tC("Finish C4: membership inference, joint dropout, DP-SGD. Verify the SPIL and Moon citations"), tO("C4 complete", THEME.colors.accent2)],
  [tD("11", "FFF6E6"), tC("Deliberate buffer. C5 federated extension or RWF-2000 only if everything above is done"), tO("Buffer", THEME.colors.accent3)],
  [tD("12-13", "F2F4F9"), tC("Figures, tables, writing, reference check"), tO("Paper draft", THEME.colors.accent5)],
], {
  placeholder: "tbl", x: 0.6, y: 1.55, w: 12.1,
  colW: [1.0, 8.5, 2.6], rowH: 0.465,
  fontSize: 12, fontFace: "Calibri", border: { type: "solid", color: "D8DEEC", pt: 1 },
  valign: "middle", margin: 0.07, autoPage: false,
});
s.addText("Days 1 to 7 are the critical path and deliver the title. Day 8 onward is additive — if the schedule slips, C3 and C5 are what I cut",
  { x: 0.6, y: 6.52, w: 12.1, h: 0.34, fontSize: 12.5, italic: true, color: "4A5A7A",
    align: "left", valign: "middle", margin: 0, isTextBox: true });
s.addNotes(
`THE SCHEDULE (about 90 seconds)

Walk the colour bands: blue is data and pose extraction, green is the three model contributions, red is analysis and finishing the privacy work, amber is buffer, grey is writing.

Three things to call out:

Days 2 and 3 are the new cost compared with my earlier plan — pose extraction over roughly 3,200 clips. It is a one-time GPU cost and the skeletons are cached, so nothing downstream repeats it.

Days 1 to 7 deliver the title: crowd-scale detection plus person-level attribution. That is the critical path and I protect it.

Point at the bottom line and be explicit about triage: if I slip, C3 and C5 are what I cut, in that order. I would rather present C1, C2 and C4 done properly than four contributions done badly.

Day 11 is unallocated on purpose. In a 13-day plan with pose extraction and manual annotation in it, something will go wrong.

ANTICIPATED QUESTION — "Only two days for writing?"
Answer: Tight, but the proposal document is already written with motivation, literature and gap analysis largely drafted, and every figure is generated by script so regenerating them is minutes. Writing is assembly rather than analysis.`
);

// ---- risks
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 Resources & Plan" });
s.addText("Risk assessment and mitigation", { placeholder: "title" });
const risks = [
  ["Pose fails in crowds", "Occlusion and distance degrade multi-person pose", "Report the degradation curve against number of detected people rather than hiding it. A measured failure mode is a result; RLVS has many lighter-crowd clips as a fallback regime", THEME.colors.accent2],
  ["No protest benchmark", "Crowd Violence has 246 clips and nothing is annotated at protest or person level", "State it plainly as a scope limitation. Use Crowd Violence plus UCF-Crime fighting and assault as the closest proxies, with confidence intervals throughout", THEME.colors.accent3],
  ["Prior work may already beat us", "Published skeleton results on RWF-2000 may exceed P7", "Verify the citation on day 10 and compare honestly. Our contribution is crowd scale, person-level attribution and audited privacy — not peak clip accuracy", THEME.colors.accent3],
  ["Annotation too small", "80–100 clips is a thin basis for the person-level claim", "Report with confidence intervals; the claim is only that attribution beats chance, not that it is precise", THEME.colors.accent3],
  ["Privacy result generality", "One session per subject, on a non-crowd dataset", "Reported as identity-plus-session linkage on a representation, not as a crowd re-identification claim. The measured defense stands regardless", "7C8AA8"],
];
risks.forEach((r, i) => {
  const y = 1.5 + i * 1.05;
  card(s, 0.6, y, 12.1, 0.95, i === 0 ? "FDEEE9" : "F7F9FD", "rk" + i);
  s.addText(r[0], { x: 0.95, y: y + 0.04, w: 2.8, h: 0.40, fontSize: 13, bold: true, color: r[3],
    align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[1], { x: 0.95, y: y + 0.42, w: 2.8, h: 0.46, fontSize: 10.5, color: "4A5A7A",
    align: "left", valign: "top", margin: 0, isTextBox: true });
  s.addText("Mitigation", { x: 3.95, y: y + 0.04, w: 1.5, h: 0.34, fontSize: 10.5, bold: true,
    color: THEME.colors.accent1, align: "left", valign: "middle", margin: 0, isTextBox: true });
  s.addText(r[2], { x: 3.95, y: y + 0.36, w: 8.45, h: 0.56, fontSize: 12, color: C.text1,
    align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.05 });
});
s.addNotes(
`RISKS (about 2 minutes) — do not skip. Row 1 is the one a professor will press on.

Row 1 is the central technical risk of the whole project: pose estimation degrades exactly where my title operates. I will not pretend otherwise. My answer is to measure it — report accuracy against the number of detected people so the degradation is a published curve rather than a hidden weakness. If the curve falls off sharply beyond a certain crowd density, that is a finding and it bounds where the method is usable.

Row 2 is a scope limitation of the field, not just of my project: there is no standard protest benchmark. I use Crowd Violence and UCF-Crime's fighting and assault classes as proxies and say so.

Row 3 is intellectual honesty about novelty. If published skeleton methods already beat P7 on RWF-2000, my contribution cannot be peak clip accuracy. It is crowd scale, person-level attribution and audited privacy. I would rather state that clearly than get caught claiming a record I do not hold.

Row 4: the annotated subset is small and I report confidence intervals rather than point estimates.

Row 5 is the honest bound on my strongest completed result.

ANTICIPATED QUESTION — "What is your single biggest risk?"
Answer: Pose quality in crowds. Everything else has a fallback or degrades gracefully. That is why days 2 and 3 are pose extraction — I will know by day 3 whether the skeletons are usable, which leaves time to adjust scope rather than discovering it in week two.`
);

// ---- closing
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "05 Resources & Plan" });
s.addText("EXPECTED OUTCOMES", { placeholder: "eyebrow" });
s.addText("Crowd-scale detection, person-level\nattribution, audited privacy", { placeholder: "title" });
s.addText("Existing skeleton methods for aggressive-behaviour detection cap out at two people, cannot say who acted, and assert a privacy property none of them tested. This project addresses all three.", { placeholder: "body" });
s.addText([
  { text: "Deliverables:", options: { bold: true, color: THEME.colors.accent1, breakLine: true } },
  { text: "Short paper with four contributions  ·  public code repository  ·  reproducible scripts", options: { color: "FFFFFF", breakLine: true, paraSpaceAfter: 10 } },
  { text: "Already complete:", options: { bold: true, color: THEME.colors.accent1, breakLine: true } },
  { text: "The privacy audit, with a measured defense and one candidate defense ruled out", options: { color: "FFFFFF", breakLine: true, paraSpaceAfter: 10 } },
  { text: "Asking for:", options: { bold: true, color: THEME.colors.accent1, breakLine: true } },
  { text: "Approval of this scope, and confirmation of lab GPU access", options: { color: "FFFFFF" } },
], { x: 0.8, y: 4.7, w: 11.0, h: 2.2, fontSize: 14, align: "left", valign: "top", margin: 0, isTextBox: true });
s.addNotes(
`CLOSING (about 60 seconds)

Deliver the thesis sentence slowly: "Existing skeleton methods for aggressive-behaviour detection cap out at two people, cannot say who acted, and assert a privacy property none of them tested. This project addresses all three."

Then be concrete: the privacy component is already done, with a measured defense and a ruled-out one. What I need is approval of the scope and GPU access.

Close with: "I'm happy to take questions, and I have the full written proposal with every number referenced to its source if you'd like to see it."

IF ASKED "what changed since you started?"
Answer: Two things, both worth saying. I found that most of the identity leakage I first measured was a positional recording artifact, corrected it, and ended up with a better result — a defense that costs almost nothing. And a review pointed out that my first draft of this proposal had drifted toward the industrial-gesture dataset rather than the crowd and protest setting the project is about. This version puts crowds and attribution back at the centre, where the title requires them.`
);

// ---------------------------------------------------------------- write
(async () => {
  await pres.writeFile({ fileName: "/sessions/modest-pensive-wozniak/mnt/outputs/deck/Phase1_Review.pptx" });
  await applyTheme("/sessions/modest-pensive-wozniak/mnt/outputs/deck/Phase1_Review.pptx", THEME);
  console.log("built + themed");
})();

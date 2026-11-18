import fs from 'node:fs/promises';
import path from 'node:path';

const root = 'C:/Users/Vishal Gautam/Desktop/Affective Lab/AffectiveProject';
const output = path.join(root, 'output/presentations');
const results = path.join(root, 'output/source_corrected');
const demos = JSON.parse(await fs.readFile(path.join(results, 'demos.json'), 'utf8'));
const external = JSON.parse(await fs.readFile(path.join(results, 'external_smoke.json'), 'utf8'));
const entries = [
  { title: 'Correct nonviolent example', data: demos.find(d => d.source.includes('Brisbane_Lions')), label: 'Nonviolent', description: 'Held-out Brisbane crowd clip. The combined model predicts nonviolent.' },
  { title: 'Correct violent example', data: demos.find(d => d.source.includes('English_Hooligans')), label: 'Violent', description: 'Held-out English Hooligans clip. The combined model predicts violent.' },
  { title: 'Missed violent example', data: demos.find(d => d.source.includes('Germany_v_Poland')), label: 'Violent', description: 'Held-out Germany versus Poland clip. The combined model predicts nonviolent despite high pose coverage.' },
  { title: 'Insufficient pose evidence', data: demos.find(d => d.usable_pose_fraction === 0), label: 'Nonviolent', description: 'Held-out Brazilian football clip. No sampled frames contain usable poses, so the demo abstains.' },
  { title: 'External false positive', data: external, label: 'Non-fight (RWF-2000)', description: 'The previously inspected external example passes through raw-video extraction. The combined model predicts violent. This checks execution and does not measure external accuracy.' },
];
const escape = s => String(s).replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cards = entries.map(({title,data:d,label,description}, i) => {
  if (!d) throw new Error('Missing demo: ' + title);
  const video = 'media/' + path.basename(d.video);
  const poster = 'media/' + path.basename(d.snapshot);
  return `<article aria-labelledby="demo-${i + 1}">
  <h2 id="demo-${i + 1}">${escape(title)}</h2>
  <video controls preload="metadata" playsinline poster="${poster}"><source src="${video}" type="video/mp4">Open the video using the link below.</video>
  <dl><div><dt>Dataset label</dt><dd>${escape(label)}</dd></div><div><dt>Demo decision</dt><dd>${escape(d.decision)}</dd></div><div><dt>Clip score</dt><dd>${d.score.toFixed(3)}</dd></div><div><dt>Usable pose coverage</dt><dd>${(100 * d.usable_pose_fraction).toFixed(1)}%</dd></div></dl>
  <p>${escape(description)}</p>
  <a href="${video}">Open MP4 in a separate window or player</a>
</article>`;
}).join('\n');
const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>24 October: crowd violence pipeline demos</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f7f9;color:#14243a;font:17px/1.5 Calibri,Arial,sans-serif}header,main,footer{max-width:1180px;margin:auto;padding:28px}header{padding-top:42px}h1{font-size:38px;line-height:1.2;margin:0 0 12px}h2{font-size:24px;line-height:1.25;margin:0 0 16px}p{margin:12px 0}a{color:#087f83;font-weight:700;text-underline-offset:3px}.intro{max-width:850px;color:#526173}.notice{border-left:4px solid #087f83;background:#eaf2f2;padding:16px 20px;margin-top:22px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:#fff;border:1px solid #ccd6df;border-radius:8px;padding:22px}video{width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;background:#14243a;border-radius:4px}dl{margin:18px 0}dl div{display:flex;gap:16px;justify-content:space-between;border-bottom:1px solid #e5e9ed;padding:5px 0}dt{color:#526173}dd{margin:0;text-align:right;font-weight:700}article p{color:#526173}footer{color:#526173;padding-top:12px;padding-bottom:36px}@media(max-width:760px){header,main,footer{padding:22px}.grid{grid-template-columns:1fr}h1{font-size:30px}article{padding:18px}}
</style></head><body>
<header><h1>Crowd violence pipeline: offline demos</h1><p class="intro">Vishal Gautam, U23AI127. Implementation discussion, 24 October 2026.</p><p><a href="Oct24_Crowd_Violence_Implementation.pptx">Open the presentation</a></p>
<div class="notice">These five annotated outputs illustrate execution, including errors and an abstention. Four come from the fixed six-video held-out demo set. The external example was previously inspected. This subset does not estimate accuracy.</div></header>
<main><div class="grid">${cards}</div></main>
<footer><p>All videos use the corrected combined model. Its threshold is 0.54. The model scores the whole clip offline, and its score is not a calibrated probability. Pose coverage is the fraction of sampled frames with usable poses. Below 25% coverage, the demo reports insufficient pose evidence. This cutoff is an initial operational rule, not a validated rejection model. All 47 test clips remain in the reported metrics.</p><p>Unzip the package before opening this page. Keep the media folder beside it. Internet access is unnecessary. If browser playback fails, use the MP4 link with a local video player.</p></footer>
</body></html>`;
await fs.writeFile(path.join(output, 'demo-index.html'), html, 'utf8');
await fs.writeFile(path.join(output, 'README.txt'), `24 OCTOBER IMPLEMENTATION DISCUSSION
Vishal Gautam, U23AI127

OPENING THE PACKAGE
1. Extract the ZIP to a folder before opening any file.
2. Open Oct24_Crowd_Violence_Implementation.pptx in PowerPoint.
3. Keep the media folder next to the presentation. Slides 7 and 8
   link to local MP4 files. The videos open externally and are not embedded.
4. For a browser fallback, open demo-index.html. It includes five videos
   with dataset labels, decisions, scores and explanation of each example.
   The package works offline. If playback fails in the browser, open the
   MP4 directly in a local video player.

PRESENTATION USE
The 10-slide deck covers the implemented pipeline, four configurations,
corrected pilot split and results, working examples, an error, controls
and final-stage work. Speaker notes include speaking guidance and sources.
Use PowerPoint Presenter View or the Notes pane to read them.
Keep the prepared explanation short and leave time for discussion.

DEMONSTRATION ORDER
Play the correct nonviolent example, then the correct violent example.
Show the missed violent example. If time allows, show the abstention or
the external false positive. The selected examples do not estimate accuracy.

CURRENT CLAIMS
Raw-video inference and annotated output execute end to end. Reliability
and interaction additions have not consistently improved the baseline.
Current results are exploratory: one corrected split and seed 42, with
the source correction following prior test inspection. The pipeline scores
whole clips offline. It does not produce event timestamps or person-level
violence attribution. The model score is not a calibrated probability.

LIVE PIPELINE IN THE ORIGINAL PROJECT
This portable package contains playback outputs, not executable model code.
From the original AffectiveProject folder, use PowerShell:
  .\\scripts\\show_pipeline.ps1 -VerifyOnly
For a selected raw video:
  .\\scripts\\show_pipeline.ps1 -Video 'C:\\path\\to\\video.mp4'
The project's environment, weights and data must be available for inference.

FINAL STAGE
The professor expects implementation, demonstration and a paper draft with
methods and results at the final presentation. The complete paper should
have at least 12 pages before 20 November. The final group date remains
unconfirmed. Use the 24 October discussion to confirm whether flagged
windows should be added to the current whole-clip implementation.
`, 'utf8');
console.log('Created demo-index.html and README.txt with five local demos.');

import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile, FileBlob } from '@oai/artifact-tool';

const root = 'C:/Users/Vishal Gautam/Desktop/Affective Lab/AffectiveProject';
const build = path.join(root, 'tmp/oct24_deck');
const output = path.join(root, 'output/presentations');
const SKILL = 'C:/Users/Vishal Gautam/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const PYTHON = 'C:/Users/Vishal Gautam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES = 'C:/Users/Vishal Gautam/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const FINAL = path.join(output, 'Oct24_Crowd_Violence_Implementation.pptx');
const results = path.join(root, 'output/source_corrected');
const read = async f => JSON.parse(await fs.readFile(path.join(results, f), 'utf8'));
const runs = await read('training_summary.json');
const controls = await read('motion/summary.json');
const demos = await read('demos.json');
const audit = await read('audit.json');
const external = await read('external_smoke.json');
const source = path.join(root, 'output/pilot/failure_analysis/similarity/source_pair_02.jpg');
const pct = x => `${(100 * x).toFixed(1)}%`;
const dec = x => x.toFixed(3);
const C = {bg:'#F6F7F9', ink:'#14243A', teal:'#087F83', muted:'#526173', line:'#CCD6DF', white:'#FFFFFF', pale:'#EAF2F2', amber:'#9C5B18'};
const deck = Presentation.create({slideSize:{width:1280,height:720}});
const fontPolicy = {basis:'design',families:['Calibri']};
const links = [];
const refs = {
 vf:'https://www.openu.ac.il/home/hassner/data/violentflows/',
 rwf:'https://arxiv.org/abs/1911.05913',
 pose:'https://openaccess.thecvf.com/content/ICCV2025W/WiCV/html/Famouri_Pose_to_Protect_Federated_Skeleton-Based_Anomaly_Detection_for_Privacy-Conscious_Video_ICCVW_2025_paper.html',
 fast:'https://arxiv.org/abs/2508.14113',
 yolo:'https://docs.ultralytics.com/tasks/pose/'
};
await fs.mkdir(build,{recursive:true});
await fs.mkdir(output,{recursive:true});
await fs.mkdir(path.join(output,'media'),{recursive:true});

function text(s,value,x,y,w,h,size=28,opts={}) {
 const sh=s.shapes.add({geometry:'textbox',name:opts.name||String(value).slice(0,55),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=value;
 sh.text.style={typeface:'Calibri',fontSize:size,color:opts.color||C.ink,bold:opts.bold||false,alignment:opts.align||'left',verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0};
 if(opts.link){sh.text.get(value).link={uri:opts.link,isExternal:true};links.push(opts.link);}
 return sh;
}
function slide(title,foot='') {
 const s=deck.slides.add();s.background.fill=C.bg;
 text(s,title,64,46,1152,68,45,{bold:true,name:'Slide title'});
 text(s,String(deck.slides.items.length).padStart(2,'0'),1168,670,48,24,18,{color:C.muted,align:'right'});
 if(foot)text(s,foot,64,668,1070,30,19,{color:C.muted});
 return s;
}
function note(s,body,sources=[]) {
 s.speakerNotes.text=body+'\n\nSources\n'+sources.join('\n');
}
function table(s,values,x,y,width,widths,heights,size=27) {
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height:heights.reduce((a,b)=>a+b,0),columnWidths:widths,values});
 t.styleOptions={headerRow:true,bandedRows:false};
 t.borders.assign({style:'solid',fill:C.line,width:1});
 values.forEach((row,r)=>{
  t.rows[r].height=heights[r];
  row.forEach((v,c)=>{
   const cell=t.getCell(r,c);cell.fill=r===0?C.ink:(r%2?C.white:C.pale);
   cell.text.style={typeface:'Calibri',fontSize:size,bold:r===0,color:r===0?C.white:C.ink,verticalAlignment:'middle',autoFit:'none',insets:{top:9,bottom:9,left:14,right:14}};
  });
 });
 return t;
}
async function photo(s,file,x,y,w,h,alt) {
 const bytes=await fs.readFile(file);
 s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:file.endsWith('.png')?'image/png':'image/jpeg',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
function titleBody(s,title,body,x,y,w,h=104) {
 text(s,title,x,y,w,42,31,{bold:true,color:C.teal});
 text(s,body,x,y+50,w,h,28);
}
const names = {baseline:'Baseline',reliability:'Reliability',interactions:'Interactions',combined:'Combined'};
const nv=demos.find(d=>d.source.includes('Brisbane_Lions'));
const violent=demos.find(d=>d.source.includes('English_Hooligans'));
const missed=demos.find(d=>d.source.includes('Germany_v_Poland'));
const sparse=demos.find(d=>d.usable_pose_fraction===0);
for(const d of [nv,violent,missed,sparse,external]){
 await fs.copyFile(path.join(results,d.video),path.join(output,'media',path.basename(d.video)));
 await fs.copyFile(path.join(results,d.snapshot),path.join(output,'media',path.basename(d.snapshot)));
}

// 1: minimal cover.
{
 const s=deck.slides.add();s.background.fill=C.ink;
 text(s,'IMPLEMENTATION DISCUSSION',72,82,1136,42,27,{color:'#91D5D1'});
 text(s,'Violence Detection\nin Crowded Videos',72,188,1110,210,76,{bold:true,color:C.white});
 text(s,'A working pipeline using human pose and relative interactions',72,450,1080,80,34,{color:'#D7E4EB'});
 text(s,'Vishal Gautam   U23AI127\nB.Tech Artificial Intelligence, SVNIT Surat\n24 October 2026',72,575,1110,102,26,{color:'#D7E4EB'});
 note(s,'Opening: My proposed framework now runs from a raw crowd video to extracted poses, clip-local tracks, motion features, a temporal classifier I trained, and an annotated output. Today I will show execution, measured pilot results and actual failure cases. The professor asked for end-to-end execution at this discussion stage. High accuracy is additional at this point, while the final stage requires stronger performance evidence. Keep the presentation short enough to allow discussion.',[path.join(root,'PROFESSOR_REQUIREMENTS.md'),path.join(root,'output/oct24/DEMO_GUIDE.md')]);
}
// 2: question and short literature context.
{
 const s=slide('Research question and foundation','The proposed additions remain hypotheses. Their value requires controlled evaluation.');
 text(s,'Can pose reliability and relative interactions distinguish violence\nfrom similar nonviolent crowd motion?',64,144,1152,106,37,{bold:true,color:C.teal});
 table(s,[['Foundation','What we use'],['RWF-2000, Cheng et al.','Motion as a reference signal for violence detection'],['Pose to Protect, Famouri et al.','Skeleton sequences as inputs to temporal models'],['FastPose + FL, Hegiste et al.','Pose-processing context from an industrial gesture task']],64,294,1152,[420,732],[58,76,76,76],27);
 text(s,'Current target: one violent or nonviolent label per short video clip.',64,608,1152,48,29);
 note(s,'The three foundation papers motivate different parts of the project and do not report directly comparable violence accuracies. Cheng et al. provide an RGB and optical-flow reference with RWF-2000. Famouri et al. study a skeleton-based crime-versus-normal sequence model. Hegiste et al. study industrial gestures, so those results cannot validate crowd violence. Skeleton violence detection and multi-person modeling already exist. Our narrow question is whether reliability and relative interactions add useful signal to a fixed temporal baseline. Identity, intent and individual guilt are outside the task. Avoid claiming that this combination is already novel.',[refs.rwf,refs.pose,refs.fast,path.join(root,'presentations/Stage1_Crowd_Violence_Detection.pptx')]);
}
// 3: full implementation in an editable table.
{
 const s=slide('The pipeline executes from raw video to output','Pretrained pose estimator. Locally trained temporal classifier.');
 table(s,[['Stage','Current implementation'],['1. Video input','Full decoding and 32 uniformly sampled frames'],['2. Multi-person pose','YOLO11n-pose, COCO-17 joints and confidence'],['3. Clip-local tracking','Hungarian association, up to 8 retained tracks'],['4. Feature construction','Body positions and velocities, masks and pair geometry'],['5. Temporal classifier','Shared per-person TCN, masked pooling, clip score'],['6. Annotated output','MP4 with score, threshold, tracks and pose-quality status']],64,145,1152,[350,802],[58,66,66,66,66,66,66],27);
 text(s,'Current inference uses the entire clip offline.',64,620,1152,40,29,{bold:true,color:C.teal});
 note(s,'Explain the whole chain rather than only the model. The supplied video is fully decoded and sampled. YOLO11n-pose is pretrained and estimates 17 joints per person. Tracking keeps observations associated within a clip and resets before the next clip. Feature construction uses body-centered positions, temporal differences and optional reliability and nearest-person interaction channels. The TCN weights are trained locally. Masks exclude absent observations during pooling. The saved model outputs a whole-clip score, and the MP4 displays that score along with sparse pose overlays. The current implementation does not produce precise event timestamps or person-level violence attribution.',[path.join(root,'affective/data.py'),path.join(root,'affective/pose.py'),path.join(root,'affective/tracking.py'),path.join(root,'affective/features.py'),path.join(root,'affective/model.py'),path.join(root,'affective/demo.py'),refs.yolo]);
}
// 4: controlled variants.
{
 const s=slide('All four proposed configurations are implemented','Fixed pose inputs, splits, encoder size and training budget across configurations.');
 table(s,[['Variant','Inputs','Channels','Parameters'],['Baseline','Normalized joints and velocities','68','36,001'],['Reliability','Baseline + confidence and validity','102','37,633'],['Interactions','Baseline + relative person geometry','76','36,385'],['Combined','Reliability + interactions','110','38,017']],64,166,1152,[220,542,150,240],[60,82,82,82,82],27);
 text(s,'Training observations define feature normalization.\nValidation loss selects the checkpoint. Validation macro-F1 selects the threshold.',64,579,1145,80,27);
 note(s,'All variants use the same missing-data placeholder policy, pose caches, train/validation/test split, hidden size 48 and epoch budget. Reliability weights observations with confidence and adds explicit validity channels. Interactions use nearest-person distance, offsets and relative velocities computed in common image coordinates before body centering. Input channels change parameter count, which is reported. Training uses seed 42, AdamW, a maximum of 180 epochs and patience 30. Only training observations determine normalization. Validation loss chooses the checkpoint and validation macro-F1 chooses the threshold. Do not imply a fair equal-parameter comparison when channel counts differ.',[path.join(root,'affective/features.py'),path.join(root,'affective/train.py'),path.join(results,'training_summary.json')]);
}
// 5: corrected data protocol and actual source evidence.
{
 const s=slide('Source review changed the pilot split','Matching source IDs and footage can appear under different filenames.');
 text(s,'147 training clips',64,144,360,50,36,{bold:true,color:C.teal});
 text(s,'48 validation clips',455,144,360,50,36,{bold:true,color:C.teal});
 text(s,'47 test clips',882,144,334,50,36,{bold:true,color:C.teal});
 text(s,'Folds 1-3 for training, fold 4 for validation and fold 5 for testing.\nThree related training clips excluded. All classifiers and normalization recomputed.',64,218,1152,84,28);
 await photo(s,source,64,323,1152,305,'Sampled Preston crowd footage across training and validation source-ID candidates');
 note(s,'The local release has 246 clips. One byte-identical duplicate within test fold 5 leaves 245 unique video files. Exact filename grouping originally missed truncated source IDs. Matching title/uploader pairs linked three training clips to validation sources. The two Preston clips show matching footage in sampled review. The Russia/Ukraine pair shares a prefix-compatible source ID but different sampled segments, so we grouped it conservatively. Excluding these three training clips leaves 242 selected clips. The original 48 validation and 47 test clips remain. All temporal models and linear controls were retrained with new training statistics. No known exact or prefix-compatible source-ID overlap remains, but hashes and filenames can miss other related footage. This correction follows inspection of the original test results, so the pilot remains exploratory.',[path.join(results,'correction.json'),path.join(results,'inventory.json'),source,path.join(results,'CORRECTION.md')]);
}
// 6: corrected measured results.
{
 const s=slide('Corrected pilot results','One split and seed 42. All 47 test clips remain in the reported metrics.');
 table(s,[['Variant','Accuracy','Macro-F1','ROC-AUC'],...runs.map(r=>[names[r.variant],pct(r.test.accuracy),dec(r.test.macro_f1),dec(r.test.roc_auc)])],64,161,1152,[420,244,244,244],[60,82,82,82,82],30);
 text(s,'Majority-class accuracy: 51.1%',64,572,530,42,29,{color:C.muted});
 text(s,'The additions have not consistently improved the baseline.',64,620,1090,40,29,{bold:true,color:C.teal});
 note(s,'These numbers come from the corrected source-group pilot, not the earlier run. Baseline and interactions each score 32 of 47 clips correctly. Interactions have higher ROC-AUC but the validation-selected threshold yields slightly lower macro-F1 and the same accuracy. Reliability scores 30 correctly and combined scores 31. This does not establish an improvement from either addition. The audit provides broad fixed-holdout bootstrap intervals, which omit seed and fold uncertainty. Do not claim significant differences from this small run. Accuracy was optional for the implementation discussion, so show these honest results after demonstrating execution.',[path.join(results,'training_summary.json'),path.join(results,'audit.json'),path.join(results,'CORRECTION.md')]);
}
// 7: correct outputs and portable playback links.
{
 const s=slide('Working video demonstrations','Examples from the fixed six-video demo set. These examples do not estimate accuracy.');
 text(s,'Dataset label: nonviolent',64,143,544,40,30,{bold:true,color:C.teal});
 text(s,'Dataset label: violent',672,143,544,40,30,{bold:true,color:C.teal});
 await photo(s,path.join(results,nv.snapshot),64,202,544,330,'Annotated held-out nonviolent video with score and tracked skeletons');
 await photo(s,path.join(results,violent.snapshot),672,202,544,330,'Annotated held-out violent video with score and tracked skeletons');
 text(s,`Prediction: nonviolent\nScore ${dec(nv.score)}, pose coverage ${pct(nv.usable_pose_fraction)}`,64,552,544,75,27);
 text(s,`Prediction: violent\nScore ${dec(violent.score)}, pose coverage ${pct(violent.usable_pose_fraction)}`,672,552,544,75,27);
 text(s,'Open nonviolent video',64,635,544,35,26,{color:C.teal,bold:true,link:`media/${path.basename(nv.video)}`});
 text(s,'Open violent video',672,635,544,35,26,{color:C.teal,bold:true,link:`media/${path.basename(violent.video)}`});
 note(s,'Play the nonviolent Brisbane crowd example and the violent English Hooligans example. Both belong to the first filenames from each held-out class in the fixed six-video set. The displayed examples are illustrative and not a new performance sample. A score above 0.54 yields the combined model violent decision unless pose quality triggers abstention. Explain that confidence in a visible body joint differs from the model clip score. Tracks identify associated observations in one clip only. Open the relative video links or use demo-index.html from the same folder. Keep the presentation folder and its media folder together.',[path.join(results,'demos.json'),nv.source,violent.source]);
}
// 8: full failure evidence.
{
 const s=slide('A missed violent clip shows the remaining limits','Combined model threshold 0.54. Full-clip scores and sparse pose overlays.');
 await photo(s,path.join(results,missed.snapshot),64,155,754,457,'A held-out violent clip classified as nonviolent despite high usable pose coverage');
 text(s,'Dataset label: violent',858,155,350,55,30,{bold:true,color:C.teal});
 text(s,`Prediction: nonviolent\nScore ${dec(missed.score)}\nPose coverage ${pct(missed.usable_pose_fraction)}`,858,225,350,142,29);
 text(s,'Usable poses do not guarantee a correct violence prediction.',858,419,350,104,30,{bold:true,color:C.amber});
 text(s,'Open missed-event video',64,632,750,36,27,{color:C.teal,bold:true,link:`media/${path.basename(missed.video)}`});
 note(s,'This Germany versus Poland clip is labelled violent but the model predicts nonviolent at 0.188, even with 96.9% usable sampled frames. Across the corrected test set, the combined model has six false positives and ten false negatives, with eleven errors above the 25% pose-coverage cutoff. Missing poses therefore cannot explain all failures. The external non-fight example also produces a false positive at score 0.844 after fresh pose extraction. It verifies raw-video execution, not external accuracy. At very low coverage, the demo flags insufficient pose evidence using an initial operational 25% cutoff. That cutoff is not a validated rejection rule and all test clips remain in the metrics. The current model cannot identify the violent person or precise event time.',[path.join(results,'failure_analysis/summary.json'),path.join(results,'demos.json'),path.join(results,'external_smoke.json')]);
}
// 9: signals and confounds, as editable evidence.
{
 const s=slide('Detection cues remain an important concern','Controls use the same corrected split. Their architecture differs from the temporal model.');
 const best=Math.max(...runs.map(r=>r.test.accuracy));
 const motion=controls.find(r=>r.variant==='motion_linear');
 const quality=controls.find(r=>r.variant==='pose_quality_only');
 table(s,[['Control / model','Inputs','Accuracy'],['Best skeleton variant','Joint positions and motion, optional interactions',pct(best)],['Motion linear control','Adjacent-frame differences and optical flow',pct(motion.test.accuracy)],['Pose-quality-only control','Seven detection counts and quality summaries',pct(quality.test.accuracy)]],64,155,1152,[370,552,230],[60,95,95,95],28);
 text(s,'Quality-only inputs contain no joint positions or trajectories.',64,534,1140,42,30,{bold:true,color:C.teal});
 text(s,'Scene, crowd density or detection behavior may explain part of the signal.\nSource-separated folds and seeds should test this before stronger claims.',64,590,1140,70,27);
 note(s,'The 80-feature motion control summarizes real adjacent decoded frame differences and Farneback flow near the original pose anchors. The seven-feature quality control uses usable-pose fraction, mean people, valid-joint fraction, total tracks, maximum detected people, discarded tracks and frames with people. It has no joint positions or trajectories. Both use training-only scaling and logistic coefficients. Validation log loss chooses motion regularization, quality C is fixed at 1 and validation macro-F1 chooses thresholds. Their different capacities and input access prevent a direct representation-superiority claim. The quality model accuracy suggests confounds worth investigating, not proof of a causal explanation. It also remains exploratory after prior test inspection.',[path.join(results,'motion/summary.json'),path.join(root,'affective/motion.py'),path.join(results,'motion/audit.json')]);
}
// 10: immediate status and final-stage obligations.
{
 const s=slide('Ready for discussion, with a clear next stage');
 titleBody(s,'Ready for 24 October','Raw-video inference and annotated output work.\nFour trained configurations and failure demos are available.',64,157,526,130);
 titleBody(s,'Next validation work','Review source footage and labels.\nRun source-separated folds and three seeds.\nMeasure full-pipeline latency.',686,157,526,165);
 titleBody(s,'Current limits','One exploratory split and one seed.\nWhole-clip output, without event timing\nor individual violence attribution.',64,410,526,144);
 titleBody(s,'Final-stage deliverables','Implementation and demonstration.\nMethods and results written at presentation.\nComplete draft of at least 12 pages\nbefore 20 November.',686,410,526,159);
 text(s,'Discussion: keep clip-level scope, or add flagged windows for the final stage?',64,637,1152,44,28,{bold:true,color:C.teal});
 note(s,'The pipeline is ready for the immediate implementation discussion. The saved-artifact audit reproduces four corrected temporal checkpoints and both linear controls, and all six held-out demos decode fully. A separate audit reproduces the raw-video example and decodes its output. These checks demonstrate consistency, not accuracy or deployment readiness. Ask the professor whether whole-clip output is enough or whether flagged windows should be implemented for the final stage. Keep scope focused on reliability and relative interactions until that discussion. The professor requires implementation, a demonstration and paper methods/results by the final presentation. A complete draft of at least 12 pages is due before 20 November. The final group date is still unconfirmed. Leave time for feedback.',[path.join(root,'PROFESSOR_REQUIREMENTS.md'),path.join(results,'audit.json'),path.join(results,'new_video_audit.json'),path.join(root,'paper/METHODS_AND_PILOT_RESULTS.md')]);
}

await fs.mkdir(path.join(build,'previews'),{recursive:true});
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidate);
console.log(`Exported ${deck.slides.items.length} slides`);
for(const [i,s] of deck.slides.items.entries()) {
 const stem=`slide-${String(i+1).padStart(2,'0')}`;
 await fs.writeFile(path.join(build,'previews',stem+'.png'),new Uint8Array(await (await deck.export({slide:s,format:'png',scale:1})).arrayBuffer()));
 await fs.writeFile(path.join(build,'previews',stem+'.layout.json'),await (await s.export({format:'layout'})).text());
 console.log('Rendered '+stem);
}
await fs.writeFile(path.join(build,'deck-inspect.ndjson'),(await deck.inspect({kind:'slide,textbox,table,notes',maxChars:200000})).ndjson);
await fs.writeFile(path.join(build,'links.json'),JSON.stringify(links,null,2));
if(process.argv.includes('--finalize')) {
 const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
 const owners=[2,3,4,6,9];
 const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:FINAL,pythonExecutable:PYTHON,
  integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry',...owners.flatMap(n=>['--require-native-table-slide',String(n)])],
  requiredNativeTableOwnerSlides:owners,fontPolicy,verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
 console.log(JSON.stringify(result));
 const finalized=await PresentationFile.importPptx(await FileBlob.load(FINAL));
 await fs.mkdir(path.join(build,'final-previews'),{recursive:true});
 for(const [i,s] of finalized.slides.items.entries()) {
  await fs.writeFile(path.join(build,'final-previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await (await finalized.export({slide:s,format:'png',scale:1})).arrayBuffer()));
 }
 console.log('Final slides rendered');
}


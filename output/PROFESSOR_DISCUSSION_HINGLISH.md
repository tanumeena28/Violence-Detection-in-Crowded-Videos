# Professor discussion aur demo: Hinglish rehearsal guide

Vishal Gautam, U23AI127. Current saved project ko 25 October 2026 ko review karke banaya gaya guide.

Project: **Violence Detection in Crowded Videos**, using pose reliability and relative interactions.

**Current position:** raw video se annotated prediction tak pipeline implemented hai. Chaar skeleton configurations trained hain. Corrected pilot results, controls aur demo videos available hain. Reliability aur interactions se consistent accuracy improvement abhi establish nahi hua. Final evaluation aur complete research manuscript pending hain.

## 1. Meeting mein kaunsi files use karni hain

| File | Kab dikhani hai |
|---|---|
| [Current implementation PPT](presentations/Oct24_Crowd_Violence_Implementation.pptx) | Main 10-slide presentation |
| [Corrected results aur six held-out demos](source_corrected/index.html) | Results, training curves aur videos |
| [Portable demo page](presentations/demo-index.html) | Five prepared playback examples ka fallback |
| [Existing 24 October playback package](presentations/Oct24_Presentation_and_Demos.zip) | Dusre laptop par offline playback. Extract karke presentation aur media folder saath rakhna |
| [Source correction](source_corrected/CORRECTION.md) | Dataset split correction explain karne ke liye |
| [Saved-artifact audit](source_corrected/AUDIT.md) | Verification aur uncertainty ke questions |
| [All test-clip diagnostics](source_corrected/failure_analysis/index.html) | Detailed failure discussion |
| [Methods aur preliminary results draft](../paper/METHODS_AND_PILOT_RESULTS.md) | Research writing ka current progress |
| [Professor requirements](../PROFESSOR_REQUIREMENTS.md) | Final deliverables aur dates |

Original project folder ki PPT current working copy hai. ZIP existing 24 October playback package hai. Latest explanation ke liye is guide aur corrected results ko use karo. Stage 1 presentation proposal-stage record hai; uske old progress statements ko current status ke roop mein present mat karna.

## 2. Starting mein exactly kya bolna hai

Ye opening lagbhag 60-90 seconds mein bol sakte ho:

> Sir, humare project ka aim crowded videos mein visible violence ko nonviolent activity se distinguish karna hai. Crowd mein cheering, running aur close contact bhi violence jaisa motion produce kar sakte hain. Saath mein occlusion aur low resolution ki wajah se body joints reliable nahi milte.
>
> Isliye maine human pose par based pipeline implement ki hai. Raw video se multiple logon ke joints extract hote hain, unke observations clip ke andar track hote hain, phir body motion aur relative interaction features temporal classifier ko diye jaate hain. Classifier ko local crowd dataset par train kiya hai. Output mein whole-clip score aur annotated video milta hai.
>
> Maine baseline, reliability, interactions aur combined, chaar configurations implement ki hain. Abhi corrected pilot evaluation aur working demos available hain. Proposed additions ka improvement abhi consistently establish nahi hua. Aaj main actual execution, measured results, failure cases aur next validation work explain karunga.

Iske baad problem, papers, pipeline, results, demo aur remaining work ke sequence mein baat karo. Code se presentation start karne ki zarurat nahi hai.

## 3. Problem aur motivation ko simple language mein explain karna

**Problem:** ek short crowd video ko violent ya nonviolent classify karna. Dataset ke supplied clip labels supervision dete hain.

**Difficulty:** fast movement apne aap mein violence ka reliable indicator nahi hai. Football crowd cheering kar sakta hai, log bhaag sakte hain, ya paas khade ho sakte hain. Dusri taraf actual aggressive act kuch logon aur kuch frames tak limited ho sakta hai. Crowd mein bodies overlap hoti hain, faces aur joints chhote dikhte hain, aur pose estimation fail kar sakta hai.

**Research question:** kya joint reliability aur relative person motion ko explicitly model karne se fixed skeleton baseline improve hota hai?

Professor ko bolo:

> Sir, sirf ye dekhna ki kitna motion hai enough nahi hai. Humein body posture aur logon ke relative movement ko dekhna hai. Saath mein humein account karna hai ki kuch joints missing ya low-confidence honge. Isi hypothesis ko chaar experiments se isolate karke test kiya hai.

**Affective Computing se connection:** body posture aur visible aggressive activity behavior ke cues hain. Current labels violent/nonviolent events ke hain. Model internal emotion, anger intensity, valence/arousal ya intent ko directly measure nahi karta.

**Privacy wording:** downstream classifier skeleton features use karta hai. Pose extractor RGB images process karta hai, aur current demo original video par overlay dikhata hai. Is implementation ko guaranteed anonymous ya formally privacy-preserving system mat kehna.

## 4. Starting se ab tak work ka sequence

| Phase | Kya kiya | Kyu kiya | Current output |
|---|---|---|---|
| Literature | RWF-2000, Pose to Protect aur FastPose + FL papers compare kiye | Task, pose representation, temporal modeling aur evaluation context samajhne ke liye | Foundation comparison in the PPT |
| Preliminary pose study | FederatedHAR gesture data aur privacy-related experiments inspect kiye | Skeleton representation aur normalization samajhne ke liye | Exploratory gesture/privacy artifacts. Ye crowd violence results nahi hain |
| Scope | Crowd clip classification aur reliability/interaction study define ki | Feasible, testable research question banane ke liye | Four controlled configurations |
| Data preparation | Violent-Flows inventory, full decoding, duplicate removal aur source grouping | Invalid sampling aur train/holdout overlap reduce karne ke liye | Corrected manifest |
| Pose pipeline | YOLO11n-pose, sampling, tracking, normalization aur caches | Raw videos ko structured temporal inputs mein convert karne ke liye | Cached multi-person pose inputs |
| Model training | Shared per-person TCN ke chaar variants train kiye | Har addition ka separate effect test karne ke liye | Four saved checkpoints and predictions |
| Source correction | Truncated IDs se linked three training clips exclude karke retrain kiya | Related footage ko partitions mein alag rakhne ke liye | 147 train, 48 validation, 47 test |
| Diagnostics | Motion control, quality-only control, failure analysis aur video audits | Model kis signal par depend kar raha hai aur kahan fail hota hai, investigate karne ke liye | Control metrics and all test-clip diagnostics |
| Demonstration | Offline annotated MP4s, raw-video inference path aur implementation PPT prepare ki | Professor ko execution dikhane ke liye | Working demo materials |
| Writing | Methods aur current preliminary results draft kiye | Final paper ko actual implementation aur evidence par base karne ke liye | Working manuscript text, complete 12-page paper pending |

Saved records mein initial pilot 21 October aur source correction 22 October ka hai. Existing implementation deck 24 October discussion ke liye prepare hui thi. Is guide mein current corrected results use hue hain.

## 5. Research papers: professor ko kya batana hai

### P7: RWF-2000 and Flow Gated Network

**Paper:** Ming Cheng, Kunjing Cai and Ming Li, *RWF-2000: An Open Large Scale Video Database for Violence Detection*. ICPR 2020. arXiv first submission 2019, inspected v3 October 2020. [Local PDF](../P7_1911.05913v3.pdf), [official arXiv page](https://arxiv.org/abs/1911.05913).

**Problem:** surveillance videos mein violence classification.

**Data:** 2,000 clips, each around five seconds.

**Method:** RGB appearance stream aur optical-flow motion stream use karta hai. Flow Gated Network motion information se appearance features ko gate karta hai. Paper ka ablation RGB-only, flow-only aur fusion compare karta hai.

**Reported RWF-2000 test accuracy:** RGB-only 84.50%, flow-only 75.50%, best fusion 87.25%, about 0.27 million parameters.

**Humne kya liya:** motion ko reference signal samajhna, aur proposed changes ko ablation se test karna. Current model TCN hai; paper ka full Flow Gated Network reproduce nahi kiya. Apna 80-feature optical-flow control ek handcrafted linear diagnostic hai.

**Limit:** paper crowd data par optical flow ki difficulty discuss karta hai, especially camera motion, low image quality aur optical-flow assumptions ke breakdown ke context mein.

Bolne ki line:

> Sir, RWF-2000 paper se violence task aur motion-based reference ka foundation liya. Unka 87.25% unke RWF-2000 protocol par hai. Humara corrected pilot Violent-Flows ke 47 test clips par hai, isliye ye directly comparable scores nahi hain.

PDF mein Figure 4 architecture aur Tables III/V results dikhane layak references hain, agar professor detail pooche.

### P5: Pose to Protect

**Paper:** Dina Famouri, Md Zarif Hossain and Ahmed Imteaj, *Pose to Protect: Federated Skeleton-Based Anomaly Detection for Privacy-Conscious Video Surveillance*. ICCV Workshops 2025, pages 3545-3553. [Local PDF](../P5_Famouri_Pose_to_Protect_Federated_Skeleton-Based_Anomaly_Detection_for_Privacy-Conscious_Video_ICCVW_2025_paper.pdf), [CVF reference page](https://openaccess.thecvf.com/content/ICCV2025W/WiCV/html/Famouri_Pose_to_Protect_Federated_Skeleton-Based_Anomaly_Detection_for_Privacy-Conscious_Video_ICCVW_2025_paper.html).

**Problem:** crime versus normal sequence classification.

**Data:** 496-video subset of UCF-Crime, including fighting, shooting, assault, robbery and normal.

**Method:** one-second interval frame sampling, OpenPose with 25 keypoints, up to two people, x/y/confidence values. Per-frame input has 2 x 25 x 3 = 150 values. A temporal LSTM with hidden size 512 performs classification. The main federated setup uses seven clients. Figure 4 studies different client counts; the text reports AUC above 0.85 across those configurations.

**Humne kya liya:** skeleton sequences ko temporal classifier ka input banana aur crowd pose failure ko important limitation treat karna.

**Difference:** hum COCO-17 joints with YOLO11n-pose use karte hain, up to eight retained tracks, and a small TCN. Humara current experiment centralized training hai. Federated training implemented nahi hai.

Bolne ki line:

> Sir, ye closest pose-based foundation hai. Lekin unka task crime versus normal hai aur input do logon tak limited hai. Hum crowd clips mein reliability aur relative interactions ka controlled effect test kar rahe hain. Skeleton use karne se formal privacy guarantee establish nahi hoti.

PDF mein Sections 4.1.1/4.1.2 data aur two-person input explain karte hain. Figure 4 federated metrics dikhata hai. Kisi unspecified figure se exact accuracy guess mat karna.

### P3: FastPose and federated action recognition

**Paper:** Vinit Hegiste, Vidit Goyal, Tatjana Legler and Martin Ruskowski, *Federated Action Recognition for Smart Worker Assistance Using FastPose*. FLTA 2025. [Local PDF](../P3_16215_FLTA2025_paper_(1).pdf), [official arXiv page](https://arxiv.org/abs/2508.14113).

**Problem:** industrial worker gestures recognize karna.

**Data:** five participants and eight upper-body gestures. Modified FastPose gives 13 joints, so 26 coordinates per frame; temporal windows contain 20 frames.

**Method:** LSTM and Transformer models under centralized, local, FedAvg and federated ensemble training.

**Reported global Transformer accuracies:** centralized 57.1%, FedAvg 69.5%, federated ensemble 73.4%. FedAvg gain 12.4 percentage points hai, relative 12.4% improvement nahi.

**Humne kya liya:** pose-processing context, controlled evaluation ka importance aur preliminary representation experiments ke liye public gesture data.

**Limit:** clean industrial gestures se dense crowd violence par transfer automatically establish nahi hota. Humne paper ke complete federated result ko reproduce nahi kiya.

Bolne ki line:

> Sir, is paper ka use pose aur experimental context ke liye hai. Iski gesture accuracy ko humare violence result ke roop mein report nahi kar rahe. Current violence pipeline ka classifier locally trained TCN hai.

PDF mein Figure 5 workflow, Table I global results aur Table II external subject evaluation useful hain.

### Violent-Flows dataset paper aur related-work boundaries

Tal Hassner, Yossi Itcher and Orit Kliper-Gross, *Violent Flows: Real-Time Detection of Violent Crowd Behavior*, CVPR Workshops 2012, is the primary dataset reference. Official database page reports 246 videos. [Dataset and paper source](https://www.openu.ac.il/home/hassner/data/violentflows/).

Stage 1 references mein Garcia-Cobo and SanMiguel ka *Human skeletons and change detection for efficient violence detection in surveillance videos* (CVIU, 2023, [DOI](https://doi.org/10.1016/j.cviu.2023.103739)) aur Truong and Hoang ka *Skeleton-based multi-person action recognition towards real-world violence detection* ([author laboratory listing](https://cvis.hcmute.edu.vn/Publications/Details/279)) bhi hain. Final related-work comparison mein inki full methods/results aur publisher metadata verify karne hain. Lab listing ko final publisher bibliography samajh kar copy mat karna.

**Contribution wording:** skeleton-based violence detection, motion features aur multi-person processing already literature mein hain. Humara candidate contribution reliability aur nearest-person interactions ka controlled study, together with source correction, failure analysis aur scene/detection controls hai. Final claim experiments aur closest related work ke comparison se decide hoga.

## 6. End-to-end pipeline: har step aur uska reason

### Step 1: Video inventory, decoding aur sampling

Raw video ko fully decode karte hain. Clip se 32 uniformly spaced frames select hote hain.

**Why:** fixed temporal input and manageable pose-extraction cost. Container header ka frame count kabhi inaccurate ho sakta hai, isliye actual decoded frames use hote hain. Uniform sampling short events miss kar sakti hai; ye current limitation hai.

### Step 2: Multi-person pose extraction

Pretrained YOLO11n-pose COCO ke 17 joints deta hai, including x/y coordinates and confidence. Extraction image size 640, person detection confidence 0.2 aur joint validity threshold 0.25 hai.

**Why:** body posture aur motion ko compact inputs mein convert karna. YOLO11n-pose ko scratch se train nahi kiya; downstream temporal classifier locally train kiya.

### Step 3: Clip-local tracking

Hungarian association box overlap and center distance se observations match karta hai. Track IDs har new clip par reset hote hain. Joint signal ke basis par up to eight tracks retain hote hain.

**Why:** time ke across consistent person slots chahiye, warna different people's observations ka mixture motion ko distort karega. Tracking perfect nahi hai. Occlusion, cuts aur large motion se tracks fragment ho sakte hain. Eight retained tracks ka cap hai; unlimited crowd tracking ka claim nahi hai.

### Step 4: Normalized body motion

Positions valid hips ke mean par center hote hain; hips unavailable hon to box center fallback hai. Box diagonal se scale normalize hota hai. Velocity actual sampled time differences use karti hai. Missing joints mask hote hain; temporal difference tab valid hota hai jab dono observations mein joint valid ho.

**Why:** absolute frame position aur apparent size ke influence ko reduce karna, aur missing joints se artificial velocity spikes avoid karna.

### Step 5: Reliability features

Positions and velocities confidence se weight hote hain. Seventeen confidence values aur seventeen validity flags additional channels hote hain.

**Why:** low-confidence observations ko explicitly represent karna. Detector confidence correctness ki calibrated probability nahi hai. Baseline bhi common missing-joint policy use karta hai; reliability variant ka extra effect confidence weighting and explicit channels hai.

### Step 6: Relative interactions

Har present track ke nearest present neighbor ke liye eight channels: distance, two offsets, two relative-velocity components, signed approach/separation measure, normalized neighbor count aur neighbor-present flag.

**Why:** kisi person ka movement surrounding person ke relation mein describe karna. Ye full all-pairs graph model nahi hai. Interaction geometry common image coordinates mein body centering se pehle calculate hoti hai. Har body ko origin par center karne ke baad inter-person distance calculate karoge to actual scene separation lose ho jayega.

### Step 7: Temporal classification

Same small TCN har person's sequence encode karta hai. Hidden size 48, residual temporal blocks with dilations 1/2/4. Masked temporal pooling ke baad observed people ki mean/max representations aur coverage scalar classifier ko feed hote hain.

**Why:** multiple frames ke patterns learn karna, and person slots ke ordering se output ko independent rakhna. Current network final whole-clip score deta hai. Individual violent-person labels available nahi hain, aur model unko output nahi karta.

### Step 8: Decision and annotation

Combined model ka validation-selected threshold 0.54 hai. Enough pose evidence par score threshold se compare hota hai. Usable sampled frames 25% se kam hon to demo `insufficient pose evidence` dikhata hai. Usable frame ke liye retained people mein kahin at least five joints 0.25 confidence threshold pass hone chahiye.

**Why:** very weak pose input ko confident-looking final decision ke roop mein display karna misleading hoga. Ye 25% cutoff initial operational rule hai. All 47 test clips normal metrics mein included hain, including low-coverage clips.

Annotated MP4 mein score, track overlays aur quality status dikhte hain. Score whole clip ka hai. Pose overlays nearest sampled frame se aate hain; har video frame par fresh pose inference nahi hota.

Demo ka `Time` current video position hai, inference latency ya detected event onset nahi. `Dataset label` supplied reference label hai; ye displayed comparison ke liye hai, classifier ka input nahi. `Visible tracks` retained observations ka current display count hai, total crowd size ka reliable estimate nahi.

## 7. Four configurations and training

| Configuration | Feature channels | Parameters | Meaning |
|---|---:|---:|---|
| Baseline | 68 | 36,001 | 17 x 2 positions + 17 x 2 velocities |
| Reliability | 102 | 37,633 | Baseline with confidence weighting and 34 explicit confidence/validity values |
| Interactions | 76 | 36,385 | Baseline plus eight nearest-neighbor features |
| Combined | 110 | 38,017 | Reliability and interactions together |

Combined per-clip shape `[32, 8, 110]` hai. Batch size one ke saath inference input `[1, 32, 8, 110]` hota hai.

Common settings: same pose caches and missing-data policy, corrected split, hidden size 48, seed 42 and tuning budget. Extra channels parameter count change karte hain, isliye equal-parameter experiment ka claim nahi hai.

Training uses AdamW, learning rate 0.001, weight decay 0.01, batch size 16, positive-weighted binary cross-entropy, gradient clipping, maximum 180 epochs and patience 30. Maximum budget ka matlab 180 actual executed epochs nahi hai. Saved runs executed 35/32/35/34 epochs for baseline/reliability/interactions/combined; selected checkpoints epochs 5/2/5/4 ke hain.

Training-only observations normalization statistics define karte hain. Validation loss checkpoint choose karti hai. Validation macro-F1 threshold choose karta hai. Test scores in decisions ko select nahi karte.

## 8. Dataset split and correction explain karna

Local Violent-Flows release: 246 videos, 123 per class. One byte-identical nonviolent duplicate in test fold 5 remove hua, leaving 245 unique files. All unique files ke poses cached hain. Three related training clips remove hone ke baad current selected evaluation mein 242 clips hain.

| Partition | Clips | Class breakdown |
|---|---:|---|
| Training, folds 1-3 | 147 | 75 nonviolent, 72 violent |
| Validation, fold 4 | 48 | 24 per class |
| Test, fold 5 | 47 | 23 nonviolent, 24 violent |

Bolne ki line:

> Sir, initial exact grouping truncated source IDs miss kar rahi thi. Source review mein matching titles/uploaders aur prefix-compatible IDs se three training clips validation sources se linked mile. Unko exclude karke same validation/test clips retain kiye. Training normalization aur saare classifiers recompute kiye.

Two Preston pairs mein sampled matching footage mila. Russia/Ukraine pair source ID match ki wajah se conservatively group hua, though sampled segments different the. No known exact/prefix-compatible source overlap remains. Other related footage filename/hash checks se miss ho sakti hai.

Original test scores correction se pehle inspect ho chuke the. Isliye corrected pilot exploratory hai. Isko fresh untouched benchmark mat describe karna. Full five-fold evaluation abhi complete nahi hui.

RWF-2000 ke 2,000 clips locally available hain; current crowd TCN ka full RWF training/evaluation complete nahi hua. One RWF non-fight clip inference path check ke liye use hua. RLVS current confirmed experiment ka part nahi hai.

## 9. Results ko honestly present karna

| Model | Correct / 47 | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| Baseline | 32 | 68.1% | 0.680 | 0.808 |
| Reliability | 30 | 63.8% | 0.638 | 0.781 |
| Interactions | 32 | 68.1% | 0.679 | 0.850 |
| Combined | 31 | 66.0% | 0.658 | 0.786 |
| Adjacent-frame motion linear control | 35 | 74.5% | 0.744 | 0.766 |
| Pose-quality-only linear control | 36 | 76.6% | 0.764 | 0.873 |

Majority-class accuracy 51.1% hai. One test clip approximately 2.13 percentage points accuracy change karta hai. Small score differences reliable improvement establish nahi karte.

Bolne ki line:

> Sir, baseline aur interaction model ki accuracy same hai. Interaction AUC better hai, lekin validation-selected decision threshold par improvement consistent nahi hai. Combined model baseline se lower score karta hai. Is pilot se combination ko superior claim nahi kar sakte.

**Metrics ka meaning:** accuracy overall correct decisions hai. Violent precision predicted violent clips mein correct violent fraction hai. Recall actual violent clips mein detected fraction hai. Macro-F1 dono classes ko equal importance deta hai. ROC-AUC threshold-independent score ranking evaluate karta hai; better AUC automatically better chosen-threshold accuracy nahi deta.

**Combined confusion matrix:** 17 true negatives, six false positives, ten false negatives, 14 true positives. Violent precision 70.0%, violent recall 58.3%. Actual 24 violent clips mein ten miss hue. Audit ka approximate fixed-holdout 95% accuracy interval 53.2%-78.7% hai. Is interval mein seed/fold uncertainty include nahi hai.

**Pose observation:** corrected selected clips ki mean usable coverage 74.3%; 31 clips below 25%. Test mein nine below cutoff hain. Combined ke 16 errors mein 11 clips cutoff se above hain. Low coverage sab failures explain nahi karti. Usable coverage ground-truth pose accuracy ka measurement nahi hai.

### Controls ne kya reveal kiya

Motion control 80 descriptors use karta hai: actual adjacent decoded-frame differences and Farneback flow around sampled anchors. Ye full published deep RGB/flow reference nahi hai.

Quality-only control ke seven inputs: usable fraction, mean detected people, valid-joint fraction, total tracks, maximum people, discarded tracks aur frames with people. Ismein joint positions/trajectories nahi hain.

> Sir, quality summaries se hi 76.6% aa raha hai. Ye concern raise karta hai ki scene type, crowd density ya detector behavior labels se associated ho sakte hain. Humein source-separated folds aur seeds par test karna hai ki signal actual violent body motion se aata hai ya shortcuts se.

Ye possible confound hai, proven causal explanation nahi. Controls and TCN ki architecture/input access different hai, isliye unke scores se pose representation ki general inferiority claim nahi karni.

## 10. Actual PPT ke slide-wise speaking points

1. **Title:** opening do. State end-to-end implementation and preliminary results. Around 45 seconds.
2. **Research question and foundation:** cheering/running ambiguity, pose unreliability, and three papers' separate roles. Mention that additions are hypotheses. Around 60-90 seconds.
3. **Pipeline:** video input se annotated MP4 tak har row explain karo. Pretrained pose extractor aur locally trained TCN distinguish karo. Around 90 seconds.
4. **Four configurations:** A/B/C/D ablation ka purpose. Baseline 68 channels and combined 110. Same caches/split/budget, training-only normalization, validation selection. Around 60 seconds.
5. **Source correction:** 246 initial, duplicate ke baad 245 unique, related train clips exclude hone ke baad 242 selected. Split 147/48/47. Around 45 seconds.
6. **Results:** corrected table explain karo. Accuracy improvement establish nahi hua. One split/seed and majority 51.1% mention karo. Around 60 seconds.
7. **Working demonstrations:** nonviolent aur violent video play karo. Score, threshold, joints and clip-local IDs explain karo. Around 90 seconds.
8. **Failure:** missed violent clip play karo. High usable coverage ke bawajood error explain karo. Around 60 seconds.
9. **Controls:** motion and quality-only results. Possible dataset/detection shortcuts explain karo. Around 60 seconds.
10. **Next stage:** specific pending experiments, full-pipeline timing and paper. Scope/date/template ke liye professor feedback lo. Around 45 seconds.

Roughly 10-12 minutes prepared presentation, followed by discussion. Short meeting ho to detailed training settings aur preliminary privacy work questions ke liye reserve karo.

## 11. Demo ka exact sequence aur kya bolna hai

PowerPoint mein `F5` full slideshow start karta hai. Current slide se `Shift+F5` use kar sakte ho. Presenter View ya Notes pane mein existing English speaking notes aur source links hain. Is guide se Hinglish rehearse karo.

Slides 7 and 8 ke videos external local MP4 links hain, embedded video nahi. `media` folder presentation ke adjacent rehna chahiye. Browser fallback pehle open karke rakhna. `Esc` aur `Alt+Tab` se PPT aur browser/player switch kar sakte ho.

### A. Correct nonviolent example

[Play nonviolent Brisbane crowd](source_corrected/demos/nonviolent_907f54265076af88.mp4).

Dataset label nonviolent. Prediction nonviolent. Score 0.114, combined threshold 0.54, usable pose coverage 59.4%.

> Sir, ye held-out nonviolent crowd example hai. Skeleton overlays sampled body observations hain. Model whole clip ka score deta hai. Score threshold se below hai, to output nonviolent hai. IDs clip ke andar association ke liye hain.

### B. Correct violent example

[Play violent English Hooligans example](source_corrected/demos/violent_dc1b654139c8c90f.mp4).

Dataset label violent. Prediction violent. Score 0.943, coverage 93.8%.

> Sir, is violent-labelled clip ka score threshold se above hai. Ye pipeline ka correct example hai. Single demo se accuracy estimate nahi hoti; full 47-clip table performance evidence hai.

Score ko 94.3% calibrated certainty mat bolna.

### C. Missed violent clip

[Play Germany versus Poland failure](source_corrected/demos/violent_59a24584d1abb3ee.mp4).

Dataset label violent. Prediction nonviolent. Score 0.188, usable coverage 96.9%.

> Sir, ye important failure hai. Usable pose observations high hain, phir bhi model violence miss karta hai. Pose coverage alone enough nahi hai. Temporal sampling, tracked participants, labels, motion context aur classifier generalization ko investigate karna hai.

Specific error cause ko verified explanation mat present karna; current diagnostics cause establish nahi karte.

### D. Insufficient-pose example

[Play low-pose Brazilian crowd](source_corrected/demos/nonviolent_f895027aa901e894.mp4).

Usable coverage zero. Demo `insufficient pose evidence` dikhata hai.

> Sir, yahan enough body observations nahi milte. Display abstain karta hai. Ye operational cutoff hai, validated rejection model nahi. Metrics mein clip phir bhi included hai.

### E. External raw-video execution check

[Play RWF non-fight output](source_corrected/demos/new_video_66aa5cc52df4ca32.mp4).

Source is a non-fight-labelled RWF-2000 clip. Corrected model predicts violent at 0.844. This example was inspected earlier.

> Sir, ye new-video inference path ka documented execution check hai. Pose extraction aur output generation execute hue, lekin classification false positive hai. Ek previously inspected external clip se external accuracy claim nahi kar rahe.

Prepared demos correctness ke basis par filter nahi hue. Six held-out examples first filenames from each class se selected the.

## 12. Live execution commands

Meeting se pehle project root par:

```powershell
Set-Location -LiteralPath 'C:\Users\Vishal Gautam\Desktop\Affective Lab\AffectiveProject'
.\scripts\show_pipeline.ps1 -VerifyOnly
```

Guide prepare karte waqt ye command pass hui: four saved checkpoints and six fully decoded demo videos. Verification label correctness ya final generalization establish nahi karti.

Meeting mein selected raw file ke liye:

```powershell
.\scripts\show_pipeline.ps1 -Video 'C:\path\to\video.mp4'
```

`C:\path\to\video.mp4` ko actual input path se replace karna. Script saved corrected model verify karta hai, pose extraction/inference runs karta hai, output decode check karta hai aur result page update karta hai. Compatible pose cache repeat run par reuse ho sakta hai. Demo fresh model training nahi karta.

Existing external sample ka runnable command:

```powershell
.\scripts\show_pipeline.ps1 -Video '.\data\RWF-2000\val\NonFight\etyiEs3j8x8_1.avi'
```

Outputs `output/source_corrected/new_video_demo.json`, `output/source_corrected/demos/new_video_*.mp4` aur result page mein milte hain.

During execution bolo:

> Sir, ye saved trained classifier par inference hai. Input video se pose representation aur prediction generate ho rahe hain. Agar cache available ho to extraction reuse ho sakta hai. Training evaluation ko separate saved experiment ke roop mein report kiya hai.

Offline videos laptop par ready rakho. Portable ZIP playback package executable training environment nahi hai; live inference ke liye original project's Python environment, weights aur input videos chahiye.

## 13. Kitna complete hai aur kya baaki hai

| Component | Status |
|---|---|
| Foundation papers and scoped research question | Available |
| Video preparation and known source correction | Implemented. Further manual source review pending |
| Multi-person poses, tracking, features and cache provenance | Implemented |
| Four TCN variants and corrected saved predictions | Trained and verified |
| Two signal controls | Implemented and evaluated on the same exploratory split |
| Offline demos and raw-video inference | Working |
| Failure diagnostics | Available. Full-video label/source review still required |
| Five folds and three seeds | Pending |
| Stronger RGB/motion comparison | Pending |
| Meaningful external dataset evaluation | Pending. One smoke-test clip available |
| Measured full-pipeline latency | Pending |
| Flagged temporal windows | Not implemented/evaluated. Scope decision required |
| Person-level violence attribution | Not implemented and not current agreed core scope |
| Federated training and formal differential privacy | Not implemented in current violence pipeline |
| Methods and preliminary results text | Drafted |
| Complete 12-page manuscript | Pending |

Percentage ki jagah milestones explain karna:

> Sir, implementation pipeline aur pilot stage complete hai. Final experimental validation aur complete paper stage pending hai. Four variants run ho chuke hain; remaining main work stronger evidence generate karna hai.

## 14. Next work: priority order

1. Complete suspicious full-video source and label review. Predictions ke basis par labels casually change mat karna.
2. Freeze a documented evaluation protocol, with source groups kept together. Existing inspected folds ko untouched holdout describe mat karna.
3. Run skeleton variants and diagnostics across source-separated folds and three seeds. Mean/spread and uncertainty report karo.
4. Compare a stronger RGB/motion reference and meaningful external RWF evaluation. Linear controls ko published deep baseline mat label karna.
5. Define a rubric for actual occlusion, crowd conditions and high-motion nonviolent clips. Report false positives and misses in these groups.
6. Measure full pipeline on specified hardware: video decode, pose estimation, tracking, features, classifier and annotation as appropriate to the stated use case.
7. Professor se flagged windows ki necessity confirm karke scope finalize karo. Window output add karne par timestamp/localization evaluation bhi define karni hogi.
8. Update paper figures/results and finalize bibliography. Add limitations, reproducibility and related-work comparison based on verified evidence.

Current record final presentation date ko unconfirmed rakhta hai. Offered dates 29/30/31 October options the. Complete paper at least 12 pages and before 20 November 2026 required hai. 19 November ko internal finished-draft target rakhna sensible hai.

## 15. Apne research paper ki story

Current title: **Crowd Violence Detection with Pose Reliability and Relative Interactions**.

Current working text [Methods and Pilot Results](../paper/METHODS_AND_PILOT_RESULTS.md) mein available hai. Ye complete formatted 12-page manuscript nahi hai.

Paper ki research question wahi honi chahiye jo implementation test karta hai. Suggested structure:

1. Abstract with actual conclusion.
2. Introduction: crowd ambiguity, pose failure and question.
3. Related work: RGB/flow, skeleton violence, interactions and reliable observations.
4. Dataset, duplicate/source checks and evaluation protocol.
5. Pose/tracking/features, TCN and four configurations.
6. Experimental settings and signal controls.
7. Actual results with uncertainty.
8. Failure analysis, high nonviolent motion and pose limitations.
9. Scope/privacy limitations, reproducibility and conclusion.
10. Verified references.

> Sir, methods aur preliminary results ka draft already available hai. Final paper mein improvement ka claim final controlled evidence ke basis par decide karenge. Agar quality/detection cues dominate karte hain, us finding ko clear limitation aur research result ke roop mein report karenge.

Twelve pages real method, analysis and references se complete karni hain. Results invent ya filler add karne ki zarurat nahi hai.

## 16. Preliminary gesture/privacy work: agar professor pooche

FederatedHAR experiment main violence metric se separate hai. Saved privacy-utility JSON mein raw coordinates se five-subject identification 59.3%, hip-centering ke baad 35.2%, velocity-only 23.8% hai. Uniform five-way chance 20% aur saved majority reference about 26.6% hai.

Hip-centering identity/session linkage reduce karta hai. It does not eliminate all leakage. Motion-only representation ne gesture utility bhi severely reduce ki. Gesture utility ke original within-block split mein temporal adjacency hai, isliye high absolute gesture accuracy ko robust transfer/generalization result mat describe karna. Single recording session per subject mein identity aur recording conditions separate nahi hote.

Bolne ki line:

> Sir, preliminary gesture dataset par skeleton coordinates mein subject/session information milti hai, aur body centering usko reduce karta hai. Ye normalization choice ko motivate karta hai. Ye privacy guarantee ya crowd violence accuracy nahi hai.

P3 released centralized training file mein earlier inspection ne truncation record ki: 13,441 complete feature rows versus 26,403 labels. Published repaired file per-client concatenation se match karta hai. Agar ye point discuss karo, authors ne kis file par training ki thi uske baare mein claim mat karna. Ye reproducibility/data-integrity observation hai.

## 17. Likely professor questions: ready answers

| Question | Hinglish answer |
|---|---|
| Apne aap kya train kiya? | Small TCN violence classifier ke four variants locally train kiye. YOLO11n-pose pretrained feature extractor hai. |
| P7 ka 87.25% aur tumhara 68.1% kyu different? | Dataset, split, representation aur protocol different hain. Same protocol par reproduction ke bina direct performance comparison valid nahi hai. |
| Reliability ya combined better kyu nahi hua? | Hypothesis abhi support nahi hui. Small data, pose/tracking errors, sampling aur detection/scene cues plausible factors hain. Controlled runs aur diagnostics se test karna hai. |
| Interactions ka AUC better hai to model better hai? | Score ranking better hai on this split, lekin fixed validation-selected threshold par accuracy same hai. One small split se general superiority establish nahi hoti. |
| Quality-only ka result important kyu? | Body trajectories ke bina labels predictable hain. Possible dataset/scene shortcuts investigate karne hain. Ye causal proof nahi hai. |
| Kya violent person identify hota hai? | Current output one clip score hai. Track IDs person-level violence labels nahi hain. Attribution ke liye model/supervision/evaluation extension chahiye. |
| Exact event timestamp milta hai? | Current inference full clip offline hai. Flagged windows not implemented/evaluated. |
| Real-time hai? | Full-pipeline real-time performance establish nahi hui. Saved fresh external extraction about 7.4 seconds aur warmed CPU classifier about 3 ms tha; ye component timings hain. |
| Skeleton privacy guarantee hai? | Guaranteed nahi. RGB pose extractor aur current annotated videos appearance process/display karte hain. Skeletons bhi identity/session cues retain kar sakte hain. |
| Pose fail ho to kya hota hai? | Demo below 25% usable sampled frames par insufficient evidence display karta hai. Ye initial quality rule hai; all test clips metrics mein included hain. |
| Five-fold evaluation hui? | Current pilot folds 1-3 train, 4 validation, 5 test hai. Full outer five-fold and three-seed runs pending hain. |
| Source leakage fully solve hui? | Known exact and prefix-compatible overlaps remove hue. Other related footage miss ho sakti hai. Manual review pending hai. |
| Final paper complete hai? | Methods/preliminary results draft hai. Complete at least 12-page manuscript pending hai, before 20 November requirement ke liye. |
| Novel contribution kya hai? | Reliability and relative interactions ka controlled evaluation candidate contribution hai. Final novelty closest literature and final results se establish karni hai. |

## 18. Meeting end par kaise close karna hai

> Sir, raw-video pipeline, trained variants aur annotated demos ready hain. Pilot se consistent improvement establish nahi hua aur quality-only result ne possible shortcuts ka concern raise kiya hai. Main next stage mein source review, multiple folds/seeds, stronger reference aur full-pipeline timing complete karna chahta hoon. Methods aur current results writing already available hai. Aapke feedback se clip-level scope aur flagged windows ki requirement finalize karunga.

Professor se four points discuss karna: final clip/window scope, next experiment priority, group's final presentation date, and paper template. Discussion ke liye time leave karna.

## 19. Meeting se pehle short preparation list

- Laptop plugged in and environment/weights locally available.
- Current implementation PPT and corrected results page already open.
- One terminal already at the project root.
- Nonviolent, violent, missed-event and insufficient-pose videos ready.
- Slides 7/8 local playback links checked, media folder intact.
- Papers bookmarked at useful figures/tables; manuscript draft one click away.
- Memorize 147/48/47, 68.1% baseline, 66.0% combined, 76.6% quality-only, and the current whole-clip output scope.

Numbers in this guide are based on corrected `training_summary.json`, `motion/summary.json`, `demos.json`, the current PPT, manuscript draft and cited local papers. Earlier archived pilot scores are not the current reported results.

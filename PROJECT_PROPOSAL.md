# Violence and Goon Detection in a Crowd or Protest

### A privacy-preserving skeleton-based approach, with a measured audit of what the representation conceals

**B.Tech Final Project Proposal** · Vishal Gautam
Prepared 13 October 2026 · Substantially revised 15 October 2026 · Target: paper draft within 13 days

---

## 1. Problem and approach

Crowds and protests are the setting where manual video monitoring fails most completely: many people, many cameras, and rare events that unfold in seconds. Most violence in such a scene involves a small number of individuals within a large crowd, which means a useful system must report not only that violence occurred but which person committed the act.

This setting also raises the stakes on how the detection is done. Protest is lawful assembly, and surveillance of assembly has a documented chilling effect. A system that identifies individuals at a protest has caused harm even when it is perfectly accurate. Unlike most computer vision applications, then, the choice of input representation here is an ethical decision and not only an engineering one.

The approach this project takes is to detect violence from 2D pose skeletons rather than from pixels, so that appearance, clothing and face are never processed; to attribute the violent act to a specific person in the scene; and — because the recent literature asserts rather than tests the privacy of skeleton representations — to measure how much identity the representation actually leaks and what it costs to remove it.

## 2. Scope and operational definitions

**Violence** is a clip-level binary label: does the clip contain a physically aggressive act between people. This is the standard formulation across RWF-2000, RLVS, Hockey Fight and Crowd Violence.

**"Goon"**, the term in the registered project title, is defined here as *a person performing a violent act in the clip* — an observable behaviour, never a type of person, and never inferred from appearance or group membership. The distinction is both scientific and ethical. Scientifically, a model can be trained and evaluated against an observable act, whereas no dataset annotates "being a goon" and any model claiming to detect a person-type would be learning appearance correlates. Ethically, the person-type framing is what converts a violence detector into a profiling system. Operationally the target is therefore per-person violent-action attribution.

**Crowd** means scenes containing more than two simultaneously visible people, where occlusion and scale variation are the norm. The definition is stated explicitly because the closest prior work caps its input at exactly two people.

**Out of scope**: identity, demographics, intent prediction, pre-crime inference, and any claim about who a person is. The system answers what happened, not who someone is.

## 3. Ethics and dual use

There is a genuine tension in this project and it is better stated than defended against. The preliminary result in §6 shows that skeleton data leaks subject identity. Identifying individuals at a protest is precisely the harm that finding warns about, and a tool built to flag violent acts can be repurposed to enumerate participants.

Four design decisions respond to this concretely rather than aspirationally. No pixels, faces or clothing are processed or stored past the pose estimation stage. Hip-centred normalisation is applied by default, because it was *measured* to remove 24 points of identity leakage for 0.4 points of task accuracy. Person-level output is scoped to a single clip, with no cross-clip or cross-camera re-identification built, since tracking is the step that converts attribution into surveillance. And the label space contains acts only, with no demographic or person-type inference anywhere in the model.

The leakage measurement will be published as a limitation of the method and not only as a feature of it. A detector that cannot be audited for identity leakage should not be deployed on lawful assembly, which makes the privacy audit a precondition of the method rather than a separate ethics exercise.

## 4. Reviewed literature

**P7 — Cheng, Cai and Li, "RWF-2000: An Open Large Scale Video Database for Violence Detection" (arXiv 2020).** The closest prior work and our accuracy reference. RWF-2000 contains 2,000 five-second real surveillance clips, balanced, with anti-leakage splitting via source-video tracking and colour-histogram similarity checks. The accompanying Flow Gated Network runs parallel RGB and optical-flow 3D-CNN branches, passes the flow branch through a sigmoid and multiplies it into the ReLU output of the RGB branch before temporal max-pooling — a learned pooling mechanism in place of a hand-designed one. It reaches 87.25% with 0.27M parameters, against 12.3M for single-stream and 24.6M for two-stream I3D. Two things carry forward: the multiplicative gating idea, which we port to joint velocity in C3; and the paper's own Table IV, which shows flow-based methods degrading on the Crowd Violence dataset because optical flow's assumptions of brightness constancy and small, locally uniform motion fail in crowded low-resolution footage.

**P5 — Famouri, Hossain and Imteaj, "Pose to Protect" (ICCV Workshops 2025).** The closest skeleton-based pipeline. OpenPose extracts 25 keypoints per person from a 496-video UCF-Crime subset, and a 2-layer LSTM with 512 hidden units performs binary crime-versus-normal classification across seven federated clients. It establishes that skeletons alone carry sufficient signal for aggressive-event classification on real surveillance footage, and it is explicitly privacy-motivated, describing the representation as "anonymous" and "desensitized". It stops short of our setting in four ways: input is capped at two people with zero-padding, which is architectural rather than configurable since the input vector is 2 × 25 × 3 = 150; the paper admits OpenPose is unreliable under occlusion, distance and low light, which is the crowd regime; it emits one label per whole sequence, so there is no indication of which person was violent; and it contains no results table anywhere, with privacy asserted but never measured. It also contradicts itself on normalisation, since §3.2 describes hip-centred coordinates with confidence dropped, implying 100 dimensions, while §4.1.2 describes frame-normalised coordinates with confidence kept, giving the 150 the model actually consumes.

**P3 — Hegiste, Goyal, Legler and Ruskowski, "Federated Action Recognition for Smart Worker Assistance Using FastPose" (FLTA 2025).** Not our application — eight industrial hand gestures from five subjects, single-person, clean indoor capture, no violence and no crowd. It earns its place for one specific reason: it is the only public skeleton dataset we found that labels subject identity on every sample, which makes it the only place a privacy audit can actually be run. It also contributes a four-paradigm evaluation protocol, and its claim that federated training beats centralized training by 12.4 points inverts the usual ordering and is worth re-testing (§5, Gap 4).

## 5. Identified research gaps

**Gap 1 — Crowd scalability.** No existing skeleton pipeline for aggressive-behaviour detection handles more than two people. In P5 the limit is the input dimensionality, not a hyperparameter. Pose quality also collapses in exactly this regime, by the paper's own admission, and the pixel-based alternative is not a free fallback since P7's Table IV shows optical-flow methods degrading on crowded footage. What is needed is a set-structured, permutation-invariant encoder over a variable number of skeletons that retains per-person representations rather than concatenating them. This is the primary gap and the one the registered title requires.

**Gap 2 — No person-level attribution.** Every reviewed method emits one label per clip. No violence dataset annotates which person is violent, so attribution cannot be trained by direct supervision. P5 names this weak-supervision problem in its introduction — calling the many normal frames noisy labels — but never adopts a multiple-instance formulation to address it, despite citing the very paper that introduced MIL for this dataset.

**Gap 3 — The privacy claim is unverified.** Both 2025 papers rest on the premise that skeletons are private, and neither runs a single privacy experiment or acknowledges the omission in its limitations. Skeleton anonymisation is an established research area, which makes the omission more serious rather than less interesting: the risk was already documented. This gap is load-bearing for us specifically, because privacy is the entire reason this project uses skeletons rather than pixels.

**Gap 4 — Baseline validity and statistical reporting.** A secondary gap inherited from the federated literature whose evaluation practice we borrow. P3 reports federated training beating centralized by 12.4 points, inverting the usual ordering. On the unseen sixth participant (their Table II, not the global test set where centralized reaches 57.1%) the centralized model scored 11.71%, which is just *below* the 12.5% chance level for eight classes — a collapsed model rather than a tuned baseline. The training budget is matched in epochs but not in gradient steps. And no variance is reported anywhere, with conclusions drawn from 9-to-16-point differences from single runs. In fairness, P3 designed its federated-ensemble condition deliberately to isolate the ensemble effect and says so; we are not claiming they missed it.

## 6. Preliminary work already completed

All figures are in `figures/`, reproducible via `scripts/`.

**Dataset verification.** P3's release contains 29,963 frames across five clients and three splits, matching the paper exactly. Each feature row holds 26 values, consistent with 13 joints × 2 coordinates. The label files store two columns, gesture and client identifier, so subject identity is an explicit field — this is what makes the privacy audit possible. The paper does not document joint ordering within a row, so we recovered it empirically from per-joint means and variances: the wrists carry the most variance, as expected for upper-body gestures, while knees and ankles are near-static and contribute almost no task signal. Plotting the mean pose per gesture confirms the label mapping independently, since "up" shows a raised arm and "stop" shows both hands lifted. Critically, the coordinates are frame-normalised rather than body-centred, with values mostly in 0.3–0.9; this turned out to matter a great deal.

**A data integrity finding.** The file `centralized_x_train.txt` stops at exactly 2,097,152 bytes — precisely 2 MiB — mid-row, containing 13,441 complete rows where the matching label file has 26,403. A repaired file is also published, and it is byte-identical to the concatenation of the five per-client training files, so the repair is sound; the per-client files are all intact. We cannot infer what the authors trained on, but any third party reproducing the centralized baseline from the obviously-named file would silently train on 51% of the data, and the centralized arm is exactly the one the paper reports collapsing. This gives Gap 4 a concrete, cheaply testable mechanism, and we will report results for both files.

**Measured client heterogeneity.** Computed from the released files, the non-IID structure is severe: gesture 3 has 64 frames for client 5 against 862 for client 2, a 13.5× imbalance within a single class, and client 1 devotes 23.5% of its data to gesture 6 where client 3 gives it 10.8%.

**Identity leakage, and a correction.** A linear probe — multinomial logistic regression on standardised 26 × 20 windows — recovers which of five subjects produced a window with **59.3% accuracy** on the data as released, against 20% chance and a 26.6% majority-class baseline, with the attacker trained and tested on disjoint gesture sets so that no test window is temporally adjacent to a training window.

We then asked what the classifier was using. Because the coordinates are frame-normalised, absolute position in the image is encoded, and we measured that subjects did stand in measurably different places. Re-running the attack under increasing invariance: hip-centring the coordinates drops leakage to **35.2%**; additionally scaling by shoulder width leaves it at 35.3%; and removing position entirely in favour of frame-to-frame velocity drops it to **23.8%**, essentially chance. Roughly two-thirds of the originally measured leakage was positional recording artifact rather than biometric signal. The residual 35% remains above the majority baseline and is consistent with genuine body geometry, since client 1's shoulder width measures visibly narrower than the others.

An earlier within-split version of this probe reached 97% and was discarded: the dataset is organised in contiguous gesture blocks split 88/6/6 *within* each block, so test frames sit temporally adjacent to training frames and a classifier can near-memorise.

**The privacy-utility trade.** The useful result is the trade rather than the leakage figure alone. Hip-centring removes 24 points of identity leakage at a cost of **0.4 points** of gesture accuracy, which is close to free and is now applied by default in our pipeline. Velocity-only is the opposite: it removes the leakage but destroys the task, dropping gesture accuracy to 16.3% against a 12.5% chance level, so it is ruled out as a defense — a negative result worth reporting.

**Limitations of this result, as they will appear in the paper.** All recordings come from a single session per subject, so clothing, camera placement and body geometry are constant; strictly this measures identity-plus-session linkage rather than cross-session re-identification. Five-way identification is far easier than open-set identification in a crowd. And the absolute gesture accuracies here are inflated by temporal adjacency in the within-block split — comparisons between representations are valid because every representation is inflated identically, but the absolute level should not be quoted as a task result.

## 7. Proposed contributions

**C1 — Crowd-scale skeleton violence detection.** A set-structured encoder over a variable number of skeletons, removing the two-person cap, evaluated on RLVS and Crowd Violence against an RGB reference and against a deliberately two-person-capped variant of our own model that reproduces P5's constraint with everything else held constant.

**C2 — Person-level attribution.** Multiple-instance learning over per-person instances: each clip is a bag, each detected person an instance, and a clip is violent if at least one person is violent. Attribution falls out of the instance scores with no person-level labels needed for training. Evaluation requires them, so we will hand-annotate which person is violent in 80–100 held-out clips and report person-level precision and recall with confidence intervals. This is the only manual annotation in the project.

**C3 — Skeleton Flow-Gated Network.** Port P7's multiplicative gating from pixels to joints: a position stream ending in ReLU, a velocity stream ending in a sigmoid, multiplied, then pooled. Where a person is still the gate closes, which is useful in a crowd where most people are not fighting. Four-way ablation over position-only, velocity-only, concatenation and gating. The novelty claim is deliberately narrow: two-stream skeleton networks with motion channels already exist (2s-AGCN), and skeleton-based violence detection on RWF-2000 also already exists and reportedly exceeds P7 — what is adapted is the multiplicative gate, not the two-stream idea and not the task.

**C4 — Privacy audit and hardening.** Substantially complete (§6). Remaining: membership inference via shadow models, random joint dropout focused on the near-static lower-body joints, and DP-SGD noise.

**C5 — Federated multi-camera extension.** Stretch objective only, treating each camera as a client, using the corrected baselines from Gap 4.

## 8. Experimental design

Primary datasets are RLVS (2,000 clips, free), Crowd Violence (246 clips, crowded scenes, free) and Hockey Fight (1,000 clips, free) as a sanity baseline; RWF-2000 is requested but access-gated and remains a stretch; P3's FederatedHAR is used for the privacy audit only. There is no standard protest benchmark, and the paper will say so plainly — Crowd Violence plus the fighting and assault classes of UCF-Crime are the closest available proxies.

Metrics go well beyond clip accuracy. Clip-level results are reported as accuracy, macro-F1 and AUC with mean ± standard deviation over three seeds. Person-level attribution is reported as precision and recall on the hand-annotated subset, with confidence intervals given the small sample. Crowd behaviour is characterised by a degradation curve of accuracy against the number of detected people, reported rather than hidden, since pose quality is the known weakness of this approach. Privacy is reported as subject re-identification against both chance and majority baselines, plus membership inference AUC against 0.5. Deployment cost is reported as parameter count and CPU inference latency per clip.

## 9. Thirteen-day schedule

| Days | Work | Output |
|---|---|---|
| 1 | Download RLVS, Crowd Violence, Hockey Fight. Request RWF-2000 access. Set up pose extraction | Data in place |
| 2–3 | Multi-person pose extraction over all clips; cache skeletons; hip-centred normalisation by default | Skeleton corpus |
| 4–5 | Set-structured per-person encoder; clip-level violence baseline; two-person-capped comparison | C1 result |
| 6–7 | MIL pooling; hand-annotate 80–100 clips; person-level attribution evaluation | C2 result |
| 8 | Skeleton Flow-Gated Network and four-way ablation | C3 result |
| 9 | Degradation curve vs number of detected people; macro-F1 and seed variance across models | Crowd analysis |
| 10 | Finish C4: membership inference, joint dropout, DP-SGD. Verify the prior-work citations | C4 complete |
| 11 | Deliberate buffer. C5 or RWF-2000 only if everything above is done | Buffer |
| 12–13 | Figures, tables, writing, reference check | Paper draft |

Days 1 to 7 are the critical path and deliver the registered title. Day 8 onward is additive; if the schedule slips, C3 and C5 are what get cut, in that order.

## 10. Risks and mitigations

The central technical risk is that **pose estimation fails in crowds** — occlusion and distance degrade multi-person pose, and this is the known weakness of the whole approach. The mitigation is to measure it rather than hide it: report the degradation curve against number of detected people, so that if accuracy falls off sharply beyond some crowd density that becomes a published finding bounding where the method is usable. Days 2 and 3 are deliberately pose extraction, so this will be known by day 3 while there is still time to adjust scope.

**No protest benchmark exists.** Crowd Violence has only 246 clips and nothing is annotated at protest or person level. This is stated as a scope limitation, with Crowd Violence and UCF-Crime's fighting and assault classes used as the closest proxies and confidence intervals reported throughout.

**Prior skeleton work may already exceed our clip accuracy.** If published skeleton methods already beat P7 on RWF-2000, our contribution cannot be peak clip accuracy; it is crowd scale, person-level attribution and audited privacy. Both flagged citations — Moon et al. on skeleton anonymisation and the skeleton violence result on RWF-2000 — **must be verified before presentation**; they were raised in review and could not be checked offline.

**The annotated subset is small.** 80–100 clips is a thin basis for the person-level claim, so it is reported with confidence intervals and the claim is only that attribution beats chance, not that it is precise.

**The privacy result's generality is bounded.** It comes from one recording session per subject on a non-crowd dataset, and is reported as identity-plus-session linkage on a representation rather than as a crowd re-identification claim. The measured defense stands regardless.

## 11. Expected outcomes

Existing skeleton methods for aggressive-behaviour detection cap out at two people, cannot say who acted, and assert a privacy property none of them tested. This project addresses all three. Deliverables are a short paper with four contributions, a public code repository and reproducible scripts. The privacy component is already complete, with one defense measured and one candidate defense ruled out.

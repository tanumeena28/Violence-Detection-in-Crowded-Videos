# Professor's requirements and project direction

Requirements recorded 22 October 2026; implementation status updated 14 November. Sources: the four professor-chat screenshots supplied by Vishal and his clarification that the working pipeline must be shown on 24 October. The chats are evidence of project expectations; they do not authorize sending messages or submitting scheduling forms.

## Dates and deliverables

| Stage | Requirement | Date / status |
|---|---|---|
| Implementation discussion | End-to-end execution of the proposed framework; a small number of samples is acceptable. High accuracy is additional, not essential at this stage. Allow time for discussion and feedback. | Working pipeline to be shown on **24 October 2026**, confirmed by Vishal. |
| Final presentation | Implementation, demonstration, and a research-paper draft with at least methods and results written at presentation time. Accuracy and performance measures matter at this next stage. | Group's final date is not yet confirmed. Professor offered **29, 30 and 31 October** for presentations before Diwali; these are options, not a booked group date. |
| Complete paper draft | At least **12 pages**, complete before **20 November 2026**. | Plan an internal finished draft by **19 November**, leaving revision time. |
| Scheduling | One entry per group in the professor's implementation-discussion form. | Administrative instruction only; no submission was made by this project workflow. |

## Are we going in the right direction?

Yes for the 24 October implementation discussion. The pipeline runs from raw crowd video through pretrained multi-person pose estimation, clip-local tracking, normalized body motion and relative interactions, a locally trained temporal classifier, and an annotated video output. All four baseline/reliability/interaction/combined configurations are implemented. The corrected pilot and controls have verified saved predictions and playable demos.

The current evidence does not support claiming a successful accuracy improvement from reliability and interaction features. On the corrected 47-clip test split, baseline and interactions reach 68.1%, reliability 63.8%, and combined 66.0%. Motion reaches 74.5%; seven aggregate pose-quality descriptors reach 76.6%. This is evidence to discuss, not a reason to hide the pilot or restart before the meeting. Scene, crowd density and detection behavior may explain part of the signal.

The November 7 repeated evaluation is now complete on 245 clips and 204 reviewed
source groups. Reliability reaches 76.9% mean accuracy, baseline/interactions
76.1% and combined 74.8%; quality-only reaches 77.6%. The November 14 matched
coverage ablation leaves three variants' mean accuracies unchanged and lowers
interactions by 0.14 percentage points. It does not remove indirect detection
cues. Both experiments remain exploratory, and the manuscript is still a
methods/results draft rather than the complete 12-page paper.

The project should remain focused on the research question in the latest Stage 1 deck: whether pose reliability and relative interactions help distinguish violent from similar nonviolent crowd motion. The older proposal's person-level attribution, differential privacy and federated extensions are not requirements in these professor chats and would expand the immediate task unnecessarily. The current classifier does not identify a violent person or infer intent.

## Proposal-to-implementation alignment

| Proposed component | Implemented status | What to explain |
|---|---|---|
| Raw video to multi-person poses | Implemented with YOLO11n-pose, 32 sampled frames and COCO-17 joints | Pose estimator is pretrained; the temporal classifier was trained locally. |
| Consistent person observations | Clip-local tracking, up to 8 retained tracks | Track fragmentation and discarded people remain limitations. IDs do not persist across clips. |
| Reliability and interaction changes | All four controlled variants implemented | Same caches and encoder family; input channels change parameter count. Improvement is a hypothesis, not established. |
| Clip-level violence score | Implemented with validation-selected model and threshold | Score is not a calibrated probability. All test clips remain in the metrics. |
| Annotated demo | Implemented, including errors and low-pose abstentions | Offline full-clip output with sampled overlays. |
| Flagged windows in the proposal | Not implemented or evaluated | The current demo scores whole clips. Ask whether a windowed extension is required for the final stage; do not describe this as temporal localization. |
| Five folds and three seeds | Completed on 7 November; matched coverage ablation completed on 14 November | Custom source-grouped exploratory evaluation. Descriptive variation does not establish significance or untouched benchmark performance. |
| Full-pipeline performance | Pilot extraction timings exist; classifier-only timings exist | Keep component timings separate. Do not call this real-time or quote model-only timing as full-pipeline latency. |

## Work order

1. Before 24 October: verify fresh raw-video inference, prepare the demo command, keep offline videos as a fallback, and write a short discussion guide.
2. At the meeting: show the pipeline first, the measured pilot second, a failure case third, then discuss the scope and the quality-only control. Leave time for the professor's feedback.
3. After the meeting: lock the evaluation protocol, complete source review, run source-group-separated folds and seeds, inspect real occlusion and nonviolent high motion, and measure the full pipeline. Preserve current pilot scores as exploratory results after prior test inspection.
4. Write methods and current pilot results now, then update with final experiments. Complete a genuine 12-page manuscript before 20 November without padding or invented results.

## Evidence files

- `C:/Users/Vishal Gautam/Pictures/Screenshots/Screenshot 2026-10-21 215437.png`: scheduling and meaning of execution pipeline.
- `C:/Users/Vishal Gautam/Pictures/Screenshots/Screenshot 2026-10-21 215451.png`: end-to-end execution; accuracy optional now and essential next stage.
- `C:/Users/Vishal Gautam/Pictures/Screenshots/Screenshot 2026-10-21 215529.png`: implement on a small sample and allow discussion.
- `C:/Users/Vishal Gautam/Pictures/Screenshots/Screenshot 2026-10-21 215601.png`: final presentation contents, at least 12-page draft before 20 November, optional October presentation dates.

The last two-day implementation target comes from Vishal's current clarification, not an inferred date from the chat screenshots.

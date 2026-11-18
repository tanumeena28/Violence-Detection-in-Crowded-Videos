# Validation diagnosis, 15 November 2026

All 317 source-grouped validation clips were fully decoded for descriptive motion
measurements. The assistant visually inspected eight chronological frames from
each of the 57 errors and 12 score-stratified correct controls in all 12 sheets.
This is assistant-assisted sampled-frame diagnosis, not independent human label
review or a full-video action annotation. No supplied labels were changed.

The original model has 42 Fight misses from 27 source groups and 15 NonFight
false alarms from 11 source groups. Fourteen misses belong to just four sources:
`3kpviz7lamy`, `_6-b11r9fjm`, `npekbgurcxi`, and `qrwtk-2a13o`. Related clips are
dependent observations, so these counts should not be treated as independent
evidence of 42 distinct failure mechanisms.

Several sampled misses show small or distant people, obstructions, difficult
lighting, or contact concentrated in part of the clip. Examples include the
stairwell (`3kpviz7lamy`), street traffic (`qrwtk-2a13o`), window-lit room
(`dc10fyqgnqo`), and supermarket (`z1wyvuv8`) sources. Other examples are clearer
close-range actions, so distance alone does not explain the errors. Some
NonFight-labeled errors show apparent physical contact, especially the elevator
and street-assault sources. These require independent full-clip review rather
than automatic relabeling.

Every validation clip decodes at 30 FPS. Median consecutive grayscale difference
at 128 by 72 pixels is 0.889 for misses versus 1.658 for correctly detected Fight
clips; the NonFight medians are 0.798 for false alarms and 0.628 for correct
decisions. This is descriptive, includes camera motion, and does not identify
violence. It supports checking weaker or localized movement rather than merely
adding a motion-magnitude threshold.

The original encoder receives 32 uniform samples across a five-second clip,
then averages two 16-frame embeddings. For a 150-frame clip, adjacent encoder
inputs are roughly five source frames apart. This can dilute localized evidence
and changes movement speed seen by the pretrained encoder. It is a testable
hypothesis, not an established cause of the errors.

The next single candidate retains that global embedding and adds four 16-frame
windows at approximately 15 sampled FPS, with evenly spaced starts. Concatenated
local mean and componentwise maximum embeddings retain average and localized
responses. The same frozen R3D-18, source split, train-only scaling, and
validation-only regularization/threshold selection are retained. No pose fusion
benefit has been demonstrated on development footage, so this experiment tests
temporal video representation directly.

The candidate must improve validation log loss and macro-F1 without reducing
Fight recall to qualify for evaluation. The rule is frozen before feature
extraction or fitting. Previously inspected released evaluation footage remains
exploratory evidence and is excluded from all selection.

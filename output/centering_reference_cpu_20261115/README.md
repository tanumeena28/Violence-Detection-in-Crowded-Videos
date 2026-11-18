# Fresh legacy CPU reference

This experiment fits `coco17-hip-box-center-v1` on CPU for comparison with
[the corrected CPU experiment](../centering_corrected_cpu_20261115/README.md).
The inputs, source groups, folds, seeds, network dimensions, coverage setting
and training budget match. It contains fresh fitted models, not copies of the
November 7 GPU checkpoints.

Use its archived implementation to inspect or resume it:

```powershell
& '.\.venv\Scripts\python.exe' output/centering_reference_cpu_20261115/run_snapshot.py run-cv --device cpu
& '.\.venv\Scripts\python.exe' output/centering_reference_cpu_20261115/run_snapshot.py report-cv --date 2026-11-15 --verification-device cpu
```

Use the corrected experiment's comparison command. [Results](index.html),
[the audit](audit.json) and [the frozen protocol](protocol.json) describe this
reference after completion. Historical GPU and RWF artifacts remain separate.

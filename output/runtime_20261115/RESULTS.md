# Controlled raw-video runtime

RTX 3050 Laptop GPU, 32 sampled frames, ten fixed clips, three warmed repeats.

Warm full-pipeline median: 0.270 s; p95: 0.390 s.

Cold process median: 8.359 s; p95: 8.503 s.

Warm includes full video decode, sampled-frame pose extraction/tracking, corrected features, normalization/transfer and GPU classifier. Cold external-process wall adds Python launch/imports and model initialization. Overlay/export excluded. No competing project GPU job during measurement.

Offline full-clip timing on ten duration-selected crowd clips; not streaming latency, a hardware-independent speed claim or a real-time demonstration.

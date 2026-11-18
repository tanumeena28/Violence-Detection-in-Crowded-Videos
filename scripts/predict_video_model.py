"""Run a sealed supervised RWF video model on a raw video, optionally render it."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
import torch
from torchvision.models.video import R3D_18_Weights, r3d_18

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import decode_sample, write_json
from affective.motion import score_linear
from affective.temporal_video import combine_embeddings, decode_windows, encode_indices


def predict(experiment, video, device="cuda"):
    plan = json.loads((experiment / "protocol.json").read_text())
    seal = json.loads((experiment / "head_frozen.json").read_text())
    if digest(experiment / "model.json") != seal["artifacts_sha256"]["model.json"] or digest(experiment / "protocol.json") != seal["protocol_sha256"]:
        raise ValueError("Sealed model or protocol changed")
    checkpoint = json.loads((experiment / "model.json").read_text())
    weights = experiment / "weights" / plan["encoder"]["weights_file"]
    if digest(weights) != plan["encoder"]["weights_sha256"]:
        raise ValueError("Video encoder weights changed")
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    started = time.perf_counter()
    model = r3d_18(weights=None)
    model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
    model.fc = torch.nn.Identity()
    model.eval().to(device)
    transform = R3D_18_Weights.KINETICS400_V1.transforms()
    local_indices = None
    if plan['schema'] == 'r3d18-global-local-mean-max-v1':
        frames, local_indices, indices, fps = decode_windows(video)
        global_vector = encode_indices(model, transform, frames, indices.reshape(2, 16), device).mean(0)
        local_vectors = encode_indices(model, transform, frames, local_indices, device)
        vector = combine_embeddings(global_vector, local_vectors).astype(np.float64)
        decoded = len(frames)
    elif plan['schema'] == 'rwf-supervised-frozen-r3d18-v1':
        images, indices, fps, decoded = decode_sample(video, 32)
        rgb = torch.from_numpy(np.stack([im[..., ::-1].copy() for im in images])).permute(0, 3, 1, 2)
        tensor = torch.stack([transform(rgb[:16]), transform(rgb[16:])]).to(device)
        with torch.inference_mode():
            vector = model(tensor).mean(0).cpu().numpy().astype(np.float64)
    else:
        raise ValueError('Unsupported sealed video model schema')
    score = float(score_linear(vector[None], checkpoint)[0])
    return {"source": str(video), "source_sha256": digest(video), "model_sha256": digest(experiment / "model.json"),
            "score": score, "threshold": checkpoint["threshold"], "prediction": int(score >= checkpoint["threshold"]),
            "decision": "violent" if score >= checkpoint["threshold"] else "nonviolent", "sampled_frames": indices.tolist(),
            "decoded_frames": decoded, "duration_seconds": decoded / fps, "device": device,
            "model_schema": plan['schema'], "local_window_frames": local_indices.tolist() if local_indices is not None else None,
            "seconds_including_model_initialization": time.perf_counter() - started,
            "scope": "Offline whole-clip prediction; score is not a calibrated probability. No person-level attribution."}


def render(video, result, target, dataset_label=None):
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = 1120, 680
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
               "-s", f"{width}x{height}", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast",
               "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    count, poster = 0, None
    draw = lambda frame, value, pos, size=.62: cv2.putText(frame, value, pos, cv2.FONT_HERSHEY_SIMPLEX, size, (225, 235, 240), 1, cv2.LINE_AA)
    try:
        while True:
            ok, raw = cap.read()
            if not ok:
                break
            frame = np.full((height, width, 3), (25, 31, 42), dtype=np.uint8)
            fit = min(760 / raw.shape[1], 530 / raw.shape[0])
            w, h = round(raw.shape[1] * fit), round(raw.shape[0] * fit)
            x, y = 20 + (760 - w) // 2, 90 + (530 - h) // 2
            frame[y:y+h, x:x+w] = cv2.resize(raw, (w, h))
            draw(frame, "VIDEO VIOLENCE CLASSIFICATION", (24, 40), .95)
            model_label = "fine-tuned RWF video" if result.get("model") == "fine_tuned_video" else "supervised RWF reference"
            draw(frame, f"Offline whole-clip model | {model_label}", (24, 70), .55)
            draw(frame, "MODEL OUTPUT", (810, 140), .7)
            draw(frame, f"Score: {result['score']:.3f}", (810, 190))
            draw(frame, f"Threshold: {result['threshold']:.2f}", (810, 230))
            draw(frame, result["decision"].upper(), (810, 310), .8)
            draw(frame, f"Time: {count/fps:.2f}s", (810, 390))
            if dataset_label is not None:
                draw(frame, "DATASET LABEL", (810, 470), .55)
                draw(frame, "violent" if dataset_label else "nonviolent", (810, 510))
            draw(frame, "Clip-level decision.", (810, 570), .5)
            draw(frame, "No person attribution.", (810, 600), .5)
            draw(frame, "Model score is not a calibrated probability. Dataset labels still require independent review.", (24, 654), .5)
            encoder.stdin.write(frame.tobytes())
            if count == round(result["decoded_frames"] / 2):
                poster = frame.copy()
            count += 1
    finally:
        cap.release()
        encoder.stdin.close()
    errors = encoder.stderr.read().decode(errors="replace")
    if encoder.wait():
        raise RuntimeError(errors)
    if poster is not None:
        cv2.imwrite(str(target.with_suffix(".jpg")), poster)
    if count != result["decoded_frames"]:
        raise ValueError("Rendered clip differs from prediction decode")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=Path("output/rwf_supervised_20261115"))
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--render", type=Path)
    parser.add_argument("--dataset-label", type=int, choices=[0, 1])
    args = parser.parse_args()
    result = predict(args.experiment.resolve(), args.video.resolve(), args.device)
    if args.render:
        result["rendered_frames"] = render(args.video.resolve(), result, args.render.resolve(), args.dataset_label)
    if args.output_json:
        write_json(args.output_json.resolve(), result)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()

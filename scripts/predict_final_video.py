"""Run a retained sealed model on a clip or successive closed video windows."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.data import write_json
from affective.inference import VideoPredictor, PosePredictor, iter_video_windows, selected_video_experiment
from scripts.predict_video_model import render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', type=Path, required=True)
    parser.add_argument('--model', choices=['active', 'fine', 'frozen', 'pose'], default='active')
    parser.add_argument('--window-seconds', type=float, help='Score successive closed windows; offline processing')
    parser.add_argument('--output-json', type=Path, required=True)
    parser.add_argument('--render', type=Path, help='Annotated whole-clip MP4, available without window mode')
    args = parser.parse_args()
    if args.render and args.window_seconds is not None:
        parser.error('--render is available only for whole-clip scoring')
    if args.model == 'pose' and args.render:
        parser.error('Use the existing pose demonstration page for skeleton overlays')
    if not torch.cuda.is_available():
        raise RuntimeError('The local CUDA GPU is required for this delivery workflow')
    video = args.video.resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    experiments = {'fine': ROOT / 'output/rwf_finetune_v2_20261115',
                   'frozen': ROOT / 'output/rwf_supervised_20261115', 'active': selected_video_experiment()}
    predictor = PosePredictor() if args.model == 'pose' else VideoPredictor(experiments[args.model])
    if args.window_seconds is None:
        result = predictor.predict(video)
        result['source'] = str(video)
        if args.render:
            result['encoded_frames'] = render(video, result, args.render.resolve())
            result['render'] = str(args.render.resolve())
    else:
        windows = []
        for images, indices, fps, decoded, start in iter_video_windows(video, args.window_seconds):
            record = {'start_seconds': start, 'end_seconds': start + decoded / fps, 'decoded_frames': decoded}
            if images is None:
                record.update({'score': None, 'prediction': None, 'decision': 'insufficient frames', 'abstain': True})
            else:
                record.update(predictor.process(images, indices, fps, decoded))
            windows.append(record)
        if not windows:
            raise ValueError('No decodable frames')
        result = {'source': str(video), 'window_seconds': args.window_seconds, 'windows': windows,
                  'decoded_frames': sum(w['decoded_frames'] for w in windows),
                  'scope': 'Offline nonoverlapping closed windows. The clip-trained model has no validated streaming or event-localization accuracy.'}
    write_json(args.output_json.resolve(), result)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()

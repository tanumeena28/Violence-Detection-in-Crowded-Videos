"""Download only public pretrained assets and verify the recorded checksums."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pose', action='store_true', help='Also download the recorded YOLO pose detector')
    args = parser.parse_args()
    experiment = ROOT / 'output/rwf_supervised_20261115'
    encoder = json.loads((experiment / 'protocol.json').read_text(encoding='utf-8'))['encoder']
    target = experiment / 'weights' / encoder['weights_file']
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary = target.with_suffix('.partial')
        print(f'Downloading {encoder["weights_file"]}', flush=True)
        urlretrieve(encoder['weights_url'], temporary)
        if digest(temporary) != encoder['weights_sha256']:
            raise ValueError('Downloaded pretrained encoder checksum differs from the recorded experiment')
        temporary.replace(target)
    if digest(target) != encoder['weights_sha256']:
        raise ValueError('Existing pretrained encoder checksum differs from the recorded experiment')
    print('Frozen video encoder checksum verified', flush=True)
    if args.pose:
        from ultralytics.utils.downloads import attempt_download_asset
        settings = json.loads((ROOT / 'output/centering_corrected_cpu_20261115/pose_settings.json').read_text(encoding='utf-8'))
        target = ROOT / 'models' / settings['weights']
        target.parent.mkdir(parents=True, exist_ok=True)
        downloaded = Path(attempt_download_asset(str(target)))
        if digest(downloaded) != settings['weights_sha256']:
            raise ValueError('Pose detector checksum differs from the retained model; obtain the recorded file from Vishal')
        print('Pose detector checksum verified', flush=True)


if __name__ == '__main__':
    main()

"""Prepare neutral full-video review clips without predictions or class filenames."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from pathlib import Path

import imageio_ffmpeg


def prepare(root, selection, out):
    if out.exists():
        raise FileExistsError("Keep review records; choose a new output directory")
    records = json.loads(selection.read_text(encoding="utf-8"))["cases"]
    random.Random(42).shuffle(records)
    (out / "clips").mkdir(parents=True)
    mapping = []
    for number, record in enumerate(records, 1):
        source = root / record["path"]
        neutral = f"{number:03d}"
        target = out / "clips" / f"{neutral}.mp4"
        command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-i", str(source),
                   "-map", "0:v:0", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                   "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
        subprocess.run(command, check=True, capture_output=True)
        mapping.append({"neutral_id": neutral, "clip_id": record["id"], "source": record["path"],
                        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        "review_video_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        if number % 10 == 0:
            print(f"Prepared {number}/{len(records)} neutral review clips", flush=True)
    (out / "coordinator_mapping.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    items = [{"id": m["neutral_id"], "video": f"clips/{m['neutral_id']}.mp4"} for m in mapping]
    page = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Clip label review</title>
<style>body{font:16px system-ui;margin:30px auto;padding:20px;max-width:1000px;background:#f4f6f8;color:#17232d}h1{margin-bottom:8px}p{line-height:1.6}.card{background:white;border-radius:10px;padding:22px;margin:22px 0}video{width:100%;max-height:420px;background:#111}label{display:inline-block;margin:12px 16px 8px 0}input,select,textarea,button{font:inherit;padding:8px}textarea{width:95%;min-height:65px}button{background:#087f8c;color:white;border:0;border-radius:6px;cursor:pointer}header{position:sticky;top:0;background:#f4f6f8;padding:12px 0;z-index:2}.status{margin-left:15px}</style></head><body>
<h1>Clip label review</h1><p>Watch each complete clip before assigning a label. Mark unclear footage as ambiguous. Violence means visible intentional physical aggression against a person; energetic movement alone is insufficient. Record uncertainty and visible difficulty without guessing. These are 40 preselected diagnostic clips.</p>
<header><label>Your name <input id="reviewer" placeholder="Reviewer name"></label><button id="save">Download review records</button><span id="status" class="status"></span></header><main id="clips"></main>
<script>const clips=CLIP_DATA;const flags=['camera movement','heavy occlusion','dense crowd','high nonviolent motion','visible edit or cut'];
document.getElementById('clips').innerHTML=clips.map(c=>`<section class="card" data-id="${c.id}"><h2>Clip ${c.id}</h2><video controls preload="none" src="${c.video}"></video><div><label>Label <select class="label"><option value="">Choose after viewing</option><option value="violent">Violent</option><option value="nonviolent">Nonviolent</option><option value="ambiguous">Ambiguous</option></select></label><label><input class="watched" type="checkbox"> Watched the complete clip</label></div><div>${flags.map(f=>`<label><input type="checkbox" class="flag" value="${f}"> ${f}</label>`).join('')}</div><textarea placeholder="Visible events, uncertainty, and approximate timestamps"></textarea></section>`).join('');
document.getElementById('save').onclick=()=>{const reviewer=document.getElementById('reviewer').value.trim();if(!reviewer){document.getElementById('status').textContent='Enter your name first.';return;}const entries=[...document.querySelectorAll('.card')].map(card=>({neutral_id:card.dataset.id,label:card.querySelector('.label').value||null,full_clip_watched:card.querySelector('.watched').checked,difficulty_flags:[...card.querySelectorAll('.flag:checked')].map(x=>x.value),notes:card.querySelector('textarea').value,review_status:card.querySelector('.watched').checked&&card.querySelector('.label').value?'reviewed':'unreviewed'}));const reviewed=entries.filter(x=>x.review_status==='reviewed').length;const record={reviewer,exported_at:new Date().toISOString(),reviewed_clips:reviewed,total_clips:entries.length,predictions_displayed:false,status:reviewed===entries.length?'complete':'partial',entries};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)],{type:'application/json'}));a.download='clip_review.json';a.click();URL.revokeObjectURL(a.href);document.getElementById('status').textContent=`Exported ${reviewed}/${entries.length} reviewed clips.`;};</script></body></html>'''
    (out / "index.html").write_text(page.replace("CLIP_DATA", json.dumps(items)), encoding="utf-8")
    (out / "README.md").write_text(
        "# Prepared independent-review pack\n\nOpen `index.html` with a reviewer who has not seen the model predictions. Full clips are transcoded to neutral numbered MP4s and shuffled with seed 42. The page contains no supplied labels, class filenames, model scores or outcome categories. Keep `coordinator_mapping.json` away from the reviewer until labeling is finished.\n\nAll 40 clips remain unreviewed. The pack is preparation, not completed independent review. The original sample was ten cases per prediction-outcome category, selected by filename; it is an exploratory diagnostic subset, not a random estimate of dataset-wide label accuracy. Exported labels belong to review records and do not overwrite frozen dataset labels.\n", encoding="utf-8")
    (out / "review_status.json").write_text(json.dumps({"status": "prepared_unreviewed", "clips": len(items), "reviewer": None, "independent_review_completed": False}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--selection", type=Path, default=Path("output/technical_review_20261115/review_cases.json"))
    parser.add_argument("--out", type=Path, default=Path("output/blind_review_20261115"))
    args = parser.parse_args()
    prepare(args.root.resolve(), args.selection.resolve(), args.out.resolve())

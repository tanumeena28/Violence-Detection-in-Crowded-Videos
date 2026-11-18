"""Pin and audit fresh video inputs before fixed-model external scoring."""
from pathlib import Path, PurePosixPath
import csv
import hashlib
import json
import re
import zipfile

import cv2

ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
from affective.cross_validation import digest,write_manifest
from affective.data import write_json


def main():
    out=ROOT/'output/external_validation_20261115'
    if (out/'protocol.json').exists():
        raise FileExistsError('External protocol already frozen')
    out.mkdir(exist_ok=True)
    data=ROOT/'data/external/HockeyFight'
    archive_hashes={'data_001.zip':'178484464a9bdce5bed5d65852ce5117c14edb903fbfe93b53e6a0eaa4349e1d',
                    'data_002.zip':'68db3527560c7c36a9f5c241b26f11eba949bbd2c144380ea078eb2f86a769fa'}
    target=(data/'videos').resolve();target.mkdir(exist_ok=True)
    names=set()
    for name,expected in archive_hashes.items():
        archive=data/name
        if digest(archive)!=expected:raise ValueError('Pinned external archive bytes changed')
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                if not member.filename.endswith('.avi'):continue
                if not re.fullmatch(r'(fi|no)\d+(?:mpg)?_+xvid\.avi',member.filename):
                    raise ValueError('Unexpected external archive member')
                destination=(target/member.filename).resolve()
                if target not in destination.parents:raise ValueError('Unsafe archive path')
                if member.filename in names:raise ValueError('Duplicate external archive filename')
                names.add(member.filename)
                with z.open(member) as source,destination.open('wb') as stream:
                    while block:=source.read(1024*1024):stream.write(block)
    if len(names)!=1000:raise ValueError('Expected complete 1000-clip Hockey Fight mirror')
    prior={}
    for manifest in [ROOT/'output/video_baseline_v2_20261115/assignments.csv',ROOT/'output/rwf_supervised_20261115/source_inventory.csv']:
        with manifest.open(newline='',encoding='utf-8') as stream:
            for row in csv.DictReader(stream):prior.setdefault(row['sha256'],[]).append(row['path'])
    rows=[];overlap=[]
    for path in sorted(target.glob('*.avi')):
        sha=digest(path);cap=cv2.VideoCapture(str(path))
        fps=cap.get(cv2.CAP_PROP_FPS);frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));cap.release()
        if fps<=0 or frames<2:raise ValueError('Unusable external video header')
        identifier=hashlib.sha256(path.name.encode()).hexdigest()[:16]
        label=int(path.name.startswith('fi'))
        rows.append({'id':identifier,'path':path.relative_to(ROOT).as_posix(),'label':label,'split':'test','fold':0,
            'sha256':sha,'source_group':path.stem,'fps':fps,'frames':frames,'width':width,'height':height})
        if sha in prior:overlap.append({'path':path.name,'known_matches':prior[sha]})
    counts={str(c):sum(r['label']==c for r in rows) for c in (0,1)}
    if counts!={'0':500,'1':500}:raise ValueError('Expected 500 Fight and 500 NonFight clips')
    write_manifest(out/'manifest.csv',rows)
    fixed_models={
        'crowd_pose_interactions':ROOT/'output/centering_corrected_cpu_20261115/fold_1/runs/interactions_seed42/model.pt',
        'rwf_frozen_video':ROOT/'output/rwf_supervised_20261115/model.json',
    }
    fine=ROOT/'output/rwf_finetune_v2_20261115'
    if json.loads((fine/'promotion.json').read_text())['eligible_for_evaluation']:
        fixed_models['rwf_finetuned_video']=fine/'model.pt'
    write_json(out/'protocol.json',{'date':'2026-11-15','dataset':'Hockey Fight','mirror':'34data/hockey-fight-videos',
        'revision':'2009e360f0887c9d0495f684a488519a625b0293','archives_sha256':archive_hashes,
        'clips':1000,'class_counts':counts,'manifest_sha256':digest(out/'manifest.csv'),
        'models':{name:{'path':str(path),'sha256':digest(path)} for name,path in fixed_models.items()},
        'finetune_candidate':'Chosen epoch and threshold sealed on RWF validation before this external protocol and before any external scoring',
        'selection':'All released mirror clips; no external fitting, normalization, threshold or model selection',
        'sampling':'Same uniform 32 full-clip samples and official R3D-18 transform; pose settings from retained checkpoint',
        'device':'cuda','external_scores_seen_before_protocol':False,
        'primary':'Fixed RWF supervised video head; crowd pose is a transfer diagnostic',
        'limits':'Sports broadcast domain, not a surveillance deployment benchmark. Mirror class labels are supplied and unreviewed. Filenames do not identify source games, so source independence, near-duplicates and Kinetics pretraining overlap remain unaudited.'})
    write_json(out/'source_audit.json',{'known_byte_identical_overlaps':overlap,
        'prior_clips_compared':sum(len(v) for v in prior.values()),'external_unique_byte_hashes':len({r['sha256'] for r in rows}),
        'policy':'Keep all clips for descriptive reporting; report exact overlap if present. No claim that absence of byte duplicates proves independent footage.'})
    print(json.dumps({'clips':len(rows),'counts':counts,'byte_overlap':len(overlap)}),flush=True)


if __name__=='__main__':main()

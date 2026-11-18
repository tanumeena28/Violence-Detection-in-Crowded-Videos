"""A single frozen, memory-bounded RWF layer-4 fine-tuning study on CUDA."""
from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
import sys
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models.video import r3d_18, R3D_18_Weights
from sklearn.metrics import log_loss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import decode_sample, read_manifest, write_json
from affective.train import choose_threshold, metrics


class FineModel(nn.Module):
    def __init__(self, baseline):
        super().__init__()
        self.encoder = r3d_18(weights=None)
        self.encoder.fc = nn.Identity()
        self.head = nn.Linear(512, 1)
        self.register_buffer('mean', torch.tensor(baseline['mean'], dtype=torch.float32))
        self.register_buffer('std', torch.tensor(baseline['std'], dtype=torch.float32))
        with torch.no_grad():
            self.head.weight.copy_(torch.tensor(baseline['coefficients'], dtype=torch.float32)[None])
            self.head.bias.fill_(baseline['intercept'])

    def forward(self, x):
        b, windows = x.shape[:2]
        embedding = self.encoder(x.flatten(0, 1)).reshape(b, windows, 512).mean(1)
        # Fixed scaling was fitted on the original training subset only.
        return self.head((embedding.float()-self.mean)/self.std).flatten()


class VideoTensors(Dataset):
    def __init__(self, rows, cache):
        self.rows, self.cache = rows, cache

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        return torch.load(self.cache/f"{row['id']}.pt", map_location='cpu', weights_only=True), int(row['label'])


def write_predictions(path, rows, scores, threshold):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['id', 'path', 'split', 'label', 'score', 'prediction'])
        writer.writeheader()
        writer.writerows({**{key:r[key] for key in ('id','path','split','label')},
            'score':float(s), 'prediction':int(s>=threshold)} for r,s in zip(rows,scores))


def prepare(source, out):
    if out.exists():
        raise FileExistsError('Use a new named experiment')
    old = json.loads((source/'protocol.json').read_text())
    base = json.loads((source/'model.json').read_text())
    selection = json.loads((source/'selection.json').read_text())
    for name, expected in json.loads((source/'head_frozen.json').read_text())['artifacts_sha256'].items():
        if digest(source/name) != expected:
            raise ValueError('Reference head changed')
    out.mkdir(parents=True)
    shutil.copy2(source/'manifest.csv', out/'manifest.csv')
    plan = {'schema':'rwf-r3d18-layer4-finetune-v1', 'date':'2026-11-15',
        'source_experiment':str(source), 'source_protocol_sha256':digest(source/'protocol.json'),
        'manifest_sha256':digest(out/'manifest.csv'), 'baseline_model':base,
        'baseline_model_sha256':digest(source/'model.json'), 'baseline_selection':selection,
        'weights':str(source/'weights'/old['encoder']['weights_file']),
        'weights_sha256':old['encoder']['weights_sha256'], 'encoder':old['encoder'],
        'sampling':'Same 32 uniform frames and two chronological 16-frame windows as the original reference',
        'input_cache':'Official RGB transform, stored as float16 tensors; fully decoded frame count and source hash recorded',
        'trainable':'Only encoder layer4 convolutions and logistic head; all BatchNorm running statistics frozen',
        'normalization':'Fixed original train-only embedding mean/std; no fitting on validation or evaluation',
        'initialization':'Original validation-selected logistic head and pretrained encoder; subsequent development experiment',
        'epochs':8, 'batch_size_clips':2, 'gradient_accumulation':8, 'workers':2,
        'optimizer':'AdamW', 'backbone_lr':1e-5, 'head_lr':1e-4, 'weight_decay':1e-4,
        'gradient_clip':1., 'seed':42, 'precision':'CUDA float16 autocast with GradScaler; float32 parameters',
        'epoch_selection':'Lowest validation log loss; earliest epoch breaks exact ties',
        'threshold_selection':'Validation macro-F1 grid, existing choose_threshold tie rules',
        'promotion_rule':'Strictly improve validation log loss and macro-F1 with nondecreasing Fight recall',
        'selection_boundary':'Freeze selected checkpoint, threshold, all epoch records and promotion decision before any evaluation scoring',
        'candidate_count':1, 'device':'cuda', 'packages':old['packages'],
        'script_sha256':digest(Path(__file__)),
        'implementation_sha256':{p.name:digest(p) for p in (ROOT/'affective').glob('*.py')},
        'limits':'Exploratory supervised development. Supplied labels remain unchanged. Original RWF evaluation footage was previously inspected. No independent human review or pretraining/near-duplicate audit is implied.'}
    write_json(out/'protocol.json',plan)
    snapshot=out/'implementation_snapshot'
    shutil.copytree(ROOT/'affective',snapshot/'affective',ignore=shutil.ignore_patterns('__pycache__'))
    (snapshot/'scripts').mkdir()
    shutil.copy2(Path(__file__),snapshot/'scripts'/Path(__file__).name)
    (out/'run_snapshot.py').write_text('import sys\nfrom pathlib import Path\ne=Path(__file__).resolve().parent\n'
        'sys.path.insert(0,str(e/"implementation_snapshot"))\nfrom scripts.run_rwf_finetune import main\n'
        'if __name__ == "__main__":\n    sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]\n    main()\n',encoding='utf-8')
    return plan


def validate(out,plan):
    if digest(Path(__file__))!=plan['script_sha256']:
        raise ValueError('Use the frozen fine-tuning script')
    for name,expected in plan['implementation_sha256'].items():
        if digest(Path(__file__).resolve().parents[1]/'affective'/name)!=expected:
            raise ValueError('Use the frozen fine-tuning implementation')
    if digest(out/'manifest.csv')!=plan['manifest_sha256'] or digest(Path(plan['weights']))!=plan['weights_sha256']:
        raise ValueError('Frozen data split or weights changed')
    if any(version(name)!=expected for name,expected in plan['packages'].items()):
        raise ValueError('Use the recorded package versions')


def prepare_tensors(root,out,plan):
    rows=[r for r in read_manifest(out/'manifest.csv') if r['split'] in ('train','val')]
    cache=out/'tensor_cache';cache.mkdir(exist_ok=True)
    transform=R3D_18_Weights.KINETICS400_V1.transforms()
    records=[];started=time.perf_counter()
    for i,row in enumerate(rows,1):
        target=cache/f"{row['id']}.pt"
        metadata=target.with_suffix('.json')
        if target.exists() and metadata.exists():
            record=json.loads(metadata.read_text())
            if record['source_sha256']!=row['sha256'] or digest(target)!=record['tensor_sha256']:
                raise ValueError('Cached input changed')
            records.append(record);continue
        path=root/row['path']
        if digest(path)!=row['sha256']:
            raise ValueError('Raw development source changed')
        frames,indices,fps,decoded=decode_sample(path,32)
        rgb=torch.from_numpy(np.stack([im[...,::-1].copy() for im in frames])).permute(0,3,1,2)
        tensor=torch.stack([transform(rgb[:16]),transform(rgb[16:])]).half()
        if tensor.shape!=(2,3,16,112,112) or not torch.isfinite(tensor).all():
            raise ValueError('Invalid input tensor')
        torch.save(tensor,target)
        record={'id':row['id'],'split':row['split'],'source_sha256':row['sha256'],
            'frame_indices':indices.tolist(),'decoded_frames':decoded,'fps':fps,'tensor_sha256':digest(target)}
        write_json(metadata,record);records.append(record)
        if i==1 or i%100==0 or i==len(rows):
            print(f'Prepared development tensors {i}/{len(rows)} | {time.perf_counter()-started:.0f}s',flush=True)
    write_json(out/'input_audit.json',{'clips':records,'wall_seconds':time.perf_counter()-started,
        'evaluation_tensors_prepared':False,'tensor_bytes':sum((cache/f"{r['id']}.pt").stat().st_size for r in rows)})


def loader(rows,cache,plan,shuffle=False):
    return DataLoader(VideoTensors(rows,cache),batch_size=plan['batch_size_clips'],shuffle=shuffle,
        num_workers=plan['workers'],pin_memory=True,persistent_workers=True,
        generator=torch.Generator().manual_seed(plan['seed']))


def score_loader(model, batches):
    model.eval();scores=[]
    with torch.inference_mode():
        for x,_ in batches:
            with torch.autocast('cuda',dtype=torch.float16):
                logits=model(x.to('cuda',non_blocking=True))
            scores.extend(logits.float().sigmoid().cpu().numpy().tolist())
    return np.asarray(scores,np.float64)


def train(out,plan):
    random.seed(plan['seed']);np.random.seed(plan['seed']);torch.manual_seed(plan['seed']);torch.cuda.manual_seed_all(plan['seed'])
    torch.set_num_threads(4);torch.backends.cudnn.deterministic=True;torch.backends.cudnn.benchmark=False
    rows=read_manifest(out/'manifest.csv')
    train_rows=[r for r in rows if r['split']=='train'];val_rows=[r for r in rows if r['split']=='val']
    model=FineModel(plan['baseline_model'])
    original=r3d_18(weights=None)
    original.load_state_dict(torch.load(plan['weights'],map_location='cpu',weights_only=True));original.fc=nn.Identity()
    model.encoder.load_state_dict(original.state_dict());del original
    for p in model.encoder.parameters():p.requires_grad=False
    for p in model.encoder.layer4.parameters():p.requires_grad=True
    model.to('cuda')
    optimizer=torch.optim.AdamW([{'params':model.encoder.layer4.parameters(),'lr':plan['backbone_lr']},
        {'params':model.head.parameters(),'lr':plan['head_lr']}],weight_decay=plan['weight_decay'])
    scaler=torch.amp.GradScaler('cuda')
    train_batches=loader(train_rows,out/'tensor_cache',plan,True)
    val_batches=loader(val_rows,out/'tensor_cache',plan)
    y_val=np.asarray([r['label'] for r in val_rows]);history=[];best_loss=float('inf');best_epoch=None
    started=time.perf_counter();torch.cuda.reset_peak_memory_stats()
    (out/'epochs').mkdir(exist_ok=True)
    for epoch in range(1,plan['epochs']+1):
        model.train()
        for module in model.modules():
            if isinstance(module,nn.BatchNorm3d):module.eval()
        optimizer.zero_grad(set_to_none=True);total_loss=0.;seen=0
        for i,(x,y) in enumerate(train_batches):
            x=x.to('cuda',non_blocking=True);y=y.float().to('cuda',non_blocking=True)
            # Normalize each final partial accumulation group by its true size.
            group_size=min(plan['gradient_accumulation'],len(train_batches)-(i//plan['gradient_accumulation'])*plan['gradient_accumulation'])
            with torch.autocast('cuda',dtype=torch.float16):
                logits=model(x);loss=nn.functional.binary_cross_entropy_with_logits(logits,y)
            if not torch.isfinite(loss):raise ValueError('Nonfinite training loss')
            scaler.scale(loss/group_size).backward()
            if (i+1)%plan['gradient_accumulation']==0 or i+1==len(train_batches):
                scaler.unscale_(optimizer);nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],plan['gradient_clip'])
                scaler.step(optimizer);scaler.update();optimizer.zero_grad(set_to_none=True)
            total_loss+=float(loss.detach())*len(y);seen+=len(y)
        scores=score_loader(model,val_batches);val_loss=float(log_loss(y_val,scores));threshold=choose_threshold(y_val,scores)
        record={'epoch':epoch,'training_loss':total_loss/seen,'validation_log_loss':val_loss,
            'threshold':threshold,'validation':metrics(y_val,scores,threshold),'elapsed_seconds':time.perf_counter()-started}
        history.append(record)
        write_predictions(out/'epochs'/f'epoch_{epoch:02d}_validation.csv',val_rows,scores,threshold)
        write_json(out/'training_history.json',history)
        if val_loss<best_loss:
            best_loss,best_epoch=val_loss,epoch
            torch.save({'schema':plan['schema'],'state_dict':model.state_dict(),'threshold':threshold,'epoch':epoch,
                'baseline_model':plan['baseline_model'],'protocol_sha256':digest(out/'protocol.json')},out/'model.pt')
        print(json.dumps(record),flush=True)
    chosen=history[best_epoch-1];reference=plan['baseline_selection']
    criteria={'log_loss_improved':best_loss<min(c['validation_log_loss'] for c in reference['candidates']),
        'macro_f1_improved':chosen['validation']['macro_f1']>reference['validation']['macro_f1'],
        'fight_recall_not_reduced':chosen['validation']['recall_violent']>=reference['validation']['recall_violent']}
    promotion={'eligible_for_evaluation':all(criteria.values()),'criteria':criteria,'chosen_epoch':best_epoch,
        'candidate_validation':chosen,'baseline_validation':reference['validation']}
    write_json(out/'promotion.json',promotion)
    shutil.copy2(out/'epochs'/f'epoch_{best_epoch:02d}_validation.csv',out/'validation_predictions.csv')
    write_json(out/'training_audit.json',{'status':'complete','epochs':len(history),'gpu':torch.cuda.get_device_name(0),
        'peak_allocated_gpu_bytes':torch.cuda.max_memory_allocated(),'wall_seconds':time.perf_counter()-started,
        'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),
        'batch_norm_statistics':'Frozen throughout training','selection_inputs':'Validation only'})
    names=['model.pt','training_history.json','promotion.json','validation_predictions.csv','input_audit.json','training_audit.json']
    write_json(out/'head_frozen.json',{'status':'selected_before_evaluation','protocol_sha256':digest(out/'protocol.json'),
        'artifacts_sha256':{name:digest(out/name) for name in names},'boundary':plan['selection_boundary']})
    print('Fine-tuning selected and sealed: '+json.dumps(promotion),flush=True)


def verify(out,plan):
    seal=json.loads((out/'head_frozen.json').read_text())
    if digest(out/'protocol.json')!=seal['protocol_sha256']:raise ValueError('Fine-tuning protocol changed')
    for name,expected in seal['artifacts_sha256'].items():
        if digest(out/name)!=expected:raise ValueError('Selected fine-tuning artifact changed')
    history=json.loads((out/'training_history.json').read_text());promotion=json.loads((out/'promotion.json').read_text())
    assert promotion['chosen_epoch']==min(history,key=lambda r:r['validation_log_loss'])['epoch']
    checkpoint=torch.load(out/'model.pt',map_location='cpu',weights_only=True)
    model=FineModel(plan['baseline_model']);model.load_state_dict(checkpoint['state_dict']);model.to('cuda')
    rows=[r for r in read_manifest(out/'manifest.csv') if r['split']=='val']
    scores=score_loader(model,loader(rows,out/'tensor_cache',plan));labels=np.asarray([r['label'] for r in rows])
    with (out/'validation_predictions.csv').open(newline='') as stream:saved=list(csv.DictReader(stream))
    np.testing.assert_allclose(scores,[float(r['score']) for r in saved],atol=1e-7,rtol=0)
    assert checkpoint['threshold']==choose_threshold(labels,scores)
    assert metrics(labels,scores,checkpoint['threshold'])==promotion['candidate_validation']['validation']
    write_json(out/'audit.json',{'status':'pass','validation_scores_reproduced':len(scores),
        'gpu':torch.cuda.get_device_name(0),'selected_epoch_reproduced':True,'head_seal_verified':True,
        'evaluation_scored':False})
    names=['protocol.json','manifest.csv',*seal['artifacts_sha256'].keys(),'head_frozen.json']
    write_json(out/'completion.json',{'status':'development_complete','artifacts_sha256':{name:digest(out/name) for name in names}})
    text='# RWF layer-4 fine-tuning study\n\n'+json.dumps(promotion,indent=2)+'\n\n'+plan['limits']+'\n'
    (out/'RESULTS.md').write_text(text,encoding='utf-8')
    print(text,flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('output/rwf_supervised_20261115'))
    p.add_argument('--out',type=Path,default=Path('output/rwf_finetune_20261115'))
    p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--prepare-only',action='store_true');p.add_argument('--verify-only',action='store_true')
    args=p.parse_args();out=args.out.resolve()
    plan=json.loads((out/'protocol.json').read_text()) if out.exists() else prepare(args.source.resolve(),out)
    validate(out,plan)
    if args.prepare_only:print('Fine-tuning protocol frozen before training',flush=True);return
    if not args.verify_only and not (out/'head_frozen.json').exists():
        torch.set_num_threads(4);prepare_tensors(args.root.resolve(),out,plan);train(out,plan)
    verify(out,plan)


if __name__=='__main__':main()

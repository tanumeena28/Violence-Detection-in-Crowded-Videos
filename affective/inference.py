"""Persistent CUDA predictors and bounded video decoding for final delivery."""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from torchvision.models.video import r3d_18,R3D_18_Weights

from .cross_validation import digest
from .demo import load_model
from .features import build_features
from .motion import score_linear
from .tracking import ClipTracker,pack_tracks
from .train import VARIANTS

ROOT=Path(__file__).resolve().parents[1]


def count_frames(video):
    cap=cv2.VideoCapture(str(video));fps=float(cap.get(cv2.CAP_PROP_FPS));count=0
    try:
        while True:
            ok,_=cap.read()
            if not ok:break
            count+=1
    finally:cap.release()
    if count<2 or not np.isfinite(fps) or fps<=0:raise ValueError('Video must contain at least two decodable frames and valid FPS')
    return count,fps


def decode_sample_bounded(video,count=32):
    """Count with a full decode, then retain only the exact uniform samples."""
    total,fps=count_frames(video)
    indices=np.linspace(0,total-1,count).round().astype(np.int32)
    needed=set(indices.tolist());sampled={};cap=cv2.VideoCapture(str(video));position=0
    try:
        while True:
            ok,frame=cap.read()
            if not ok:break
            if position in needed:sampled[position]=frame
            position+=1
    finally:cap.release()
    if position!=total or set(sampled)!=needed:raise ValueError('Video decode changed between bounded passes')
    return [sampled[int(i)] for i in indices],indices,fps,total


def iter_video_windows(video,seconds=5.):
    if not np.isfinite(seconds) or seconds<=0:raise ValueError('Window seconds must be positive')
    cap=cv2.VideoCapture(str(video));fps=float(cap.get(cv2.CAP_PROP_FPS))
    if not np.isfinite(fps) or fps<=0:cap.release();raise ValueError('Invalid video FPS')
    limit=max(2,round(seconds*fps));start=0;frames=[]
    try:
        while True:
            ok,frame=cap.read()
            if not ok:break
            frames.append(frame)
            if len(frames)==limit:
                indices=np.linspace(0,len(frames)-1,32).round().astype(np.int32)
                yield [frames[int(i)] for i in indices],indices,fps,len(frames),start/fps
                start+=len(frames);frames=[]
        if frames:
            # A one-frame tail is recorded but cannot receive a violence prediction.
            if len(frames)==1:
                yield None,None,fps,1,start/fps
            else:
                indices=np.linspace(0,len(frames)-1,32).round().astype(np.int32)
                yield [frames[int(i)] for i in indices],indices,fps,len(frames),start/fps
    finally:cap.release()


class VideoPredictor:
    def __init__(self,experiment,device='cuda'):
        self.experiment=Path(experiment).resolve();self.device=device
        self.plan=json.loads((self.experiment/'protocol.json').read_text())
        seal=json.loads((self.experiment/'head_frozen.json').read_text())
        if digest(self.experiment/'protocol.json')!=seal['protocol_sha256']:raise ValueError('Sealed video protocol changed')
        self.finetuned=self.plan['schema']=='rwf-r3d18-layer4-finetune-v1'
        torch.set_num_threads(4);torch.backends.cudnn.deterministic=True;torch.backends.cudnn.benchmark=False
        if self.finetuned:
            from scripts.run_rwf_finetune import FineModel
            path=self.experiment/'model.pt'
            if digest(path)!=seal['artifacts_sha256']['model.pt']:raise ValueError('Fine-tuned model changed')
            checkpoint=torch.load(path,map_location='cpu',weights_only=True)
            self.model=FineModel(checkpoint['baseline_model']);self.model.load_state_dict(checkpoint['state_dict'])
            self.threshold=checkpoint['threshold'];self.model_hash=digest(path)
        else:
            if self.plan['schema']!='rwf-supervised-frozen-r3d18-v1':raise ValueError('Unsupported final video model')
            path=self.experiment/'model.json'
            if digest(path)!=seal['artifacts_sha256']['model.json']:raise ValueError('Video head changed')
            self.head=json.loads(path.read_text());self.threshold=self.head['threshold'];self.model_hash=digest(path)
            weights=self.experiment/'weights'/self.plan['encoder']['weights_file']
            if digest(weights)!=self.plan['encoder']['weights_sha256']:raise ValueError('Video encoder weights changed')
            self.model=r3d_18(weights=None)
            self.model.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True));self.model.fc=torch.nn.Identity()
        self.model.eval().to(device);self.transform=R3D_18_Weights.KINETICS400_V1.transforms()

    def process(self,images,indices,fps,decoded):
        started=time.perf_counter()
        rgb=torch.from_numpy(np.stack([im[...,::-1].copy() for im in images])).permute(0,3,1,2)
        tensor=torch.stack([self.transform(rgb[:16]),self.transform(rgb[16:])]).to(self.device)
        with torch.inference_mode():
            if self.finetuned:
                # Match the sealed training input storage precision.
                with torch.autocast(self.device.split(':')[0],dtype=torch.float16,enabled=self.device.startswith('cuda')):
                    clip=tensor.half()[None] if self.device.startswith('cuda') else tensor[None]
                    # Validation used two clips per batch. Preserve that convolution
                    # shape for single-video calls, including CUDA rounding behavior.
                    logits=self.model(clip.expand(self.plan['batch_size_clips'],*clip.shape[1:]).contiguous())
                score=float(logits[0].float().sigmoid().item())
            else:
                embedding=self.model(tensor).mean(0).cpu().numpy().astype(np.float64)
                score=float(score_linear(embedding[None],self.head)[0])
        return {'model':'fine_tuned_video' if self.finetuned else 'frozen_video','score':score,'threshold':self.threshold,
            'prediction':int(score>=self.threshold),'decision':'violent' if score>=self.threshold else 'nonviolent',
            'abstain':False,'device':self.device,'model_sha256':self.model_hash,'decoded_frames':decoded,
            'sampled_frames':indices.tolist(),'duration_seconds':decoded/fps,'processing_seconds':time.perf_counter()-started,
            'scope':'Whole-clip score; not calibrated or person-level attribution'}

    def predict(self,video):
        started=time.perf_counter();images,indices,fps,decoded=decode_sample_bounded(video)
        result=self.process(images,indices,fps,decoded)
        result.update({'source_sha256':digest(video),'seconds_including_decode':time.perf_counter()-started})
        return result


class PosePredictor:
    def __init__(self,checkpoint=None,device='cuda'):
        from ultralytics import YOLO
        path=Path(checkpoint or ROOT/'output/centering_corrected_cpu_20261115/fold_1/runs/interactions_seed42/model.pt')
        self.model,self.saved=load_model(path);self.model.to(device).eval();self.device=device;self.model_hash=digest(path)
        settings=json.loads((ROOT/'output/centering_corrected_cpu_20261115/pose_settings.json').read_text())
        weights=ROOT/'models'/settings['weights']
        if digest(weights)!=settings['weights_sha256'] or self.saved['pose_signature']!=settings['signature']:
            raise ValueError('Pose extraction provenance differs from retained model')
        self.pose=YOLO(str(weights));self.settings=settings

    def process(self,images,indices,fps,decoded):
        started=time.perf_counter();tracker=ClipTracker();detections=[]
        for start in range(0,32,self.settings['batch_size']):
            results=self.pose.predict(images[start:start+self.settings['batch_size']],device=self.device,
                imgsz=self.settings['image_size'],conf=.2,max_det=100,verbose=False)
            for result in results:
                if result.keypoints is None or result.boxes is None or len(result.boxes)==0:
                    boxes=np.zeros((0,4),np.float32);points=np.zeros((0,17,3),np.float32)
                else:
                    boxes=result.boxes.xyxyn.cpu().numpy().astype(np.float32)
                    points=np.concatenate([result.keypoints.xyn.cpu().numpy(),result.keypoints.conf.cpu().numpy()[...,None]],-1).astype(np.float32)
                detections.append({'boxes':boxes,'keypoints':points,'ids':tracker.update(boxes,len(detections))})
        points,boxes,present,tracks,total=pack_tracks(detections,8)
        valid=(points[...,2]>=.25)&present[...,None]
        usable=float((valid.sum((1,2))>=5).mean())
        reliability,interactions=VARIANTS[self.saved['variant']]
        features,mask=build_features(points,boxes,present,indices.astype(np.float32)/fps,reliability,interactions,
            feature_schema=self.saved['feature_schema'])
        scaled=np.clip((features-self.saved['mean'].numpy())/self.saved['std'].numpy(),-10,10)*mask[...,None]
        with torch.inference_mode():
            score=float(self.model(torch.from_numpy(scaled[None].astype(np.float32)).to(self.device),
                torch.from_numpy(mask[None]).to(self.device)).sigmoid().item())
        abstain=usable<.25;threshold=self.saved['threshold']
        return {'model':'crowd_pose_interactions','score':score,'threshold':threshold,'prediction':int(score>=threshold),
            'decision':'insufficient pose evidence' if abstain else 'violent' if score>=threshold else 'nonviolent',
            'abstain':abstain,'usable_pose_fraction':usable,'device':self.device,'model_sha256':self.model_hash,
            'decoded_frames':decoded,'sampled_frames':indices.tolist(),'duration_seconds':decoded/fps,
            'processing_seconds':time.perf_counter()-started,'scope':'Clip-level pose model; track IDs are not violent-person labels'}

    def predict(self,video):
        started=time.perf_counter();images,indices,fps,decoded=decode_sample_bounded(video)
        result=self.process(images,indices,fps,decoded)
        result.update({'source_sha256':digest(video),'seconds_including_decode':time.perf_counter()-started})
        return result


def selected_video_experiment():
    pointer=ROOT/'output/final_delivery_20261115/active_model.json'
    if pointer.exists():
        record=json.loads(pointer.read_text())
        return ROOT/record['experiment']
    return ROOT/'output/rwf_supervised_20261115'

"""Shared per-person TCN followed by masked set pooling and clip classification."""
import torch
from torch import nn


class TemporalBlock(nn.Module):
    def __init__(self, hidden, dilation, dropout):
        super().__init__()
        self.net = nn.Sequential(nn.Conv1d(hidden, hidden, 3, padding=dilation, dilation=dilation),
                                 nn.GELU(), nn.Dropout(dropout),
                                 nn.Conv1d(hidden, hidden, 1), nn.GELU())

    def forward(self, x):
        return x + self.net(x)


class CrowdTCN(nn.Module):
    def __init__(self, input_dim, hidden=48, dropout=0.2):
        super().__init__()
        self.project = nn.Conv1d(input_dim, hidden, 1)
        self.temporal = nn.Sequential(*[TemporalBlock(hidden, d, dropout) for d in (1, 2, 4)])
        # mean and max over observed people, plus measured pose coverage.
        self.classifier = nn.Sequential(nn.Linear(hidden * 2 + 1, hidden), nn.GELU(),
                                        nn.Dropout(dropout), nn.Linear(hidden, 1))

    def forward(self, features, mask):
        b, t, p, f = features.shape
        x = features.permute(0, 2, 3, 1).reshape(b * p, f, t)
        m = mask.permute(0, 2, 1).reshape(b * p, 1, t)
        x = self.project(x * m) * m
        for block in self.temporal:
            x = block(x) * m
        people = (x.sum(-1) / m.sum(-1).clamp_min(1)).reshape(b, p, -1)
        valid = mask.sum(1) > 0
        pooled_mean = (people * valid[..., None]).sum(1) / valid.sum(1, keepdim=True).clamp_min(1)
        pooled_max = people.masked_fill(~valid[..., None], -1e4).max(1).values
        pooled_max = torch.where(valid.any(1, keepdim=True), pooled_max, torch.zeros_like(pooled_max))
        coverage = mask.mean((1, 2)).unsqueeze(1)
        return self.classifier(torch.cat([pooled_mean, pooled_max, coverage], 1)).squeeze(-1)

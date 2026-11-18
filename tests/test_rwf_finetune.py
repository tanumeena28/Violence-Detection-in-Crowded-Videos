import pytest
import torch
from torch import nn

from scripts.run_rwf_finetune import FineModel, freeze_backbone


def test_bounded_finetuning_freezes_early_layers_and_batch_norm_parameters():
    baseline={'mean':[0.]*512,'std':[1.]*512,'coefficients':[.001]*512,'intercept':0.}
    model=FineModel(baseline)
    freeze_backbone(model)
    assert all(not p.requires_grad for p in model.encoder.layer3.parameters())
    assert all(p.requires_grad for p in model.head.parameters())
    for module in model.encoder.layer4.modules():
        if isinstance(module,nn.BatchNorm3d):
            assert all(not p.requires_grad for p in module.parameters())
        if isinstance(module,nn.Conv3d):
            assert all(p.requires_grad for p in module.parameters())


@pytest.mark.skipif(not torch.cuda.is_available(),reason='Local GPU preflight')
def test_cuda_gradients_reach_only_the_planned_layers_without_bn_updates():
    torch.set_num_threads(4)
    baseline={'mean':[0.]*512,'std':[1.]*512,'coefficients':[.001]*512,'intercept':0.}
    model=FineModel(baseline).to('cuda');freeze_backbone(model);model.train()
    running={}
    for name,module in model.named_modules():
        if isinstance(module,nn.BatchNorm3d):
            module.eval();running[name]=module.running_mean.clone()
    with torch.autocast('cuda',dtype=torch.float16):
        logits=model(torch.randn(1,2,3,16,112,112,device='cuda'))
        loss=nn.functional.binary_cross_entropy_with_logits(logits,torch.ones(1,device='cuda'))
    loss.backward()
    assert torch.isfinite(loss)
    assert model.encoder.layer4[0].conv1[0].weight.grad is not None
    assert model.encoder.layer3[0].conv1[0].weight.grad is None
    assert model.head.weight.grad is not None
    for name,module in model.named_modules():
        if name in running:
            torch.testing.assert_close(module.running_mean,running[name],rtol=0,atol=0)

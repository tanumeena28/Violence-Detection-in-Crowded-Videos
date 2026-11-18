param([switch]$CpuOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    py -3.13 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.13 environment creation failed' }
}
$pilotPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$torchIndex = if ($CpuOnly) { 'https://download.pytorch.org/whl/cpu' } else { 'https://download.pytorch.org/whl/cu128' }
& $pilotPython -m pip install torch torchvision --index-url $torchIndex
if ($LASTEXITCODE -ne 0) { throw 'PyTorch installation failed' }
& $pilotPython -m pip install -r requirements-pilot.txt
if ($LASTEXITCODE -ne 0) { throw 'Pilot dependencies installation failed' }
@'
import torch
print('Torch:', torch.__version__, 'CUDA:', torch.cuda.is_available())
'@ | & $pilotPython -
if ($LASTEXITCODE -ne 0) { throw 'PyTorch verification failed' }

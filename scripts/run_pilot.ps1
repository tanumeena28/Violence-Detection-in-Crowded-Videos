param([int]$Epochs = 180, [switch]$SkipExtract)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pilotPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pilotPython)) { throw 'Run scripts/setup_pilot.ps1 first' }
& $pilotPython -m affective.cli prepare
if ($LASTEXITCODE -ne 0) { throw 'Dataset preparation failed' }
if (-not $SkipExtract) {
    & $pilotPython -m affective.cli extract
    if ($LASTEXITCODE -ne 0) { throw 'Pose extraction failed' }
}
& $pilotPython -m affective.cli train --epochs $Epochs
if ($LASTEXITCODE -ne 0) { throw 'Training failed' }
& $pilotPython -m affective.cli demo --count 6
if ($LASTEXITCODE -ne 0) { throw 'Demo generation failed' }
& $pilotPython -m affective.cli motion
if ($LASTEXITCODE -ne 0) { throw 'Motion control failed' }
& $pilotPython -m affective.cli analyze
if ($LASTEXITCODE -ne 0) { throw 'Failure analysis failed' }
& $pilotPython scripts/audit_pilot.py
if ($LASTEXITCODE -ne 0) { throw 'Pilot artifact audit failed' }
& $pilotPython -m affective.cli report
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed' }
Write-Host 'Open output/pilot/index.html for the meeting demonstration.'

param([string]$Video = '', [switch]$VerifyOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pilotPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$demoOutput = Join-Path $projectRoot 'output\source_corrected'
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath $pilotPython)) { throw 'Pilot Python environment is missing. Run scripts/setup_pilot.ps1.' }
& $pilotPython scripts/audit_pilot.py --out $demoOutput
if ($LASTEXITCODE -ne 0) { throw 'Saved pipeline verification failed' }
if ($Video) {
    $resolvedVideo = (Resolve-Path -LiteralPath $Video).Path
    & $pilotPython -m affective.cli --out $demoOutput demo --run combined_seed42 --video $resolvedVideo
    if ($LASTEXITCODE -ne 0) { throw 'Raw-video pipeline failed' }
    & $pilotPython scripts/check_new_video.py --out $demoOutput
    if ($LASTEXITCODE -ne 0) { throw 'New-video output verification failed' }
}
if (-not $VerifyOnly) {
    & $pilotPython -m affective.cli --out $demoOutput report
    if ($LASTEXITCODE -ne 0) { throw 'Results report generation failed' }
}
Write-Host "Working pipeline verified. Open: $demoOutput\index.html"
Write-Host "Discussion guide: $projectRoot\output\oct24\DEMO_GUIDE.md"
if ($Video) { Write-Host "Raw-video output: $demoOutput\new_video_demo.json and demos\new_video_*.mp4" }

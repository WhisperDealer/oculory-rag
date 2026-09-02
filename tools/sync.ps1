# Thin wrapper so the sync can be run from PowerShell 5.1 without remembering the python path.
# All logic lives in sync.py (stdlib only). Usage: powershell -File tools/sync.ps1 --check
param([Parameter(ValueFromRemainingArguments = $true)] $Args)
$script = Join-Path $PSScriptRoot 'sync.py'
& python $script @Args
if ($LASTEXITCODE -eq 9009 -or $LASTEXITCODE -eq 49) {
    # 'python' resolved to the Microsoft Store stub; fall back to the py launcher.
    & py -3 $script @Args
}
exit $LASTEXITCODE

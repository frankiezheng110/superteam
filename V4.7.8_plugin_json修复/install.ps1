$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Error "[superteam] error: 'claude' was not found in PATH"
}

Write-Host "[superteam] validating plugin..."
& claude plugin validate $RootDir

$BinDir = Join-Path $HOME '.claude\bin'
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

$PsLauncher = Join-Path $BinDir 'claude-superteam.ps1'
$CmdLauncher = Join-Path $BinDir 'claude-superteam.cmd'

$PsContent = @"
`$ErrorActionPreference = 'Stop'
& claude --plugin-dir "$RootDir" @args
"@
Set-Content -Path $PsLauncher -Value $PsContent -Encoding ASCII

$CmdContent = @"
@echo off
claude --plugin-dir "$RootDir" %*
"@
Set-Content -Path $CmdLauncher -Value $CmdContent -Encoding ASCII

Write-Host ""
Write-Host "[superteam] installed launchers:"
Write-Host "  $PsLauncher"
Write-Host "  $CmdLauncher"

# V4.6.0: merge hooks into user-level ~/.claude/settings.json (JSON deep-merge)
$SettingsTarget = Join-Path $HOME '.claude\settings.json'
$HookTemplate = Join-Path $RootDir 'hooks\hooks_settings_template.json'
$MergeScript = Join-Path $RootDir 'hooks\install_merge.py'

if (Test-Path $HookTemplate) {
    Write-Host ""
    Write-Host "[superteam] merging V4.6.0 hooks into $SettingsTarget ..."
    & python $MergeScript $HookTemplate $SettingsTarget
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[superteam] hook merge failed"
    }
    Write-Host "[superteam] running matrix self-check ..."
    & python (Join-Path $RootDir 'hooks\matrix_selfcheck.py')
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[superteam] matrix self-check failed — hook files and matrix are out of sync"
    }
}

Write-Host "[superteam] usage:"
Write-Host "  cd <target-repo>"
Write-Host "  claude-superteam"

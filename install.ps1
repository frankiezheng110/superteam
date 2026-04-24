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
Write-Host "[superteam] usage:"
Write-Host "  cd <target-repo>"
Write-Host "  claude-superteam"

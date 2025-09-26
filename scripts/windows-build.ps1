#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

$dist = Join-Path $repoRoot "dist"
if (-not (Test-Path $dist)) {
    New-Item -ItemType Directory -Path $dist | Out-Null
}

$stagingExe = Join-Path $dist "ytsprint.exe"
if (Test-Path $stagingExe) {
    Remove-Item -Force $stagingExe
}

Remove-Item -ErrorAction SilentlyContinue -Recurse build
Remove-Item -ErrorAction SilentlyContinue ytsprint.spec

$pythonArch = python -c "import platform; print(platform.architecture()[0])"
switch ($pythonArch) {
    "64bit" { $artifactArch = "x64" }
    "32bit" { $artifactArch = "x86" }
    default {
        throw "Unsupported Python architecture: $pythonArch. Install either 64-bit or 32-bit interpreter."
    }
}

Write-Host "Building Windows executable for architecture=$artifactArch..."
pyinstaller --onefile --clean --name ytsprint ytsprint/cli.py

$builtExe = Join-Path $dist "ytsprint.exe"
if (-not (Test-Path $builtExe)) {
    throw "PyInstaller output not found at $builtExe"
}

$targetExe = Join-Path $dist ("ytsprint-windows-{0}.exe" -f $artifactArch)
if (Test-Path $targetExe) {
    Remove-Item -Force $targetExe
}
Move-Item -Path $builtExe -Destination $targetExe -Force

Write-Host "Windows binary available at $targetExe"

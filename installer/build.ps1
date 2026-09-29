param([string]$Compiler = '')
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$source = Join-Path $repo 'Fusion_addin\HelixPathPilot'
$versionText = [IO.File]::ReadAllText((Join-Path $source 'version.py'))
$parts = foreach ($part in @('MAJOR','MINOR','PATCH')) {
    $match = [regex]::Match($versionText, "(?m)^VERSION_$part = (\d+)$")
    if (-not $match.Success) { throw "Missing version component: $part" }
    $match.Groups[1].Value
}
$version = $parts -join '.'
# Windows PowerShell 5 cannot ConvertFrom-Json the empty description key in Fusion manifests.
$manifest = [IO.File]::ReadAllText((Join-Path $source 'HelixPathPilot.manifest'))
$manifestVersion = [regex]::Match($manifest, '"version"\s*:\s*"([0-9.]+)"').Groups[1].Value
if ($manifestVersion -ne $version) { throw 'Manifest and version.py disagree. Run tools/sync_manifest.py first.' }
if (-not $Compiler) {
    $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($command) { $Compiler = $command.Source }
    else { $Compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe' }
}
if (-not (Test-Path -LiteralPath $Compiler)) { throw 'Inno Setup compiler not found. Pass -Compiler <path to ISCC.exe>.' }
& $Compiler "/DAppVersion=$version" (Join-Path $PSScriptRoot 'HelixPathPilot.iss')
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed: $LASTEXITCODE" }
$exe = Join-Path $PSScriptRoot "dist\HelixPathPilot-$version-Windows-Setup.exe"
$hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText("$exe.sha256", "$hash  $([IO.Path]::GetFileName($exe))`n", [Text.UTF8Encoding]::new($false))
Write-Output "Built: $exe"

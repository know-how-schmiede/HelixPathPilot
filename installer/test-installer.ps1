param([Parameter(Mandatory=$true)][string]$Installer)
$ErrorActionPreference = 'Stop'
$registryKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{1D69E956-5380-4F80-9383-6D89CEBB0493}_is1'
if (Test-Path $registryKey) { throw 'An installer-managed installation exists. Run this test in a clean Windows account.' }
$repo = Split-Path $PSScriptRoot -Parent
$source = Join-Path $repo 'Fusion_addin\HelixPathPilot'
$testRoot = Join-Path $PSScriptRoot ('.test-' + [guid]::NewGuid().ToString('N'))
$destination = Join-Path $testRoot 'HelixPathPilot'
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$exe = (Resolve-Path -LiteralPath $Installer).Path
$report = @()
foreach ($language in @('en','de')) {
    $log = Join-Path $testRoot "$language.log"
    $arguments = "/VERYSILENT /SUPPRESSMSGBOXES /SP- /NORESTART /LANG=$language /DIR=`"$destination`" /LOG=`"$log`""
    $process = Start-Process -FilePath $exe -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Installation failed: $($process.ExitCode). See $log" }
    $count = 0
    foreach ($file in Get-ChildItem -LiteralPath $source -File -Recurse) {
        $relative = $file.FullName.Substring($source.Length + 1)
        if ($relative -match '(^|\\)(__pycache__|\.vscode|\.idea|\.git)(\\|$)|\.py[co]$|(^|\\)\.gitkeep$|^presets\\user\\') { continue }
        $installed = Join-Path $destination $relative
        if (-not (Test-Path -LiteralPath $installed)) { throw "Missing payload: $relative" }
        if ((Get-FileHash -LiteralPath $installed).Hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash) { throw "Payload mismatch: $relative" }
        $count++
    }
    if (Test-Path -LiteralPath (Join-Path $destination '.vscode')) { throw 'Editor configuration was packaged.' }
    $report += "$language : exit 0, $count payload file hashes match."
    if ($language -eq 'en') {
        # The German update must replace even an edited Python source file.
        [IO.File]::WriteAllText((Join-Path $destination 'version.py'), '# simulated old source')
        [IO.File]::WriteAllText((Join-Path $destination 'user-note.txt'), 'preserve')
    }
}
$uninstaller = Join-Path $destination 'unins000.exe'
$process = Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Uninstall failed: $($process.ExitCode)" }
if (Test-Path -LiteralPath (Join-Path $destination 'HelixPathPilot.py')) { throw 'Uninstall left packaged source behind.' }
if (-not (Test-Path -LiteralPath (Join-Path $destination 'user-note.txt'))) { throw 'Uninstall removed an unowned file.' }
if (Test-Path $registryKey) { throw 'Uninstall registry entry remains.' }
$report += 'Uninstall: exit 0, packaged source removed, unowned file preserved, registration removed.'
$report += "Logs: $testRoot"
$report | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'dist\installer-test-report.txt') -Encoding UTF8
$report

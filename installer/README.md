# Windows installer / Windows-Installer

## Deutsch

`dist/HelixPathPilot-0.6.3-Windows-Setup.exe` enthält **Deutsch und Englisch**
mit Sprachauswahl. Der Installer installiert die bestätigte Add-in-Version 0.6.3;
die Paketierung ändert deren Versionsnummer nicht. Die EXE ist nicht signiert.

Fusion schließen, EXE starten und Ziel prüfen. Nach der Installation Fusion neu
starten und HelixPathPilot unter „Skripte und Add-Ins“ ausführen. Die Oberfläche
des Add-ins bleibt deutsch. Keine Administratorrechte erforderlich.

Die automatische Erkennung prüft unter `%APPDATA%`:

1. `Autodesk\Autodesk Fusion\API\AddIns\HelixPathPilot` mit bestehendem Manifest.
2. `Autodesk\Autodesk Fusion 360\API\AddIns\HelixPathPilot` mit bestehendem Manifest.
3. Vorhandenen modernen, danach bisherigen AddIns-Ordner.
4. Ohne vorhandene Ordner den modernen Standardpfad.

Eine frühere Installation dieses Setups behält ihr gewähltes Ziel. Bei mehreren
manuellen Kopien oder einem benutzerdefinierten API-Pfad das Ziel im Assistenten
prüfen und gegebenenfalls ändern. Fusion-Einstellungen werden nicht ausgelesen
oder verändert. Dateien werden im Ziel aktualisiert; andere Installationen
werden nicht entfernt. Eigene Codeänderungen vor einem Update sichern.
Benutzervorlagen unter `%APPDATA%\HelixPathPilot\presets` bleiben unangetastet.

Deinstallation über Windows → Apps → HelixPathPilot, vorher Fusion schließen.
Nur vom Setup installierte Dateien werden entfernt; zusätzliche Dateien und
Python-Cacheordner können zurückbleiben. Es gibt keine rekursive Komplettlöschung.

### Erneut bauen

Inno Setup 6 installieren und aus dem Repository aufrufen:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File installer/build.ps1
```

`-Compiler "C:\...\ISCC.exe"` erlaubt einen anderen Compilerpfad.
Die Ausführungsrichtlinie gilt nur für diesen Prozess. Das Buildskript liest
`version.py`, prüft die Manifest-Version und erzeugt EXE und SHA-256-Prüfsumme.
Das eigentliche Inno-Skript ist `HelixPathPilot.iss`. Paketquelle ist ausschließlich
`Fusion_addin/HelixPathPilot`. Entwicklungsordner, Python-Caches und lokale
Vorlagen werden ausgeschlossen. `dist` ist als Buildausgabe durch Git ignoriert;
die EXE kann als Release-Anhang verteilt werden.

### Prüfung am 2026-09-29

Gebaut mit Inno Setup 6.7.0. Englische Neuinstallation und deutsches Update in
einen separaten Testordner: Exitcode 0, jeweils 63 identische Datei-Hashes.
Das Update ersetzt auch absichtlich veränderten Python-Code. Deinstallation:
Exitcode 0, installierte Quelldateien und Registrierung entfernt, zusätzliche
Testdatei erhalten. Erkannter Standardpfad auf diesem Rechner:
`%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\HelixPathPilot`.

Der Test hat die tatsächliche Fusion-Installation nicht verändert. Interaktive
Darstellung des Assistenten, Installation auf einem zweiten PC und Start des
Add-ins aus einer durch Setup installierten Kopie sind noch manuell zu prüfen.
Die Add-in-Funktion 0.6.3 wurde vom Benutzer bereits bestätigt.

Wiederholbarer Test (nur ohne vorhandene Setup-Registrierung, idealerweise in
einem separaten Windows-Testkonto):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File installer/test-installer.ps1 -Installer installer/dist/HelixPathPilot-0.6.3-Windows-Setup.exe
```

Der Test erzeugt vorübergehend den Windows-Deinstallationseintrag, entfernt ihn
anschließend und behält Logs unter `.test-*`. Das Ergebnis liegt unter
`dist/installer-test-report.txt`. Scheitert der Test vor der Deinstallation,
den Uninstaller im ausgegebenen Testordner ausführen, bevor erneut getestet wird.

## English

The EXE includes **English and German** with a language selector and installs
the confirmed add-in version 0.6.3 for the current Windows user. No administrator
rights are required. The executable is unsigned; the add-in UI remains German.

Close Fusion before installation, updates or removal. Setup detects the current
and legacy Fusion AddIns locations, preferring an existing HelixPathPilot
manifest; a previous setup-managed destination is retained. Review the destination
if you use a custom Fusion API directory or have multiple copies. Restart Fusion
and run the add-in from Scripts and Add-Ins after installation.

Personal presets outside the installation folder are preserved. Updates replace
packaged code; back up custom modifications first. Uninstall through Windows Apps.
Unowned files and generated Python caches are not recursively deleted.

Build using the PowerShell command above. `build.ps1` checks the source/manifest
versions and creates the multilingual EXE and SHA-256 checksum under `dist`.
The English install, German update and uninstall tests passed, including all
63 payload hashes and preservation of an unowned file. Interactive wizard layout,
a second PC and Fusion startup after setup installation still require manual checks.

## Sources / Quellen

- [Autodesk: add-in locations and custom API paths](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WritingDebugging_UM.htm)
- [Inno Setup: non-administrative installation](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm)
- [Inno Setup: languages](https://jrsoftware.org/ishelp/topic_languagessection.htm)

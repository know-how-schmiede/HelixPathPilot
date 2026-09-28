# CodeX Plan – HelixPathPilot

## Ziel

Dieses Dokument beschreibt, wie das Projekt **HelixPathPilot** strukturiert, entwickelt und dokumentiert werden soll.

HelixPathPilot ist ein Autodesk-Fusion-Add-in zur Erzeugung von:

- parametrischen Helices
- Helices mit variabler Steigung
- Helices mit variablem Durchmesser
- Helices mit mehreren Abschnitten
- oberflächengeführten Helices auf Rotationskörpern
- speicherbaren Vorlagen / Presets
- später optional Sweep-/Drahtkörpern

## Grundsätze für die Umsetzung

CodeX soll das Projekt so entwickeln, dass:

1. die mathematische Logik möglichst getrennt von der Fusion-API bleibt,
2. die Dokumentation während des Projekts aktiv gepflegt wird,
3. der Entwicklungsstand jederzeit nachvollziehbar ist,
4. neue Ideen und Änderungen nicht verloren gehen,
5. jede größere Änderung in `version.py`, `docs/timeline.md` und `docs/ablaufplan.md` dokumentiert wird.

## Vorlage-Add-in

Im Ordner:

```text
Fusion_addin/
```

legt der Benutzer ein **leeres Beispiel-AddIn** als Vorlage ab.

CodeX soll dieses Add-in als technische Ausgangsbasis verwenden und die eigentliche Projektstruktur darauf aufbauen bzw. daran anlehnen.

Die Vorlage soll nicht unkontrolliert überschrieben werden.

## Empfohlene Projektstruktur

```text
HelixPathPilot/
│
├── Fusion_addin/
│   └── <leeres Beispiel-AddIn als Vorlage>
│
├── HelixPathPilot/
│   ├── commands/
│   │   ├── createParametricHelix/
│   │   ├── createSurfaceHelix/
│   │   └── presetManager/
│   ├── core/
│   │   ├── helix_math.py
│   │   ├── helix_segments.py
│   │   ├── surface_helix.py
│   │   ├── preview_builder.py
│   │   ├── sketch_builder.py
│   │   └── preset_model.py
│   ├── presets/
│   │   ├── builtin/
│   │   └── user/
│   ├── resources/
│   │   ├── icons/
│   │   ├── banner/
│   │   └── logo/
│   ├── lib/
│   └── version.py
│
├── docs/
│   ├── codex_plan.md
│   ├── ablaufplan.md
│   └── timeline.md
│
├── README.md
├── README-DE.md
├── LICENSE
└── .gitignore
```

## Architekturprinzipien

### `core/`

Enthält die fachliche und mathematische Logik:

- Berechnung der Helix
- Verarbeitung von Segmenten
- Interpolation von Steigung und Durchmesser
- Surface-Helix-Logik
- Preset-Datenmodell

### `commands/`

Enthält die Fusion-spezifischen UI- und Command-Teile:

- Dialoge
- Eingaben
- Buttons
- Fusion-Event-Handling
- Vorschau
- Erzeugen der finalen 3D-Skizze

### `resources/`

Enthält Logo, Icons, Banner und weitere UI-Grafiken.

### `docs/`

Enthält die Projektdokumentation.

## Dokumentationspflicht während der Entwicklung

Bei jeder relevanten Änderung:

1. **Version prüfen**
   - Muss sich die Versionsnummer ändern?
   - Falls ja: `version.py` aktualisieren.

2. **Timeline ergänzen**
   - Was wurde umgesetzt, geändert oder neu entschieden?

3. **Ablaufplan prüfen**
   - Wurde ein Schritt erledigt?
   - Muss ein neuer Schritt ergänzt werden?
   - Haben sich Prioritäten verschoben?

4. **README prüfen**
   - Nur anpassen, wenn sich die Projektübersicht spürbar verändert.
   - Die README-Dateien sollen bewusst kompakt bleiben.

## Umgang mit neuen Ideen und Änderungen

Wenn neue Funktionen, Anforderungen oder technische Änderungen entstehen, soll CodeX:

- sie in `docs/timeline.md` erfassen,
- sie in `docs/ablaufplan.md` einer Version oder dem Backlog zuordnen,
- bei Bedarf die README-Dateien anpassen.

Mögliche Status:

- geplant
- in Arbeit
- umgesetzt
- zurückgestellt
- verworfen

Nicht jede neue Idee muss sofort umgesetzt werden.

## Versionsstrategie

- `0.1.x` – Projektbasis / Basic Helix
- `0.2.x` – Variable Helix
- `0.3.x` – Surface Helix
- `0.4.x` – Presets
- `0.5.x` – Preview / Interaktion
- `0.6.x` – Output / Refactoring / Stabilisierung
- `0.7.x` – Dokumentation / Beispiele / UX
- `0.8.x` – Beta-Vorbereitung
- `0.9.x` – Setup EXE / Packaging mit Inno Setup
- `1.0.0` – erstes stabiles Release

Patch-Versionen dienen für Bugfixes, kleinere technische Korrekturen und Dokumentationsanpassungen.

## Qualitätsziele

CodeX soll auf Folgendes achten:

- klarer und lesbarer Python-Code
- nachvollziehbare Ordnerstruktur
- modulare Architektur
- saubere Benennung
- sparsame Abhängigkeiten
- dokumentierte Zwischenstände
- gut testbare Kernlogik

## Version 0.9 – Setup EXE

Für **Version 0.9** ist die Erstellung einer **Setup EXE mit Inno Setup** vorgesehen.

Dazu gehören:

- Installationsdateien vorbereiten
- benötigte Add-in-Dateien zusammenstellen
- Inno-Setup-Skript anlegen
- Installationspfade definieren
- Versionsnummer aus `version.py` übernehmen oder synchron halten
- Testinstallation dokumentieren
- Release-Prozess ergänzen

## Erwartetes Verhalten von CodeX

CodeX soll nicht nur Code erzeugen, sondern das Projekt konsistent halten:

- Code schreiben
- Dokumentation aktualisieren
- Ablaufplan fortschreiben
- Timeline ergänzen
- Versionsstand pflegen
- neue Ideen sinnvoll einordnen
- README-Dateien auf die Projektübersicht fokussieren

## Standard-Arbeitsweise

Bei jeder größeren Änderung:

1. Code anpassen
2. `version.py` prüfen / aktualisieren
3. `docs/timeline.md` ergänzen
4. `docs/ablaufplan.md` anpassen
5. ggf. README-Dateien nachziehen

## Zielbild

Am Ende soll das Projekt:

- technisch sauber aufgebaut sein,
- eine nachvollziehbare Entwicklungshistorie besitzen,
- klare nächste Schritte dokumentieren,
- für GitHub gut verständlich sein,
- leicht weiterentwickelt werden können.

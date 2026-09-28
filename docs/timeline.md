# Timeline – HelixPathPilot

Dieses Dokument dient als fortlaufende Chronik des Projekts.

Hier werden festgehalten:

- umgesetzte Funktionen
- wichtige Entscheidungen
- geänderte Anforderungen
- neue Ideen
- technische Richtungsänderungen
- Meilensteine

## Verwendung

Bei jeder relevanten Änderung soll ein neuer Eintrag ergänzt werden.

### Typen

- **Feature**
- **Change**
- **Fix**
- **Docs**
- **Decision**
- **Idea**
- **Refactor**
- **Release**

## Eintragsvorlage

```md
### YYYY-MM-DD – v0.0.0 – Typ

**Kurzbeschreibung:**  
...

**Details:**  
- ...
- ...
```

## Projektverlauf

### 2026-09-28 – v0.1.0 (development) – Feature

**Kurzbeschreibung:**

Ersten Umsetzungsschritt abgeschlossen: separate Add-in-Projektbasis angelegt.

**Details:**

- `HelixPathPilot/` mit Fusion-Einstiegspunkten, Manifest, Icon und zentraler Version angelegt.
- Start-/Stop-Struktur an die Vorlage angelehnt, Hilfsmodule unverändert übernommen.
- Leere Command-Registrierung sowie Ordner für Kernlogik, spätere Commands, Presets und Ressourcen vorbereitet.
- Vorlage unter `Fusion_addin/` unverändert erhalten; Demo-Commands nicht in das aktive Add-in übernommen.
- Git-Ausnahmen für notwendige Fusion-Manifeste und Python-Hilfsmodule ergänzt, die zuvor ignoriert wurden.
- README-Dateien, Ablaufplan und Entwicklungsanleitung aktualisiert.
- Noch keine Helix-Erzeugung; Laufzeittest in Fusion bleibt offen.

### 2026-09-28 – v0.1.0 – Decision

**Kurzbeschreibung:**  
Projektname auf **HelixPathPilot** festgelegt.

**Details:**  
- Der Name passt zur bestehenden Plugin-Familie.
- Das Projekt fokussiert sich nicht nur auf Federn, sondern auf allgemeine Helix-Pfade.

### 2026-09-28 – v0.1.0 – Decision

**Kurzbeschreibung:**  
Zwei Hauptmodi für die Geometrieerzeugung festgelegt.

**Details:**  
- Parametric Helix
- Surface Helix
- Surface Helix soll sich zunächst auf rotationssymmetrische Körper stützen.

### 2026-09-28 – v0.1.0 – Decision

**Kurzbeschreibung:**  
Dokumentationsstruktur definiert.

**Details:**  
- `version.py` dient als zentrale Versionsquelle.
- `docs/timeline.md` dokumentiert die Entwicklungshistorie.
- `docs/ablaufplan.md` dokumentiert den geplanten Umsetzungsweg.
- README-Dateien bleiben auf die Projektübersicht fokussiert.

### 2026-09-28 – v0.1.0 – Docs

**Kurzbeschreibung:**  
Erste GitHub-Dokumentation erstellt.

**Details:**  
- README in Deutsch erstellt
- README in Englisch erstellt
- zusätzliche Projektdokumente verlinkt

### 2026-09-28 – v0.1.0 – Idea

**Kurzbeschreibung:**  
Setup EXE mit Inno Setup für Version 0.9 vorgesehen.

**Details:**  
- Installer soll den Add-in-Installationsprozess vereinfachen.
- Packaging und Versionsabgleich sollen vorbereitet werden.

## Pflegehinweis

Neue Ideen sollen hier zeitnah als Entscheidung, Idee oder Änderung dokumentiert werden.

Wenn sich dadurch der geplante Umsetzungsweg verändert, muss zusätzlich `docs/ablaufplan.md` angepasst werden.

# HelixPathPilot
<p align="center">
  <img src="docs/images/banner.png" alt="HelixPathPilot Banner">
</p>

**HelixPathPilot** ist ein Add-in für Autodesk Fusion zur Erzeugung parametrischer und oberflächengeführter Helix-Kurven.

Das Projekt soll deutlich mehr Flexibilität als eine klassische Helix mit konstanter Steigung und konstantem Durchmesser bieten. Geplant sind variable Steigungen, variable Durchmesser, mehrere Helix-Abschnitte, oberflächengeführte Helices auf rotationssymmetrischen Körpern, Live-Vorschau und wiederverwendbare Presets.

## Geplante Hauptfunktionen

- Parametrische Helix-Erzeugung
- Auswahl einer Helix-Achse
- Einstellbare Länge, Steigung und Durchmesser
- Rechts- und linksdrehende Helices
- Einstellbarer Startwinkel
- Mehrere Helix-Abschnitte
- Variable Durchmesser
- Variable Steigungen
- Lineare und später weiche Übergänge
- Live-Vorschau im Fusion-Viewport
- Erzeugung als 3D-Skizze
- Surface Helix auf rotationssymmetrischen Körpern
- Einstellbarer Surface Offset
- Speichern, Laden, Import und Export von Presets
- Spätere Erweiterung für Sweep-/Federkörper

## Arbeitsmodi

### Parametric Helix

Die Helix wird vollständig über Parameter wie Durchmesser, Steigung, Länge, Drehrichtung und Startwinkel definiert.

Mehrere Abschnitte können unterschiedliche Start- und Endwerte für Durchmesser und Steigung besitzen.

### Surface Helix

Ein rotationssymmetrischer Körper bzw. dessen Oberfläche dient als Formgeber. Die Helix folgt der Kontur des Körpers und kann optional mit einem Abstand zur Oberfläche erzeugt werden.

Dieser Modus eignet sich besonders für komplexe Federformen, konische Wicklungen oder andere Helices mit kontinuierlich veränderlichem Radius.

## Presets

Helix-Konfigurationen sollen unter frei wählbaren Namen gespeichert werden können.

Geplant ist ein JSON-basiertes Austauschformat:

```text
*.helixpilot.json
```

Damit können Vorlagen archiviert, mit Git versioniert und zwischen Installationen ausgetauscht werden.

## Mögliche Anwendungen

- Druckfedern
- konische und progressive Federn
- Drahtformen
- Heizspiralen
- Spiralschläuche
- Kabelwicklungen
- Schnecken und Förderschnecken
- dekorative Helices
- parametrische Sweep-Pfade
- Spezialgeometrien für den 3D-Druck

## Projektstatus

Die Projektbasis (0.1.0, Entwicklungsstand) liegt unter `HelixPathPilot/`.
Sie enthält die Fusion-Einstiegspunkte, die Command-Registrierung und die Hilfsmodule der Vorlage.
Die Helix-Erzeugung ist noch nicht implementiert. Die bereitgestellte Vorlage bleibt unter `Fusion_addin/` erhalten.

Die [Entwicklungsanleitung](docs/development.md) beschreibt das Laden und die manuelle Prüfung in Fusion.

Die genaue Funktionalität und Benutzeroberfläche kann sich während der Entwicklung verändern.

## Weiterführende Projektdokumente

Zusätzliche Projektdokumente befinden sich im Ordner `docs/`:

- [CodeX Plan](docs/codex_plan.md) – Umsetzungsregeln und Arbeitsweise für die Weiterentwicklung
- [Ablaufplan](docs/ablaufplan.md) – geplanter Umsetzungsweg mit Versionslogik
- [Timeline](docs/timeline.md) – nachvollziehbare Entwicklungshistorie und Änderungsdokumentation

Die README konzentriert sich bewusst auf die Projektübersicht. Detaillierte Entwicklungs- und Fortschrittsinformationen werden in den oben verlinkten Dokumenten gepflegt.

## Autor

**Know-How-Schmiede**

- Website: https://www.know-how-schmiede.de
- YouTube: https://www.youtube.com/@knowhowschmiede
- GitHub: https://github.com/know-how-schmiede

## Hinweis

HelixPathPilot ist ein unabhängiges Projekt und steht in keiner offiziellen Verbindung zu Autodesk.

Autodesk und Fusion sind Marken bzw. eingetragene Marken ihrer jeweiligen Rechteinhaber.

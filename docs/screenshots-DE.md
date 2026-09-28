# HelixPathPilot – Screenshots

[Projektübersicht](../README-DE.md) · [English](screenshots.md)

Die Screenshots sind nach der dargestellten Version gegliedert, neueste zuerst.
Jede Version dokumentiert ihre damalige Oberfläche und Funktionen. Die Bilder
müssen daher nicht dem aktuellen Entwicklungsstand entsprechen.

## Versionen

- [v0.2.3](#v023) – tangentiale Übergänge, drei Abschnitte und Zebraanalyse
- [v0.2.2](#v022) – Anwendungsbeispiel und Abschnittsdialog
- [v0.1.2](#v012) – Achsausrichtung, Parameterdialog, Menü und Symbolleiste

## v0.2.3

### Sweep-Körper und Helix-Pfad

Eine Helix mit drei Abschnitten und verändertem Durchmesser- und Steigungsverlauf:
als Skizzenpfad und als anschließend in Fusion modellierter Sweep-Körper.
Die Körpererzeugung erfolgt in einem eigenen Modellierungsschritt.

| Sweep-Körper | Helix-Pfad mit Stützpunkten |
| --- | --- |
| <img src="images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-00.png" alt="Sweep-Körper aus drei Abschnitten mit verjüngten Enden" width="200"> | <img src="images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-01.png" alt="Zugehöriger Helix-Skizzenpfad mit Spline-Stützpunkten" width="200"> |

### Abschnittsdialog mit aktivierten G1-Übergängen

**Tangentiale Übergänge (G1)** ist aktiviert. Das Beispiel verwendet drei
Abschnitte mit jeweils 50 mm Länge, insgesamt 150 mm axialer Länge und einer
angezeigten Windungszahl von 35,541.

![Dialog von HelixPathPilot v0.2.3 mit drei Abschnitten und aktivierten tangentialen Übergängen](images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-02.png)

### Übergangsdetail mit Zebraanalyse

Der rote Pfeil markiert einen Abschnittsübergang am Sweep-Körper. Der Benutzer
bestätigt eine verbesserte Darstellung nach der G1-Angleichung. Die Zebraansicht
dokumentiert das Erscheinungsbild dieses Beispiels; sie belegt keine
G2-Krümmungsstetigkeit.

![Zebraanalyse des Helix-Sweeps mit rotem Pfeil am verbesserten Abschnittsübergang](images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-03.png)

## v0.2.2

### Anwendungsbeispiel

Ein federförmiger Körper mit unterschiedlichen Windungsabständen entlang einer
schrägen Achse, daneben Helix-Skizzengeometrie. HelixPathPilot erzeugt die
Skizzenpfade; die Körpererzeugung erfolgt als eigener Modellierungsschritt in Fusion.

![Federförmiger Körper mit unterschiedlichen Windungsabständen und Helix-Skizzengeometrie in Fusion](images/screenshots/v0-2-2/HelixPathPilot_v0-2-2_-00.png)

### Abschnittsdialog

Der vollständige Dialog mit **Abschnitt 1**, Start-/Enddurchmesser und -steigung,
Abschnittsverwaltung, Gesamtlänge und Windungszahl. **Achslänge übernehmen** ist
hier deaktiviert, da keine endliche Linie oder Kante ausgewählt ist.

![Abschnittsdialog von HelixPathPilot v0.2.2 mit einem Abschnitt, 50 mm Gesamtlänge und 10 Windungen](images/screenshots/v0-2-2/HelixPathPilot_v0-2-2_-01.png)

## v0.1.2

### Helices entlang einer schrägen Achse

Helix-Kurven mit ihren Spline-Stützpunkten um eine schräge Linie im Fusion-Viewport.

![Helix-Kurven mit Stützpunkten um eine schräge Achse](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-00.png)

### Parameterdialog

Optionale Achsauswahl, Achsrichtungsumkehr, Durchmesser, axiale Länge, Steigung,
Startwinkel und Drehrichtung. Ohne Achsauswahl wird die globale Z-Achse verwendet.

![Dialog HelixPathPilot v0.1.2 mit Achsauswahl und Helix-Parametern](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-01.png)

### Erstellen-Menü

Der versionierte Eintrag **HelixPathPilot v0.1.2** mit Helix-Icon unter
**Volumenkörper → Erstellen**.

![HelixPathPilot v0.1.2 im Erstellen-Menü unter Volumenkörper](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-02.png)

### Icon in der Symbolleiste

Das Helix-Icon ermöglicht den direkten Aufruf im Bereich Erstellen.

![Helix-Icon von HelixPathPilot in der Erstellen-Symbolleiste](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-03.png)

## Weitere Versionen ergänzen

Originalbilder unter `docs/images/screenshots/v<major>-<minor>-<patch>/` ablegen.
In diesem Dokument und [der englischen Galerie](screenshots.md) jeweils einen
Versionsabschnitt mit Inhaltsverzeichnis-Link, kurzen Bildunterschriften und
aussagekräftigen Alternativtexten ergänzen. Ältere Abschnitte und Bilder bleiben
erhalten. Die READMEs enthalten jeweils nur ein ausgewähltes Vorschaubild und
den Galerie-Link; bei Bedarf Vorschau und Versionsbeschriftung gemeinsam aktualisieren.

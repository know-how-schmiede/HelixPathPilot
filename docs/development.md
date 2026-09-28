# Entwicklung und Funktionstest

## Aktiver Stand – 0.1.1 (development)

Die Implementierung ersetzt die Vorlage unter `Fusion_addin/HelixPathPilot/`.
Nur diesen Ordner in Fusion laden. `HelixPathPilot/` im Repo-Hauptverzeichnis
ist der inaktive Altstand 0.1.0.

- `core/helix_math.py`: Fusion-unabhängige Berechnung (Längen in cm, Winkel in rad).
- `commands/createParametricHelix/entry.py`: Dialog, Validierung und Events.
- `commands/createParametricHelix/sketch_builder.py`: Ausgabe in die Hauptkomponente.
- `version.py`: aktive Versionsquelle; Manifest-Version synchron halten.
- `lib/fusionAddInUtils/`: Autodesk-Hilfsmodule mit ursprünglichen Lizenzhinweisen.

Der Command erzeugt eine räumliche Fitted Spline mit 32 Abschnitten pro Windung,
maximal 4097 Punkten / 128 Windungen. Auch angebrochene Windungen sind möglich.
Die Kurve nähert die mathematische Helix an. Es gibt noch keine Live-Vorschau,
freie Achsauswahl oder nachträgliche Änderung über gespeicherte Helix-Parameter.
Rechtsdrehend bedeutet positive Rotation um +Z bei zunehmendem Z; der Startwinkel
wird von +X in Richtung +Y gemessen. Die Länge bezeichnet die axiale Höhe.

## In Fusion prüfen

1. Eventuell laufenden Altstand stoppen. Im Dialog **Skripte und Zusatzmodule**
   das vorhandene Add-in aus `<Repo>/Fusion_addin/HelixPathPilot/` hinzufügen.
2. Ein Design-Dokument öffnen und das Add-in starten. Unter **Dienstprogramme /
   Zusatzmodule** im Design-Arbeitsbereich erscheint **Helix erstellen**.
3. Standardwerte bestätigen: Durchmesser 20 mm, Länge 50 mm, Steigung 5 mm.
   Erwartet: eine Skizze `HelixPathPilot – Helix` in der Hauptkomponente,
   zehn Windungen, Start (10, 0, 0) mm und Ende (10, 0, 50) mm.
4. Linksdrall, Startwinkel 90° und Länge 12 mm bei Steigung 5 mm prüfen.
   Erwartet: Start (0, 10, 0) mm, 2,4 Windungen mit umgekehrter Drehrichtung.
5. Null, negative Werte, ungültige Ausdrücke und mehr als 128 Windungen eingeben:
   OK bleibt gesperrt. Unterschiedliche Längeneinheiten ausprobieren.
6. Abbrechen oder zu einem anderen Command wechseln: keine neue Skizze.
7. Ausführen und Rückgängig prüfen; bei aktivierter Unterkomponente muss die
   Helix weiterhin um die globale Z-Achse in der Hauptkomponente liegen.
8. Add-in stoppen: Button verschwindet. Erneut starten: genau ein Button.
   Ohne Design-Dokument muss eine verständliche Meldung erscheinen.

Die Registrierung beschreibt die [Autodesk-Anleitung](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UsingSamplesFromGitHub_UM.htm).
Die Skizzenausgabe folgt dem [Autodesk-Beispiel für räumliche Splines](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchFittedSplines_add_Sample.htm).

## Automatisierte Prüfungen

Mit Python aus dem Repo-Hauptverzeichnis:

```text
python -B -m unittest discover -s tests -v
```

Alle neun Tests bestanden am 2026-09-28. Sie benötigen keine Fusion-Installation und prüfen die Mathematik,
Metadaten und Fehlerbereinigung des Skizzenadapters mit einem API-Testdouble.
Der manuelle Fusion-Laufzeittest und die macOS-Prüfung bleiben offen.

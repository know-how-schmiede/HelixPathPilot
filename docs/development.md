# Entwicklung und Funktionstest

## Aktiver Stand – 0.1.2 (development)

Die Implementierung ersetzt die Vorlage unter `Fusion_addin/HelixPathPilot/`.
Nur diesen Ordner in Fusion laden. `HelixPathPilot/` im Repo-Hauptverzeichnis
ist der inaktive Altstand 0.1.0.

- `core/helix_math.py`: Fusion-unabhängige Berechnung (Längen in cm, Winkel in rad).
- `core/axis.py`: Achskoordinatensystem und räumliche Transformation.
- `commands/createParametricHelix/axis_selection.py`: Fusion-Auswahl in Weltkoordinaten.
- `commands/createParametricHelix/entry.py`: Dialog, Validierung und Events.
- `commands/createParametricHelix/sketch_builder.py`: Ausgabe in die Hauptkomponente.
- `version.py`: aktive Versionsquelle; Manifest-Version synchron halten.
- `lib/fusionAddInUtils/`: Autodesk-Hilfsmodule mit ursprünglichen Lizenzhinweisen.

Der Command erzeugt eine räumliche Fitted Spline mit 32 Abschnitten pro Windung,
maximal 4097 Punkten / 128 Windungen. Auch angebrochene Windungen sind möglich.
Die Kurve nähert die mathematische Helix an. Es gibt noch keine Live-Vorschau
oder nachträgliche Änderung über gespeicherte Helix-Parameter.
Rechtsdrehend bedeutet positive Rotation um die gewählte Achsrichtung bei
zunehmender axialer Höhe. Die Länge bezeichnet diese Höhe.

## Achsauswahl

Optional eine Konstruktionsachse, gerade Modellkante oder Skizzenlinie auswählen.
Ohne Auswahl wird die globale Z-Achse verwendet. Linien starten an ihrem
geometrischen Anfangspunkt; Konstruktionsachsen an ihrem geometrischen Ursprung.
Der angeklickte Punkt legt den Startpunkt nicht fest. **Achsrichtung umkehren**
kehrt die Längsrichtung bei gleichem Ursprung um; die Drehrichtung bleibt eine
separate Einstellung relativ zur neuen Achsrichtung.

Der Startwinkel null liegt in Richtung der auf die Achsnormalebene projizierten
globalen X-Achse. Bei nahezu paralleler Achsrichtung (|X-Anteil| ≥ 0,99) dient
die globale Y-Achse als Referenz. Bei globaler +Z-Achse bleibt das bisherige
Verhalten erhalten. Skizzenlinien verwenden Weltgeometrie, Kanten und Achsen
ihre Geometrie im Auswahl-/Baugruppenkontext. Die Ausgabe liegt in der Hauptkomponente.

## Versions- und Iconpflege

Der Buttonname wird direkt aus `version.py` als `HelixPathPilot v<VERSION>` gebildet.
Die statische Manifest-Version ist ebenfalls auf **0.1.2** gesetzt. Nach künftigen
Versionsänderungen `python -B tools/sync_manifest.py` ausführen; ein Test prüft den Gleichstand.

Die Icons liegen unter `resources/icons/helix/` in 16, 32 und 64 Pixeln als SVG
und PNG. `python -B tools/build_icons.py` erzeugt sie und `AddInIcon.svg` erneut.
Die kleine Variante verwendet weniger Windungen für bessere Lesbarkeit.
Menüposition und Icondateien folgen der
[Autodesk-Dokumentation zur Benutzeroberfläche](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserInterface_UM.htm).

## In Fusion prüfen

1. Eventuell laufenden Altstand stoppen. Im Dialog **Skripte und Zusatzmodule**
   das vorhandene Add-in aus `<Repo>/Fusion_addin/HelixPathPilot/` hinzufügen.
2. Ein Design-Dokument öffnen und das Add-in starten. Unter **Volumenkörper →
   Erstellen** erscheint **HelixPathPilot v0.1.2** mit Helix-Icon, ebenso in der
   Symbolleiste. Im bisherigen Zusatzmodule-Panel darf kein alter Button verbleiben.
3. Standardwerte bestätigen: Durchmesser 20 mm, Länge 50 mm, Steigung 5 mm.
   Erwartet: eine Skizze `HelixPathPilot – Helix` in der Hauptkomponente,
   zehn Windungen, Start (10, 0, 0) mm und Ende (10, 0, 50) mm.
4. Linksdrall, Startwinkel 90° und Länge 12 mm bei Steigung 5 mm prüfen.
   Erwartet: Start (0, 10, 0) mm, 2,4 Windungen mit umgekehrter Drehrichtung.
5. Null, negative Werte, ungültige Ausdrücke und mehr als 128 Windungen eingeben:
   OK bleibt gesperrt. Unterschiedliche Längeneinheiten ausprobieren.
6. Abbrechen oder zu einem anderen Command wechseln: keine neue Skizze.
7. Ausführen und Rückgängig prüfen; bei aktivierter Unterkomponente muss die
   Helix ohne Achsauswahl weiterhin um die globale Z-Achse in der Hauptkomponente liegen.
8. Add-in stoppen: Button verschwindet. Erneut starten: genau ein Button.
   Ohne Design-Dokument muss eine verständliche Meldung erscheinen.
9. X-/Y-Konstruktionsachsen sowie eine schräge, versetzte Achse auswählen.
   Länge entlang der Achse und Radius senkrecht dazu prüfen; Richtung umkehren.
10. Eine gerade Modellkante und eine Skizzenlinie auswählen, auch aus einer
    verschobenen/gedrehten und verschachtelten Unterkomponente. Die Helix muss
    an der ausgewählten Weltgeometrie liegen. Kreis- und Splinekanten sind nicht auswählbar.
11. Auswahl löschen: globale Z-Achse wird wieder verwendet. Linksdrall und
    Startwinkel 90° an einer schrägen Achse prüfen.

Die Registrierung beschreibt die [Autodesk-Anleitung](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UsingSamplesFromGitHub_UM.htm).
Die Skizzenausgabe folgt dem [Autodesk-Beispiel für räumliche Splines](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchFittedSplines_add_Sample.htm).

## Automatisierte Prüfungen

Mit Python aus dem Repo-Hauptverzeichnis:

```text
python -B -m unittest discover -s tests -v
```

Alle 19 Tests bestanden am 2026-09-28. Sie benötigen keine Fusion-Installation und
prüfen Mathematik, Achstransformation, Metadaten, Icons und Fusion-Adapter mit Testdoubles.
Der Benutzer hat die grundsätzliche Funktion von 0.1.1 bestätigt. Die neue
Menüplatzierung und Achsauswahl von 0.1.2 sowie die macOS-Prüfung bleiben offen.

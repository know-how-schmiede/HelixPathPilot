# Entwicklung und Funktionstest

## Aktiver Stand – 0.3.0 (development)

### Dialogreiter und Surface-Grundlage

„Helix erstellen“ enthält die Moduswahl und die bisherigen Helix-Parameter.
„Einstellungen“ enthält die G1-Option (standardmäßig aktiv, nicht dauerhaft
gespeichert). „Info“ zeigt das mitgelieferte Logo, die zentrale Versionsnummer,
Projektinformationen und anklickbare Links entsprechend der Layoutvorlage.

Der neue Modus „Surface Helix – Flächenprüfung“ erlaubt die Auswahl einer
einzelnen Körperfläche. Analytische Zylinder- und Kegelmantelflächen werden
erkannt; andere Typen werden mit einem Hinweis abgelehnt. Eine erkannte Fläche
ist noch nicht auf vollständige Umfangsabdeckung oder Beschnitt geprüft.
Es gibt in diesem Modus noch keine Skizzenausgabe; Ausführen ist gesperrt.
Konturableitung, variable Steigung auf der Oberfläche und Offset folgen später.

Manuell in Fusion prüfen:

- Alle drei Reiter öffnen, Logo und Texte auf Abschneiden prüfen, Links öffnen.
- G1 in „Einstellungen“ deaktivieren, zurückwechseln und eine mehrteilige Helix erstellen.
- Zwischen den Modi wechseln: Parametereingaben bleiben erhalten; nur die jeweiligen Auswahlfelder sind sichtbar.
- Zylinder- und Kegelmantelfläche erkennen lassen; ebene Stirnfläche, Kugel und Freiformfläche ablehnen lassen. Auch Flächen in Unterkomponenten prüfen.
- Auswahl entfernen: Auswahlhinweis. In Surface-Prüfung bleibt Ausführen immer gesperrt, auch auf dem Info-Reiter.
- Zum parametrischen Modus zurückkehren und erstellen, abbrechen sowie rückgängig machen.

UI-Grundlage: [Autodesk Command Inputs](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CommandInputs_UM.htm).
Flächentypen: [Autodesk SurfaceTypes](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SurfaceTypes.htm).

Die Implementierung ersetzt die Vorlage unter `Fusion_addin/HelixPathPilot/`.
Nur diesen Ordner in Fusion laden. `HelixPathPilot/` im Repo-Hauptverzeichnis
ist der inaktive Altstand 0.1.0.

- `core/helix_math.py`: Fusion-unabhängige Berechnung (Längen in cm, Winkel in rad).
- `core/helix_segments.py`: validiertes Datenmodell für mehrere Abschnitte.
- `core/variable_helix.py`: Winkelintegration, Punktbudget und variable Kurvenberechnung.
- `commands/createParametricHelix/segment_editor.py`: Abschnittsverwaltung im Dialog.
- `core/axis.py`: Achskoordinatensystem und räumliche Transformation.
- `commands/createParametricHelix/axis_selection.py`: Fusion-Auswahl in Weltkoordinaten.
- `commands/createParametricHelix/entry.py`: Dialog, Validierung und Events.
- `commands/createParametricHelix/sketch_builder.py`: Ausgabe in die Hauptkomponente.
- `version.py`: aktive Versionsquelle; Manifest-Version synchron halten.
- `lib/fusionAddInUtils/`: Autodesk-Hilfsmodule mit ursprünglichen Lizenzhinweisen.

Der Command erzeugt eine 3D-Skizze mit einer räumlichen Fitted Spline pro Abschnitt.
Benachbarte Splines teilen ihren Endpunkt. Die Abtastung erfolgt mit mindestens
32 Intervallen pro Windung und zwei Intervallen pro Abschnitt. Grenzen:
32 Abschnitte, 128 Windungen insgesamt und 4097 eindeutige Stützpunkte.
Auch angebrochene Windungen sind möglich.
Die Kurve nähert die mathematische Helix an. Es gibt noch keine Live-Vorschau
oder nachträgliche Änderung über gespeicherte Helix-Parameter.
Rechtsdrehend bedeutet positive Rotation um die gewählte Achsrichtung bei
zunehmender axialer Höhe. Die Länge bezeichnet diese Höhe.

## Tangentiale Abschnittsübergänge

**Tangentiale Übergänge (G1)** ist standardmäßig eingeschaltet. Nach dem Erzeugen
aller Splines setzt Fusion zwischen jeweils zwei benachbarten Splines eine
Tangentialbedingung. Gemeinsame Endpunkte allein sichern nur den Anschluss,
nicht die gleiche Richtung. Steigungssprünge und unterschiedliche
Durchmessergradienten können deshalb ohne diese Option Knicke verursachen.

Die Bedingung gleicht die Tangenten an; Fusion darf dazu die Splineform anpassen.
Die angezeigten Längen und Windungszahlen beschreiben weiterhin das berechnete
Ausgangsmodell, keine erneute Vermessung der vom Solver angepassten Kurve.
G1 garantiert keine gleiche Krümmung (G2). Reflexionslinien oder Flächengrenzen
können daher weiterhin sichtbar sein; der Sweep hängt außerdem vom Profil ab.
G2 ist als weiterer Ausbau vorgemerkt.

Die Option lässt sich ausschalten, um die bisherige Ausgabe zu erhalten.
Bestehende Skizzen und Sweeps werden nicht nachträglich geändert: Helix mit
aktivierter Option neu erzeugen und als Sweep-Pfad verwenden. Scheitert eine
Tangentialbedingung, wird die gesamte neue Skizze entfernt und ein Fehler angezeigt.

Grundlage: [Fusion-API für Tangentialbedingungen](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_GeometricConstraints_addTangent.htm)
und [unterstützte Bedingungen für 3D-Skizzen](https://help.autodesk.com/cloudhelp/ENU/Fusion-Sketch/files/SKT-REF-3D-SKETCH-SUPPORTED-CONSTRAINT.htm).

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
Die statische Manifest-Version ist ebenfalls auf **0.3.0** gesetzt. Nach künftigen
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
   Erstellen** erscheint **HelixPathPilot v0.3.0** mit Helix-Icon, ebenso in der
   Symbolleiste. Im bisherigen Zusatzmodule-Panel darf kein alter Button verbleiben.
3. Standardwerte für Abschnitt 1 bestätigen: Start-/Enddurchmesser 20 mm,
   Abschnittslänge 50 mm, Start-/Endsteigung 5 mm.
   Erwartet: eine Skizze `HelixPathPilot – Helix` in der Hauptkomponente,
   zehn Windungen, Start (10, 0, 0) mm und Ende (10, 0, 50) mm.
4. Linksdrall, Startwinkel 90° und Abschnittslänge 12 mm bei beiden Steigungen 5 mm prüfen.
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
12. Abschnitt 1 auf Länge 50 mm, Durchmesser 20 → 30 mm und Steigung 5 → 10 mm
    setzen. Abschnitt hinzufügen; Länge 25 mm, Enddurchmesser 20 mm und Steigung
    10 → 5 mm setzen. Erwartet: Gesamtlänge 75 mm, etwa 10,397 Windungen,
    zwei verbundene Splines. Der Startdurchmesser von Abschnitt 2 ist gesperrt
    und folgt dem Enddurchmesser von Abschnitt 1.
13. Drei Abschnitte anlegen, den mittleren und danach den ersten entfernen:
    Abschnittsnummern bleiben stabil (es können Lücken entstehen), Durchmesserverknüpfungen werden angepasst. Mindestens ein
    Abschnitt bleibt erhalten. Erneut hinzufügen und Eingaben prüfen.
14. Einen ungültigen Ausdruck eingeben und einen Abschnitt hinzufügen:
    Fehlermeldung statt Verlust bestehender Werte. Eingabe korrigieren und wiederholen.
15. Bei mehreren Abschnitten Achsrichtung, Linksdrall und Startwinkel prüfen;
    Abbrechen hinterlässt keine Geometrie, Rückgängig entfernt die gesamte Skizze.
16. Eine endliche Linie oder gerade Körperkante auswählen und **Achslänge übernehmen**
    anklicken. Beispiel: Abschnitte mit 20 und 40 mm auf einer 90-mm-Linie ergeben
    30 und 60 mm. Gesamtlänge prüfen. Ohne Auswahl oder bei einer unendlichen
    Konstruktionsachse bleibt der Button deaktiviert. Die Übernahme ist einmalig;
    spätere Änderungen an Linie oder Abschnittslängen sind nicht verknüpft.
17. Zwei Abschnitte mit Steigungssprung (z. B. 5 auf 10 mm) und verändertem
    Durchmesserverlauf jeweils mit und ohne G1-Option erzeugen. Einen identischen
    Profil-Sweep vergleichen und die Tangentialbedingungen an den gemeinsamen
    Punkten prüfen. Auch drei Abschnitte auf einer schrägen Achse testen.
18. Gesamtlänge und Form nach der Tangentiallösung kontrollieren. Bei sehr starken
    Änderungen auf unerwünschte Auslenkungen oder Selbstüberschneidungen achten.
    Abschalten muss weiterhin die bisherige abschnittsweise Ausgabe ermöglichen.

Die Registrierung beschreibt die [Autodesk-Anleitung](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UsingSamplesFromGitHub_UM.htm).
Die Skizzenausgabe folgt dem [Autodesk-Beispiel für räumliche Splines](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchFittedSplines_add_Sample.htm).

## Automatisierte Prüfungen

Mit Python aus dem Repo-Hauptverzeichnis:

```text
python -B -m unittest discover -s tests -v
```

Alle 56 Tests bestanden am 2026-09-29. Sie benötigen keine Fusion-Installation und
prüfen Mathematik, Segmentmodell, Editor-Zustand, Achstransformation, Metadaten,
Icons und Fusion-Adapter mit Testdoubles. Für 0.3.0 prüfen sie zusätzlich die
Flächentyperkennung, verschachtelte Dialogeingaben, G1-Übergabe aus dem
Einstellungsreiter und die Ausführungssperre mit Rückkehr zum parametrischen Modus.
Der Benutzer hat die grundsätzliche Funktion von 0.1.1 sowie Menüposition, Icons
und beliebige Achsausrichtung von 0.1.2 sowie den Stand 0.2.0 bestätigt.
In 0.2.1 wurde ein Abbruch beim Aufbau des Abschnittsdialogs gemeldet und in
0.2.2 behoben: `CommandInput.name` ist schreibgeschützt. Die Testdoubles bilden
diese API-Einschränkung jetzt ab. Der Benutzer bestätigt die grundsätzliche Funktion von 0.2.2; die oben
aufgeführten Sonderfälle sind damit nicht einzeln als geprüft dokumentiert.
Die macOS-Prüfung bleibt offen.
Für 0.2.3 prüfen Testdoubles das Setzen aller Tangentialbedingungen und die
Fehlerbereinigung. Die eigentliche Fusion-Solver-Geometrie und der Sweep sind
damit nicht geprüft. Der Benutzer bestätigt einen verbesserten Übergang im
Sweep-Beispiel; die weiteren G1-Sonderfälle bleiben offen. Bilder: [Galerie v0.2.3](screenshots-DE.md#v023).

## Abschnittsverwaltung und variable Helices

Jeder Abschnitt besitzt eine aufklappbare Gruppe mit Länge, Start-/Enddurchmesser
und Start-/Endsteigung. Neue Abschnitte übernehmen Länge sowie Enddurchmesser
und Endsteigung des vorherigen Abschnitts als konstante Anfangswerte.
Jeder Abschnitt kann entfernt werden, solange mindestens einer verbleibt.
Abschnittstitel werden bei der Erstellung vergeben und behalten ihre Nummer.
Abschnitte werden in ihrer angezeigten Reihenfolge erzeugt; Umordnen und
Speichern als Preset sind noch nicht implementiert. Nach dem Schließen des
Dialogs werden die Eingaben nicht für einen weiteren Aufruf gespeichert.

`HelixSegment` enthält positive, endliche Werte für `length`, `diameter_start`,
`diameter_end`, `pitch_start` und `pitch_end`. Alle Längen verwenden dieselbe
Einheit (in Fusion cm). `values_at(fraction)` liefert Durchmesser und Steigung
an einer relativen axialen Position von 0 bis 1, linear zwischen den Endwerten.
Die Interpolation bezieht sich auf die axiale Länge, nicht auf den Drehwinkel.

`SegmentedHelix` besitzt eine unveränderliche Abschnittsliste, einen gemeinsamen
Startwinkel (rad) und eine gemeinsame Drehrichtung. Die Gesamtlänge ist die
Summe der Abschnittslängen. Benachbarte Durchmesser müssen übereinstimmen
(Toleranz: relativ 1e-9 oder absolut 1e-9 in der verwendeten Längeneinheit).
Steigungssprünge und wechselnde Durchmessergradienten können im Ausgangsmodell
einen Knick verursachen. Die optionale G1-Bedingung gleicht anschließend die
Tangenten der Fusion-Splines an; sie ändert nicht die zugrunde liegende lineare Interpolation.

`HelixParameters.as_segmented()` bildet die bisherige Helix auf einen konstanten
Abschnitt ab. Die Basis-Validierung verwendet bereits dieses Modell; die
Punktberechnung der einfachen Helix und ihr Limit bleiben erhalten.
`variable_helix.py` integriert die Windungszahl als Integral von `1 / Steigung(z)`
über die axiale Länge. Für linear veränderliche Steigung wird die logarithmische
Lösung verwendet; bei konstanter Steigung gilt weiterhin Länge / Steigung.
Die inverse Funktion liefert axiale Positionen für gleichmäßige Winkelschritte.
Der Durchmesser wird an diesen axialen Positionen linear interpoliert.
**Achslänge übernehmen** setzt die axiale Gesamtlänge einmalig auf die Länge
der ausgewählten endlichen Skizzenlinie oder geraden Körperkante. Die bisherigen
Längenverhältnisse der Abschnitte bleiben erhalten; Durchmesser und Steigungen
bleiben unverändert. Ungültige Werte oder überschrittene Windungs-/Punktlimits
werden vor der Änderung abgefangen. Konstruktionsachsen sind unendlich und
liefern keine übernehmbare Länge. Die Richtungsumkehr ändert die Länge nicht;
bei umgekehrter Richtung verläuft die Helix vom gleichen Ursprung in Gegenrichtung.

# Entwicklung und Funktionstest

## Aktiver Stand – 0.4.3 (development)

### Abschnitte gezielt entfernen (Korrektur in 0.4.3)

**Aktuelle Bestätigung:** Der Benutzer bestätigt das Entfernen in Fusion.
Das Auswahlfeld war zunächst übersehen worden; die letzte Meldung, dass nur der
letzte Abschnitt entfernt werde, ist damit als Bedienmissverständnis geklärt.
Die unten beschriebenen Nachkorrekturen dokumentieren den Entwicklungsverlauf.

Die einzelnen Entfernen-Buttons innerhalb der Abschnittsgruppen wurden durch
zwei feste Eingaben unter der Abschnittsliste ersetzt:

1. In „Abschnitt entfernen“ den gewünschten Abschnitt auswählen.
2. „Ausgewählten Abschnitt entfernen“ drücken.

Die Auswahl allein verändert keine Geometrie. Die Liste verwendet die sichtbaren
Abschnittsnamen, auch wenn deren Nummern nach Entfernen oder Vorlagenladen Lücken
haben. Der letzte verbleibende Abschnitt ist geschützt. Nach dem Entfernen werden
Vorschau und Abschnittszahl aktualisiert; die dynamischen Gruppen enthalten keine
Entfernen-Buttons mehr. Entfernte Felder bleiben bis zum Dialogende ausgeblendet.

Benutzer meldete: Nur der erste Abschnitt ließ sich entfernen, andere bei mindestens
zwei verbleibenden Abschnitten ohne Fehlermeldung nicht. Die native Ursache ist
weiterhin nicht nachgewiesen. Der neue feste Button vermeidet die dynamischen
Ereignisauslöser innerhalb der Abschnittsgruppen.

Manuell erneut prüfen: drei Abschnitte anlegen, in der Auswahl Abschnitt 2 wählen
und entfernen, anschließend Abschnitt 3 entfernen. Danach müssen nur Abschnitt 1
und seine Vorschau verbleiben. Ebenso nach Laden einer mehrteiligen Vorlage prüfen.
113 automatisierte Tests bestanden; Entfernen grundsätzlich vom Benutzer in Fusion bestätigt. Die einzelnen Prüffolgen sind nicht separat protokolliert.

### Kompakter Dialog und Abschnittsfarben (0.4.3)

Der Dialog wird mit 520 × 560 Pixeln geöffnet, auch wenn Fusion zuvor eine
übergroße Höhe gespeichert hatte. Die Mindestgröße beträgt 380 × 300 Pixel;
weitere Eingaben sind über den scrollbaren Inhaltsbereich erreichbar. Nach
Vorlagenladen, Moduswechsel und Hinzufügen von Abschnitten wird die
kompakte Größe erneut gesetzt. Der Reiter „Vorlagen“ entlastet den Erstellungsdialog;
nach dem Laden wird „Helix erstellen“ aktiviert.

Jeder Abschnitt erhält eine eigene Vorschaufarbe, in Listenreihenfolge. Die
Farbtextzeile im Dialog wurde entfernt, da Fusion das HTML als Klartext anzeigte.
Nach Entfernen eines Abschnitts folgen die Farben der neuen Reihenfolge.
32 unterschiedliche Farben stehen bereit; bei vielen Abschnitten können sich
Farbtöne ähneln. Surface Helix verwendet als einzelner Abschnitt die erste Farbe.
Farben gelten nur für die temporäre Grafik, nicht für die fertige Skizze oder Presets.

Manuelle Fusion-Prüfung (offen):

- Dialog auf dem bisher betroffenen Bildschirm öffnen: OK/Abbrechen sichtbar, Inhalt scrollbar.
- Zwei und anschließend viele Abschnitte laden/erstellen, Reiter und Modi wechseln; OK erreichbar halten, auch bei erhöhter Windows-Anzeigeskalierung.
- Ersten, mittleren und letzten Abschnitt entfernen; Vorschau und Ausgabe mit der verbleibenden Abschnittsliste vergleichen. Entfernen/Hinzufügen mehrfach wiederholen.
- Vorschau aus/ein, Abbrechen und finale Ausgabe prüfen; keine zurückbleibenden farbigen Grafiken.

API-Grundlagen: [Dialoggröße](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Command_setDialogSize.htm)
und [Custom-Graphics-Farben](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CustomGraphics_UM.htm).

Korrektur innerhalb 0.4.3: Benutzer bestätigt die farbige Vorschau, meldet aber
Absturz bzw. keine Reaktion beim Entfernen. Entfernte Abschnittsgruppen werden
jetzt ausgeblendet und aus dem Modell genommen, statt den auslösenden Button
während `inputChanged` zu zerstören. Fusion räumt diese Eingaben beim Schließen
des Dialogs auf. Beim Entfernen wird keine Größenänderung mehr ausgelöst;
Validierung während laufender Editoränderungen wird abgefangen. Die native
Absturzursache ist außerhalb von Fusion nicht bestätigt; erneute Fusion-Prüfung offen.

### Eigene Vorlagen (0.4.2)

Der Benutzer bestätigt die Funktion der eigenen Vorlagen. Die gemeldete übergroße
Dialoghöhe wird in 0.4.3 adressiert; einzelne Sonderfälle bleiben offen.

Unter „Vorlagen“ einen Namen eingeben und „Als eigene Vorlage speichern“ drücken.
Gespeichert werden die aktuellen Werte des aktiven Modus. Die neue Vorlage wird
in der Liste ausgewählt und mit „Eigene“ gekennzeichnet. Speichern verändert keine
Geometrie. Details und Speicherorte: [Preset-Bedienung](presets.md).

Manuelle Fusion-Prüfung (offen):

- Variable Helix mit zwei Abschnitten speichern, Dialog schließen, wieder öffnen und laden; Werte, Achsumkehr, Winkel, Drehrichtung und G1 vergleichen.
- Surface-Werte ohne ausgewählte Fläche speichern und später mit Fläche laden.
- Gleichen Namen erneut speichern: Hinweis statt Überschreiben; leeren Namen und ungültige Eingaben ebenfalls prüfen.
- Eigene Vorlage löschen: Nein erhält die Datei, Ja entfernt sie aus der Liste. Aktuelle Helix-Werte bleiben erhalten.
- Mitgelieferte Vorlage wählen: Löschen deaktiviert. Abbrechen des Helix-Dialogs macht gespeicherte/gelöschte Dateien nicht rückgängig.

Die Löschbestätigung verwendet Fusions [MessageBox-API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MessageBoxButtonTypes.htm).

### Vorlagen laden (0.4.1)

Der Benutzer bestätigt die sichtbare Vorlagenauswahl und das Laden in Fusion.
Zwei [Screenshots von 0.4.1](screenshots-DE.md#v041) zeigen die Vorlagenliste
und eine geladene variable Vorlage mit bearbeiteten Abschnitten und Vorschau.
Die Rückfrage zu unveränderten Werten wurde durch Betätigen von „Vorlage laden“
geklärt; die Auswahl allein übernimmt bewusst keine Parameter. Die einzelnen
Sonderfälle der folgenden Checkliste sind damit nicht vollständig bestätigt.

Die Vorlagen stehen seit 0.4.3 im eigenen Reiter „Vorlagen“ (in 0.4.1 noch als Gruppe unter „Helix erstellen“).
Eine der drei Vorlagen auswählen und „Vorlage laden“ drücken. Auswahl allein
ändert keine Parameter. Laden ersetzt Parameter und Modus; bestehende Achs-
und Flächenauswahlen sowie die Live-Vorschau-Einstellung bleiben erhalten.
Die Surface-Vorlage benötigt weiterhin eine gültige Mantelfläche. Ungültige
Vorlagendateien werden gemeldet und übersprungen; der übrige Dialog bleibt nutzbar.

Manuell in Fusion prüfen (offen):

- Basisvorlage laden: ein Abschnitt, 50 mm Länge, 20 mm Durchmesser, 5 mm Steigung.
- Variable Vorlage laden: zwei Abschnitte, 75 mm Gesamtlänge; Vorschau und Ausgabe prüfen.
- Surface-Vorlage laden: automatischer Moduswechsel, Steigung 5 → 10 mm; ohne Fläche bleibt OK gesperrt.
- Zwischen Vorlagen mehrfach wechseln; danach Abschnitte hinzufügen/entfernen.
- Gewählte Achse/Fläche und ausgeschaltete Vorschau beim Laden beibehalten.

API-Grundlage: [Autodesk ListItem.isSelected](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_ListItem.htm).

### Preset-Grundlage (0.4.0)

Datenmodell, JSON-Validierung und drei Built-in-Vorlagen sind implementiert.
Details: [Preset-Format](presets.md). Der Fusion-Dialog bleibt in dieser
Ausbaustufe unverändert; Speichern/Laden und Dateiverwaltung folgen.
Sieben neue Tests prüfen Roundtrips beider Modi, Schemafehler, Limits,
ungültige Daten und die mitgelieferten Vorlagen.

Der Benutzer meldet für 0.3.6 keine aufgefallenen Fehler. Dies bestätigt den
bisherigen Einsatz; der vollständige Sonderfallkatalog ist nicht einzeln protokolliert.

### Reproduzierbare Surface-Testmodelle

Der [Testmodellkatalog mit Prüfprotokoll](surface-testmodelle.md) definiert
elf Modellvarianten, vierzehn Geometrieprüfungen und sieben Prüfungen für
Ablehnung und Dialogverhalten. Er enthält Bauanleitungen, konkrete Eingaben
und unabhängig berechenbare Sollwerte. Der vollständige manuelle Durchlauf
in Fusion steht noch aus; die bisherige Funktionsbestätigung bleibt davon getrennt.

### Variable Surface-Steigung (0.3.5)

Der Benutzer bestätigt die Funktion in Fusion. Zwei [Screenshots von 0.3.5](screenshots-DE.md#v035)
zeigen zunehmende Steigung am Zylinder und abnehmende Steigung am Kegel,
jeweils mit positivem Offset. Die folgenden Sonderfälle sind damit nicht einzeln bestätigt.

Start- und Endsteigung sind unabhängig einstellbar (Standard jeweils 5 mm).
Gleiche Werte ergeben konstante Steigung. Der Verlauf ist linear entlang der
axialen Länge, nicht entlang des Drehwinkels. Beim Wechsel des Startrands
bleiben Start-/Endwerte der jeweiligen Laufrichtung zugeordnet.
Offset verändert diesen Verlauf und die Windungszahl nicht.
Vorschau und Ausgabe verwenden dasselbe Modell; beide Steigungen müssen
positiv und endlich sein. Die bisherigen Windungs-/Punktlimits bleiben aktiv.

Manuell in Fusion prüfen (noch offen):

- Zylinder R=10 mm, Länge=50 mm, Steigung 5 → 10 mm: etwa 6,931 Windungen;
  bei 5 → 5 mm weiterhin 10 Windungen.
- 10 → 5 mm, Randwechsel, Linksdrall und Startwinkel 90° prüfen.
- Kegel mit zwei Kreisrändern: zunehmende/abnehmende Steigung mit positivem
  und negativem Offset kombinieren; Vorschau mit finaler Skizze vergleichen.
- Endsteigung 0, negativ oder ungültiger Ausdruck: Ausführen gesperrt,
  alte Vorschau entfernt; gültigen Wert wiederherstellen.

### Surface Offset (0.3.4)

Der Benutzer bestätigt die Offset-Funktion, die Vorschau und ausdrücklich
den negativen Abstand zur Mantelfläche. Drei [Screenshots von 0.3.4](screenshots-DE.md#v034)
zeigen die Beispiele. Die weiteren Prüffälle unten sind damit nicht einzeln bestätigt.

„Surface Offset“ im Surface-Modus ist standardmäßig 0. Positive Abstände
verschieben die Helix entlang der Mantelnormalen von der Rotationsachse weg,
negative zur Achse hin. Dies gilt auch bei Innenflächen; es ist keine
automatische Orientierung nach der Außennormalen eines Volumenkörpers.

Bei Kegelsteigung k = (Endradius − Startradius) / Länge und Offset d gilt
Δr = d / sqrt(1+k²), Δz = −d·k / sqrt(1+k²). Beim Zylinder ist k = 0.
Die Endpunkte werden zusammen mit der Mantelfläche versetzt und können daher
beim Kegel über deren ursprüngliche axiale Grenzen hinausragen. Axiale Länge,
Steigung und Windungszahl ändern sich nicht. Offset wird vor dem Randwechsel
angewendet. Nichtpositive resultierende Radien und ungültige Werte sperren
die Ausgabe. Die Spline bleibt eine Näherung der berechneten Punkte.

In Fusion prüfen: Zylinder Radius 10 mm mit +2 mm ergibt Helixradius 12 mm,
mit −2 mm 8 mm; −10 mm muss abgewiesen werden. Kegelstumpf mit beiden
Vorzeichen, schräger Achse und beiden Starträndern prüfen. Der senkrechte
Abstand soll dem Offset entsprechen, nicht die rein radiale Differenz.
Vorschau aus/ein, Abbrechen und Rückgängig kontrollieren. Offset 0 entspricht
der bisherigen Ausgabe.

### Surface Helix erzeugen (0.3.3)

Die grundsätzliche Funktion wurde vom Benutzer in Fusion bestätigt. Fünf
[Screenshots von 0.3.3](screenshots-DE.md#v033) dokumentieren Zylinder-/Kegelvorschau
und anschließende Modellierungsbeispiele. Die unten genannten Sonderfälle
sind damit nicht einzeln als geprüft dokumentiert.

Im Modus „Surface Helix“ eine vollständige Zylinder- oder Kegelmantelfläche
auswählen. Die Helix läuft über die gesamte erkannte axiale Länge mit einstellbarer
Start-/Endsteigung (Standard jeweils 5 mm pro Windung). Startwinkel und Drehrichtung
beziehen sich auf die jeweilige Laufrichtung. „Am anderen Rand starten“ setzt
den Ursprung zum gegenüberliegenden Rand und kehrt Achse sowie Radiusverlauf um.
Die automatische Achse und Radien sind unabhängig von den verdeckten
parametrischen Eingaben. Die Grafikvorschau bleibt leichtgewichtig.

Ausführen erzeugt `HelixPathPilot – Surface Helix` als einzelne 3D-Spline in
der Hauptkomponente. Die berechneten Stützpunkte liegen auf der analytischen
Mantelfläche; die Spline dazwischen ist eine Näherung. Es entsteht keine
assoziative Bindung an den Körper. G1 hat bei dieser einzelnen Spline keine
Wirkung. Surface Offset ist seit 0.3.4 enthalten; variable Surface-Steigung ist seit 0.3.5 enthalten.

In Fusion prüfen: Zylinder Radius 10 mm / Länge 50 mm / Steigung 5 mm ergibt
zehn Windungen. Kegelstumpf mit Radien 10 und 20 mm entsprechend prüfen;
Startrand wechseln, Linksdrall und Startwinkel 90° testen. Beide Formen auch
schräg und in Unterkomponenten prüfen. Oberfläche gegen die fertige Spline
kontrollieren. Ungültige Fläche, Steigung null oder mehr als 128 Windungen
müssen Ausführen sperren. Vorschau aus/ein, Moduswechsel, Abbrechen, Erstellen
und Rückgängig prüfen; genau eine Skizze darf entstehen.

### Live-Vorschau und Abschnittsmarkierungen (0.3.1)

Benutzer bestätigt nach der Performance-Korrektur die funktionierende Vorschau,
passende Geschwindigkeit und korrekte Durchmesserverknüpfung in den Abschnitten.
Die Mantelflächenerkennung wurde ebenfalls bestätigt. Die unten aufgeführten
Sonderfälle sind damit nicht einzeln als geprüft dokumentiert.

Die Live-Vorschau ist standardmäßig aktiv und im Reiter „Einstellungen“
abschaltbar. Nach der Performance-Korrektur ohne Versionswechsel zeichnet
`executePreview` ausschließlich temporäre Custom Graphics: seit 0.4.3 eine farbige Liniengrafik je Abschnitt
und Grenzpunkte. Dabei werden weder Skizzen erstellt noch G1-Bedingungen gelöst.
Die Vorschau zeigt den berechneten Pfad; die finale G1-Anpassung kann davon
abweichen und wird im Dialog entsprechend angekündigt. Unveränderte Grafik
wird wiederverwendet, sofern Fusion sie nicht bereits zurückgerollt hat.
Ungültige Eingaben, Abschalten, Moduswechsel und Dialogende entfernen die Grafik.
`isValidResult` bleibt false: Erst Ausführen erzeugt die echte Skizze mit G1.
Surface Helix verwendet seit 0.3.3 ebenfalls diese Vorschau und Skizzenausgabe.

Die Skizze behält alle Spline-Stützpunkte für unveränderte Abtastgenauigkeit.
`arePointsShown = False` blendet die verbundenen Punkte aus. Separate,
unverbundene Skizzenpunkte markieren die tatsächlichen Abschnittsgrenzen
nach der G1-Lösung: n+1 Marker für n Abschnitte. Diese Marker sind eine
Momentaufnahme und folgen einer späteren manuellen Splineänderung nicht.
Beim Selektieren/Bearbeiten kann Fusion zusätzliche Splinehilfen anzeigen.

Die Startdurchmesser aller Folgeabschnitte werden auch vor dem Lesen der
Parameter synchronisiert. Ein Tooltip nennt den direkten Vorgänger.

Manuell prüfen: vier Abschnitte mit unterschiedlichen Enddurchmessern ändern,
mittleren/ersten Abschnitt entfernen und Folgewerte kontrollieren. Währenddessen
müssen Vorschau, Achsrichtung, Startwinkel und G1 aktualisiert werden. Vorschau
abschalten, ungültige Werte eingeben und zwischen Surface/Parametrisch wechseln;
keine veraltete Helix darf sichtbar bleiben. Abbrechen hinterlässt keine Skizze,
Bestätigen genau eine, Rückgängig entfernt sie samt Markern. Anfang, alle
Abschnittsgrenzen und Ende auf sichtbare Marker prüfen, auch auf schräger Achse.

API-Grundlagen: [Fusion Custom Graphics](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CustomGraphics_UM.htm),
[Skizzenpunktanzeige](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_arePointsShown.htm).

### Dialogreiter und Surface-Grundlage

„Helix erstellen“ enthält die Moduswahl und die bisherigen Helix-Parameter.
„Einstellungen“ enthält Live-Vorschau und G1-Option (standardmäßig aktiv, nicht dauerhaft
gespeichert). „Info“ zeigt das mitgelieferte Logo, die zentrale Versionsnummer,
Projektinformationen und anklickbare Links entsprechend der Layoutvorlage.

Der Modus „Surface Helix“ erlaubt die Auswahl einer einzelnen
Körperfläche. Analytische Zylinder- und Kegelmäntel mit zwei vollständigen,
koaxialen Kreisrändern werden geprüft. Die Randmittelpunkte werden auf die
Flächenachse projiziert und entlang dieser Achse sortiert: ihre Differenz ergibt
die axiale Länge, die Kreisradien ergeben Anfang und Ende des Radiusverlaufs.
Die Vorschrift `radius_at(distance)` interpoliert innerhalb dieses Bereichs.
Damit sind auch verschobene und schräge Achsen abgedeckt, ohne achsparallele
Bounding Box oder Annahmen zur UV-Parametrisierung.

Der Flächeninhalt muss zum vollen 360°-Mantel passen (relative Toleranz 1e-6,
absolute Flächentoleranz 1e-8 cm²). Zusätzliche Konturen, Teilflächen, Spitzen,
geteilte Kreisränder und andere Flächentypen werden abgelehnt. Die Maßanzeige
verwendet die Dokumenteinheit. Der Start liegt am Rand mit der kleineren
Koordinate entlang der Flächenachse, nicht zwingend am räumlich unteren Rand.
Bei gültiger Fläche und Steigung sind Vorschau und Skizzenausgabe verfügbar.
Variable Steigung auf der Oberfläche ist seit 0.3.5 verfügbar; Offset ist seit 0.3.4 verfügbar.

Neue manuelle Prüffälle: Zylinder mit Radius 10 mm und Länge 50 mm ergibt
50 mm / 10 mm / 10 mm; Kegelstumpf mit Radien 10 und 20 mm und Höhe 50 mm
ergibt 50 mm und die beiden Radien in Achsreihenfolge. Beide Modelle auch
schräg und in verschobenen Unterkomponenten prüfen. Halbmantel, Querbohrung,
schräger Anschnitt und Kegelspitze müssen einen Ablehnungshinweis ergeben.

Manuell in Fusion prüfen:

- Alle drei Reiter öffnen, Logo und Texte auf Abschneiden prüfen, Links öffnen.
- G1 in „Einstellungen“ deaktivieren, zurückwechseln und eine mehrteilige Helix erstellen.
- Zwischen den Modi wechseln: Parametereingaben bleiben erhalten; nur die jeweiligen Auswahlfelder sind sichtbar.
- Zylinder- und Kegelmantelfläche erkennen lassen; ebene Stirnfläche, Kugel und Freiformfläche ablehnen lassen. Auch Flächen in Unterkomponenten prüfen.
- Auswahl entfernen: Auswahlhinweis und gesperrtes Ausführen, auch auf dem Info-Reiter. Mit gültiger Fläche und Steigung muss Ausführen möglich sein.
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
Die Kurve nähert die mathematische Helix an. Eine Live-Vorschau ist verfügbar;
nachträgliche Änderungen über gespeicherte Helix-Parameter sind noch nicht möglich.
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
Die statische Manifest-Version ist ebenfalls auf **0.4.3** gesetzt. Nach künftigen
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
   Erstellen** erscheint **HelixPathPilot v0.4.3** mit Helix-Icon, ebenso in der
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

Alle 113 Tests bestanden am 2026-09-29. Sie benötigen keine Fusion-Installation und
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

## Zeilenenden im Repository

Die Datei `.gitattributes` legt LF für Textdateien fest, unabhängig von der
lokalen Einstellung `core.autocrlf`. Binärdateien werden nicht konvertiert;
Windows-Batchdateien verwenden CRLF. `.editorconfig` übernimmt dieselben
Zeilenenden für unterstützende Editoren. Beim Commit beide Regeldateien mit aufnehmen.

### Nachkorrektur Abschnitt entfernen (weiterhin 0.4.3)

Der Benutzer meldet, dass auch nach dem ersten Korrekturversuch Abschnitt und
Vorschau sichtbar bleiben. Entfernen verwendet jetzt eine beim Aufbau gespeicherte
Button-Zuordnung und ändert die aktive Abschnittsliste vor allen Grafikaufrufen.
Alle Eingabefelder des entfernten Abschnitts werden zusätzlich einzeln ausgeblendet.
Vorschau und Abschnittszahl werden unmittelbar aktualisiert. Fehler werden beim
Entfernen mit Meldungsfenster und Traceback protokolliert. Regressionstests prüfen,
dass ein Fehler beim Grafikabbau die Modelländerung nicht verhindert. Die konkrete
Ursache im Fusion-Lauf ist noch nicht bestätigt; erneuter Test mit drei Abschnitten offen.

### Auswahlziel beim Entfernen festhalten (0.4.3)

Nach der Rückmeldung, dass nur der letzte Abschnitt entfernt werde, wird das Ziel
jetzt beim Auswahlereignis anhand des Abschnittsnamens als stabile Kennung gespeichert.
Der Entfernen-Button liest keinen späteren Listenindex mehr. Beim Neuaufbau wird die
Auswahl erst nach Einfügen aller Einträge explizit gesetzt. Eine Textzeile zeigt das
wirksame Ziel vor dem Klick. Die genaue native Ursache bleibt unbestätigt. Regressionen
mit veraltetem Index und später veränderter nativer Auswahl bestehen; Fusion-Nachtest offen.

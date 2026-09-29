# Ablaufplan – HelixPathPilot

Dieses Dokument beschreibt den geplanten Umsetzungsweg des Projekts inklusive Versionslogik.

Der Ablaufplan ist bewusst **lebendig** und soll während der Entwicklung fortgeschrieben werden.

## Statuslogik

- [ ] geplant
- [~] in Arbeit
- [x] erledigt
- [-] zurückgestellt
- [!] geändert / neu bewertet

## Versionsstrategie

- **0.1.x** – Projektbasis
- **0.2.x** – Variable Helix
- **0.3.x** – Surface Helix
- **0.4.x** – Presets
- **0.5.x** – Preview / Interaktion
- **0.6.x** – Output / Refactoring / Stabilisierung
- **0.7.x** – Dokumentation / Beispiele / UX
- **0.8.x** – Beta-Vorbereitung
- **0.9.x** – Setup EXE / Packaging mit Inno Setup
- **1.0.0** – erstes stabiles Release

# Version 0.1.x – Projektbasis

## Ziel

Technische Grundlage schaffen und eine erste einfache Helix erzeugen.

## Schritte

- [x] Projektstruktur anlegen
- [x] Vorlage aus `Fusion_addin/` integrieren
- [x] `version.py` anlegen
- [x] `docs/timeline.md` anlegen
- [x] `docs/ablaufplan.md` anlegen
- [x] `docs/codex_plan.md` anlegen
- [x] README-Dateien ergänzen
- [x] Basis-Command für Helix-Erzeugung anlegen
- [x] Achsauswahl integrieren
- [x] Durchmesser, Länge und Steigung integrieren
- [x] Drehrichtung integrieren
- [x] Startwinkel integrieren
- [x] erste 3D-Skizzenerzeugung umsetzen
- [x] erste lauffähige Basisversion testen (0.1.1 grundsätzlich vom Benutzer bestätigt)
- [x] Achsauswahl und neue Menüplatzierung von 0.1.2 in Fusion prüfen (vom Benutzer bestätigt, inklusive Icons)

## Zielversion

**0.1.x** – Projektbasis wird in Entwicklungsständen vervollständigt.

Stand 2026-09-28, **0.1.2 (development)**: Aktives Add-in unter
`Fusion_addin/HelixPathPilot/`. Basis-Command mit Durchmesser, Länge, Steigung,
Drehrichtung und Startwinkel implementiert; Ausgabe als angenäherte 3D-Spline
um eine Konstruktionsachse, gerade Kante oder Skizzenlinie in der Hauptkomponente.
Ohne Auswahl bleibt die globale Z-Achse aktiv; die Achsrichtung ist umkehrbar.
Button mit Versionsnummer und eigenen Icons unter Volumenkörper → Erstellen.
Die eingegebenen Werte werden
nicht als nachträglich editierbare Helix-Parameter gespeichert.
Die Projektbasis einschließlich Achsauswahl, Menüposition und Icons wurde vom Benutzer bestätigt.
Ladeanleitung und manuelle Prüfschritte: [Entwicklung](development.md).

# Version 0.2.x – Variable Helix

## Ziel

Mehrere Abschnitte mit unterschiedlichen Parametern ermöglichen.

## Schritte

- [x] Datenmodell für Helix-Segmente erstellen
- [x] Segmentliste / Abschnittsverwaltung implementieren
- [x] variable Durchmesser unterstützen
- [x] variable Steigungen unterstützen
- [x] lineare Übergänge umsetzen
- [x] Berechnungslogik überarbeiten
- [x] segmentierte Helix als 3D-Skizze erzeugen
- [x] Optionale tangentiale Abschnittsübergänge (G1) ergänzen (0.2.3)
- [x] Testfälle ergänzen (50 automatisierte Tests insgesamt)
- [~] Tangentialbedingungen und Sweep prüfen: Benutzer bestätigt verbesserten Übergang im Beispiel; weitere Sonderfälle bleiben offen
- [~] Fusion-Prüfung von 0.2.2: grundsätzliche Funktion vom Benutzer bestätigt; Sonderfälle gemäß Entwicklungsanleitung noch offen

## Zielversion

**0.2.x**

Stand 2026-09-28: **0.2.3 (development)** enthält Datenmodell, Abschnittsverwaltung
und variable Skizzenausgabe. Bis zu 32 Abschnitte mit linearem Durchmesser- und
Steigungsverlauf sind möglich; gemeinsame Grenzen werden verbunden.
Der vorherige Stand 0.2.0 wurde vom Benutzer als lauffähig bestätigt.
Der Dialogaufbaufehler von 0.2.1 ist behoben; Achslängenübernahme wurde vorgezogen.
Für sichtbare Sweep-Übergänge wurden Tangentialbedingungen (G1) als aktivierbare Option ergänzt.
Surface-Helix-Grundlage ist in 0.3.0 begonnen; weitere G1-Sonderfälle bleiben
für die manuelle Fusion-Prüfung offen.

# Version 0.3.x – Surface Helix

## Ziel

Helix anhand einer Rotationsoberfläche bzw. eines Rotationskörpers erzeugen.

## Schritte

- [x] Auswahl von Körper / Fläche vorbereiten (0.3.0: einzelne Mantelfläche am Körper)
- [~] Prüfung auf geeignete Rotationsgeometrie einbauen (vollständige analytische Zylinder-/Kegelmäntel mit zwei Kreisrändern geprüft; weitere Rotationsflächen offen)
- [x] Radius aus Oberflächenkontur ableiten (axiale Länge, Start-/Endradius, linearer Radiusverlauf; Fusion-Prüfung offen)
- [x] Helix auf der Oberfläche berechnen (0.3.3: vollständige Zylinder-/Kegelmäntel, konstante Steigung, schnelle Vorschau und 3D-Skizzenausgabe; grundsätzliche Funktion vom Benutzer in Fusion bestätigt, Sonderfälle offen)
- [x] Surface Offset integrieren (0.3.4: Offset-Funktion, Vorschau und negativer Abstand vom Benutzer in Fusion bestätigt; weitere Sonderfälle offen)
- [x] Kombination mit variabler Steigung ermöglichen (0.3.5: Start-/Endsteigung linear entlang der Achse; Funktion vom Benutzer in Fusion bestätigt, weitere Sonderfälle offen)
- [x] Testmodelle definieren (0.3.6: Modellbauanleitungen, Sollwerte und Prüfprotokoll in [Surface-Testmodelle](surface-testmodelle.md); manueller Durchlauf offen)
- [~] erste stabile Surface-Helix-Version testen (Benutzer meldet für 0.3.6 keine Fehler; vollständiger Sonderfallkatalog noch nicht einzeln protokolliert)

## Zielversion

**0.3.0**

Stand 2026-09-29: **0.3.0 (development)** bietet zunächst die Flächenauswahl
und Flächentypprüfung. Surface Helix erzeugt noch keine Geometrie; Ausführen
bleibt in diesem Modus gesperrt. Parametrische Helices bleiben verfügbar.
Zusätzlich umgesetzt: Dialogreiter „Helix erstellen“, „Einstellungen“ und
„Info“ mit Logo, Versionsanzeige und Projektlinks nach Benutzervorlage.
Erweiterung in 0.3.2: Radius und axialer Bereich werden
aus zwei koaxialen Kreisrändern abgeleitet. Der Flächeninhalt wird mit dem
vollständigen Zylinder-/Kegelmantel verglichen; Teilflächen und Ausschnitte
werden abgelehnt. Kegelspitzen und geteilte Kreisränder sind noch nicht unterstützt.
Stand 0.3.3: Oberflächenhelix mit konstanter Steigung, Startwinkel, Drehrichtung
und Randwechsel implementiert. 0.3.4 ergänzt Surface Offset; 0.3.5 ergänzt
variable Steigung im Surface-Modus. Testmodelle und Prüfprotokoll sind in 0.3.6 definiert.
Benutzer meldet für 0.3.6 keine aufgefallenen Fehler. Der vollständige Surface-Testdurchlauf
bleibt als manuelle Prüfung offen; die Entwicklung geht mit Presets weiter.

# Version 0.4.x – Presets

## Ziel

Helix-Konfigurationen speichern, laden, importieren und exportieren.

## Schritte

- [x] Preset-Datenmodell anlegen (0.4.0: beide Modi, Schema 1, feste Einheiten und JSON-Validierung)
- [x] Built-in-Presets definieren (0.4.0: Basishelix, variable Abschnitte und Surface-Steigung)
- [x] Speichern unter frei wählbarem Namen umsetzen (0.4.2: Benutzerprofil, ohne Überschreiben bestehender Namen)
- [x] Presets laden (0.4.1: Built-ins bestätigt; 0.4.2: eigene Vorlagen vom Benutzer als funktionierend bestätigt)
- [x] Presets löschen (0.4.2: eigene Vorlagen mit Bestätigung; Built-ins geschützt)
- [ ] JSON-Export umsetzen
- [ ] JSON-Import umsetzen
- [x] Dateiendung `*.helixpilot.json` verwenden (Built-in-Dateien in 0.4.0)
- [~] Fehlerbehandlung für ungültige Presets ergänzen (Datenvalidierung in 0.4.0; 0.4.2 ergänzt Dateifehler im Dialog; Importprüfung folgt)

## Zielversion

**0.4.0** – Datenmodell und Built-in-Vorlagen implementiert; [Formatbeschreibung](presets.md). 0.4.1 ergänzt Built-in-Auswahl und Laden im Dialog. 0.4.2 ergänzt Speichern/Laden/Löschen eigener Vorlagen. Als Nächstes JSON-Dateiimport/-export.

# Version 0.5.x – Preview / Interaktion

## Ziel

Eine gute Benutzererfahrung mit Live-Vorschau im Viewport schaffen.

## Schritte

- [x] Live-Vorschau-Grundlage implementieren (vorgezogen in 0.3.1; Vorschau und Geschwindigkeit vom Benutzer in Fusion bestätigt)
- [x] Vorschau für Parametric Helix (0.3.1)
- [x] Vorschau für Variable Helix (0.3.1)
- [ ] Vorschau für Surface Helix
- [ ] performante Aktualisierung bei Parameteränderungen
- [x] unnötige Neuberechnungen reduzieren (0.3.1 ohne Versionswechsel: Custom-Graphics-Vorschau statt Skizze/G1 bei jeder Eingabe, unveränderte Grafik wiederverwenden)
- [~] UI-Feinschliff (0.4.3: kompakte Dialoggröße, eigener Vorlagenreiter und farbige Abschnittsvorschau; Farben und Entfernen über zentrale Auswahl vom Benutzer bestätigt, weitere Bildschirmprüfungen offen)
- [ ] Eingabevalidierung verbessern

## Zielversion

**0.5.0**

# Version 0.6.x – Output / Refactoring / Stabilisierung

## Ziel

Technische Qualität erhöhen und spätere Erweiterungen vorbereiten.

## Schritte

- [ ] Code aufräumen
- [ ] Kernlogik weiter von Fusion-API trennen
- [ ] interne Datenmodelle vereinheitlichen
- [ ] Fehlerbehandlung verbessern
- [ ] Grundlagen für optionalen Sweep-Output vorbereiten
- [ ] Logging verbessern
- [ ] Stabilitätstests durchführen

## Zielversion

**0.6.0**

# Version 0.7.x – Dokumentation / Beispiele / UX

## Ziel

Projekt für Anwender und Mitwirkende verständlicher machen.

## Schritte

- [ ] Dokumentation erweitern
- [ ] Beispielanwendungen ergänzen
- [ ] Beispiel-Presets anlegen
- [~] Screenshots / Visuals einpflegen (v0.1.2, v0.2.2, v0.2.3, v0.3.3, v0.3.4, v0.3.5 und v0.4.1 in deutscher und englischer Versionsgalerie dokumentiert; weitere Versionen folgen)
- [ ] Installationshinweise vorbereiten
- [ ] Bedienkonzept prüfen
- [ ] Benennungen und Texte im UI verbessern

## Zielversion

**0.7.0**

# Version 0.8.x – Beta-Vorbereitung

## Ziel

Projekt auf eine Beta-Phase vorbereiten.

## Schritte

- [ ] offene Bugs sammeln
- [ ] kritische Bugs beheben
- [ ] Testcheckliste aufbauen
- [ ] Doku auf Konsistenz prüfen
- [ ] Presets und Beispieldateien prüfen
- [ ] Release-Struktur vorbereiten
- [ ] Versions- und Paketierungslogik prüfen

## Zielversion

**0.8.0**

# Version 0.9.x – Setup EXE / Packaging

## Ziel

Erstellung einer Setup EXE mit Inno Setup.

## Schritte

- [ ] Installationsstruktur definieren
- [ ] Dateien für Distribution zusammenstellen
- [ ] Inno-Setup-Skript anlegen
- [ ] Versionsnummern in Installer übernehmen
- [ ] Installer-Icon / Metadaten einbinden
- [ ] Testinstallation durchführen
- [ ] Deinstallation testen
- [ ] Installationsanleitung dokumentieren
- [ ] Release-Paket vorbereiten

## Zielversion

**0.9.0**

# Version 1.0.0 – Erstes stabiles Release

## Ziel

Erste offiziell veröffentlichbare Version bereitstellen.

## Schritte

- [ ] letzte offene Punkte bewerten
- [ ] finale Doku prüfen
- [ ] finale Versionsnummer setzen
- [ ] Release Notes erstellen
- [ ] Repository für Veröffentlichung prüfen
- [ ] Release-Paket bereitstellen

# Backlog / neue Ideen

## Umgesetzt in 0.3.1 – Benutzerwünsche vom 2026-09-29

- [x] Durchmesserverknüpfung für die gesamte Abschnittskette zusätzlich beim Lesen synchronisieren; Tooltips zeigen den direkten Vorgänger. 32 Abschnitte sowie Entfernen mittlerer/erster Abschnitte automatisiert geprüft.
- [x] Punktdarstellung vereinfachen: interne Spline-Stützpunkte ausblenden und Abschnittsanfänge/-enden mit separaten Punkten markieren, ohne die Kurvenauflösung zu reduzieren.
- [x] Live-Vorschau für parametrische/variable Helices vorziehen: schnelle Custom Graphics mit gewählter Achse, unter Einstellungen schaltbar. Finale Skizze und G1 erst beim Bestätigen; Performance-Korrektur ohne Versionsänderung.
- [x] Vorschau, Geschwindigkeit und Durchmesserverknüpfung der Abschnitte in Fusion prüfen (vom Benutzer bestätigt).
- [ ] Weitere Sonderfälle in Fusion prüfen: Grenzmarkierungen beim Bearbeiten/Selektieren, Vorschau bei ungültigen Eingaben, Abbrechen, Moduswechsel und Rückgängig.

Surface-Konturableitung, Oberflächenhelix und Offset sind implementiert; variable Surface-Steigung ist seit 0.3.5 implementiert. Testmodelle sind definiert; der vollständige Surface-Testdurchlauf in Fusion bleibt offen. Preset-Dialog und Benutzerdateiverwaltung sind bis 0.4.2 implementiert; als Nächstes JSON-Dateiimport/-export.

Benutzer bestätigt die Mantelflächenerkennung. Gemeldete Eingabelatenz von
15–20 Sekunden durch Ersatz der Skizzenvorschau adressiert; Benutzer bestätigt
anschließend passende Geschwindigkeit und Vorschau sowie korrekte Abschnittsdurchmesser.

## Weitere Ideen

- [x] Helixlänge aus endlicher Skizzenlinie oder gerader Körperkante einmalig übernehmen (0.2.2): positive, endliche Länge prüfen, unendliche Konstruktionsachsen ausschließen, Abschnittslängen proportional skalieren. Fusion-Prüfung noch offen.
- [ ] direkter Sweep-Output
- [ ] Drahtdurchmesser als Komfortfunktion
- [ ] automatische Federerzeugung
- [ ] Krümmungsstetige Übergänge (G2) untersuchen; G1-Tangentialbedingungen sind seit 0.2.3 implementiert
- [ ] verbesserte Validierung für Surface-Geometrien
- [ ] zusätzliche Beispiel-Presets
- [ ] mehrsprachige UI
- [ ] macOS-spezifische Prüfung
- [ ] Signierung / Release-Prozess

## Pflegehinweis

Wenn neue Ideen entstehen oder Anforderungen geändert werden, soll CodeX:

1. die Änderung in `timeline.md` eintragen,
2. sie hier passend einordnen,
3. bei Bedarf die Versionszuordnung anpassen,
4. den Status bestehender Punkte aktualisieren.

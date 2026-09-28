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
- [ ] Basis-Command für Helix-Erzeugung anlegen
- [ ] Achsauswahl integrieren
- [ ] Durchmesser, Länge und Steigung integrieren
- [ ] Drehrichtung integrieren
- [ ] Startwinkel integrieren
- [ ] erste 3D-Skizzenerzeugung umsetzen
- [ ] erste lauffähige Basisversion testen

## Zielversion

**0.1.0**

Stand 2026-09-28: Projektbasis unter `HelixPathPilot/` angelegt, mit
Start-/Stop-Einstieg, leerer Command-Registrierung und Hilfsmodulen aus der
unveränderten Vorlage. Version 0.1.0 bleibt ein Entwicklungsstand; die
Helix-Erzeugung und der Laufzeittest in Fusion sind noch offen.
Nächster Schritt: Basis-Command für die parametrische Helix.
Ladeanleitung und manuelle Prüfschritte: [Entwicklung](development.md).

# Version 0.2.x – Variable Helix

## Ziel

Mehrere Abschnitte mit unterschiedlichen Parametern ermöglichen.

## Schritte

- [ ] Datenmodell für Helix-Segmente erstellen
- [ ] Segmentliste / Abschnittsverwaltung implementieren
- [ ] variable Durchmesser unterstützen
- [ ] variable Steigungen unterstützen
- [ ] lineare Übergänge umsetzen
- [ ] Berechnungslogik überarbeiten
- [ ] segmentierte Helix als 3D-Skizze erzeugen
- [ ] Testfälle ergänzen

## Zielversion

**0.2.0**

# Version 0.3.x – Surface Helix

## Ziel

Helix anhand einer Rotationsoberfläche bzw. eines Rotationskörpers erzeugen.

## Schritte

- [ ] Auswahl von Körper / Fläche vorbereiten
- [ ] Prüfung auf geeignete Rotationsgeometrie einbauen
- [ ] Radius aus Oberflächenkontur ableiten
- [ ] Helix auf der Oberfläche berechnen
- [ ] Surface Offset integrieren
- [ ] Kombination mit variabler Steigung ermöglichen
- [ ] Testmodelle definieren
- [ ] erste stabile Surface-Helix-Version testen

## Zielversion

**0.3.0**

# Version 0.4.x – Presets

## Ziel

Helix-Konfigurationen speichern, laden, importieren und exportieren.

## Schritte

- [ ] Preset-Datenmodell anlegen
- [ ] Built-in-Presets definieren
- [ ] Speichern unter frei wählbarem Namen umsetzen
- [ ] Presets laden
- [ ] Presets löschen
- [ ] JSON-Export umsetzen
- [ ] JSON-Import umsetzen
- [ ] Dateiendung `*.helixpilot.json` verwenden
- [ ] Fehlerbehandlung für ungültige Presets ergänzen

## Zielversion

**0.4.0**

# Version 0.5.x – Preview / Interaktion

## Ziel

Eine gute Benutzererfahrung mit Live-Vorschau im Viewport schaffen.

## Schritte

- [ ] Live-Vorschau-Grundlage implementieren
- [ ] Vorschau für Parametric Helix
- [ ] Vorschau für Variable Helix
- [ ] Vorschau für Surface Helix
- [ ] performante Aktualisierung bei Parameteränderungen
- [ ] unnötige Neuberechnungen reduzieren
- [ ] UI-Feinschliff
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
- [ ] Screenshots / Visuals einpflegen
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

- [ ] direkter Sweep-Output
- [ ] Drahtdurchmesser als Komfortfunktion
- [ ] automatische Federerzeugung
- [ ] zusätzliche Übergangstypen (smooth)
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

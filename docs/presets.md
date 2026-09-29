# Preset-Format – Stand 0.4.0

Die erste Preset-Ausbaustufe enthält ein Fusion-unabhängiges Datenmodell,
JSON-Serialisierung und drei mitgelieferte Vorlagen. Es gibt noch keine
Preset-Bedienelemente im Fusion-Dialog und keine Benutzerdateiverwaltung.

## Format

Dateiendung: `*.helixpilot.json`. JSON als UTF-8, maximal 128 KiB.
`schema_version` ist 1; Längen sind ausdrücklich in **cm**, Winkel in **rad**
gespeichert, unabhängig von der Fusion-Anzeigeeinheit. Name: 1 bis 100 Zeichen,
nicht nur Leerraum, keine Steuerzeichen. Der Name ist kein Dateipfad.

Gemeinsame Felder: `schema_version`, `name`, `mode`, `length_unit`, `angle_unit`,
`parameters`, `reverse_axis` und `tangent_joins`. Unbekannte oder fehlende Felder,
doppelte JSON-Schlüssel, nichtendliche Zahlen und unbekannte Schemaversionen
werden abgelehnt, um unbeabsichtigte Parameteränderungen zu verhindern.

`mode: "parametric"` speichert unter `parameters` die Abschnittsliste `segments`,
`start_angle` und `right_handed`. Jeder Abschnitt enthält `length`,
`diameter_start`, `diameter_end`, `pitch_start` und `pitch_end`. Die vorhandenen
Grenzen für Abschnittszahl, Windungen und Stützpunkte sowie die
Durchmesserkontinuität gelten auch für Presets.

`mode: "surface"` speichert unter `parameters` nur `pitch_start`, `pitch_end`,
`offset`, `start_angle`, `right_handed` und `reverse` (Startrandwechsel).
`reverse_axis` muss hier false sein; `tangent_joins` hat im Surface-Modus keine
Wirkung. Radius, Länge und Achse stammen weiterhin aus einer ausgewählten Fläche.
Offset-Radiusgrenzen und Windungslimits können deshalb erst zusammen mit dieser
Fläche geprüft werden.

Flächen- und Achsauswahlen werden nicht serialisiert; sie sind dokumentabhängig.
Die Live-Vorschau bleibt eine Dialogeinstellung und gehört nicht zum Preset.

## Mitgelieferte Vorlagen

Unter `Fusion_addin/HelixPathPilot/presets/builtin/`:

| Datei | Inhalt in Anzeigeeinheit mm |
| --- | --- |
| `basic.helixpilot.json` | Länge 50, Durchmesser 20, Steigung 5; 10 Windungen |
| `variable.helixpilot.json` | Abschnitt 1: Länge 50, Durchmesser 20 → 30, Steigung 5 → 10; Abschnitt 2: Länge 25, Durchmesser 30 → 20, Steigung 10 → 5 |
| `surface.helixpilot.json` | Steigung 5 → 10, Offset 0; Fläche später auswählen |

Alle Vorlagen sind rechtsdrehend mit Startwinkel 0. Parametrische Vorlagen
verwenden G1-Übergänge und keine Achsumkehr.

## Entwicklerschnittstelle

`core.presets.HelixPreset` besitzt `to_dict()`, `to_json()`, `from_dict()` und
`from_json()`. Die Parameter sind ein `SegmentedHelix` oder `SurfaceSettings`.
Die Datenmodelle sind unveränderlich; exportierte Dictionaries sind unabhängige
Kopien. Validierungsfehler werden als `ValueError` gemeldet.

Nächster Schritt: Dialogintegration für benannte Benutzerpresets mit Laden,
Speichern, Löschen und JSON-Dateiimport/-export. Die jetzigen Methoden lesen
und schreiben JSON-Text, aber noch keine Dateien oder Fusion-Eingaben.

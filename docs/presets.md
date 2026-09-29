# Preset-Format und Bedienung – Stand 0.4.3

Die erste Preset-Ausbaustufe enthält ein Fusion-unabhängiges Datenmodell,
JSON-Serialisierung und drei mitgelieferte Vorlagen. Seit 0.4.1 sind die Vorlagen
im Fusion-Dialog sichtbar; seit 0.4.3 liegen sie im eigenen Reiter **Vorlagen**. Auswählen und
**Vorlage laden** drücken, um Modus und Parameter zu übernehmen. Dabei werden
aktuelle Parameter ersetzt; Achse und Mantelfläche bleiben separat gewählt.
Nach dem Laden wechselt der Dialog zu „Helix erstellen“. Die Auswahl allein verändert noch keine Eingaben. Seit 0.4.2 können eigene
Vorlagen gespeichert, geladen und gelöscht werden.

## Eigene Vorlagen verwalten

1. Gewünschten Modus und Helix-Werte einstellen.
2. Unter „Vorlagen“ einen Namen eingeben und **Als eigene Vorlage speichern** drücken.
3. Die gespeicherte Vorlage erscheint mit „Eigene“ in der Liste. Zum Wiederherstellen
   auswählen und **Vorlage laden** drücken, auch nach erneutem Öffnen des Dialogs.
4. **Eigene Vorlage löschen** entfernt die ausgewählte Benutzerdatei nach Bestätigung.
   Die aktuellen Helix-Werte bleiben dabei erhalten; mitgelieferte Vorlagen sind geschützt.

Doppelte Namen werden ohne Unterscheidung der Groß-/Kleinschreibung abgewiesen.
Zum Speichern einer Variante einen neuen Namen verwenden. Führender und
abschließender Leerraum wird entfernt. Ungültige Eingaben werden nicht gespeichert.
Surface-Einstellungen können ohne Fläche gespeichert werden; die Eignung der
Fläche und geometrieabhängige Grenzen werden beim Erzeugen geprüft.

Speichern und Löschen wirken sofort auf Dateien. Abbrechen des Helix-Dialogs
oder Fusions Rückgängig für Modellierungsschritte setzt diese Dateiaktionen nicht zurück.

Speicherorte außerhalb des Add-in-Verzeichnisses:

- Windows: `%APPDATA%\HelixPathPilot\presets`
- macOS: `~/Library/Application Support/HelixPathPilot/presets`

Die Namen erscheinen im JSON-Inhalt; Dateinamen werden aus normalisierten Namen
abgeleitet und enthalten keine eingegebenen Pfadzeichen. Der gesamte Ordner kann
zur Sicherung kopiert werden. Die Dateien unter `presets/user/` im Add-in-Ordner
werden nicht verwendet. Ein Dateiauswahldialog für Import/Export folgt später.

[Screenshots der Vorlagenauswahl und einer geladenen Helix](screenshots-DE.md#v041)
zeigen die Bedienung in Version 0.4.1.

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

`commands.presetManager.catalog` liest die mitgelieferten Dateien und meldet
ungültige Dateien einzeln. Der Dialog übernimmt validierte Vorlagen in die
Fusion-Eingaben. Die Kernmethoden selbst verarbeiten weiterhin nur JSON-Text.

`core.preset_store.PresetStore` verwaltet Benutzerdateien unabhängig von Fusion.
Lesen prüft Größe und Schema erneut; beschädigte Dateien werden beim Auflisten
einzeln gemeldet und übersprungen. Speichern überschreibt keine vorhandene Datei.

Nächster Schritt: JSON-Dateiimport/-export.

# Entwicklung und erster Funktionstest

## Projektbasis – 0.1.0 (development)

`Fusion_addin/HelixPathPilot/` bleibt die ursprüngliche Vorlage.
Das zu entwickelnde Add-in liegt separat unter `HelixPathPilot/`:

- `HelixPathPilot.py`: Fusion-Einstiegspunkte `run` und `stop`, Logging und Fehlerbehandlung.
- `HelixPathPilot.manifest`: Fusion-Metadaten; Version mit `version.py` synchron halten.
- `commands/`: leere Registrierung und vorbereitete Pakete für die drei geplanten Commands.
- `core/`: reserviert für Fusion-unabhängige Mathematik und Datenmodelle.
- `lib/fusionAddInUtils/`: unveränderte Hilfsmodule der Autodesk-Vorlage inklusive Lizenzhinweisen.
- `presets/builtin/` und `presets/user/`: vorbereitet; lokale Benutzer-Presets werden nicht versioniert.
- `resources/`: vorbereitete Ordner für Icons, Banner und Logo.

Demo-Commands und Demo-Paletten sind nur in der Vorlage enthalten.
Das neue Add-in erzeugt in diesem Schritt noch keine Buttons oder Geometrie.
Die aktive Versionsquelle ist `HelixPathPilot/version.py`; die Versionsdatei in
der Vorlage beschreibt nur deren ursprünglichen Stand.

## In Fusion laden

1. In Fusion den Dialog **Skripte und Zusatzmodule / Scripts and Add-Ins** öffnen.
2. Ein vorhandenes Add-in hinzufügen und den Unterordner
   `<Repo>/HelixPathPilot/` wählen, der die gleichnamigen `.py`- und `.manifest`-Dateien enthält.
3. HelixPathPilot starten. Die Vorlage gleichen Namens dabei nicht parallel laden.
4. In den Textbefehlen / Text Commands die Meldung
   `HelixPathPilot v0.1.0 (development) started` prüfen (`DEBUG = True`).
5. Add-in stoppen und die entsprechende `stopped`-Meldung prüfen.
6. Starten und Stoppen wiederholen; es sollen keine Fehlermeldungen erscheinen.

Die Registrierung eines vorhandenen Add-in-Ordners beschreibt die
[Autodesk-Anleitung](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UsingSamplesFromGitHub_UM.htm).
Der Aufbau folgt der [Autodesk-Python-Vorlage](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/PythonTemplate_UM.htm).

## Prüfstatus

Die 13 Python-Dateien wurden auf gültige Syntax geprüft. Manifest-Version,
Icon-Pfad, unveränderte Hilfsmodul-Kopien und Start/Stop der leeren
Command-Registrierung wurden erfolgreich geprüft.

Syntax und Manifest lassen sich außerhalb von Fusion prüfen. Die Fusion-API
(`adsk`) benötigt für einen aussagekräftigen Laufzeittest die Fusion-Anwendung.
Der manuelle Start-/Stop-Test in Fusion ist noch offen; ebenso die macOS-Prüfung.
Die Angabe `windows|mac` im Manifest wurde aus der Vorlage übernommen.

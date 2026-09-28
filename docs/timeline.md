# Timeline – HelixPathPilot

Pro Version gibt es einen kompakten Eintrag mit einem direkt für GitHub nutzbaren
Kurztext, gekennzeichnet durch **GitHub:**. Entwicklungsstände sind keine
Bestätigung eines abgeschlossenen Fusion-Laufzeittests.

## 0.2.0 – 2026-09-28 – Entwicklung

**GitHub:** Datenmodell für mehrteilige Helices ergänzt: Abschnittslänge,
Start-/Enddurchmesser und Start-/Endsteigung mit linearer Interpolation und
Validierung. Grundlage für die kommende Abschnittsverwaltung; der Dialog
erzeugt weiterhin die einfache Helix.

Die Dokumentation ergänzt eine nach Versionen gegliederte Screenshot-Galerie
in Deutsch und Englisch mit Vorschau in beiden READMEs.

- Unveränderliche Segmentliste, Gesamtlänge und Übernahme bestehender Helix-Parameter implementiert.
- Vier Screenshots aus v0.1.2 mit Bildunterschriften eingebunden; Struktur für weitere Versionen angelegt. Reine Dokumentationsergänzung ohne Änderung der Add-in-Version.
- Gemeinsame Validierung für einfache und mehrteilige Helix; 29 automatisierte Tests bestanden.
- Benutzer bestätigt Menüposition, Icons und Ausrichtung an beliebiger Achse aus 0.1.2.
- Vorgemerkt: Helix-Gesamtlänge aus endlicher Skizzenlinie oder Körperkante übernehmen. Unendliche Achsen und ungültige Längen ausschließen; Umsetzung in einer späteren Version.

## 0.1.2 – 2026-09-28 – Entwicklung

**GitHub:** HelixPathPilot mit Versionsanzeige nach Volumenkörper → Erstellen
verschoben und mit Helix-Icons für Menü und Symbolleiste ausgestattet.
Freie Achsauswahl über Konstruktionsachsen, gerade Modellkanten und Skizzenlinien
mit umkehrbarer Richtung ergänzt.

- Buttonname aus `version.py`; Manifest auf 0.1.2 aktualisiert. Synchronisierungsskript und Versionstest sichern den Abgleich.
- Ohne Auswahl weiterhin globale Z-Achse; räumliche Orientierung der Helix in der Hauptkomponente.
- Skalierbare SVG-Icons und PNG-Dateien in 16, 32 und 64 Pixeln; Add-in-Listenicon angeglichen.
- 19 automatisierte Tests bestanden. Menüplatzierung, Icons und Achsauswahl anschließend vom Benutzer in Fusion bestätigt.
- Benutzer bestätigt die grundsätzliche Funktion des bisherigen Basis-Commands 0.1.1.

## 0.1.1 – 2026-09-28 – Entwicklung

**GitHub:** Basis-Command für Helices mit konstantem Durchmesser und konstanter
Steigung ergänzt. Dialog mit Länge, Drehrichtung und Startwinkel; Ausgabe als
3D-Spline um die globale Z-Achse. Aktives Add-in unter `Fusion_addin/HelixPathPilot/`.

- Vorlage auf Benutzerwunsch durch die Implementierung ersetzt; Demo-Commands entfernt.
- Fusion-unabhängige Helix-Berechnung, Eingabevalidierung und Begrenzung auf 128 Windungen.
- Neun automatisierte Tests für Geometrie, Validierung, Metadaten und Skizzenadapter bestanden.
- Die Kurve ist eine Spline-Näherung, keine nachträglich parametrisch verknüpfte Helix.
- Timeline nach Versionsnummer zusammengefasst. Freie Achsauswahl und Fusion-Laufzeittest offen.
- `HelixPathPilot/` im Repo-Hauptverzeichnis bleibt als Altstand 0.1.0 erhalten und wird nicht weiterentwickelt.

## 0.1.0 – 2026-09-28 – Entwicklung

**GitHub:** Projektbasis für HelixPathPilot angelegt: Fusion-Einstiegspunkte,
Command-Struktur, Versionsverwaltung und zweisprachige Projektdokumentation.

- Projektname und Hauptmodi Parametric Helix / Surface Helix festgelegt.
- Add-in-Gerüst mit Autodesk-Hilfsmodulen zunächst separat unter `HelixPathPilot/` angelegt.
- Ordner für Mathematik, Commands, Presets und Ressourcen vorbereitet; Git-Ausnahmen für Manifest und Hilfsmodule ergänzt.
- Ablaufplan und Dokumentationsregeln definiert. Inno-Setup-Installer für Version 0.9 vorgesehen.

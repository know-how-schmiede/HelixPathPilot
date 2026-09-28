# Timeline – HelixPathPilot

Pro Version gibt es einen kompakten Eintrag mit einem direkt für GitHub nutzbaren
Kurztext, gekennzeichnet durch **GitHub:**. Entwicklungsstände sind keine
Bestätigung eines abgeschlossenen Fusion-Laufzeittests.

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

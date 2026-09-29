# Timeline – HelixPathPilot

Pro Version gibt es einen kompakten Eintrag mit einem direkt für GitHub nutzbaren
Kurztext, gekennzeichnet durch **GitHub:**. Entwicklungsstände sind keine
Bestätigung eines abgeschlossenen Fusion-Laufzeittests.

## 0.3.5 – 2026-09-29 – Entwicklung

**GitHub:** Variable Steigung für Surface Helix ergänzt. Start- und Endsteigung
verlaufen linear entlang der axialen Länge auf Zylinder- und Kegelmänteln,
einschließlich Surface Offset, Randwechsel und schneller Vorschau.

- Gleiche Werte erhalten konstante Steigung; Standard jeweils 5 mm. Start-/Endwerte gelten in Laufrichtung, auch nach Randwechsel.
- Gemeinsame Berechnung für Vorschau und Skizzenausgabe; positive endliche Steigungen und bisherige Windungs-/Punktlimits werden geprüft.
- 82 automatisierte Tests bestanden: analytischer Winkelverlauf, Mantelabstand auf schrägen Achsen, beide Steigungsverläufe, Drehrichtungen und Randwechsel sowie Dialogvalidierung und Vorschau-/Ausgabeübergabe.
- Benutzer bestätigt die Funktion der variablen Surface-Steigung in Fusion; weitere Sonderfälle gemäß Entwicklungsanleitung bleiben offen. Nächster Schritt: Testmodelle definieren.
- Zwei Screenshots von 0.3.5 in deutscher und englischer Galerie ergänzt: zunehmende Steigung am Zylinder und abnehmende Steigung am Kegel, jeweils mit positivem Offset. README-Vorschauen aktualisiert; Version unverändert.

## 0.3.4 – 2026-09-29 – Entwicklung

**GitHub:** Surface Offset ergänzt. Helix-Pfade lassen sich mit positivem oder
negativem Normalabstand zu Zylinder- und Kegelmänteln erzeugen und vorab anzeigen.

- Standard 0; positive Werte zeigen von der Achse weg, negative zur Achse hin, unabhängig von Innen-/Außenfläche und Laufrichtung.
- Am Kegel werden Radius und axialer Ursprung entlang der Mantelnormalen verschoben. Endpunkte sind die versetzten Randpunkte; axiale Spannweite, Steigung und Windungszahl bleiben gleich.
- Flächenradien, resultierende Helixradien und Offset im Dialog angezeigt. Ungültige Abstände und Erreichen/Überschreiten der Rotationsachse werden abgewiesen.
- 80 Tests bestanden, einschließlich Normalabstand auf schrägen Zylinder-/Kegelachsen, beide Laufrichtungen und identischer Parameterübergabe an Vorschau/Ausgabe. Benutzer bestätigt Offset-Funktion, Vorschau und negativen Abstand zur Mantelfläche in Fusion; weitere Sonderfälle bleiben offen.
- Drei Screenshots von 0.3.4 in deutscher und englischer Galerie ergänzt: positiver Zylinderoffset sowie negativer und positiver Kegeloffset. README-Vorschauen aktualisiert. Version bleibt auf Benutzerwunsch 0.3.4.
- Nächster Schritt: variable Steigung im Surface-Modus.

## 0.3.3 – 2026-09-29 – Entwicklung

**GitHub:** Surface Helix erzeugt jetzt eine angenäherte 3D-Spline auf vollständigen
Zylinder- und Kegelmänteln. Einstellbar sind konstante axiale Steigung, Startwinkel,
Drehrichtung und Startrand. Schnelle Grafikvorschau ohne Skizzenberechnung.

- Radiusverlauf, Achse und Länge stammen aus der ausgewählten Fläche. Randwechsel verschiebt den Ursprung zum anderen Rand und kehrt Achse und Radiusverlauf um.
- Gemeinsame Abtastung und Skizzenausgabe mit parametrischer Helix; Limits 128 Windungen und 4097 Punkte. Eine Spline, keine G1-Abschnittsbedingungen im Surface-Modus.
- Vorschau und Ausgabe verwenden dieselben Parameter. Fehlende/ungeeignete Fläche sowie ungültige Steigung oder Winkel sperren Ausführen. Verdeckte parametrische Eingaben beeinflussen Surface Helix nicht.
- 78 Tests bestanden: analytische Mantelgleichung aller berechneten Punkte auf schrägen Achsen, beide Laufrichtungen, Linksdrall, Teilwindungen und Dialogintegration. Benutzer bestätigt die grundsätzliche Funktion in Fusion; weitergehende Sonderfälle bleiben offen.
- Fünf Screenshots von 0.3.3 in deutscher und englischer Galerie ergänzt: Zylinder-/Kegelvorschau und Anwendungsbeispiele mit Nut und Wickelkörpern. README-Vorschauen aktualisiert; Version unverändert.
- Surface Offset und variable Surface-Steigung bleiben nächste Ausbauschritte. Keine nachträgliche Verknüpfung der Skizze mit der Fläche.

## 0.3.2 – 2026-09-29 – Entwicklung

**GitHub:** Surface-Konturableitung ergänzt. Axiale Länge und Start-/Endradius
werden aus den beiden Kreisrändern einer analytischen Mantelfläche abgeleitet
und im Dialog angezeigt. Neues Fusion-unabhängiges Profilmodell mit linearem
Radiusverlauf und Achsursprung am ersten Rand in Richtung der Flächenachse.
Koaxialität, Randnormalen, positive Radien und vollständige Mantelfläche werden
geprüft. Teilflächen, zusätzliche Ausschnitte, Kegelspitzen und geteilte Ränder
werden vorerst abgewiesen. 74 Tests bestanden, einschließlich schräger und
umgekehrter Achsen sowie Fusion-Adapter mit Testdoubles. Prüfung der neuen
Maßanzeige in Fusion offen. Noch keine Surface-Helix-Ausgabe oder Offset.

## 0.3.1 – 2026-09-29 – Entwicklung

**Performance-Korrektur ohne Versionsänderung:** Benutzer meldet 15–20 Sekunden
Reaktionszeit und bestätigt die Mantelflächenerkennung. Die bisherige Vorschau
erzeugte bei jeder Änderung eine vollständige Skizze einschließlich G1-Solver.
Sie wurde durch temporäre Custom Graphics ersetzt: eine Liniengrafik und
Grenzpunkte, keine Skizzen-/Solveraufrufe während der Eingabe. Unveränderte
Grafik wird wiederverwendet; ungültige Eingaben, Moduswechsel, Abschalten,
Ausführen und Dialogende räumen sie auf. Die finale Skizze mit G1 entsteht
erst beim Bestätigen. Die Vorschau zeigt den mathematischen Pfad vor der
G1-Anpassung; ein Dialoghinweis erklärt die mögliche Abweichung.
68 automatisierte Tests bestanden. Benutzer bestätigt anschließend, dass
Vorschau und Geschwindigkeit passen und die Durchmesserverknüpfung in den
Abschnitten korrekt funktioniert. Keine numerische Laufzeitmessung angegeben.
Die folgenden ursprünglichen Vorschauangaben werden durch diese Korrektur ersetzt.

**GitHub:** Live-Vorschau für parametrische und variable Helices ergänzt,
Punktanzeige auf Abschnittsgrenzen reduziert und Durchmesserverknüpfung über
die vollständige Abschnittskette abgesichert.

- Live-Vorschau standardmäßig aktiv, unter „Einstellungen“ abschaltbar. Gleiche Ausgabe wie beim Bestätigen, einschließlich gewählter Achse und G1. Erfolgreiche Vorschau wird über Fusions Vorschautransaktion beim Bestätigen übernommen; Abbrechen verwirft sie.
- Ungültige Eingaben und Surface-Flächenprüfung erzeugen keine Vorschau. Solverfehler erscheinen als Hinweis im Dialog, ohne Meldungsfenster bei jeder Änderung.
- Alle Spline-Stützpunkte bleiben erhalten, werden aber über die Skizzenpunktanzeige ausgeblendet. Separate, unverbundene Markierungspunkte zeigen Anfang, gemeinsame Grenzen und Ende (n+1 Marker für n Abschnitte). Koordinaten werden nach der G1-Lösung übernommen.
- Startdurchmesser jedes Folgeabschnitts wird zusätzlich beim Lesen synchronisiert; Tooltips nennen den direkten Vorgänger. Tests decken alle 32 Abschnitte und Entfernen mittlerer/erster Abschnitte ab.
- 63 automatisierte Tests bestanden. Fusion-Laufzeitprüfung von Darstellung, Vorschau-Rollback und Ergebnisübernahme steht aus; die ursprüngliche Ursache der gemeldeten Anzeigeabweichung ist außerhalb von Fusion nicht reproduziert.

## 0.3.0 – 2026-09-29 – Entwicklung

**GitHub:** Surface-Helix-Grundlage mit Auswahl und Erkennung analytischer
Zylinder- und Kegelmantelflächen ergänzt. Der Dialog enthält jetzt die Reiter
„Helix erstellen“, „Einstellungen“ und „Info“ mit Projektlogo und Projektlinks.

- Der Modus „Surface Helix – Flächenprüfung“ prüft einzelne Körperflächen; er erzeugt noch keine Helix und sperrt Ausführen. Konturableitung, Offset und Oberflächenkurve bleiben offen.
- Andere Flächentypen, ungültige und leere Auswahlen erhalten verständliche Hinweise. Die Erkennung des Flächentyps bestätigt noch keine Eignung der beschnittenen Fläche für eine vollständige Helix.
- G1-Option im Einstellungsreiter, weiterhin standardmäßig aktiv und nur für den aktuellen Dialogaufruf.
- Info-Reiter nach der bereitgestellten Layoutvorlage: vorhandenes Logo, Version, Beschreibung, Website, Repository, Releases, Issues, YouTube und MIT-Lizenz.
- Logo als 240-Pixel-Ressource direkt im installierbaren Add-in enthalten (Quelle: `docs/images/Logo_1.png`).
- 56 automatisierte Tests bestanden, einschließlich Flächenauswahl, Moduswechsel, Ausführungssperre und G1-Übergabe aus dem Einstellungsreiter. Darstellung, Links und Moduswechsel müssen noch in Fusion geprüft werden.

## 0.2.3 – 2026-09-28 – Entwicklung

**GitHub:** Option „Tangentiale Übergänge (G1)“ ergänzt. Benachbarte Helix-Splines
erhalten Tangentialbedingungen, um Richtungssprünge an Abschnittsgrenzen beim
Sweep zu vermeiden. Die Option ist standardmäßig aktiviert.

- Ursache sichtbarer Übergänge: gemeinsame Endpunkte ohne angeglichene Tangenten; Steigungs- und Durchmessergradienten können springen.
- Fusion gleicht die Tangenten über `addTangent` an; dabei kann sich die Kurvenform ändern. Keine G2-Krümmungsangleichung.
- Bei fehlgeschlagener Tangentialbedingung wird die gesamte neue Skizze entfernt und die betreffende Abschnittsgrenze gemeldet.
- 50 automatisierte Tests bestanden. Benutzer bestätigt einen besser aussehenden Übergang im Sweep-Beispiel; weitergehende Sonderfälle bleiben offen.
- Vier Screenshots von v0.2.3 mit Sweep-Körper, Helix-Pfad, Abschnittsdialog und Zebraanalyse in beiden Galerien ergänzt; README-Vorschauen aktualisiert. Add-in-Version unverändert.
- G2-Übergänge als möglicher weiterer Ausbau vorgemerkt.

## 0.2.2 – 2026-09-28 – Entwicklung

**GitHub:** Abbruch beim Aufbau des Abschnittsdialogs behoben. Abschnittstitel
werden beim Anlegen gesetzt. Neue Funktion „Achslänge übernehmen“ skaliert die
Helix einmalig auf die Länge einer endlichen Linie oder geraden Körperkante.

- Ursache: Schreibzugriff auf die schreibgeschützte Fusion-Eigenschaft `CommandInput.name`; bisherige Testdoubles waren hier zu großzügig.
- Abschnittsnummern bleiben beim Entfernen anderer Abschnitte stabil; mindestens ein Abschnitt bleibt erhalten.
- Mehrere Abschnittslängen werden proportional verteilt. Unendliche Achsen, Null-/ungültige Längen und überschrittene Kurvenlimits werden abgewiesen.
- 47 automatisierte Tests bestanden, einschließlich Regression für schreibgeschützte Namen. Benutzer bestätigt die grundsätzliche Funktion von 0.2.2.
- Zwei Screenshots von v0.2.2 in beiden Versionsgalerien ergänzt und README-Vorschauen aktualisiert; ältere Bilder bleiben erhalten. Add-in-Version unverändert.
- Surface-Helix-Grundlage zugunsten dieser Fehlerkorrektur und der bereits gewünschten Längenübernahme nachgeordnet.

## 0.2.1 – 2026-09-28 – Entwicklung

**GitHub:** Abschnittsverwaltung im Helix-Dialog integriert. Mehrteilige Helices
mit linear veränderlichem Durchmesser und variabler Steigung erzeugen;
Gesamtlänge und Windungszahl werden direkt angezeigt.

- Bis zu 32 Abschnitte hinzufügen, bearbeiten und entfernen; Startdurchmesser folgen automatisch dem vorherigen Abschnitt.
- Winkel aus der entlang der Achse veränderlichen Steigung berechnet; durchgehende Position und Phase an Abschnittsgrenzen.
- Eine 3D-Skizze mit verbundenen Splines; gemeinsame Endpunkte erhalten mögliche Knicke an Übergängen.
- 42 automatisierte Tests bestanden. Dialog und variable Ausgabe noch in Fusion prüfen.
- Benutzer bestätigt den vorherigen Stand 0.2.0 als lauffähig. Achslängenübernahme bleibt für später vorgemerkt.

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
- Laufende Version 0.2.0 anschließend vom Benutzer bestätigt.
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

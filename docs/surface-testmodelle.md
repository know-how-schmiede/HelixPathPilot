# Surface Helix – Testmodelle und Prüfprotokoll

Referenzstand: **0.3.6**, definiert am 2026-09-29.

Diese Modelle machen die Fusion-Prüfung reproduzierbar. Die grundsätzliche
Funktion wurde vom Benutzer bestätigt; die einzelnen Prüfungen unten sind
noch offen. Es werden hier Modellbauanleitungen bereitgestellt, keine bereits
erzeugten oder geprüften Fusion-Dateien.

## Modelle vorbereiten

Ein neues Design mit Millimeter als Längeneinheit verwenden. Jedes Modell in
einer eigenen benannten Komponente erstellen. Maße sind in mm angegeben.
Körper zunächst ohne Fasen, Rundungen oder zusätzliche Flächenteilungen bauen.
Für jede Variante eine Kopie des Ausgangsmodells verwenden.

| ID / Komponentenname | Aufbau | Zu wählende Fläche / Zweck |
| --- | --- | --- |
| Z01_Zylinder | Kreis R=10 auf XY, 50 entlang +Z extrudieren | Vollständiger äußerer Zylindermantel; Basisfall |
| K01_Kegelstumpf | In XZ das Profil (Radius, Höhe) (0,0), (20,0), (10,50), (0,50) schließen und 360° um Z drehen | Kegelmantel mit Kreisrändern R=20 und R=10; Basisfall |
| Z02_Innenmantel | Konzentrische Kreise R=15 und R=10 auf XY; Ringfläche 50 extrudieren | Innerer Zylindermantel R=10; Offset unabhängig von Körperaußennormale |
| K02_Schraeg | Kopie von K01 als Komponente; um globale X-Achse 35° drehen, danach um (80,30,20) verschieben | Mantel; Raumlage und Transformation |
| Z03_Verschachtelt | Z01 in eine Unterkomponente einer neuen Elternkomponente kopieren; Elternkomponente um globale Y-Achse 30° drehen und um (40,80,20) verschieben | Mantel über die verschachtelte Instanz auswählen; Ausgabe in Hauptkomponente |
| N01_Halbmantel | Halbkreis R=10 als geschlossene Fläche 50 extrudieren | Gekrümmter 180°-Mantel; muss abgelehnt werden |
| N02_Querbohrung | Kopie von Z01; mittig bei Z=25 eine Querbohrung Ø=4 entlang X vollständig durch den Körper schneiden | Äußerer Mantel mit zusätzlichen Randkonturen; muss abgelehnt werden |
| N03_SchraegerAnschnitt | Kopie von Z01; mit einer um X geneigten Ebene durch (0,0,40) teilen (Neigung 15° gegenüber XY), oberen Teil entfernen | Verbleibender Mantel mit elliptischem Rand; muss abgelehnt werden |
| N04_Kegelspitze | Dreieck (Radius, Höhe) (0,0), (20,0), (0,50) in XZ um Z drehen | Kegelmantel mit Spitze statt zweitem Kreisrand; muss abgelehnt werden |
| N05_Kugel | Halbkreis R=10 um seinen Durchmesser drehen | Kugelfläche; nicht unterstützter Flächentyp |

Die Reihenfolge der angezeigten Flächenradien folgt der von Fusion gelieferten
Flächenachse. Für K01 den Startrand so wählen, dass die **Helixradien** vom
großen zum kleinen Rand laufen. Bei Offset 0 entspricht dies 20 → 10 mm.
Die geometrischen Maße bleiben bei schrägen und verschachtelten Varianten gleich.

## Sollwerte und Durchführung

Standard, sofern nicht anders angegeben: Startwinkel 0°, rechtsdrehend,
Offset 0, Live-Vorschau ein. Steigungen sind axiale Werte in mm pro Windung.
Jede gültige Prüfung mit OK abschließen und die fertige Skizze prüfen.
Zum Vergleichen Körper bei Bedarf transparent darstellen oder ausblenden.

| Fall | Modell und Eingaben | Erwartetes Ergebnis | Status |
| --- | --- | --- | --- |
| S01 | Z01, Steigung 5 → 5 | Länge 50; Helixradius 10; 10,000 Windungen | offen |
| S02 | Z01, 5 → 10 | 6,931 Windungen; Abstände nehmen in Laufrichtung zu | offen |
| S03 | Z01, 10 → 5 | 6,931 Windungen; Abstände nehmen in Laufrichtung ab | offen |
| S04 | Z01, 5 → 5, Offset +2 / −2 | Radius 12 / 8; jeweils 10,000 Windungen, gleiche axiale Endlagen | offen |
| S05 | K01, 5 → 10 | 6,931 Windungen; Radius 20 → 10; Start und Ende an den gewählten Rändern | offen |
| S06 | K01, 5 → 10, Offset +2 | Helixradien 21,961 → 11,961; beide Endpunkte um 0,392 entlang der Richtung vom großen zum kleinen Rand verschoben | offen |
| S07 | K01, 10 → 5, Offset −2 | Helixradien 18,039 → 8,039; beide Endpunkte um 0,392 entgegen der Richtung vom großen zum kleinen Rand verschoben; 6,931 Windungen | offen |
| S08 | S06, anderen Startrand wählen | Radien 11,961 → 21,961; Steigung weiterhin 5 am neuen Start und 10 am neuen Ende; 6,931 Windungen | offen |
| S09 | Z01, 5 → 10; Linksdrall, dann Startwinkel 90° | Windungszahl und Radien unverändert; entgegengesetzter Umlaufsinn, danach Vierteldrehung um die Achse relativ zum Startwinkel 0° | offen |
| S10 | Z02, 5 → 5, Offset +2 / −2 | Radius 12 / 8; positiver Offset zeigt auch an der Innenfläche von der Achse weg | offen |
| S11 | K02, Eingaben wie S06 | Gleiche Längen, Radien, Windungszahl und Normalabstände wie S06, passend zur schrägen Modellachse | offen |
| S12 | Z03, Eingaben wie S02 | Helix folgt der transformierten Instanz; genau eine Skizze in der Hauptkomponente | offen |
| S13 | Z01, 40 → 40 | 1,250 Windungen; Endpunkt am zweiten Rand, Viertelwindung gegenüber Start versetzt | offen |
| S14 | Z01, 0,390625 → 0,390625, danach 0,39 → 0,39 | 128 Windungen zulässig; zweiter Wert überschreitet das Limit und wird abgelehnt | offen |

Dialogwerte auf 0,001 mm bzw. 0,001 Windungen gerundet vergleichen.
Die Offset-Sollwerte beschreiben die mathematischen Endpunkte. Die ausgegebene
Spline ist zwischen ihren Stützpunkten eine Näherung; daraus wird keine
garantierte globale Abstandstoleranz abgeleitet. Sichtbare Abweichungen mit
Messstelle und Screenshot protokollieren.

Unabhängige Berechnungsgrundlage: Für konstante Steigung p ist die Windungszahl
L/p. Für linear veränderliche Steigung p₀ → p₁ ist sie
L · ln(p₁/p₀) / (p₁−p₀). Beim K01 gilt in Richtung vom großen zum kleinen
Rand k=(10−20)/50=−0,2. Bei Normaloffset d sind die Verschiebungen
Δr=d/√(1+k²) und Δz=−d·k/√(1+k²). Offset verändert die Windungszahl nicht.

## Ablehnung und Dialogverhalten

| Fall | Durchführung | Erwartetes Ergebnis | Status |
| --- | --- | --- | --- |
| V01 | N01 bis N05 jeweils auswählen; zusätzlich ebene Stirnfläche von Z01 auswählen | Verständlicher Ablehnungshinweis; OK gesperrt; keine alte Vorschau | offen |
| V02 | Gültige Z01-Auswahl entfernen | Auswahlhinweis; OK gesperrt; Vorschau entfernt | offen |
| V03 | Z01: Start- und Endsteigung einzeln auf 0, −1 oder ungültigen Ausdruck setzen; danach gültigen Wert wiederherstellen | Ungültige Eingabe sperrt OK und entfernt Vorschau; gültiger Wert stellt beides wieder her | offen |
| V04 | Z01: Offset −10 und −11; K01: Offset −11 | Erreichen/Überschreiten der Achse wird abgelehnt | offen |
| V05 | S02: Vorschau aus/ein; Surface → parametrisch → Surface wechseln | Grafik passend zum Modus; keine liegen gebliebene Vorschau; Surface-Werte bleiben während des Dialogs erhalten | offen |
| V06 | S02: abbrechen, erneut öffnen und erstellen, dann rückgängig | Abbrechen hinterlässt keine Skizze; OK erzeugt genau eine Surface-Helix-Skizze; Rückgängig entfernt sie | offen |
| V07 | S05 mit G1 ein und aus erstellen | Jeweils eine Surface-Spline; G1 hat im Surface-Modus keine Wirkung | offen |

## Ergebnisse erfassen

Pro Durchlauf Fusion-Version, Betriebssystem, Add-in-Version und Datum notieren.
Modelle bei Bedarf als `Surface-Testmodelle.f3d` archivieren; dieser Dateiname
bezeichnet eine künftig zu speichernde Datei, keinen vorhandenen Download.

| Datum / Prüfer | Fall | Ist-Ergebnis / Messwerte | Bestanden / Fehler | Modell / Screenshot / Issue |
| --- | --- | --- | --- | --- |
| — | — | Noch kein vollständiger Durchlauf protokolliert | offen | — |

Erst nach erfolgreicher Prüfung aller Fälle und Klärung gemeldeter Abweichungen
den Ablaufplanpunkt „erste stabile Surface-Helix-Version testen“ abschließen.
Automatisierte Kern- und Adaptertests ergänzen diese Prüfung, ersetzen jedoch
nicht Fusions Geometrie-, Vorschau- und Rückgängig-Verhalten.

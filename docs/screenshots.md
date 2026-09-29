# HelixPathPilot screenshots

[Project overview](../README.md) · [Deutsch](screenshots-DE.md)

Screenshots are grouped by the version they show, newest first. Each version
documents its own UI and capabilities; it does not necessarily match the current
development version. The Fusion interface in these screenshots is German.

## Versions

- [v0.4.1](#v041) — preset selection and a loaded variable helix
- [v0.3.5](#v035) — variable Surface Helix pitch on cylinders and cones
- [v0.3.4](#v034) — Surface Offset previews with positive and negative distances
- [v0.3.3](#v033) — Surface Helix on cylinders and cones, previews and application examples
- [v0.2.3](#v023) — tangent transitions, three-section example and zebra analysis
- [v0.2.2](#v022) — application example and section editor
- [v0.1.2](#v012) — axis alignment, parameter dialog, menu and toolbar

## v0.4.1

### Selecting a built-in preset

The open list shows all three presets: “Basishelix 20 × 50 mm”,
“Surface 5 → 10 mm” and “Zwei variable Abschnitte”. Click **Vorlage laden**
(Load preset) to apply the selected parameters; selection alone changes no values.

![HelixPathPilot v0.4.1 preset list showing the three built-in parametric and Surface presets](images/screenshots/v0-4-1/HelixPathPilot_v0-4-1_-01.png)

### Loaded preset with edited sections

The message “Geladen: Zwei variable Abschnitte” confirms that the preset was
loaded. The preview shows subsequently adjusted values: two sections of 50 mm
each, diameters 10 → 30 → 10 mm and pitches 5 → 10 → 5 mm. These values differ
from the packaged preset. Section numbers 3 and 4 reflect the continuing
numbering within the dialog session.

![Loaded variable preset in HelixPathPilot v0.4.1 with two edited sections and a helix preview](images/screenshots/v0-4-1/HelixPathPilot_v0-4-1_-00.png)

The user has confirmed that preset selection and loading work in Fusion.

## v0.3.5

### Increasing pitch on a cylinder

The preview shows a start pitch of 5 mm and an end pitch of 30 mm over an axial
length of 110 mm. A +5 mm offset gives a helix radius of 55 mm; the dialog shows
7.884 turns. Coil spacing increases along the direction of travel.

![Surface Helix v0.3.5 dialog and cylinder preview with 5 → 30 mm pitch and a 5 mm offset](images/screenshots/v0.3.5/HelixPathPilot_v0-3-5_-00.png)

### Decreasing pitch on a cone

Pitch decreases from 20 mm to 2 mm. With an axial length of 60 mm and a +5 mm
normal offset, the dialog shows 7.675 turns and helix radii of
54.472 → 24.472 mm. The coils become more closely spaced toward the narrow end.

![Surface Helix v0.3.5 dialog and cone preview with 20 → 2 mm pitch and a 5 mm offset](images/screenshots/v0.3.5/HelixPathPilot_v0-3-5_-01.png)

The user has confirmed that variable Surface Helix pitch works in Fusion.

## v0.3.4

### Positive offset on a cylinder

The preview shows a helix 10 mm away from the cylindrical face. The face radius
is 50 mm and the helix radius is 60 mm. An axial length of 110 mm and a pitch
of 20 mm produce 5.5 turns.

![Surface Helix v0.3.4 cylinder preview with a 10 mm offset and 60 mm helix radius](images/screenshots/v0-3-4/HelixPathPilot_v0-3-4_-00.png)

### Negative offset on a cone

A normal offset of −5 mm places the helix inside the transparent conical face.
Face radii are 35 → 5 mm; displayed helix radii are 30.528 → 0.528 mm.
An axial length of 60 mm and a pitch of 10 mm produce six turns.

![Surface Helix preview inside a transparent truncated cone with a negative 5 mm offset](images/screenshots/v0-3-4/HelixPathPilot_v0-3-4_-01.png)

### Positive offset on a cone

A normal offset of +5 mm moves the helix outward. The dialog shows face radii
of 50 → 20 mm and helix radii of 54.472 → 24.472 mm. On a cone, the radial
change is smaller than the perpendicular distance.

![Surface Helix preview outside a truncated cone with a positive 5 mm offset](images/screenshots/v0-3-4/HelixPathPilot_v0-3-4_-02.png)

The user has confirmed the offset feature and preview, including negative
distances from the face.

## v0.3.3

### Surface Helix on a cylinder

Selected cylindrical face with helix preview and dialog: 110 mm axial length,
50 mm radius, 10 mm pitch and 11 turns. The start angle is −45°.

![HelixPathPilot v0.3.3 Surface Helix dialog and cylinder preview with 11 turns](images/screenshots/v0-3-3/HelixPathPilot_v0-3-3_-00.png)

### Surface Helix on a truncated cone

The dialog shows a 60 mm axial length, radii changing from 50 to 20 mm and six
turns at a pitch of 10 mm. The selected face and preview path are visible in the model.

![Surface Helix v0.3.3 dialog with a conical face, six turns and radii from 50 to 20 mm](images/screenshots/v0-3-3/HelixPathPilot_v0-3-3_-03.png)

### Applications of the generated paths

These examples show a helical groove on a truncated cone, a magenta winding
with a rectangular cross-section around a cone and a round-section winding
around a cylinder. HelixPathPilot generates sketch paths; the illustrated
bodies and grooves are created in subsequent modeling steps in Fusion.

![Truncated cone with a helical groove using a Surface Helix path](images/screenshots/v0-3-3/HelixPathPilot_v0-3-3_-01.png)

![Magenta rectangular-section winding around a green truncated cone](images/screenshots/v0-3-3/HelixPathPilot_v0-3-3_-02.png)

![Magenta round-section winding around a green cylinder](images/screenshots/v0-3-3/HelixPathPilot_v0-3-3_-04.png)

The user has confirmed that basic Surface Helix generation works in Fusion.

## v0.2.3

### Sweep body and helix path

A three-section helix with changing diameter and pitch, shown as a sketch path
and as a subsequently modeled sweep body in Fusion. Body creation is a separate
modeling step.

| Sweep body | Helix path with fit points |
| --- | --- |
| <img src="images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-00.png" alt="Three-section swept body with tapered ends" width="200"> | <img src="images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-01.png" alt="Corresponding helix sketch path and spline fit points" width="200"> |

### Three-section dialog with G1 enabled

**Tangentiale Übergänge (G1)** is enabled. The example uses three sections of
50 mm each, a total axial length of 150 mm and a displayed turn count of 35.541.

![HelixPathPilot v0.2.3 dialog with three sections and tangent transitions enabled](images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-02.png)

### Transition detail with zebra analysis

The red arrow marks a section transition on the swept body. The user reports an
improved transition after enabling G1. The zebra view documents the appearance
of this example; it does not establish G2 curvature continuity.

![Zebra analysis of the swept helix with a red arrow marking the improved section transition](images/screenshots/c0-2-3/HelixPathPilot_v0-2-3_-03.png)

## v0.2.2

### Application example

A spring-shaped body with varying coil spacing around an inclined axis, alongside
helix sketch geometry. HelixPathPilot generates the sketch paths; body creation
is a separate modeling step in Fusion.

![Spring-shaped body with varying coil spacing and helix sketch geometry in Fusion](images/screenshots/v0-2-2/HelixPathPilot_v0-2-2_-00.png)

### Section editor

The complete dialog with **Section 1**, start/end diameter and pitch, section
controls, total length and turn count. **Achslänge übernehmen** (use axis length)
is disabled here because no finite line or edge is selected.

![HelixPathPilot v0.2.2 section editor showing one section, 50 mm total length and 10 turns](images/screenshots/v0-2-2/HelixPathPilot_v0-2-2_-01.png)

## v0.1.2

### Helices aligned with an inclined axis

Helix curves and their spline fit points around an inclined line in the Fusion viewport.

![Helix curves and fit points around an inclined axis](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-00.png)

### Parameter dialog

Optional axis selection, axis reversal, diameter, axial length, pitch, start angle
and handedness. Without an axis selection, the global Z axis is used.

![HelixPathPilot v0.1.2 dialog with axis selection and helix parameters](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-01.png)

### Create menu

The versioned **HelixPathPilot v0.1.2** entry and its helix icon under
**Solid → Create** (German UI: **Volumenkörper → Erstellen**).

![HelixPathPilot v0.1.2 in the Solid Create menu](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-02.png)

### Toolbar icon

The helix icon provides direct access from the Create toolbar panel.

![HelixPathPilot helix icon in the Create toolbar panel](images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-03.png)

## Adding future versions

Store original screenshots in `docs/images/screenshots/v<major>-<minor>-<patch>/`.
Add a version section and a contents link to both this document and
[the German gallery](screenshots-DE.md), with short captions and descriptive alt text.
Keep earlier version sections and their images. The READMEs contain one selected
preview and a gallery link; update that preview and its version label when appropriate.

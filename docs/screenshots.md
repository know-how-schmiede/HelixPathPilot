# HelixPathPilot screenshots

[Project overview](../README.md) · [Deutsch](screenshots-DE.md)

Screenshots are grouped by the version they show, newest first. Each version
documents its own UI and capabilities; it does not necessarily match the current
development version. The Fusion interface in these screenshots is German.

## Versions

- [v0.2.3](#v023) — tangent transitions, three-section example and zebra analysis
- [v0.2.2](#v022) — application example and section editor
- [v0.1.2](#v012) — axis alignment, parameter dialog, menu and toolbar

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

# HelixPathPilot
<p align="center">
  <img src="docs/images/banner.png" alt="HelixPathPilot Banner">
</p>

**HelixPathPilot** is an Autodesk Fusion add-in for creating parametric and surface-driven helix curves.

The project is intended to provide significantly more flexibility than a conventional helix with constant pitch and diameter. Planned capabilities include variable pitch, variable diameter, multiple helix sections, surface-driven helices on rotational bodies, live preview and reusable presets.

## Planned Main Features

- Parametric helix generation
- Selectable helix axis
- Configurable length, pitch and diameter
- Right-handed and left-handed helices
- Configurable start angle
- Multiple helix sections
- Variable diameters
- Variable pitch
- Linear and later smooth transitions
- Live preview in the Fusion viewport
- Generation as a 3D sketch
- Surface Helix on rotational bodies
- Configurable surface offset
- Save, load, import and export presets
- Future sweep / spring body generation

## Working Modes

### Parametric Helix

The helix is fully defined by parameters such as diameter, pitch, length, handedness and start angle.

Multiple sections may use different start and end values for diameter and pitch.

### Surface Helix

A rotational body or its surface is used as the geometric driver. The helix follows the body contour and can optionally be created with a configurable offset from the surface.

This mode is especially useful for complex spring shapes, tapered windings and other helices with continuously varying radius.

## Presets

Helix configurations can be saved under user-defined names.

A JSON-based exchange format is planned:

```text
*.helixpilot.json
```

This allows presets to be archived, versioned with Git and transferred between installations.

## Possible Use Cases

- Compression springs
- Conical and progressive springs
- Wire forms
- Heating coils
- Spiral hoses
- Cable windings
- Augers and screw conveyor paths
- Decorative helices
- Parametric sweep paths
- Special geometries for additive manufacturing

## Project Status

Development version **0.2.1** lives in `Fusion_addin/HelixPathPilot/`.
**Solid → Create → HelixPathPilot v0.2.1** creates a 3D sketch around a selected axis.
Add or remove up to 32 sections with individual lengths, start/end diameters
and start/end pitches. Handedness and start angle apply to the whole helix.
Construction axes, straight edges and sketch lines are supported, with global Z
as the default. The user confirmed the basic command, axis selection and icons work.
The segment editor and variable helix output are implemented and covered by
automated tests; runtime validation of 0.2.1 in Fusion is still pending.
The top-level `HelixPathPilot/` folder is the inactive 0.1.0 scaffold.

See [development setup and smoke checks](docs/development.md) for loading the add-in in Fusion.

Features and user interface details may change during development.

## Screenshots

Helices aligned with an inclined axis in **v0.1.2**:

[![Helix curves around an inclined axis in Fusion, version 0.1.2](docs/images/screenshots/v0-1-2/HelixPathPilot_v0-1-2_-00.png)](docs/screenshots.md#v012)

See the [versioned screenshot gallery](docs/screenshots.md) for the parameter dialog,
Create menu and toolbar. Screenshots document the version shown; newer versions
may look different.

## Additional Project Documents

Additional project documentation is available in the `docs/` folder:

- [CodeX Plan](docs/codex_plan.md) – implementation rules and development workflow
- [Implementation Plan](docs/ablaufplan.md) – planned implementation path with version milestones
- [Timeline](docs/timeline.md) – traceable project history and change log

The README is intentionally focused on the project overview. Detailed planning and development progress are maintained in the linked documents above.

## Author

**Know-How-Schmiede**

- Website: https://www.know-how-schmiede.de
- YouTube: https://www.youtube.com/@knowhowschmiede
- GitHub: https://github.com/know-how-schmiede

## Disclaimer

HelixPathPilot is an independent project and is not officially affiliated with Autodesk.

Autodesk and Fusion are trademarks or registered trademarks of their respective owners.

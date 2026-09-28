# HelixPathPilot

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

HelixPathPilot is currently in the concept and development phase.

Features and user interface details may change during development.

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

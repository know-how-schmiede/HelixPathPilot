"""Fusion adapter for the sampled helix, in root-component coordinates."""

import adsk.core

from ...core.helix_math import helix_points


def create_sketch(design, parameters):
    coordinates = helix_points(parameters)
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    try:
        sketch.name = 'HelixPathPilot – Helix'
        points = adsk.core.ObjectCollection.create()
        for xyz in coordinates:
            points.add(sketch.modelToSketchSpace(adsk.core.Point3D.create(*xyz)))
        spline = sketch.sketchCurves.sketchFittedSplines.add(points)
        if spline is None:
            raise RuntimeError('Fusion konnte die Helix-Spline nicht erzeugen.')
        return sketch
    except Exception:
        # Do not leave an empty sketch when spline creation fails.
        sketch.deleteMe()
        raise

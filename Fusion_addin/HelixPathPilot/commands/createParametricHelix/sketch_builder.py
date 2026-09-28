"""Fusion adapter for the sampled helix, in root-component coordinates."""

import adsk.core

from ...core.helix_math import helix_points
from ...core.axis import AxisFrame
from ...core.helix_segments import SegmentedHelix
from ...core.variable_helix import segmented_points


def create_sketch(design, parameters, axis=None):
    sections = segmented_points(parameters) if isinstance(parameters, SegmentedHelix) else [helix_points(parameters)]
    coordinates = [(axis or AxisFrame()).transform(points) for points in sections]
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    try:
        sketch.name = 'HelixPathPilot – Helix'
        previous_endpoint = None
        for section in coordinates:
            points = adsk.core.ObjectCollection.create()
            for index, xyz in enumerate(section):
                if index == 0 and previous_endpoint is not None:
                    points.add(previous_endpoint)
                else:
                    points.add(sketch.modelToSketchSpace(adsk.core.Point3D.create(*xyz)))
            spline = sketch.sketchCurves.sketchFittedSplines.add(points)
            if spline is None:
                raise RuntimeError('Fusion konnte die Helix-Spline nicht erzeugen.')
            previous_endpoint = spline.endSketchPoint
        return sketch
    except Exception:
        # Do not leave an empty sketch when spline creation fails.
        sketch.deleteMe()
        raise

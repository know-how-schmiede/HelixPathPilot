"""Fusion adapter for the sampled helix, in root-component coordinates."""

import adsk.core

from ...core.helix_math import helix_points
from ...core.axis import AxisFrame
from ...core.helix_segments import SegmentedHelix
from ...core.variable_helix import segmented_points


def create_sketch(design, parameters, axis=None, tangent_joins=False):
    sections = segmented_points(parameters) if isinstance(parameters, SegmentedHelix) else [helix_points(parameters)]
    coordinates = [(axis or AxisFrame()).transform(points) for points in sections]
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    try:
        sketch.name = 'HelixPathPilot – Helix'
        previous_endpoint = None
        splines = []
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
            splines.append(spline)
        if tangent_joins:
            # Apply after all splines exist so the solver sees the complete chain.
            for index, (first, second) in enumerate(zip(splines, splines[1:]), 1):
                try:
                    constraint = sketch.geometricConstraints.addTangent(first, second)
                    if constraint is None:
                        raise RuntimeError('Fusion hat keine Tangentialbedingung erzeugt.')
                except Exception as error:
                    raise RuntimeError(
                        f'Tangentialer Übergang zwischen Abschnitt {index} und {index + 1} '
                        'konnte nicht erzeugt werden. Bitte Steigungen und Durchmesserverläufe '
                        'angleichen oder „Tangentiale Übergänge (G1)“ deaktivieren.'
                    ) from error
        # Keep all fit points for accuracy, but display only section boundaries.
        # Unconnected sketch points remain visible when arePointsShown is false.
        # Read actual endpoints after G1 solving, in sketch coordinates.
        sketch.arePointsShown = False
        boundaries = [splines[0].startSketchPoint] + [s.endSketchPoint for s in splines]
        for endpoint in boundaries:
            marker = sketch.sketchPoints.add(endpoint.geometry)
            if marker is None:
                raise RuntimeError('Abschnittsmarkierung konnte nicht erzeugt werden.')
        return sketch
    except Exception:
        # Do not leave an empty sketch when spline creation fails.
        sketch.deleteMe()
        raise

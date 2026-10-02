"""Fusion adapter for the sampled helix, in root-component coordinates."""

from ...i18n import tr

import adsk.core

from ...core.helix_math import helix_points
from ...core.axis import AxisFrame
from ...core.helix_segments import SegmentedHelix
from ...core.variable_helix import segmented_points
from ...core.cleanup import cleanup_created


def create_sketch(design, parameters, axis=None, tangent_joins=False):
    sections = segmented_points(parameters) if isinstance(parameters, SegmentedHelix) else [helix_points(parameters)]
    coordinates = [(axis or AxisFrame()).transform(points) for points in sections]
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    try:
        sketch.name = tr('HelixPathPilot – Helix')
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
                raise RuntimeError(tr('Fusion could not create the helix spline.'))
            previous_endpoint = spline.endSketchPoint
            splines.append(spline)
        if tangent_joins:
            # Apply after all splines exist so the solver sees the complete chain.
            for index, (first, second) in enumerate(zip(splines, splines[1:]), 1):
                try:
                    constraint = sketch.geometricConstraints.addTangent(first, second)
                    if constraint is None:
                        raise RuntimeError(tr('Fusion did not create a tangent constraint.'))
                except Exception as error:
                    raise RuntimeError(
                        tr(
                            'Could not create a tangent join between sections {p0} and {p1}. '
                            'Please align pitch and diameter transitions or disable “Tangent '
                            'joins (G1)”.', p0=index, p1=index + 1)
                    ) from error
        # Keep all fit points for accuracy, but display only section boundaries.
        # Unconnected sketch points remain visible when arePointsShown is false.
        # Read actual endpoints after G1 solving, in sketch coordinates.
        sketch.arePointsShown = False
        boundaries = [splines[0].startSketchPoint] + [s.endSketchPoint for s in splines]
        for endpoint in boundaries:
            marker = sketch.sketchPoints.add(endpoint.geometry)
            if marker is None:
                raise RuntimeError(tr('Could not create the section marker.'))
        return sketch
    except Exception as error:
        # Do not leave an empty sketch when spline creation fails.
        cleanup_created([(tr('Helix sketch'), sketch)], error)
        raise

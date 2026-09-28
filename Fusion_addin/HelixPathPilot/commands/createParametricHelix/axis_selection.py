"""Convert selected Fusion geometry to a frame in root-component space."""

import adsk.core
import adsk.fusion
import math

from ...core.axis import AxisFrame


def selected_axis_length(selection_input):
    """Return a finite straight line's length in cm; infinite axes have no length."""
    if selection_input.selectionCount != 1:
        raise ValueError('Bitte eine endliche Skizzenlinie oder gerade Körperkante auswählen.')
    entity = selection_input.selection(0).entity
    if not entity.isValid:
        raise ValueError('Die gewählte Linie ist nicht mehr gültig.')
    if not (adsk.fusion.SketchLine.cast(entity) or adsk.fusion.BRepEdge.cast(entity)):
        raise ValueError('Unendliche Konstruktionsachsen haben keine übernehmbare Länge.')
    # For finite lines selected_axis keeps the full endpoint vector, not a unit vector.
    frame = selected_axis(selection_input)
    length = math.hypot(*frame.direction)
    if not math.isfinite(length) or length <= 0:
        raise ValueError('Die gewählte Linie muss eine positive, endliche Länge haben.')
    return length


def selected_axis(selection_input, reverse=False):
    if selection_input.selectionCount == 0:
        frame = AxisFrame()
    else:
        entity = selection_input.selection(0).entity
        if not entity.isValid:
            raise ValueError('Die gewählte Achse ist nicht mehr gültig.')
        axis = adsk.fusion.ConstructionAxis.cast(entity)
        sketch_line = adsk.fusion.SketchLine.cast(entity)
        edge = adsk.fusion.BRepEdge.cast(entity)
        if axis:
            # Proxy geometry already includes its assembly context.
            geometry = axis.geometry
            origin, direction = geometry.origin, geometry.direction
        elif sketch_line:
            geometry = sketch_line.worldGeometry
            origin = geometry.startPoint
            direction = origin.vectorTo(geometry.endPoint)
        elif edge:
            geometry = adsk.core.Line3D.cast(edge.geometry)
            if geometry is None:
                raise ValueError('Bitte eine gerade Modellkante auswählen.')
            origin = geometry.startPoint
            direction = origin.vectorTo(geometry.endPoint)
        else:
            raise ValueError('Bitte eine Konstruktionsachse, gerade Kante oder Skizzenlinie auswählen.')
        frame = AxisFrame(tuple(origin.asArray()), tuple(direction.asArray()))
    if reverse:
        frame = frame.reversed()
    frame.basis()
    return frame

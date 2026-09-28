"""Convert selected Fusion geometry to a frame in root-component space."""

import adsk.core
import adsk.fusion

from ...core.axis import AxisFrame


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

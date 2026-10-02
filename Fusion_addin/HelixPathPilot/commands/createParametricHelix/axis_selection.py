"""Convert selected Fusion geometry to a frame in root-component space."""

from ...i18n import tr

import adsk.core
import adsk.fusion
import math

from ...core.axis import AxisFrame


def selected_axis_length(selection_input):
    """Return a finite straight line's length in cm; infinite axes have no length."""
    if selection_input.selectionCount != 1:
        raise ValueError(tr('Please select a finite sketch line or straight body edge.'))
    entity = selection_input.selection(0).entity
    if not entity.isValid:
        raise ValueError(tr('The selected line is no longer valid.'))
    if not (adsk.fusion.SketchLine.cast(entity) or adsk.fusion.BRepEdge.cast(entity)):
        raise ValueError(tr('Infinite construction axes have no usable length.'))
    # For finite lines selected_axis keeps the full endpoint vector, not a unit vector.
    frame = selected_axis(selection_input)
    length = math.hypot(*frame.direction)
    if not math.isfinite(length) or length <= 0:
        raise ValueError(tr('The selected line must have a positive, finite length.'))
    return length


def selected_axis(selection_input, reverse=False):
    if selection_input.selectionCount == 0:
        frame = AxisFrame()
    else:
        entity = selection_input.selection(0).entity
        if not entity.isValid:
            raise ValueError(tr('The selected axis is no longer valid.'))
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
                raise ValueError(tr('Please select a straight model edge.'))
            origin = geometry.startPoint
            direction = origin.vectorTo(geometry.endPoint)
        else:
            raise ValueError(tr('Please select a construction axis, straight edge or sketch line.'))
        frame = AxisFrame(tuple(origin.asArray()), tuple(direction.asArray()))
    if reverse:
        frame = frame.reversed()
    frame.basis()
    return frame

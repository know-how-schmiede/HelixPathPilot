"""Initial surface eligibility check; does not generate a surface helix yet."""

from ...i18n import tr

import adsk.core
import adsk.fusion

from ...core.axis import AxisFrame
from ...core.surface_profile import profile_from_rings


def selected_surface_kind(selection):
    if selection.selectionCount != 1:
        raise ValueError(tr('Please select a cylindrical or conical lateral face.'))
    entity = selection.selection(0).entity
    if not entity.isValid:
        raise ValueError(tr('The selected face is no longer valid.'))
    face = adsk.fusion.BRepFace.cast(entity)
    if face is None:
        raise ValueError(tr('Please select a single lateral face of the body.'))
    kind = face.geometry.surfaceType
    if kind == adsk.core.SurfaceTypes.CylinderSurfaceType:
        return tr('Cylindrical lateral face')
    if kind == adsk.core.SurfaceTypes.ConeSurfaceType:
        return tr('Conical lateral face')
    raise ValueError(tr(
        'Only analytical cylindrical and conical lateral faces are currently recognized. Planar, '
        'spherical, toroidal and freeform faces are not yet supported.'))


def selected_surface_profile(selection):
    """Use actual face rims, not an axis-aligned bounding box or unbounded surface."""
    selected_surface_kind(selection)
    face = adsk.fusion.BRepFace.cast(selection.selection(0).entity)
    surface = face.geometry
    axis = AxisFrame(tuple(surface.origin.asArray()), tuple(surface.axis.asArray()))
    rings = []
    for edge in face.edges:
        curve = edge.geometry
        circle = adsk.core.Circle3D.cast(curve)
        if circle is not None:
            rings.append((tuple(circle.center.asArray()), tuple(circle.normal.asArray()), circle.radius))
        elif adsk.core.Line3D.cast(curve) is None:
            raise ValueError(tr(
                'Only complete circular boundaries and straight lateral seams are supported; '
                'partial faces and additional cutouts are not suitable.'))
    return profile_from_rings(axis, rings, face.area,
        cylinder=surface.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType)

"""Initial surface eligibility check; does not generate a surface helix yet."""

import adsk.core
import adsk.fusion

from ...core.axis import AxisFrame
from ...core.surface_profile import profile_from_rings


def selected_surface_kind(selection):
    if selection.selectionCount != 1:
        raise ValueError('Bitte eine Zylinder- oder Kegelmantelfläche auswählen.')
    entity = selection.selection(0).entity
    if not entity.isValid:
        raise ValueError('Die gewählte Fläche ist nicht mehr gültig.')
    face = adsk.fusion.BRepFace.cast(entity)
    if face is None:
        raise ValueError('Bitte eine einzelne Mantelfläche des Körpers auswählen.')
    kind = face.geometry.surfaceType
    if kind == adsk.core.SurfaceTypes.CylinderSurfaceType:
        return 'Zylindermantelfläche'
    if kind == adsk.core.SurfaceTypes.ConeSurfaceType:
        return 'Kegelmantelfläche'
    raise ValueError('Aktuell werden nur analytische Zylinder- und Kegelmantelflächen erkannt. '
                     'Ebene, Kugel-, Torus- und Freiformflächen werden noch nicht unterstützt.')


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
            raise ValueError('Nur vollständige Kreisränder und gerade Mantelnähte werden unterstützt; '
                             'Teilflächen und zusätzliche Ausschnitte sind nicht geeignet.')
    return profile_from_rings(axis, rings, face.area,
        cylinder=surface.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType)

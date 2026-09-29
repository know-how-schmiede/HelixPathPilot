"""Initial surface eligibility check; does not generate a surface helix yet."""

import adsk.core
import adsk.fusion


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

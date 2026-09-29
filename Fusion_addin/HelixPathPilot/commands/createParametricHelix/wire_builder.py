"""Check the solved spline chain, then sweep a circular wire as a new body."""

import math

import adsk.core
import adsk.fusion

from ...core.wire_clearance import check_clearance, validate_diameter
from ...core.cleanup import cleanup_created


def _check_path(splines, diameter):
    tolerance = max(1e-7, diameter / 1000)
    points = []
    previous_tangent = None
    for spline in splines:
        evaluator = spline.worldGeometry.evaluator
        ok, start, end = evaluator.getParameterExtents()
        if not ok:
            raise ValueError('Drahtprüfung: Spline-Parameter nicht verfügbar.')
        ok, strokes = evaluator.getStrokes(start, end, tolerance)
        if not ok or len(strokes) < 2:
            raise ValueError('Drahtprüfung: Spline konnte nicht abgetastet werden.')
        if len(points) + len(strokes) > 16000:
            raise ValueError('Drahtprüfung: Pfad zu komplex (maximal 16000 Prüfpunkte).')
        # Check the actual solved spline, including G1 changes, before sweeping.
        count = max(256, len(strokes))
        for i in range(count + 1):
            parameter = start + (end - start) * i / count
            ok, _, curvature = evaluator.getCurvature(parameter)
            if not ok or not math.isfinite(curvature):
                raise ValueError('Drahtprüfung: Krümmung konnte nicht bestimmt werden.')
            if abs(curvature) * (diameter / 2 + tolerance) >= 0.98:
                raise ValueError('Drahtdurchmesser zu groß für die lokale Krümmung. '
                                 'Bitte die Drahtstärke reduzieren.')
        ok, tangent = evaluator.getTangent(start)
        if not ok:
            raise ValueError('Drahtprüfung: Starttangente fehlt.')
        if previous_tangent is not None and previous_tangent.angleTo(tangent) > 1e-3:
            raise ValueError('Drahtkörper benötigt tangentiale Abschnittsübergänge. '
                             'Bitte G1 aktivieren oder die Abschnittswerte angleichen.')
        ok, previous_tangent = evaluator.getTangent(end)
        if not ok:
            raise ValueError('Drahtprüfung: Endtangente fehlt.')
        xyz = [(p.x, p.y, p.z) for p in strokes]
        if points and math.dist(points[-1], xyz[0]) > tolerance:
            raise ValueError('Drahtprüfung: Abschnitte sind nicht verbunden.')
        points.extend(xyz[1:] if points else xyz)
    check_clearance(points, diameter, tolerance)


def create_wire(design, sketch, diameter):
    """Own and clean up auxiliary output; caller owns the input path sketch."""
    validate_diameter(diameter)
    curves = sketch.sketchCurves.sketchFittedSplines
    splines = [curves.item(i) for i in range(curves.count)]
    if not splines:
        raise ValueError('Kein Helixpfad für den Drahtkörper vorhanden.')
    _check_path(splines, diameter)
    root = design.rootComponent
    created = []
    try:
        collection = adsk.core.ObjectCollection.create()
        for spline in splines:
            collection.add(spline)
        path = adsk.fusion.Path.create(collection, adsk.fusion.ChainedCurveOptions.noChainedCurves)
        if path is None:
            raise RuntimeError('Fusion konnte den Sweep-Pfad nicht erstellen.')
        plane_input = root.constructionPlanes.createInput()
        start_path = adsk.fusion.Path.create(splines[0], adsk.fusion.ChainedCurveOptions.noChainedCurves)
        zero = adsk.core.ValueInput.createByReal(0)
        if hasattr(plane_input, 'setByPath'):
            success = plane_input.setByPath(start_path,
                adsk.fusion.PathDistanceTypes.ProportionalPathDistanceType, zero)
        else:
            success = plane_input.setByDistanceOnPath(splines[0], zero)
        if not success:
            raise RuntimeError('Profilebene am Helixanfang konnte nicht erstellt werden.')
        plane = root.constructionPlanes.add(plane_input)
        if plane is None:
            raise RuntimeError('Fusion konnte die Profilebene nicht erstellen.')
        created.append(('Drahtebene', plane))
        plane.name = 'HelixPathPilot – Drahtebene'
        profile_sketch = root.sketches.add(plane)
        if profile_sketch is None:
            raise RuntimeError('Fusion konnte die Profilskizze nicht erstellen.')
        created.append(('Drahtprofil', profile_sketch))
        profile_sketch.name = 'HelixPathPilot – Drahtprofil'
        center = profile_sketch.modelToSketchSpace(splines[0].startSketchPoint.worldGeometry)
        profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(center, diameter / 2)
        if profile_sketch.profiles.count != 1:
            raise RuntimeError('Das Drahtprofil ist nicht geschlossen.')
        sweeps = root.features.sweepFeatures
        sweep_input = sweeps.createInput(profile_sketch.profiles.item(0), path,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweep_input.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        feature = sweeps.add(sweep_input)
        if feature is None:
            raise RuntimeError('Fusion konnte den Draht-Sweep nicht erstellen.')
        created.append(('Draht-Sweep', feature))
        if (feature.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
                or feature.bodies.count != 1 or not feature.bodies.item(0).isSolid):
            raise RuntimeError('Fusion meldet einen ungültigen Drahtkörper. '
                               + feature.errorOrWarningMessage)
        feature.name = 'HelixPathPilot – Draht-Sweep'
        feature.bodies.item(0).name = 'HelixPathPilot – Draht'
        for entity in (plane, profile_sketch, sketch):
            entity.isLightBulbOn = False
        return feature
    except Exception as error:
        cleanup_created(created, error)
        raise RuntimeError('Draht-Sweep fehlgeschlagen: ' + str(error)) from error

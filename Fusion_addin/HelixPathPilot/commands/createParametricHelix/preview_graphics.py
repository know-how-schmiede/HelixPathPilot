"""Transient helix display without sketch entities or constraint solving."""

import adsk.fusion

from ...core.variable_helix import segmented_points


class HelixPreview:
    def __init__(self, design):
        self.design = design
        self.group = None
        self.key = None

    def clear(self):
        if self.group is not None and self.group.isValid:
            self.group.deleteMe()
        self.group = None
        self.key = None

    def show(self, model, axis):
        key = (model, axis)
        if self.group is not None and self.group.isValid and self.key == key:
            return
        self.clear()
        sections = [axis.transform(points) for points in segmented_points(model)]
        points = sections[0] + [p for section in sections[1:] for p in section[1:]]
        coordinates = adsk.fusion.CustomGraphicsCoordinates.create(
            [value for point in points for value in point])
        self.group = self.design.rootComponent.customGraphicsGroups.add()
        try:
            self.group.isSelectable = False
            line = self.group.addLines(coordinates, [], True)
            if line is None:
                raise RuntimeError('Vorschaulinie konnte nicht erzeugt werden.')
            line.weight = 2.0
            boundaries = [0]
            for section in sections:
                boundaries.append(boundaries[-1] + len(section) - 1)
            self.group.addPointSet(coordinates, boundaries,
                adsk.fusion.CustomGraphicsPointTypes.PointCloudCustomGraphicsPointType, '')
            self.key = key
        except Exception:
            self.clear()
            raise

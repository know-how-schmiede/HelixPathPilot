"""Transient helix display without sketch entities or constraint solving."""

from ...i18n import tr

import adsk.core
import adsk.fusion

from ...core.variable_helix import segmented_points
from ...core.preview_colors import section_color


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

    def invalidate(self, model, axis):
        """Keep an unchanged preview through inputChanged / executePreview."""
        if self.key != (model, axis):
            self.clear()

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
            boundaries = [0]
            for index, section in enumerate(sections):
                start = boundaries[-1]
                end = start + len(section) - 1
                line = self.group.addLines(coordinates, list(range(start, end + 1)), True)
                if line is None:
                    raise RuntimeError(tr('Could not create the preview line.'))
                line.weight = 2.0
                line.color = adsk.fusion.CustomGraphicsSolidColorEffect.create(
                    adsk.core.Color.create(*section_color(index), 255))
                boundaries.append(end)
            self.group.addPointSet(coordinates, boundaries,
                adsk.fusion.CustomGraphicsPointTypes.PointCloudCustomGraphicsPointType, '')
            self.key = key
        except Exception:
            self.clear()
            raise

"""Validated segment data for variable helices, without Fusion dependencies.

Lengths share one unit (cm in Fusion); start_angle is in radians. Diameter and
pitch vary linearly with axial distance within each segment, not with angle.
This module defines data only; variable-helix sampling is a separate step.
"""

from ..i18n import tr

from dataclasses import dataclass
import math
from numbers import Real


def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(tr('{p0} must be a finite number.', p0=label))


def _positive(value, label):
    _finite(value, label)
    if value <= 0:
        raise ValueError(tr('{p0} must be greater than zero.', p0=label))


@dataclass(frozen=True)
class HelixSegment:
    length: float
    diameter_start: float
    diameter_end: float
    pitch_start: float
    pitch_end: float

    def __post_init__(self):
        for name, value in (
            (tr('Section length'), self.length),
            (tr('Start diameter'), self.diameter_start),
            (tr('End diameter'), self.diameter_end),
            (tr('Start pitch'), self.pitch_start),
            (tr('End pitch'), self.pitch_end),
        ):
            _positive(value, name)

    @classmethod
    def constant(cls, length, diameter, pitch):
        return cls(length, diameter, diameter, pitch, pitch)

    def values_at(self, fraction):
        """Return (diameter, pitch) at a relative axial position in [0, 1]."""
        _finite(fraction, tr('Section position'))
        if not 0 <= fraction <= 1:
            raise ValueError(tr('Section position must be between 0 and 1.'))
        # Weighted sums avoid overflow when subtracting extreme endpoint values.
        return (
            (1 - fraction) * self.diameter_start + fraction * self.diameter_end,
            (1 - fraction) * self.pitch_start + fraction * self.pitch_end,
        )


@dataclass(frozen=True)
class SegmentedHelix:
    segments: tuple
    start_angle: float = 0.0
    right_handed: bool = True

    def __post_init__(self):
        # Own an immutable snapshot even when the future UI passes a list.
        try:
            segments = tuple(self.segments)
        except TypeError as error:
            raise ValueError(tr('A section list is required.')) from error
        if not segments or not all(isinstance(s, HelixSegment) for s in segments):
            raise ValueError(tr('At least one valid helix section is required.'))
        object.__setattr__(self, 'segments', segments)
        _finite(self.start_angle, tr('Start angle'))
        if not isinstance(self.right_handed, bool):
            raise ValueError(tr('Handedness must be a boolean value.'))
        for index, (previous, current) in enumerate(zip(segments, segments[1:]), 2):
            if not math.isclose(previous.diameter_end, current.diameter_start,
                                rel_tol=1e-9, abs_tol=1e-9):
                raise ValueError(tr('The start diameter of section {p0} must match the end diameter of the previous section.', p0=index))
        # Pitch may jump at a boundary; this produces a tangent discontinuity.
        self.total_length

    @property
    def total_length(self):
        try:
            length = math.fsum(segment.length for segment in self.segments)
        except OverflowError as error:
            raise ValueError(tr('The total length is too large.')) from error
        _positive(length, tr('Total length'))
        return length

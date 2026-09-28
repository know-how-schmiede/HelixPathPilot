"""Validated segment data for variable helices, without Fusion dependencies.

Lengths share one unit (cm in Fusion); start_angle is in radians. Diameter and
pitch vary linearly with axial distance within each segment, not with angle.
This module defines data only; variable-helix sampling is a separate step.
"""

from dataclasses import dataclass
import math
from numbers import Real


def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f'{label} muss eine endliche Zahl sein.')


def _positive(value, label):
    _finite(value, label)
    if value <= 0:
        raise ValueError(f'{label} muss größer als null sein.')


@dataclass(frozen=True)
class HelixSegment:
    length: float
    diameter_start: float
    diameter_end: float
    pitch_start: float
    pitch_end: float

    def __post_init__(self):
        for name, value in (
            ('Abschnittslänge', self.length),
            ('Startdurchmesser', self.diameter_start),
            ('Enddurchmesser', self.diameter_end),
            ('Startsteigung', self.pitch_start),
            ('Endsteigung', self.pitch_end),
        ):
            _positive(value, name)

    @classmethod
    def constant(cls, length, diameter, pitch):
        return cls(length, diameter, diameter, pitch, pitch)

    def values_at(self, fraction):
        """Return (diameter, pitch) at a relative axial position in [0, 1]."""
        _finite(fraction, 'Abschnittsposition')
        if not 0 <= fraction <= 1:
            raise ValueError('Die Abschnittsposition muss zwischen 0 und 1 liegen.')
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
            raise ValueError('Eine Abschnittsliste wird benötigt.') from error
        if not segments or not all(isinstance(s, HelixSegment) for s in segments):
            raise ValueError('Mindestens ein gültiger Helix-Abschnitt wird benötigt.')
        object.__setattr__(self, 'segments', segments)
        _finite(self.start_angle, 'Startwinkel')
        if not isinstance(self.right_handed, bool):
            raise ValueError('Die Drehrichtung muss als boolescher Wert vorliegen.')
        for index, (previous, current) in enumerate(zip(segments, segments[1:]), 2):
            if not math.isclose(previous.diameter_end, current.diameter_start,
                                rel_tol=1e-9, abs_tol=1e-9):
                raise ValueError(f'Der Startdurchmesser von Abschnitt {index} muss '
                                 'zum Enddurchmesser des vorherigen Abschnitts passen.')
        # Pitch may jump at a boundary; this produces a tangent discontinuity.
        self.total_length

    @property
    def total_length(self):
        try:
            length = math.fsum(segment.length for segment in self.segments)
        except OverflowError as error:
            raise ValueError('Die Gesamtlänge ist zu groß.') from error
        _positive(length, 'Gesamtlänge')
        return length

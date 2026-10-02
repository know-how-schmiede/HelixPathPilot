"""Finite, full circular cylinder/cone profiles, independent of Fusion."""

from ..i18n import tr

from dataclasses import dataclass
import math

from .axis import AxisFrame


@dataclass(frozen=True)
class SurfaceProfile:
    axis: AxisFrame
    length: float
    radius_start: float
    radius_end: float

    def radius_at(self, distance):
        if not math.isfinite(distance) or not 0 <= distance <= self.length:
            raise ValueError(tr('Position is outside the axial surface range.'))
        return self.radius_start + (self.radius_end - self.radius_start) * distance / self.length


def profile_from_rings(axis, rings, area, cylinder=False):
    """Accept only two coaxial circular rims and the complete lateral area.

    rings contains (center, normal, radius) tuples; lengths in cm, area in cm².
    Sorting along the surface axis avoids dependence on edge enumeration order.
    """
    direction = axis.basis()[2]
    if len(rings) != 2:
        raise ValueError(tr(
            'The lateral face requires exactly two complete circular boundaries; tips, holes and '
            'split boundaries are not yet supported.'))
    rims = []
    for center, normal, radius in rings:
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError(tr('Boundary radii must be positive and finite.'))
        rim_direction = AxisFrame(center, normal).basis()[2]
        if abs(abs(sum(a*b for a, b in zip(direction, rim_direction))) - 1) > 1e-8:
            raise ValueError(tr('Circular boundaries must be perpendicular to the rotation axis.'))
        delta = tuple(center[i] - axis.origin[i] for i in range(3))
        height = sum(a*b for a, b in zip(delta, direction))
        offset = math.hypot(*(delta[i] - height*direction[i] for i in range(3)))
        if offset > max(1e-6, radius * 1e-7):
            raise ValueError(tr('Circular boundaries do not share the same rotation axis.'))
        rims.append((height, radius))
    rims.sort()
    (start, r0), (end, r1) = rims
    length = end - start
    if not math.isfinite(length) or length <= 1e-6:
        raise ValueError(tr('The axial surface range is too small or invalid.'))
    if cylinder and not math.isclose(r0, r1, rel_tol=1e-7, abs_tol=1e-6):
        raise ValueError(tr('The cylinder boundary radii do not match.'))
    expected = math.pi * (r0 + r1) * math.hypot(length, r1-r0)
    if not math.isfinite(area) or area <= 0 or not math.isclose(area, expected, rel_tol=1e-6, abs_tol=1e-8):
        raise ValueError(tr('The face is not a complete, untrimmed 360° lateral face.'))
    origin = tuple(axis.origin[i] + start*direction[i] for i in range(3))
    return SurfaceProfile(AxisFrame(origin, direction), length, r0, r1)

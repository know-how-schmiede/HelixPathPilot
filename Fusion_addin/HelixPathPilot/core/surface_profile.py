"""Finite, full circular cylinder/cone profiles, independent of Fusion."""

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
            raise ValueError('Position liegt außerhalb des axialen Flächenbereichs.')
        return self.radius_start + (self.radius_end - self.radius_start) * distance / self.length


def profile_from_rings(axis, rings, area, cylinder=False):
    """Accept only two coaxial circular rims and the complete lateral area.

    rings contains (center, normal, radius) tuples; lengths in cm, area in cm².
    Sorting along the surface axis avoids dependence on edge enumeration order.
    """
    direction = axis.basis()[2]
    if len(rings) != 2:
        raise ValueError('Die Mantelfläche benötigt genau zwei vollständige Kreisränder; '
                         'Spitzen, Bohrungen und geteilte Ränder werden noch nicht unterstützt.')
    rims = []
    for center, normal, radius in rings:
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError('Die Randradien müssen positiv und endlich sein.')
        rim_direction = AxisFrame(center, normal).basis()[2]
        if abs(abs(sum(a*b for a, b in zip(direction, rim_direction))) - 1) > 1e-8:
            raise ValueError('Kreisränder müssen senkrecht zur Rotationsachse liegen.')
        delta = tuple(center[i] - axis.origin[i] for i in range(3))
        height = sum(a*b for a, b in zip(delta, direction))
        offset = math.hypot(*(delta[i] - height*direction[i] for i in range(3)))
        if offset > max(1e-6, radius * 1e-7):
            raise ValueError('Kreisränder liegen nicht auf derselben Rotationsachse.')
        rims.append((height, radius))
    rims.sort()
    (start, r0), (end, r1) = rims
    length = end - start
    if not math.isfinite(length) or length <= 1e-6:
        raise ValueError('Der axiale Flächenbereich ist zu klein oder ungültig.')
    if cylinder and not math.isclose(r0, r1, rel_tol=1e-7, abs_tol=1e-6):
        raise ValueError('Die Zylinder-Randradien stimmen nicht überein.')
    expected = math.pi * (r0 + r1) * math.hypot(length, r1-r0)
    if not math.isfinite(area) or area <= 0 or not math.isclose(area, expected, rel_tol=1e-6, abs_tol=1e-8):
        raise ValueError('Die Fläche ist kein vollständiger, unbeschnittener 360°-Mantel.')
    origin = tuple(axis.origin[i] + start*direction[i] for i in range(3))
    return SurfaceProfile(AxisFrame(origin, direction), length, r0, r1)

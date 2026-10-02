"""Right-handed coordinate frames for helix placement; no Fusion dependency."""

from ..i18n import tr

from dataclasses import dataclass
import math


def _unit(vector):
    if len(vector) != 3 or not all(math.isfinite(v) for v in vector):
        raise ValueError(tr('The axis direction must be finite.'))
    length = math.hypot(*vector)
    if length == 0 or not math.isfinite(length):
        raise ValueError(tr('The axis requires a valid direction.'))
    return tuple(v / length for v in vector)


@dataclass(frozen=True)
class AxisFrame:
    origin: tuple = (0.0, 0.0, 0.0)
    direction: tuple = (0.0, 0.0, 1.0)

    def basis(self):
        if len(self.origin) != 3 or not all(math.isfinite(v) for v in self.origin):
            raise ValueError(tr('The axis origin must be finite.'))
        z = _unit(self.direction)
        # Project global X onto the normal plane. Near parallel, use global Y.
        reference = (1.0, 0.0, 0.0) if abs(z[0]) < 0.99 else (0.0, 1.0, 0.0)
        dot = sum(a * b for a, b in zip(reference, z))
        x = _unit(tuple(a - dot * b for a, b in zip(reference, z)))
        y = (z[1] * x[2] - z[2] * x[1],
             z[2] * x[0] - z[0] * x[2],
             z[0] * x[1] - z[1] * x[0])
        return x, y, z

    def transform(self, points):
        x, y, z = self.basis()
        return [tuple(self.origin[i] + p[0] * x[i] + p[1] * y[i] + p[2] * z[i]
                      for i in range(3)) for p in points]

    def reversed(self):
        return AxisFrame(self.origin, tuple(-v for v in self.direction))

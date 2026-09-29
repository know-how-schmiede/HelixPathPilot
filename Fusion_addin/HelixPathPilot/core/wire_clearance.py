"""Numerical tube-clearance check, independent of Fusion (lengths in cm).

This is a conservative sampled preflight, not a proof for an arbitrary spline.
The CAD kernel must still accept the final sweep. Local neighbours are excluded
from the distance test; their admissibility is checked by curvature instead.
"""

import math


def validate_diameter(diameter):
    if isinstance(diameter, bool) or not math.isfinite(diameter) or diameter <= 0:
        raise ValueError('Der Drahtdurchmesser muss endlich und größer als null sein.')


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def segment_distance(a, b, c, d):
    """Minimum distance between closed 3D line segments, including endpoints."""
    u, v, w = _sub(b, a), _sub(d, c), _sub(a, c)
    aa, bb, cc = _dot(u, u), _dot(u, v), _dot(v, v)
    dd, ee = _dot(u, w), _dot(v, w)
    if aa == 0 or cc == 0:
        raise ValueError('Der Helixpfad enthält ein Segment ohne Länge.')
    clamp = lambda x: max(0.0, min(1.0, x))
    candidates = [(0, clamp(ee / cc)), (1, clamp((ee + bb) / cc)),
                  (clamp(-dd / aa), 0), (clamp((bb - dd) / aa), 1)]
    determinant = aa * cc - bb * bb
    if determinant > 1e-14 * aa * cc:
        s, t = (bb * ee - cc * dd) / determinant, (aa * ee - bb * dd) / determinant
        if 0 <= s <= 1 and 0 <= t <= 1:
            candidates.append((s, t))
    return min(math.sqrt(sum((w[k] + s*u[k] - t*v[k])**2 for k in range(3)))
               for s, t in candidates)


def check_clearance(points, diameter, tolerance):
    """Check a stroked curve with its stated chord tolerance.

    Reject contact as well as overlap, allowing two chord-error margins.
    A sweep along x reduces pair checks; a work limit fails closed rather than
    hanging Fusion on exceptionally dense paths.
    """
    validate_diameter(diameter)
    if len(points) < 2 or len(points) > 16000:
        raise ValueError('Drahtprüfung: Pfad zu kurz oder zu komplex (maximal 16000 Prüfpunkte).')
    if any(len(p) != 3 or any(not math.isfinite(v) for v in p) for p in points):
        raise ValueError('Drahtprüfung: ungültige Pfadkoordinaten.')
    clearance = diameter + 2 * tolerance
    edges, length = [], 0.0
    for index, (a, b) in enumerate(zip(points, points[1:])):
        step = math.dist(a, b)
        if step <= 1e-12:
            raise ValueError('Drahtprüfung: Pfad enthält doppelte Punkte.')
        low = tuple(min(x, y) for x, y in zip(a, b))
        high = tuple(max(x, y) for x, y in zip(a, b))
        edges.append((low[0], high[0], index, a, b, low, high, length, length + step))
        length += step
    active, checks = [], 0
    for edge in sorted(edges):
        low_x, _, index, a, b, low, high, start, end = edge
        active = [other for other in active if other[1] + clearance >= low_x]
        for other in active:
            checks += 1
            if checks > 2000000:
                raise ValueError('Drahtprüfung zu aufwendig. Bitte weniger Windungen verwenden.')
            _, _, j, c, d, lo, hi, begin, finish = other
            if abs(index - j) <= 1:
                continue
            gap = max(start - finish, begin - end)
            if gap < math.pi * diameter / 2:
                continue
            if any(low[k] > hi[k] + clearance or lo[k] > high[k] + clearance for k in (1, 2)):
                continue
            if segment_distance(a, b, c, d) <= clearance:
                raise ValueError('Drahtdurchmesser zu groß: Windungen oder Abschnitte berühren '
                                 'oder überschneiden sich. Bitte die Drahtstärke reduzieren '
                                 'oder den Helixverlauf ändern.')
        active.append(edge)

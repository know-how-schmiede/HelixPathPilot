"""Sample piecewise helices with pitch linear in axial distance."""

from ..i18n import tr

import math

from .helix_math import MAX_POINTS, SAMPLES_PER_TURN

MAX_SEGMENTS = 32


def _log_ratio(segment):
    delta = segment.pitch_end - segment.pitch_start
    relative = delta / segment.pitch_start
    if abs(relative) < 0.5:
        return math.log1p(relative)
    return math.log(segment.pitch_end) - math.log(segment.pitch_start)


def segment_turns(segment):
    """Integral of 1/pitch(z) over one segment, in turns."""
    delta = segment.pitch_end - segment.pitch_start
    if delta == 0:
        return segment.length / segment.pitch_start
    return segment.length * (_log_ratio(segment) / delta)


def sampling_plan(model):
    if len(model.segments) > MAX_SEGMENTS:
        raise ValueError(tr('A maximum of {p0} sections is allowed.', p0=MAX_SEGMENTS))
    turns = [segment_turns(segment) for segment in model.segments]
    if any(not math.isfinite(t) or t <= 0 or t > 128 for t in turns) or math.fsum(turns) > 128:
        raise ValueError(tr('Maximum 128 turns in total; please check length and pitch.'))
    counts = [max(2, math.ceil(t * SAMPLES_PER_TURN)) for t in turns]
    if sum(counts) + 1 > MAX_POINTS:
        raise ValueError(tr('Too many sample points. Please reduce the number of sections or turns.'))
    return list(zip(turns, counts))


def _axial_fraction(segment, turn_fraction):
    if turn_fraction in (0, 1) or segment.pitch_start == segment.pitch_end:
        return turn_fraction
    ratio = _log_ratio(segment)
    if ratio > 0:
        # Equivalent to expm1(q*r)/expm1(r), without overflow for large r.
        return math.exp((turn_fraction - 1) * ratio) * (
            -math.expm1(-turn_fraction * ratio)) / (-math.expm1(-ratio))
    return math.expm1(turn_fraction * ratio) / math.expm1(ratio)


def segmented_points(model):
    """One point list per segment; adjacent lists share their exact endpoint."""
    plan = sampling_plan(model)
    result = []
    height = 0.0
    angle = model.start_angle % math.tau
    handedness = 1 if model.right_handed else -1
    for segment, (turns, count) in zip(model.segments, plan):
        sweep = handedness * math.tau * turns
        points = []
        for index in range(count + 1):
            q = index / count
            fraction = _axial_fraction(segment, q)
            radius = segment.values_at(fraction)[0] / 2
            theta = angle + sweep * q
            points.append((radius * math.cos(theta), radius * math.sin(theta),
                           height + segment.length * fraction))
        if result:
            points[0] = result[-1][-1]
        result.append(points)
        height = points[-1][2]
        angle = (angle + sweep) % math.tau
    return result

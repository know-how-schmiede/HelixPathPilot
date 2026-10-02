"""Map a finite rotational profile to the shared sampled helix model."""

from ..i18n import tr

import math

from .axis import AxisFrame
from .helix_segments import _finite
from .helix_segments import HelixSegment, SegmentedHelix
from .variable_helix import sampling_plan


def surface_helix(profile, pitch, start_angle=0, right_handed=True, reverse=False, offset=0,
                  *, pitch_end=None):
    """Normal offset away from the axis; cone rims shift axially as well.

    Pitch varies linearly along axial travel from pitch to pitch_end (default:
    constant pitch). Start/end pitches follow travel direction after reversal.
    Pitch and axial span are unchanged by offset. Offset direction does not depend on
    face orientation (inside/outside of a solid) or helix travel direction.
    """
    _finite(offset, tr('Surface offset'))
    slant = math.hypot(profile.length, profile.radius_end - profile.radius_start)
    radial_shift = offset * (profile.length / slant)
    axial_shift = -offset * ((profile.radius_end - profile.radius_start) / slant)
    origin = profile.axis.transform([(0, 0, axial_shift)])[0]
    axis = AxisFrame(origin, profile.axis.direction)
    axis.basis()
    first, last = profile.radius_start + radial_shift, profile.radius_end + radial_shift
    if min(first, last) <= 0:
        raise ValueError(tr('Surface offset reaches or crosses the rotation axis. Please choose a smaller negative offset.'))
    if reverse:
        origin = axis.transform([(0, 0, profile.length)])[0]
        axis = AxisFrame(origin, tuple(-v for v in axis.direction))
        first, last = last, first
    model = SegmentedHelix((HelixSegment(profile.length, 2*first, 2*last, pitch,
                                        pitch if pitch_end is None else pitch_end),),
                           start_angle, right_handed)
    sampling_plan(model)
    return model, axis

"""Map a finite rotational profile to the shared sampled helix model."""

from .axis import AxisFrame
from .helix_segments import HelixSegment, SegmentedHelix
from .variable_helix import sampling_plan


def surface_helix(profile, pitch, start_angle=0, right_handed=True, reverse=False):
    axis = profile.axis
    first, last = profile.radius_start, profile.radius_end
    if reverse:
        origin = axis.transform([(0, 0, profile.length)])[0]
        axis = AxisFrame(origin, tuple(-v for v in axis.direction))
        first, last = last, first
    model = SegmentedHelix((HelixSegment(profile.length, 2*first, 2*last, pitch, pitch),),
                           start_angle, right_handed)
    sampling_plan(model)
    return model, axis

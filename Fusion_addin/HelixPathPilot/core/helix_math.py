"""Constant-radius helix sampling, independent of Fusion.

Lengths use one consistent unit (centimetres in Fusion); angles use radians.
Right-handed means positive rotation about +Z as Z increases.
"""

from dataclasses import dataclass
import math

from .helix_segments import HelixSegment, SegmentedHelix

SAMPLES_PER_TURN = 32
MAX_POINTS = 4097


@dataclass(frozen=True)
class HelixParameters:
    diameter: float
    length: float
    pitch: float
    start_angle: float = 0.0
    right_handed: bool = True

    def as_segmented(self):
        """Represent the basic helix as one constant segment for future editors."""
        return SegmentedHelix(
            (HelixSegment.constant(self.length, self.diameter, self.pitch),),
            self.start_angle, self.right_handed,
        )

    def segment_count(self):
        self.as_segmented()
        turns = self.length / self.pitch
        if not math.isfinite(turns) or turns > (MAX_POINTS - 1) / SAMPLES_PER_TURN:
            raise ValueError('Maximal 128 Windungen pro Helix sind möglich.')
        return max(2, math.ceil(turns * SAMPLES_PER_TURN))


def helix_points(parameters):
    """Return XYZ tuples including both ends; partial turns are supported."""
    segments = parameters.segment_count()
    radius = parameters.diameter / 2
    angle = parameters.start_angle % math.tau
    sweep = math.tau * (parameters.length / parameters.pitch)
    if not parameters.right_handed:
        sweep = -sweep
    return [
        (
            radius * math.cos(angle + sweep * index / segments),
            radius * math.sin(angle + sweep * index / segments),
            parameters.length * index / segments,
        )
        for index in range(segments + 1)
    ]

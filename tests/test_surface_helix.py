"""Surface helix samples stay on the analytic mantle in either direction."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))
from HelixPathPilot.core.axis import AxisFrame
from HelixPathPilot.core.surface_profile import SurfaceProfile
from HelixPathPilot.core.surface_helix import surface_helix
from HelixPathPilot.core.variable_helix import segmented_points


class SurfaceHelixTests(unittest.TestCase):
    def test_cylinder_and_cone_on_tilted_axis_both_directions(self):
        for radius_end in (2, 4):
            profile = SurfaceProfile(AxisFrame((10, 20, 30), (1, 2, 3)), 5, 2, radius_end)
            direction = profile.axis.basis()[2]
            for reverse in (False, True):
                model, axis = surface_helix(profile, 0.5, reverse=reverse)
                points = axis.transform(segmented_points(model)[0])
                for index, point in enumerate(points):
                    delta = tuple(point[i] - profile.axis.origin[i] for i in range(3))
                    height = sum(a*b for a, b in zip(delta, direction))
                    fraction = index / (len(points)-1)
                    self.assertAlmostEqual(height, 5 * (1-fraction if reverse else fraction))
                    radius = math.hypot(*(delta[i] - height*direction[i] for i in range(3)))
                    self.assertAlmostEqual(radius, 2+(radius_end-2)*height/5)

    def test_fractional_turns_start_angle_and_handedness(self):
        profile = SurfaceProfile(AxisFrame(), 1.25, 2, 2)
        for right in (True, False):
            model, _ = surface_helix(profile, 1, math.pi/2, right)
            points = segmented_points(model)[0]
            self.assertAlmostEqual(points[0][1], 2)
            self.assertAlmostEqual(points[-1][0], -2 if right else 2)
            self.assertEqual(points[-1][2], 1.25)

    def test_invalid_pitch_angle_and_sampling_limit(self):
        profile = SurfaceProfile(AxisFrame(), 5, 2, 2)
        for pitch in (0, -1, math.nan, math.inf, 0.001):
            with self.assertRaises(ValueError):
                surface_helix(profile, pitch)
        with self.assertRaises(ValueError):
            surface_helix(profile, 1, math.inf)

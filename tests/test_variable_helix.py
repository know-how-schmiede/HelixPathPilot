import math
from pathlib import Path
import sys
import unittest

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin' / 'HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
from HelixPathPilot.core.helix_math import HelixParameters, helix_points
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix
from HelixPathPilot.core.variable_helix import sampling_plan, segment_turns, segmented_points


class VariableHelixTests(unittest.TestCase):
    def test_constant_matches_previous_generator(self):
        parameters = HelixParameters(2, 5, 0.5, 0.7, False)
        actual = segmented_points(parameters.as_segmented())[0]
        expected = helix_points(parameters)
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            for x, y in zip(a, b):
                self.assertAlmostEqual(x, y)

    def test_linear_pitch_analytic_integral_and_radius(self):
        segment = HelixSegment(10, 2, 6, 1, 3)
        expected_turns = 5 * math.log(3)
        self.assertAlmostEqual(segment_turns(segment), expected_turns)
        points = segmented_points(SegmentedHelix((segment,)))[0]
        for i, (x, y, z) in enumerate(points):
            self.assertAlmostEqual(math.hypot(x, y), 1 + z / 5)
            analytic_angle = math.tau * 5 * math.log1p(z / 5)
            sample_angle = math.tau * expected_turns * i / (len(points) - 1)
            self.assertAlmostEqual(analytic_angle, sample_angle)
            self.assertAlmostEqual(x, (1 + z / 5) * math.cos(analytic_angle))
        self.assertEqual(points[-1][2], 10)

    def test_decreasing_and_nearly_constant_pitch(self):
        for p0, p1 in ((3, 1), (1, 1 + 1e-12), (1, 1 - 1e-12)):
            segment = HelixSegment(2, 2, 2, p0, p1)
            points = segmented_points(SegmentedHelix((segment,)))[0]
            heights = [p[2] for p in points]
            self.assertEqual(heights[0], 0)
            self.assertEqual(heights[-1], 2)
            self.assertTrue(all(a < b for a, b in zip(heights, heights[1:])))
        self.assertAlmostEqual(segment_turns(HelixSegment(2, 2, 2, 1, 1 + 1e-12)), 2)

    def test_continuous_joins_and_fractional_phase(self):
        model = SegmentedHelix((HelixSegment.constant(0.125, 2, 0.5),
                                HelixSegment(1, 2, 4, 1, 1)), start_angle=0.3)
        sections = segmented_points(model)
        self.assertEqual(sections[0][-1], sections[1][0])
        end = sections[-1][-1]
        self.assertAlmostEqual(end[0], 2 * math.cos(0.3 + math.tau * 1.25))
        self.assertAlmostEqual(end[1], 2 * math.sin(0.3 + math.tau * 1.25))
        self.assertAlmostEqual(end[2], model.total_length)

    def test_left_hand_reflects_variable_curve(self):
        segments = (HelixSegment(5, 2, 3, 1, 2),)
        right = segmented_points(SegmentedHelix(segments))[0]
        left = segmented_points(SegmentedHelix(segments, right_handed=False))[0]
        for a, b in zip(right, left):
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], -b[1])
            self.assertEqual(a[2], b[2])

    def test_global_limits(self):
        with self.assertRaises(ValueError):
            sampling_plan(SegmentedHelix((HelixSegment.constant(65, 2, 1),) * 2))
        with self.assertRaises(ValueError):
            sampling_plan(SegmentedHelix((HelixSegment.constant(0.1, 2, 1),) * 33))
        with self.assertRaises(ValueError):
            sampling_plan(SegmentedHelix((HelixSegment.constant(1e308, 2, 1e-308),)))
        # Below 128 turns, but per-section rounding exceeds the point budget.
        with self.assertRaises(ValueError):
            sampling_plan(SegmentedHelix((HelixSegment.constant(127.9 / 30, 2, 1),) * 30))


if __name__ == '__main__':
    unittest.main()

"""Variable-helix data contract, independent of Fusion and its UI."""

from dataclasses import FrozenInstanceError
import math
from pathlib import Path
import sys
import unittest

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin' / 'HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix
from HelixPathPilot.core.helix_math import HelixParameters, helix_points


class SegmentTests(unittest.TestCase):
    def test_linear_values_at_axial_positions(self):
        segment = HelixSegment(10, 2, 6, 1, 3)
        self.assertEqual(segment.values_at(0), (2, 1))
        self.assertEqual(segment.values_at(0.25), (3, 1.5))
        self.assertEqual(segment.values_at(1), (6, 3))
        taper = HelixSegment(10, 6, 2, 3, 1)
        self.assertEqual(taper.values_at(0.75), (3, 1.5))

    def test_constant_segment(self):
        segment = HelixSegment.constant(5, 2, 0.5)
        for fraction in (0, 0.4, 1):
            self.assertEqual(segment.values_at(fraction), (2, 0.5))

    def test_invalid_dimensions(self):
        for field in ('length', 'diameter_start', 'diameter_end', 'pitch_start', 'pitch_end'):
            for value in (0, -1, math.inf, math.nan, None, '2 mm', True):
                with self.subTest(field=field, value=value):
                    values = dict(length=5, diameter_start=2, diameter_end=3, pitch_start=1, pitch_end=2)
                    values[field] = value
                    with self.assertRaises(ValueError):
                        HelixSegment(**values)

    def test_invalid_fraction(self):
        segment = HelixSegment.constant(5, 2, 1)
        for fraction in (-0.1, 1.1, math.nan, math.inf, None, True):
            with self.subTest(fraction=fraction), self.assertRaises(ValueError):
                segment.values_at(fraction)

    def test_sequence_total_length_and_immutability(self):
        source = [HelixSegment(3, 2, 4, 1, 2), HelixSegment(7, 4, 6, 2, 3)]
        helix = SegmentedHelix(source, start_angle=math.pi, right_handed=False)
        source.clear()
        self.assertEqual(len(helix.segments), 2)
        self.assertEqual(helix.total_length, 10)
        self.assertFalse(helix.right_handed)
        with self.assertRaises(FrozenInstanceError):
            helix.segments[0].length = 99

    def test_diameter_gap_rejected_pitch_jump_allowed(self):
        first = HelixSegment.constant(3, 2, 1)
        with self.assertRaisesRegex(ValueError, 'Abschnitt 2'):
            SegmentedHelix((first, HelixSegment.constant(3, 4, 1)))
        helix = SegmentedHelix((first, HelixSegment.constant(3, 2, 3)))
        self.assertEqual(helix.total_length, 6)

    def test_roundoff_at_join_is_accepted(self):
        SegmentedHelix((HelixSegment.constant(1, 0.1 + 0.2, 1),
                        HelixSegment.constant(1, 0.3, 1)))

    def test_invalid_sequence_and_global_parameters(self):
        for segments in ((), None, [object()]):
            with self.subTest(segments=segments), self.assertRaises(ValueError):
                SegmentedHelix(segments)
        segment = HelixSegment.constant(1, 1, 1)
        with self.assertRaises(ValueError):
            SegmentedHelix((segment,), start_angle=math.nan)
        with self.assertRaises(ValueError):
            SegmentedHelix((segment,), right_handed='left')

    def test_total_length_overflow_rejected(self):
        segment = HelixSegment.constant(1e308, 2, 1)
        with self.assertRaisesRegex(ValueError, 'Gesamtlänge'):
            SegmentedHelix((segment, segment))

    def test_basic_helix_conversion_preserves_parameters(self):
        parameters = HelixParameters(2, 5, 0.5, math.pi / 2, False)
        model = parameters.as_segmented()
        self.assertEqual(model.segments, (HelixSegment.constant(5, 2, 0.5),))
        self.assertEqual(model.start_angle, parameters.start_angle)
        self.assertEqual(model.right_handed, parameters.right_handed)
        self.assertEqual(model.total_length, 5)
        self.assertEqual(len(helix_points(parameters)), 321)


if __name__ == '__main__':
    unittest.main()

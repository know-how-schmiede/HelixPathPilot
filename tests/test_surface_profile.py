"""Analytic surface profiles, independent of Fusion and face orientation."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))
from HelixPathPilot.core.axis import AxisFrame
from HelixPathPilot.core.surface_profile import profile_from_rings


class ProfileTests(unittest.TestCase):
    def rings(self, r0=2, r1=2):
        return [((0, 0, 3), (0, 0, 1), r0), ((0, 0, 8), (0, 0, -1), r1)]

    def test_cylinder_and_reversed_rim_order(self):
        p = profile_from_rings(AxisFrame(), self.rings()[::-1], 20*math.pi, True)
        self.assertEqual(p.axis.origin, (0, 0, 3))
        self.assertEqual(p.length, 5)
        self.assertEqual(p.radius_at(0), 2)
        self.assertEqual(p.radius_at(5), 2)

    def test_cone_linear_radius_and_reversed_axis(self):
        area = math.pi * 6 * math.hypot(5, 2)
        for direction, start, end in (((0, 0, 1), 2, 4), ((0, 0, -1), 4, 2)):
            p = profile_from_rings(AxisFrame(direction=direction), self.rings(2, 4), area)
            self.assertEqual(p.radius_at(0), start)
            self.assertEqual(p.radius_at(2.5), 3)
            self.assertEqual(p.radius_at(5), end)
            for distance in (-1, 6, math.nan):
                with self.assertRaises(ValueError):
                    p.radius_at(distance)

    def test_tilted_translated_axis(self):
        axis = AxisFrame((10, -20, 7), (1, 2, 3))
        centers = axis.transform([(0, 0, 3), (0, 0, 8)])
        rings = [(center, axis.direction, 2) for center in centers]
        p = profile_from_rings(axis, rings, 20*math.pi, True)
        self.assertAlmostEqual(p.length, 5)
        for actual, expected in zip(p.axis.origin, centers[0]):
            self.assertAlmostEqual(actual, expected)

    def test_partial_or_perforated_area_rejected(self):
        for area in (10*math.pi, 20*math.pi-0.01, 0, math.nan):
            with self.assertRaises(ValueError):
                profile_from_rings(AxisFrame(), self.rings(), area)

    def test_invalid_rims(self):
        for rings in (self.rings()[:1], self.rings()+self.rings()[:1], self.rings(0, 2),
                      self.rings(math.inf, 2),
                      [self.rings()[0], ((1, 0, 8), (0, 0, 1), 2)],
                      [self.rings()[0], ((0, 0, 8), (1, 0, 0), 2)],
                      [self.rings()[0], self.rings()[0]]):
            with self.assertRaises(ValueError):
                profile_from_rings(AxisFrame(), rings, 20*math.pi)
        with self.assertRaises(ValueError):
            profile_from_rings(AxisFrame(), self.rings(2, 3), 20*math.pi, True)

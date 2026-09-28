"""Placement and Fusion selection adapter checks without a Fusion process."""

import importlib.util
import math
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin' / 'HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
from HelixPathPilot.core.axis import AxisFrame
from HelixPathPilot.core.helix_math import HelixParameters, helix_points


class AxisTests(unittest.TestCase):
    def test_default_preserves_coordinates(self):
        points = helix_points(HelixParameters(2, 5, 0.5))
        self.assertEqual(AxisFrame().transform(points), points)

    def test_translated_x_axis(self):
        frame = AxisFrame((10, 20, 30), (2, 0, 0))
        self.assertEqual(frame.transform([(1, 0, 0), (1, 0, 5)]),
                         [(10, 21, 30), (15, 21, 30)])
        self.assertEqual(frame.reversed().transform([(1, 0, 5)]), [(5, 21, 30)])

    def test_arbitrary_frame_preserves_radius_height_and_handedness(self):
        frame = AxisFrame((3, 4, 5), (1, -2, 3))
        x, y, z = frame.basis()
        for a in (x, y, z):
            self.assertAlmostEqual(math.hypot(*a), 1)
        for a, b in ((x, y), (x, z), (y, z)):
            self.assertAlmostEqual(sum(v * w for v, w in zip(a, b)), 0)
        cross = (x[1]*y[2]-x[2]*y[1], x[2]*y[0]-x[0]*y[2], x[0]*y[1]-x[1]*y[0])
        for actual, expected in zip(cross, z):
            self.assertAlmostEqual(actual, expected)
        local = helix_points(HelixParameters(2, 5, 0.5))
        for p, q in zip(local, frame.transform(local)):
            delta = tuple(q[i] - frame.origin[i] for i in range(3))
            height = sum(delta[i] * z[i] for i in range(3))
            self.assertAlmostEqual(height, p[2])
            self.assertAlmostEqual(math.hypot(*(delta[i] - height*z[i] for i in range(3))), 1)

    def test_parallel_and_negative_directions(self):
        for direction in ((1, 0, 0), (-1, 0, 0), (0, 0, -1), (1, 1e-12, 0)):
            for vector in AxisFrame(direction=direction).basis():
                self.assertAlmostEqual(math.hypot(*vector), 1)

    def test_invalid_frame(self):
        for frame in (AxisFrame(direction=(0, 0, 0)), AxisFrame(direction=(math.nan, 0, 1)),
                      AxisFrame(origin=(0, math.inf, 0))):
            with self.assertRaises(ValueError):
                frame.transform([(0, 0, 0)])


class Vector:
    def __init__(self, *xyz):
        self.xyz = xyz

    def asArray(self):
        return self.xyz

    def vectorTo(self, other):
        return Vector(*(b - a for a, b in zip(self.xyz, other.xyz)))


class SelectionTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        adsk.fusion = types.ModuleType('adsk.fusion')
        for name in ('ConstructionAxis', 'SketchLine', 'BRepEdge'):
            setattr(adsk.fusion, name, types.SimpleNamespace(
                cast=lambda e, kind=name: e if e.kind == kind else None))
        adsk.core.Line3D = types.SimpleNamespace(cast=lambda g: g if g.kind == 'line' else None)
        modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        modules.start()
        self.addCleanup(modules.stop)
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.commands.createParametricHelix.axis_selection',
            ADDIN / 'commands/createParametricHelix/axis_selection.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def selection(self, entity=None):
        selection = Mock(selectionCount=0 if entity is None else 1)
        selection.selection.return_value.entity = entity
        return selection

    def test_default_and_reverse(self):
        self.assertEqual(self.module.selected_axis(self.selection()), AxisFrame())
        self.assertEqual(self.module.selected_axis(self.selection(), True), AxisFrame().reversed())

    def test_construction_axis_uses_context_geometry(self):
        entity = types.SimpleNamespace(kind='ConstructionAxis', isValid=True,
            geometry=types.SimpleNamespace(origin=Vector(10, 20, 30), direction=Vector(0, 2, 0)))
        frame = self.module.selected_axis(self.selection(entity))
        self.assertEqual(frame, AxisFrame((10, 20, 30), (0, 2, 0)))

    def test_sketch_line_uses_world_geometry(self):
        entity = types.SimpleNamespace(kind='SketchLine', isValid=True,
            worldGeometry=types.SimpleNamespace(startPoint=Vector(10, 20, 30), endPoint=Vector(15, 20, 30)))
        frame = self.module.selected_axis(self.selection(entity))
        self.assertEqual(frame, AxisFrame((10, 20, 30), (5, 0, 0)))

    def test_edge_and_invalid_entities(self):
        entity = types.SimpleNamespace(kind='BRepEdge', isValid=True,
            geometry=types.SimpleNamespace(kind='line', startPoint=Vector(1, 2, 3), endPoint=Vector(1, 2, 8)))
        self.assertEqual(self.module.selected_axis(self.selection(entity)), AxisFrame((1, 2, 3), (0, 0, 5)))
        entity.geometry.kind = 'circle'
        with self.assertRaises(ValueError):
            self.module.selected_axis(self.selection(entity))
        entity.isValid = False
        with self.assertRaises(ValueError):
            self.module.selected_axis(self.selection(entity))


if __name__ == '__main__':
    unittest.main()

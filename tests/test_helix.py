"""Checks for geometry and the Fusion adapter without a Fusion runtime."""

import ast
import importlib.util
import json
import math
from pathlib import Path
import runpy
import sys
import types
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / 'Fusion_addin' / 'HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
from HelixPathPilot.core.helix_math import HelixParameters, helix_points
from HelixPathPilot.core.axis import AxisFrame
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix


class HelixTests(unittest.TestCase):
    def test_default_helix_dimensions_and_turns(self):
        points = helix_points(HelixParameters(2, 5, 0.5))
        self.assertEqual(len(points), 321)
        for index, (x, y, z) in enumerate(points):
            self.assertAlmostEqual(math.hypot(x, y), 1)
            self.assertAlmostEqual(z, 5 * index / 320)
        self.assertAlmostEqual(points[-1][0], 1)
        self.assertAlmostEqual(points[-1][1], 0)
        self.assertEqual(points[-1][2], 5)
        self.assertAlmostEqual(points[32][2], 0.5)

    def test_partial_turn_and_angle(self):
        points = helix_points(HelixParameters(2, 0.125, 0.5, math.pi / 2))
        self.assertAlmostEqual(points[0][0], 0)
        self.assertAlmostEqual(points[0][1], 1)
        self.assertAlmostEqual(points[-1][0], -1)
        self.assertAlmostEqual(points[-1][1], 0)
        self.assertEqual(points[-1][2], 0.125)

    def test_handedness(self):
        right = helix_points(HelixParameters(2, 0.125, 0.5))
        left = helix_points(HelixParameters(2, 0.125, 0.5, right_handed=False))
        self.assertAlmostEqual(right[-1][1], 1)
        self.assertAlmostEqual(left[-1][1], -1)
        self.assertEqual(right[-1][2], left[-1][2])

    def test_invalid_parameters(self):
        for field in ('diameter', 'length', 'pitch'):
            for value in (0, -1, math.inf, math.nan):
                with self.subTest(field=field, value=value):
                    values = dict(diameter=2, length=5, pitch=0.5)
                    values[field] = value
                    with self.assertRaises(ValueError):
                        helix_points(HelixParameters(**values))
        with self.assertRaises(ValueError):
            helix_points(HelixParameters(2, 5, 0.5, math.inf))

    def test_point_budget_and_overflow(self):
        self.assertEqual(len(helix_points(HelixParameters(2, 128, 1))), 4097)
        for length, pitch in ((129, 1), (1e308, 1e-308)):
            with self.assertRaises(ValueError):
                helix_points(HelixParameters(2, length, pitch))

    def test_syntax_and_metadata(self):
        for path in ADDIN.rglob('*.py'):
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        manifest = json.loads((ADDIN / 'HelixPathPilot.manifest').read_text())
        version = runpy.run_path(str(ADDIN / 'version.py'))
        self.assertEqual(manifest['version'], version['VERSION'])
        self.assertTrue((ADDIN / manifest['iconFilename']).is_file())
        for size in (16, 32, 64):
            icon = ADDIN / 'resources/icons/helix' / f'{size}x{size}.svg'
            self.assertEqual(ET.parse(icon).getroot().attrib['viewBox'], '0 0 32 32')


class SketchAdapterTests(unittest.TestCase):
    def setUp(self):
        # Load the adapter without importing the UI command registry.
        adsk = types.ModuleType('adsk')
        core = types.ModuleType('adsk.core')
        adsk.core = core
        core.Point3D = types.SimpleNamespace(create=lambda *xyz: xyz)

        class Collection(list):
            add = list.append

        core.ObjectCollection = types.SimpleNamespace(create=Collection)
        self.modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': core})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        name = 'HelixPathPilot.commands.createParametricHelix.sketch_builder'
        spec = importlib.util.spec_from_file_location(
            name, ADDIN / 'commands/createParametricHelix/sketch_builder.py')
        self.adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.adapter)
        self.design = Mock()
        self.sketch = self.design.rootComponent.sketches.add.return_value
        self.sketch.modelToSketchSpace.side_effect = lambda p: p

    def test_creates_spatial_curve_in_root(self):
        result = self.adapter.create_sketch(self.design, HelixParameters(2, 5, 0.5))
        self.assertIs(result, self.sketch)
        self.design.rootComponent.sketches.add.assert_called_once_with(
            self.design.rootComponent.xYConstructionPlane)
        points = self.sketch.sketchCurves.sketchFittedSplines.add.call_args.args[0]
        self.assertEqual(points[0], (1, 0, 0))
        self.assertEqual(points[-1][2], 5)
        self.sketch.deleteMe.assert_not_called()

    def test_failed_spline_removes_empty_sketch(self):
        for failure in ('exception', 'null'):
            with self.subTest(failure=failure):
                add = self.sketch.sketchCurves.sketchFittedSplines.add
                add.side_effect = RuntimeError('API failure') if failure == 'exception' else None
                add.return_value = None
                self.sketch.deleteMe.reset_mock()
                with self.assertRaises(RuntimeError):
                    self.adapter.create_sketch(self.design, HelixParameters(2, 5, 0.5))
                self.sketch.deleteMe.assert_called_once()

    def test_invalid_input_creates_no_sketch(self):
        with self.assertRaises(ValueError):
            self.adapter.create_sketch(self.design, HelixParameters(0, 5, 0.5))
        self.design.rootComponent.sketches.add.assert_not_called()

    def test_selected_axis_is_applied_before_sketch_conversion(self):
        self.adapter.create_sketch(self.design, HelixParameters(2, 5, 0.5),
                                   AxisFrame((10, 20, 30), (1, 0, 0)))
        points = self.sketch.sketchCurves.sketchFittedSplines.add.call_args.args[0]
        for actual, expected in zip(points[-1], (15, 21, 30)):
            self.assertAlmostEqual(actual, expected)

    def test_sections_share_fusion_endpoint(self):
        add = self.sketch.sketchCurves.sketchFittedSplines.add
        first, second = Mock(), Mock()
        add.side_effect = [first, second]
        model = SegmentedHelix((HelixSegment.constant(2, 2, 1), HelixSegment(2, 2, 3, 1, 2)))
        self.adapter.create_sketch(self.design, model)
        self.assertEqual(add.call_count, 2)
        self.assertIs(add.call_args_list[1].args[0][0], first.endSketchPoint)
        self.sketch.geometricConstraints.addTangent.assert_not_called()

    def test_tangent_constraints_join_each_adjacent_pair(self):
        splines = [Mock(), Mock(), Mock()]
        self.sketch.sketchCurves.sketchFittedSplines.add.side_effect = splines
        model = SegmentedHelix((HelixSegment.constant(2, 2, 1),) * 3)
        self.adapter.create_sketch(self.design, model, tangent_joins=True)
        tangent = self.sketch.geometricConstraints.addTangent
        self.assertEqual(tangent.call_count, 2)
        self.assertEqual(tangent.call_args_list[0].args, (splines[0], splines[1]))
        self.assertEqual(tangent.call_args_list[1].args, (splines[1], splines[2]))
        self.sketch.deleteMe.assert_not_called()

    def test_one_section_needs_no_tangent_constraint(self):
        self.adapter.create_sketch(self.design, HelixParameters(2, 5, 0.5), tangent_joins=True)
        self.sketch.geometricConstraints.addTangent.assert_not_called()

    def test_failed_tangent_constraint_removes_whole_sketch(self):
        model = SegmentedHelix((HelixSegment.constant(2, 2, 1),) * 3)
        for failure in (None, RuntimeError('Solver error')):
            with self.subTest(failure=failure):
                self.sketch.deleteMe.reset_mock()
                self.sketch.geometricConstraints.addTangent.side_effect = [Mock(), failure]
                with self.assertRaisesRegex(RuntimeError, 'Abschnitt 2 und 3'):
                    self.adapter.create_sketch(self.design, model, tangent_joins=True)
                self.sketch.deleteMe.assert_called_once()

    def test_later_section_failure_removes_entire_sketch(self):
        add = self.sketch.sketchCurves.sketchFittedSplines.add
        add.side_effect = [Mock(), RuntimeError('Second segment failed')]
        model = SegmentedHelix((HelixSegment.constant(2, 2, 1),) * 2)
        with self.assertRaises(RuntimeError):
            self.adapter.create_sketch(self.design, model)
        self.sketch.deleteMe.assert_called_once()

    def test_only_section_boundary_markers_without_reducing_sampling(self):
        splines = [Mock(), Mock(), Mock()]
        self.sketch.sketchCurves.sketchFittedSplines.add.side_effect = splines
        # Simulate solver-adjusted endpoint coordinates.
        splines[0].startSketchPoint.geometry = (1, 0, 0)
        for index, spline in enumerate(splines):
            spline.endSketchPoint.geometry = (1, 0, 2 * (index + 1))
        model = SegmentedHelix((HelixSegment.constant(2, 2, 1),) * 3)
        self.adapter.create_sketch(self.design, model, tangent_joins=True)
        self.assertFalse(self.sketch.arePointsShown)
        markers = self.sketch.sketchPoints.add.call_args_list
        self.assertEqual([call.args[0] for call in markers],
                         [(1, 0, 0), (1, 0, 2), (1, 0, 4), (1, 0, 6)])
        for call in self.sketch.sketchCurves.sketchFittedSplines.add.call_args_list:
            self.assertEqual(len(call.args[0]), 65)

    def test_marker_failure_cleans_up_sketch(self):
        self.sketch.sketchPoints.add.return_value = None
        with self.assertRaisesRegex(RuntimeError, 'Abschnittsmarkierung'):
            self.adapter.create_sketch(self.design, HelixParameters(2, 5, 0.5))
        self.sketch.deleteMe.assert_called_once()


if __name__ == '__main__':
    unittest.main()

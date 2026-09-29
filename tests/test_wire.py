import importlib
import math
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))
from HelixPathPilot.core.wire_clearance import check_clearance, segment_distance, validate_diameter


class ClearanceTests(unittest.TestCase):
    def helix(self, pitch=0.5, turns=3):
        return [(math.cos(i*math.tau/256), math.sin(i*math.tau/256), pitch*i/256)
                for i in range(turns*256+1)]

    def test_valid_thin_wire(self):
        check_clearance(self.helix(), 0.1, 0.0001)

    def test_adjacent_turns_overlap_or_touch(self):
        for diameter in (0.5, 0.6):
            with self.assertRaisesRegex(ValueError, 'überschneiden'):
                check_clearance(self.helix(), diameter, 0.0001)

    def test_pitch_alone_is_not_sufficient(self):
        with self.assertRaises(ValueError):
            check_clearance(self.helix(pitch=2), 1.95, 0.0001)

    def test_straight_local_neighbours_are_not_collisions(self):
        check_clearance([(0, 0, i/100) for i in range(101)], 0.2, 0.0001)

    def test_crossing_distant_segments(self):
        with self.assertRaises(ValueError):
            check_clearance([(-2, 0, 0), (2, 0, 0), (2, 2, 0),
                             (0, 2, 0), (0, -2, 0)], 0.1, 0.0001)

    def test_segment_distances(self):
        self.assertAlmostEqual(segment_distance((0,0,0), (2,0,0), (1,-1,1), (1,1,1)), 1)
        self.assertAlmostEqual(segment_distance((0,0,0), (1,0,0), (2,0,0), (3,0,0)), 1)
        self.assertAlmostEqual(segment_distance((0,0,0), (2,0,0), (1,-1,0), (1,1,0)), 0)

    def test_invalid_diameter(self):
        for diameter in (0, -1, math.inf, math.nan, True):
            with self.assertRaises(ValueError):
                validate_diameter(diameter)


class WireBuilderTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        adsk.fusion = types.ModuleType('adsk.fusion')
        adsk.core.ObjectCollection = Mock()
        adsk.core.ValueInput = types.SimpleNamespace(createByReal=lambda x: x)
        for name, key in [('ChainedCurveOptions', 'noChainedCurves'),
                          ('PathDistanceTypes', 'ProportionalPathDistanceType'),
                          ('FeatureOperations', 'NewBodyFeatureOperation'),
                          ('SweepOrientationTypes', 'PerpendicularOrientationType'),
                          ('FeatureHealthStates', 'HealthyFeatureHealthState')]:
            setattr(adsk.fusion, name, types.SimpleNamespace(**{key: 0}))
        adsk.fusion.Path = Mock()
        commands = types.ModuleType('HelixPathPilot.commands')
        commands.__path__ = [str(Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot/commands')]
        module_patch = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': adsk.core,
            'adsk.fusion': adsk.fusion, 'HelixPathPilot.commands': commands})
        module_patch.start()
        self.addCleanup(module_patch.stop)
        # Avoid executing the add-in command package's startup imports.
        package = types.ModuleType('HelixPathPilot.commands.createParametricHelix')
        package.__path__ = [str(Path(commands.__path__[0]) / 'createParametricHelix')]
        sys.modules[package.__name__] = package
        sys.modules.pop(package.__name__ + '.wire_builder', None)
        self.builder = importlib.import_module(package.__name__ + '.wire_builder')
        self.design, self.sketch, self.spline = Mock(), Mock(), Mock()
        self.sketch.sketchCurves.sketchFittedSplines.count = 1
        self.sketch.sketchCurves.sketchFittedSplines.item.return_value = self.spline
        root = self.design.rootComponent
        self.plane = root.constructionPlanes.add.return_value
        self.profile = root.sketches.add.return_value
        self.profile.profiles.count = 1
        self.feature = root.features.sweepFeatures.add.return_value
        self.feature.healthState = 0
        self.feature.bodies.count = 1
        self.feature.bodies.item.return_value.isSolid = True
        evaluator = self.spline.worldGeometry.evaluator
        evaluator.getParameterExtents.return_value = (True, 0, 1)
        evaluator.getStrokes.return_value = (True, [types.SimpleNamespace(x=0,y=0,z=i) for i in (0,1)])
        evaluator.getCurvature.return_value = (True, Mock(), 0)
        tangent = Mock()
        tangent.angleTo.return_value = 0
        evaluator.getTangent.return_value = (True, tangent)

    def test_sweep_success(self):
        result = self.builder.create_wire(self.design, self.sketch, 0.1)
        self.assertIs(result, self.feature)
        self.profile.sketchCurves.sketchCircles.addByCenterRadius.assert_called_once()
        self.assertEqual(self.profile.sketchCurves.sketchCircles.addByCenterRadius.call_args.args[1], 0.05)
        self.assertFalse(self.sketch.isLightBulbOn)
        self.feature.deleteMe.assert_not_called()

    def test_curvature_rejected_before_auxiliary_geometry(self):
        self.spline.worldGeometry.evaluator.getCurvature.return_value = (True, Mock(), 30)
        with self.assertRaisesRegex(ValueError, 'Krümmung'):
            self.builder.create_wire(self.design, self.sketch, 0.1)
        self.design.rootComponent.constructionPlanes.add.assert_not_called()

    def test_colliding_spline_rejected_before_sweep(self):
        points = ClearanceTests().helix()
        self.spline.worldGeometry.evaluator.getStrokes.return_value = (
            True, [types.SimpleNamespace(x=x, y=y, z=z) for x, y, z in points])
        with self.assertRaisesRegex(ValueError, 'überschneiden'):
            self.builder.create_wire(self.design, self.sketch, 0.6)
        self.design.rootComponent.features.sweepFeatures.add.assert_not_called()

    def test_nontangent_sections_are_rejected(self):
        tangent = self.spline.worldGeometry.evaluator.getTangent.return_value[1]
        tangent.angleTo.return_value = 0.5
        with self.assertRaisesRegex(ValueError, 'G1'):
            self.builder._check_path([self.spline, self.spline], 0.1)

    def test_multiple_sections_are_all_added_to_path(self):
        second = Mock()
        self.sketch.sketchCurves.sketchFittedSplines.count = 2
        self.sketch.sketchCurves.sketchFittedSplines.item.side_effect = [self.spline, second]
        with patch.object(self.builder, '_check_path') as check:
            self.builder.create_wire(self.design, self.sketch, 0.1)
        check.assert_called_once_with([self.spline, second], 0.1)
        collection = self.builder.adsk.core.ObjectCollection.create.return_value
        self.assertEqual([call.args[0] for call in collection.add.call_args_list], [self.spline, second])

    def test_kernel_failure_cleans_auxiliary_geometry(self):
        self.design.rootComponent.features.sweepFeatures.add.side_effect = RuntimeError('kernel')
        with self.assertRaisesRegex(RuntimeError, 'kernel'):
            self.builder.create_wire(self.design, self.sketch, 0.1)
        self.profile.deleteMe.assert_called_once()
        self.plane.deleteMe.assert_called_once()
        self.sketch.deleteMe.assert_not_called()

    def test_unhealthy_body_is_deleted(self):
        self.feature.healthState = 2
        self.feature.errorOrWarningMessage = 'invalid'
        with self.assertRaisesRegex(RuntimeError, 'invalid'):
            self.builder.create_wire(self.design, self.sketch, 0.1)
        self.feature.deleteMe.assert_called_once()

    def test_failed_evaluation_is_not_silently_accepted(self):
        self.spline.worldGeometry.evaluator.getStrokes.return_value = (False, [])
        with self.assertRaises(ValueError):
            self.builder.create_wire(self.design, self.sketch, 0.1)
        self.design.rootComponent.features.sweepFeatures.add.assert_not_called()

"""Preview uses a constant number of graphics calls, never sketch solving."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
from HelixPathPilot.core.axis import AxisFrame
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix


class PreviewTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.fusion = types.ModuleType('adsk.fusion')
        adsk.fusion.CustomGraphicsCoordinates = types.SimpleNamespace(create=lambda values: values)
        adsk.fusion.CustomGraphicsPointTypes = types.SimpleNamespace(PointCloudCustomGraphicsPointType=1)
        modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.fusion': adsk.fusion})
        modules.start()
        self.addCleanup(modules.stop)
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.commands.createParametricHelix.preview_graphics',
            ADDIN / 'commands/createParametricHelix/preview_graphics.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.design = Mock()
        self.group = self.design.rootComponent.customGraphicsGroups.add.return_value
        self.preview = module.HelixPreview(self.design)
        self.model = SegmentedHelix((HelixSegment.constant(2, 2, 1),) * 3)

    def test_one_line_strip_and_boundary_indices_in_world_coordinates(self):
        self.preview.show(self.model, AxisFrame((10, 20, 30), (1, 0, 0)))
        coords, indices, strip = self.group.addLines.call_args.args
        self.assertEqual(coords[:3], [10, 21, 30])
        self.assertEqual(len(coords), 193 * 3)
        self.assertTrue(strip)
        self.assertEqual(indices, [])
        self.assertEqual(self.group.addPointSet.call_args.args[1], [0, 64, 128, 192])
        self.assertFalse(self.group.isSelectable)
        self.design.rootComponent.sketches.add.assert_not_called()

    def test_identical_preview_reused_and_changed_axis_rebuilt(self):
        self.preview.show(self.model, AxisFrame())
        self.preview.show(self.model, AxisFrame())
        self.assertEqual(self.group.addLines.call_count, 1)
        self.preview.show(self.model, AxisFrame(direction=(1, 0, 0)))
        self.assertEqual(self.group.addLines.call_count, 2)
        self.group.deleteMe.assert_called_once()

    def test_cleanup_is_idempotent_and_accepts_fusion_rollback(self):
        self.preview.show(self.model, AxisFrame())
        self.preview.clear()
        self.preview.clear()
        self.group.deleteMe.assert_called_once()
        self.preview.show(self.model, AxisFrame())
        self.group.isValid = False
        self.preview.clear()
        self.group.deleteMe.assert_called_once()

    def test_failed_graphics_creation_cleans_up(self):
        self.group.addLines.return_value = None
        with self.assertRaises(RuntimeError):
            self.preview.show(self.model, AxisFrame())
        self.group.deleteMe.assert_called_once()
        self.assertIsNone(self.preview.group)

"""Preview colors sections without sketch solving or per-point graphics calls."""

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
        adsk.core = types.ModuleType('adsk.core')
        adsk.core.Color = types.SimpleNamespace(create=lambda *rgba: rgba)
        adsk.fusion = types.ModuleType('adsk.fusion')
        adsk.fusion.CustomGraphicsSolidColorEffect = types.SimpleNamespace(create=lambda color: color)
        adsk.fusion.CustomGraphicsCoordinates = types.SimpleNamespace(create=lambda values: values)
        adsk.fusion.CustomGraphicsPointTypes = types.SimpleNamespace(PointCloudCustomGraphicsPointType=1)
        modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        modules.start()
        self.addCleanup(modules.stop)
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.commands.createParametricHelix.preview_graphics',
            ADDIN / 'commands/createParametricHelix/preview_graphics.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.design = Mock()
        self.group = self.design.rootComponent.customGraphicsGroups.add.return_value
        self.lines = []
        def add_line(*args):
            line = Mock()
            self.lines.append(line)
            return line
        self.group.addLines.side_effect = add_line
        self.preview = module.HelixPreview(self.design)
        self.model = SegmentedHelix((HelixSegment.constant(2, 2, 1),) * 3)

    def test_colored_sections_and_boundary_indices_in_world_coordinates(self):
        self.preview.show(self.model, AxisFrame((10, 20, 30), (1, 0, 0)))
        coords, indices, strip = self.group.addLines.call_args_list[0].args
        self.assertEqual(coords[:3], [10, 21, 30])
        self.assertEqual(len(coords), 193 * 3)
        self.assertTrue(strip)
        self.assertEqual(indices, list(range(65)))
        self.assertEqual(self.group.addLines.call_args_list[1].args[1], list(range(64, 129)))
        self.assertEqual(self.group.addLines.call_args_list[2].args[1], list(range(128, 193)))
        self.assertEqual(len({line.color for line in self.lines}), 3)
        from HelixPathPilot.core.preview_colors import section_color
        self.assertEqual([line.color for line in self.lines],
                         [(*section_color(i), 255) for i in range(3)])
        self.assertEqual(self.group.addPointSet.call_args.args[1], [0, 64, 128, 192])
        self.assertFalse(self.group.isSelectable)
        self.design.rootComponent.sketches.add.assert_not_called()

    def test_identical_preview_reused_and_changed_axis_rebuilt(self):
        self.preview.show(self.model, AxisFrame())
        self.preview.show(self.model, AxisFrame())
        self.assertEqual(self.group.addLines.call_count, 3)
        self.preview.show(self.model, AxisFrame(direction=(1, 0, 0)))
        self.assertEqual(self.group.addLines.call_count, 6)
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
        self.group.addLines.side_effect = None
        self.group.addLines.return_value = None
        with self.assertRaises(RuntimeError):
            self.preview.show(self.model, AxisFrame())
        self.group.deleteMe.assert_called_once()
        self.assertIsNone(self.preview.group)

    def test_all_32_sections_have_distinct_colors_and_bounded_calls(self):
        model = SegmentedHelix((HelixSegment.constant(1, 2, 1),) * 32)
        self.preview.show(model, AxisFrame())
        self.assertEqual(len({line.color for line in self.lines}), 32)
        self.assertEqual(self.group.addLines.call_count, 32)
        self.group.addPointSet.assert_called_once()

    def test_failure_after_first_section_removes_whole_preview(self):
        self.group.addLines.side_effect = [Mock(), None]
        with self.assertRaises(RuntimeError):
            self.preview.show(self.model, AxisFrame())
        self.group.deleteMe.assert_called_once()
        self.assertIsNone(self.preview.key)

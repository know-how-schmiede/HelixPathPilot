"""Surface eligibility checks without a running Fusion process."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class SurfaceSelectionTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        adsk.fusion = types.ModuleType('adsk.fusion')
        adsk.core.SurfaceTypes = types.SimpleNamespace(CylinderSurfaceType=1, ConeSurfaceType=2)
        adsk.fusion.BRepFace = types.SimpleNamespace(
            cast=lambda entity: entity if entity.kind == 'face' else None)
        modules = patch.dict(sys.modules, {
            'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        modules.start()
        self.addCleanup(modules.stop)
        path = Path(__file__).resolve().parents[1] / (
            'Fusion_addin/HelixPathPilot/commands/createSurfaceHelix/surface_selection.py')
        spec = importlib.util.spec_from_file_location('surface_selection', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def selection(self, surface_type=1, valid=True, kind='face', count=1):
        selection = Mock(selectionCount=count)
        selection.selection.return_value.entity = types.SimpleNamespace(
            kind=kind, isValid=valid, geometry=types.SimpleNamespace(surfaceType=surface_type))
        return selection

    def test_cylinder_and_cone(self):
        for kind, label in ((1, 'Zylindermantelfläche'), (2, 'Kegelmantelfläche')):
            self.assertEqual(self.module.selected_surface_kind(self.selection(kind)), label)

    def test_other_surface_types_rejected(self):
        for kind in (0, 3, 4, 5, 6, 7):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.module.selected_surface_kind(self.selection(kind))

    def test_empty_or_multiple_selection_rejected(self):
        for count in (0, 2):
            with self.assertRaises(ValueError):
                self.module.selected_surface_kind(self.selection(count=count))

    def test_invalid_face_and_whole_body_rejected(self):
        for selection in (self.selection(valid=False), self.selection(kind='body')):
            with self.assertRaises(ValueError):
                self.module.selected_surface_kind(selection)

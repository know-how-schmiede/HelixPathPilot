"""Surface eligibility checks without a running Fusion process."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
import math
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))


class SurfaceSelectionTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        adsk.fusion = types.ModuleType('adsk.fusion')
        adsk.core.SurfaceTypes = types.SimpleNamespace(CylinderSurfaceType=1, ConeSurfaceType=2)
        for name, kind in (('Circle3D', 'circle'), ('Line3D', 'line')):
            setattr(adsk.core, name, types.SimpleNamespace(cast=lambda curve, kind=kind:
                curve if curve.kind == kind else None))
        adsk.fusion.BRepFace = types.SimpleNamespace(
            cast=lambda entity: entity if entity.kind == 'face' else None)
        modules = patch.dict(sys.modules, {
            'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
        modules.start()
        self.addCleanup(modules.stop)
        path = Path(__file__).resolve().parents[1] / (
            'Fusion_addin/HelixPathPilot/commands/createSurfaceHelix/surface_selection.py')
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.commands.createSurfaceHelix.surface_selection', path)
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

    def test_extract_context_axis_and_rims(self):
        vector = lambda *xyz: types.SimpleNamespace(asArray=lambda: xyz)
        selection = self.selection()
        face = selection.selection(0).entity
        face.geometry.origin = vector(10, 20, 30)
        face.geometry.axis = vector(1, 0, 0)
        face.area = 20 * math.pi
        face.edges = [types.SimpleNamespace(geometry=types.SimpleNamespace(
            kind='circle', center=vector(x, 20, 30), normal=vector(1, 0, 0), radius=2))
            for x in (18, 13)]
        face.edges.append(types.SimpleNamespace(geometry=types.SimpleNamespace(kind='line')))
        profile = self.module.selected_surface_profile(selection)
        self.assertEqual(profile.axis.origin, (13, 20, 30))
        self.assertEqual(profile.length, 5)
        self.assertEqual(profile.radius_at(2), 2)
        face.edges.append(types.SimpleNamespace(geometry=types.SimpleNamespace(kind='arc')))
        with self.assertRaisesRegex(ValueError, 'Teilflächen'):
            self.module.selected_surface_profile(selection)

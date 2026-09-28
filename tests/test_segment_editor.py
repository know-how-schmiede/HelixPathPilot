"""Exercise dialog state with lightweight Fusion input doubles."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin' / 'HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))


class Input:
    def __init__(self, identifier, name, value=None):
        self.id, self.name, self.value = identifier, name, value
        self.isValidExpression = True
        self.isEnabled = True
        self.deleted = False

    def deleteMe(self):
        self.deleted = True
        return True


class Inputs:
    def addGroupCommandInput(self, identifier, name):
        group = Input(identifier, name)
        group.children = Inputs()
        return group

    def addValueInput(self, identifier, name, units, value):
        return Input(identifier, name, value)

    def addBoolValueInput(self, identifier, name, *args):
        return Input(identifier, name, False)


class EditorTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        core = types.ModuleType('adsk.core')
        adsk.core = core
        core.ValueInput = types.SimpleNamespace(createByReal=lambda value: value)
        modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': core})
        modules.start()
        self.addCleanup(modules.stop)
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.commands.createParametricHelix.segment_editor',
            ADDIN / 'commands/createParametricHelix/segment_editor.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.editor_type = module.SegmentEditor
        self.editor = module.SegmentEditor(Inputs(), 'mm')

    def test_initial_values_and_append_inherit_endpoint(self):
        fields = self.editor.rows[0][1]
        fields['diameter_end'].value = 4
        fields['pitch_end'].value = 2
        self.editor.changed('add_section')
        model = self.editor.read()
        self.assertEqual(model.total_length, 10)
        self.assertEqual(model.segments[1].diameter_start, 4)
        self.assertEqual(model.segments[1].pitch_start, 2)
        self.assertFalse(self.editor.rows[1][1]['diameter_start'].isEnabled)

    def test_linked_diameter_and_middle_deletion(self):
        self.editor.changed('add_section')
        self.editor.changed('add_section')
        fields = self.editor.rows[0][1]
        fields['diameter_end'].value = 7
        self.editor.changed(fields['diameter_end'].id)
        self.assertEqual(self.editor.rows[1][1]['diameter_start'].value, 7)
        group, _, remove = self.editor.rows[1]
        self.editor.changed(remove.id)
        self.assertTrue(group.deleted)
        self.assertEqual(self.editor.rows[1][0].name, 'Abschnitt 2')
        self.assertEqual(self.editor.read().segments[1].diameter_start, 7)

    def test_first_deletion_unlocks_start_and_last_cannot_be_removed(self):
        self.editor.changed('add_section')
        self.editor.changed(self.editor.rows[0][2].id)
        self.assertTrue(self.editor.rows[0][1]['diameter_start'].isEnabled)
        self.assertFalse(self.editor.rows[0][2].isEnabled)
        self.editor.changed(self.editor.rows[0][2].id)
        self.assertEqual(len(self.editor.rows), 1)

    def test_invalid_append_preserves_rows_and_recovers(self):
        field = self.editor.rows[0][1]['pitch_end']
        field.isValidExpression = False
        with self.assertRaises(ValueError):
            self.editor.changed('add_section')
        self.assertEqual(len(self.editor.rows), 1)
        self.assertFalse(self.editor.busy)
        field.isValidExpression = True
        self.editor.changed('add_section')
        self.assertEqual(len(self.editor.rows), 2)

    def test_row_limit_and_separate_sessions(self):
        for _ in range(31):
            self.editor.changed('add_section')
        self.assertFalse(self.editor.add_button.isEnabled)
        with self.assertRaises(ValueError):
            self.editor.changed('add_section')
        other = self.editor_type(Inputs(), 'in')
        self.assertEqual(len(other.rows), 1)
        self.assertEqual(len(self.editor.rows), 32)


if __name__ == '__main__':
    unittest.main()

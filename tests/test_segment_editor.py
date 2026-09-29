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
        self.id, self._name, self.value = identifier, name, value
        self.isValidExpression = True
        self.isEnabled = True
        self.deleted = False

    @property
    def name(self):
        # Fusion CommandInput.name is read-only, including GroupCommandInput.
        return self._name

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

    def test_load_replaces_rows_and_keeps_unique_ids(self):
        from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix
        old = self.editor.rows[0][0]
        model = SegmentedHelix((HelixSegment.constant(2, 3, 1),
                                HelixSegment.constant(4, 3, 2)))
        self.editor.load(model)
        self.assertTrue(old.deleted)
        self.assertEqual(self.editor.read(), model)
        self.assertFalse(self.editor.busy)
        self.assertNotEqual(old.id, self.editor.rows[0][0].id)
        self.editor.changed('add_section')
        self.assertEqual(len(self.editor.rows), 3)

    def test_failed_load_preserves_original_rows(self):
        from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix
        original = self.editor.read()
        with patch.object(self.editor.container.children, 'addGroupCommandInput',
                          side_effect=RuntimeError('Input failed')):
            with self.assertRaises(RuntimeError):
                self.editor.load(SegmentedHelix((HelixSegment.constant(2, 3, 1),)))
        self.assertEqual(self.editor.read(), original)
        self.assertFalse(self.editor.busy)

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
        self.assertEqual(self.editor.rows[1][0].name, 'Abschnitt 3')
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

    def test_initial_heading_and_read_only_name(self):
        self.assertEqual(self.editor.rows[0][0].name, 'Abschnitt 1')
        self.assertFalse(self.editor.rows[0][2].isEnabled)
        with self.assertRaises(AttributeError):
            self.editor.rows[0][0].name = 'Invalid write'

    def test_axis_length_preserves_proportions_and_other_values(self):
        self.editor.changed('add_section')
        self.editor.rows[1][1]['length'].value = 10
        self.editor.fit_total_length(6)
        model = self.editor.read()
        self.assertEqual([s.length for s in model.segments], [2, 4])
        self.assertEqual(model.total_length, 6)
        self.assertEqual(model.segments[0].pitch_start, 0.5)
        self.assertFalse(self.editor.busy)

    def test_invalid_axis_length_does_not_change_inputs(self):
        for length in (0, -1, float('inf'), float('nan'), 1000):
            with self.subTest(length=length), self.assertRaises(ValueError):
                self.editor.fit_total_length(length)
            self.assertEqual(self.editor.read().total_length, 5)

    def test_all_32_starts_follow_immediate_predecessor(self):
        for _ in range(31):
            self.editor.changed('add_section')
        for index, (_, fields, _) in enumerate(self.editor.rows):
            fields['diameter_end'].value = index + 3
        # No inputChanged event: read must repair every displayed linked value.
        model = self.editor.read()
        for index in range(1, 32):
            fields = self.editor.rows[index][1]
            self.assertFalse(fields['diameter_start'].isEnabled)
            self.assertEqual(fields['diameter_start'].value, index + 2)
            self.assertEqual(model.segments[index].diameter_start, index + 2)

    def test_chain_relinks_after_middle_and_first_removal(self):
        for _ in range(4):
            self.editor.changed('add_section')
        for index, (_, fields, _) in enumerate(self.editor.rows):
            fields['diameter_end'].value = index + 3
        self.editor.changed(self.editor.rows[2][2].id)
        self.editor.changed(self.editor.rows[0][2].id)
        model = self.editor.read()
        self.assertTrue(self.editor.rows[0][1]['diameter_start'].isEnabled)
        for index in range(1, len(model.segments)):
            self.assertEqual(model.segments[index].diameter_start, model.segments[index - 1].diameter_end)
            self.assertEqual(self.editor.rows[index][1]['diameter_start'].value,
                             model.segments[index - 1].diameter_end)


if __name__ == '__main__':
    unittest.main()

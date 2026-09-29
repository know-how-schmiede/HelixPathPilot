"""Check tab wiring and mode safety with isolated Fusion doubles."""

import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))


class Inputs:
    def __init__(self):
        self.items = {}

    def itemById(self, key):
        # Intentionally local: catch accidental lookups across tab boundaries.
        return self.items.get(key)

    def __getattr__(self, method):
        if not method.startswith('add'):
            raise AttributeError(method)

        def add(key, name, *args):
            item = Mock(id=key, isValidExpression=True, selectionCount=0)
            item.children = Inputs()
            item.isVisible = True
            if method == 'addValueInput':
                item.value = args[-1]
            elif method == 'addBoolValueInput':
                item.value = args[-1]
            elif method == 'addDropDownCommandInput':
                item.selectedItem = types.SimpleNamespace(index=0)
                entries = []
                class ListItem:
                    def __init__(self, index):
                        self.index = index
                    @property
                    def isSelected(self):
                        return item.selectedItem is self
                    @isSelected.setter
                    def isSelected(self, value):
                        if value:
                            item.selectedItem = self
                def add_entry(label, selected, *unused):
                    entry = ListItem(len(entries))
                    entries.append(entry)
                    if selected:
                        entry.isSelected = True
                    return entry
                item.listItems.add.side_effect = add_entry
                item.listItems.item.side_effect = lambda index: entries[index]
            elif method == 'addImageCommandInput':
                if not Path(args[0]).is_file():
                    raise ValueError('Missing packaged logo')
            self.items[key] = item
            return item
        return add


class DialogTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        adsk.fusion = types.ModuleType('adsk.fusion')
        design = Mock()
        design.unitsManager.defaultLengthUnits = 'mm'
        design.unitsManager.formatValue.return_value = '50 mm'
        adsk.core.Application = Mock()
        adsk.core.Application.get.return_value.activeProduct = design
        adsk.core.ValueInput = types.SimpleNamespace(
            createByString=lambda text: 0.0, createByReal=lambda value: value)
        adsk.core.DropDownStyles = types.SimpleNamespace(TextListDropDownStyle=0)
        adsk.fusion.Design = types.SimpleNamespace(cast=lambda value: value)
        package = types.ModuleType('HelixPathPilot.commands')
        package.__path__ = [str(ADDIN / 'commands')]
        self.callbacks = {}
        utility = types.ModuleType('HelixPathPilot.lib.fusionAddInUtils')
        utility.add_handler = lambda event, callback, **kw: self.callbacks.update({event: callback})
        utility.handle_error = Mock()
        # Restore the entire module table so these doubles cannot leak to other tests.
        modules = patch.dict(sys.modules, {
            'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion,
            'HelixPathPilot.commands': package,
            'HelixPathPilot.lib.fusionAddInUtils': utility})
        modules.start()
        self.addCleanup(modules.stop)
        self.entry = importlib.import_module('HelixPathPilot.commands.createParametricHelix.entry')
        preview_patch = patch.object(self.entry, 'HelixPreview')
        self.graphics = preview_patch.start().return_value
        self.addCleanup(preview_patch.stop)
        self.root = Inputs()
        command = types.SimpleNamespace(commandInputs=self.root, validateInputs='validate',
            inputChanged='changed', execute='execute', executePreview='preview', destroy='destroy')
        self.entry.command_created(types.SimpleNamespace(command=command))
        self.create = self.root.itemById('create_tab').children

    def test_load_builtin_presets_into_actual_output(self):
        fields = self.create.itemById('presets').children
        choice = fields.itemById('preset_choice')
        self.assertEqual(choice.listItems.add.call_count, 3)
        # Packaged order: basic, surface, variable.
        choice.listItems.item(2).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_load')))
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](types.SimpleNamespace())
            model = create.call_args.args[1]
            self.assertEqual(len(model.segments), 2)
            self.assertEqual(model.total_length, 7.5)
        choice.listItems.item(1).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_load')))
        self.assertEqual(self.create.itemById('helix_mode').selectedItem.index, 1)
        self.assertTrue(self.create.itemById('surface_group').isVisible)
        surface = self.create.itemById('surface_group').children
        self.assertEqual(surface.itemById('surface_pitch_end').value, 1)
        event = types.SimpleNamespace()
        self.callbacks['validate'](event)
        self.assertFalse(event.areInputsValid)  # Loading never invents a face selection.
        choice.listItems.item(0).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_load')))
        self.callbacks['validate'](event)
        self.assertTrue(event.areInputsValid)
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](types.SimpleNamespace())
            self.assertEqual(len(create.call_args.args[1].segments), 1)

    def test_settings_value_reaches_sketch_and_nested_parameters_validate(self):
        event = types.SimpleNamespace()
        self.callbacks['validate'](event)
        self.assertTrue(event.areInputsValid)
        settings = self.root.itemById('settings_tab').children
        settings.itemById('tangent_joins').value = False
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](types.SimpleNamespace())
            self.assertFalse(create.call_args.kwargs['tangent_joins'])
        self.assertIsNotNone(self.root.itemById('info_tab').children.itemById('info_logo'))

    def test_surface_mode_blocks_creation_and_return_restores_validation(self):
        mode = self.create.itemById('helix_mode')
        mode.selectedItem.index = 1
        self.callbacks['changed'](types.SimpleNamespace(input=mode))
        self.assertFalse(self.create.itemById('parameter_group').isVisible)
        self.assertTrue(self.create.itemById('surface_group').isVisible)
        event = types.SimpleNamespace()
        self.callbacks['validate'](event)
        self.assertFalse(event.areInputsValid)
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](event)
            create.assert_not_called()
            self.assertTrue(event.executeFailed)
        mode.selectedItem.index = 0
        self.callbacks['changed'](types.SimpleNamespace(input=mode))
        self.callbacks['validate'](event)
        self.assertTrue(event.areInputsValid)
        self.assertTrue(self.create.itemById('parameter_group').isVisible)

    def test_preview_never_builds_sketch_and_can_be_disabled(self):
        event = types.SimpleNamespace()
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['preview'](event)
            self.assertFalse(event.isValidResult)
            self.graphics.show.assert_called_once()
            self.root.itemById('settings_tab').children.itemById('live_preview').value = False
            self.callbacks['preview'](event)
            self.assertFalse(event.isValidResult)
            create.assert_not_called()
            self.callbacks['execute'](types.SimpleNamespace())
            create.assert_called_once()

    def test_invalid_or_surface_input_never_creates_preview(self):
        event = types.SimpleNamespace()
        angle = self.create.itemById('parameter_group').children.itemById('start_angle')
        with patch.object(self.entry, 'create_sketch') as create:
            angle.isValidExpression = False
            self.callbacks['preview'](event)
            self.assertFalse(event.isValidResult)
            angle.isValidExpression = True
            self.create.itemById('helix_mode').selectedItem.index = 1
            self.callbacks['preview'](event)
            self.assertFalse(event.isValidResult)
            create.assert_not_called()

    def test_preview_failure_is_reported_and_next_preview_recovers(self):
        event = types.SimpleNamespace()
        status = self.create.itemById('parameter_group').children.itemById('preview_status')
        with patch.object(self.graphics, 'show', side_effect=[RuntimeError('Graphics'), Mock()]):
            self.callbacks['preview'](event)
            self.assertFalse(event.isValidResult)
            self.assertIn('Graphics', status.text)
            self.callbacks['preview'](event)
            self.assertFalse(event.isValidResult)
            self.assertIn('G1', status.text)

    def test_invalid_edit_and_destroy_clear_graphics(self):
        angle = self.create.itemById('parameter_group').children.itemById('start_angle')
        angle.isValidExpression = False
        self.callbacks['changed'](types.SimpleNamespace(input=angle))
        self.graphics.clear.assert_called_once()
        self.callbacks['destroy'](types.SimpleNamespace())
        self.assertEqual(self.graphics.clear.call_count, 2)
        self.assertEqual(self.entry._previews, [])

    def test_surface_preview_and_output_use_face_profile_not_hidden_parameters(self):
        from HelixPathPilot.core.axis import AxisFrame
        from HelixPathPilot.core.surface_profile import SurfaceProfile
        profile = SurfaceProfile(AxisFrame((10, 0, 0), (0, 1, 0)), 5, 2, 4)
        self.create.itemById('helix_mode').selectedItem.index = 1
        self.create.itemById('parameter_group').children.itemById('start_angle').isValidExpression = False
        fields = self.create.itemById('surface_group').children
        fields.itemById('surface_reverse').value = True
        fields.itemById('surface_offset').value = 0.5
        fields.itemById('surface_pitch_end').value = 1.5
        event = types.SimpleNamespace()
        with patch.object(self.entry, 'selected_surface_profile', return_value=profile), \
             patch.object(self.entry, 'selected_surface_kind', return_value='Kegelmantelfläche'), \
             patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['validate'](event)
            self.assertTrue(event.areInputsValid)
            self.callbacks['preview'](event)
            model, axis = self.graphics.show.call_args.args
            from HelixPathPilot.core.surface_helix import surface_helix
            expected_model, expected_axis = surface_helix(profile, 0.5, reverse=True, offset=0.5, pitch_end=1.5)
            self.assertEqual(model, expected_model)
            self.assertEqual(axis, expected_axis)
            create.assert_not_called()
            self.callbacks['execute'](event)
            self.assertEqual(create.call_args.args[1:], (model, axis))
            self.assertFalse(create.call_args.kwargs['tangent_joins'])
            self.assertEqual(create.return_value.name, 'HelixPathPilot – Surface Helix')
            end_pitch = fields.itemById('surface_pitch_end')
            end_pitch.isValidExpression = False
            self.callbacks['changed'](types.SimpleNamespace(input=end_pitch))
            self.graphics.clear.assert_called()
            self.callbacks['validate'](event)
            self.assertFalse(event.areInputsValid)
            self.graphics.show.reset_mock()
            self.callbacks['preview'](event)
            self.graphics.show.assert_not_called()
            create.reset_mock()
            self.callbacks['execute'](event)
            create.assert_not_called()
            end_pitch.isValidExpression = True
            self.callbacks['validate'](event)
            self.assertTrue(event.areInputsValid)
            end_pitch.value = -1
            self.callbacks['validate'](event)
            self.assertFalse(event.areInputsValid)
            end_pitch.value = 1.5
            fields.itemById('surface_pitch').value = 0
            self.callbacks['validate'](event)
            self.assertFalse(event.areInputsValid)

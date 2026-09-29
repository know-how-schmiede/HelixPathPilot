"""Check tab wiring and mode safety with isolated Fusion doubles."""

import importlib
from pathlib import Path
import sys
import types
import tempfile
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
            item.name = name
            item.children = Inputs()
            item.isVisible = True
            if method in ('addValueInput', 'addStringValueInput'):
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
                    entry.name = label
                    entries.append(entry)
                    if selected:
                        entry.isSelected = True
                    return entry
                item.listItems.add.side_effect = add_entry
                item.listItems.item.side_effect = lambda index: entries[index]
                def clear_entries():
                    entries.clear()
                    item.selectedItem = None
                item.listItems.clear.side_effect = clear_entries
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
        adsk.core.MessageBoxButtonTypes = types.SimpleNamespace(YesNoButtonType=3)
        adsk.core.DialogResults = types.SimpleNamespace(DialogYes=1, DialogOK=0)
        self.ui = adsk.core.Application.get.return_value.userInterface
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
        from HelixPathPilot.core.preset_store import PresetStore
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = PresetStore(self.temp.name)
        store_patch = patch.object(self.entry, 'PresetStore', return_value=self.store)
        store_patch.start()
        self.addCleanup(store_patch.stop)
        preview_patch = patch.object(self.entry, 'HelixPreview')
        self.graphics = preview_patch.start().return_value
        self.addCleanup(preview_patch.stop)
        self.root = Inputs()
        command = types.SimpleNamespace(commandInputs=self.root, validateInputs='validate',
            inputChanged='changed', execute='execute', executePreview='preview', destroy='destroy',
            setDialogInitialSize=Mock(), setDialogMinimumSize=Mock(), setDialogSize=Mock())
        self.command = command
        self.entry.command_created(types.SimpleNamespace(command=command))
        self.create = self.root.itemById('create_tab').children
        self.preset_fields = self.root.itemById('presets_tab').children.itemById('presets').children

    def test_wire_is_optional_and_sweeps_only_on_execute(self):
        enabled = self.create.itemById('wire_enabled')
        diameter = self.create.itemById('wire_diameter')
        self.assertFalse(enabled.value)
        self.assertFalse(diameter.isVisible)
        with patch.object(self.entry, 'create_sketch') as sketch, patch.object(self.entry, 'create_wire') as wire:
            self.callbacks['execute'](types.SimpleNamespace())
            wire.assert_not_called()
            enabled.value = True
            self.callbacks['changed'](types.SimpleNamespace(input=enabled))
            self.assertTrue(diameter.isVisible)
            self.callbacks['preview'](types.SimpleNamespace())
            wire.assert_not_called()
            self.callbacks['execute'](types.SimpleNamespace())
            self.assertEqual(wire.call_args.args[1:], (sketch.return_value, 0.1))

    def test_wire_error_removes_path_and_reports_failure(self):
        self.create.itemById('wire_enabled').value = True
        with patch.object(self.entry, 'create_sketch') as sketch, patch.object(
                self.entry, 'create_wire', side_effect=ValueError('Drahtdurchmesser zu groß')):
            event = types.SimpleNamespace()
            self.callbacks['execute'](event)
            self.assertTrue(event.executeFailed)
            self.assertIn('zu groß', event.executeFailedMessage)
            sketch.return_value.deleteMe.assert_called_once()

    def test_invalid_wire_diameter_blocks_execution_before_sketch(self):
        self.create.itemById('wire_enabled').value = True
        self.create.itemById('wire_diameter').value = -1
        event = types.SimpleNamespace()
        self.callbacks['validate'](event)
        self.assertFalse(event.areInputsValid)
        with patch.object(self.entry, 'create_sketch') as sketch:
            self.callbacks['execute'](event)
            sketch.assert_not_called()

    def test_dialog_size_is_bounded_on_open_and_section_add(self):
        self.command.setDialogSize.assert_called_with(520, 560)
        self.command.setDialogMinimumSize.assert_called_once_with(380, 300)
        self.assertIsNone(self.create.itemById('presets'))
        self.command.setDialogSize.reset_mock()
        self.callbacks['changed'](types.SimpleNamespace(input=types.SimpleNamespace(id='add_section')))
        self.command.setDialogSize.assert_called_once_with(520, 560)

    def test_remove_section_does_not_delete_event_source_or_resize(self):
        parameters = self.create.itemById('parameter_group').children
        self.callbacks['changed'](types.SimpleNamespace(input=types.SimpleNamespace(id='add_section')))
        group = parameters.itemById('sections').children.itemById('section_0')
        remove = parameters.itemById('remove_section')
        self.command.setDialogSize.reset_mock()
        self.callbacks['changed'](types.SimpleNamespace(input=remove))
        group.deleteMe.assert_not_called()
        self.assertFalse(group.isVisible)
        self.assertFalse(remove.isEnabled)
        self.assertFalse(group.children.itemById('section_0_length').isVisible)
        self.command.setDialogSize.assert_not_called()
        self.assertEqual(len(self.graphics.show.call_args.args[0].segments), 1)
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](types.SimpleNamespace())
            self.assertEqual(len(create.call_args.args[1].segments), 1)

    def test_graphics_cleanup_failure_cannot_prevent_section_removal(self):
        self.callbacks['changed'](types.SimpleNamespace(input=types.SimpleNamespace(id='add_section')))
        parameters = self.create.itemById('parameter_group').children
        group = parameters.itemById('sections').children.itemById('section_0')
        with patch.object(self.graphics, 'clear', side_effect=RuntimeError('Graphics rollback')):
            self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('remove_section')))
        self.assertFalse(group.isVisible)
        self.assertIn('Graphics rollback', parameters.itemById('error').text)
        self.entry.futil.handle_error.assert_called_with('Abschnitt entfernen', show_message_box=True)
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](types.SimpleNamespace())
            self.assertEqual(len(create.call_args.args[1].segments), 1)

    def test_central_remove_selects_middle_then_last_section(self):
        parameters = self.create.itemById('parameter_group').children
        for _ in range(2):
            self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('add_section')))
        groups = parameters.itemById('sections').children
        for i, length in enumerate((2, 3, 4)):
            group = groups.itemById(f'section_{i}')
            group.children.itemById(f'section_{i}_length').value = length
            self.assertIsNone(group.children.itemById(f'remove_section_{i}'))
        choice = parameters.itemById('remove_section_choice')
        choice.listItems.item(1).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=choice))
        self.assertTrue(groups.itemById('section_1').isVisible)
        self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('remove_section')))
        self.assertFalse(groups.itemById('section_1').isVisible)
        self.assertEqual([s.length for s in self.graphics.show.call_args.args[0].segments], [2, 4])
        # The selection now addresses the old third row despite its non-contiguous ID.
        choice.listItems.item(1).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=choice))
        self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('remove_section')))
        self.assertFalse(groups.itemById('section_2').isVisible)
        self.assertFalse(parameters.itemById('remove_section').isEnabled)
        with patch.object(self.entry, 'create_sketch') as create:
            self.callbacks['execute'](types.SimpleNamespace())
            self.assertEqual([s.length for s in create.call_args.args[1].segments], [2])

    def test_remove_target_survives_native_selection_change_during_validation(self):
        parameters = self.create.itemById('parameter_group').children
        for _ in range(2):
            self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('add_section')))
        choice = parameters.itemById('remove_section_choice')
        choice.listItems.item(1).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=choice))
        self.assertIn('Abschnitt 2', parameters.itemById('remove_section_target').text)
        # Simulate native selection changing before the action event. The user's
        # selection event, not a later native list index, determines the target.
        choice.listItems.item(2).isSelected = True
        self.callbacks['validate'](types.SimpleNamespace())
        self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('remove_section')))
        groups = parameters.itemById('sections').children
        self.assertFalse(groups.itemById('section_1').isVisible)
        self.assertTrue(groups.itemById('section_2').isVisible)
        self.assertIn('Abschnitt 1', parameters.itemById('remove_section_target').text)

    def test_remove_target_uses_label_even_if_native_index_is_stale(self):
        parameters = self.create.itemById('parameter_group').children
        for _ in range(2):
            self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('add_section')))
        choice = parameters.itemById('remove_section_choice')
        choice.selectedItem = types.SimpleNamespace(index=2, name='Abschnitt 1')
        self.callbacks['changed'](types.SimpleNamespace(input=choice))
        self.callbacks['changed'](types.SimpleNamespace(input=parameters.itemById('remove_section')))
        groups = parameters.itemById('sections').children
        self.assertFalse(groups.itemById('section_0').isVisible)
        self.assertTrue(groups.itemById('section_2').isVisible)

    def test_export_selection_then_import_as_user_preset_without_loading(self):
        from HelixPathPilot.core.preset_files import read_preset_file
        fields = self.preset_fields
        dialog = self.ui.createFileDialog.return_value
        dialog.filename = str(Path(self.temp.name) / 'export')
        dialog.showSave.return_value = 0
        parameters = self.create.itemById('parameter_group').children
        parameters.itemById('start_angle').value = 1.5
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_export')))
        path = Path(dialog.filename + '.helixpilot.json')
        exported = read_preset_file(path)
        self.assertEqual(exported.parameters.start_angle, 0)  # Saved selection, not edited inputs.
        dialog.filename = str(path)
        dialog.showOpen.return_value = 0
        self.ui.inputBox.return_value = ('Importiert', False)
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_import')))
        self.assertEqual(self.store.list()[0][0][1].name, 'Importiert')
        self.assertEqual(parameters.itemById('start_angle').value, 1.5)
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_load')))
        self.assertEqual(parameters.itemById('start_angle').value, 0)

    def test_import_export_cancel_and_bad_import_leave_state_unchanged(self):
        fields = self.preset_fields
        dialog = self.ui.createFileDialog.return_value
        dialog.showOpen.return_value = 1
        dialog.showSave.return_value = 1
        for key in ('preset_import', 'preset_export'):
            self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById(key)))
        self.assertEqual(self.store.list()[0], [])
        path = Path(self.temp.name) / 'broken.json'
        path.write_text('{', encoding='utf-8')
        dialog.filename = str(path)
        dialog.showOpen.return_value = 0
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_import')))
        self.assertIn('fehlgeschlagen', fields.itemById('preset_note').text)
        self.ui.inputBox.assert_not_called()
        self.assertEqual(self.store.list()[0], [])

    def test_export_checks_final_extension_before_overwriting(self):
        fields = self.preset_fields
        dialog = self.ui.createFileDialog.return_value
        dialog.filename = str(Path(self.temp.name) / 'existing')
        dialog.showSave.return_value = 0
        target = Path(dialog.filename + '.helixpilot.json')
        target.write_text('keep', encoding='utf-8')
        self.ui.messageBox.return_value = 0
        event = types.SimpleNamespace(input=fields.itemById('preset_export'))
        self.callbacks['changed'](event)
        self.assertEqual(target.read_text(), 'keep')
        self.ui.messageBox.assert_called_once()
        self.ui.messageBox.return_value = 1
        self.callbacks['changed'](event)
        from HelixPathPilot.core.preset_files import read_preset_file
        self.assertEqual(read_preset_file(target).mode, 'parametric')

    def test_import_name_cancel_and_duplicate_do_not_overwrite(self):
        from HelixPathPilot.core.presets import HelixPreset, SurfaceSettings
        preset = HelixPreset('Existing', SurfaceSettings())
        key = self.store.save(preset)
        source = Path(self.temp.name) / 'source.json'
        source.write_text(preset.to_json(), encoding='utf-8')
        dialog = self.ui.createFileDialog.return_value
        dialog.filename = str(source)
        dialog.showOpen.return_value = 0
        event = types.SimpleNamespace(input=self.preset_fields.itemById('preset_import'))
        self.ui.inputBox.return_value = ('Renamed', True)
        self.callbacks['changed'](event)
        self.assertEqual(len(self.store.list()[0]), 1)
        self.ui.inputBox.return_value = ('Existing', False)
        self.callbacks['changed'](event)
        self.assertIn('existiert bereits', self.preset_fields.itemById('preset_note').text)
        self.assertEqual(self.store.load(key), preset)

    def test_user_preset_save_load_delete_and_cancel(self):
        fields = self.preset_fields
        fields.itemById('preset_name').value = 'Meine Feder'
        parameters = self.create.itemById('parameter_group').children
        parameters.itemById('start_angle').value = 1.2
        def click(key):
            self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById(key)))
        click('preset_save')
        self.assertEqual(len(self.store.list()[0]), 1)
        self.assertTrue(fields.itemById('preset_delete').isEnabled)
        parameters.itemById('start_angle').value = 0
        click('preset_load')
        self.assertEqual(parameters.itemById('start_angle').value, 1.2)
        click('preset_save')
        self.assertIn('existiert bereits', fields.itemById('preset_note').text)
        self.ui.messageBox.return_value = 0
        click('preset_delete')
        self.assertEqual(len(self.store.list()[0]), 1)
        self.ui.messageBox.return_value = 1
        click('preset_delete')
        self.assertEqual(self.store.list()[0], [])
        self.assertFalse(fields.itemById('preset_delete').isEnabled)
        click('preset_delete')
        self.assertIn('Mitgelieferte', fields.itemById('preset_note').text)

    def test_surface_save_without_face_and_invalid_input(self):
        fields = self.preset_fields
        self.create.itemById('helix_mode').listItems.item(1).isSelected = True
        fields.itemById('preset_name').value = 'Surface gespeichert'
        surface = self.create.itemById('surface_group').children
        surface.itemById('surface_offset').value = -0.2
        event = types.SimpleNamespace(input=fields.itemById('preset_save'))
        surface.itemById('surface_pitch').isValidExpression = False
        self.callbacks['changed'](event)
        self.assertEqual(self.store.list()[0], [])
        surface.itemById('surface_pitch').isValidExpression = True
        self.callbacks['changed'](event)
        self.assertEqual(self.store.list()[0][0][1].parameters.offset, -0.2)

    def test_load_builtin_presets_into_actual_output(self):
        fields = self.preset_fields
        choice = fields.itemById('preset_choice')
        self.assertEqual(choice.listItems.add.call_count, 3)
        # Packaged order: basic, surface, variable.
        choice.listItems.item(2).isSelected = True
        self.callbacks['changed'](types.SimpleNamespace(input=fields.itemById('preset_load')))
        self.root.itemById('create_tab').activate.assert_called_once()
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

    def test_valid_edit_checks_cache_without_forcing_graphics_rebuild(self):
        angle = self.create.itemById('parameter_group').children.itemById('start_angle')
        self.callbacks['changed'](types.SimpleNamespace(input=angle))
        self.graphics.clear.assert_not_called()
        self.graphics.invalidate.assert_called_once()
        self.callbacks['preview'](types.SimpleNamespace())
        self.assertEqual(self.graphics.invalidate.call_args.args, self.graphics.show.call_args.args)

    def test_disabling_preview_clears_immediately_and_enabling_checks_current_path(self):
        live = self.root.itemById('settings_tab').children.itemById('live_preview')
        live.value = False
        self.callbacks['changed'](types.SimpleNamespace(input=live))
        self.graphics.clear.assert_called_once()
        self.graphics.invalidate.assert_not_called()
        live.value = True
        self.callbacks['changed'](types.SimpleNamespace(input=live))
        self.graphics.invalidate.assert_called_once()

    def test_non_geometry_settings_do_not_invalidate_preview(self):
        for key in ('wire_diameter', 'tangent_joins', 'preset_name'):
            self.callbacks['changed'](types.SimpleNamespace(input=types.SimpleNamespace(id=key)))
        self.graphics.clear.assert_not_called()
        self.graphics.invalidate.assert_not_called()

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

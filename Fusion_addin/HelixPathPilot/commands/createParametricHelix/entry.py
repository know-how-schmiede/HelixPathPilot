"""Create a section-based helix around a selected axis."""

from ...i18n import configure_from_fusion, tr

from pathlib import Path
from dataclasses import replace

import adsk.core
import adsk.fusion

from ... import config
from ...core.variable_helix import sampling_plan
from ...core.surface_helix import surface_helix
from ...core.presets import HelixPreset, SurfaceSettings
from ...core.preset_store import PresetStore
from ...core.preset_files import read_preset_file, write_preset_file, export_path
from ...lib import fusionAddInUtils as futil
from ...version import APP_NAME, VERSION
from .sketch_builder import create_sketch
from .wire_builder import create_wire
from ...core.wire_clearance import validate_diameter
from ...core.cleanup import cleanup_created
from .axis_selection import selected_axis, selected_axis_length
from .segment_editor import SegmentEditor
from .dialog_tabs import add_settings_and_info
from .preview_graphics import HelixPreview
from ..createSurfaceHelix.surface_selection import selected_surface_kind, selected_surface_profile
from ..presetManager.catalog import builtin_presets, preset_display_name

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createParametricHelix'
CMD_NAME = f'{APP_NAME} v{VERSION}'
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
LEGACY_PANEL_ID = 'SolidScriptsAddinsPanel'
ICON_FOLDER = str(Path(__file__).resolve().parents[2] / 'resources' / 'icons' / 'helix')
_definition_handlers = []
_sessions = []
_previews = []


def _panel(ui):
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    return workspace.toolbarPanels.itemById(PANEL_ID) if workspace else None


def start():
    app = adsk.core.Application.get()
    configure_from_fusion(app)
    ui = app.userInterface
    stop()
    panel = _panel(ui)
    if panel is None:
        raise RuntimeError(tr('The Create panel in the Solid workspace is missing.'))
    try:
        definition = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, tr('Create a multi-section helix with variable diameter and pitch.'),
            ICON_FOLDER,
        )
        futil.add_handler(definition.commandCreated, command_created,
                          local_handlers=_definition_handlers)
        control = panel.controls.addCommand(definition)
        control.isPromotedByDefault = True
        control.isPromoted = True
    except Exception:
        stop()
        raise


def stop():
    for preview in _previews:
        preview.clear()
    _previews.clear()
    ui = adsk.core.Application.get().userInterface
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    if workspace:
        # Also remove a control left at the old location during an update.
        for panel_id in (PANEL_ID, LEGACY_PANEL_ID):
            panel = workspace.toolbarPanels.itemById(panel_id)
            control = panel.controls.itemById(CMD_ID) if panel else None
            if control:
                control.deleteMe()
    definition = ui.commandDefinitions.itemById(CMD_ID)
    if definition:
        definition.deleteMe()
    _definition_handlers.clear()
    for handlers in _sessions:
        handlers.clear()
    _sessions.clear()


def _parameters(inputs, editor):
    if not inputs.itemById('start_angle').isValidExpression:
        raise ValueError(tr('Please enter a valid start angle.'))
    parameters = editor.read(inputs.itemById('start_angle').value,
                             inputs.itemById('right_handed').value)
    sampling_plan(parameters)
    return parameters


def command_created(args):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        app.userInterface.messageBox(tr('Please open a design document first.'), CMD_NAME)
        return
    command = args.command
    command.isExecutedWhenPreEmpted = False
    root_inputs = command.commandInputs
    create_tab = root_inputs.addTabCommandInput('create_tab', tr('Create helix'))
    create_inputs = create_tab.children
    preset_tab = root_inputs.addTabCommandInput('presets_tab', tr('Presets'))
    preset_group = preset_tab.children.addGroupCommandInput('presets', tr('Manage presets'))
    preset_group.isExpanded = True
    preset_inputs = preset_group.children
    preset_choice = preset_inputs.addDropDownCommandInput(
        'preset_choice', tr('Preset'), adsk.core.DropDownStyles.TextListDropDownStyle)
    presets, preset_errors = builtin_presets()
    store = PresetStore()
    user_entries, user_errors = store.list()
    preset_errors.extend(user_errors)
    preset_keys = [None] * len(presets) + [key for key, _ in user_entries]
    builtin_count = len(presets)
    presets.extend(preset for _, preset in user_entries)
    for index, preset in enumerate(presets):
        label = tr('Surface') if preset.mode == 'surface' else tr('Parametric')
        origin = tr('Custom') if preset_keys[index] else tr('Built-in')
        preset_choice.listItems.add(f'{preset_display_name(preset, builtin=preset_keys[index] is None)} ({label}, {origin})', index == 0)
    preset_load = preset_inputs.addBoolValueInput('preset_load', tr('Load preset'), False, '', False)
    preset_load.isEnabled = bool(presets)
    preset_name = preset_inputs.addStringValueInput('preset_name', tr('Custom preset name'), '')
    preset_inputs.addBoolValueInput('preset_save', tr('Save as custom preset'), False, '', False)
    preset_delete = preset_inputs.addBoolValueInput('preset_delete', tr('Delete custom preset'), False, '', False)
    preset_delete.isEnabled = bool(preset_keys and preset_keys[0])
    preset_inputs.addBoolValueInput('preset_import', tr('Import JSON preset'), False, '', False)
    preset_export = preset_inputs.addBoolValueInput('preset_export', tr('Export selected preset'), False, '', False)
    preset_export.isEnabled = bool(presets)
    preset_export.tooltip = tr('Exports the saved selection, not unsaved helix changes.')
    preset_note = preset_inputs.addTextBoxCommandInput('preset_note', '',
        tr(
            'Select and load a preset. Current parameters will be replaced; axis and lateral face'
            ' remain selected separately.'), 3, True)
    if preset_errors or not presets:
        preset_note.text = tr('Presets partially unavailable: ') + (
            '\n'.join(preset_errors) if preset_errors else tr('No preset files found.'))
    mode = create_inputs.addDropDownCommandInput(
        'helix_mode', tr('Mode'), adsk.core.DropDownStyles.TextListDropDownStyle)
    mode.listItems.add(tr('Parametric helix'), True)
    mode.listItems.add(tr('Surface helix'), False)
    wire_enabled = create_inputs.addBoolValueInput('wire_enabled', tr('Create wire body'), True, '', False)
    wire_diameter = create_inputs.addValueInput('wire_diameter', tr('Wire diameter'),
        design.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(0.1))
    wire_diameter.isVisible = False
    wire_note = create_inputs.addTextBoxCommandInput('wire_note', '',
        tr(
            'Preview shows the path. On OK: intersection check and sweep as a new body. Wire '
            'diameter is not saved in presets.'), 3, True)
    wire_note.isVisible = False
    surface_group = create_inputs.addGroupCommandInput('surface_group', tr('Surface helix'))
    surface_group.isExpanded = True
    surface_group.isVisible = False
    surface_inputs = surface_group.children
    surface_inputs.addTextBoxCommandInput('surface_help', '',
        tr(
            'Select a cylindrical or conical lateral face with two complete circular boundaries. '
            'Length and radius follow the face. Pitch is the axial distance per turn. Output is '
            'an approximated 3D spline.'), 3, True)
    surface_input = surface_inputs.addSelectionInput('surface', tr('Lateral face'), tr('Select lateral face'))
    surface_input.addSelectionFilter('Faces')
    surface_input.setSelectionLimits(0, 1)
    surface_input.isUseCurrentSelections = False
    units = design.unitsManager.defaultLengthUnits
    surface_pitch = surface_inputs.addValueInput('surface_pitch', tr('Start pitch'), units,
        adsk.core.ValueInput.createByReal(0.5))
    surface_pitch_end = surface_inputs.addValueInput('surface_pitch_end', tr('End pitch'), units,
        adsk.core.ValueInput.createByReal(0.5))
    surface_pitch.tooltip = tr('Axial pitch at the selected start boundary; must be positive.')
    surface_pitch_end.tooltip = (tr(
        'Pitch at the end boundary, linear along the axial length. Equal start and end values '
        'give constant pitch. When switching boundaries, values still follow the travel '
        'direction.'))
    surface_offset = surface_inputs.addValueInput('surface_offset', tr('Surface offset'), units,
        adsk.core.ValueInput.createByReal(0.0))
    surface_offset.tooltip = (tr(
        'Perpendicular distance to the lateral face. Positive: away from the axis; negative: '
        'towards the axis. On a cone, endpoints also shift axially. Direction is independent of '
        'inner or outer face.'))
    surface_angle = surface_inputs.addValueInput('surface_angle', tr('Start angle'), 'deg',
        adsk.core.ValueInput.createByReal(0.0))
    surface_right = surface_inputs.addBoolValueInput('surface_right', tr('Right-handed'), True, '', True)
    surface_reverse = surface_inputs.addBoolValueInput('surface_reverse', tr('Start at the other boundary'), True, '', False)
    surface_status = surface_inputs.addTextBoxCommandInput('surface_status', '', '', 6, True)
    parameter_group = create_inputs.addGroupCommandInput('parameter_group', tr('Helix parameters'))
    parameter_group.isExpanded = True
    inputs = parameter_group.children
    inputs.addTextBoxCommandInput(
        'axis_info', '', tr(
            'Without selection: global Z axis. For lines, the helix starts at the line start; for'
            ' construction axes, at the axis origin. Output in the root component; pitch per '
            'turn.'), 3, True
    )
    axis_input = inputs.addSelectionInput('axis', tr('Axis (optional)'),
                                          tr('Select a construction axis, straight edge or sketch line'))
    for selection_filter in ('ConstructionLines', 'LinearEdges', 'SketchLines'):
        axis_input.addSelectionFilter(selection_filter)
    axis_input.setSelectionLimits(0, 1)
    axis_input.isUseCurrentSelections = False
    inputs.addBoolValueInput('reverse_axis', tr('Reverse axis direction'), True, '', False)
    fit_length = inputs.addBoolValueInput('fit_axis_length', tr('Use axis length'), False, '', False)
    fit_length.isEnabled = False
    fit_length.tooltip = tr(
        'Use the total length of a finite line or straight edge once. Sections are scaled '
        'proportionally.')
    units = design.unitsManager.defaultLengthUnits
    inputs.addValueInput('start_angle', tr('Start angle'), 'deg',
                         adsk.core.ValueInput.createByString('0 deg'))
    inputs.addBoolValueInput('right_handed', tr('Right-handed'), True, '', True)
    tangent_joins, live_preview = add_settings_and_info(root_inputs)
    editor = SegmentEditor(inputs, units)
    inputs.addTextBoxCommandInput('section_info', '',
        tr(
            'Diameter and pitch vary linearly along each section. From section 2 onwards, the '
            'start diameter is taken from the previous end.'), 2, True)
    summary = inputs.addTextBoxCommandInput('summary', '', '', 2, True)
    inputs.addTextBoxCommandInput('error', '', '', 2, True)
    preview_status = inputs.addTextBoxCommandInput('preview_status', '', '', 2, True)
    handlers = []
    _sessions.append(handlers)
    graphics = HelixPreview(design)
    _previews.append(graphics)

    def selected_preset_index():
        choice = preset_choice.selectedItem
        if choice is None or not 0 <= choice.index < len(presets):
            raise ValueError(tr('Please select a preset.'))
        return choice.index

    def refresh_user_presets(selected_key=None):
        nonlocal presets, preset_keys
        entries, errors = store.list()
        presets = presets[:builtin_count] + [preset for _, preset in entries]
        preset_keys = [None] * builtin_count + [key for key, _ in entries]
        selected = preset_keys.index(selected_key) if selected_key in preset_keys else 0
        editor.busy = True
        try:
            preset_choice.listItems.clear()
            for index, preset in enumerate(presets):
                mode_label = tr('Surface') if preset.mode == 'surface' else tr('Parametric')
                origin = tr('Custom') if preset_keys[index] else tr('Built-in')
                preset_choice.listItems.add(f'{preset_display_name(preset, builtin=preset_keys[index] is None)} ({mode_label}, {origin})', index == selected)
            preset_load.isEnabled = bool(presets)
            preset_export.isEnabled = bool(presets)
            preset_delete.isEnabled = bool(preset_keys and preset_keys[selected])
        finally:
            editor.busy = False
        return '\n'.join(errors)

    def save_preset():
        if mode.selectedItem.index == 1:
            if any(not field.isValidExpression for field in
                   (surface_pitch, surface_pitch_end, surface_offset, surface_angle)):
                raise ValueError(tr('Please enter valid surface values.'))
            parameters = SurfaceSettings(surface_pitch.value, surface_pitch_end.value,
                surface_offset.value, surface_angle.value, surface_right.value, surface_reverse.value)
            reverse = False
        else:
            parameters = _parameters(inputs, editor)
            reverse = inputs.itemById('reverse_axis').value
        preset = HelixPreset(preset_name.value, parameters, reverse, tangent_joins.value)
        key = store.save(preset)
        errors = refresh_user_presets(key)
        preset_note.text = tr('Saved: {p0}.', p0=preset.name.strip()) + ('\n' + errors if errors else '')

    def import_preset():
        dialog = app.userInterface.createFileDialog()
        dialog.title = tr('Import helix preset')
        dialog.filter = 'HelixPathPilot (*.helixpilot.json);;JSON (*.json)'
        dialog.isMultiSelectEnabled = False
        if dialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        preset = read_preset_file(dialog.filename)
        name, cancelled = app.userInterface.inputBox(
            tr('Name of the imported custom preset:'), CMD_NAME, preset.name)
        if cancelled:
            return
        preset = replace(preset, name=name)
        key = store.save(preset)
        errors = refresh_user_presets(key)
        preset_name.value = preset.name.strip()
        preset_note.text = (tr('Imported: {p0}. Press “Load preset” to apply.', p0=preset.name.strip())
                            + ('\n' + errors if errors else ''))

    def export_preset():
        index = selected_preset_index()
        preset = store.load(preset_keys[index]) if preset_keys[index] else presets[index]
        dialog = app.userInterface.createFileDialog()
        dialog.title = tr('Export preset: {p0}', p0=preset_display_name(preset, builtin=preset_keys[index] is None))
        dialog.filter = 'HelixPathPilot (*.helixpilot.json)'
        dialog.isMultiSelectEnabled = False
        if dialog.showSave() != adsk.core.DialogResults.DialogOK:
            return
        path = export_path(dialog.filename)
        overwrite = path.exists()
        if overwrite and app.userInterface.messageBox(
                tr('Overwrite file?\n{p0}', p0=path), CMD_NAME,
                adsk.core.MessageBoxButtonTypes.YesNoButtonType) != adsk.core.DialogResults.DialogYes:
            return
        path = write_preset_file(path, preset, overwrite=overwrite)
        preset_note.text = tr('Exported: {p0}\n{p1}', p0=preset_display_name(preset, builtin=preset_keys[index] is None), p1=path)

    def delete_preset():
        index = selected_preset_index()
        key = preset_keys[index]
        if key is None:
            raise ValueError(tr('Built-in presets cannot be deleted.'))
        name = presets[index].name
        if app.userInterface.messageBox(tr('Delete custom preset “{p0}”?', p0=name), CMD_NAME,
                adsk.core.MessageBoxButtonTypes.YesNoButtonType) != adsk.core.DialogResults.DialogYes:
            return
        store.delete(key)
        errors = refresh_user_presets()
        preset_note.text = tr('Deleted: {p0}.', p0=name) + ('\n' + errors if errors else '')

    def load_preset():
        index = selected_preset_index()
        preset = store.load(preset_keys[index]) if preset_keys[index] else presets[index]
        graphics.clear()
        editor.busy = True
        try:
            if preset.mode == 'parametric':
                editor.load(preset.parameters)
                inputs.itemById('start_angle').value = preset.parameters.start_angle
                inputs.itemById('right_handed').value = preset.parameters.right_handed
                inputs.itemById('reverse_axis').value = preset.reverse_axis
            else:
                for field, value in (
                    (surface_pitch, preset.parameters.pitch_start),
                    (surface_pitch_end, preset.parameters.pitch_end),
                    (surface_offset, preset.parameters.offset),
                    (surface_angle, preset.parameters.start_angle),
                    (surface_right, preset.parameters.right_handed),
                    (surface_reverse, preset.parameters.reverse)):
                    field.value = value
            tangent_joins.value = preset.tangent_joins
            is_surface = preset.mode == 'surface'
            mode.listItems.item(1 if is_surface else 0).isSelected = True
            parameter_group.isVisible = not is_surface
            surface_group.isVisible = is_surface
            preset_note.text = tr('Loaded: {p0}.', p0=preset_display_name(preset, builtin=preset_keys[index] is None)) + (
                tr(' Please select or check a suitable lateral face.') if is_surface else '')
            preset_name.value = preset_display_name(preset, builtin=preset_keys[index] is None)
            create_tab.activate()
            command.setDialogSize(520, 560)
        finally:
            editor.busy = False

    def surface_parameters():
        for field, label in ((surface_pitch, tr('Start pitch')),
                             (surface_pitch_end, tr('End pitch')),
                             (surface_angle, tr('Start angle')),
                             (surface_offset, tr('Surface offset'))):
            if not field.isValidExpression:
                raise ValueError(tr('{p0}: please enter a valid value with appropriate units.', p0=label))
        return surface_helix(selected_surface_profile(surface_input), surface_pitch.value,
            surface_angle.value, surface_right.value, surface_reverse.value, surface_offset.value,
            pitch_end=surface_pitch_end.value)

    def current_parameters():
        if mode.selectedItem.index == 1:
            return surface_parameters()
        return (_parameters(inputs, editor),
                selected_axis(axis_input, inputs.itemById('reverse_axis').value))

    def current_wire_diameter():
        if not wire_enabled.value:
            return None
        if not wire_diameter.isValidExpression:
            raise ValueError(tr('Please enter a valid wire diameter.'))
        validate_diameter(wire_diameter.value)
        return wire_diameter.value

    def validate(event):
        if editor.busy:
            event.areInputsValid = False
            return
        if mode.selectedItem.index == 1:
            try:
                kind = selected_surface_kind(surface_input)
                profile = selected_surface_profile(surface_input)
                model, _ = surface_parameters()
                current_wire_diameter()
                fmt = lambda value: design.unitsManager.formatValue(value, units)
                surface_status.text = (tr(
                    '{p0}: complete 360° lateral face.\nAxial length: {p1}\nSurface radii: {p2} → '
                    '{p3}\nHelix radii: {p4} → {p5} · Offset: {p6}\nTurns: {p7:.3f}\nHelix radii in '
                    'travel direction; surface radii in surface axis direction.', p0=kind, p1=fmt(profile.length), p2=fmt(profile.radius_start), p3=fmt(profile.radius_end), p4=fmt(model.segments[0].diameter_start / 2), p5=fmt(model.segments[0].diameter_end / 2), p6=fmt(surface_offset.value), p7=sum((t for t, _ in sampling_plan(model)))))
                event.areInputsValid = True
            except ValueError as error:
                surface_status.text = str(error)
                event.areInputsValid = False
            return
        try:
            model = _parameters(inputs, editor)
            current_wire_diameter()
            selected_axis(axis_input, inputs.itemById('reverse_axis').value)
            length = design.unitsManager.formatValue(model.total_length, units)
            turns = sum(t for t, _ in sampling_plan(model))
            summary.text = tr('{p0} section(s) · Total length: {p1} · Turns: {p2:.3f}', p0=len(model.segments), p1=length, p2=turns)
            inputs.itemById('error').text = ''
            event.areInputsValid = True
        except ValueError as error:
            summary.text = ''
            inputs.itemById('error').text = str(error)
            event.areInputsValid = False

    def build_current_sketch():
        model, axis = current_parameters()
        diameter = current_wire_diameter()
        sketch = create_sketch(design, model, axis,
            tangent_joins=tangent_joins.value if mode.selectedItem.index == 0 else False)
        try:
            if mode.selectedItem.index == 1:
                sketch.name = tr('HelixPathPilot – Surface helix')
            if diameter is not None:
                create_wire(design, sketch, diameter)
        except Exception as error:
            cleanup_created([(tr('Helix sketch'), sketch)], error)
            raise
        return sketch

    def preview(event):
        # Graphics are not a final result. Only execute creates the real sketch.
        event.isValidResult = False
        preview_status.text = ''
        if editor.busy or not live_preview.value:
            graphics.clear()
            return
        try:
            model, axis = current_parameters()
            graphics.show(model, axis)
            if tangent_joins.value and mode.selectedItem.index == 0:
                preview_status.text = tr('Path preview; G1 joins are adjusted on creation.')
        except Exception as error:
            graphics.clear()
            status = surface_status if mode.selectedItem.index == 1 else preview_status
            status.text = tr('Preview unavailable: {p0}', p0=error)

    def execute(event):
        try:
            graphics.clear()
            build_current_sketch()
        except Exception as error:
            event.executeFailed = True
            event.executeFailedMessage = str(error)
            futil.handle_error(CMD_NAME)

    def input_changed(event):
        if editor.busy:
            return
        try:
            changed_id = event.input.id
            if changed_id == 'wire_enabled':
                wire_diameter.isVisible = wire_enabled.value
                wire_note.isVisible = wire_enabled.value
                return
            if changed_id == 'remove_section_choice':
                editor.select_remove_target()
                return
            if changed_id == 'remove_section_target':
                return
            if changed_id == 'remove_section':
                changed_id = editor.selected_remove_id()
            if changed_id.startswith('remove_section_'):
                before = len(editor.rows)
                try:
                    editor.changed(changed_id)
                    if len(editor.rows) != before:
                        graphics.clear()
                        if live_preview.value:
                            model, axis = current_parameters()
                            graphics.show(model, axis)
                        # Update the count immediately, independently of Fusion's
                        # scheduling of validateInputs / executePreview.
                        model = _parameters(inputs, editor)
                        length = design.unitsManager.formatValue(model.total_length, units)
                        summary.text = tr('{p0} section(s) · Total length: {p1}', p0=len(model.segments), p1=length)
                        inputs.itemById('error').text = ''
                except Exception as error:
                    inputs.itemById('error').text = str(error)
                    futil.handle_error(tr('Remove section'), show_message_box=True)
                return
            if changed_id == 'preset_choice':
                preset_delete.isEnabled = bool(preset_keys[selected_preset_index()])
                return
            if changed_id in ('preset_load', 'preset_save', 'preset_delete', 'preset_import', 'preset_export'):
                try:
                    {'preset_load': load_preset, 'preset_save': save_preset,
                     'preset_delete': delete_preset, 'preset_import': import_preset,
                     'preset_export': export_preset}[changed_id]()
                except Exception as error:
                    preset_note.text = tr('Preset action failed: {p0}', p0=error)
                return
            affects_preview = (changed_id.startswith(('section_', 'surface_')) or changed_id in
                    ('surface', 'helix_mode', 'live_preview', 'axis', 'reverse_axis', 'start_angle',
                     'right_handed', 'fit_axis_length', 'add_section'))
            if changed_id == 'helix_mode':
                graphics.clear()
                surface_mode = mode.selectedItem.index == 1
                parameter_group.isVisible = not surface_mode
                surface_group.isVisible = surface_mode
                command.setDialogSize(520, 560)
                return
            if changed_id == 'fit_axis_length':
                editor.fit_total_length(selected_axis_length(axis_input))
            else:
                editor.changed(changed_id)
            if changed_id == 'add_section':
                command.setDialogSize(520, 560)
            if changed_id == 'axis':
                try:
                    selected_axis_length(axis_input)
                    fit_length.isEnabled = True
                except ValueError:
                    fit_length.isEnabled = False
            if affects_preview:
                if not live_preview.value:
                    graphics.clear()
                else:
                    # Read after linked diameters / section topology are updated.
                    # Invalid expressions must clear stale graphics even when
                    # Fusion does not subsequently send executePreview.
                    model, axis = current_parameters()
                    graphics.invalidate(model, axis)
        except (ValueError, RuntimeError) as error:
            graphics.clear()
            status = surface_status if mode.selectedItem.index == 1 else inputs.itemById('error')
            status.text = str(error)

    def destroy(event):
        graphics.clear()
        if graphics in _previews:
            _previews.remove(graphics)
        for index, session in enumerate(_sessions):
            if session is handlers:
                _sessions.pop(index)
                break
        handlers.clear()

    futil.add_handler(command.validateInputs, validate, local_handlers=handlers)
    futil.add_handler(command.inputChanged, input_changed, local_handlers=handlers)
    futil.add_handler(command.execute, execute, local_handlers=handlers)
    futil.add_handler(command.executePreview, preview, local_handlers=handlers)
    futil.add_handler(command.destroy, destroy, local_handlers=handlers)
    # Override a previously remembered oversized dialog. Nonzero height enables
    # scrolling instead of growing with the section list; keep resizing possible.
    command.setDialogMinimumSize(380, 300)
    command.setDialogInitialSize(520, 560)
    command.setDialogSize(520, 560)

"""Create a section-based helix around a selected axis."""

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
from .axis_selection import selected_axis, selected_axis_length
from .segment_editor import SegmentEditor
from .dialog_tabs import add_settings_and_info
from .preview_graphics import HelixPreview
from ..createSurfaceHelix.surface_selection import selected_surface_kind, selected_surface_profile
from ..presetManager.catalog import builtin_presets

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
    ui = adsk.core.Application.get().userInterface
    stop()
    panel = _panel(ui)
    if panel is None:
        raise RuntimeError('Das Erstellen-Panel im Volumenkörper-Bereich fehlt.')
    try:
        definition = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, 'Helix mit mehreren Abschnitten, variablem Durchmesser und variabler Steigung erstellen.',
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
        raise ValueError('Bitte einen gültigen Startwinkel eingeben.')
    parameters = editor.read(inputs.itemById('start_angle').value,
                             inputs.itemById('right_handed').value)
    sampling_plan(parameters)
    return parameters


def command_created(args):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        app.userInterface.messageBox('Bitte zuerst ein Design-Dokument öffnen.', CMD_NAME)
        return
    command = args.command
    command.isExecutedWhenPreEmpted = False
    root_inputs = command.commandInputs
    create_tab = root_inputs.addTabCommandInput('create_tab', 'Helix erstellen')
    create_inputs = create_tab.children
    preset_tab = root_inputs.addTabCommandInput('presets_tab', 'Vorlagen')
    preset_group = preset_tab.children.addGroupCommandInput('presets', 'Vorlagen verwalten')
    preset_group.isExpanded = True
    preset_inputs = preset_group.children
    preset_choice = preset_inputs.addDropDownCommandInput(
        'preset_choice', 'Vorlage', adsk.core.DropDownStyles.TextListDropDownStyle)
    presets, preset_errors = builtin_presets()
    store = PresetStore()
    user_entries, user_errors = store.list()
    preset_errors.extend(user_errors)
    preset_keys = [None] * len(presets) + [key for key, _ in user_entries]
    builtin_count = len(presets)
    presets.extend(preset for _, preset in user_entries)
    for index, preset in enumerate(presets):
        label = 'Surface' if preset.mode == 'surface' else 'Parametrisch'
        origin = 'Eigene' if preset_keys[index] else 'Mitgeliefert'
        preset_choice.listItems.add(f'{preset.name} ({label}, {origin})', index == 0)
    preset_load = preset_inputs.addBoolValueInput('preset_load', 'Vorlage laden', False, '', False)
    preset_load.isEnabled = bool(presets)
    preset_name = preset_inputs.addStringValueInput('preset_name', 'Name für eigene Vorlage', '')
    preset_inputs.addBoolValueInput('preset_save', 'Als eigene Vorlage speichern', False, '', False)
    preset_delete = preset_inputs.addBoolValueInput('preset_delete', 'Eigene Vorlage löschen', False, '', False)
    preset_delete.isEnabled = bool(preset_keys and preset_keys[0])
    preset_inputs.addBoolValueInput('preset_import', 'JSON-Vorlage importieren', False, '', False)
    preset_export = preset_inputs.addBoolValueInput('preset_export', 'Ausgewählte Vorlage exportieren', False, '', False)
    preset_export.isEnabled = bool(presets)
    preset_export.tooltip = 'Exportiert die gespeicherte Auswahl, nicht ungespeicherte Änderungen der Helix.'
    preset_note = preset_inputs.addTextBoxCommandInput('preset_note', '',
        'Vorlage auswählen und laden. Aktuelle Parameter werden ersetzt; '
        'Achse und Mantelfläche bleiben separat gewählt.', 3, True)
    if preset_errors or not presets:
        preset_note.text = 'Vorlagen nicht vollständig verfügbar: ' + (
            '\n'.join(preset_errors) if preset_errors else 'Keine Vorlagendateien gefunden.')
    mode = create_inputs.addDropDownCommandInput(
        'helix_mode', 'Modus', adsk.core.DropDownStyles.TextListDropDownStyle)
    mode.listItems.add('Parametrische Helix', True)
    mode.listItems.add('Surface Helix', False)
    wire_enabled = create_inputs.addBoolValueInput('wire_enabled', 'Drahtkörper erstellen', True, '', False)
    wire_diameter = create_inputs.addValueInput('wire_diameter', 'Drahtdurchmesser',
        design.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(0.1))
    wire_diameter.isVisible = False
    wire_note = create_inputs.addTextBoxCommandInput('wire_note', '',
        'Vorschau zeigt den Pfad. Bei OK: Überschneidungsprüfung und Sweep als neuer Körper. '
        'Drahtstärke wird nicht in Vorlagen gespeichert.', 3, True)
    wire_note.isVisible = False
    surface_group = create_inputs.addGroupCommandInput('surface_group', 'Surface Helix')
    surface_group.isExpanded = True
    surface_group.isVisible = False
    surface_inputs = surface_group.children
    surface_inputs.addTextBoxCommandInput('surface_help', '',
        'Zylinder- oder Kegelmantel mit zwei vollständigen Kreisrändern auswählen. '
        'Länge und Radius folgen der Fläche. Die Steigung bezeichnet den axialen '
        'Abstand pro Windung. Ausgabe als angenäherte 3D-Spline.', 3, True)
    surface_input = surface_inputs.addSelectionInput('surface', 'Mantelfläche', 'Mantelfläche auswählen')
    surface_input.addSelectionFilter('Faces')
    surface_input.setSelectionLimits(0, 1)
    surface_input.isUseCurrentSelections = False
    units = design.unitsManager.defaultLengthUnits
    surface_pitch = surface_inputs.addValueInput('surface_pitch', 'Startsteigung', units,
        adsk.core.ValueInput.createByReal(0.5))
    surface_pitch_end = surface_inputs.addValueInput('surface_pitch_end', 'Endsteigung', units,
        adsk.core.ValueInput.createByReal(0.5))
    surface_pitch.tooltip = 'Axiale Steigung am gewählten Startrand; muss positiv sein.'
    surface_pitch_end.tooltip = ('Steigung am Zielrand, linear entlang der axialen Länge. '
        'Gleiche Start- und Endwerte ergeben konstante Steigung. '
        'Beim Randwechsel gelten die Werte weiterhin in Laufrichtung.')
    surface_offset = surface_inputs.addValueInput('surface_offset', 'Surface Offset', units,
        adsk.core.ValueInput.createByReal(0.0))
    surface_offset.tooltip = ('Senkrechter Abstand zur Mantelfläche. Positiv: von der Achse weg; '
        'negativ: zur Achse hin. Beim Kegel verschieben sich auch die Endpunkte axial. '
        'Die Richtung ist unabhängig von Innen- oder Außenfläche.')
    surface_angle = surface_inputs.addValueInput('surface_angle', 'Startwinkel', 'deg',
        adsk.core.ValueInput.createByReal(0.0))
    surface_right = surface_inputs.addBoolValueInput('surface_right', 'Rechtsdrehend', True, '', True)
    surface_reverse = surface_inputs.addBoolValueInput('surface_reverse', 'Am anderen Rand starten', True, '', False)
    surface_status = surface_inputs.addTextBoxCommandInput('surface_status', '', '', 6, True)
    parameter_group = create_inputs.addGroupCommandInput('parameter_group', 'Helix-Parameter')
    parameter_group.isExpanded = True
    inputs = parameter_group.children
    inputs.addTextBoxCommandInput(
        'axis_info', '', 'Ohne Auswahl: globale Z-Achse. Bei Linien beginnt die Helix am '
        'Linienanfang, bei Konstruktionsachsen am Achsursprung. '
        'Ausgabe in der Hauptkomponente; Steigung pro Windung.', 3, True
    )
    axis_input = inputs.addSelectionInput('axis', 'Achse (optional)',
                                          'Konstruktionsachse, gerade Kante oder Skizzenlinie wählen')
    for selection_filter in ('ConstructionLines', 'LinearEdges', 'SketchLines'):
        axis_input.addSelectionFilter(selection_filter)
    axis_input.setSelectionLimits(0, 1)
    axis_input.isUseCurrentSelections = False
    inputs.addBoolValueInput('reverse_axis', 'Achsrichtung umkehren', True, '', False)
    fit_length = inputs.addBoolValueInput('fit_axis_length', 'Achslänge übernehmen', False, '', False)
    fit_length.isEnabled = False
    fit_length.tooltip = 'Gesamtlänge einmalig aus einer endlichen Linie oder geraden Kante übernehmen. Abschnitte werden proportional skaliert.'
    units = design.unitsManager.defaultLengthUnits
    inputs.addValueInput('start_angle', 'Startwinkel', 'deg',
                         adsk.core.ValueInput.createByString('0 deg'))
    inputs.addBoolValueInput('right_handed', 'Rechtsdrehend', True, '', True)
    tangent_joins, live_preview = add_settings_and_info(root_inputs)
    editor = SegmentEditor(inputs, units)
    inputs.addTextBoxCommandInput('section_info', '',
        'Durchmesser und Steigung ändern sich linear entlang der Abschnittslänge. '
        'Ab Abschnitt 2 wird der Startdurchmesser vom vorherigen Ende übernommen.', 2, True)
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
            raise ValueError('Bitte eine Vorlage auswählen.')
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
                mode_label = 'Surface' if preset.mode == 'surface' else 'Parametrisch'
                origin = 'Eigene' if preset_keys[index] else 'Mitgeliefert'
                preset_choice.listItems.add(f'{preset.name} ({mode_label}, {origin})', index == selected)
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
                raise ValueError('Bitte gültige Surface-Werte eingeben.')
            parameters = SurfaceSettings(surface_pitch.value, surface_pitch_end.value,
                surface_offset.value, surface_angle.value, surface_right.value, surface_reverse.value)
            reverse = False
        else:
            parameters = _parameters(inputs, editor)
            reverse = inputs.itemById('reverse_axis').value
        preset = HelixPreset(preset_name.value, parameters, reverse, tangent_joins.value)
        key = store.save(preset)
        errors = refresh_user_presets(key)
        preset_note.text = f'Gespeichert: {preset.name.strip()}.' + ('\n' + errors if errors else '')

    def import_preset():
        dialog = app.userInterface.createFileDialog()
        dialog.title = 'Helix-Vorlage importieren'
        dialog.filter = 'HelixPathPilot (*.helixpilot.json);;JSON (*.json)'
        dialog.isMultiSelectEnabled = False
        if dialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        preset = read_preset_file(dialog.filename)
        name, cancelled = app.userInterface.inputBox(
            'Name der importierten eigenen Vorlage:', CMD_NAME, preset.name)
        if cancelled:
            return
        preset = replace(preset, name=name)
        key = store.save(preset)
        errors = refresh_user_presets(key)
        preset_name.value = preset.name.strip()
        preset_note.text = (f'Importiert: {preset.name.strip()}. Zum Anwenden „Vorlage laden“ drücken.'
                            + ('\n' + errors if errors else ''))

    def export_preset():
        index = selected_preset_index()
        preset = store.load(preset_keys[index]) if preset_keys[index] else presets[index]
        dialog = app.userInterface.createFileDialog()
        dialog.title = f'Vorlage exportieren: {preset.name}'
        dialog.filter = 'HelixPathPilot (*.helixpilot.json)'
        dialog.isMultiSelectEnabled = False
        if dialog.showSave() != adsk.core.DialogResults.DialogOK:
            return
        path = export_path(dialog.filename)
        overwrite = path.exists()
        if overwrite and app.userInterface.messageBox(
                f'Datei überschreiben?\n{path}', CMD_NAME,
                adsk.core.MessageBoxButtonTypes.YesNoButtonType) != adsk.core.DialogResults.DialogYes:
            return
        path = write_preset_file(path, preset, overwrite=overwrite)
        preset_note.text = f'Exportiert: {preset.name}\n{path}'

    def delete_preset():
        index = selected_preset_index()
        key = preset_keys[index]
        if key is None:
            raise ValueError('Mitgelieferte Vorlagen können nicht gelöscht werden.')
        name = presets[index].name
        if app.userInterface.messageBox(f'Eigene Vorlage „{name}“ löschen?', CMD_NAME,
                adsk.core.MessageBoxButtonTypes.YesNoButtonType) != adsk.core.DialogResults.DialogYes:
            return
        store.delete(key)
        errors = refresh_user_presets()
        preset_note.text = f'Gelöscht: {name}.' + ('\n' + errors if errors else '')

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
            preset_note.text = f'Geladen: {preset.name}.' + (
                ' Bitte eine geeignete Mantelfläche auswählen bzw. prüfen.' if is_surface else '')
            preset_name.value = preset.name
            create_tab.activate()
            command.setDialogSize(520, 560)
        finally:
            editor.busy = False

    def surface_parameters():
        if any(not field.isValidExpression for field in
               (surface_pitch, surface_pitch_end, surface_angle, surface_offset)):
            raise ValueError('Bitte gültige Werte für Steigung, Startwinkel und Surface Offset eingeben.')
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
            raise ValueError('Bitte einen gültigen Drahtdurchmesser eingeben.')
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
                surface_status.text = (f'{kind}: vollständiger 360°-Mantel.\n'
                    f'Axiale Länge: {fmt(profile.length)}\n'
                    f'Flächenradien: {fmt(profile.radius_start)} → {fmt(profile.radius_end)}\n'
                    f'Helixradien: {fmt(model.segments[0].diameter_start/2)} → '
                    f'{fmt(model.segments[0].diameter_end/2)} · Offset: {fmt(surface_offset.value)}\n'
                    f'Windungen: {sum(t for t, _ in sampling_plan(model)):.3f}\n'
                    'Helixradien in Laufrichtung; Flächenradien in Flächenachsrichtung.')
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
            summary.text = f'{len(model.segments)} Abschnitt(e) · Gesamtlänge: {length} · Windungen: {turns:.3f}'
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
        if mode.selectedItem.index == 1:
            sketch.name = 'HelixPathPilot – Surface Helix'
        if diameter is not None:
            try:
                create_wire(design, sketch, diameter)
            except Exception:
                sketch.deleteMe()
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
                preview_status.text = 'Pfadvorschau; G1-Übergänge werden beim Erstellen angeglichen.'
        except Exception as error:
            graphics.clear()
            status = surface_status if mode.selectedItem.index == 1 else preview_status
            status.text = f'Vorschau nicht verfügbar: {error}'

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
                        summary.text = f'{len(model.segments)} Abschnitt(e) · Gesamtlänge: {length}'
                        inputs.itemById('error').text = ''
                except Exception as error:
                    inputs.itemById('error').text = str(error)
                    futil.handle_error('Abschnitt entfernen', show_message_box=True)
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
                    preset_note.text = f'Vorlagenaktion fehlgeschlagen: {error}'
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
            inputs.itemById('error').text = str(error)

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

"""Create a section-based helix around a selected axis."""

from pathlib import Path

import adsk.core
import adsk.fusion

from ... import config
from ...core.variable_helix import sampling_plan
from ...lib import fusionAddInUtils as futil
from ...version import APP_NAME, VERSION
from .sketch_builder import create_sketch
from .axis_selection import selected_axis, selected_axis_length
from .segment_editor import SegmentEditor
from .dialog_tabs import add_settings_and_info
from .preview_graphics import HelixPreview
from ..createSurfaceHelix.surface_selection import selected_surface_kind, selected_surface_profile

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
    mode = create_inputs.addDropDownCommandInput(
        'helix_mode', 'Modus', adsk.core.DropDownStyles.TextListDropDownStyle)
    mode.listItems.add('Parametrische Helix', True)
    mode.listItems.add('Surface Helix – Flächenprüfung', False)
    surface_group = create_inputs.addGroupCommandInput('surface_group', 'Surface Helix – Grundlage')
    surface_group.isExpanded = True
    surface_group.isVisible = False
    surface_inputs = surface_group.children
    surface_inputs.addTextBoxCommandInput('surface_help', '',
        'Zylinder- und Kegelmantelflächen mit zwei vollständigen Kreisrändern prüfen. '
        'Hier wird noch keine Helix erzeugt; Ausführen bleibt gesperrt. '
        'Bitte eine einzelne Mantelfläche am Körper auswählen.', 3, True)
    surface_input = surface_inputs.addSelectionInput('surface', 'Mantelfläche', 'Mantelfläche auswählen')
    surface_input.addSelectionFilter('Faces')
    surface_input.setSelectionLimits(0, 1)
    surface_input.isUseCurrentSelections = False
    surface_status = surface_inputs.addTextBoxCommandInput('surface_status', '', '', 5, True)
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

    def validate(event):
        if mode.selectedItem.index == 1:
            try:
                kind = selected_surface_kind(surface_input)
                profile = selected_surface_profile(surface_input)
                fmt = lambda value: design.unitsManager.formatValue(value, units)
                surface_status.text = (f'{kind}: vollständiger 360°-Mantel.\n'
                    f'Axiale Länge: {fmt(profile.length)}\n'
                    f'Startradius: {fmt(profile.radius_start)} · Endradius: {fmt(profile.radius_end)}\n'
                    'Start am ersten Rand in Richtung der Flächenachse. '
                    'Helix-Berechnung und Offset folgen im nächsten Ausbau.')
            except ValueError as error:
                surface_status.text = str(error)
            event.areInputsValid = False
            return
        try:
            model = _parameters(inputs, editor)
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
        if mode.selectedItem.index == 1:
            raise ValueError('Surface Helix bietet derzeit nur die Flächenprüfung; keine Skizzenausgabe.')
        axis = selected_axis(axis_input, inputs.itemById('reverse_axis').value)
        return create_sketch(design, _parameters(inputs, editor), axis,
                             tangent_joins=tangent_joins.value)

    def preview(event):
        # Graphics are not a final result. Only execute creates the real sketch.
        event.isValidResult = False
        preview_status.text = ''
        if editor.busy or not live_preview.value or mode.selectedItem.index == 1:
            graphics.clear()
            return
        try:
            model = _parameters(inputs, editor)
            axis = selected_axis(axis_input, inputs.itemById('reverse_axis').value)
            graphics.show(model, axis)
            if tangent_joins.value:
                preview_status.text = 'Pfadvorschau; G1-Übergänge werden beim Erstellen angeglichen.'
        except Exception as error:
            graphics.clear()
            preview_status.text = f'Vorschau nicht verfügbar: {error}'

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
            if (changed_id.startswith(('section_', 'remove_section_')) or changed_id in
                    ('helix_mode', 'live_preview', 'axis', 'reverse_axis', 'start_angle',
                     'right_handed', 'fit_axis_length', 'add_section')):
                # Also remove stale graphics for invalid expressions, for which
                # Fusion may not send executePreview at all.
                graphics.clear()
            if changed_id == 'helix_mode':
                surface_mode = mode.selectedItem.index == 1
                parameter_group.isVisible = not surface_mode
                surface_group.isVisible = surface_mode
                return
            if changed_id == 'fit_axis_length':
                editor.fit_total_length(selected_axis_length(axis_input))
            else:
                editor.changed(changed_id)
            if changed_id == 'axis':
                try:
                    selected_axis_length(axis_input)
                    fit_length.isEnabled = True
                except ValueError:
                    fit_length.isEnabled = False
        except ValueError as error:
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

"""Create a constant-pitch helix around a selected axis."""

from pathlib import Path

import adsk.core
import adsk.fusion

from ... import config
from ...core.helix_math import HelixParameters
from ...lib import fusionAddInUtils as futil
from ...version import APP_NAME, VERSION
from .sketch_builder import create_sketch
from .axis_selection import selected_axis

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createParametricHelix'
CMD_NAME = f'{APP_NAME} v{VERSION}'
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
LEGACY_PANEL_ID = 'SolidScriptsAddinsPanel'
ICON_FOLDER = str(Path(__file__).resolve().parents[2] / 'resources' / 'icons' / 'helix')
_definition_handlers = []
_sessions = []


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
            CMD_ID, CMD_NAME, 'Helix mit konstantem Durchmesser und konstanter Steigung erstellen.',
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


def _parameters(inputs):
    for name in ('diameter', 'length', 'pitch', 'start_angle'):
        if not inputs.itemById(name).isValidExpression:
            raise ValueError('Bitte gültige Werte mit passenden Einheiten eingeben.')
    parameters = HelixParameters(
        diameter=inputs.itemById('diameter').value,
        length=inputs.itemById('length').value,
        pitch=inputs.itemById('pitch').value,
        start_angle=inputs.itemById('start_angle').value,
        right_handed=inputs.itemById('right_handed').value,
    )
    parameters.segment_count()
    return parameters


def command_created(args):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        app.userInterface.messageBox('Bitte zuerst ein Design-Dokument öffnen.', CMD_NAME)
        return
    command = args.command
    command.isExecutedWhenPreEmpted = False
    inputs = command.commandInputs
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
    units = design.unitsManager.defaultLengthUnits
    for name, label, default in (
        ('diameter', 'Durchmesser', '20 mm'),
        ('length', 'Länge', '50 mm'),
        ('pitch', 'Steigung', '5 mm'),
    ):
        inputs.addValueInput(name, label, units, adsk.core.ValueInput.createByString(default))
    inputs.addValueInput('start_angle', 'Startwinkel', 'deg',
                         adsk.core.ValueInput.createByString('0 deg'))
    inputs.addBoolValueInput('right_handed', 'Rechtsdrehend', True, '', True)
    inputs.addTextBoxCommandInput('error', '', '', 2, True)
    handlers = []
    _sessions.append(handlers)

    def validate(event):
        try:
            _parameters(inputs)
            selected_axis(axis_input, inputs.itemById('reverse_axis').value)
            inputs.itemById('error').text = ''
            event.areInputsValid = True
        except ValueError as error:
            inputs.itemById('error').text = str(error)
            event.areInputsValid = False

    def execute(event):
        try:
            axis = selected_axis(axis_input, inputs.itemById('reverse_axis').value)
            create_sketch(design, _parameters(inputs), axis)
        except Exception as error:
            event.executeFailed = True
            event.executeFailedMessage = str(error)
            futil.handle_error(CMD_NAME)

    def destroy(event):
        for index, session in enumerate(_sessions):
            if session is handlers:
                _sessions.pop(index)
                break
        handlers.clear()

    futil.add_handler(command.validateInputs, validate, local_handlers=handlers)
    futil.add_handler(command.execute, execute, local_handlers=handlers)
    futil.add_handler(command.destroy, destroy, local_handlers=handlers)

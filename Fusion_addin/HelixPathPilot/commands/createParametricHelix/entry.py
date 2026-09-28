"""Create a constant-pitch helix around the global Z axis."""

import adsk.core
import adsk.fusion

from ... import config
from ...core.helix_math import HelixParameters
from ...lib import fusionAddInUtils as futil
from .sketch_builder import create_sketch

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createParametricHelix'
CMD_NAME = 'Helix erstellen'
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
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
        raise RuntimeError('Das Zusatzmodule-Panel im Design-Arbeitsbereich fehlt.')
    try:
        definition = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, 'Helix mit konstantem Durchmesser und konstanter Steigung erstellen.'
        )
        futil.add_handler(definition.commandCreated, command_created,
                          local_handlers=_definition_handlers)
        control = panel.controls.addCommand(definition)
        control.isPromoted = True
    except Exception:
        stop()
        raise


def stop():
    ui = adsk.core.Application.get().userInterface
    panel = _panel(ui)
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
        'axis_info', '', 'Achse: globale Z-Achse. Ausgabe in der Hauptkomponente. '
        'Die Länge wird entlang +Z gemessen; die Steigung gilt pro Windung.', 3, True
    )
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
            inputs.itemById('error').text = ''
            event.areInputsValid = True
        except ValueError as error:
            inputs.itemById('error').text = str(error)
            event.areInputsValid = False

    def execute(event):
        try:
            create_sketch(design, _parameters(inputs))
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

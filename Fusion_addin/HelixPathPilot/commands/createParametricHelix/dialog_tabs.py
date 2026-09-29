"""Settings and project information shared by the helix dialog."""

from pathlib import Path

from ...version import APP_NAME, VERSION

REPOSITORY = 'https://github.com/know-how-schmiede/HelixPathPilot'


def add_settings_and_info(root):
    settings = root.addTabCommandInput('settings_tab', 'Einstellungen').children
    preview = settings.addBoolValueInput('live_preview', 'Live-Vorschau', True, '', True)
    preview.tooltip = ('Schnelle Pfadvorschau ohne Skizzenberechnung. '
                       'G1-Übergänge werden erst beim Erstellen angeglichen.')
    tangent = settings.addBoolValueInput(
        'tangent_joins', 'Tangentiale Übergänge (G1)', True, '', True)
    tangent.tooltip = ('Gleicht die Tangenten benachbarter Splines für einen knickfreien Pfad an. '
                       'Fusion kann die Kurvenform am Übergang anpassen. '
                       'Gleiche Krümmung (G2) wird nicht erzwungen.')
    settings.addTextBoxCommandInput('settings_help', '',
        'G1 gleicht die Richtung an Abschnittsgrenzen an und erleichtert anschließende Sweeps. '
        'Ohne diese Option bleiben die berechneten Abschnittsübergänge unverändert.<br><br>'
        'Die Einstellungen gelten für den aktuellen Dialogaufruf.', 5, True)

    info = root.addTabCommandInput('info_tab', 'Info').children
    info.addTextBoxCommandInput('info_title', '', f'{APP_NAME} {VERSION}', 1, True)
    logo = info.addImageCommandInput('info_logo', '', str(
        Path(__file__).resolve().parents[2] / 'resources' / 'logo.png'))
    logo.isFullWidth = True
    paragraphs = [
        ('description', 'HelixPathPilot von Know-How-Schmiede erstellt Helix-Pfade in Autodesk Fusion. '
         'Mehrere Abschnitte mit variablem Durchmesser und variabler Steigung werden als 3D-Skizze ausgegeben.', 3),
        ('website', 'Tutorials zu Fusion und weitere Plugins finden Sie auf der '
         '<a href="https://www.know-how-schmiede.de">Homepage der Know-How-Schmiede</a>.', 3),
        ('source', f'Der Quellcode kann im <a href="{REPOSITORY}">GitHub-Repository</a> eingesehen werden.', 2),
        ('releases', f'Updates finden Sie unter <a href="{REPOSITORY}/releases">Releases im GitHub-Repository</a>.', 2),
        ('issues', f'Fehler gefunden? Bitte unter <a href="{REPOSITORY}/issues">Issues im Repository</a> melden '
         '– mit Add-in-Version und Schritten zum Nachstellen.', 3),
        ('youtube', 'Gefällt Ihnen das Plugin? Dann lassen Sie gerne ein kostenloses YouTube-Abo bei '
         '<a href="https://www.youtube.com/@knowhowschmiede">@knowhowschmiede</a> da!', 3),
        ('license', 'Rene Triebenstein · MIT-Lizenz', 1),
    ]
    for key, text, rows in paragraphs:
        info.addTextBoxCommandInput(f'info_{key}', '', text, rows, True).isFullWidth = True
    return tangent, preview

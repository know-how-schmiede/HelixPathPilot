"""Settings and project information shared by the helix dialog."""

from ...i18n import tr

from pathlib import Path

from ...version import APP_NAME, VERSION

REPOSITORY = 'https://github.com/know-how-schmiede/HelixPathPilot'


def add_settings_and_info(root):
    settings = root.addTabCommandInput('settings_tab', tr('Settings')).children
    preview = settings.addBoolValueInput('live_preview', tr('Live preview'), True, '', True)
    preview.tooltip = (tr('Fast path preview without sketch calculation. G1 joins are adjusted only on creation.'))
    tangent = settings.addBoolValueInput(
        'tangent_joins', tr('Tangent joins (G1)'), True, '', True)
    tangent.tooltip = (tr(
        'Aligns tangents of adjacent splines for a path without kinks. Fusion may adjust the '
        'curve shape at the join. Equal curvature (G2) is not enforced.'))
    settings.addTextBoxCommandInput('settings_help', '',
        tr(
            'G1 aligns direction at section boundaries and simplifies subsequent sweeps. Without '
            'this option, calculated section joins remain unchanged.<br><br>Settings apply to the'
            ' current dialog session.'), 5, True)

    info = root.addTabCommandInput('info_tab', tr('About')).children
    info.addTextBoxCommandInput('info_title', '', f'{APP_NAME} {VERSION}', 1, True)
    logo = info.addImageCommandInput('info_logo', '', str(
        Path(__file__).resolve().parents[2] / 'resources' / 'logo.png'))
    logo.isFullWidth = True
    paragraphs = [
        ('description', tr(
            'HelixPathPilot by Know-How-Schmiede creates helix paths in Autodesk Fusion. Multiple'
            ' sections with variable diameter and pitch are output as a 3D sketch.'), 3),
        ('website', tr(
            'Find Fusion tutorials and more add-ins on the <a '
            'href="https://www.know-how-schmiede.de">Know-How-Schmiede website</a>.'), 3),
        ('source', tr('View the source code in the <a href="{p0}">GitHub repository</a>.', p0=REPOSITORY), 2),
        ('releases', tr('Find updates under <a href="{p0}/releases">releases in the GitHub repository</a>.', p0=REPOSITORY), 2),
        ('issues', tr(
            'Found a bug? Please report it under <a href="{p0}/issues">repository issues</a> with'
            ' the add-in version and steps to reproduce.', p0=REPOSITORY), 3),
        ('youtube', tr(
            'Enjoying the add-in? Consider a free YouTube subscription to <a '
            'href="https://www.youtube.com/@knowhowschmiede">@knowhowschmiede</a>!'), 3),
        ('license', tr('Rene Triebenstein · MIT License'), 1),
    ]
    for key, text, rows in paragraphs:
        info.addTextBoxCommandInput(f'info_{key}', '', text, rows, True).isFullWidth = True
    return tangent, preview

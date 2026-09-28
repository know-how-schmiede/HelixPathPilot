"""Per-dialog section inputs; Fusion input objects are owned by this editor."""

import adsk.core

from ...core.helix_segments import HelixSegment, SegmentedHelix
from ...core.variable_helix import MAX_SEGMENTS

FIELDS = (
    ('length', 'Abschnittslänge'),
    ('diameter_start', 'Startdurchmesser'),
    ('diameter_end', 'Enddurchmesser'),
    ('pitch_start', 'Startsteigung'),
    ('pitch_end', 'Endsteigung'),
)


class SegmentEditor:
    def __init__(self, inputs, units):
        self.units = units
        self.rows = []
        self.next_id = 0
        self.busy = False
        self.container = inputs.addGroupCommandInput('sections', 'Abschnitte')
        self.container.isExpanded = True
        self.add_button = inputs.addBoolValueInput('add_section', 'Abschnitt hinzufügen', False, '', False)
        self.add(HelixSegment.constant(5, 2, 0.5))

    def add(self, segment):
        if len(self.rows) >= MAX_SEGMENTS:
            raise ValueError(f'Maximal {MAX_SEGMENTS} Abschnitte sind möglich.')
        row_id = self.next_id
        self.next_id += 1
        group = self.container.children.addGroupCommandInput(f'section_{row_id}', '')
        group.isExpanded = True
        fields = {}
        for name, label in FIELDS:
            fields[name] = group.children.addValueInput(
                f'section_{row_id}_{name}', label, self.units,
                adsk.core.ValueInput.createByReal(getattr(segment, name)))
        remove = group.children.addBoolValueInput(f'remove_section_{row_id}', 'Abschnitt entfernen', False, '', False)
        self.rows.append((group, fields, remove))
        self.refresh()

    def refresh(self):
        for index, (group, fields, remove) in enumerate(self.rows):
            group.name = f'Abschnitt {index + 1}'
            remove.isEnabled = len(self.rows) > 1
            fields['diameter_start'].isEnabled = index == 0
            if index:
                previous = self.rows[index - 1][1]['diameter_end']
                if previous.isValidExpression and fields['diameter_start'].value != previous.value:
                    fields['diameter_start'].value = previous.value
        self.add_button.isEnabled = len(self.rows) < MAX_SEGMENTS

    def read(self, start_angle=0, right_handed=True):
        segments = []
        for index, (_, fields, _) in enumerate(self.rows):
            if any(not value.isValidExpression for value in fields.values()):
                raise ValueError(f'Abschnitt {index + 1}: Bitte gültige Werte mit passenden Einheiten eingeben.')
            values = {name: value.value for name, value in fields.items()}
            if segments:
                values['diameter_start'] = segments[-1].diameter_end
            try:
                segments.append(HelixSegment(**values))
            except ValueError as error:
                raise ValueError(f'Abschnitt {index + 1}: {error}') from error
        return SegmentedHelix(segments, start_angle, right_handed)

    def changed(self, changed_id):
        if self.busy:
            return
        if (changed_id != 'add_section' and not changed_id.startswith('remove_section_')
                and not any(changed_id == value.id for _, fields, _ in self.rows for value in fields.values())):
            return
        self.busy = True
        try:
            if changed_id == 'add_section':
                last = self.read().segments[-1]
                self.add(HelixSegment.constant(last.length, last.diameter_end, last.pitch_end))
            elif changed_id.startswith('remove_section_') and len(self.rows) > 1:
                for index, (group, _, remove) in enumerate(self.rows):
                    if remove.id == changed_id:
                        group.deleteMe()
                        self.rows.pop(index)
                        break
            self.refresh()
        finally:
            self.busy = False

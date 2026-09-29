"""Per-dialog section inputs; Fusion input objects are owned by this editor."""

import adsk.core
from dataclasses import replace
from types import SimpleNamespace

from ...core.helix_segments import HelixSegment, SegmentedHelix
from ...core.variable_helix import MAX_SEGMENTS, sampling_plan

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
        self.retired_rows = []
        self.remove_ids = {}
        self.next_id = 0
        self.busy = False
        self.container = inputs.addGroupCommandInput('sections', 'Abschnitte')
        self.container.isExpanded = True
        self.remove_choice = inputs.addDropDownCommandInput(
            'remove_section_choice', 'Abschnitt entfernen', adsk.core.DropDownStyles.TextListDropDownStyle)
        self.remove_button = inputs.addBoolValueInput('remove_section', 'Ausgewählten Abschnitt entfernen',
                                                     False, '', False)
        self.remove_target = inputs.addTextBoxCommandInput('remove_section_target', '', '', 1, True)
        self.remove_signature = ()
        self.remove_target_id = None
        self.remove_labels = {}
        self.add_button = inputs.addBoolValueInput('add_section', 'Abschnitt hinzufügen', False, '', False)
        self.add(HelixSegment.constant(5, 2, 0.5))

    def add(self, segment):
        if len(self.rows) >= MAX_SEGMENTS:
            raise ValueError(f'Maximal {MAX_SEGMENTS} Abschnitte sind möglich.')
        row_id = self.next_id
        self.next_id += 1
        group = self.container.children.addGroupCommandInput(f'section_{row_id}', f'Abschnitt {row_id + 1}')
        group.isExpanded = True
        fields = {}
        try:
            for name, label in FIELDS:
                fields[name] = group.children.addValueInput(
                    f'section_{row_id}_{name}', label, self.units,
                    adsk.core.ValueInput.createByReal(getattr(segment, name)))
            # Stable Python identity; no dynamically-created per-row action button.
            remove = SimpleNamespace(id=f'remove_section_{row_id}', isEnabled=True)
        except Exception:
            group.deleteMe()
            raise
        self.rows.append((group, fields, remove))
        self.remove_ids[f'remove_section_{row_id}'] = self.rows[-1]
        self.refresh()

    def load(self, model):
        """Build replacement rows first so failed input creation preserves old rows."""
        sampling_plan(model)
        old_rows = self.rows
        was_busy = self.busy
        self.busy = True
        self.rows = []
        try:
            for segment in model.segments:
                self.add(segment)
        except Exception:
            for group, _, _ in self.rows:
                group.deleteMe()
            self.rows = old_rows
            self.refresh()
            raise
        else:
            for group, _, _ in old_rows:
                group.deleteMe()
        finally:
            self.remove_ids = {row[2].id: row for row in self.rows}
            self.busy = was_busy

    def refresh(self):
        for index, (group, fields, remove) in enumerate(self.rows):
            remove.isEnabled = len(self.rows) > 1
            fields['diameter_start'].isEnabled = index == 0
            fields['diameter_start'].tooltip = (
                f"Wird automatisch vom Enddurchmesser von {self.rows[index - 1][0].name} übernommen."
                if index else 'Frei wählbarer Startdurchmesser des ersten Abschnitts.')
            if index:
                previous = self.rows[index - 1][1]['diameter_end']
                if previous.isValidExpression and fields['diameter_start'].value != previous.value:
                    fields['diameter_start'].value = previous.value
        self.add_button.isEnabled = len(self.rows) < MAX_SEGMENTS
        signature = tuple(remove.id for _, _, remove in self.rows)
        if signature != self.remove_signature:
            if self.remove_target_id not in signature:
                self.remove_target_id = signature[0] if signature else None
            self.remove_labels = {group.name: remove.id for group, _, remove in self.rows}
            self.remove_choice.listItems.clear()
            selected_item = None
            for index, (group, _, _) in enumerate(self.rows):
                item = self.remove_choice.listItems.add(group.name, False)
                if signature[index] == self.remove_target_id:
                    selected_item = item
            # Set selection only after all items exist; do not depend on the
            # native list's automatic selection while it is being populated.
            if selected_item is not None:
                selected_item.isSelected = True
            self.remove_signature = signature
        self.remove_choice.isEnabled = len(self.rows) > 1
        self.remove_button.isEnabled = len(self.rows) > 1
        self.update_remove_caption()

    def update_remove_caption(self):
        label = next((name for name, key in self.remove_labels.items()
                      if key == self.remove_target_id), 'Kein Abschnitt')
        self.remove_target.text = f'Zum Entfernen ausgewählt: {label}'

    def select_remove_target(self):
        selected = self.remove_choice.selectedItem
        target = self.remove_labels.get(selected.name) if selected is not None else None
        if target is None:
            raise ValueError('Bitte den zu entfernenden Abschnitt erneut auswählen.')
        self.remove_target_id = target
        self.update_remove_caption()

    def selected_remove_id(self):
        if self.remove_target_id not in self.remove_signature:
            raise ValueError('Bitte den zu entfernenden Abschnitt auswählen.')
        return self.remove_target_id

    def read(self, start_angle=0, right_handed=True):
        # Also synchronize before validation/preview: programmatic input updates
        # do not always cause another inputChanged event in Fusion.
        was_busy = self.busy
        self.busy = True
        try:
            self.refresh()
        finally:
            self.busy = was_busy
        segments = []
        for index, (group, fields, _) in enumerate(self.rows):
            for name, label in FIELDS:
                if not fields[name].isValidExpression:
                    raise ValueError(f'{group.name} – {label}: Bitte einen gültigen '
                                     'Wert mit passenden Einheiten eingeben.')
            values = {name: value.value for name, value in fields.items()}
            if segments:
                values['diameter_start'] = segments[-1].diameter_end
            try:
                segments.append(HelixSegment(**values))
            except ValueError as error:
                raise ValueError(f'{group.name}: {error}') from error
        return SegmentedHelix(segments, start_angle, right_handed)

    def fit_total_length(self, length):
        """One-shot proportional resize; validate everything before changing inputs."""
        model = self.read()
        resized = SegmentedHelix(tuple(
            replace(segment, length=length * (segment.length / model.total_length))
            for segment in model.segments))
        sampling_plan(resized)
        self.busy = True
        try:
            for (_, fields, _), segment in zip(self.rows, resized.segments):
                fields['length'].value = segment.length
        finally:
            self.busy = False

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
                row = self.remove_ids.get(changed_id)
                index = next((i for i, active in enumerate(self.rows) if active is row), None)
                if index is not None:
                    # Commit the model change before touching native UI/graphics.
                    # Never read properties of the button dispatching this event.
                    self.retired_rows.append(self.rows.pop(index))
                    self.remove_ids.pop(changed_id, None)
                    group, fields, remove = row
                    for field in fields.values():
                        field.isVisible = False
                    remove.isVisible = False
                    group.isVisible = False
            self.refresh()
        finally:
            self.busy = False

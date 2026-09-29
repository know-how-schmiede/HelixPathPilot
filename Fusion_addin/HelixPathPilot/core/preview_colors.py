"""Shared preview colors by section order, independent of Fusion and row IDs."""

import colorsys

# High contrast starting colors; additional sections get distinct hues.
_BASE = ((0, 114, 178), (213, 94, 0), (0, 158, 115), (170, 68, 153),
         (180, 140, 0), (0, 150, 180), (205, 70, 95), (105, 100, 195))
SECTION_COLORS = _BASE + tuple(
    tuple(round(channel * 255) for channel in colorsys.hsv_to_rgb(
        (0.13 + index * 0.61803398875) % 1, 0.72, 0.72))
    for index in range(24))


def section_color(index):
    return SECTION_COLORS[index % len(SECTION_COLORS)]


def section_color_hex(index):
    return '#{:02X}{:02X}{:02X}'.format(*section_color(index))

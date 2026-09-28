"""Build small geometric SVG/PNG helix icons using only the standard library."""

import math
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1] / 'Fusion_addin' / 'HelixPathPilot'
ICONS = ROOT / 'resources' / 'icons' / 'helix'


def chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))


def build(size):
    turns = 2 if size == 16 else 3
    width = 3.2 if size == 16 else 2.8
    points = []
    for index in range(241):
        f = index / 240
        angle = -math.pi / 2 + turns * math.tau * f
        points.append((16 + 9 * math.cos(angle), 5 + 22 * f + 2 * math.sin(angle)))
    coordinates = ' '.join(f'{x:.3f},{y:.3f}' for x, y in points)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 32 32">
  <title>HelixPathPilot</title>
  <path d="M16 2 V30" fill="none" stroke="#8295a5" stroke-width="1.3" stroke-dasharray="2 2"/>
  <polyline points="{coordinates}" fill="none" stroke="#149eae" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="16" cy="3" r="2" fill="#e89b30"/>
</svg>
'''
    (ICONS / f'{size}x{size}.svg').write_text(svg, encoding='utf-8')
    # Raster fallback from the same vector geometry, using 4x supersampling.
    samples = 4
    side = size * samples
    scale = side / 32
    pixels = bytearray(side * side * 4)

    def disc(x, y, radius, color):
        x, y, radius = x * scale, y * scale, radius * scale
        for row in range(max(0, int(y - radius)), min(side, math.ceil(y + radius))):
            for col in range(max(0, int(x - radius)), min(side, math.ceil(x + radius))):
                if (col + 0.5 - x) ** 2 + (row + 0.5 - y) ** 2 <= radius ** 2:
                    offset = (row * side + col) * 4
                    pixels[offset:offset + 4] = bytes((*color, 255))

    for index in range(281):
        y = 2 + index / 10
        if (y - 2) % 4 < 2:
            disc(16, y, 0.65, (130, 149, 165))
    for a, b in zip(points, points[1:]):
        for step in range(5):
            t = step / 4
            disc(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), width / 2, (20, 158, 174))
    disc(16, 3, 2, (232, 155, 48))
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            offsets = [((y * samples + j) * side + x * samples + i) * 4
                       for j in range(samples) for i in range(samples)]
            alpha = sum(pixels[o + 3] for o in offsets)
            for channel in range(3):
                rows.append(round(sum(pixels[o + channel] * pixels[o + 3] for o in offsets) / alpha) if alpha else 0)
            rows.append(round(alpha / samples ** 2))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')
    (ICONS / f'{size}x{size}.png').write_bytes(png)


if __name__ == '__main__':
    ICONS.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 64):
        build(size)
    (ROOT / 'AddInIcon.svg').write_bytes((ICONS / '32x32.svg').read_bytes())
    print('Built SVG and PNG icons at 16, 32 and 64 pixels.')

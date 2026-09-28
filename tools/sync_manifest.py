"""Synchronize Fusion's static manifest with the active version.py."""

import json
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1] / 'Fusion_addin' / 'HelixPathPilot'
version = runpy.run_path(str(root / 'version.py'))['VERSION']
path = root / 'HelixPathPilot.manifest'
manifest = json.loads(path.read_text(encoding='utf-8'))
manifest['version'] = version
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=4) + '\n', encoding='utf-8')
print(f'Manifest version: {version}')

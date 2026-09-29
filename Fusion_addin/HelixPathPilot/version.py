"""
Central version information for HelixPathPilot.

This file is the single source of truth for the current project version.
Keep this file in sync with:
- docs/timeline.md
- docs/ablaufplan.md
- installer metadata (later, e.g. Inno Setup)
"""

APP_NAME = "HelixPathPilot"
APP_TITLE = "HelixPathPilot"
APP_AUTHOR = "Know-How-Schmiede"

VERSION_MAJOR = 0
VERSION_MINOR = 4
VERSION_PATCH = 0

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
__version__ = VERSION

RELEASE_STAGE = "development"
RELEASE_DATE = "2026-09-29"

PROJECT_STATUS = "preset data model and built-in examples / development"


def get_version():
    return VERSION


def get_version_tuple():
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)


def get_full_version_label():
    return f"{APP_NAME} v{VERSION} ({RELEASE_STAGE})"

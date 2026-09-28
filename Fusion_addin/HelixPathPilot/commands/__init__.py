"""Registry of implemented Fusion commands."""

# Each entry module provides start() and stop(), as in the supplied template.
from .createParametricHelix import entry as create_parametric_helix

commands = (create_parametric_helix,)


def start():
    for command in commands:
        command.start()


def stop():
    for command in reversed(commands):
        command.stop()

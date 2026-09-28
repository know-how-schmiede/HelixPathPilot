"""Fusion command registry. Register implemented entry modules here."""

# Each entry module provides start() and stop(), as in the supplied template.
commands = ()


def start():
    for command in commands:
        command.start()


def stop():
    for command in reversed(commands):
        command.stop()

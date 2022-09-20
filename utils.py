from pathlib import Path
import sys
import tty
import termios
from subprocess import run


def edit(file: Path, line: int, col: int):
    cmd = ["nvim", f"+call cursor({line}, {col})", file.absolute()]
    run(cmd)


def get_char() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

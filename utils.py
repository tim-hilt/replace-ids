from pathlib import Path
from subprocess import getoutput
import sys
import tty
import termios
import re


def get_char() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def findall(p, s):
    return [m.start() for m in re.finditer(p, s)]

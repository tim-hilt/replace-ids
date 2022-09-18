import argparse
import os
from pathlib import Path
import logging


def validate_args(args):
    path = args.path
    if not os.path.exists(path) or not os.path.isdir(path):
        logging.error(f"path invalid: {path}")
        exit(1)


def parse_args() -> Path:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to where ids should be replaced")
    args = parser.parse_args()
    validate_args(args)
    path = args.path
    return Path(path)

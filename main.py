#!/usr/bin/env python

import os

from args import parse_args
from replaceIds import get_matches, process_file


def main():
    path = parse_args()
    os.chdir(path)
    files = get_matches()
    for file, matches in files.items():
        process_file(file, matches)


if __name__ == "__main__":
    main()

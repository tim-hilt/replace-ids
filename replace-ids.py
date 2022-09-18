#!/usr/bin/env python

import os
import re
from subprocess import getoutput
from pathlib import Path
import logging
from typing import Final

from args import parse_args
from choice import get_selection
from utils import findall

SEARCH_STRING: Final = "'\\bid='"


def process_output(output: list([str])):
    matches = {}
    for match in output:
        file_with_pos, code = match.split(" ", 1)
        file, line, col, *_ = file_with_pos.split(":")
        if not file in matches:
            matches[file] = []
        matches[file].append({"match": code, "line": line, "col": col})
    return matches


def process_file(file: Path, matches):
    logging.info(f"Processing file {file}")
    for match in matches:
        print(match["match"])
        formatted_match = format_match(match["match"])
        suggestion = get_suggestion(formatted_match)
        print(f"Suggestion: {formatted_match} -> {suggestion}")
        # sel = get_selection()


def format_match(match: str) -> str:
    id_substr = match[match.find("id="):]
    after_id = id_substr[3:]
    # TODO: If variable detected, then jump directly to the source
    opening_delimiters = ["\"", "{\"", "{"]
    closing_delimiters = ["\"", "\"}", "}"]
    for opening_delimiter, closing_delimiter in zip(opening_delimiters, closing_delimiters):
        if after_id.startswith(opening_delimiter):
            start = len(opening_delimiter)
            op = findall(opening_delimiter, after_id)
            cl = findall(closing_delimiter, after_id)
            if len(op) > 1 and opening_delimiter != "\"":
                i = 0
                while True:
                    if len(op) > i + 2 and op[i + 1] < cl[i]:
                        i += 1
                        continue
                    end = cl[i]
                    break
            else:
                end = after_id.find(closing_delimiter, start + 1)
            return after_id[start:end]
    return match


def get_suggestion(match: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '-', match).lower().replace("_", "-")


def main():
    path = parse_args()
    os.chdir(path)
    cmd = f"rg --vimgrep {SEARCH_STRING}"
    out = getoutput(cmd).split("\n")
    files = process_output(out)
    for file, matches in files.items():
        process_file(file, matches)


if __name__ == "__main__":
    main()

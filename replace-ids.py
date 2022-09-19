#!/usr/bin/env python

import fileinput
import os
import re
from subprocess import getoutput
from pathlib import Path
import logging
from enum import Enum
from typing import Final, TypedDict

from args import parse_args
from choice import Choice, get_selection
from utils import edit


class DelimiterDefinition(TypedDict):
    opening: str
    closing: str


class Delimiters(TypedDict):
    string: DelimiterDefinition
    curly_string: DelimiterDefinition


SEARCH_STRING: Final = "'\\bid='"
DELIMITERS: Final[Delimiters] = {"string": {"opening": "\"", "closing": "\""},
                                 "curly_string": {"opening": "{\"", "closing": "\"}"}}


class Match(TypedDict):
    match: str
    line: int
    col: int


def process_output(output: list([str])):
    matches = {}
    for match in output.split("\n"):
        file_with_pos, code = match.split(" ", 1)
        file, line, col, *_ = file_with_pos.split(":")
        if file not in matches:
            matches[file]: list([Match]) = []
        matches[file].append(
            {"match": code, "line": int(line), "col": int(col)})
    return matches


def get_search_result():
    cmd = f"rg --vimgrep {SEARCH_STRING}"
    out = getoutput(cmd)
    return process_output(out)


class MatchType(Enum):
    CURLY_STRING = 1
    STRING = 2
    VARIABLE = 3


def get_match_type(match: str) -> MatchType:
    id_substr = match[match.find("id="):]
    after_id = id_substr[3:]
    if after_id.startswith(DELIMITERS["string"]["opening"]):
        return MatchType.STRING
    elif after_id.startswith(DELIMITERS["curly_string"]["opening"]):
        return MatchType.CURLY_STRING
    return MatchType.VARIABLE


def find_id(line: str, match_type: MatchType) -> tuple[int, int]:
    match match_type:
        case MatchType.CURLY_STRING:
            p = re.compile('id={"([^"]+)')
        case MatchType.STRING:
            p = re.compile('id="([^"]+)')
    m = p.search(line)
    return m.span(1)


def process_file(file: Path, matches: list([Match])):
    logging.info(f"Processing file {file}")
    for match in matches:
        code = match["match"]
        print(code)
        match_type = get_match_type(code)
        match match_type:
            case MatchType.VARIABLE:
                col_offset = 4
                edit(file, match["line"], match["col"] + col_offset)
                continue
            case MatchType.STRING:
                start, end = find_id(code, MatchType.STRING)
            case MatchType.CURLY_STRING:
                start, end = find_id(code, MatchType.CURLY_STRING)
        curr_id = code[start:end]
        suggested_id = get_suggestion(curr_id)
        print(f"Suggestion: {curr_id} -> {suggested_id}")
        sel = get_selection()

        match sel:
            case Choice.SKIP:
                continue
            case Choice.EDIT:
                edit(file, match["line"], match["col"])
            case Choice.YES:
                accept_suggestion(
                    file, match["line"], start, end, suggested_id)


def accept_suggestion(file: Path, line_num: int, start: int, end: int, suggestion: str):
    for num, line in enumerate(fileinput.input(file, inplace=True)):
        if num == line_num:
            print(f"{line[:start]}{suggestion}{line[end + 1:]}")


def get_suggestion(match: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '-', match).lower().replace("_", "-")


def main():
    path = parse_args()
    os.chdir(path)
    files = get_search_result()
    for file, matches in files.items():
        process_file(file, matches)


if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
import re
from subprocess import getoutput
from pathlib import Path
import logging
from enum import Enum
from typing import Final, TypedDict

from args import parse_args
from choice import get_selection
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
    line: str
    col: str


def process_output(output: list([str])):
    matches = {}
    for match in output.split("\n"):
        file_with_pos, code = match.split(" ", 1)
        file, line, col, *_ = file_with_pos.split(":")
        if file not in matches:
            matches[file]: list([Match]) = []
        matches[file].append({"match": code, "line": line, "col": col})
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


def format_string_match(match: str) -> str:
    after_id = match[match.find("id=") + 4:]
    delim = DELIMITERS["string"]["opening"]
    start = len(delim)
    end = after_id.find(delim, start + 1)
    return after_id[start:end]


def format_curly_string_match(match: str) -> str:
    id_substr = match[match.find("id="):]
    after_id = id_substr[3:]
    opening_delim = DELIMITERS["curly_string"]["opening"]
    start = len(opening_delim)
    closing_delim = DELIMITERS["curly_string"]["closing"]
    end = after_id.find(closing_delim, start + 1)
    return after_id[start:end]


def process_file(file: Path, matches: list([Match])):
    logging.info(f"Processing file {file}")
    for match in matches:
        code = match["match"]
        print(code)
        match_type = get_match_type(code)
        match match_type:
            case MatchType.VARIABLE:
                edit(file, match["line"], match["col"])
                continue
            case MatchType.STRING:
                formatted_match = format_string_match(code)
            case MatchType.CURLY_STRING:
                formatted_match = format_curly_string_match(code)
        suggestion = get_suggestion(formatted_match)
        print(f"Suggestion: {formatted_match} -> {suggestion}")
        sel = get_selection()


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

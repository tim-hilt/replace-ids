#!/usr/bin/env python

import os
import re
from subprocess import run, getoutput
from pathlib import Path
import logging
from enum import Enum
from typing import Final, TypedDict

from args import parse_args
from choice import get_selection
from utils import findall


class DelimiterDefinition(TypedDict):
    opening: str
    closing: str


class Delimiters(TypedDict):
    string: DelimiterDefinition
    curly_string: DelimiterDefinition


SEARCH_STRING: Final = "'\\bid='"
DELIMITERS: Final(Delimiters) = {"string": {"opening": "\"", "closing": "\""},
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
        if not file in matches:
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
    if after_id.startswith(DELIMITERS["string"]["opening_delimiter"]):
        return MatchType.STRING
    elif after_id.startswith(DELIMITERS["curly_string"]["opening_delimiter"]):
        return MatchType.CURLY_STRING
    return MatchType.VARIABLE


def edit_src(file: str, line: str, col: str):
    cmd = f"nvim {file}:{line}:{col}"
    run(cmd)


def process_file(file: Path, matches: list([Match])):
    logging.info(f"Processing file {file}")
    for match in matches:
        # TODO: DRY! match["match"]
        print(match["match"])
        match_type = get_match_type(match["match"])
        match match_type:
            case MatchType.VARIABLE:
                edit_src(file, match["line"], match["col"])
                continue
            case MatchType.STRING:
                formatted_match = format_string_match(match["match"])
            case MatchType.CURLY_STRING:
                formatted_match = format_curly_string_match(match["match"])
        suggestion = get_suggestion(formatted_match)
        print(f"Suggestion: {formatted_match} -> {suggestion}")
        # sel = get_selection()


def format_string_match(match: str) -> str:
    id_substr = match[match.find("id="):]
    after_id = id_substr[3:]
    delim = DELIMITERS["string"]["opening_delimiter"]
    start = len(delim)
    end = after_id.find(delim, start + 1)
    return after_id[start:end]


def format_curly_string_match(match: str) -> str:
    id_substr = match[match.find("id="):]
    after_id = id_substr[3:]
    opening_delim = DELIMITERS["curly_string"]["opening_delimiter"]
    start = len(opening_delim)
    closing_delim = DELIMITERS["curly_string"]["closing_delimiter"]
    end = after_id.find(closing_delim, start + 1)
    return after_id[start:end]


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

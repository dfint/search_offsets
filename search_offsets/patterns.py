from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from more_itertools import chunked


class Pattern(NamedTuple):
    """
    A named tuple to contain information about a pattern: it's name and the pattern in bytes.
    """

    name: str
    pattern: bytes

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, pattern={self.pattern!r})"


def hex_to_bytes(s: str) -> bytes:
    """
    Convert hexadecimal string to bytes.
    """
    return int(s, 16).to_bytes(1, "little")


def convert_to_pattern(s: list[str]) -> list[int | None]:
    """
    Convert list of the pattern tokens to a list of byte values or None if the token is "??".
    """
    return [None if item == "??" else int(item, 16) for item in s]


def load_patterns(filename: str = "fn_byte_patterns.ffsess") -> list[Pattern]:
    """
    Load patterns to a list from ffsess file.
    """
    patterns = []

    with Path(filename).open() as patterns_file:
        for tab_line, pattern_line in chunked(patterns_file, 2):
            command, _, tab_name = tab_line.rstrip().partition(" ")
            assert command == "Tab", command
            rule_name, _, _, *pattern = pattern_line.rstrip().split(" ")
            assert rule_name == "RuleBytePattern"
            pattern = convert_to_pattern(pattern)
            pattern_object = Pattern(tab_name, pattern)

            patterns.append(pattern_object)

    return patterns


def group_patterns(patterns: list[Pattern]) -> Mapping[int, list[Pattern]]:
    """
    Group patterns by their first byte.
    """
    patterns_dict = defaultdict(list)
    for pattern in patterns:
        patterns_dict[pattern.pattern[0]].append(pattern)
    return patterns_dict


def check_pattern(buffer: bytes, start_index: int, pattern: list[int | None]) -> bool:
    """
    Check if the pattern matches the buffer starting at the given index.
    """
    for i, c in enumerate(pattern):
        if c is None:
            continue

        if buffer[start_index + i] != pattern[i]:
            return False

    return True

from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import NamedTuple

from loguru import logger
from more_itertools import chunked


class Pattern(NamedTuple):
    """
    A named tuple to contain information about a pattern: it's name and the pattern in bytes.
    """

    name: str
    pattern: Sequence[int | None]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, pattern={self.pattern!r})"

    def __hash__(self) -> int:
        return hash(tuple(self.pattern))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            return False
        return self.pattern == other.pattern


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


def check_duplicates(patterns: list[Pattern]) -> None:
    """
    Check for duplicate patterns.
    """
    duplicates = defaultdict(list)

    for pattern in patterns:
        duplicates[pattern].append(pattern.name)

    print(list(duplicates.values()))

    for names in duplicates.values():
        if len(names) > 1:
            logger.warning(f"Duplicate patterns: {names}")


def load_patterns(pattern_path: Path) -> list[Pattern]:
    """
    Load patterns to a list from ffsess file.
    """
    patterns = []

    with Path(pattern_path).open() as patterns_file:
        for tab_line, pattern_line in chunked(patterns_file, 2):
            command, _, tab_name = tab_line.rstrip().partition(" ")
            assert command == "Tab", command
            rule_name, _, _, *pattern = pattern_line.rstrip().split(" ")
            assert rule_name == "RuleBytePattern"
            parsed_pattern = convert_to_pattern(pattern)
            pattern_object = Pattern(tab_name, parsed_pattern)

            patterns.append(pattern_object)

    check_duplicates(patterns)

    return patterns


def group_patterns(patterns: list[Pattern]) -> Mapping[int, list[Pattern]]:
    """
    Group patterns by their first byte.
    """
    patterns_dict = defaultdict(list)
    for pattern in patterns:
        assert pattern.pattern[0] is not None
        patterns_dict[pattern.pattern[0]].append(pattern)
    return patterns_dict


def check_pattern(buffer: bytes, start_index: int, pattern: Sequence[int | None]) -> bool:
    """
    Check if the pattern matches the buffer starting at the given index.
    """
    for i, c in enumerate(pattern):
        if c is None:
            continue

        if buffer[start_index + i] != c:
            return False

    return True

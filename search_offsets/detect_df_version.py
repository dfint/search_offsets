from __future__ import annotations

import functools
import re
from typing import NamedTuple

pattern = re.compile(rb"\x00((\d+)\.(\d+)(\-([^\d]+)(\d*))?)\x00")


class VersionInfo(NamedTuple):
    major: int
    minor: int
    beta_text: bytes | None = None
    beta_number: int | None = None

    def compare(self, other: VersionInfo) -> int:
        """
        Compare two VersionInfo objects.
        """
        if self == other:
            return 0

        if self.major != other.major:
            return self.major - other.major
        if self.minor != other.minor:
            return self.minor - other.minor
        if self.beta_text != other.beta_text:
            if self.beta_text is None:
                return 1
            if other.beta_text is None:
                return -1

            return 1 if self.beta_text > other.beta_text else -1
        if self.beta_number is not None and other.beta_number is not None:
            return self.beta_number - other.beta_number

        return 0

    @classmethod
    def from_match(cls, value: re.Match[bytes]) -> VersionInfo:
        """
        Create a VersionInfo object from a regex match.
        """
        try:
            beta_number = int(value.group(6))
        except (ValueError, TypeError):
            beta_number = None

        return cls(
            major = int(value.group(2)),
            minor = int(value.group(3)),
            beta_text = value.group(5),
            beta_number = beta_number,
        )


def match_comparator(left: re.Match[bytes], right: re.Match[bytes]) -> int:
    """
    Compare two regex matches containing version information.
    """
    return VersionInfo.from_match(left).compare(VersionInfo.from_match(right))


def detect_df_version(data: bytes) -> str | None:
    """
    Try to detect the version of Dwarf Fortress.
    """
    match = list(pattern.finditer(data))
    if not match:
        return None

    version_comparing_key = functools.cmp_to_key(match_comparator)
    return max(match, key=version_comparing_key).group(1).decode()

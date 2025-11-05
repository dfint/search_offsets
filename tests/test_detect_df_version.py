import operator
from collections.abc import Callable
from typing import Any

import pytest

from search_offsets.detect_df_version import VersionInfo, detect_df_version


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"", None),
        (b"\x0051.01-beta1\x00", "51.01-beta1"),
        (b"\x0051.02\x00", "51.02"),
        (b"\x0051.03-foo\x00", "51.03-foo"),
        (b"\x0051.05\x00\x0051.01\x00\x0050.01\x00", "51.05"),
        (b"\x0051.13-lua+filesystem-test-1\x00", "51.13-lua+filesystem-test-1"),
    ],
)
def test_detect_df_version(data: bytes, expected: str | None) -> None:
    assert detect_df_version(data) == expected


@pytest.mark.parametrize(
    ("left", "right", "comparison"),
    [
        (VersionInfo(51, 0), VersionInfo(51, 0), operator.eq),
        (VersionInfo(52, 0), VersionInfo(50, 0), operator.gt),
        (VersionInfo(51, 0), VersionInfo(52, 0), operator.lt),
        (VersionInfo(51, 1), VersionInfo(51, 0), operator.gt),
        (VersionInfo(51, 1), VersionInfo(51, 2), operator.lt),
        (VersionInfo(51, 1), VersionInfo(51, 1, b"beta", 1), operator.gt),
        (VersionInfo(51, 1, b"beta", 2), VersionInfo(51, 1, b"beta", 1), operator.gt),
        (VersionInfo(51, 1, b"beta", 1), VersionInfo(51, 1, b"zeta", 1), operator.lt),
    ],
)
def test_version_comparing_key(
    *,
    left: VersionInfo,
    right: VersionInfo,
    comparison: Callable[[Any, Any], bool],
) -> None:
    assert comparison(left.compare(right), 0)

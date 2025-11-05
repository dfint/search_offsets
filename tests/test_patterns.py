import pytest
from hypothesis import given
from hypothesis import strategies as st

from search_offsets.patterns import convert_to_pattern, hex_to_bytes


@given(st.integers(0, 255))
def test_hex_to_bytes(byte: int):
    assert hex_to_bytes(f"{byte:02X}") == byte.to_bytes(1, "little")


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        (["??"], [None]),
        (["FF"], [255]),
        (["FF", "??"], [255, None]),
    ],
)
def test_convert_to_pattern(pattern: list[str], expected: list[int | None]):
    assert convert_to_pattern(pattern) == expected

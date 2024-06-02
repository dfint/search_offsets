from hypothesis import given
from hypothesis import strategies as st

from search_offsets.patterns import hex_to_bytes


@given(st.integers(0, 255))
def test_hex_to_bytes(byte: int):
    assert hex_to_bytes(f"{byte:02X}") == byte.to_bytes(1, "little")

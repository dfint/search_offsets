import pytest

from search_offsets.detect_df_version import detect_df_version


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x0051.01-beta1\x00", "51.01-beta1"),
        (b"\x0051.02\x00", "51.02"),
        (b"\x0051.03-foo\x00", None),
        (b"\x0051.05\x00\x0051.01\x00\x0050.01\x00", "51.05"),
    ],
)
def test_detect_df_version(data: bytes, expected: str | None) -> None:
    assert detect_df_version(data) == expected

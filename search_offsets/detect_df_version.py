import re

pattern = re.compile(rb"\x00((\d+)\.(\d+)(\-([^\d]+)(\d*))?)\x00")

MAX_BETA = 10000


def version_comparing_key(value: re.Match[bytes]) -> tuple[int, int, int]:
    """
    Return a tuple of (major, minor, beta) used for detecting max version number in the executable.
    """
    beta_text = value.group(5)
    beta_number = value.group(6) or MAX_BETA
    return int(value.group(2)), int(value.group(3)), beta_text, int(beta_number)


def detect_df_version(data: bytes) -> str:
    """
    Try to detect the version of Dwarf Fortress.
    """
    match = list(pattern.finditer(data))
    if not match:
        return None

    return max(match, key=version_comparing_key).group(1).decode()

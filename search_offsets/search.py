import binascii
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import lief
from omegaconf import DictConfig
from rich import print  # noqa: A004

from search_offsets.config import with_config
from search_offsets.patterns import (
    Pattern,
    check_pattern,
    group_patterns,
    load_patterns,
)
from search_offsets.render_template import init_jinja_env

root_dir = Path(__file__).parent.parent


def search_offsets(path: str, patterns: list[Pattern]) -> Mapping[str, list[int]]:
    """
    Search patterns in the given file.
    """
    patterns_dict: Mapping[int, list[Pattern]] = group_patterns(patterns)

    found = defaultdict(list)

    data = Path(path).read_bytes()
    for i, c in enumerate(data):
        possible_patterns = patterns_dict.get(c, [])
        for pattern in possible_patterns:
            if check_pattern(data, i, pattern.pattern):
                found[pattern.name].append(i)

    return found


def process_found(
    pe: lief.PE.Binary,
    pattern_names: Iterable[Pattern],
    found: Mapping[str, int],
) -> Iterable[tuple[str, int]]:
    """
    Prepare found offsets to printing.
    """
    for pattern in pattern_names:
        pattern_name = pattern.name
        if not found[pattern_name]:
            yield pattern_name, None
            continue

        for i, offset in enumerate(found[pattern_name], -1):
            suffix = "" if i < 0 else f"_{i}"
            name = pattern_name + suffix
            if name == "addchar_0":
                name = "addchar_top"

            rva = pe.offset_to_virtual_address(offset)
            yield name, rva


def print_offsets(pe: lief.PE.Binary, pattern_names: Iterable[Pattern], found: Mapping[str, int]) -> None:
    """
    Print found offsets to the console.
    """
    processed = dict(process_found(pe, pattern_names, found))
    for key, value in processed.items():
        if value is None:
            print(f"{key}: NOT FOUND")
        else:
            print(f"{key} = 0x{value:X}")


@dataclass
class _Config:
    path: Path
    patterns: Path
    version_name: str | None = None


@with_config(_Config, "defaults.yaml", ".config.yaml")
def main(config: DictConfig) -> None:
    """
    Process the given portable executable file, print its checksum (time stamp) and offsets of the found patterns.
    """
    print(f"{config.path=}")
    print(f"{config.patterns=}")
    print(f"{config.version_name=}")
    print()

    is_pe_binary = False
    with config.path.open("rb") as executable:
        parsed_binary = lief.parse(executable)
        if parsed_binary is None:
            msg = f"Unknown format of file {config.path.name}"
            raise TypeError(msg)

        print(f"Detected file format: {parsed_binary.format}")

        if isinstance(parsed_binary, lief.PE.Binary):
            checksum = parsed_binary.header.time_date_stamps
            is_pe_binary = True
        elif isinstance(parsed_binary, lief.ELF.Binary):
            executable.seek(0)
            checksum = binascii.crc32(executable.read())
        else:
            msg = f"Unsupported file format: {parsed_binary.format}"
            raise TypeError(msg)

        print(f"checksum = 0x{checksum:X}")

    if not is_pe_binary:
        found = {}
        template_name = "linux_offsets.toml.jinja"
    else:
        patterns = load_patterns(config.patterns)
        found = search_offsets(config.path, patterns)
        print_offsets(parsed_binary, patterns, found)
        template_name = "windows_offsets.toml.jinja"

    version_name = config.get("version_name", None)
    if version_name:
        jinja_env = init_jinja_env()
        template = jinja_env.get_template(template_name)
        result = template.render(**found, checksum=checksum, version_name=version_name)
        file_name = f"offsets_{config.version_name.replace(' ', '_')}.toml"
        (root_dir / file_name).write_text(result, encoding="utf-8")
        print(f"Created {file_name} file")


if __name__ == "__main__":
    main()

import binascii
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import lief
from omegaconf import DictConfig
from rich import print  # noqa: A004

from search_offsets.config import with_config
from search_offsets.detect_df_version import detect_df_version
from search_offsets.detect_steam_api import detect_steam_api
from search_offsets.patterns import (
    Pattern,
    check_pattern,
    group_patterns,
    load_patterns,
)
from search_offsets.render_template import init_jinja_env

root_dir = Path(__file__).parent.parent


def search_offsets(path: str | Path, patterns: list[Pattern]) -> Mapping[str, list[int]]:
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
    pe: lief.PE.Binary | lief.ELF.Binary,
    pattern_names: Iterable[Pattern],
    found: Mapping[str, list[int]],
) -> Iterable[tuple[str, int | None]]:
    """
    Prepare found offsets for template rendering.
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


def print_offsets(offsets: Mapping[str, int | None]) -> None:
    """
    Print found offsets to the console.
    """
    for key, value in offsets.items():
        if value is None:
            print(f"{key}: NOT FOUND")
        else:
            print(f"{key} = 0x{value:X}")


def change_dir_path_to_file_path(path: Path) -> Path:
    """Change directory path to file path if needed."""
    if path.is_file():
        return path

    for file_name in ("Dwarf Fortress.exe", "dwarfort"):
        file_path = path / file_name
        if file_path.exists():
            print(f"Directory path changed to file path: {file_path!r}")
            return file_path

    return path


@dataclass
class _Config:
    path: str
    patterns: Path
    version_name: str | None = None
    autogenerate_version_name: bool = False


def process_game_directory(config: DictConfig, path: Path) -> None:  # noqa: PLR0915
    """
    Process the given portable executable file, print its checksum (time stamp) and offsets of the found patterns.
    """
    print(f"{path=}")
    print(f"{config.patterns=}")
    print(f"{config.version_name=}")
    print(f"{config.autogenerate_version_name=}")
    print()

    path = change_dir_path_to_file_path(path)

    is_pe_binary = False
    with path.open("rb") as executable:
        parsed_binary = lief.parse(executable)
        if parsed_binary is None:
            msg = f"Unknown format of file {path.name}"
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

        executable.seek(0)
        version = detect_df_version(executable.read())
        print(f"Detected DF version = {version}")

        steam_detected = detect_steam_api(parsed_binary)
        print(f"Steam api detected: {steam_detected}")

        if config.autogenerate_version_name:
            steam = "steam" if steam_detected else "other"
            os_part = "win64" if isinstance(parsed_binary, lief.PE.Binary) else "linux64"
            config.version_name = f"{version} {steam} {os_part}"
            print(f"Generated version name: {config.version_name}")

    if not is_pe_binary:
        processed = {}
        template_name = "linux_offsets.toml.jinja"
    else:
        patterns = load_patterns(config.patterns)
        found = search_offsets(path, patterns)
        processed = dict(process_found(parsed_binary, patterns, found))
        print_offsets(processed)
        if any(not row for row in processed.values()):
            print("Not all offsets are found")
            return

        template_name = "windows_offsets.toml.jinja"

    version_name = config.get("version_name", None)
    if version_name:
        jinja_env = init_jinja_env()
        template = jinja_env.get_template(template_name)
        result = template.render(**processed, checksum=checksum, version_name=version_name)
        file_name = f"offsets_{config.version_name.replace(' ', '_')}.toml"
        (root_dir / file_name).write_text(result, encoding="utf-8")
        print(f"Created {file_name} file")


@with_config(_Config, "defaults.yaml", ".config.yaml")
def main(config: DictConfig) -> None:
    for path in Path().rglob(config.path):
        if path.is_dir():
            process_game_directory(config, path)
            print()


if __name__ == "__main__":
    main()

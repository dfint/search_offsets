from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from omegaconf import DictConfig
from peclasses.portable_executable import PortableExecutable, SectionTable

from search_offsets.config import with_config
from search_offsets.patterns import (
    Pattern,
    check_pattern,
    group_patterns,
    load_patterns,
)
from search_offsets.render_template import render_template

root_dir = Path(__file__).parent.parent


def search(path: str, patterns: list[Pattern]) -> Mapping[str, list[int]]:
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


def print_found(section_table: SectionTable, pattern_names: Iterable[str], found: Mapping[str, int]) -> None:
    """
    Print offsets of the found patterns.
    """
    for pattern in pattern_names:
        if not found[pattern]:
            print(f"{pattern}: NOT FOUND")
            continue

        for i, offset in enumerate(found[pattern], -1):
            suffix = "" if i < 0 else f"_{i}"
            name = pattern + suffix
            if name == "addchar_0":
                name = "addchar_top"

            rva = section_table.offset_to_rva(offset)
            print(f"{name} = 0x{rva:X}")


@dataclass
class _Config:
    path: Path
    patterns: Path
    version_name: str | None


@with_config(_Config, "defaults.yaml", ".config.yaml")
def main(config: DictConfig) -> None:
    """
    Process the given portable executable file, print its checksum(time stamp) and offsets of the found patterns.
    """
    patterns: list[Pattern] = load_patterns(config.patterns)

    with config.path.open("rb") as exe:
        pe = PortableExecutable(exe)
        print(f"checksum = 0x{pe.file_header.timedate_stamp:X}")
        section_table = pe.section_table

    found = search(config.path, patterns)
    print_found(section_table, map(str, patterns), found)

    if config.get("version_name", None):
        result = render_template(found, checksum=pe.file_header.timedate_stamp, version_name=config.version_name)
        file_name =  f"offsets_{config.version_name.replace(' ', '_')}.toml"
        (root_dir / file_name).write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()

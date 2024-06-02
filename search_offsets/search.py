from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path

import typer
from peclasses.portable_executable import PortableExecutable, SectionTable

from search_offsets.patterns import (
    Pattern,
    check_pattern,
    group_patterns,
    load_patterns,
)


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


app = typer.Typer()


@app.command()
def main(path: Path) -> None:
    """
    Process the given portable executable file, print its checksum(time stamp) and offsets of the found patterns.
    """
    patterns: list[Pattern] = load_patterns()

    with path.open("rb") as exe:
        pe = PortableExecutable(exe)
        print(f"checksum = 0x{pe.file_header.timedate_stamp:X}")
        section_table = pe.section_table

    found = search(path, patterns)
    print_found(section_table, map(str, patterns), found)


if __name__ == "__main__":
    app()

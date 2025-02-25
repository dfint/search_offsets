import lief


def detect_steam_api(parsed_binary: lief.Binary) -> bool:
    """
    Detect that there an import of steam api library. Works both for PE and ELF binaries.
    """
    imported_functions = (item.name for item in parsed_binary.imported_functions)
    return "SteamAPI_Init" in imported_functions

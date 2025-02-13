from jinja2 import Environment, PackageLoader, select_autoescape


def hex_filter(value: int) -> str:
    """
    jinja2 filter to convert an integer to a hexadecimal string.
    """
    try:
        return f"0x{value:X}"
    except TypeError:
        return value


def init_jinja_env() -> Environment:
    """
    Initialize jinja2 environment.
    """
    env = Environment(loader=PackageLoader("search_offsets"), autoescape=select_autoescape())
    env.filters["hex"] = hex_filter
    return env

from collections.abc import Mapping

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


def render_template(found: Mapping[str, list[int]], checksum: int, version_name: str) -> str:
    """
    Render the template with the found offsets.
    """
    env = init_jinja_env()
    template = env.get_template("windows_offsets.toml.jinja")
    return template.render(**found, checksum=checksum, version_name=version_name)

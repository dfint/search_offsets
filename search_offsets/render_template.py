from collections.abc import Mapping

from jinja2 import Environment, PackageLoader, select_autoescape


def hex_filter(value: int) -> str:
    """
    jinja2 filter to convert an integer to a hexadecimal string.
    """
    return f"0x{value:X}"


def render_template(found: Mapping[str, list[int]], checksum: int, version_name: str) -> str:
    """
    Render the template with the found offsets.
    """
    env = Environment(loader=PackageLoader("search_offsets"), autoescape=select_autoescape())
    env.filters["hex"] = hex_filter
    template = env.get_template("offsets.toml.jinja")
    return template.render(**found, checksum=checksum, version_name=version_name)

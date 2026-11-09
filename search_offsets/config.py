import functools
import sys
from collections.abc import Callable
from pathlib import Path

import yaml
from loguru import logger
from pydantic import BaseModel, ValidationError

type ConfiguredFunction[ConfigT: BaseModel] = Callable[[ConfigT], None]


def with_config[ConfigT: BaseModel](
    config_class: type[ConfigT], *config_files: str,
) -> Callable[[ConfiguredFunction[ConfigT]], Callable[[], None]]:
    """
    A decorator to load the config file and merge it with the CLI options.
    """

    def decorator(func: ConfiguredFunction[ConfigT]) -> Callable[[], None]:
        @functools.wraps(func)
        def wrapper() -> None:
            config_data = {}

            for config_file in config_files:
                try:
                    with Path(config_file).open(encoding="utf-8") as file:
                        file_config = yaml.safe_load(file) or {}
                except FileNotFoundError:
                    logger.info(f"Config {config_file} not found")
                    continue
                if not isinstance(file_config, dict):
                    logger.error(f"Config {config_file} must contain a YAML mapping")
                    return
                config_data.update(file_config)

            try:
                for option in sys.argv[1:]:
                    key, separator, value = option.partition("=")
                    if not separator or not key:
                        logger.error(f"Expected a key=value option, got {option!r}")
                        return
                    config_data[key] = yaml.safe_load(value)

                config = config_class.model_validate(config_data)
            except (ValidationError, yaml.YAMLError) as error:
                logger.error(f"Invalid configuration: {error}")
                return

            func(config)

        return wrapper

    return decorator

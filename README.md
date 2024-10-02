# Search patterns

[![Tests](https://github.com/dfint/search_offsets/actions/workflows/tests.yml/badge.svg)](https://github.com/dfint/search_offsets/actions/workflows/tests.yml)

1. Install python 3.10

2. Install poetry:

    ```shell
    pip install poetry
    ```

3. Run search:

    ```shell
    poetry run search path="C:/path/to/Dwarf Fortress/Dwarf Fortress.exe"
    ```

    or:

    ```shell
    uv run search path="C:/path/to/Dwarf Fortress/Dwarf Fortress.exe"
    ```

Alternatively, you can add a yaml config in the root of the project instead of using the CLI options:

`.config.yaml:`

```yaml
path: "C:/path/to/Dwarf Fortress/Dwarf Fortress.exe"
```

And then run the utility just with `poetry run search`.

If `version_name` configuration is set, the offsets will be written into a ready to use toml file.

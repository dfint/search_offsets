# Search patterns

[![Tests](https://github.com/dfint/search_offsets/actions/workflows/tests.yml/badge.svg)](https://github.com/dfint/search_offsets/actions/workflows/tests.yml)

1. Install python 3.10

2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

3. Run search:

    ```shell
    uv run search path="C:/path/to/Dwarf Fortress/Dwarf Fortress.exe"
    ```

Alternatively, you can add a yaml config in the root of the project instead of using the CLI options:

`.config.yaml:`

```yaml
path: "C:/path/to/Dwarf Fortress/Dwarf Fortress.exe"
```

And then run the utility just with `uv run search`.

If `version_name` configuration is set, the offsets will be written into a ready to use toml file.

Also, `version_name` can be autogerated:

```yaml
path: "C:/path/to/Dwarf Fortress/Dwarf Fortress.exe"
autogenerate_version_name: true
```

For steam version it will look like "52.02 steam linux64",
for classic and itch versions it will be "52.02 other linux64".

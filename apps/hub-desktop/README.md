# personal-context-hub

Packaged desktop/browser shell and the `pch` / `personal-context-hub` user CLI.

```bash
uvx personal-context-hub
# or: uv tool install personal-context-hub && pch
```

From a source checkout (contributors):

```bash
make install
uv run pch doctor
uv run pch serve --headless
```

Binds loopback only. Vault default: `~/.pch`.

Documentation: [Getting started](../../docs/getting-started.md) · [CLI](../../docs/reference/cli.md)
